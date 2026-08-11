---
description: g2p_register_definitions - the principal metadata information on Registers
---

# G2PRegisterDefinition

This table - [g2p\_register\_definitions](https://gitlab.com/openg2p/registry/registry-platform/-/blob/develop/core/openg2p-registry-core/src/openg2p_registry_core/models/g2p_register_metadata.py) - stores the core metadata definition for all register types within the platform.

Every dataset in the registry whether it is a **REGISTER**, **TABLE**, **PROGRAM\_REGISTER**, or **CORE\_TABLE** must have a corresponding entry in this table.

***

### Core Attributes

| Attribute                 | Description                                                                                                                                                                                  |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **register\_id**          | Primary key of the table. Uniquely identifies a register definition.                                                                                                                         |
| **register\_mnemonic**    | Short name for the register. This is a **critical configuration field**. The platform dynamically derives the underlying models, history models, and service classes based on this mnemonic. |
| **register\_subject**     | A short label describing the subject or entity represented by the register.                                                                                                                  |
| **register\_description** | A detailed description of the purpose of the register.                                                                                                                                       |

***

### Dynamic Class Resolution

The platform dynamically constructs class names based on the **`register_mnemonic`**.

| Component      | Derived Class                        |
| -------------- | ------------------------------------ |
| ORM Model      | `G2PRegister{Mnemonic}`              |
| History Model  | `G2PRegisterHistory{Mnemonic}`       |
| Domain Service | `G2PRegisterDomainService{Mnemonic}` |

For example, if the register mnemonic is **`PrimarySubject`**, the platform resolves:

| Type           | Derived Class                            |
| -------------- | ---------------------------------------- |
| ORM Model      | `G2PRegisterPrimarySubject`              |
| History Model  | `G2PRegisterHistoryPrimarySubject`       |
| Domain Service | `G2PRegisterDomainServicePrimarySubject` |

This mechanism allows the platform to **load domain-specific implementations dynamically**.

***

### Register Hierarchy Configuration

| Attribute                | Description                                                      |
| ------------------------ | ---------------------------------------------------------------- |
| **master\_register\_id** | Defines hierarchical relationships between registers and tables. |

For example:

| Register                 | Master Register          |
| ------------------------ | ------------------------ |
| Group register           | None                     |
| Primary subject register | Group register           |
| Child table              | Primary subject register |

This hierarchy enables the platform to understand **parent-child relationships between datasets**.

***

### Register Display Configuration

| Attribute          | Description                                                                                                                      |
| ------------------ | -------------------------------------------------------------------------------------------------------------------------------- |
| **register\_rank** | Determines the order in which registers appear in UI dropdowns. Registers with a **lower rank value appear higher** in the list. |
| **register\_icon** | UI icon associated with the register.                                                                                            |
| **has\_image**     | Indicates whether records in the register include image attributes.                                                              |

***

### Register Type Configuration

| Attribute             | Description                                                                               |
| --------------------- | ----------------------------------------------------------------------------------------- |
| **register\_purpose** | Classification of the register: `REGISTER`, `TABLE`, `PROGRAM_REGISTER`, or `CORE_TABLE`. |

***

### Program Register Configuration

Applicable **only** when `register_purpose` is `PROGRAM_REGISTER`.

| Attribute             | Description                                                             |
| --------------------- | ----------------------------------------------------------------------- |
| **program\_id**       | Identifier of the benefit program associated with the program register. |
| **program\_mnemonic** | Short mnemonic representing the benefit program.                        |

***

### ID Generation Configuration

| Attribute                                | Description                                                                                          |
| ---------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| **functional\_id\_generation\_required** | Indicates whether the platform should generate a functional identifier for records in this register. |

***

### Deduplication Configuration

| Attribute                   | Description                                                                           |
| --------------------------- | ------------------------------------------------------------------------------------- |
| **dedup\_is\_enabled**      | Indicates whether deduplication should be applied to the register.                    |
| **dedup\_threshold\_score** | Threshold score used by the deduplication algorithm to classify potential duplicates. |

The attributes used for deduplication are defined as JSON in [`g2p_register_schemas`](g2pregisterschema.md).

***

### Completion Score Configuration

| Attribute                       | Description                                                                                |
| ------------------------------- | ------------------------------------------------------------------------------------------ |
| **completion\_score\_required** | Indicates whether section completion scores must be computed for records in this register. |

***

### Registrant Authentication Configuration

| Attribute                                       | Description                                                                                       |
| ----------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **requires\_registrant\_authentication**        | Indicates whether registrants must authenticate before interacting with records in this register. |
| **registrant\_authentication\_validity\_days**  | Number of days a registrant authentication remains valid.                                         |
| **registrant\_re\_auth\_warning\_days\_before** | Number of days before authentication expiry when a re-authentication warning is shown.            |

***

## Reference Implementation

A reference implementation of the **register metadata configuration** can be found in the Farmer Registry extension.

The SQL script that initializes the `g2p_register_definition` table and other registry metadata is available in the [OpenG2P Registry Extensions repository](https://gitlab.com/openg2p/registry/farmer-registry/-/tree/develop/farmer-extension) — Farmer Extension.

The g2p\_register\_definition database script for Farmer Registry is available [here](https://gitlab.com/openg2p/registry/farmer-registry/-/blob/develop/farmer-extension/src/openg2p_registry_farmer_extension/db_scripts/register-metadata/g2p_register_definitions.sql).

```
```
