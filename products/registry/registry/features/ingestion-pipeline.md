---
description: >-
  Operational capabilities exposed by the ingestion pipeline - APIs,
  configuration management, observability, and user-facing behavior.
---

# Ingestion Pipeline

## Partner data ingestion

External partner systems submit data through the partner API.

**Endpoint:** `POST /partner/ingest_data`

**Query parameters:**

| Parameter        | Required | Description                                                                                           |
| ---------------- | -------- | ----------------------------------------------------------------------------------------------------- |
| `data_model`     | No       | Data model mnemonic. If omitted, all active data models are scanned against `pattern_for_data_model`. |
| `register_id`    | No       | Target register. When supplied together with `intake_form_id`, skips the classification stage.        |
| `intake_form_id` | No       | Target intake form. When supplied together with `register_id`, skips the classification stage.        |

**Request body:** Arbitrary JSON envelope defined by the partner data model. Structure is not enforced at the API layer - validation is driven by configured key paths and patterns.

**Response:** A `correlation_id` rendered through a partner-specific Jinja response template stored in MinIO (`data_models.response_template_file_id`). All records created from a single API call (including list fan-out) share the same `correlation_id`.

***

## Staff data ingestion

Staff users can submit data through the staff portal using the same core ingest service.

**Endpoint:** `POST /input-mechanism-data/ingest-data`

**Permission:** `intakeSubmission:edit`

**Behaviour:** Same ingestion pipeline as the partner API, but returns a plain JSON response (no MinIO response template rendering).

***

## Classification bypass

When both `register_id` and `intake_form_id` are provided on ingest, the classification worker is skipped:

* `incoming_raw_data.classification_status` is set to `PROCESSED` immediately.
* `incoming_classified_data` is inserted with `transformation_status = PENDING`.
* The transformation beat producer picks up the row on its next poll.

Useful when the caller already knows the target register and intake form (e.g. staff-initiated or pre-classified submissions).

***

### ADD and UPDATE pipeline actions

Classification resolves whether the payload creates a new record or updates an existing one.

| Action     | Trigger                                                        | Outcome                                                                            |
| ---------- | -------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **ADD**    | External record identifier not found in registry               | Intake form submission created and finalized (`draft_status = FINAL`)              |
| **UPDATE** | External record identifier matches an existing registry record | Change request created via `G2PChangeRequestWorkerService.create_change_request()` |

The ingestion beat producer routes to `ingest_data_worker` (ADD) or `change_request_ingest_worker` (UPDATE) based on `pipeline_action` on the classified row.

UPDATE change requests enter the standard verification and approval workflow. Auto-approval applies when configured for the target section and source channel.

### Bulk and list ingestion

When `incoming_model_key_paths.is_list = true`, a single API call containing a list of records is fanned out into multiple ingest rows:

* Each list element gets its own `ingest_id`.
* All records share a single `correlation_id` for end-to-end traceability.
* Each record progresses independently through classification, transformation, and ingestion.

***

## Payload enrichment

For standards that follow notification-then-search (e.g. DCI), the incoming payload may contain only a reference identifier. An enricher implementation resolves the full business record before transformation.

* Configured via `raw_payload_enricher_class` on `incoming_model_semantic_patterns`.
* Instantiated by `G2PPayloadEnricherFactory` from extension packages (e.g. `openg2p_registry_nsr_extension`).
* Runs in the **transformation worker**, after business payload extraction and before Jinja template rendering.

***

## Traceability and observability

Staff can search and inspect ingestion records at every pipeline stage.

**Prefix:** `/ingestion-data`

| Endpoint                                     | Permission             | Description                                              |
| -------------------------------------------- | ---------------------- | -------------------------------------------------------- |
| `POST /get_ingestion_summary_data`           | —                      | Summary statistics across ingestion records              |
| `POST /search_in_ingestion_data`             | `incomingMessage:view` | Search and paginate ingestion records                    |
| `POST /get_raw_payload`                      | `incomingMessage:view` | Retrieve the original raw payload by `ingest_id`         |
| `POST /get_enriched_and_transformed_payload` | `incomingMessage:view` | Retrieve enriched and transformed payload by `ingest_id` |

Traceability chain: `correlation_id` → `ingest_id` → classified data → enriched/transformed data → `intake_form_submission_id` (ADD) or `change_request_id` (UPDATE).

***

## Ingestion configuration management

Staff configure how payloads are identified, classified, enriched, and transformed through the ingestion config API.

**Prefix:** `/ingestion-config`

### Key paths

| Endpoint                           | Permission             | Description                                         |
| ---------------------------------- | ---------------------- | --------------------------------------------------- |
| `POST /create_incoming_key_path`   | `ingestKeyPath:create` | Create signature/message key paths for a data model |
| `POST /get_incoming_key_path`      | `ingestKeyPath:view`   | Get key path by ID                                  |
| `POST /get_all_incoming_key_paths` | `ingestKeyPath:view`   | List all key paths                                  |
| `POST /update_incoming_key_path`   | `ingestKeyPath:edit`   | Update key path                                     |
| `POST /delete_incoming_key_path`   | `ingestKeyPath:delete` | Delete key path                                     |

### Semantic patterns

| Endpoint                          | Permission                | Description                |
| --------------------------------- | ------------------------- | -------------------------- |
| `POST /create_semantic_pattern`   | `ingestExpression:create` | Create semantic pattern    |
| `POST /get_semantic_pattern`      | `ingestExpression:view`   | Get semantic pattern by ID |
| `POST /get_all_semantic_patterns` | `ingestExpression:view`   | List all semantic patterns |
| `POST /update_semantic_pattern`   | `ingestExpression:edit`   | Update semantic pattern    |
| `POST /delete_semantic_pattern`   | `ingestExpression:delete` | Delete semantic pattern    |

### Register semantic patterns

| Endpoint                                   | Permission                | Description                   |
| ------------------------------------------ | ------------------------- | ----------------------------- |
| `POST /create_register_semantic_pattern`   | `ingestExpression:create` | Create register-level pattern |
| `POST /get_register_semantic_pattern`      | `ingestExpression:view`   | Get register pattern by ID    |
| `POST /get_all_register_semantic_patterns` | `ingestExpression:view`   | List all register patterns    |
| `POST /update_register_semantic_pattern`   | `ingestExpression:edit`   | Update register pattern       |
| `POST /delete_register_semantic_pattern`   | `ingestExpression:delete` | Delete register pattern       |

### Templates

| Endpoint                  | Permission              | Description                                    |
| ------------------------- | ----------------------- | ---------------------------------------------- |
| `POST /create_template`   | `ingestTemplate:create` | Create Jinja transformation template reference |
| `POST /get_template`      | `ingestTemplate:view`   | Get template by ID                             |
| `POST /get_all_templates` | `ingestTemplate:view`   | List all templates                             |
| `POST /update_template`   | `ingestTemplate:edit`   | Update template                                |
| `POST /delete_template`   | `ingestTemplate:delete` | Delete template                                |

### Subscription activity logs

| Endpoint                                          | Permission                  | Description                      |
| ------------------------------------------------- | --------------------------- | -------------------------------- |
| `POST /create_subscription_activity_log`          | `ingestSubscription:create` | Log WebSub subscription activity |
| `POST /get_subscription_activity_logs_by_partner` | `ingestSubscription:view`   | Get logs for a partner           |
| `POST /get_all_subscription_activity_logs`        | `ingestSubscription:view`   | List all subscription logs       |

## Partner response templating

Partner API success and error responses are not returned as fixed JSON schemas. Instead, each data model can define a `response_template_file_id` pointing to a Jinja template in MinIO. The template receives the `correlation_id` (and error details on failure) and renders the partner-specific response envelope.

This allows each interoperability standard (DCI, custom formats) to return responses in its own schema without changing the core API.

## Error handling and failed records

When a pipeline stage fails:

1. The worker rolls back the current transaction and records the error.
2. The row status is reset to `PENDING` for retry, up to `worker_max_attempts` (default: 5).
3. After exhausting retries, the row is marked `FAILED` with the error message in `*_latest_error_code`.

Failed records can be inspected via `/ingestion-data/search_in_ingestion_data` and retried manually by resetting the relevant status field to `PENDING`.

There is no separate broker dead-letter queue.

**Configuration:**

| Setting                | Default                 | Env prefix                                           |
| ---------------------- | ----------------------- | ---------------------------------------------------- |
| `worker_max_attempts`  | 5                       | `REGISTRY_CELERY_WORKERS_`                           |
| Beat polling frequency | configurable            | `REGISTRY_CELERY_BEAT_`                              |
| Worker queue           | `registry_worker_queue` | `REGISTRY_CELERY_BEAT_` / `REGISTRY_CELERY_WORKERS_` |

***

## Permissions summary

| Permission              | Scope                                                |
| ----------------------- | ---------------------------------------------------- |
| `intakeSubmission:edit` | Staff data ingestion                                 |
| `incomingMessage:view`  | Search and inspect ingestion records                 |
| `ingestKeyPath:*`       | Key path configuration                               |
| `ingestExpression:*`    | Semantic and register semantic pattern configuration |
| `ingestTemplate:*`      | Transformation template configuration                |
| `ingestSubscription:*`  | WebSub subscription activity logs                    |
