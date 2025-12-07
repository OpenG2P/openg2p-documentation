---
layout:
  width: default
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
---

# Ingestion pipeline

The Base Registry supports ingesting data from external systems through a fully **asynchronous ingestion pipeline.** Partner systems may send registry-related events in different formats or interoperable standards. Incoming messages are validated for signature authenticity, stored as raw events without transformation, and then processed in stages using Celery workers. The pipeline separates raw persistence, semantic interpretation, and registry update operations, allowing each stage to run independently and at scale.

The registry integrates with subscription APIs defined by partner registries, allowing it to subscribe to events from other departments & registries.

#### 5.1 Multi-Standard Payload Support

The registry ingestion layer can receive and interpret payloads conforming to different interoperability standards such as SPDci, UNDP's DCI models, or national registry formats. Raw payloads are classified using metadata patterns, and domain-specific semantic meaning is extracted by applying JSONPaths.  If the incoming payload contains only reference identifiers, the ingestion pipeline can automatically fetch the full record from the partner system using search APIs defined within the interoperability standard.&#x20;

\
The incoming payloads are then transformed using Jinja templates and then applied as Change Requests. These change requests follow the same verification and approval rules as defined in the registry.
