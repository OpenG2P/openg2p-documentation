---
description: g2p_register_schemas - JSON schemas for datasets
---

# G2PRegisterSchema

The [`G2PRegisterSchema`](https://github.com/OpenG2P/openg2p-registry-gen2-core/blob/develop/openg2p-registry-core/src/openg2p_registry_core/models/g2p_register_schema.py) metadata table stores **JSON-based configuration schemas** used by the platform to control **deduplication, search results, and filtering behavior** for each register.

While ORM models define the structure of the data and Pydantic schemas define validation and API contracts, this metadata table allows the platform to **dynamically configure UI behavior and search functionality** without requiring changes to application code.

Each register can have a corresponding schema definition that specifies:

* Attributes used for **duplicate detection**
* Attributes displayed in **search results**
* Attributes available for **UI filtering**

***

### Attributes

| Attribute                  | Description                                                                                            |
| -------------------------- | ------------------------------------------------------------------------------------------------------ |
| **register\_id**           | Identifier of the register. References `g2p_register_definitions.register_id`.                         |
| **deduplicate\_schema**    | JSON defining attributes used by the deduplication algorithm to detect potential duplicate records.    |
| **search\_result\_schema** | JSON defining attributes displayed in the **Search Results** page (up to eight attributes per result). |
| **filter\_schema**         | JSON defining attributes available as **filter options** on the register list page.                    |

***

### UI Behavior

Applicable to datasets classified as **REGISTER** or **PROGRAM\_REGISTER**.

| Schema                     | UI function                                  |
| -------------------------- | -------------------------------------------- |
| **search\_result\_schema** | Attributes shown in the search results list. |
| **filter\_schema**         | Attributes shown in the filter panel.        |

***

### Related metadata

| Table                      | Document                                          |
| -------------------------- | ------------------------------------------------- |
| `g2p_register_definitions` | [G2PRegisterDefinition](g2pregisterdefinition.md) |

***

## Reference Implementation

A reference implementation of `G2PRegisterSchema` can be found [here](https://github.com/OpenG2P/openg2p-registry-gen2-extensions/blob/develop/openg2p-registry-farmer-extension/src/openg2p_registry_farmer_extension/db_scripts/register-metadata/g2p_register_schemas.sql) in the Farmer Extension repository.
