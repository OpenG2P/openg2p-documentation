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

# Unified Registry model

The Base Registry implements a generic and extensible registry model that can be instantiated to represent any domain entity such as farmers, workers, students, land records or institutions. The core registry architecture provides a canonical structure for maintaining identity, related attributes, and relationships between registry records. Each registry instance inherits the base behaviors while retaining the ability to define custom domain fields, validation logic, and workflow rules. The approach ensures that the registry product remains consistent at its core, regardless of the domain manifestation, while allowing extensibility through metadata-driven configuration instead of hard-coded logic.

#### Dynamic Data Model Definition

The Base Registry supports defining registry data models dynamically through metadata, without requiring changes to the application source code. Registry schema definitions are represented using JSON Schema, enabling implementers to define attributes, constraints, and custom sections that reflect the domain’s requirements. When a new registry type is introduced, the system automatically provisions the required storage tables, version history tables, and change request interfaces by interpreting the model metadata, eliminating repetitive CRUD implementation for each registry.

#### Hierarchical Relationships

The registry framework supports hierarchical and relational data modeling. A registry record may refer to one or more child registers, such as a farmer having multiple land holdings, vehicles, family members, or crop records. Relationships are expressed using foreign keys and exposed through dynamic UI patterns such as nested tabs or contextual panels. This model allows each registry instance to evolve naturally with its domain structure while maintaining a consistent interaction pattern across all registries.
