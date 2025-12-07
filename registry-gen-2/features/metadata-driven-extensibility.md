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

# Metadata driven extensibility

The registry platform is designed for low-code extensibility, enabling new registry types, registers, operations, data mappings, and partner integrations to be added through configuration rather than changes to the core codebase. The Base Registry provides a minimalist and stable runtime, while each domain implementation — such as an Agriculture Registry with Farmer, Crop, Land, and Vehicle Registers — defines only its extensions: ORM models, Pydantic schemas, business validation logic, and JSON UI schemas.

A registry instance consists of **Registers** represented as individual physical tables (e.g., `farmer_register`, `crop_register`, `land_register`). The overall deployment is called a **Registry**, while each table is a Register. To enable low-code UI and ingestion behavior, each register is accompanied by **metadata entries**, stored in database tables, which define form layouts, register operations, change operations, ingestion patterns, and payload transformation templates.

* **JSON Schema defines the UI form** for each register, determining layout, grouping, validation rules, and custom widgets. This allows implementers to build screens without React coding. JSON Schema becomes the low-code entry point for UI development and reflects the domain model of each register.
* **ORM models and Pydantic schemas are defined manually** by implementers, representing the persistence and API boundary respectively. They are part of the low-code extensibility surface instead of auto-generated. Implementers write minimal Python classes to define the storage schema (ORM) and API validation schema (Pydantic) for each Register, while inheriting shared behavior such as change logging, versioning, and consent checks from the Base Registry.
* **Custom business validation rules** can be written in the service layer. This supports domain needs such as attribute cross-checks, field dependencies, and ID proofing logic without modifying core system logic.
* **Custom UI components (widgets)** such as lookup selectors, evidence upload controls, relation pickers, or autocomplete dropdowns can be registered once and reused across registers. The JSON Schema simply refers to the widget name, allowing rich UI without writing form code.

The ingestion pipeline is also metadata-driven. Incoming event payloads from external systems (e.g., Civil Registries, DCI-based exchanges, UNDP standards) may arrive in different shapes. Ingestion metadata defines:

* **signature matching patterns** to determine the sender, the event type, and the data model,
* **semantic mapping templates** (e.g., Jinja, JSONPath) to convert incoming payloads into register change operations,
* **payload enrichment logic** specifying whether follow-up calls are needed (e.g., when the event contains only a Person ID),
* **routing rules** to direct the incoming data into the appropriate register operations

Celery workers execute ingestion asynchronously. Incoming data is stored as raw payloads with verified signatures. Workers later apply metadata-defined mappings to transform payloads into change operations that flow through the global Change Log engine, triggering approval workflows and version updates.

This architecture makes the Base Registry a **general-purpose registry engine**, not a domain-specific implementation. Core capabilities such as change logging, approvals, consent enforcement, versioning, deduplication pre-checks, and event publication are implemented once in the base layer. All domain diversity is expressed through **low-code extensions**, where new registers, operations, widget configurations, ingestion mappings, and standards integrations are achieved through editable metadata and lightweight Python classes (ORM + Pydantic), without modifying or duplicating core logic.
