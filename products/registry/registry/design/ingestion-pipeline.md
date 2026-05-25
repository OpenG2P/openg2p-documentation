---
description: >-
  End-to-end asynchronous ingestion flow -- from partner payload receipt to
  change request creation.
---

# Ingestion Pipeline

The ingestion pipeline is responsible for receiving data from external systems, classifying and transforming incoming payloads, and creating change requests in the registry. The pipeline is fully asynchronous and designed for high-throughput, horizontally scalable processing.

## Requirements

The ingestion pipeline is designed to satisfy the following requirements:

1. Data can arrive from **multiple sources** - staff portal, beneficiary portal, agency applications, and other registries.
2. Each source may send data in **different schemas** - both standards-based and custom formats.
3. The pipeline supports **multiple interoperability standards** such as DCI and national registry formats.
4. Processing must be **asynchronous** to decouple API response times from pipeline execution.
5. The pipeline must **scale out horizontally** by adding Celery workers.
6. **High throughput** - the system must handle bulk ingestion without blocking; list payloads are fanned out into individual ingest records.
7. **Traceability** - every raw incoming message must be traceable all the way through to the resulting intake form submission or change request and register record.
8. **Auditability** - raw payloads are persisted before any transformation occurs.

## Configuration models

The ingestion pipeline uses several configuration tables to control how incoming payloads are identified, classified, and transformed.

#### `g2p_partners`

| Column                    | Description                                              |
| ------------------------- | -------------------------------------------------------- |
| `partner_id`              | Primary key                                              |
| `partner_mnemonic`        | Short name for the partner system                        |
| `keymanager_reference_id` | Reference to the partner's public key in the key manager |
| `is_active`               | Whether the partner is currently active                  |

#### `data_models`

| Column                      | Description                                                                                  |
| --------------------------- | -------------------------------------------------------------------------------------------- |
| `data_model_id`             | Primary key                                                                                  |
| `data_model_mnemonic`       | Short name for the data model (e.g. `dci_v1`, `custom_farmer`)                               |
| `pattern_for_data_model`    | JSONPath or regex pattern used to identify this data model from a raw payload                |
| `response_template_file_id` | MinIO object ID for the Jinja template used to render the partner API success/error response |
| `is_active`                 | Whether the data model is currently active                                                   |

#### `incoming_model_key_paths`

Signature envelope and message extraction configuration. One row per data model.

| Column                           | Description                                               |
| -------------------------------- | --------------------------------------------------------- |
| `key_path_id`                    | Primary key                                               |
| `data_model_id`                  | Foreign key to the data model                             |
| `key_path_for_message_id`        | JSONPath to extract the message identifier                |
| `key_path_for_sender`            | JSONPath to extract the sender identifier                 |
| `key_path_for_signature`         | JSONPath to extract the signature value                   |
| `key_path_for_signature_payload` | JSONPath to extract the payload that was signed           |
| `is_list`                        | Whether the payload contains a list of records to fan out |
| `key_path_for_list_elements`     | JSONPath to the list elements when `is_list = true`       |

#### `incoming_model_register_semantic_patterns`

First-pass classification resolver. Determines the target register and external record identifier, enabling dynamic **ADD** vs **UPDATE** resolution.

| Column                           | Description                                        |
| -------------------------------- | -------------------------------------------------- |
| `register_semantic_pattern_id`   | Primary key                                        |
| `data_model_id`                  | Foreign key to the data model                      |
| `register_id`                    | Target register for payloads matching this pattern |
| `pattern_for_register`           | Pattern to match the register from the payload     |
| `key_path_for_record_identifier` | JSONPath to extract the external record identifier |

#### `incoming_model_semantic_patterns`

Second-pass classification resolver. Determines the target intake form (ADD) or section (UPDATE), selects the enricher, and defines the business payload extraction path.

| Column                          | Description                                                               |
| ------------------------------- | ------------------------------------------------------------------------- |
| `semantic_pattern_id`           | Primary key                                                               |
| `data_model_id`                 | Foreign key to the data model                                             |
| `register_id`                   | Target register for payloads matching this pattern                        |
| `intake_form_id`                | Target intake form (ADD path)                                             |
| `section_id`                    | Target section (UPDATE path)                                              |
| `pattern_for_register`          | Optional pattern to match the register from the payload                   |
| `pattern_for_intake_form`       | Pattern to match the intake form from the payload (ADD)                   |
| `pattern_for_section`           | Pattern to match the section from the payload (UPDATE)                    |
| `key_path_for_business_payload` | JSONPath to extract the business-relevant portion of the payload          |
| `raw_payload_enricher_class`    | Fully qualified class name of the enricher implementation (empty if none) |

The enricher is used for standards that follow the notification-then-search philosophy. When a payload contains only a reference identifier, the enricher fetches or resolves additional data before transformation proceeds. Enrichment runs in the **transformation** worker, not during classification.

#### `incoming_templates`

| Column                      | Description                                                    |
| --------------------------- | -------------------------------------------------------------- |
| `template_id`               | Primary key                                                    |
| `data_model_id`             | Foreign key to the data model                                  |
| `register_id`               | Target register                                                |
| `template_file_id`          | Reference to the Jinja template file in object storage (MinIO) |
| `jsonld_expansion_required` | Whether JSON-LD expansion is applied before Jinja rendering    |

Unique constraint on `(data_model_id, register_id)`.

## Pipeline data tables

Runtime tables that track each ingested message as it progresses through the pipeline.

#### `incoming_raw_data`

Metadata for each ingested record. Status field `classification_status` drives the classification stage.

#### `incoming_raw_data_payloads`

Raw payload storage. The full JSON envelope is persisted here **before any transformation**.

#### `incoming_classified_data`

Classification output. Status fields `transformation_status` and `ingestion_status` drive subsequent stages.

#### `incoming_enriched_transformed_data`

Enrichment and transformation output.

## Orchestration

Async processing is **DB-status-driven**, not a single Celery task chain. The API persists rows with `PENDING` status; **Celery Beat producers** periodically poll for pending rows and dispatch worker tasks.

| Beat producer                              | Polls                                                      | Worker dispatched                                                     |
| ------------------------------------------ | ---------------------------------------------------------- | --------------------------------------------------------------------- |
| `ingest_data_classification_beat_producer` | `incoming_raw_data.classification_status = PENDING`        | `ingest_data_classification_worker`                                   |
| `ingest_data_transformation_beat_producer` | `incoming_classified_data.transformation_status = PENDING` | `ingest_data_transformation_worker`                                   |
| `ingest_data_beat_producer`                | `incoming_classified_data.ingestion_status = PENDING`      | `ingest_data_worker` (ADD) or `change_request_ingest_worker` (UPDATE) |

There is no `send_task` call from the FastAPI ingest handler. Processing begins when beat producers pick up newly inserted rows.

## Pipeline stages

{% stepper %}
{% step %}
**API Ingestion**

The partner system calls the `/partner/ingest_data` endpoint. The API layer performs the following synchronous operations:

* Validates the request structure and resolves the partner from the payload.
* Matches the payload against `incoming_model_key_paths` to extract the sender, signature envelope, and message identifier.
* Resolves the data model by query parameter or by matching `pattern_for_data_model`.
* Stores the raw payload in PostgreSQL (`incoming_raw_data` + `incoming_raw_data_payloads`) without any transformation.
* Fans out list payloads into individual ingest records sharing a single `correlation_id`.
* Returns a `correlation_id` to the caller for traceability. The partner API renders the response through a MinIO-stored Jinja template (`data_models.response_template_file_id`).

**Optional classification bypass:** When both `register_id` and `intake_form_id` query parameters are supplied, classification is skipped — `incoming_classified_data` is written immediately with `transformation_status = PENDING`.

**Staff equivalent:** `POST /input-mechanism-data/ingest-data` uses the same core service with staff IAM permissions.

Cryptographic signature verification via the key manager is implemented (`_validate_signature`) but **currently disabled** in the ingest service. Partner identity is resolved from the payload sender mnemonic.

A Celery Beat producer then picks up the row for asynchronous classification processing.
{% endstep %}

{% step %}
**Classification Worker**

The classification worker (`ingest_data_classification_worker`) picks up raw payloads with `classification_status = PENDING` and applies semantic pattern matching:

* **Two-pass classification** (when register patterns are configured):
  * Pass 1: matches `incoming_model_register_semantic_patterns` to determine `register_id` and extract the external record identifier.
  * Resolves **ADD** vs **UPDATE** — if the record already exists in the registry, the action is UPDATE; otherwise ADD.
  * Pass 2: matches `incoming_model_semantic_patterns` to determine `intake_form_id` (ADD) or `section_id` + `internal_record_id` (UPDATE).
* **Legacy classification** (when no register patterns exist): single-pass semantic matching only.
* Writes `incoming_classified_data` and sets raw row `classification_status = PROCESSED`.

Enrichment does **not** occur in this stage.
{% endstep %}

{% step %}
**Transformation Worker**

The transformation worker (`ingest_data_transformation_worker`) picks up classified payloads with `transformation_status = PENDING`:

* Extracts the business payload using `key_path_for_business_payload` from the matched semantic pattern.
* If `raw_payload_enricher_class` is configured, invokes the enricher via `G2PPayloadEnricherFactory` to fetch or resolve additional data (notification-then-search).
* Looks up the appropriate `incoming_template` for the resolved `(data_model_id, register_id)`.
* Applies the Jinja template (from MinIO) to transform the enriched payload into the registry's internal change payload format. Optional JSON-LD expansion when `jsonld_expansion_required = true`.
* Validates the transformed output against the target intake form sections (ADD) or register section (UPDATE).
* Persists `incoming_enriched_transformed_data` and sets `transformation_status = PROCESSED`, `ingestion_status = PENDING`.
{% endstep %}

{% step %}
**Ingestion Worker**

* Creates an intake form submission via `G2PIntakeFormDataService`.
* Saves section payloads from the transformed data.
* Finalizes the submission (`draft_status = FINAL`).
* Stores `intake_form_submission_id` on the classified row.

**UPDATE — `change_request_ingest_worker`**

* Builds a `ChangeRequestRequestPayload` from the transformed section data.
* Calls `G2PChangeRequestWorkerService.create_change_request()` with `change_request_source = INGESTION_PIPELINE`.
* The change request enters the standard verification and approval workflow.
* If auto-approval is configured for this section and source channel, the change request is approved immediately.
* Stores `change_request_id` on the classified row.
{% endstep %}
{% endstepper %}

{% hint style="warning" %}
Every stage has built-in rollback and retry logic. If a stage fails, it is retried up to the configured `worker_max_attempts` before being moved to a dead-letter queue for manual inspection.
{% endhint %}

{% content-ref url="../features/ingestion-pipeline.md" %}
[ingestion-pipeline.md](../features/ingestion-pipeline.md)
{% endcontent-ref %}
