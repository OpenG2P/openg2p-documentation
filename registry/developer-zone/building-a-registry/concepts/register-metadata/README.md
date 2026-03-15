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
  tags:
    visible: true
---

# Register metadata

While the **ORM models** define how data is stored in the database and the **Pydantic schemas** define validation and API data structures, the OpenG2P Registry platform also requires registers to be defined in **platform metadata tables**.

These metadata definitions allow the platform to dynamically:

* Discover available registers
* Configure UI rendering
* Route API requests
* Load appropriate service classes and domain models

The metadata is also important for the **Registry UI layer**, which uses these definitions to dynamically render register interfaces and workflows.

The primary metadata table used for this purpose is **`g2p_register_definition`**.

Register metadata can be created either:

* Directly through database configuration scripts, or
* Through the **Configuration section of the Registry Staff UI**
