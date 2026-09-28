---
description: >-
  Design for capturing high-frequency, semi-structured field observations
  (e.g. crop-sown/harvest events) separately from versioned register data,
  with async enrichment and computation feeding aggregates back to the
  registry.
---

# Observations

## Observations — Feature Design Document

**Project:** OpenG2P Registry\
**Feature:** Observations\
**Status:** Design / Pre-implementation

***


### 1. Enums

**RecordStatusEnum** (reused from `core/.../models/enum.py`)
`ACTIVE`, `ARCHIVED`

**RelationTypeEnum** (new)
`VOIDS` — this observation replaces another observation.
`FOLLOWS` — this observation is the next lifecycle step after another observation.

**SourceEnum** (new)
Fixed values: `AGENT_WEB_UI`, `AGENT_APP`, `STAFF_WEB_UI`, `STAFF_APP`, `BENE_WEB_UI`, `BENE_APP`
Pattern value: `PARTNER_{partner_mnemonic}` — `{partner_mnemonic}` validated against the Partner Management Service (`partner_mgmt_api_url`, `apis/openg2p-registry-partner-api/.../config.py`), not the local `g2p_partners` table

**ProcessStatusEnum** (reused from `core/.../models/g2p_functional_id_generation_queue.py`)
`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED` — used for `computation_status`

**EnrichmentStatusEnum** (new)
`PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`, `NOT_APPLICABLE` — used for `enrichment_status`

---

### 2. Model Design

#### 2.1 `G2PObservation` — table `g2p_observations`

| Field | Type | Nullable | Notes |
|---|---|---|---|
| observation_id | String (uuid4) | No | PK |
| observation_type | String | No | Indexed |
| internal_record_id | String | No | Indexed. The subject/context the observation is about |
| register_mnemonic | String | No | Indexed |
| observed_at | DateTime | No | Indexed |
| created_at | DateTime | No | |
| created_by | String | No | |
| submission_id | String | Yes | Indexed |
| source | String | Yes | Fixed value or `PARTNER_{partner_mnemonic}`, app-level validated against Partner Management Service (not a DB enum, not the local `g2p_partners` table) |
| latitude | Numeric | Yes | |
| longitude | Numeric | Yes | |
| record_status | String (RecordStatusEnum) | No | Default `ACTIVE` |
| related_observation_id | String | Yes | Indexed |
| relation_type | String (RelationTypeEnum) | Yes | |
| schema_version | Integer | No | |

#### 2.1.1 `G2PObservationPayload` — table `g2p_observations_payload`

Split from `G2PObservation` so envelope-only reads (timeline listing, search, hierarchy walks, void/follow resolution) never do IO on the JSONB payload. One row per observation, 1:1, written in the same transaction as the `g2p_observations` insert. Fetched explicitly (join or second query) only when payload contents are actually needed — schema validation at write time, `ENRICHMENT_WORKER`, `COMPUTATION_WORKER`, reporting-view extraction.

| Field | Type | Nullable | Notes |
|---|---|---|---|
| observation_id | String | No | PK. Same value as the `g2p_observations` row — no DB-level FK, consistent with the rest of the platform |
| payload | JSONB | No | Write-once |
| payload_enriched | JSONB | Yes | Upserted by `ENRICHMENT_WORKER`. Updating it never touches `g2p_observations` |

#### 2.2 `G2PObservationTypeDefinition` — table `g2p_observation_type_definitions`

No free-standing `observation_type`. Every definition is scoped under exactly one `register_mnemonic` — there is no separate allowed/disallowed mapping table. A `(register_mnemonic, observation_type)` pair is valid if and only if a definition row exists for it; existence *is* the allow-list.

| Field | Type | Nullable | Notes |
|---|---|---|---|
| observation_type_definition_id | String | No | PK |
| register_mnemonic | String | No | Indexed. The definition's owning register/table type |
| observation_type | String | No | Indexed |
| display_name | String | No | |
| description | String | Yes | |
| payload_json_schema | JSONB | No | JSON Schema document |
| schema_version | Integer | No | |
| follows_observation_type | String | Yes | References another `observation_type`. Drives the generic UI's FOLLOWS-candidate step (Section 10.6) — null means this type never follows anything |
| enrichment_applicable | Boolean | No | Default `false`. Gates `enrichment_status` at enqueue time |
| computation_applicable | Boolean | No | Default `false`. Gates whether a queue row is created at all |
| is_enabled | Boolean | No | Default `true` |

Unique index: `(register_mnemonic, observation_type)`. The same `observation_type` string could exist under a different `register_mnemonic` as a completely separate, independently-defined row — nothing links them; they'd just happen to share a name.

#### 2.3 `G2PObservationProcessingQueue` — table `g2p_observation_processing_queue`

Renamed from `G2PObservationAggregateQueue`. `G2PObservationAggregateDefinition` is removed — which aggregate(s) a given `observation_type` produces is now internal to that type's computation adapter (2.6), not a separate metadata table.

| Field | Type | Nullable | Notes |
|---|---|---|---|
| queue_id | String | No | PK |
| observation_id | String | No | Indexed. Source row is immutable — no snapshot fields needed |
| queue_timestamp | DateTime | No | Set on enqueue |
| enrichment_status | String (EnrichmentStatusEnum) | No | `PENDING` if `enrichment_applicable`, else `NOT_APPLICABLE` |
| enrichment_no_of_attempts | Integer | No | Default `0` |
| enrichment_latest_timestamp | DateTime | Yes | Last enrichment attempt |
| enrichment_latest_error_code | String | Yes | |
| computation_status | String (ProcessStatusEnum) | No | Default `PENDING`. Row only created if `computation_applicable` |
| computation_no_of_attempts | Integer | No | Default `0` |
| computation_latest_timestamp | DateTime | Yes | Last computation attempt |
| computation_latest_error_code | String | Yes | |

Enqueue rule: a row is created only if `enrichment_applicable` or `computation_applicable` is `true` for the observation's type. At creation:
- `enrichment_applicable = true` → `enrichment_status = PENDING`, `computation_status = PENDING`.
- `enrichment_applicable = false` → `enrichment_status = NOT_APPLICABLE`, `computation_status = PENDING`.

Open item: neither case covers `computation_applicable = false` (an enrichment-only type, no rollup). By symmetry this would need `computation_status = NOT_APPLICABLE` too, set from `computation_applicable` at enqueue — not yet confirmed as a requirement.

Pickup/dispatch logic lives entirely in Celery Beat — see Section 6.

#### 2.4 `G2PRegisterObservationAggregate` — table `g2p_register_observation_aggregates`

| Field | Type | Nullable | Notes |
|---|---|---|---|
| aggregate_id | String | No | PK |
| internal_record_id | String | No | Indexed |
| register_mnemonic | String | No | Indexed. Required to know which register/table `internal_record_id` resolves against |
| aggregate_type | String | No | Indexed |
| period_key | String | No | Indexed, e.g. `2018_SUMMER_IRRIGATED`. Adapter-defined label, format not enforced by the platform |
| period_start_date | Date | No | Indexed. Adapter-derived; the generic sortable/rangeable anchor `period_key` alone doesn't provide |
| period_end_date | Date | No | Adapter-derived |
| aggregate_value | JSONB | No | Computed measures |
| geo_dimensions | JSONB | Yes | Resolved by `COMPUTATION_WORKER` from `internal_record_id`/`register_mnemonic`'s geo hierarchy — never adapter-populated |
| custom_dimensions | JSONB | Yes | Populated by the computation adapter; shape is specific to `aggregate_type` |
| computed_at | DateTime | No | |

Unique index: `(internal_record_id, aggregate_type, period_key)`. `register_mnemonic` is not part of the key — `internal_record_id` values are already unique platform-wide (`uuid4`).

#### 2.5 `G2PRegisterObservationAggregateHistory` — table `g2p_register_observation_aggregate_history`

Same fields as 2.4, plus `history_id` (PK). No unique constraint. Append-only.

#### 2.6 Interfaces and Factories

**Result type and interfaces** (`core/openg2p-registry-core/src/openg2p_registry_core/interfaces/`):

```python
# g2p_observation_result.py

from dataclasses import dataclass
from datetime import date
from typing import Any, Optional


@dataclass(frozen=True)
class ObservationAggregationResult:
    """One row COMPUTATION_WORKER will upsert into g2p_register_observation_aggregates.

    geo_dimensions is deliberately absent here — it is resolved by COMPUTATION_WORKER
    from internal_record_id/register_mnemonic, never returned by the adapter.
    """

    internal_record_id: str
    register_mnemonic: str
    aggregate_type: str
    period_key: str
    period_start_date: date
    period_end_date: date
    aggregate_value: dict[str, Any]
    custom_dimensions: Optional[dict[str, Any]] = None
```

```python
# g2p_observation_enricher_interface.py

from abc import ABC, abstractmethod
from typing import Any

from openg2p_registry_core.models import G2PObservation


class G2PObservationEnricherInterface(ABC):
    """Resolved per observation_type by G2PObservationAdapterFactory.get_enricher()."""

    @abstractmethod
    async def enrich(self, observation: G2PObservation) -> dict[str, Any]:
        """Return the JSON document ENRICHMENT_WORKER upserts into
        g2p_observations_payload.payload_enriched. Must not mutate
        g2p_observations or g2p_observations_payload.payload.
        """
        raise NotImplementedError
```

```python
# g2p_observation_computation_interface.py

from abc import ABC, abstractmethod

from openg2p_registry_core.interfaces.g2p_observation_result import ObservationAggregationResult
from openg2p_registry_core.models import G2PObservation


class G2PObservationComputationInterface(ABC):
    """Resolved per observation_type by G2PObservationAdapterFactory.get_computer()."""

    @abstractmethod
    async def compute(self, observation: G2PObservation) -> list[ObservationAggregationResult]:
        """Return zero, one, or several aggregation results for this observation.

        The adapter fetches whatever further g2p_observations / g2p_observations_payload
        rows it needs itself (e.g. a related_observation_id chain — Section 8, steps 3-6).

        period_start_date/period_end_date are derived here too: mechanical date
        arithmetic off observation.observed_at for calendar-grain periods (month/
        quarter/year — a shared helper can serve every adapter needing this, since
        the logic is identical regardless of aggregate_type), or a domain-specific
        lookup for business-grain periods (season, program cycle) where the range
        isn't derivable from observed_at at all — e.g. mapping payload.season =
        "SUMMER_IRRIGATED" through a season-calendar table this adapter owns.
        """
        raise NotImplementedError
```

**Factory** — one factory, not two, resolving both interfaces by naming convention off `observation_type`, same dynamic-import pattern as `G2PScoreComputeFactory`:

```python
# g2p_observation_adapter_factory.py

import importlib

from openg2p_registry_core.interfaces.g2p_observation_computation_interface import (
    G2PObservationComputationInterface,
)
from openg2p_registry_core.interfaces.g2p_observation_enricher_interface import (
    G2PObservationEnricherInterface,
)

_EXTENSION_MODULE = "openg2p_registry_extensions.observation_compute.services"


def _title_case(observation_type: str) -> str:
    """CROP_HARVEST_EVENT -> CropHarvestEvent"""
    return "".join(part.capitalize() for part in observation_type.split("_"))


class G2PObservationAdapterFactory:
    """Resolution key is observation_type, not aggregate_type or register_mnemonic —
    an adapter is chosen per observation type, and its compute() decides internally
    which aggregate_type(s) to produce.

    Caution: observation_type is scoped per register_mnemonic (Section 2.2), not
    globally unique. If the same observation_type string is ever defined under two
    different register_mnemonics with genuinely different behavior, this convention
    (keyed on observation_type alone) resolves both to the same class, which may be
    wrong. The current catalog (Section 5) never reuses a name across
    register_mnemonics, so this doesn't arise today — if it does, fold
    register_mnemonic into the class name too, e.g.
    G2PObservationComputer{RegisterMnemonic}{TitleCase(observation_type)}.
    """

    @staticmethod
    def get_enricher(observation_type: str) -> G2PObservationEnricherInterface:
        class_name = f"G2PObservationEnricher{_title_case(observation_type)}"
        module = importlib.import_module(_EXTENSION_MODULE)
        try:
            enricher_class = getattr(module, class_name)
        except AttributeError as exc:
            raise ValueError(
                f"No enricher registered for observation_type={observation_type!r} "
                f"(expected class {class_name} in {_EXTENSION_MODULE})"
            ) from exc
        return enricher_class()

    @staticmethod
    def get_computer(observation_type: str) -> G2PObservationComputationInterface:
        class_name = f"G2PObservationComputer{_title_case(observation_type)}"
        module = importlib.import_module(_EXTENSION_MODULE)
        try:
            computer_class = getattr(module, class_name)
        except AttributeError as exc:
            raise ValueError(
                f"No computer registered for observation_type={observation_type!r} "
                f"(expected class {class_name} in {_EXTENSION_MODULE})"
            ) from exc
        return computer_class()
```

For each result an adapter returns, `COMPUTATION_WORKER` resolves `geo_dimensions` itself from that result's own `internal_record_id`/`register_mnemonic` (its geo hierarchy) — a generic step applied uniformly regardless of `aggregate_type`, so no adapter implements geo resolution. `COMPUTATION_WORKER` then upserts each result (with its resolved `geo_dimensions`) into `g2p_register_observation_aggregates` (Section 2.4) and appends it to `g2p_register_observation_aggregate_history` (Section 2.5).

---

### 3. Observation Envelope Design

Envelope = every column on `G2PObservation` (Section 2.1). `payload`/`payload_enriched` are not envelope columns at all — they live in the separate `G2PObservationPayload` table (Section 2.1.1).

| Purpose | Fields |
|---|---|
| Identity | `observation_id` |
| Classification | `observation_type`, `schema_version` |
| Subject linkage | `internal_record_id`, `register_mnemonic` |
| Timing | `observed_at`, `created_at` |
| Provenance | `created_by`, `submission_id`, `source` |
| Location | `latitude`, `longitude` |
| Lifecycle | `record_status`, `related_observation_id`, `relation_type` |

---

### 4. Observation Payload Metadata Design

`G2PObservationTypeDefinition.payload_json_schema` holds a JSON Schema document per `(register_mnemonic, observation_type)` pair — not per `observation_type` alone, since a type has no meaning outside its owning `register_mnemonic` (Section 2.2). Validation runs at write time: the incoming observation's own `(register_mnemonic, observation_type)` looks up the one matching definition, then `jsonschema.validate(payload, definition.payload_json_schema)`.

Write path: one transaction inserts one `g2p_observations` row and one `g2p_observations_payload` row. Validation runs against the payload before either insert commits.

`schema_version` on `G2PObservationTypeDefinition` increments on any schema change. `schema_version` on `G2PObservation` stores the version active at capture time.

Enumerated payload fields reference `G2PAttribute`/`G2PAttributeValue` code lists (`core/.../models/g2p_attributes.py`) where an equivalent code list already exists (e.g. `commodity_code` reuses the same list as `G2PCrop.commodity`).

Reportable payload keys per `observation_type` are declared in `reporting.yaml`/`reporting_views.sql` (farmer-registry), one entry per key that a materialized reporting view extracts.

---

### 5. Observation Types

Each row is a complete, self-contained `G2PObservationTypeDefinition` — nested under exactly one `register_mnemonic`, not cross-referenced from elsewhere.

| register_mnemonic | observation_type | follows_observation_type | Payload fields |
|---|---|---|---|
| `IndividualLand` | `CROP_SOWING_EVENT` | — | `commodity_code`, `season`, `sowing_method`, `area_sown_ha`, `seed_variety`, `seed_source`, `is_cluster_participant`, `cluster_id`, `notes`, `photo_document_ids` |
| `IndividualLand` | `CROP_HARVEST_EVENT` | `CROP_SOWING_EVENT` | `collected_land_ha`, `collected_product_quintal`, `harvest_method`, `is_cluster_participant`, `cluster_id`, `notes`, `photo_document_ids` |
| `IndividualLivestock` | `LIVESTOCK_HEALTH_EVENT` | — | `health_status`, `vaccination_type`, `treatment_notes`, `photo_document_ids` |
| `Household` | `HOUSEHOLD_FOOD_SECURITY_SURVEY` | — | `food_security_score`, `meals_per_day`, `coping_strategy`, `notes` |
| `IndividualLand` | `WEATHER_OBSERVATION` | — | `rainfall_mm`, `temperature_c`, `event_type`, `notes` |

#### 5.1 `payload_json_schema` — `IndividualLand` / `CROP_SOWING_EVENT`

```json
{
  "type": "object",
  "required": ["commodity_code", "season", "sowing_method", "area_sown_ha"],
  "properties": {
    "commodity_code": {"type": "string", "enum": ["WHEAT", "MAIZE", "TEFF", "BARLEY", "RICE", "SORGHUM", "SOYA_BEAN"]},
    "season": {"type": "string", "pattern": "^[0-9]{4}_(SUMMER|BELG|MEHER)_(IRRIGATED|RAINFED)$"},
    "sowing_method": {"type": "string", "enum": ["MANUAL", "TRACTOR", "CLUSTER_TRACTOR"]},
    "area_sown_ha": {"type": "number", "minimum": 0},
    "seed_variety": {"type": "string"},
    "seed_source": {"type": "string", "enum": ["OWN", "GOVERNMENT_SUBSIDY", "COOPERATIVE", "MARKET"]},
    "is_cluster_participant": {"type": "boolean"},
    "cluster_id": {"type": "string"},
    "notes": {"type": "string"},
    "photo_document_ids": {"type": "array", "items": {"type": "string"}}
  }
}
```

#### 5.2 `payload_json_schema` — `IndividualLand` / `CROP_HARVEST_EVENT`

```json
{
  "type": "object",
  "required": ["collected_land_ha", "collected_product_quintal", "harvest_method"],
  "properties": {
    "collected_land_ha": {"type": "number", "minimum": 0},
    "collected_product_quintal": {"type": "number", "minimum": 0},
    "harvest_method": {"type": "string", "enum": ["MANUAL", "COMBINE", "CLUSTER_COMBINE"]},
    "is_cluster_participant": {"type": "boolean"},
    "cluster_id": {"type": "string"},
    "notes": {"type": "string"},
    "photo_document_ids": {"type": "array", "items": {"type": "string"}}
  }
}
```

---

### 6. Celery Beat and Workers

#### 6.1 `observation_processing_beat_producer` (Celery Beat)

Single beat task, fixed polling interval (`observation_processing_beat_producer_frequency` setting — same convention as the platform's existing `score_compute_beat_producer_frequency`).

Each tick:
1. Query `g2p_observation_processing_queue` for rows matching either:
   - `enrichment_status = 'PENDING'`, OR
   - `computation_status = 'PENDING'` AND `enrichment_status IN ('COMPLETED', 'NOT_APPLICABLE')`.
2. For each matched row, dispatch to exactly one worker — never both from the same row on the same tick:
   - If `enrichment_status = 'PENDING'` → mark `enrichment_status = 'PROCESSING'`, `celery_app.send_task(ENRICHMENT_WORKER, queue_id)`.
   - Else (`computation_status = 'PENDING'`, enrichment already resolved) → mark `computation_status = 'PROCESSING'`, `celery_app.send_task(COMPUTATION_WORKER, queue_id)`.

A row whose `enrichment_status` is still `PENDING` is therefore always dispatched for enrichment first; it only becomes computation-eligible on a later tick, once `enrichment_status` reaches `COMPLETED` (or was `NOT_APPLICABLE` from enqueue).

#### 6.2 `ENRICHMENT_WORKER`

1. Load the queue row (`queue_id`), its `g2p_observations` row, and its `g2p_observations_payload` row.
2. Resolve `G2PObservationAdapterFactory.get_enricher(observation_type) -> G2PObservationEnricherInterface` (Section 2.6).
3. Call `enricher.enrich(observation)` → JSON.
4. Upsert the returned JSON into `g2p_observations_payload.payload_enriched` for this `observation_id`. This never touches `g2p_observations` (Section 2.1.1).
5. On success: `enrichment_status = COMPLETED`, `enrichment_latest_timestamp = now()`.
6. On failure: increment `enrichment_no_of_attempts`; `enrichment_status = PENDING` (retry) if attempts remain, else `FAILED`; record `enrichment_latest_error_code`.
7. Never touches `computation_status` — it stays `PENDING`, picked up by Beat on a later tick.

#### 6.3 `COMPUTATION_WORKER`

1. Load the queue row (`queue_id`) and its `g2p_observations` row.
2. Resolve `G2PObservationAdapterFactory.get_computer(observation_type) -> G2PObservationComputationInterface` (Section 2.6).
3. Call `computer.compute(observation)` → `list[ObservationAggregationResult]`. The adapter fetches whatever further `g2p_observations`/`g2p_observations_payload` rows it needs — e.g. a `related_observation_id`-linked observation (Section 8, steps 3–6).
4. For each result, resolve `geo_dimensions` from that result's own `internal_record_id`/`register_mnemonic` — worker-owned, never adapter-owned (Section 2.6).
5. Upsert each result (with its resolved `geo_dimensions`) into `g2p_register_observation_aggregates`; append each to `g2p_register_observation_aggregate_history`.
6. On success: `computation_status = COMPLETED`, `computation_latest_timestamp = now()`.
7. On failure: increment `computation_no_of_attempts`; `computation_status = PENDING` (retry) if attempts remain, else `FAILED`; record `computation_latest_error_code`.

#### 6.4 Dispatch table

| enrichment_status | computation_status | Beat dispatches to |
|---|---|---|
| `PENDING` | `PENDING` | `ENRICHMENT_WORKER` |
| `PROCESSING` or `FAILED` | `PENDING` | *(nothing yet — not eligible)* |
| `COMPLETED` or `NOT_APPLICABLE` | `PENDING` | `COMPUTATION_WORKER` |
| `COMPLETED` or `NOT_APPLICABLE` | `COMPLETED`, `PROCESSING`, or `FAILED` | *(nothing — done, in flight, or terminally failed)* |

---

### 7. Sample Records — Crop Sown / Harvest (based on PDF: Amhara, Wheat, 2018 summer irrigated)

**obs-0001 — initial sowing record, Farmer X, plot land-77abf3**

`g2p_observations`:
```json
{
  "observation_id": "obs-0001",
  "observation_type": "CROP_SOWING_EVENT",
  "internal_record_id": "land-77abf3",
  "register_mnemonic": "IndividualLand",
  "observed_at": "2018-06-15T00:00:00Z",
  "created_by": "agent-014",
  "source": "AGENT_APP",
  "latitude": 11.5936,
  "longitude": 37.3908,
  "record_status": "ARCHIVED",
  "related_observation_id": null,
  "relation_type": null,
  "schema_version": 1
}
```
`g2p_observations_payload`:
```json
{
  "observation_id": "obs-0001",
  "payload": {
    "commodity_code": "WHEAT",
    "season": "2018_SUMMER_IRRIGATED",
    "sowing_method": "TRACTOR",
    "area_sown_ha": 0.75,
    "seed_variety": "Kubsa",
    "seed_source": "GOVERNMENT_SUBSIDY",
    "is_cluster_participant": true,
    "cluster_id": "CLU-AMH-014"
  },
  "payload_enriched": null
}
```

**obs-0002 — correction of obs-0001 (`VOIDS`)**

`g2p_observations`:
```json
{
  "observation_id": "obs-0002",
  "observation_type": "CROP_SOWING_EVENT",
  "internal_record_id": "land-77abf3",
  "register_mnemonic": "IndividualLand",
  "observed_at": "2018-06-15T00:00:00Z",
  "created_by": "agent-014",
  "source": "AGENT_APP",
  "latitude": 11.5936,
  "longitude": 37.3908,
  "record_status": "ACTIVE",
  "related_observation_id": "obs-0001",
  "relation_type": "VOIDS",
  "schema_version": 1
}
```
`g2p_observations_payload`:
```json
{
  "observation_id": "obs-0002",
  "payload": {
    "commodity_code": "WHEAT",
    "season": "2018_SUMMER_IRRIGATED",
    "sowing_method": "TRACTOR",
    "area_sown_ha": 0.85,
    "seed_variety": "Kubsa",
    "seed_source": "GOVERNMENT_SUBSIDY",
    "is_cluster_participant": true,
    "cluster_id": "CLU-AMH-014"
  },
  "payload_enriched": null
}
```

**obs-0003 — harvest for obs-0002 (`FOLLOWS`)**

`g2p_observations`:
```json
{
  "observation_id": "obs-0003",
  "observation_type": "CROP_HARVEST_EVENT",
  "internal_record_id": "land-77abf3",
  "register_mnemonic": "IndividualLand",
  "observed_at": "2018-10-20T00:00:00Z",
  "created_by": "agent-014",
  "source": "AGENT_APP",
  "latitude": 11.5936,
  "longitude": 37.3908,
  "record_status": "ACTIVE",
  "related_observation_id": "obs-0002",
  "relation_type": "FOLLOWS",
  "schema_version": 1
}
```
`g2p_observations_payload`:
```json
{
  "observation_id": "obs-0003",
  "payload": {
    "collected_land_ha": 0.80,
    "collected_product_quintal": 13.6,
    "harvest_method": "CLUSTER_COMBINE",
    "is_cluster_participant": true,
    "cluster_id": "CLU-AMH-014"
  },
  "payload_enriched": null
}
```

**obs-0004 — sowing, Farmer Y, plot land-9c21e0, no cluster**

`g2p_observations`:
```json
{
  "observation_id": "obs-0004",
  "observation_type": "CROP_SOWING_EVENT",
  "internal_record_id": "land-9c21e0",
  "register_mnemonic": "IndividualLand",
  "observed_at": "2018-06-18T00:00:00Z",
  "created_by": "agent-014",
  "source": "AGENT_APP",
  "record_status": "ACTIVE",
  "related_observation_id": null,
  "relation_type": null,
  "schema_version": 1
}
```
`g2p_observations_payload`:
```json
{
  "observation_id": "obs-0004",
  "payload": {
    "commodity_code": "WHEAT",
    "season": "2018_SUMMER_IRRIGATED",
    "sowing_method": "MANUAL",
    "area_sown_ha": 0.40,
    "seed_variety": "Kubsa",
    "seed_source": "OWN",
    "is_cluster_participant": false
  },
  "payload_enriched": null
}
```

**obs-0005 — harvest for obs-0004 (`FOLLOWS`)**

`g2p_observations`:
```json
{
  "observation_id": "obs-0005",
  "observation_type": "CROP_HARVEST_EVENT",
  "internal_record_id": "land-9c21e0",
  "register_mnemonic": "IndividualLand",
  "observed_at": "2018-10-22T00:00:00Z",
  "created_by": "agent-014",
  "source": "AGENT_APP",
  "record_status": "ACTIVE",
  "related_observation_id": "obs-0004",
  "relation_type": "FOLLOWS",
  "schema_version": 1
}
```
`g2p_observations_payload`:
```json
{
  "observation_id": "obs-0005",
  "payload": {
    "collected_land_ha": 0.38,
    "collected_product_quintal": 6.1,
    "harvest_method": "MANUAL",
    "is_cluster_participant": false
  },
  "payload_enriched": null
}
```

---

### 8. Sample Rollup Computation — Farmer Level

`G2PObservationTypeDefinition` for `(IndividualLand, CROP_HARVEST_EVENT)`: `enrichment_applicable = false`, `computation_applicable = true`.

**Trigger**: insert of `obs-0003` (`CROP_HARVEST_EVENT`) enqueues one `G2PObservationProcessingQueue` row with `enrichment_status = NOT_APPLICABLE`, `computation_status = PENDING`.

**Beat**: this row is dispatched straight to `COMPUTATION_WORKER` on the first tick that sees it — `enrichment_status` is already `NOT_APPLICABLE`, so Beat never routes it to `ENRICHMENT_WORKER` (Section 6).

**COMPUTATION_WORKER steps**:
1. Receive `queue_id` from Beat → `computation_status = PENDING`, `enrichment_status = NOT_APPLICABLE` → eligible.
2. Resolve `G2PObservationAdapterFactory.get_computer("CROP_HARVEST_EVENT")` → `G2PObservationComputerCropHarvestEvent`.
3. Fetch `g2p_observations` row for `obs-0003` (envelope only, no payload IO yet), read `internal_record_id` (`land-77abf3`, mnemonic `IndividualLand`) and `related_observation_id` (`obs-0002`, `relation_type = FOLLOWS`) → fetch the `g2p_observations` envelope row for the sowing observation `obs-0002`.
4. Resolve `land-77abf3` up the `master_register_id` chain to its owning `Individual` (`individual-55f2`) via `G2PRegisterHierarchicalService`.
5. Adapter fetches `g2p_observations_payload` rows for `obs-0002` and `obs-0003` — the only step in this walkthrough that reads the payload table.
6. Adapter reads `payload.area_sown_ha` from `obs-0002` (`0.85`), `payload.collected_land_ha` (`0.80`) and `payload.collected_product_quintal` (`13.6`) from `obs-0003`, computes `yield_quintal_per_ha = collected_product_quintal / collected_land_ha = 17.0`.
7. Adapter reads `payload.season = "2018_SUMMER_IRRIGATED"` from `obs-0002` for `period_key`, then maps the `"SUMMER_IRRIGATED"` season code through its own season-calendar table to get `period_start_date = 2018-06-01`, `period_end_date = 2018-10-31` — not derived from `obs-0003`'s `observed_at`, since that's one harvest date inside the season window, not the window's boundary.
8. Adapter returns `[{internal_record_id: "individual-55f2", register_mnemonic: "Individual", aggregate_type: "SEASON_CROP_YIELD_SUMMARY", period_key: "2018_SUMMER_IRRIGATED", period_start_date: "2018-06-01", period_end_date: "2018-10-31", aggregate_value: {...}, custom_dimensions: {"primary_commodity": "WHEAT"}}]`.
9. Worker resolves `geo_dimensions` for the result from `individual-55f2`'s geo hierarchy, then upserts the result (with its resolved `geo_dimensions`) into `g2p_register_observation_aggregates` and appends to `g2p_register_observation_aggregate_history`; sets `computation_status = COMPLETED`.

**Result row (`g2p_register_observation_aggregates`)**:
```json
{
  "aggregate_id": "agg-1001",
  "internal_record_id": "individual-55f2",
  "register_mnemonic": "Individual",
  "aggregate_type": "SEASON_CROP_YIELD_SUMMARY",
  "period_key": "2018_SUMMER_IRRIGATED",
  "period_start_date": "2018-06-01",
  "period_end_date": "2018-10-31",
  "aggregate_value": {
    "total_area_sown_ha": 0.85,
    "total_area_collected_ha": 0.80,
    "total_production_quintal": 13.6,
    "yield_quintal_per_ha": 17.0,
    "by_commodity": {
      "WHEAT": {"area_sown_ha": 0.85, "production_quintal": 13.6}
    }
  },
  "geo_dimensions": {
    "region_id": "AMH",
    "region_name": "Amhara"
  },
  "custom_dimensions": {
    "primary_commodity": "WHEAT"
  },
  "computed_at": "2018-10-21T02:00:00Z"
}
```

---

### 9. Sample Rollup Computation — Region Level

Materialized view: `fr_rpt_observation_crop_performance` (`farmer-registry/docker/db-seed/reporting_views.sql`, `custom:` path in `reporting.yaml`).

**View grouping columns**: `geo_1` (region), `geo_2`, `geo_3`, `commodity_code`, `season`.

**View steps**:
1. Source rows: `g2p_observations` where `observation_type IN ('CROP_SOWING_EVENT', 'CROP_HARVEST_EVENT')` and `record_status = 'ACTIVE'`.
2. Join `g2p_observations_payload` on `observation_id` — this view needs payload contents, unlike Section 8's envelope-only lookups.
3. Join `IndividualLand` → `Individual` → `Household` for `geo_1..geo_5` (same inheritance mechanism as `fr_rpt_crop`).
4. Unpack `payload.commodity_code`, `payload.season`, `payload.area_sown_ha`, `payload.collected_land_ha`, `payload.collected_product_quintal`, `payload.is_cluster_participant`.
5. Group by `(geo_1, commodity_code, season)`.
6. Aggregate: `SUM(area_sown_ha)`, `SUM(area_sown_ha) FILTER (WHERE is_cluster_participant)`, `SUM(collected_land_ha)`, `SUM(collected_product_quintal)`, `COUNT(DISTINCT farmer_id)`, `COUNT(DISTINCT farmer_id) FILTER (WHERE gender = 'MALE')`, `COUNT(DISTINCT farmer_id) FILTER (WHERE gender = 'FEMALE')`.
7. Compute `productivity_quintal_per_ha = SUM(collected_product_quintal) / NULLIF(SUM(collected_land_ha), 0)`.

**Sample output row (Amhara, Wheat, 2018 summer irrigated — computed from obs-0001..obs-0005)**:

| geo_1 | commodity_code | season | total_farmers | male | female | total_area_sown_ha | area_sown_ha_cluster | total_area_collected_ha | total_production_quintal | productivity_quintal_per_ha |
|---|---|---|---|---|---|---|---|---|---|---|
| Amhara | WHEAT | 2018_SUMMER_IRRIGATED | 2 | 2 | 0 | 1.25 | 0.85 | 1.18 | 19.7 | 16.69 |

This row is the same shape as the PDF's regional wheat performance table (planned/sown/collected land in hectares, collected product in quintals, cluster vs. non-cluster split, participant farmer counts by gender, productivity ratio), populated from individual `g2p_observations` rows instead of a manually compiled spreadsheet.

---

### Observations - Tabular Presentation

**Envelope fields** — `g2p_observations`

| observation_id | observation_type | internal_record_id | register_mnemonic | observed_at | record_status | related_observation_id | relation_type |
|---|---|---|---|---|---|---|---|
| obs-0001 | CROP_SOWING_EVENT | land-77abf3 | IndividualLand | 2018-06-15T00:00:00Z | ARCHIVED | — | — |
| obs-0002 | CROP_SOWING_EVENT | land-77abf3 | IndividualLand | 2018-06-15T00:00:00Z | ACTIVE | obs-0001 | VOIDS |
| obs-0003 | CROP_HARVEST_EVENT | land-77abf3 | IndividualLand | 2018-10-20T00:00:00Z | ACTIVE | obs-0002 | FOLLOWS |
| obs-0004 | CROP_SOWING_EVENT | land-9c21e0 | IndividualLand | 2018-06-18T00:00:00Z | ACTIVE | — | — |
| obs-0005 | CROP_HARVEST_EVENT | land-9c21e0 | IndividualLand | 2018-10-22T00:00:00Z | ACTIVE | obs-0004 | FOLLOWS |

**Payload fields** — `g2p_observations_payload` (columns match Section 2.1.1 exactly; `payload`/`payload_enriched` are single JSONB cells, not flattened)

| observation_id | payload | payload_enriched |
|---|---|---|
| obs-0001 | `{"commodity_code": "WHEAT", "season": "2018_SUMMER_IRRIGATED", "sowing_method": "TRACTOR", "area_sown_ha": 0.75, "seed_variety": "Kubsa", "seed_source": "GOVERNMENT_SUBSIDY", "is_cluster_participant": true, "cluster_id": "CLU-AMH-014"}` | `null` |
| obs-0002 | `{"commodity_code": "WHEAT", "season": "2018_SUMMER_IRRIGATED", "sowing_method": "TRACTOR", "area_sown_ha": 0.85, "seed_variety": "Kubsa", "seed_source": "GOVERNMENT_SUBSIDY", "is_cluster_participant": true, "cluster_id": "CLU-AMH-014"}` | `null` |
| obs-0003 | `{"collected_land_ha": 0.80, "collected_product_quintal": 13.6, "harvest_method": "CLUSTER_COMBINE", "is_cluster_participant": true, "cluster_id": "CLU-AMH-014"}` | `null` |
| obs-0004 | `{"commodity_code": "WHEAT", "season": "2018_SUMMER_IRRIGATED", "sowing_method": "MANUAL", "area_sown_ha": 0.40, "seed_variety": "Kubsa", "seed_source": "OWN", "is_cluster_participant": false}` | `null` |
| obs-0005 | `{"collected_land_ha": 0.38, "collected_product_quintal": 6.1, "harvest_method": "MANUAL", "is_cluster_participant": false}` | `null` |

**Aggregate fields** — `g2p_register_observation_aggregates` (columns match Section 2.4 exactly; `aggregate_value`/`geo_dimensions`/`custom_dimensions` are single JSONB cells)

| aggregate_id | internal_record_id | register_mnemonic | aggregate_type | period_key | period_start_date | period_end_date | aggregate_value | geo_dimensions | custom_dimensions | computed_at |
|---|---|---|---|---|---|---|---|---|---|---|
| agg-1001 | individual-55f2 | Individual | SEASON_CROP_YIELD_SUMMARY | 2018_SUMMER_IRRIGATED | 2018-06-01 | 2018-10-31 | `{"total_area_sown_ha": 0.85, "total_area_collected_ha": 0.80, "total_production_quintal": 13.6, "yield_quintal_per_ha": 17.0, "by_commodity": {"WHEAT": {"area_sown_ha": 0.85, "production_quintal": 13.6}}}` | `{"region_id": "AMH", "region_name": "Amhara"}` | `{"primary_commodity": "WHEAT"}` | 2018-10-21T02:00:00Z |

---

### 10. Field Recording UX Design

#### 10.1 Search model

Two distinct search modes, not one general-purpose search box.

**Contextual (default)** — every observation is recorded from inside a subject's profile (Farmer, Land, Livestock). That profile carries an **Observations** tab: a timeline of that subject's own observations only, pre-scoped by `internal_record_id`, sorted by `observed_at` descending, filter chips for `observation_type` and `season`. No search input needed for this mode — the agent is already looking at the plot/animal they're recording for, and the candidate list is short (a handful of observations per subject per season).

**Open-ended (secondary)** — a search bar for the case where the agent has not yet navigated to the subject: filters on farmer name/functional ID, `observation_type`, season, date range. Query scope is the agent's synced offline dataset (their assigned route/cluster for the current season), not a live full-registry search.

#### 10.2 Recording a new observation — screen flow

1. **Subject profile → Observations tab → "+ Record Observation."**
2. **Type picker** — list of `observation_type` values from every `G2PObservationTypeDefinition` row (Section 2.2) whose `register_mnemonic` equals this subject's own `register_mnemonic`. Existence of a definition row *is* what makes a type valid here — no separate allowed/disallowed check. A Land profile shows `CROP_SOWING_EVENT`, `CROP_HARVEST_EVENT`, `WEATHER_OBSERVATION` (all three defined under `IndividualLand`, Section 5); a Livestock profile shows `LIVESTOCK_HEALTH_EVENT` (defined under `IndividualLivestock`).
3. **Form screen** — rendered directly from `payload_json_schema` (Section 4). Enum fields render as choice chips, not free text. Required fields marked from the schema's `required` list.

#### 10.3 Envelope auto-fill

None of the envelope fields (Section 3) are hand-entered on the form.

| Field | Source |
|---|---|
| `internal_record_id`, `register_mnemonic` | current subject context |
| `observed_at` | device clock, defaults to now, editable for backdating |
| `latitude`, `longitude` | device GPS, manual pin-drop fallback |
| `created_by` | logged-in agent |
| `source` | fixed per client build, e.g. `AGENT_APP` |
| `schema_version` | active version of the type definition at submit time |

#### 10.4 Smart defaults

Payload fields pre-fill from the most recent `ACTIVE` observation of the same `observation_type` for the same subject (`commodity_code`, `seed_variety`, `sowing_method`, `cluster_id` carry over from last season's entry). Agent edits only what changed.

#### 10.5 Correcting a record (`VOIDS`)

1. From the Observations timeline, tap a past record → **"Correct this record."**
2. The same form opens, pre-filled with that record's existing payload.
3. Agent edits only the wrong fields.
4. On submit, the client sets `related_observation_id` = the tapped record's `observation_id` and `relation_type = VOIDS` automatically — the agent never sees or enters an ID.
5. The original record is shown in the timeline greyed out / struck through, labeled "Superseded," tappable to view the correction chain.

#### 10.6 Linking a lifecycle step (`FOLLOWS`)

This is one generic capability in the UI, not custom code per `observation_type`. It activates whenever `G2PObservationTypeDefinition.follows_observation_type` (Section 2.2) is non-null for the type being recorded — currently only `(IndividualLand, CROP_HARVEST_EVENT)`, which declares `follows_observation_type = CROP_SOWING_EVENT` (Section 5). Nothing in the client hardcodes "harvest follows sowing"; it reads that pairing from the type definition and reacts the same way for any other type that declares one.

1. Before showing the form, the client checks `follows_observation_type` on the type definition. If null, skip straight to the form (Section 10.2) — no FOLLOWS step at all.
2. If set, query this subject's `ACTIVE` observations of that type that are not yet `FOLLOWS`-linked by anything ("open" candidates) — one generic query, parameterized by whatever type the definition names.
3. **Exactly one open match** → auto-select it, show a confirmation chip built from its data (e.g. "Harvest for: Wheat, sown 15 Jun") — no picker shown.
4. **More than one open match** (e.g. double-cropping) → short list picker, agent taps one.
5. **Zero open matches** → form blocks submission with a message templated from metadata, not hardcoded per type: `"No open {display_name} found for this record — record one first"`, where `{display_name}` is the followed type's own `G2PObservationTypeDefinition.display_name`.
6. On submit, `related_observation_id`/`relation_type = FOLLOWS` set automatically from the selection.

#### 10.7 Offline behavior

Form submissions save to local storage immediately as drafts and sync opportunistically. Each entry in the Observations timeline carries a sync-status badge (`Pending sync` / `Synced`) so the agent can see what hasn't reached the server without needing connectivity to confirm it was captured.

#### 10.8 Screen inventory

1. Subject Profile → Observations tab (timeline, filter chips)
2. Observation Type picker (types defined under this subject's `register_mnemonic`, Section 2.2)
3. Record Observation form (schema-driven, envelope auto-filled)
4. Correct Observation form (same as 3, pre-filled, auto-`VOIDS`)
5. Link-to-prior picker (auto-selected when unambiguous, shown only when not)
6. Sync/pending queue indicator (timeline badge, no separate screen)

---

### 11. APIs

Exposed identically across `partner-api`, `staff-api`, and `bene-api` (differing only in auth/actor context, matching the platform's existing three-service split) — which service handles a given call is determined by which `source` prefix (`AGENT_*`/`PARTNER_*`, `STAFF_*`, `BENE_*`) the caller authenticates as.

Every endpoint is `POST` — no `GET` verb anywhere in this platform. A "fetch" endpoint is still `POST`, distinguished by a `get_`-prefixed path; all filters that would otherwise be query/path params go in the JSON request body instead.

#### 11.1 Metadata APIs — Observation Type Definitions

| Path | Request body | Purpose |
|---|---|---|
| `/create_observation_type` | `register_mnemonic`, `observation_type`, `payload_json_schema`, flags | Create a `G2PObservationTypeDefinition` (Section 2.2) |
| `/update_observation_type` | `register_mnemonic`, `observation_type`, fields to change | Update a definition (e.g. `schema_version` bump) |
| `/get_observation_type` | `register_mnemonic`, `observation_type` | Fetch one definition — used by the form renderer for `payload_json_schema` (Section 10.2, point 3) |
| `/get_observation_types` | `register_mnemonic` (optional) | List definitions; scoped to one `register_mnemonic` when given — the exact query behind the Type Picker (Section 10.2, point 2), or all definitions when omitted (admin/catalog use) |

Response body for a single definition = the `G2PObservationTypeDefinition` row (Section 2.2) verbatim — `payload_json_schema` returned as-is, since it's consumed directly by the schema-driven form renderer, not reprocessed.

#### 11.2 Data APIs — Observations

| Path | Request body | Purpose |
|---|---|---|
| `/record_observation` | envelope fields + `payload` (see below) | Record one observation. Validates `payload` against the resolved `(register_mnemonic, observation_type)` schema (Section 4), writes `g2p_observations` + `g2p_observations_payload` in one transaction, enqueues `G2PObservationProcessingQueue` (Section 2.3) |
| `/record_observations` | array of the above | Same, batch — the offline-sync path (Section 10.7) |
| `/get_observation` | `observation_id` | Fetch one observation — envelope (Section 2.1) joined with payload (Section 2.1.1) |
| `/get_observations` | `internal_record_id`, `observation_type`, `status`, `open` (bool) | Contextual timeline query (Section 10.1) — `open: true` is also the FOLLOWS-candidate query (Section 10.6, point 2) |
| `/search_observations` | `query`, `observation_type`, `season`, `date_from`, `date_to` | Open-ended search (Section 10.1, secondary mode) |

`open: true` filters to `record_status = 'ACTIVE'` and not yet pointed at by any other observation's `related_observation_id`/`relation_type = FOLLOWS` — the one generic query Section 10.6 depends on.

`/record_observation`'s request body supplies the envelope fields the caller owns (`observation_type`, `internal_record_id`, `register_mnemonic`, `observed_at`, `latitude`/`longitude`, `related_observation_id`/`relation_type` if correcting or following) plus `payload`; the server fills `observation_id`, `created_at`, `created_by`, `source`, `schema_version`.

**Example — `POST /record_observation`** (recording `obs-0003`, the harvest linked via `FOLLOWS` to `obs-0002`, Section 7):

Request:
```json
{
  "observation_type": "CROP_HARVEST_EVENT",
  "internal_record_id": "land-77abf3",
  "register_mnemonic": "IndividualLand",
  "observed_at": "2018-10-20T00:00:00Z",
  "latitude": 11.5936,
  "longitude": 37.3908,
  "related_observation_id": "obs-0002",
  "relation_type": "FOLLOWS",
  "payload": {
    "collected_land_ha": 0.80,
    "collected_product_quintal": 13.6,
    "harvest_method": "CLUSTER_COMBINE",
    "is_cluster_participant": true,
    "cluster_id": "CLU-AMH-014"
  }
}
```

Response: `200 OK`, body = the full `g2p_observations` row for `obs-0003` (Section 7).

#### 11.3 Data APIs — Observation Aggregates

| Path | Request body | Purpose |
|---|---|---|
| `/get_observation_aggregates` | `internal_record_id`, `aggregate_type` (optional) | Latest aggregate row(s) for a subject |
| `/get_observation_aggregate` | `internal_record_id`, `aggregate_type` | Latest single aggregate for a subject — the number a subject's profile surfaces |
| `/get_observation_aggregate_history` | `internal_record_id`, `aggregate_type` | Full `g2p_register_observation_aggregate_history` (Section 2.5) for that subject/aggregate_type — trend over time |

Read-only — nothing writes to `g2p_register_observation_aggregates` through this API; the only writer is `COMPUTATION_WORKER` (Section 6.3).

**Example — `POST /get_observation_aggregate`**

Request:
```json
{
  "internal_record_id": "individual-55f2",
  "aggregate_type": "SEASON_CROP_YIELD_SUMMARY"
}
```

Response body = the `agg-1001` row (Section 8), verbatim.
