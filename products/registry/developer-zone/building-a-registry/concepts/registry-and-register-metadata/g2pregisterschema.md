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

## Attributes

<table><thead><tr><th width="202.65509033203125">Attribute</th><th>Description</th></tr></thead><tbody><tr><td><strong>register_id</strong></td><td>The identifier of the register to which this schema configuration belongs. This references the register defined in the <code>g2p_register_definition</code> table.</td></tr><tr><td><strong>deduplicate_schema</strong></td><td>Stored in <strong>JSON format</strong>. Defines the attributes that should be used by the platform’s deduplication algorithm to detect potential duplicate records in the register.</td></tr><tr><td><strong>search_result_schema</strong></td><td>Stored in <strong>JSON format</strong>. Defines the attributes that should be displayed in the <strong>Search Results page</strong> in the Registry Staff UI. The UI displays up to <strong>eight attributes</strong> for each search result entry. All attributes of the register become visible when the user opens the <strong>detailed view</strong> of a specific record.</td></tr><tr><td><strong>filter_schema</strong></td><td>Stored in <strong>JSON format</strong>. Defines the attributes that should be available as <strong>filter options</strong> in the UI. The filter section on the register list page is rendered dynamically based on this configuration.</td></tr></tbody></table>

***

## UI Behavior Driven by the Schema

The Registry Staff UI uses this metadata to dynamically construct search and filtering interfaces.

This configuration is applicable only to datasets classified as:

* **REGISTER**
* **PROGRAM\_REGISTER**

<table><thead><tr><th width="205.36334228515625">Schema</th><th>UI Function</th></tr></thead><tbody><tr><td><strong>search_result_schema</strong></td><td>Defines which attributes appear in the <strong>Search Results List</strong>.</td></tr><tr><td><strong>filter_schema</strong></td><td>Determines which attributes appear in the <strong>Filter panel</strong> on the register list page.</td></tr></tbody></table>

This approach allows implementation teams to **customize UI behavior without modifying frontend code**.

***

## Reference Implementation

A reference implementation of `G2PRegisterSchema` can be found [here](https://github.com/OpenG2P/openg2p-registry-gen2-extensions/blob/develop/openg2p-registry-farmer-extension/src/openg2p_registry_farmer_extension/db_scripts/register-metadata/g2p_register_schemas.sql) in the Farmer Extension repository.
