---
description: >-
  End-to-end asynchronous ingestion flow -- from partner payload receipt to
  change request creation.
---

# Ingestion Pipeline

The ingestion pipeline is responsible for receiving data from external systems, classifying and transforming incoming payloads, and creating change requests in the registry. The pipeline is fully asynchronous and designed for high-throughput, horizontally scalable processing.

## Requirements

The ingestion pipeline is designed to satisfy the following requirements:

1. Data can arrive from **multiple sources** -- staff portal, beneficiary portal, agency applications, and other registries.
2. Each source may send data in **different schemas** -- both standards-based and custom formats.
3. The pipeline supports **multiple interoperability standards** such as DCI and national registry formats.
4. Some standards follow a **notification-then-search philosophy** (e.g. DCI sends an event with an identifier; the receiver must invoke a search API on the source to retrieve the full record).
5. Processing must be **asynchronous** to decouple API response times from pipeline execution.
6. The pipeline must **scale out horizontally** by adding Celery workers.
7. **High throughput** -- the system must handle bulk ingestion without blocking.
8. **Traceability** -- every raw incoming message must be traceable all the way through to the resulting change log and register record.
9. **Auditability** -- raw payloads are persisted before any transformation occurs.
10. **Error handling and retries** -- every stage supports rollback and retry up to a configurable `worker_max_attempts` threshold.

## Configuration models

The ingestion pipeline uses several configuration tables to control how incoming payloads are identified, classified, and transformed.

### incoming\_partners

| Column                    | Description                                              |
| ------------------------- | -------------------------------------------------------- |
| `partner_id`              | Primary key                                              |
| `partner_mnemonic`        | Short name for the partner system                        |
| `keymanager_reference_id` | Reference to the partner's public key in the key manager |
| `is_active`               | Whether the partner is currently active                  |

### data\_models

| Column                   | Description                                                                   |
| ------------------------ | ----------------------------------------------------------------------------- |
| `data_model_id`          | Primary key                                                                   |
| `data_model_mnemonic`    | Short name for the data model (e.g. `dci_v1`, `custom_farmer`)                |
| `pattern_for_data_model` | JSONPath or regex pattern used to identify this data model from a raw payload |
| `is_active`              | Whether the data model is currently active                                    |

### incoming\_model\_signature\_patterns

| Column                           | Description                                     |
| -------------------------------- | ----------------------------------------------- |
| `signature_pattern_id`           | Primary key                                     |
| `data_model_id`                  | Foreign key to the data model                   |
| `key_path_for_sender`            | JSONPath to extract the sender identifier       |
| `key_path_for_signature`         | JSONPath to extract the signature value         |
| `key_path_for_signature_payload` | JSONPath to extract the payload that was signed |

### incoming\_model\_semantic\_patterns

| Column                          | Description                                                      |
| ------------------------------- | ---------------------------------------------------------------- |
| `semantic_pattern_id`           | Primary key                                                      |
| `data_model_id`                 | Foreign key to the data model                                    |
| `register_id`                   | Target register for payloads matching this pattern               |
| `operation_id`                  | Target section/operation                                         |
| `pattern_for_register`          | Pattern to match the register from the payload                   |
| `pattern_for_operation`         | Pattern to match the operation from the payload                  |
| `key_path_for_business_payload` | JSONPath to extract the business-relevant portion of the payload |

### incoming\_templates

| Column             | Description                                            |
| ------------------ | ------------------------------------------------------ |
| `template_id`      | Primary key                                            |
| `data_model_id`    | Foreign key to the data model                          |
| `register_id`      | Target register                                        |
| `operation_id`     | Target section/operation                               |
| `template_file_id` | Reference to the Jinja template file in object storage |

### incoming\_payload\_enricher

| Column                       | Description                                               |
| ---------------------------- | --------------------------------------------------------- |
| `enricher_id`                | Primary key                                               |
| `data_model_id`              | Foreign key to the data model                             |
| `register_id`                | Target register                                           |
| `operation_id`               | Target section/operation                                  |
| `raw_payload_enricher_class` | Fully qualified class name of the enricher implementation |

The enricher is used for standards that follow the notification-then-search philosophy. When a payload contains only a reference identifier, the enricher fetches the full record from the source system before classification proceeds.

## Pipeline stages

{% stepper %}
{% step %}
#### API Ingestion

The partner system calls the `/partner/ingest_data` endpoint. The API layer performs the following synchronous operations:

* Validates the request structure and partner credentials.
* Matches the payload against `incoming_model_signature_patterns` to verify the cryptographic signature.
* Stores the raw payload in MinIO without any transformation.
* Returns a `correlation_id` to the caller for traceability.

A Celery task is then dispatched to begin asynchronous processing.
{% endstep %}

{% step %}
#### Classification Worker

The classification worker picks up the raw payload and applies semantic pattern matching:

* Matches the payload against configured `incoming_model_semantic_patterns`.
* Determines the target `register_id` and `operation_id` (section).
* Extracts the business payload using the configured JSONPath.
* If an `incoming_payload_enricher` is configured for this pattern, the enricher is invoked to fetch additional data from the source system.
{% endstep %}

{% step %}
#### Transformation Worker

The transformation worker converts the classified payload from the external schema to the internal registry schema:

* Looks up the appropriate `incoming_template` for the resolved register and operation.
* Applies the Jinja template to transform the external payload into the registry's internal change payload format.
* Validates the transformed output against the target section's JSON form schema.
{% endstep %}

{% step %}
#### Ingestion Worker

The ingestion worker creates the actual registry change request:

* Calls `G2PRegisterService.create_change_log()` with the transformed payload.
* The change request enters the standard verification and approval workflow.
* If auto-approval is configured for this section and source channel, the change request is approved immediately.
{% endstep %}
{% endstepper %}

{% hint style="warning" %}
Every stage has built-in rollback and retry logic. If a stage fails, it is retried up to the configured `worker_max_attempts` before being moved to a dead-letter queue for manual inspection.
{% endhint %}

{% content-ref url="../features/ingestion-pipeline.md" %}
[ingestion-pipeline.md](../features/ingestion-pipeline.md)
{% endcontent-ref %}
