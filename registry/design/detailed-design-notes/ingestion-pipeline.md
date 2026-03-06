---
description: >-
  This document outlines the end-to-end ingestion flow from the partner API
  through to registry change request creation. The pipeline is fully
  asynchronous and decoupled into specific celery stages.
---

# Ingestion pipeline

{% stepper %}
{% step %}
### API Ingestion (`/partner/ingest_data`)

**Module:** `openg2p-registry-partner-api` / `openg2p-registry-core`

* **Validation**: Reconciles the incoming request against per-configured key paths (`incoming_model_key_paths`) to extract the sender, message ID, and signature.
* **Processing**: Identifies the corresponding `DataModel` (either via query param or regex pattern matching on the payload) and verifies the payload signature from the key manager. If the payload is a continuous list, it handles splitting it into manageable individual elements.
* **Storage**: Persists the raw payload into the `incoming_raw_data` and `incoming_raw_data_payloads` tables with a `PENDING` classification status.
* **Response**: Immediately returns a `correlation_id` back to the partner system for tracking.
{% endstep %}

{% step %}
### Classification Worker

**Module:** `openg2p-registry-celery-workers` (`ingest_data_classification_worker.py`)

* **Trigger**: `ingest_data_classification_beat_producer` continuously polls for records in `incoming_raw_data` with a `PENDING` status.
* **Classification**: Matches the payload against `incoming_model_semantic_patterns` to determine the corresponding registry definition (`register_id`) and section (`section_id`).
* **Storage**: Successfully mapped records are stored in `incoming_classified_data` and the original raw data row is marked as `PROCESSED`.
{% endstep %}

{% step %}
### Transformation Worker

**Module:** `openg2p-registry-celery-workers` (`ingest_data_transformation_worker.py`)

* **Trigger**: `ingest_data_transformation_beat_producer` picks up records from `incoming_classified_data` pending transformation.
* **Enrichment**: Extracts the specific business payload using configured key paths and invokes a dynamic enricher class (`G2PPayloadEnricherInterface`) to populate the payload with additional context (e.g. cross-referencing parent properties).
* **Transformation**: Uses per-configured Jinja hosted in Minio (`incoming_templates`) to transform the payload from the external partner's schema directly into our internal OpenG2P schema standard.
* **Storage**: Stores both states in `incoming_enriched_transformed_data` and updates pipeline statuses.
{% endstep %}

{% step %}
### Ingestion Worker

**Module:** `openg2p-registry-celery-workers` (`ingest_data_worker.py`)

* **Trigger**: `ingest_data_beat_producer` picks up rows that have a `PENDING` ingestion status.
* **Change Request Creation**: Uses the previously mapped register IDs, section IDs, and fully transformed payload to create a `ChangeRequestRequestPayload`.
* **Execution**: Invokes the core core method `G2PRegisterService.create_change_request()`.
* **Completion**: Adds the new data to the registry change request queue and stamps the generated `change_request_id` onto the `incoming_classified_data` record.
{% endstep %}
{% endstepper %}

{% hint style="info" %}
Every stage follows a rollback and retry mechanism up to a configured `worker_max_attempts`. If a failure threshold is met, the particular segment fails cleanly and logs its specific exception code back onto the database record (`*_latest_error_code`), ensuring healthy records are not blocked.
{% endhint %}
