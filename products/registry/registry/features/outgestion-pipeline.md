---
description: >-
  The Base Registry implements a fully asynchronous outgestion pipeline that
  pushes registry data changes to external partner systems through configurable
  transformation and WebSub-based event delivery.
---

# Outgestion Pipeline

### Key capabilities

#### Event-driven data delivery

When a change request is approved in the registry, the outgestion pipeline automatically captures the change and delivers it to subscribed external systems. Partner systems receive data without needing to poll the registry the pipeline pushes changes as they happen using the [WebSub protocol](https://www.w3.org/TR/websub/).

#### Multi-format output

The pipeline supports delivering the same registry data in different formats to different partner systems. Each partner receives data transformed through a dedicated Jinja2 template that maps registry fields to the partner's expected schema. Templates support JSON-LD expansion for linked data interoperability with standards like DCI.

#### Configurable topics

Administrators define outgestion topics that pair a register (e.g., Farmer Register) with a data model (e.g., DCI v1) and a WebSub topic URL. Each topic acts as a delivery channel -- when registry data matching that register and data model changes, the pipeline transforms and publishes it to the topic's subscribers.

#### Template-based transformation

Outgoing data is transformed from the registry's internal format to the external partner's schema using Jinja2 templates stored in MinIO object storage. Templates are managed through the staff portal API and can be uploaded, updated, or replaced without code changes.

### Processing architecture

The pipeline separates concerns across three asynchronous phases:

1. **Topic registration** -- new topics are registered with the WebSub hub so subscribers can discover and subscribe to them.
2. **Data transformation** -- raw registry change data is transformed into the partner's expected format using the configured Jinja2 template.
3. **Data publishing** -- transformed data is published to the WebSub hub, which distributes it to all subscribed partner systems.

Each phase runs independently via Celery workers, enabling:

* **Independent scaling** -- transformation-heavy workloads can scale separately from publishing.
* **Fault isolation** -- a publishing failure does not block other transformations.
* **Automatic retries** -- each stage retries up to a configurable maximum before marking as failed.

### Outgestion vs. ingestion

| Aspect           | Ingestion                                                | Outgestion                             |
| ---------------- | -------------------------------------------------------- | -------------------------------------- |
| Direction        | External systems → Registry                              | Registry → External systems            |
| Trigger          | Partner submits data                                     | Change request approved                |
| Protocol         | WebSub subscription callbacks                            | WebSub topic publication               |
| Pipeline stages  | Classification → Enrichment → Transformation → Ingestion | Transformation → Publishing            |
| Template purpose | Map external schema to registry format                   | Map registry format to external schema |
| Configuration    | Incoming partners, signature patterns, semantic patterns | Outgoing topics, outgoing templates    |

### Topic management

Topics are managed through the staff portal with role-based permissions:

* **Create** topics for new register and data model combinations.
* **Activate / deactivate** topics to control data flow without deleting configuration.
* **Re-register** topics with the WebSub hub if registration needs to be retried.
* **Delete** inactive topics that are no longer needed.

Each topic automatically registers with the WebSub hub on creation. Registration status is tracked and can be monitored through the API.

### Template management

Templates control how registry data is formatted for each external system:

* **Upload** Jinja2 template files for specific register and data model combinations.
* **Update** templates when partner schema requirements change.
* **Preview** template output by retrieving the template file via presigned MinIO URLs.

Templates receive the full registry change payload as input and produce the external-format output. JSON-LD expansion can be applied to the input data before rendering, enabling interoperability with linked data standards.

### Monitoring and traceability

Every outgoing record tracks:

* **Change origin** -- which user and change request triggered the outgestion.
* **Transformation state** -- status, timestamp, attempt count, and last error for the transformation stage.
* **Publishing state** -- status, timestamp, attempt count, and last error for the publishing stage.
* **Partner attribution** -- if the original change was made by a partner, the `changed_by_partner_id` is recorded.

Records can be queried by status (`PENDING`, `PROCESSING`, `PROCESSED`, `FAILED`) to monitor pipeline health and identify stuck or failed deliveries.

{% content-ref url="../design/outgestion-pipeline.md" %}
[outgestion-pipeline.md](../design/outgestion-pipeline.md)
{% endcontent-ref %}
