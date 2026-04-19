---
description: g2p_registry_configuration
---

# G2PRegistryConfiguration

The [`g2p_registry_configuration`](https://github.com/OpenG2P/openg2p-registry-gen2-core/blob/develop/openg2p-registry-core/src/openg2p_registry_core/models/g2p_registry_configuration.py) table stores the **high-level configuration for a Registry instance**. This configuration defines the **identity and branding of the registry deployment**, which is primarily used by the Registry Staff Portal.

A registry instance typically represents a **domain-specific registry operated by a government department or organization**, such as:

* Farmer Registry operated by the Ministry of Agriculture
* Household Registry operated by the Ministry of Social Welfare
* Vehicle Registry operated by the Transport Department

The information stored in this table is used by the platform to display **registry-level metadata and branding in the user interface**.

***

## Attributes

| Attribute             | Description                                                                                                                                                                                                                                                                       |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **configuration\_id** | Primary key of the table. A **UUID** is used to uniquely identify the registry configuration.                                                                                                                                                                                     |
| **registry\_name**    | Defines the name of the registry instance. This typically represents the **official name of the registry and the hosting organization**. Example: _Farmer Registry – Ministry of Agriculture_. The registry name is displayed in the **top header of the Registry Staff Portal**. |
| **registry\_logo**    | A **Base64-encoded image** used as the logo for the registry instance. This is typically the **logo of the hosting department or organization**, and is displayed in the Registry Staff Portal UI.                                                                                |

***

Reference Implementation

Database scripts for g2p\_registry\_configuration for a Reference Farmer Registry are available [here](https://github.com/OpenG2P/openg2p-registry-gen2-extensions/blob/develop/openg2p-registry-farmer-extension/src/openg2p_registry_farmer_extension/db_scripts/registry-configurations/g2p_registry_configuration.sql).
