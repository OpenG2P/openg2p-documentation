---
description: >-
  g2p_register_ui_tabs - UI Configuration (Tabs) for Registers & Program
  Registers
---

# G2PRegisterUITab

The [`g2p_register_tabs`](https://github.com/OpenG2P/registry-platform/blob/develop/core/openg2p-registry-core/src/openg2p_registry_core/models/g2p_register_metadata.py) table stores **tab definitions for registers** within the OpenG2P Registry platform.

This configuration is applicable only to datasets classified as:

* **REGISTER**
* **PROGRAM\_REGISTER**

The **Registry Staff UI** uses this metadata to dynamically render the **tabbed interface** when viewing or managing records within a register.

In addition to defining UI tabs, this table is also used to configure **Intake Forms**, which serve as input channels for creating new records in registers.

A register or program register may have **multiple intake forms**, each designed for different operational channels such as:

* Staff Portal
* Agent Portal
* Beneficiary Portal

***

### Attributes

| Attribute        | Description                                                                    |
| ---------------- | ------------------------------------------------------------------------------ |
| **tab\_id**      | Primary key. Uniquely identifies a tab.                                        |
| **register\_id** | Register to which the tab belongs.                                             |
| **tab\_label**   | Label displayed in the UI (translated when language configuration is present). |
| **tab\_order**   | Display order. Lower values appear first.                                      |

***

### Intake form fields (legacy)

Some deployments store intake-form flags on register tabs. When using dedicated intake form tables (G2PIntakeFormDefinition), prefer seeding `g2p_intake_form_*` metadata instead.

| Attribute                           | Description                                    |
| ----------------------------------- | ---------------------------------------------- |
| **used\_for\_new\_intake\_form**    | Tab represents an intake form for new records. |
| **intake\_form\_name**              | Display name when multiple intake forms exist. |
| **intake\_form\_description**       | Short description of the form.                 |
| **no\_of\_verifications\_required** | Verifications before intake approval.          |
| **intake\_form\_auto\_approve**     | Auto-approve intake submissions.               |

***

### Lifecycle

| Attribute      | Description                                                  |
| -------------- | ------------------------------------------------------------ |
| **is\_active** | When `FALSE`, tab is retired without deleting configuration. |

***

### Related metadata

Sections are linked to tabs through G2PRegisterUITabSection.

| Table                          | Document                                    |
| ------------------------------ | ------------------------------------------- |
| `g2p_register_ui_tab_sections` | G2PRegisterUITabSection                     |
| `g2p_register_sections`        | [G2PRegisterSection](g2pregistersection.md) |

***

## Reference Implementation

Reference implementation of this table for a Farmer Registry can be found in the Farmer Extension repository - [here](https://github.com/OpenG2P/farmer-registry/blob/develop/farmer-extension/src/openg2p_registry_farmer_extension/db_scripts/register-metadata/g2p_register_ui_tabs.sql).
