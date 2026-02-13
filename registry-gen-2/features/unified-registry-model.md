# Unified Registry model

The Base Registry implements a generic and extensible registry model that can be instantiated to represent any domain entity such as farmers, workers, students, land records or institutions. The core registry architecture provides a canonical structure for maintaining identity, related attributes, and relationships between registry records. Each registry instance inherits the base behaviors while retaining the ability to define custom domain fields, validation logic, and workflow rules. The approach ensures that the registry product remains consistent at its core, regardless of the domain manifestation, while enabling a low-code extensibility model through metadata-driven configuration rather than hard-coded logic.

**Registry and Registers**\
In the Base Registry platform, the deployed instance is referred to as a **Registry**, while each persisted dataset within that instance is called a **Register**. A Registry represents a domain context such as agriculture, social protection, or education, and contains multiple Registers that store structured records. For example, an Agriculture Registry may include a Farmer Register, a Crop Register, a Land Register, and a Vehicle Register. Each Register maintains its own schema, version history, and change workflow, but inherits uniform governance and lifecycle management from the parent Registry. This terminology ensures conceptual clarity between the overall domain registry and the specific data tables representing distinct entity types.

#### 1.1 Dynamic Data Model Definition

The Base Registry supports defining the structure of each Register dynamically through metadata, without requiring changes to the application source code. Data models are expressed once and materialized across three layers of the system:&#x20;

1. a JSON Schema used to render UI forms
2. an ORM model defining the persistence structure of each Register in PostgreSQL
3. and a Pydantic schema governing validation and API representations

This unified model approach enables a low-code configuration experience where implementers declare attributes, constraints, and custom sections in metadata rather than writing business logic or CRUD operations. When a new Registry instance is created, the platform interprets the model metadata (the three layers explained above), and exposes the required APIs and change request interfaces in a consistent manner across all Registers.

#### 1.2 Hierarchical Relationships

The registry framework supports hierarchical and relational data modeling. A registry record may refer to one or more child registers, such as a farmer having multiple land holdings, vehicles, family members, or crop records. Relationships are expressed using linked IDs and exposed through dynamic UI patterns with nested tabs. This model allows each registry instance to evolve naturally with its domain structure while maintaining a consistent interaction pattern across all registries.
