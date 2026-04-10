# Functional ID generation

## Functional ID Generation — Feature Design Document

**Project:** OpenG2P Registry Gen2\
**Feature:** Functional ID Generation\
**Status:** Implemented / Documentation\
**Date:** 2026-04-10

***

### 1. Overview

Functional ID Generation is a two-stage asynchronous process that automatically generates human-readable, domain-specific IDs (e.g., `FAR-00001`, `HH-00045`) for registry records, replacing the system-generated UUID with user-facing identifiers.

The feature is **opt-in per register** (controlled by `functional_id_generation_required` flag on `G2PRegisterDefinition`). When enabled, it integrates with an external **Functional ID Generation Service** to allocate unique numeric IDs and compose them with domain-specific prefixes and suffixes.

The design follows a **queue + beat producer + worker** pattern with **two separate pipelines**:

1. **Allocation** — Generate prefix/suffix, call external service to allocate numeric ID, update register
2. **Updation** — Notify external service that the allocated ID has been used

***

### 2. Design Principles

* **Asynchronous**: All operations queued immediately; record gets its ID in the background within seconds
* **Fault-tolerant**: Retry logic with configurable max attempts; failed items remain in queue for manual intervention
* **Extensible**: Prefix/suffix generation is domain-specific (extensions provide implementations)
* **Stateless workers**: All data needed for processing is stored in the queue item
* **Immutable audit trail**: Queue stores all attempts, timestamps, and error codes

***

### 3. Scope and Constraints

* **Opt-in per register**: Register metadata `functional_id_generation_required` must be `true`
* **Trigger point**: Queue populated after a new record is created (via change request approval)
* **External dependency**: Calls a remote Functional ID Generation Service via HTTP
* **Unique constraint**: `functional_record_id` has a database unique constraint — no duplicates
* **Fallback**: If ID generation fails after max retries, record remains with `functional_record_id = null`

***

### 4. Data Model

#### 4.1 `G2PFunctionalIdGenerationQueue`

Two-stage queue item tracking both allocation and updation phases. The same row transitions through both pipelines sequentially.

**Location:** `openg2p-registry-gen2-core/.../models/g2p_functional_id_generation_queue.py`

```python
class ProcessStatusEnum(str, enum.Enum):
    NOT_APPLICABLE = "NOT_APPLICABLE"
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class G2PFunctionalIdGenerationQueue(BaseORMModel):
    __tablename__ = "g2p_functional_id_generation_queue"

    queue_id: Mapped[str] = mapped_column(
        String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    register_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    internal_record_id: Mapped[str] = mapped_column(String, nullable=False, index=True)

    # === ALLOCATION STAGE ===
    # After allocation worker completes, these are populated:
    resolved_id: Mapped[str] = mapped_column(String, nullable=True)           # numeric ID from external service
    resolved_prefix: Mapped[str] = mapped_column(String, nullable=True)       # domain-specific prefix
    resolved_suffix: Mapped[str] = mapped_column(String, nullable=True)       # domain-specific suffix

    # Allocation status and retry tracking
    id_allocation_status: Mapped[ProcessStatusEnum] = mapped_column(
        String, nullable=False, default=ProcessStatusEnum.PENDING, index=True
    )
    id_allocation_no_of_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    id_allocation_latest_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    id_allocation_latest_error_code: Mapped[str] = mapped_column(String, nullable=True)

    # === UPDATION STAGE ===
    # After allocation completes, updation begins
    id_updation_status: Mapped[ProcessStatusEnum] = mapped_column(
        String, nullable=False, default=ProcessStatusEnum.NOT_APPLICABLE, index=True
    )
    id_updation_no_of_attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    id_updation_latest_timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    id_updation_latest_error_code: Mapped[str] = mapped_column(String, nullable=True)
```

**Unique constraint:** `(register_id, internal_record_id)` — one queue item per record per register.

**Status transitions:**

Allocation phase:

```
PENDING → PROCESSING → COMPLETED
              ↓ (error, retries < max)
              PENDING (reset for retry)
              ↓ (error, retries >= max)
              FAILED
```

Updation phase (only if allocation succeeded):

```
NOT_APPLICABLE → PENDING → PROCESSING → COMPLETED
                             ↓ (error, retries < max)
                             PENDING (reset for retry)
                             ↓ (error, retries >= max)
                             FAILED
```

***

#### 4.2 `G2PRegister.functional_record_id`

Field already exists on the base `G2PRegister` model:

```python
class G2PRegister(BaseORMModel):
    __abstract__ = True

    internal_record_id: Mapped[str] = mapped_column(String, primary_key=True, ...)  # UUID
    functional_record_id: Mapped[str] = mapped_column(
        String, nullable=True, unique=True, index=True
    )  # e.g. "FAR-00001"
    # ... other fields
```

Remains `nullable=True` because:

* New records start without an ID
* Failed ID generation leaves it null
* Records created before the feature was enabled may not have IDs

***

#### 4.3 `G2PRegisterDefinition.functional_id_generation_required`

```python
class G2PRegisterDefinition(BaseORMModel):
    __tablename__ = "g2p_register_definitions"

    register_id: Mapped[str] = mapped_column(String, primary_key=True, ...)
    # ... other fields
    functional_id_generation_required: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False
    )
```

Setting this to `true` enables ID generation for the register. The queue population logic checks this flag before creating a queue item.

***

### 5. Trigger: Record Creation

The queue is populated in the post-approval hook when a new record is created. In the registry, **all record mutations go through change requests**, so the trigger is in `G2PRegisterService.approve_change_request()`.

#### Trigger Logic

```python
# Inside G2PRegisterService.approve_change_request()
# ... existing approval logic ...

# [POST-APPROVAL] Queue ID generation if enabled
if register_definition.functional_id_generation_required:
    await self._enqueue_functional_id_generation(
        register_id=change_request.register_id,
        internal_record_id=change_request.internal_record_id,
    )
```

#### `_enqueue_functional_id_generation` logic

```
1. Check register_definition.functional_id_generation_required = True
2. Check if a PENDING queue item already exists for (register_id, internal_record_id)
   If yes → skip (ID generation already queued)
3. If no → INSERT into g2p_functional_id_generation_queue:
      register_id = ...
      internal_record_id = ...
      id_allocation_status = PENDING
      id_updation_status = NOT_APPLICABLE
```

**Guard:** Only queued for new records, not for edits. In the registry, edit CRs do not generate new IDs — the `functional_record_id` remains stable across the record's lifetime.

***

### 6. Interface and Factory

#### 6.1 `IdAffix` Data Class

Returned by the domain-specific ID generator. Contains the prefix and suffix to be composed with the numeric ID.

```python
class IdAffix(BaseModel):
    prefix: str   # e.g. "FAR-"
    suffix: str   # e.g. "" (usually empty, but could be "-ABC")
```

#### 6.2 `G2PIdGeneratorInterface`

**Location:** `openg2p-registry-gen2-core/.../interfaces/g2p_id_generator_interface.py`

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel

class IdAffix(BaseModel):
    prefix: str
    suffix: str

class G2PIdGeneratorInterface(ABC):

    @abstractmethod
    def generate_prefix_suffix(
        self,
        g2p_register: G2PRegister,
        register_mnemonic: str,
    ) -> IdAffix:
        """
        Generate domain-specific prefix and suffix for the record.

        Args:
            g2p_register:       The register record (e.g., G2PRegisterFarmer instance).
            register_mnemonic:  The register's mnemonic (e.g., "FARMER").

        Returns:
            IdAffix with prefix and optional suffix.
        """
        ...
```

#### 6.3 `G2PIdGeneratorFactory`

**Location:** `openg2p-registry-gen2-core/.../interfaces/g2p_id_generator_factory.py` or in extensions

Actually implemented in extensions (discovered dynamically). The factory is a `BaseService` singleton:

```python
import importlib
from openg2p_fastapi_common.service import BaseService

class G2PIdGeneratorFactory(BaseService):

    def get_id_generator(self) -> G2PIdGeneratorInterface:
        """
        Dynamically load the ID generator from extensions.

        Looks for: openg2p_registry_extensions.register_domain.id_generator.G2PIdGeneratorService
        """
        try:
            module = importlib.import_module(
                "openg2p_registry_extensions.register_domain.id_generator"
            )
            implementation_class = getattr(module, "G2PIdGeneratorService")
            generator = implementation_class.get_component()
            if not generator:
                generator = implementation_class()
            return generator
        except (AttributeError, ModuleNotFoundError) as e:
            logger.warning(f"No ID generator found: {e}")
            return None
```

***

### 7. Allocation Stage: Beat Producer + Worker

#### 7.1 Allocation Beat Producer

**Location:** `openg2p-registry-gen2-celery/.../tasks/functional_id_allocation_beat_producer.py`

Polls for `PENDING` allocation items and queues them to the allocation worker.

```python
@celery_app.task(name="functional_id_allocation_beat_producer")
def functional_id_allocation_beat_producer():
    """
    Queries PENDING functional ID allocation requests and dispatches to worker.
    Updates status from PENDING → PROCESSING before dispatch.
    """
    with session_maker() as session:
        pending_items = (
            session.execute(
                select(G2PFunctionalIdGenerationQueue)
                .filter(G2PFunctionalIdGenerationQueue.id_allocation_status == ProcessStatusEnum.PENDING)
                .limit(_config.no_of_tasks_to_process)  # batch size
            )
            .scalars().all()
        )

        for item in pending_items:
            item.id_allocation_status = ProcessStatusEnum.PROCESSING
            session.add(item)
            
            celery_app.send_task(
                Workers.FUNCTIONAL_ID_ALLOCATION_WORKER,
                args=(item.queue_id,),
                queue=_config.worker_queue,
            )

        session.commit()
```

#### 7.2 Allocation Worker

**Location:** `openg2p-registry-gen2-celery/.../tasks/functional_id_allocation_worker.py`

The critical worker. Does the following:

1. Load the register record and its definition
2. Get the domain-specific ID generator service from factory
3. Call generator to get prefix/suffix
4. Call external Functional ID Generation Service to allocate numeric ID
5. Compose functional\_record\_id = prefix + numeric\_id + suffix
6. Update the register record with the new functional\_record\_id
7. Mark allocation as COMPLETED and set updation to PENDING
8. Retry logic on error

```python
@celery_app.task(name="functional_id_allocation_worker", bind=True)
def functional_id_allocation_worker(self, queue_id: str):
    """
    Allocates a functional ID by:
    1. Getting domain-specific prefix/suffix
    2. Calling external ID generation service
    3. Updating register record
    4. Setting updation status to PENDING
    """
    with session_maker() as session:
        queue_item = session.get(G2PFunctionalIdGenerationQueue, queue_id)
        
        try:
            # 1. Load register definition and domain record
            register_definition = session.get(G2PRegisterDefinition, queue_item.register_id)
            register_class = _get_register_class(register_definition.register_mnemonic)
            register_record = session.execute(
                select(register_class).where(
                    register_class.internal_record_id == queue_item.internal_record_id
                )
            ).scalar_one_or_none()
            
            # 2. Get domain-specific prefix/suffix
            factory = G2PIdGeneratorFactory.get_component()
            id_generator = factory.get_id_generator()
            id_affix = id_generator.generate_prefix_suffix(register_record, register_definition.register_mnemonic)
            
            # 3. Call external service to allocate numeric ID
            numeric_id = _allocate_functional_record_id(id_affix.prefix)
            
            # 4. Compose final functional ID
            functional_record_id = _compose_functional_record_id(
                id_affix.prefix,
                numeric_id,
                id_affix.suffix,
            )  # e.g. "FAR-00001"
            
            # 5. Update register record
            register_record.functional_record_id = functional_record_id
            session.add(register_record)
            
            # 6. Update queue item
            queue_item.resolved_prefix = id_affix.prefix
            queue_item.resolved_id = numeric_id
            queue_item.resolved_suffix = id_affix.suffix
            queue_item.id_allocation_status = ProcessStatusEnum.COMPLETED
            queue_item.id_updation_status = ProcessStatusEnum.PENDING  # trigger next stage
            queue_item.id_allocation_latest_timestamp = datetime.now()
            queue_item.id_allocation_no_of_attempts += 1
            session.add(queue_item)
            
            session.commit()
            
        except Exception as e:
            session.rollback()
            queue_item.id_allocation_no_of_attempts += 1
            queue_item.id_allocation_latest_timestamp = datetime.now()
            queue_item.id_allocation_latest_error_code = str(e)
            
            # Retry logic: if attempts < max, reset to PENDING
            if queue_item.id_allocation_no_of_attempts < _config.worker_max_attempts:
                queue_item.id_allocation_status = ProcessStatusEnum.PENDING
            else:
                queue_item.id_allocation_status = ProcessStatusEnum.FAILED
            
            session.add(queue_item)
            session.commit()
            raise e
```

#### 7.3 External ID Generation Service Integration

The worker makes an HTTP POST call to an external service to allocate a numeric ID:

```python
def _allocate_functional_record_id(resolved_prefix: str) -> str:
    """
    Calls external ID generation service to allocate next ID for the prefix.
    
    Config:
        functional_id_generation_url: base URL (e.g., "http://id-service:8080/v1")
        id_generation_allocation_path: path template (e.g., "/idgenerator/{id_type}/id")
    
    Builds URL: functional_id_generation_url + id_generation_allocation_path.format(id_type=prefix)
    Example: "http://id-service:8080/v1/idgenerator/FAR-/id"
    
    Expected response: { "response": { "id": "00001" } }
    """
    allocation_url = _build_functional_id_generation_url(resolved_prefix)
    
    try:
        response = httpx.post(allocation_url, timeout=30.0)
        response.raise_for_status()
    except httpx.HTTPError as e:
        raise Exception(f"ID allocation request failed: {str(e)}")
    
    response_json = response.json()
    numeric_id = response_json.get("response", {}).get("id")
    if not numeric_id:
        raise Exception(f"No ID in response from {allocation_url}")
    
    return numeric_id
```

**Configuration:**

```python
# In config.py
functional_id_generation_url: str = "http://functional-id-service/v1"
id_generation_allocation_path: str = "/idgenerator/{id_type}/id"
```

The `{id_type}` placeholder is replaced with the resolved prefix (e.g., `"FAR-"`).

***

### 8. Updation Stage: Beat Producer + Worker

#### 8.1 Updation Beat Producer

**Location:** `openg2p-registry-gen2-celery/.../tasks/functional_id_updation_beat_producer.py`

Polls for `PENDING` updation items and queues them to the updation worker. Triggered only after allocation completes.

```python
@celery_app.task(name="functional_id_updation_beat_producer")
def functional_id_updation_beat_producer():
    """
    Queries items with id_updation_status = PENDING and dispatches to updation worker.
    These are items that completed allocation and now need updation notification.
    """
    with session_maker() as session:
        pending_items = (
            session.execute(
                select(G2PFunctionalIdGenerationQueue)
                .filter(G2PFunctionalIdGenerationQueue.id_updation_status == ProcessStatusEnum.PENDING)
                .limit(_config.no_of_tasks_to_process)
            )
            .scalars().all()
        )

        for item in pending_items:
            item.id_updation_status = ProcessStatusEnum.PROCESSING
            session.add(item)
            
            celery_app.send_task(
                Workers.FUNCTIONAL_ID_UPDATION_WORKER,
                args=(item.queue_id,),
                queue=_config.worker_queue,
            )

        session.commit()
```

#### 8.2 Updation Worker

**Location:** `openg2p-registry-gen2-celery/.../tasks/functional_id_updation_worker.py`

Notifies the external service that an ID has been used. Currently a placeholder implementation.

```python
@celery_app.task(name="functional_id_updation_worker", bind=True)
def functional_id_updation_worker(self, queue_id: str):
    """
    Notifies external ID service that the allocated ID has been used.
    This allows the external service to track which IDs are in use.
    """
    with session_maker() as session:
        queue_item = session.get(G2PFunctionalIdGenerationQueue, queue_id)
        
        try:
            # Compose the final functional_record_id from resolved parts
            functional_record_id = _compose_functional_record_id(
                queue_item.resolved_prefix,
                queue_item.resolved_id,
                queue_item.resolved_suffix,
            )
            
            # Notify external service
            _notify_functional_id_used(functional_record_id)
            
            # Mark updation complete
            queue_item.id_updation_status = ProcessStatusEnum.COMPLETED
            queue_item.id_updation_latest_timestamp = datetime.now()
            queue_item.id_updation_no_of_attempts += 1
            session.add(queue_item)
            session.commit()
            
        except Exception as e:
            session.rollback()
            queue_item.id_updation_no_of_attempts += 1
            queue_item.id_updation_latest_timestamp = datetime.now()
            queue_item.id_updation_latest_error_code = str(e)
            
            # Retry logic
            if queue_item.id_updation_no_of_attempts < _config.worker_max_attempts:
                queue_item.id_updation_status = ProcessStatusEnum.PENDING
            else:
                queue_item.id_updation_status = ProcessStatusEnum.FAILED
            
            session.add(queue_item)
            session.commit()
            raise e


def _notify_functional_id_used(functional_record_id: str) -> None:
    """
    Placeholder: Notifies external service that the ID has been used.
    Could be extended to call a webhook or update endpoint.
    """
    updation_url = _build_functional_id_updation_url()
    logger.info(
        f"Functional ID updation placeholder: "
        f"functional_record_id={functional_record_id}, url={updation_url}"
    )
    # TODO: Implement actual notification logic
```

***

### 9. Beat Schedule and Configuration

#### 9.1 Beat Schedule

Both beat producers are registered with Celery Beat:

```python
# In celery-beat-producers/src/.../app.py
app.conf.beat_schedule = {
    "functional_id_allocation_beat_producer": {
        "task": "functional_id_allocation_beat_producer",
        "schedule": _config.functional_id_allocation_beat_producer_frequency
                   or _config.default_beat_producer_frequency,
    },
    "functional_id_updation_beat_producer": {
        "task": "functional_id_updation_beat_producer",
        "schedule": _config.functional_id_updation_beat_producer_frequency
                   or _config.default_beat_producer_frequency,
    },
}
```

Default frequency is \~20 seconds (configurable).

#### 9.2 Worker Constants

**Location:** `celery/.../utils/workers.py`

```python
class Workers:
    FUNCTIONAL_ID_ALLOCATION_WORKER = "functional_id_allocation_worker"
    FUNCTIONAL_ID_UPDATION_WORKER = "functional_id_updation_worker"
    # ... other worker constants
```

#### 9.3 Configuration

**Location:** `celery-beat-producers/src/.../config.py` and `celery-workers/src/.../config.py`

```python
class Settings(BaseSettings):
    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_backend_url: str = "redis://localhost:6379/0"
    worker_queue: str = "registry_worker_queue"
    
    # Batch size and task limits
    no_of_tasks_to_process: int = 4      # max items per beat cycle
    worker_max_attempts: int = 5         # retry limit
    default_beat_producer_frequency: int = 20  # seconds
    
    # Optional per-feature frequencies
    functional_id_allocation_beat_producer_frequency: Optional[int] = None
    functional_id_updation_beat_producer_frequency: Optional[int] = None
    
    # External ID Service
    functional_id_generation_url: str = "http://functional-id-service/v1"
    id_generation_allocation_path: str = "/idgenerator/{id_type}/id"
    id_generation_updation_path: str = "/idgenerator/mark-used"  # placeholder
```

***

### 10. Extension Implementation

#### Directory Structure

```
openg2p-registry-{domain}-extension/
└── src/
    └── openg2p_registry_extensions/
        └── register_domain/
            └── id_generator/
                ├── __init__.py
                └── g2p_id_generator_service.py
```

#### Example: Farmer Extension

```python
# g2p_id_generator_service.py
from openg2p_fastapi_common.service import BaseService
from openg2p_registry_core.interfaces import G2PIdGeneratorInterface, IdAffix

class G2PIdGeneratorService(BaseService, G2PIdGeneratorInterface):

    def generate_prefix_suffix(
        self,
        g2p_register,  # e.g., G2PRegisterFarmer instance
        register_mnemonic: str,
    ) -> IdAffix:
        """
        Maps register types to domain-specific prefixes.
        """
        mnemonic = (register_mnemonic or "").lower()
        
        if mnemonic == "farmer":
            return IdAffix(prefix="FAR-", suffix="")
        elif mnemonic == "household":
            return IdAffix(prefix="HH-", suffix="")
        else:
            return IdAffix(prefix="DEFAULT-", suffix="")
```

The factory discovers and instantiates this class at runtime via `importlib`.

***

### 11. End-to-End Data Flow

```
Staff approves Change Request (creates new Farmer record)
  │
  ▼
G2PRegisterService.approve_change_request()
  ├─ Creates G2PRegisterFarmer record with functional_record_id = null
  ├─ Writes history snapshot
  └─ Calls _enqueue_functional_id_generation()
       │
       └─ INSERT into g2p_functional_id_generation_queue:
            queue_id: "uuid1"
            register_id: "FARMER"
            internal_record_id: "farm-123"
            id_allocation_status: PENDING
            id_updation_status: NOT_APPLICABLE

     ↓ (every ~20 seconds)

functional_id_allocation_beat_producer
  ├─ Queries PENDING allocation items → finds queue_id "uuid1"
  ├─ Sets status to PROCESSING
  └─ celery_app.send_task("functional_id_allocation_worker", args=("uuid1",))

     ↓

functional_id_allocation_worker("uuid1")
  ├─ Loads G2PRegisterFarmer and G2PRegisterDefinition
  ├─ factory.get_id_generator() → G2PIdGeneratorService.generate_prefix_suffix()
  │    → IdAffix(prefix="FAR-", suffix="")
  ├─ httpx.post("http://id-service/v1/idgenerator/FAR-/id") → "00001"
  ├─ functional_record_id = "FAR-" + "00001" + "" = "FAR-00001"
  ├─ UPDATE g2p_register_farmers SET functional_record_id = "FAR-00001"
  ├─ UPDATE g2p_functional_id_generation_queue:
  │    resolved_prefix = "FAR-"
  │    resolved_id = "00001"
  │    resolved_suffix = ""
  │    id_allocation_status = COMPLETED
  │    id_updation_status = PENDING  ← trigger next stage

     ↓ (next beat cycle)

functional_id_updation_beat_producer
  ├─ Queries PENDING updation items → finds queue_id "uuid1"
  ├─ Sets status to PROCESSING
  └─ celery_app.send_task("functional_id_updation_worker", args=("uuid1",))

     ↓

functional_id_updation_worker("uuid1")
  ├─ Reads resolved_prefix, resolved_id, resolved_suffix from queue
  ├─ functional_record_id = "FAR-00001"
  ├─ _notify_functional_id_used("FAR-00001")  [placeholder]
  ├─ UPDATE g2p_functional_id_generation_queue:
  │    id_updation_status = COMPLETED

     ↓

Staff loads the Farmer record
  └─ G2PRegisterFarmer.functional_record_id = "FAR-00001" ✓
```

***

### 12. Retry Logic and Error Handling

Both allocation and updation workers use the same retry strategy:

```
Attempt 1 → Error?
  ├─ Yes: log error, increment attempts, reset status to PENDING
  │        (will be picked up on next beat cycle)
  └─ No: set status to COMPLETED

... (repeats up to worker_max_attempts = 5)

After 5 attempts:
  └─ Set status to FAILED, keep error_code for debugging
```

Failed items remain in the queue indefinitely. They require manual intervention or operator scripts to reset the status or remove them.

***

### 13. Retry Configuration

**Location:** `celery-workers/src/.../config.py`

```python
class Settings(BaseSettings):
    worker_max_attempts: int = 5  # Configurable via env var
```

Environment variable: `REGISTRY_CELERY_WORKERS_WORKER_MAX_ATTEMPTS`

Reasonable value: 5 attempts (covers transient network failures).

***

### 14. Unique Constraint Implications

The `unique=True` constraint on `functional_record_id` means:

* **Can't have duplicates**: If two records somehow get the same functional ID, the second update fails
* **Retry-safe**: If allocation succeeds but the update fails, retrying is safe (upsert semantics)
* **Conflicts with external service**: If the external service allocates the same ID twice (bug), the second allocation fails

To prevent this, ensure the external ID service is stateless and deterministic (for a given `id_type`, always return the next sequential ID).

***

### 15. Summary

The Functional ID Generation feature implements a robust, async pipeline that:

1. **Queues on record creation** — zero blocking; API returns immediately
2. **Two-stage processing** — allocation (get ID from external service) then updation (notify service it's in use)
3. **Fault-tolerant** — retries on transient failures; fails safely on permanent errors
4. **Extensible** — domain-specific prefix/suffix generation via factory
5. **Audited** — queue stores all attempts, timestamps, errors
6. **Configurable** — frequency, retry limits, external service URL all via env vars

The design enables registries to integrate with enterprise ID management systems (e.g., Aadhaar-based ID services, custom sequential ID generators) without coupling to the registry core.

***

### 16. Configuration Checklist

Before deploying, ensure these are configured:

| Setting                                            | Location          | Example                     | Notes                               |
| -------------------------------------------------- | ----------------- | --------------------------- | ----------------------------------- |
| `functional_id_generation_url`                     | workers config    | `http://id-service:8080/v1` | External service base URL           |
| `id_generation_allocation_path`                    | workers config    | `/idgenerator/{id_type}/id` | Path template; `{id_type}` = prefix |
| `id_generation_updation_path`                      | workers config    | `/idgenerator/mark-used`    | Path for updation endpoint (TBD)    |
| `worker_max_attempts`                              | workers config    | `5`                         | Retry limit                         |
| `functional_id_allocation_beat_producer_frequency` | beat config       | `20`                        | Seconds; `None` = use default       |
| `functional_id_updation_beat_producer_frequency`   | beat config       | `20`                        | Seconds; `None` = use default       |
| `functional_id_generation_required`                | register metadata | `true/false`                | Per register; opt-in                |

***

### 17. API Considerations

The feature is primarily async background processing. The only user-facing API changes:

* `GET /register-data/get_subject_record` — will now include `functional_record_id` (previously null)
* Optional: **Queue status monitoring** — staff portal could expose `/register-config/get_id_generation_queue_status` to show pending allocations

Currently no user-facing API to manually trigger ID generation. Queue population happens automatically on CR approval.
