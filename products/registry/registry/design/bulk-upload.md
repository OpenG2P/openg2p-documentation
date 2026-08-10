# Data Upload

## Data Upload — Feature Design Document

**Project:** OpenG2P Registry Gen2\
**Feature:** Data Upload (Bulk File Import + Ingestion Pipeline)\
**Status:** Implemented\
**Date:** 2026-05-05

***

### 1. Overview

Data Upload lets staff bulk-import register records from structured files (CSV, Excel, JSON, etc.) through the Staff Portal. Each row in the file is fed into the platform **ingestion pipeline** (transformation → intake form → register ingest). Register and intake form are known at enqueue time, so classification is skipped for file import.

The design follows the platform’s standard async pattern:

**configuration → upload → queue → beat/worker → ingest pipeline → intake form → register ingest**

Core provides all infrastructure (models, services, workers, APIs). Domain-specific mapping lives in **ingestion templates** (Jinja), **semantic patterns**, and optional **payload enrichers** in extensions.

Bulk upload is available **only via the Staff Portal**. Staff select an import-file configuration, upload a file, and the system processes it asynchronously row by row.

***

### 2. Scope and Constraints

* File import is an **input mechanism** alongside intake forms and verifiable credentials (`G2PInputMechanism.mechanism_type = IMPORT_FILE`).
* Each import is bound to a **register**, **intake form**, and **data model** via `G2PRegistryImportFileConfiguration`.
* Processing is **fully asynchronous**: the upload API returns after enqueueing; rows are processed in the background.
* Supported file formats: **CSV, TSV, XLSX, XLS, JSON, JSONL, XML**.
* Every row eventually becomes an **intake form submission** (ADD) or a **change request** (UPDATE), then flows through existing register-ingest workers.
* Register writes are **not direct** — they go through intake form finalization → `intake_form_register_ingest_worker`.
* File uploads for import are catalogued in `g2p_registry_documents` (intended bucket: `DATA_IMPORT_FILES`).
* **Idempotency**: re-processing the same `(document_id, record_number)` is skipped via `import_file_process_log`.

***

### 3. Design Across Repositories

| Repository / package | What it owns |
| --- | --- |
| `core/openg2p-registry-core` | Models, ingest service, ingestion config, import-file config, document handling |
| `celery/openg2p-registry-celery-beat-producers` | Beat producers for file processing and all ingest stages |
| `celery/openg2p-registry-celery-workers` | `import_file_process_worker`, transformation/ingest workers |
| `apis/openg2p-registry-staff-portal-api` | Staff APIs: enqueue import, import-file and ingestion configuration |
| `ui/staff-portal-ui` | Import modal, import-file configuration UI |
| Extensions (`openg2p_registry_extensions`) | Payload enrichers referenced by semantic patterns |

***

### 4. Data Model

#### 4.1 `G2PRegistryImportFileConfiguration`

Defines an import “template” staff can pick when uploading. Links register + intake form + data model.

**Location:** `core/openg2p-registry-core/src/openg2p_registry_core/models/g2p_registry_import_file_configuration.py`

```python
class G2PRegistryImportFileConfiguration(BaseORMModel):
    __tablename__ = "g2p_registry_import_file_configurations"

    import_file_configuration_id: Mapped[str]  # PK
    register_id: Mapped[str]
    form_id: Mapped[str]
    data_model_id: Mapped[str]
    import_file_template_mnemonic: Mapped[str]
    import_file_template_description: Mapped[str]
```

| Column | Purpose |
| --- | --- |
| `import_file_configuration_id` | PK |
| `register_id` | Target register |
| `form_id` | Target intake form |
| `data_model_id` | Data model for ingest envelope |
| `import_file_template_mnemonic` | Display name in UI |
| `import_file_template_description` | Description |

***

#### 4.2 `ImportFileProcessQueue`

One row per uploaded file awaiting processing.

**Location:** `core/openg2p-registry-core/src/openg2p_registry_core/models/import_file_process_queue.py`

```python
class ImportFileProcessQueue(BaseORMModel):
    __tablename__ = "import_file_process_queue"

    import_file_id: Mapped[str]  # PK
    document_id: Mapped[str]     # unique FK to g2p_registry_documents
    data_model_id: Mapped[str]
    register_id: Mapped[str]
    intake_form_id: Mapped[str]
    queued_at: Mapped[datetime]
    queued_by: Mapped[str | None]
    intake_form_ingestion_status: Mapped[ProcessStatusEnum]
    intake_form_ingestion_timestamp: Mapped[datetime | None]
    intake_form_ingestion_attempts: Mapped[int]
    intake_form_ingestion_error: Mapped[str | None]
    number_of_records_present: Mapped[int | None]
    number_of_records_ingested: Mapped[int | None]
```

| Column | Purpose |
| --- | --- |
| `import_file_id` | PK |
| `document_id` | FK to `g2p_registry_documents` (unique) |
| `data_model_id`, `register_id`, `intake_form_id` | Processing context |
| `queued_at`, `queued_by` | Audit |
| `intake_form_ingestion_status` | `PENDING` → `PROCESSING` → `PROCESSED` / `FAILED` |
| `number_of_records_present`, `number_of_records_ingested` | Result counters |

***

#### 4.3 `ImportFileProcessLog`

Per-row idempotency log.

**Location:** `core/openg2p-registry-core/src/openg2p_registry_core/models/import_file_process_log.py`

```python
class ImportFileProcessLog(BaseORMModel):
    __tablename__ = "import_file_process_log"

    import_file_record_id: Mapped[str]  # PK
    import_file_id: Mapped[str]
    document_id: Mapped[str]
    record_number: Mapped[int]
    ingestion_timestamp: Mapped[datetime]
    # Unique: (document_id, record_number)
```

Unique constraint: `(document_id, record_number)` — prevents duplicate ingest of the same row on retry.

***

#### 4.4 Ingestion Pipeline Tables

**Location:** `core/openg2p-registry-core/src/openg2p_registry_core/models/ingestion_pipeline.py`

**`incoming_raw_data`** — one row per ingested file row:

* `ingest_id`, `partner_id`, `data_model_id`
* `ingest_message_id`, `ingest_correlation_id`
* `classification_status` + attempt/error tracking

**`incoming_raw_data_payloads`** — raw JSON/XML/text payload + searchable `raw_data_text`

**`incoming_classified_data`** — resolved routing:

* `register_id`, `intake_form_id`, `semantic_pattern_id`
* `pipeline_action` (`ADD` / `UPDATE`)
* `section_id`, `internal_record_id` (for UPDATE)
* `transformation_status`, `ingestion_status`
* `intake_form_submission_id`, `change_request_id`

**`incoming_enriched_transformed_data`** — `enriched_data_json`, `transformed_data_json`

***

#### 4.5 Ingestion Configuration Tables

**Location:** `core/openg2p-registry-core/src/openg2p_registry_core/models/ingestion_configuration.py`

| Table | Purpose |
| --- | --- |
| `incoming_model_key_paths` | JSONPath extraction for message ID, sender, signature, list splitting |
| `incoming_model_register_semantic_patterns` | First-pass: resolve register + record identifier (ADD vs UPDATE) |
| `incoming_model_semantic_patterns` | Second-pass: resolve intake form / section + business payload path |
| `incoming_templates` | Jinja template per `(data_model_id, register_id)` |
| `g2p_input_mechanisms` | UI-visible input mechanisms per register |

***

### 5. Configuration (Admin Setup)

Before staff can upload, an administrator configures:

1. **Data model** — defines the ingest envelope shape.
2. **Incoming key paths** — how to read sender, message ID, signature, and optional list elements.
3. **Semantic patterns** — how to classify payload to register / intake form / section.
4. **Ingestion template** — Jinja mapping from enriched business payload → section-mnemonic keyed intake form structure.
5. **Import file configuration** — binds register + form + data model into a staff-selectable template.
6. **Input mechanism** — exposes `IMPORT_FILE` in the Staff Portal “New Intake” dropdown.

Configuration APIs live under `/ingestion-config/*` and `/input-mechanism-metadata/*`.

***

### 6. Staff Portal Upload Flow

#### 6.1 UI

1. Staff opens **New Intake → Import File** (`AddNewDropdown` → `ImportModal`).
2. Staff selects a configured import template (`useImportFileConfigs`).
3. Staff uploads a file → `POST /api/shared/upload-document` (catalogues in `g2p_registry_documents`).
4. UI calls `POST /api/input-mechanism/enqueue-import` → backend `POST /input-mechanism-data/enqueue_import_file`.

**Auth:** `intakeSubmission:edit`

#### 6.2 Enqueue Service

**Location:** `core/.../services/input_mechanism_data_service.py`

`InputMechanismDataService.enqueue_import_file()`:

1. Validates document exists.
2. Inserts `ImportFileProcessQueue` with `intake_form_ingestion_status = PENDING`.
3. Returns `import_file_id`.

***

### 7. File Processing Worker

#### 7.1 Beat Producer

**Location:** `celery/openg2p-registry-celery-beat-producers/.../tasks/import_file_process_beat_producer.py`

`import_file_process_beat_producer` polls `ImportFileProcessQueue` where status = `PENDING`, marks `PROCESSING`, dispatches `import_file_process_worker`.

**Config key:** `import_file_process_beat_producer_frequency`

#### 7.2 Worker Logic

**Location:** `celery/openg2p-registry-celery-workers/.../tasks/import_file_process_worker.py`

`import_file_process_worker(import_file_id)`:

```
1. Load queue item, data model, document metadata
2. Download file from MinIO via document handler
3. parse_file_to_records() → list[dict]  (one dict per row)
4. For each record_number:
   a. Skip if ImportFileProcessLog exists for (document_id, record_number)
   b. Build ingest envelope:
        headers: { message_id, sender_id, signature }  (from worker config)
        body:    row dict (flattened for JSON/XML)
   c. G2PIngestService.ingest_data(
        data_model_mnemonic,
        ingest_data,
        register_id=queue.register_id,
        intake_form_id=queue.intake_form_id,
      )
      → classification is bypassed (status = PROCESSED, IncomingClassifiedData pre-created)
   d. Insert ImportFileProcessLog; commit per row
5. Update queue: records_present, records_ingested, status = PROCESSED
```

**Why classification is skipped for file import:** `G2PIngestService.ingest_data()` accepts optional `register_id` + `intake_form_id`. When both are provided, it writes `IncomingClassifiedData` directly with `transformation_status = PENDING`.

**Supported formats:** `.csv`, `.tsv`, `.xlsx`, `.xls`, `.json`, `.jsonl`, `.xml`

***

### 8. Ingestion Pipeline (after file rows are enqueued)

For staff bulk upload, `register_id` and `intake_form_id` are supplied at ingest time, so classification is bypassed and each row starts at transformation. Subsequent stages:

#### 8.1 Stage 1 — Enrichment & Transformation

**Trigger:** `incoming_classified_data.transformation_status = PENDING`\
**Beat:** `ingest_data_transformation_beat_producer`\
**Worker:** `ingest_data_transformation_worker`

```
1. Extract business payload via semantic pattern JSONPath
2. Enrich via G2PPayloadEnricherFactory (extension class from semantic pattern)
3. Render Jinja ingestion template → transformed_data_json
      keyed by section_mnemonic → list[record dict]
4. Validate transformed payload (ADD: primary section required; UPDATE: target section required)
5. Set transformation_status = PROCESSED, ingestion_status = PENDING
```

***

#### 8.2 Stage 2 — Ingestion into Intake Form / Change Request

**Trigger:** `incoming_classified_data.ingestion_status = PENDING`\
**Beat:** `ingest_data_beat_producer`

Routes by `pipeline_action`:

| Action | Worker | Result |
| --- | --- | --- |
| `ADD` | `ingest_data_worker` | Creates intake form submission, saves sections, finalizes |
| `UPDATE` | `change_request_ingest_worker` | Creates change request for existing record section |

**`ingest_data_worker` (ADD) highlights:**

* Creates `G2PIntakeFormSubmission`
* Merges section records (handles list vs single-record sections)
* Finalizes submission (`draft_status = FINAL`)
* Links `intake_form_submission_id` on `IncomingClassifiedData`

***

#### 8.3 Stage 3 — Register Ingest (downstream)

After intake form finalization/approval:

**Beat:** `intake_form_register_ingest_beat_producer`\
**Worker:** `intake_form_register_ingest_worker`

Promotes approved intake submissions into domain register tables (existing platform flow). This is shared with manual intake forms, not unique to file upload.

***

### 9. Import File Configuration APIs

**Prefix:** `/input-mechanism-metadata`

| Endpoint | Purpose |
| --- | --- |
| `create_import_file_configuration` | Create template |
| `get_import_file_configuration` | List for register |
| `update_import_file_configuration` | Update template |
| `delete_import_file_configuration` | Remove template |

Enqueue endpoint:

| Endpoint | Purpose | Permission |
| --- | --- | --- |
| `POST /input-mechanism-data/enqueue_import_file` | Enqueue uploaded file for processing | `intakeSubmission:edit` |

***

### 10. UI Components

| Component | Location | Role |
| --- | --- | --- |
| `AddNewDropdown` | Staff portal header | Shows `IMPORT_FILE` mechanism |
| `ImportModal` | `ui/staff-portal-ui/src/features/intake-form/components/` | Upload + enqueue |
| `RegisterImportFileConfigView` | Configuration → Register → File Import tab | Admin CRUD for import templates |

***

### 11. End-to-End Data Flow (File Upload)

```
Staff selects import template + uploads farmers.csv
  │
  ▼
Upload to MinIO → g2p_registry_documents (document_id)
  │
  ▼
POST /input-mechanism-data/enqueue_import_file
  └─ INSERT import_file_process_queue (PENDING)

    ↓  (beat: import_file_process_beat_producer)

import_file_process_worker
  ├─ Parse CSV → N row dicts
  ├─ For each row:
  │    ├─ G2PIngestService.ingest_data(..., register_id, intake_form_id)
  │    │    ├─ INSERT incoming_raw_data
  │    │    └─ INSERT incoming_classified_data (transformation = PENDING)
  │    └─ INSERT import_file_process_log
  └─ Queue → PROCESSED

    ↓  (beat: ingest_data_transformation_beat_producer)

ingest_data_transformation_worker (per ingest_id)
  ├─ Enrich business payload (extension enricher)
  ├─ Render Jinja template → { "farmer": [{...}], "household": [{...}] }
  └─ ingestion_status → PENDING

    ↓  (beat: ingest_data_beat_producer)

ingest_data_worker
  ├─ Create intake form submission
  ├─ Save all sections from transformed payload
  ├─ Finalize submission
  └─ ingestion_status → PROCESSED

    ↓  (beat: intake_form_register_ingest_beat_producer)

intake_form_register_ingest_worker
  ├─ Write domain register tables
  ├─ Trigger deduplication, functional ID, score compute, etc.
  └─ register_ingest_process_status → PROCESSED
```

***

### 12. Error Handling & Retries

Each pipeline stage tracks:

* `*_number_of_attempts`
* `*_latest_error_code`
* `*_date_time`

On failure, status resets to `PENDING` until `worker_max_attempts`, then `FAILED`. File-level failures set `import_file_process_queue.intake_form_ingestion_error`.

Per-row commits in the file worker mean partial file success is possible: some rows ingested, others not yet processed.

***

### 13. Extension Points

| Extension point | Interface / mechanism | Used in |
| --- | --- | --- |
| Payload enrichment | `G2PPayloadEnricherInterface` via `G2PPayloadEnricherFactory` | Transformation stage |
| Ingestion mapping | Jinja template in `incoming_templates` | Transformation stage |

***

### 14. Summary of Key Artifacts

#### `openg2p-registry-core`

| Type | File | Description |
| --- | --- | --- |
| Model | `models/g2p_registry_import_file_configuration.py` | Import template config |
| Model | `models/import_file_process_queue.py` | File processing queue |
| Model | `models/import_file_process_log.py` | Per-row idempotency |
| Model | `models/ingestion_pipeline.py` | Raw/classified/enriched tables |
| Model | `models/ingestion_configuration.py` | Key paths, semantic patterns, templates |
| Model | `models/g2p_input_mechanisms.py` | Input mechanism registry |
| Service | `services/g2p_ingest_service.py` | Raw ingest entry point |
| Service | `services/input_mechanism_data_service.py` | Enqueue uploaded file |
| Service | `services/import_file_configuration_service.py` | Import template CRUD |
| Service | `services/g2p_ingestion_configuration_service.py` | Ingestion metadata CRUD |
| Ctrl Svc | `controller_services/import_file_configuration_controller_service.py` | HTTP layer for import config |

#### `openg2p-registry-celery-beat-producers`

| Type | File | Description |
| --- | --- | --- |
| Beat | `tasks/import_file_process_beat_producer.py` | Polls PENDING file queue |
| Beat | `tasks/ingest_data_transformation_beat_producer.py` | Polls transformation |
| Beat | `tasks/ingest_data_beat_producer.py` | Polls ingestion |
| Beat | `tasks/intake_form_register_ingest_beat_producer.py` | Polls approved intake → register |
| Config | `config.py` | `import_file_process_beat_producer_frequency` |
| Constant | `utils/workers.py` | `IMPORT_FILE_PROCESS_WORKER` |

#### `openg2p-registry-celery-workers`

| Type | File | Description |
| --- | --- | --- |
| Worker | `tasks/import_file_process_worker.py` | Parse file, call ingest per row |
| Worker | `tasks/ingest_data_transformation_worker.py` | Enrich + template render |
| Worker | `tasks/ingest_data_worker.py` | ADD → intake form |
| Worker | `tasks/change_request_ingest_worker.py` | UPDATE → change request |
| Worker | `tasks/intake_form_register_ingest_worker.py` | Intake → domain register |

#### `openg2p-registry-staff-portal-api`

| Type | File | Description |
| --- | --- | --- |
| Controller | `controllers/input_mechanism_data_controller.py` | Enqueue import |
| Controller | `controllers/g2p_ingestion_configuration_controller.py` | Ingestion config CRUD |

#### `staff-portal-ui`

| Type | File | Description |
| --- | --- | --- |
| Component | `features/intake-form/components/ImportModal.tsx` | File upload dialog |
| Component | `features/configuration/registers/RegisterImportFileConfigView.tsx` | Admin config |
| Component | `components/ui/AddNewDropdown.tsx` | Input mechanism selector |
| Hook | `features/shared/hooks/useFileUpload.ts` | Document upload helper |
| API route | `app/api/input-mechanism/enqueue-import/route.ts` | Proxy to enqueue endpoint |
