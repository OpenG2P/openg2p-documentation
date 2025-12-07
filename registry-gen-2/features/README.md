# Features

## Base Registry Platform — Product Features

### 1. Unified Registry Model

The Base Registry implements a generic and extensible registry model that can be instantiated to represent any domain entity such as farmers, workers, students, land records or institutions. The core registry architecture provides a canonical structure for maintaining identity, related attributes, and relationships between registry records. Each registry instance inherits the base behaviors while retaining the ability to define custom domain fields, validation logic, and workflow rules. The approach ensures that the registry product remains consistent at its core, regardless of the domain manifestation, while allowing extensibility through metadata-driven configuration instead of hard-coded logic.

#### 1.1 Dynamic Data Model Definition

The Base Registry supports defining registry data models dynamically through metadata, without requiring changes to the application source code. Registry schema definitions are represented using JSON Schema, enabling implementers to define attributes, constraints, and custom sections that reflect the domain’s requirements. When a new registry type is introduced, the system automatically provisions the required storage tables, version history tables, and change request interfaces by interpreting the model metadata, eliminating repetitive CRUD implementation for each registry.

#### 1.2 Hierarchical Relationships

The registry framework supports hierarchical and relational data modeling. A registry record may refer to one or more child registers, such as a farmer having multiple land holdings, vehicles, family members, or crop records. Relationships are expressed using foreign keys and exposed through dynamic UI patterns such as nested tabs or contextual panels. This model allows each registry instance to evolve naturally with its domain structure while maintaining a consistent interaction pattern across all registries.

***

### 2. Change Management and Approval Workflow

All data modifications in the registry are processed through a centrally managed change request workflow. The Base Registry enforces that no record, including newly created records, can be introduced or modified without undergoing an approval process. When a user or system initiates a change, a new change request is created along with supporting evidence. The change request follows a structured workflow that may include manual verification, multi-level approvals, and automated validations before the changes are committed to the registry.

#### 2.1 Shadow Write Model

Changes are staged in a unified change log (shadow) table before being applied to the master registry. The system maintains a clear separation between the “proposed state” and the “approved state” of a registry record. Only after the change request is approved does the Base Registry write the updated values to the main registry table, ensuring strict governance around data modification. The shadow write model enables visibility into pending changes, concurrent approvals, and auditability of the decision-making process.

#### 2.2 Versioned Record History

Every change that is approved results in a new entry in the registry’s version history table. Version history captures the state of the record at the time of change, the timestamp, and the actors involved in verification and approval. This provides a complete historical ledger of the registry’s evolution across time while ensuring that previous states remain accessible for audits, reporting, and roll-back scenarios. Version history is implemented at a per-registry level, allowing records to maintain an independent state timeline.

***

### 3. Auditability and Traceability

The Base Registry provides end-to-end traceability for all data lifecycle events. Every change request records who initiated the change, who verified the supporting evidence, and who approved the change for execution. The registry maintains immutable logs for each step of the workflow, including timestamps and digital signatures when applicable. This makes the registry suitable for systems that require legal or regulatory accountability, such as land registries, civil registers, and entitlement systems.

#### 3.1 Integrated Evidence Handling

A change request can include documentary evidence such as certifications, photographs, affidavits, or structured data payloads. The registry stores references to the evidence and ensures that verifiers and approvers must explicitly review or acknowledge the evidence before a change request proceeds. Evidence review forms part of the traceability record and can be audited later to establish whether due process was followed when updating registry information.

***

### 4. Data Integrity, Security, and Encryption

The Base Registry provides secure data storage mechanisms that protect sensitive fields through encryption at rest. Individual columns in the registry database can be encrypted using pgcrypto, with encryption keys managed via a dedicated Key Management Service. This approach ensures a high level of confidentiality for personally identifiable information while keeping cryptographic operations transparent to the registry application. The platform ensures secure access to registry data through authenticated and authorized APIs.

#### 4.1 De-Duplication and Record Matching

To prevent duplicate registry records, the platform includes a built-in deduplication engine. Whenever a new change request is created, the registry performs similarity matching against existing records using SQL trigram-based matching or pluggable machine learning models. Possible duplicates are flagged in the change request workflow, allowing verifiers and approvers to take informed decisions before approving the proposed change. Deduplication runs asynchronously, ensuring that user interaction remains responsive while still providing timely alerting.

***

### 5. Async Ingestion Pipeline for External Events

The Base Registry supports ingesting data from external systems through a fully asynchronous ingestion pipeline. Partner systems may send registry-related events in different formats or interoperability standards. Incoming messages are validated for signature authenticity, stored as raw events without transformation, and then processed in stages using Celery workers. The pipeline separates raw persistence, semantic interpretation, and registry update operations, allowing each stage to run independently and at scale.

#### 5.1 Multi-Standard Payload Support

The registry ingestion layer can receive and interpret payloads conforming to different interoperability standards such as SPDci, UNDP's DCI models, or national registry formats. Raw payloads are classified using metadata patterns, and domain-specific semantic meaning is extracted by applying JSONPath or Jinja templates. If the incoming payload contains only reference identifiers, the ingestion pipeline can automatically fetch the full record from the partner system using search APIs defined within the interoperability standard.

***

### 6. Dynamic UI Rendering

The Base Registry includes a dynamic form rendering engine that reads the registry’s JSON schema and generates appropriate UI forms at runtime. Instead of building custom screens for each registry, UI components interpret schema definitions, grouping rules, and widget specifications to render entry forms, detail views, and table listings. Custom field types such as lookup widgets can be declared in the schema and automatically linked with lookup APIs that return enumeration values from centralized metadata.

#### 6.1 Extensible Component Model

UI implementers may define new custom components that the renderer can use inside JSON Schema definitions. The registry frontend exposes reusable interface patterns including hierarchical tab navigation for child registers, audit history views, pending change alerts, and version comparison screens. This ensures a consistent user experience across all registry types while still allowing domain-specific customization.

***

### 7. Event Publishing and WebSub Integration

The Base Registry includes event publishing support using a WebSub-compatible mechanism. Whenever a registry changes state, the system generates and publishes a notification to subscribers who have registered interest in that registry type or event type. Topics can be aligned with interoperability standards, enabling external systems to receive updates in standardized payload formats. The registry integrates with subscription APIs defined by partner registries, allowing it to both publish and receive registry events.

#### 7.1 Standard-Based Message Transformation

Outgoing messages are generated using template-driven mapping engines that convert internal registry records into standard payload structures defined by interoperability specifications. The registry can publish the same registry event in multiple formats by using separate topic namespaces, enabling compatibility with different consumers. Template mappings are stored as metadata and can be versioned independently, supporting backward compatibility without changing registry business logic.

***

### 8. Consent-Aware Data Sharing

The Base Registry supports a consent governance model that ensures that personal data is shared only when a valid consent artefact is in force. Consent decisions are tied to the subject identity, the requesting partner system, the data categories being shared, and an expiry period. The consent artefact can be generated using standardized consent models, and consent enforcement is integrated into data publishing flows so that no outbound data is sent without validating against stored consent records.

***

### 9. Metadata-Driven Extensibility

The registry platform is designed so that all new registry types, operations, and mappings are defined through metadata rather than code. Metadata tables store registry definitions, operation schemas, ingestion patterns, and transformation templates. This model makes the Base Registry product a general-purpose registry engine rather than a hard-coded application. By updating metadata, implementers can introduce new change operations, new message formats, and new partner integrations without modifying source code.

***

### 10. Cloud-Native Deployment and Scaling

The Base Registry is implemented as a set of microservices, with clear separation between registry APIs, ingestion pipeline workers, and metadata management. All components can be scaled horizontally based on workload, allowing the registry to handle high-volume ingestion of events or bursty change approval processes. The platform is compatible with container orchestration environments such as Kubernetes and supports centralized logging, metrics, and distributed tracing for operational visibility.

***

### 11. Observability and Operational Control

The registry exposes metrics and dashboards for monitoring registry health, event ingestion backlog, change requests pending approval, and deduplication risk scores. Administrators can view the status of ingestion pipelines, the history of change events, and audit trails of evidence verification. The platform includes configurable retry policies and dead-letter queues so that failed ingestion or processing jobs can be reviewed and retried safely without losing visibility of failure modes.

***

### 12. Standard Compliance

The Base Registry is built to be compatible with widely adopted interoperability standards for identity, data exchange, and registry events. The platform supports JSON Schema for structural validation and JSON-LD for semantic meaning, making registry payloads machine-interpretable across systems. The registry can be integrated with consent standards such as the Kantara Consent Receipt and event exchange standards such as SPDci, enabling it to operate within large-scale governmental identity and social protection ecosystems.
