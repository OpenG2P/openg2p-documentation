# Score Computation framework

## Score Computation — Feature Design Document

**Project:** OpenG2P Registry Gen2\
**Feature:** Score Computation\
**Status:** Design / Pre-implementation\
**Date:** 2026-04-09

***

### 1. Overview

Score Computation is an asynchronous, extensible feature that automatically computes domain-specific scores (e.g. PMT Score, FSF Score) for records in a registry, whenever a change request that touches one or more contributing attributes is approved.

The design follows the same **metadata → trigger → queue → beat/worker → interface/factory → results** pattern used by deduplication and functional ID generation in the existing codebase. Core provides all infrastructure; domain extensions provide only the computation logic.

***

### 2. Scope and Constraints

* Score computation is available **only for registers with `register_purpose = RegisterPurposeEnum.REGISTER`**. Registers with purpose `PROGRAM_REGISTER` or `TABLE` are excluded.
* Every insert or update to a domain register table is **always mediated through a Change Request** — there are no direct writes. Score computation therefore triggers on **Change Request approval**, not on CR creation.
* The feature is **fully asynchronous**: the approval API returns immediately; the score is computed in the background by a Celery worker.
* The base registry (`registry-platform/core/openg2p-registry-core` and `registry-platform/celery`) provides all infrastructure. The **actual computation formula** lives entirely in the registry's own extension package.

***

### 3. Design Across Repositories

| Repository                         | What changes                                              |
| ---------------------------------- | --------------------------------------------------------- |
| `registry-platform/core/openg2p-registry-core`       | New models, interface, factory, controller service        |
| `registry-platform/celery`     | New beat producer, worker, Workers constant, config keys  |
| `registry-platform/apis`       | New API endpoint on staff portal                          |
| `registry-platform/ui/ui-widgets` | New `scores-display` widget                               |
| The registry's extension package | Concrete compute service implementations (per score type) |

***

### 4. Data Model

#### 4.1 `G2PRegisterScoreDefinition`

Stores the score types configured for a register, and which attributes contribute to each score. One register may have multiple score definitions (one per score type).

**Location:** `registry-platform/core/openg2p-registry-core/src/openg2p_registry_core/models/g2p_register_score_definition.py`

```python
class G2PRegisterScoreDefinition(BaseORMModel):
    __tablename__ = "g2p_register_score_definitions"

    score_definition_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    register_id: Mapped[str] = mapped_column(
        String, nullable=False, index=True
    )
    # e.g. "PMT_SCORE", "FSF_SCORE" — used as factory lookup key
    score_type: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # JSON list of field paths that contribute to this score
    # e.g. ["income", "assets.land_area", "household.member_count"]
    contributing_attributes: Mapped[JSON] = mapped_column(JSON, nullable=False)

    # Optional extra config for the compute implementation
    # e.g. {"formula_version": "2024", "external_api_url": "..."}
    score_config: Mapped[JSON] = mapped_column(JSON, nullable=True)

    is_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
```

**Constraint enforced at service layer:** `register_purpose` must be `RegisterPurposeEnum.REGISTER` when creating or updating a score definition.

**Unique constraint:** `(register_id, score_type)` — a register may only have one definition per score type.

***

#### 4.2 `G2PScoreComputeQueue`

One queue item per `(internal_record_id, score_type)` per trigger event. Follows the same pattern as `G2PFunctionalIdGenerationQueue`.

**Location:** `registry-platform/core/openg2p-registry-core/src/openg2p_registry_core/models/g2p_score_compute_queue.py`

```python
class G2PScoreComputeQueue(BaseORMModel):
    __tablename__ = "g2p_score_compute_queue"

    queue_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    register_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    internal_record_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    score_definition_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    score_type: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # FK to the change request that triggered this computation
    change_request_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # Snapshot of contributing attribute values at time of CR approval
    # Eliminates need for the worker to re-read the domain register table
    contributing_attribute_values: Mapped[JSON] = mapped_column(JSON, nullable=False)

    # Processing status — reuses ProcessStatusEnum from existing codebase
    compute_status: Mapped[ProcessStatusEnum] = mapped_column(
        String, nullable=False, default=ProcessStatusEnum.PENDING, index=True
    )
    compute_no_of_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    compute_latest_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    compute_latest_error_code: Mapped[str] = mapped_column(String, nullable=True)
```

**Upsert behaviour:** When a trigger event fires for a `(internal_record_id, score_type)` pair that already has a `PENDING` queue item, the existing row is updated (`change_request_id` and `contributing_attribute_values` are refreshed) rather than inserting a duplicate. This ensures the worker always computes on the most recent approved state.

***

#### 4.3 `G2PRegisterScore`

Stores the latest computed score per record per score type. One row per `(internal_record_id, score_type)`, upserted on every computation.

**Location:** `registry-platform/core/openg2p-registry-core/src/openg2p_registry_core/models/g2p_register_score.py`

```python
class G2PRegisterScore(BaseORMModel):
    __tablename__ = "g2p_register_scores"

    score_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    register_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    internal_record_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    score_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    score_definition_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # The CR that last triggered this computation — full audit trail
    triggered_by_cr_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    computed_score: Mapped[float] = mapped_column(Float, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
```

**Upsert key:** `(internal_record_id, score_type)`. The `score_id` remains stable across recomputations; only `computed_score`, `computed_at`, and `triggered_by_cr_id` are updated.

***

#### 4.4 `G2PRegisterScoreHistory` _(recommended)_

Appends an immutable snapshot on every computation. Consistent with the pattern used by `G2PRegisterHistory` in the existing codebase.

```python
class G2PRegisterScoreHistory(BaseORMModel):
    __tablename__ = "g2p_register_score_history"

    history_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    register_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    internal_record_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    score_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    score_definition_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    triggered_by_cr_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    computed_score: Mapped[float] = mapped_column(Float, nullable=False)
    computed_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
```

This table is append-only. It enables answering "how has this record's PMT score changed over time and which CR caused each change?"

***

### 5. Trigger: Change Request Approval

The queue is populated inside `G2PRegisterService.approve_change_request()`, after the domain record has been updated and the history snapshot written. This is the only correct trigger point — the contributing attribute values in the domain table are not updated until approval.

#### Trigger Logic

```python
# Inside G2PRegisterService.approve_change_request(change_request_id, ...)
# ... existing approval logic (update domain table, write history) ...

# [NEW] Score compute queue population
await self._enqueue_score_computations(
    session=session,
    register_id=change_request.register_id,
    internal_record_id=change_request.internal_record_id,
    change_request_id=change_request.change_request_id,
    approved_payload=change_request_payload.change_payload,
)
```

#### `_enqueue_score_computations` logic

```
1. Fetch all G2PRegisterScoreDefinition records for register_id WHERE is_enabled = True
2. Check register_purpose = REGISTER (guard — skip silently if not)
3. For each score_definition:
   a. Extract the keys present in approved_payload
   b. Check if any key intersects with score_definition.contributing_attributes
   c. If no intersection → skip (this CR did not touch any contributing attribute)
   d. If intersection:
      i.  Read current values of ALL contributing_attributes from the domain record
          (not just the changed ones — the score needs the full attribute set)
      ii. UPSERT into g2p_score_compute_queue:
            - If PENDING row exists for (internal_record_id, score_type):
                update change_request_id, contributing_attribute_values, updated_at
            - Else: insert new row with status = PENDING
```

***

### 6. Interface and Factory

#### 6.1 `G2PScoreComputeInterface`

**Location:** `registry-platform/core/openg2p-registry-core/.../interfaces/g2p_score_compute_interface.py`

```python
from abc import ABC, abstractmethod
from uuid import UUID

class G2PScoreComputeInterface(ABC):

    @abstractmethod
    async def compute_score(
        self,
        internal_record_id: str,
        contributing_attribute_values: dict,
        score_config: dict,
    ) -> float:
        """
        Compute and return the score for the given record.

        Args:
            internal_record_id:            The UUID of the register record.
            contributing_attribute_values: Snapshot of the attribute values
                                           that feed into this score (from queue).
            score_config:                  Implementation-specific configuration
                                           from G2PRegisterScoreDefinition.score_config.
        Returns:
            The computed score as a float.
        """
        ...
```

#### 6.2 `G2PScoreComputeFactory`

**Location:** `registry-platform/core/openg2p-registry-core/.../interfaces/g2p_score_compute_factory.py`

Mirrors `G2PPayloadEnricherFactory` exactly. Uses `importlib` to load the implementation from the extensions namespace at runtime.

```python
import importlib
from openg2p_fastapi_common.service import BaseService
from .g2p_score_compute_interface import G2PScoreComputeInterface

class G2PScoreComputeFactory(BaseService):

    def get_compute_service(self, score_type: str) -> G2PScoreComputeInterface:
        """
        Dynamically loads the compute service for the given score_type.

        Naming convention:
            score_type "PMT_SCORE"  →  G2PScoreComputeServicePmtScore
            score_type "FSF_SCORE"  →  G2PScoreComputeServiceFsfScore

        The implementation class must exist in:
            openg2p_registry_extensions.score_compute.services
        """
        class_name = self._score_type_to_class_name(score_type)
        module = importlib.import_module(
            "openg2p_registry_extensions.score_compute.services"
        )
        compute_class = getattr(module, class_name)
        return compute_class()

    @staticmethod
    def _score_type_to_class_name(score_type: str) -> str:
        # "PMT_SCORE" → "G2PScoreComputeServicePmtScore"
        title_case = score_type.replace("_", " ").title().replace(" ", "")
        return f"G2PScoreComputeService{title_case}"
```

***

### 7. Celery Beat Producer and Worker

#### 7.1 Beat Producer

**Location:** `registry-platform/celery/.../tasks/score_compute_beat_producer.py`

Follows the exact pattern of `deduplication_register_beat_producer.py`.

```python
@celery_app.task(name="score_compute_beat_producer")
def score_compute_beat_producer():
    """
    Queries PENDING score compute queue items and dispatches them to the worker.
    Transitions status from PENDING → PROCESSING before dispatch.
    """
    with session_maker() as session:
        pending_items = (
            session.execute(
                select(G2PScoreComputeQueue)
                .filter(G2PScoreComputeQueue.compute_status == ProcessStatusEnum.PENDING)
                .limit(_config.no_of_tasks_to_process)
            )
            .scalars().all()
        )

        for item in pending_items:
            item.compute_status = ProcessStatusEnum.PROCESSING
            session.add(item)
            celery_app.send_task(
                Workers.SCORE_COMPUTE_WORKER,
                args=(item.queue_id,),
                queue=_config.worker_queue,
            )
        session.commit()
```

#### 7.2 Worker

**Location:** `registry-platform/celery/.../tasks/score_compute_worker.py`

The worker is stateless — it reads everything it needs from the queue item (including the attribute snapshot and the `change_request_id`). The worker delegates to the factory; it never contains formula logic.

```python
@celery_app.task(name="score_compute_worker", bind=True, max_retries=3)
def score_compute_worker(self, queue_id: str):
    with session_maker() as session:
        queue_item = session.get(G2PScoreComputeQueue, queue_id)
        score_definition = session.get(G2PRegisterScoreDefinition, queue_item.score_definition_id)

        try:
            # 1. Load factory and get domain-specific compute service
            factory = G2PScoreComputeFactory.get_component()
            compute_service = factory.get_compute_service(queue_item.score_type)

            # 2. Compute the score
            computed_score = asyncio.get_event_loop().run_until_complete(
                compute_service.compute_score(
                    internal_record_id=queue_item.internal_record_id,
                    contributing_attribute_values=queue_item.contributing_attribute_values,
                    score_config=score_definition.score_config or {},
                )
            )

            # 3. Upsert into g2p_register_scores
            _upsert_score(session, queue_item, computed_score)

            # 4. Append to score history
            _append_score_history(session, queue_item, computed_score)

            # 5. Mark queue item COMPLETED
            queue_item.compute_status = ProcessStatusEnum.COMPLETED
            queue_item.compute_latest_timestamp = datetime.utcnow()
            session.commit()

        except Exception as e:
            session.rollback()
            queue_item.compute_no_of_attempts += 1
            queue_item.compute_latest_error_code = str(e)
            queue_item.compute_latest_timestamp = datetime.utcnow()

            if self.request.retries < self.max_retries:
                queue_item.compute_status = ProcessStatusEnum.PENDING   # reset for retry
            else:
                queue_item.compute_status = ProcessStatusEnum.FAILED

            session.add(queue_item)
            session.commit()
            raise
```

#### 7.3 `Workers` constants update

Add to `registry-platform/celery/.../utils/workers.py`:

```python
SCORE_COMPUTE_WORKER = "score_compute_worker"
```

#### 7.4 Beat schedule and config

Add to `openg2p-registry-celery-beat-producers/src/.../app.py` beat schedule:

```python
"score_compute_beat_producer": {
    "task": "score_compute_beat_producer",
    "schedule": _config.score_compute_beat_producer_frequency
               or _config.default_beat_producer_frequency,
},
```

Add to `config.py`:

```python
score_compute_beat_producer_frequency: Optional[int] = None
```

***

### 8. Core Service

**Location:** `registry-platform/core/openg2p-registry-core/.../services/g2p_score_compute_service.py`

Provides the `_enqueue_score_computations` method (called from `G2PRegisterService.approve_change_request`) and manages the score definition CRUD. This is a `BaseService` singleton.

```python
class G2PScoreComputeService(BaseService):

    async def get_score_definitions(self, register_id: str, session) -> list[G2PRegisterScoreDefinition]:
        ...

    async def create_score_definition(self, register_id: str, score_type: str,
                                       contributing_attributes: list, score_config: dict,
                                       session) -> G2PRegisterScoreDefinition:
        # Guard: register_purpose must be REGISTER
        ...

    async def enqueue_score_computations(self, register_id: str, internal_record_id: str,
                                          change_request_id: str, approved_payload: dict,
                                          session) -> None:
        # Core trigger logic described in Section 5
        ...

    async def get_scores_for_record(self, internal_record_id: str,
                                     session) -> list[G2PRegisterScore]:
        ...

    async def get_score_history(self, internal_record_id: str, score_type: str,
                                 session) -> list[G2PRegisterScoreHistory]:
        ...
```

***

### 9. Controller Service and API Endpoint

#### 9.1 Controller Service

**Location:** `registry-platform/core/openg2p-registry-core/.../controller_services/g2p_score_controller_service.py`

```python
class G2PScoreControllerService(BaseService):

    async def get_scores_for_record(self, request: GetScoresRequest) -> GetScoresResponse:
        # Calls G2PScoreComputeService.get_scores_for_record()
        # Returns list of { score_type, computed_score, computed_at, triggered_by_cr_id }
        ...

    async def get_score_history(self, request: GetScoreHistoryRequest) -> GetScoreHistoryResponse:
        ...
```

#### 9.2 Staff Portal API Controller

**Location:** `registry-platform/apis/openg2p-registry-staff-portal-api/.../controllers/g2p_score_controller.py`

```
POST /register-data/get_scores
    Request:  { internal_record_id: str }
    Response: { scores: [{ score_type, computed_score, computed_at, triggered_by_cr_id }] }
    Auth:     @require_permissions("registerScore:view")

POST /register-data/get_score_history
    Request:  { internal_record_id: str, score_type: str }
    Response: { history: [{ computed_score, computed_at, triggered_by_cr_id }] }
    Auth:     @require_permissions("registerScore:view")

POST /register-metadata/get_score_definitions
    Request:  { register_id: str }
    Response: { score_definitions: [...] }
    Auth:     @require_permissions("registerDefinition:view")

POST /register-metadata/create_score_definition
    Request:  { register_id, score_type, contributing_attributes, score_config }
    Response: { score_definition: {...} }
    Auth:     @require_permissions("registerDefinition:manage")

POST /register-metadata/update_score_definition
    Request:  { score_definition_id, contributing_attributes?, score_config?, is_enabled? }
    Response: { score_definition: {...} }
    Auth:     @require_permissions("registerDefinition:manage")
```

***

### 10. Extension Implementation

#### Directory structure in the registry's extension package

```
openg2p-registry-{domain}-extension/
└── src/
    └── openg2p_registry_extensions/        ← namespace mapping
        └── score_compute/
            └── services/
                ├── __init__.py
                ├── g2p_score_compute_service_pmt_score.py
                └── g2p_score_compute_service_fsf_score.py
```

#### Example PMT Score implementation

```python
# g2p_score_compute_service_pmt_score.py
from openg2p_registry_core.interfaces import G2PScoreComputeInterface

class G2PScoreComputeServicePmtScore(G2PScoreComputeInterface):

    async def compute_score(
        self,
        internal_record_id: str,
        contributing_attribute_values: dict,
        score_config: dict,
    ) -> float:
        """
        Proxy Means Test (PMT) score computation.
        Weights and formula version are read from score_config.
        """
        weights = score_config.get("weights", {})
        score = 0.0

        income       = contributing_attribute_values.get("income", 0)
        land_area    = contributing_attribute_values.get("assets.land_area", 0)
        member_count = contributing_attribute_values.get("household.member_count", 1)

        score += income       * weights.get("income", 0.4)
        score += land_area    * weights.get("land_area", 0.3)
        score += member_count * weights.get("member_count", 0.3)

        return round(score, 4)
```

#### Namespace packaging (`pyproject.toml`)

```toml
[tool.hatch.build.targets.wheel.sources]
"src/openg2p_registry_extensions" = "openg2p_registry_extensions"
```

This ensures the factory's `importlib.import_module("openg2p_registry_extensions.score_compute.services")` resolves correctly when the extension package is installed alongside core.

***

### 11. UI — Scores Display

#### 11.1 New widget: `scores-display`

**Location:** `registry-platform/ui/ui-widgets/src/widgets/ScoresDisplayWidget.tsx`

A read-only widget that fetches and displays all computed scores for the current record.

```tsx
interface ScoresDisplayConfig extends BaseWidgetConfig {
  widget: 'scores-display';
  'widget-data-source': {
    type: 'api';
    service: string;        // e.g. "staff-portal-api"
    endpoint: string;       // e.g. "get_scores"
    params: { internal_record_id_path: string };  // dot-path to record ID in form values
  };
}
```

Renders as a compact table:

| Score Type | Score | Computed At      | Triggered by CR |
| ---------- | ----- | ---------------- | --------------- |
| PMT\_SCORE | 47.32 | 2026-04-08 14:22 | CR-00123        |
| FSF\_SCORE | 82.10 | 2026-04-08 14:22 | CR-00123        |

Shows a spinner/pending badge when a `PENDING` queue item exists for the record (polled via a secondary data source or SSE).

Register the widget in `src/registry/defaultWidgets.ts`:

```typescript
import ScoresDisplayWidget from '../widgets/ScoresDisplayWidget';
widgetRegistry.register('scores-display', ScoresDisplayWidget);
```

#### 11.2 Core Section in UI Schema

Scores are surfaced as a **core section** — a section managed by the registry platform, not user-configurable via `SectionBuilder`. Distinguish it with a `section-is-core: true` flag in `SectionConfig`:

```json
{
  "section-id": "scores",
  "section-title": "Computed Scores",
  "section-is-core": true,
  "section-editable": false,
  "panels": [
    {
      "panel-id": "scores-panel",
      "widgets": [
        {
          "widget": "scores-display",
          "widget-id": "record-scores",
          "widget-data-source": {
            "type": "api",
            "service": "staff-portal-api",
            "endpoint": "get_scores",
            "params": { "internal_record_id_path": "internal_record_id" }
          }
        }
      ]
    }
  ]
}
```

`SectionBuilder` should hide or lock sections with `section-is-core: true` to prevent accidental editing.

***

### 12. End-to-End Data Flow

```
Staff approves Change Request (change_request_id = "CR-00123")
  │
  ▼
G2PRegisterService.approve_change_request("CR-00123")
  ├─ Updates G2PRegisterFarmer (income: 5000 → 3500)
  ├─ Writes G2PRegisterHistoryFarmer snapshot
  └─ Calls G2PScoreComputeService.enqueue_score_computations()
       │
       ├─ Loads score definitions for register_id
       │    [PMT_SCORE: contributing = ["income", "assets.land_area"]]
       │    [FSF_SCORE: contributing = ["income", "household.member_count"]]
       │
       ├─ "income" ∈ approved_payload → both score types affected
       │
       ├─ Reads current values: { income: 3500, assets.land_area: 2.1,
       │                           household.member_count: 4 }
       │
       ├─ UPSERT g2p_score_compute_queue:
       │    Row 1: (record_A, PMT_SCORE, CR-00123, {income:3500, land:2.1}, PENDING)
       │    Row 2: (record_A, FSF_SCORE, CR-00123, {income:3500, members:4}, PENDING)
       └─ Returns (API response already sent)

    ↓  (every ~20 seconds)

score_compute_beat_producer
  ├─ Queries PENDING rows → finds Row 1 and Row 2
  ├─ Sets both to PROCESSING
  └─ celery_app.send_task("score_compute_worker", args=("queue_id_1",))
     celery_app.send_task("score_compute_worker", args=("queue_id_2",))

    ↓

score_compute_worker("queue_id_1")  [PMT_SCORE]
  ├─ Reads queue item → score_type="PMT_SCORE", cr_id="CR-00123"
  ├─ factory.get_compute_service("PMT_SCORE")
  │    → loads G2PScoreComputeServicePmtScore from extensions
  ├─ compute_score({income:3500, land:2.1}, score_config) → 47.32
  ├─ UPSERT g2p_register_scores:
  │    (record_A, PMT_SCORE, 47.32, now(), triggered_by="CR-00123")
  ├─ INSERT g2p_register_score_history:
  │    (record_A, PMT_SCORE, 47.32, now(), triggered_by="CR-00123")
  └─ Sets queue item → COMPLETED

    ↓

Staff portal UI loads the record
  └─ ScoresDisplayWidget calls GET /register-data/get_scores
       → returns [{ PMT_SCORE: 47.32 }, { FSF_SCORE: 82.10 }]
```

***

### 13. Migration Checklist

All new tables require Alembic migrations. Add to `CoreInitializer.migrate_database()`:

```python
await G2PRegisterScoreDefinition.create_migrate()
await G2PScoreComputeQueue.create_migrate()
await G2PRegisterScore.create_migrate()
await G2PRegisterScoreHistory.create_migrate()
```

***

### 14. Summary of All New Artifacts

#### `registry-platform/core/openg2p-registry-core`

| Type      | File                                                  | Description                    |
| --------- | ----------------------------------------------------- | ------------------------------ |
| Model     | `models/g2p_register_score_definition.py`             | Score type config per register |
| Model     | `models/g2p_score_compute_queue.py`                   | Async compute queue            |
| Model     | `models/g2p_register_score.py`                        | Latest score per record/type   |
| Model     | `models/g2p_register_score_history.py`                | Immutable score audit trail    |
| Interface | `interfaces/g2p_score_compute_interface.py`           | Abstract `compute_score()`     |
| Factory   | `interfaces/g2p_score_compute_factory.py`             | Dynamic loader by `score_type` |
| Service   | `services/g2p_score_compute_service.py`               | Enqueue logic, CRUD, results   |
| Ctrl Svc  | `controller_services/g2p_score_controller_service.py` | HTTP layer                     |

#### `registry-platform/celery`

| Type     | File                                   | Description                             |
| -------- | -------------------------------------- | --------------------------------------- |
| Beat     | `tasks/score_compute_beat_producer.py` | Polls PENDING, dispatches               |
| Worker   | `tasks/score_compute_worker.py`        | Computes, persists, retries             |
| Constant | `utils/workers.py`                     | `SCORE_COMPUTE_WORKER`                  |
| Config   | `config.py`                            | `score_compute_beat_producer_frequency` |

#### `registry-platform/apis`

| Type       | File                      | Description     |
| ---------- | ------------------------- | --------------- |
| Controller | `g2p_score_controller.py` | 5 new endpoints |

#### `registry-platform/ui/ui-widgets`

| Type     | File                              | Description                    |
| -------- | --------------------------------- | ------------------------------ |
| Widget   | `widgets/ScoresDisplayWidget.tsx` | `scores-display` widget        |
| Types    | `types/index.ts`                  | `ScoresDisplayConfig` type     |
| Registry | `registry/defaultWidgets.ts`      | Auto-register `scores-display` |

#### The registry's extension package

| Type | File                                                            | Description |
| ---- | --------------------------------------------------------------- | ----------- |
| Impl | `score_compute/services/g2p_score_compute_service_pmt_score.py` | PMT formula |
| Impl | `score_compute/services/g2p_score_compute_service_fsf_score.py` | FSF formula |
