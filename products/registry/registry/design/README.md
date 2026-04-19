---
description: Technical architecture and design of OpenG2P Registry
---

# Design

This section covers the technical architecture and internal design of OpenG2P Registry. It describes the foundational data structures, processing pipelines, and cross-cutting concerns that underpin the platform. Each topic provides insight into how the registry is built, how data flows through the system, and the design decisions that shape its behaviour.

## Architecture overview

OpenG2P Registry is built as a set of FastAPI-based microservices that communicate through well-defined internal APIs and asynchronous task queues. The principal technology components are:

* **FastAPI** -- serves the REST API layer for both staff-portal and partner-facing endpoints.
* **Celery workers** -- handle all asynchronous processing including ingestion, outgestion, deduplication, and computation tasks.
* **PostgreSQL** -- primary data store with column-level encryption for sensitive fields.
* **Redis** -- used for caching, session management, and as the Celery message broker.
* **MinIO** -- object storage for documents, attachments, and raw ingestion payloads.
* **Keycloak** -- identity and access management for staff users, partner systems, and registrant authentication.

The functional architecture diagram is available on the [Registry landing page](../).

## Key design principles

| Principle                   | Description                                                                                                                                                                                                    |
| --------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Metadata-driven**         | The core platform is domain-agnostic. Register structure, sections, tabs, and UI forms are all driven by metadata configuration rather than hard-coded logic.                                                  |
| **Change-request-centric**  | Every mutation to registry data flows through an approval workflow. No record is created or modified without a corresponding change request.                                                                   |
| **Asynchronous processing** | Celery workers handle ingestion, outgestion, deduplication, and computation. This decouples the API layer from heavy processing and enables horizontal scale-out.                                              |
| **Schema-driven UI**        | JSON schemas stored in register metadata drive the rendering of forms in the staff portal, eliminating the need for per-register frontend code.                                                                |
| **Envelope encryption**     | Sensitive columns are encrypted at rest using AES with a Data Encryption Key (DEK) that is itself protected by an asymmetric KMS key. Read and write operations never call the KMS, avoiding latency overhead. |

## Design topics

The following sub-pages cover individual design topics in detail:

{% content-ref url="data-model.md" %}
[data-model.md](data-model.md)
{% endcontent-ref %}

{% content-ref url="change-management.md" %}
[change-management.md](change-management.md)
{% endcontent-ref %}

{% content-ref url="ingestion-pipeline.md" %}
[ingestion-pipeline.md](ingestion-pipeline.md)
{% endcontent-ref %}

{% content-ref url="../../../../registry/design/detailed-design-notes/outgestion-pipeline.md" %}
[outgestion-pipeline.md](../../../../registry/design/detailed-design-notes/outgestion-pipeline.md)
{% endcontent-ref %}

{% content-ref url="consent-management.md" %}
[consent-management.md](consent-management.md)
{% endcontent-ref %}

{% content-ref url="encryption-at-rest.md" %}
[encryption-at-rest.md](encryption-at-rest.md)
{% endcontent-ref %}

{% content-ref url="../../../../registry/design/detailed-design-notes/partner-apis.md" %}
[partner-apis.md](../../../../registry/design/detailed-design-notes/partner-apis.md)
{% endcontent-ref %}

{% content-ref url="../../../../registry/design/detailed-design-notes/deduplication.md" %}
[deduplication.md](../../../../registry/design/detailed-design-notes/deduplication.md)
{% endcontent-ref %}

{% content-ref url="../../../../registry/design/detailed-design-notes/computation-framework.md" %}
[computation-framework.md](../../../../registry/design/detailed-design-notes/computation-framework.md)
{% endcontent-ref %}

{% content-ref url="../../../../registry/design/detailed-design-notes/vc-issuance.md" %}
[vc-issuance.md](../../../../registry/design/detailed-design-notes/vc-issuance.md)
{% endcontent-ref %}

{% content-ref url="registrant-authentication-oidc-widget/" %}
[registrant-authentication-oidc-widget](registrant-authentication-oidc-widget/)
{% endcontent-ref %}

{% content-ref url="ui-engineering-design/" %}
[ui-engineering-design](ui-engineering-design/)
{% endcontent-ref %}
