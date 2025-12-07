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

The registry platform is designed so that all new registry types, operations, and mappings are defined through metadata rather than code. Metadata tables store registry definitions, operation schemas, ingestion patterns, and transformation templates. This model makes the Base Registry product a general-purpose registry engine rather than a hard-coded application. By updating metadata, implementers can introduce new change operations, new message formats, and new partner integrations without modifying source code.
