---
description: >-
  Design of the outgestion pipeline for pushing data to external partner
  systems.
---

# Outgestion Pipeline

### Overview

The outgestion pipeline is the counterpart to the ingestion pipeline. While ingestion brings data into the registry from external systems, outgestion pushes registry data changes outward to partner systems, external registries, and downstream consumers.

The pipeline is fully asynchronous, built on Celery workers with Redis as the message broker. When a change request is approved in the registry, the outgestion pipeline captures the change, transforms it into the partner's expected schema using Jinja2 templates, and publishes it via the WebSub protocol.

#### Key design goals

1. **Event-driven delivery** -- registry changes are automatically propagated to subscribed external systems without polling.
2. **Schema flexibility** -- each partner system can receive data in its own format via configurable Jinja2 templates.
3. **Asynchronous processing** -- decouples the registry approval workflow from external delivery, so partner system availability does not block registry operations.
4. **Horizontal scalability** -- scales out by adding Celery workers.
5. **Traceability** -- every outgoing record is traceable from the originating change request through transformation to final publication.
6. **Fault tolerance** -- every stage supports retry up to a configurable `worker_max_attempts` threshold before marking as failed.

### Outgestion topics

An outgestion topic defines a delivery channel for a specific register and data model combination. Topics use the [WebSub protocol](https://www.w3.org/TR/websub/) to register with a hub and publish content to subscribers.

Each topic is uniquely constrained by `(register_id, data_model_id)`. When a registry change matches a topic's register and data model, the outgestion pipeline picks it up for processing.

#### Topic lifecycle

1. **Creation** -- an administrator creates a topic via the staff portal API, specifying the register, data model, and WebSub topic URL.
2. **Registration** -- the topic registration beat producer detects the new topic (status: `PENDING`) and dispatches a worker to register it with the WebSub hub.
3. **Active** -- once registered (`PROCESSED`), the topic is ready to receive and publish data.
4. **Deactivation** -- topics can be toggled inactive, halting publication without deleting configuration.

#### Topic states

| State        | Meaning                                |
| ------------ | -------------------------------------- |
| `PENDING`    | Awaiting WebSub hub registration       |
| `PROCESSING` | Registration request in flight         |
| `PROCESSED`  | Successfully registered with hub       |
| `FAILED`     | Registration failed after max attempts |

### Template-based transformation

Outgestion templates convert internal registry data into the external schema expected by partner systems. Templates are Jinja2 files stored in MinIO object storage.

Each template is bound to a unique `(register_id, data_model_id)` combination, matching the corresponding outgestion topic. When the transformation worker processes an outgoing record, it:

1. Retrieves the raw change payload from `outgoing_raw_data_payloads`.
2. Looks up the `OutgoingTemplate` matching the record's register and data model.
3. Fetches the Jinja2 template file from MinIO via `TemplateHelper`.
4. Optionally expands the data using JSON-LD expansion (for linked data interoperability).
5. Renders the template with the expanded data to produce the transformed payload.
6. Stores the result in `outgoing_transformed_data_payloads`.

This approach allows the same registry data to be delivered in different schemas to different partners -- each partner's topic has its own template.

### Event publishing flow

The outgestion pipeline processes data through three asynchronous stages, each driven by a Celery beat producer that polls for `PENDING` records and dispatches workers.

#### Stage 1: Topic registration

**Beat producer:** `outgest_topic_register_beat_producer` **Worker:** `outgest_topic_register_worker`

Registers newly created outgestion topics with the WebSub hub. This is a one-time operation per topic.

* Beat producer queries `outgoing_topics` for rows with `websub_register_status = PENDING`.
* Updates status to `PROCESSING` and dispatches a worker per topic.
* Worker calls `WebsubHelper.register_topic()` which POSTs `hub.mode=register` to the WebSub hub.
* On success: status becomes `PROCESSED`. On failure: retries up to `worker_max_attempts`, then `FAILED`.

#### Stage 2: Data transformation

**Beat producer:** `outgest_data_transformation_beat_producer` **Worker:** `outgest_data_transformation_worker`

Transforms raw outgoing data into the partner's expected format.

* Beat producer queries `outgoing_raw_data` for rows with `transformation_status = PENDING`.
* Updates status to `PROCESSING` and dispatches a worker per record.
* Worker fetches the raw payload, locates the matching outgoing template, and renders via Jinja2.
* Transformed output is stored in `outgoing_transformed_data_payloads`.
* On success: `transformation_status = PROCESSED` and `publish_status` is set to `PENDING`, triggering Stage 3.

#### Stage 3: Data publishing

**Beat producer:** `outgest_data_publish_beat_producer` **Worker:** `outgest_data_publish_worker`

Publishes transformed data to the WebSub hub for delivery to subscribers.

* Beat producer queries `outgoing_raw_data` for rows with `publish_status = PENDING`.
* Updates status to `PROCESSING` and dispatches a worker per record.
* Worker fetches the transformed payload and calls `WebsubHelper.publish()` which POSTs the content to the WebSub hub with `hub.mode=publish`.
* The hub then distributes the content to all subscribers of that topic.
* On success: `publish_status = PROCESSED`. On failure: retries up to `worker_max_attempts`, then `FAILED`.

#### Flow diagram

```
Change Request Approved
        |
        v
 outgoing_raw_data (PENDING)
 outgoing_raw_data_payloads
        |
        v
 [Beat Producer: transformation]
        |
        v
 outgest_data_transformation_worker
   - Fetch raw payload
   - Lookup OutgoingTemplate
   - Render Jinja2 template
   - Store in outgoing_transformed_data_payloads
   - Set publish_status = PENDING
        |
        v
 [Beat Producer: publish]
        |
        v
 outgest_data_publish_worker
   - Fetch transformed payload
   - POST to WebSub hub
   - Hub distributes to subscribers
        |
        v
 Partner System receives data
```

### Configuration models

#### outgoing\_topics

Defines WebSub topic endpoints for each register and data model combination.

| Column                               | Type             | Description                                                         |
| ------------------------------------ | ---------------- | ------------------------------------------------------------------- |
| `topic_id`                           | UUID (PK)        | Unique identifier                                                   |
| `register_id`                        | String (indexed) | Target register                                                     |
| `data_model_id`                      | String (indexed) | Target data model                                                   |
| `websub_topic`                       | String           | WebSub topic URL                                                    |
| `description`                        | String           | Human-readable description                                          |
| `is_active`                          | Boolean          | Whether topic accepts new data                                      |
| `websub_register_status`             | String           | Registration state (`PENDING`, `PROCESSING`, `PROCESSED`, `FAILED`) |
| `websub_register_datetime`           | DateTime         | Last registration attempt timestamp                                 |
| `websub_register_number_of_attempts` | Integer          | Retry counter                                                       |
| `websub_register_latest_error_code`  | String           | Last error message                                                  |

Unique constraint: `(data_model_id, register_id)`

#### outgoing\_templates

Defines Jinja2 transformation templates for each register and data model combination.

| Column             | Type             | Description                                |
| ------------------ | ---------------- | ------------------------------------------ |
| `template_id`      | UUID (PK)        | Unique identifier                          |
| `data_model_id`    | String (indexed) | Target data model                          |
| `register_id`      | String (indexed) | Target register                            |
| `template_file_id` | String           | Reference to Jinja2 template file in MinIO |

Unique constraint: `(data_model_id, register_id)`

#### outgoing\_raw\_data

Tracks each outgoing record through the transformation and publishing stages.

| Column                  | Type             | Description                                 |
| ----------------------- | ---------------- | ------------------------------------------- |
| `outgest_id`            | String (PK)      | Unique outgestion identifier                |
| `change_request_id`     | String (indexed) | Originating change request                  |
| `internal_record_id`    | String (indexed) | Registry record identifier                  |
| `register_id`           | String (indexed) | Register the record belongs to              |
| `data_model_id`         | String (indexed) | Data model used                             |
| `topic_id`              | String (indexed) | Target outgestion topic                     |
| `changed_by`            | String           | User who made the change                    |
| `changed_at`            | DateTime         | When the change was made                    |
| `approved_by`           | String           | User who approved the change                |
| `approved_at`           | DateTime         | When the change was approved                |
| `changed_by_partner_id` | String (indexed) | Partner that originated the change (if any) |
| `transformation_status` | String (indexed) | Transformation stage state                  |
| `publish_status`        | String (indexed) | Publishing stage state                      |

#### outgoing\_raw\_data\_payloads

Stores the original registry data before transformation.

| Column              | Type        | Description                 |
| ------------------- | ----------- | --------------------------- |
| `change_request_id` | String (PK) | Links to the change request |
| `raw_data_json`     | JSONB       | Raw data in JSON format     |
| `raw_data_xml`      | Text        | Raw data in XML format      |

#### outgoing\_transformed\_data\_payloads

Stores the template-transformed data ready for publishing.

| Column                  | Type        | Description                     |
| ----------------------- | ----------- | ------------------------------- |
| `change_request_id`     | String (PK) | Links to the change request     |
| `transformed_data_json` | JSONB       | Transformed data in JSON format |
| `transformed_data_xml`  | Text        | Transformed data in XML format  |

### Error handling

Every pipeline stage tracks retry state independently:

* **Attempt counter** -- incremented on each try.
* **Error code** -- the latest error message is stored for debugging.
* **Status rollback** -- on failure below max attempts, status resets to `PENDING` for the beat producer to re-dispatch.
* **Terminal failure** -- after `worker_max_attempts` (default: 5) the status moves to `FAILED` for manual inspection.

Each stage uses database transactions with rollback on error, ensuring no partial state is committed.

### API endpoints

The outgestion configuration is managed through the staff portal API under the `/outgestion-config` prefix.

#### Topic management

| Endpoint                   | Permission            | Description                    |
| -------------------------- | --------------------- | ------------------------------ |
| `POST /create_topic`       | `outgestTopic:create` | Create new outgestion topic    |
| `POST /get_all_topics`     | `outgestTopic:view`   | List topics (paginated)        |
| `POST /get_topic`          | `outgestTopic:view`   | Get single topic details       |
| `POST /update_topic`       | `outgestTopic:edit`   | Update topic configuration     |
| `POST /toggle_topicstatus` | `outgestTopic:edit`   | Activate or deactivate topic   |
| `POST /re_register_topic`  | `outgestTopic:edit`   | Re-trigger WebSub registration |
| `POST /delete_topic`       | `outgestTopic:delete` | Delete inactive topic          |

#### Template management

| Endpoint                  | Permission               | Description                        |
| ------------------------- | ------------------------ | ---------------------------------- |
| `POST /create_template`   | `outgestTemplate:create` | Create new transformation template |
| `POST /get_template`      | `outgestTemplate:view`   | Get single template details        |
| `POST /get_all_templates` | `outgestTemplate:view`   | List templates (paginated)         |
| `POST /update_template`   | `outgestTemplate:edit`   | Update template configuration      |
| `POST /delete_template`   | `outgestTemplate:delete` | Delete template                    |
