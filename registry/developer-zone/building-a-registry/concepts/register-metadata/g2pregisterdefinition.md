---
description: g2p_register_definitions - the principal metadata information on Registers
---

# G2PRegisterDefinition

This table - [g2p\_register\_definitions](https://github.com/OpenG2P/openg2p-registry-gen2-core/blob/develop/openg2p-registry-core/src/openg2p_registry_core/models/g2p_register_metadata.py) - stores the **core metadata definition for all register types** within the platform.

Every dataset in the registry—whether it is a **REGISTER**, **TABLE**, or **PROGRAM\_REGISTER**—must have a corresponding entry in this table.

***

## Core Attributes

| Attribute                 | Description                                                                                                                                                                                  |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **register\_id**          | Primary key of the table. Uniquely identifies a register definition.                                                                                                                         |
| **register\_mnemonic**    | Short name for the register. This is a **critical configuration field**. The platform dynamically derives the underlying models, history models, and service classes based on this mnemonic. |
| **register\_subject**     | A short label describing the subject or entity represented by the register.                                                                                                                  |
| **register\_description** | A detailed description of the purpose of the register.                                                                                                                                       |

***

## Dynamic Class Resolution

The platform dynamically constructs class names based on the **`register_mnemonic`**.

| Component     | Derived Class                  |
| ------------- | ------------------------------ |
| ORM Model     | `G2PRegister{Mnemonic}`        |
| History Model | `G2PRegisterHistory{Mnemonic}` |
| Service Class | `G2PRegisterService{Mnemonic}` |

For example, if the register mnemonic is **Farmer**, the platform will resolve:

| Type          | Derived Class              |
| ------------- | -------------------------- |
| ORM Model     | `G2PRegisterFarmer`        |
| History Model | `G2PRegisterHistoryFarmer` |
| Service Class | `G2PRegisterServiceFarmer` |

This mechanism allows the platform to **load domain-specific implementations dynamically**.

***

## Register Hierarchy Configuration

| Attribute                | Description                                                      |
| ------------------------ | ---------------------------------------------------------------- |
| **master\_register\_id** | Defines hierarchical relationships between registers and tables. |

For example:

| Register            | Master Register     |
| ------------------- | ------------------- |
| Household Register  | None                |
| Individual Register | Household Register  |
| Subscriptions Table | Individual Register |

This hierarchy enables the platform to understand **parent-child relationships between datasets**.

***

## Register Display Configuration

| Attribute          | Description                                                                                                                      |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| **register\_rank** | Determines the order in which registers appear in UI dropdowns. Registers with a **lower rank value appear higher** in the list. |
| **register\_icon** | UI icon associated with the register.                                                                                            |
| **has\_image**     | Indicates whether records in the register include image attributes.                                                              |

***

## Register Type Configuration

| Attribute             | Description                                                                                                         |
| --------------------- | ------------------------------------------------------------------------------------------------------------------- |
| **register\_purpose** | Specifies the classification of the register. Possible values include: `REGISTER`, `TABLE`, and `PROGRAM_REGISTER`. |

***

## Program Register Configuration

These fields are applicable **only when the register type is `PROGRAM_REGISTER`**.

| Attribute             | Description                                                             |
| --------------------- | ----------------------------------------------------------------------- |
| **program\_id**       | Identifier of the benefit program associated with the program register. |
| **program\_mnemonic** | Short mnemonic representing the benefit program.                        |

This configuration links the register with the **Program and Benefit Management System (PBMS)**.

***

## Deduplication Configuration

The platform supports **record de-duplication** during data entry or change requests.

| Attribute                   | Description                                                                                                  |
| --------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **dedup\_is\_enabled**      | Indicates whether deduplication should be applied to the register.                                           |
| **dedup\_threshold\_score** | Defines the threshold score used by the deduplication algorithm to classify records as potential duplicates. |

The specific attributes used for deduplication are defined as a **JSON configuration** in the table:

[`g2p_register_schemas`](https://github.com/OpenG2P/openg2p-registry-gen2-core/blob/develop/openg2p-registry-core/src/openg2p_registry_core/models/g2p_register_schema.py)

The deduplication process typically runs during **change request processing**, where newly submitted records are compared against existing records to identify potential duplicates.

## Reference Implementation

A reference implementation of the **register metadata configuration** can be found in the Farmer Registry extension.

The SQL script that initializes the `g2p_register_definition` table and other registry metadata is available in the [OpenG2P Registry Extensions repository](https://github.com/OpenG2P/openg2p-registry-gen2-extensions) — Farmer Extension.

The g2p\_register\_definition database script for Farmer Registry is available [here](https://github.com/OpenG2P/openg2p-registry-gen2-extensions/blob/develop/openg2p-registry-farmer-extension/src/openg2p_registry_farmer_extension/db_scripts/register-metadata/g2p_register_definitions.sql).

```
```
