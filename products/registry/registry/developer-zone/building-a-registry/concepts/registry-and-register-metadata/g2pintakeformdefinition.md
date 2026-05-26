---
description: >-
  g2p_intake_form_definitions - the principal metadata information on creation
  of intake forms on registers
---

# G2PIntakeFormDefinition

Defines **intake forms** — structured input channels for creating new records in a **REGISTER** or **PROGRAM\_REGISTER**.

An intake form groups sections (via G2PIntakeFormUITab and G2PIntakeFormUITabSection) into a workflow exposed through portal UIs or the ingestion pipeline.

***

### Attributes

| Attribute                               | Description                                                         |
| --------------------------------------- | ------------------------------------------------------------------- |
| **form\_id**                            | Primary key.                                                        |
| **register\_id**                        | Target register. References `g2p_register_definitions.register_id`. |
| **form\_mnemonic**                      | Unique short name for API routing and configuration lookup.         |
| **form\_description**                   | Human-readable description of purpose and channel.                  |
| **number\_of\_verifications**           | Independent verifications required before approval.                 |
| **used\_only\_in\_ingestion\_pipeline** | When `TRUE`, form is pipeline-only and not shown in portal UIs.     |

***

### Intake workflow

When a user submits an intake form:

1. The platform creates intake submission records and **change requests per section**.
2. The **primary section** (G2PRegisterSection) is processed first.
3. Required verifications must complete before approval.
4. On approval, change requests are applied to the register.

***

### Related metadata

| Table                             | Document                                    |
| --------------------------------- | ------------------------------------------- |
| `g2p_intake_form_ui_tabs`         | G2PIntakeFormUITab                          |
| `g2p_intake_form_ui_tab_sections` | G2PIntakeFormUITabSection                   |
| `g2p_register_sections`           | [G2PRegisterSection](g2pregistersection.md) |

Input channel linkage (staff portal, agent portal, etc.) may be configured in `meta_data/registry-configurations/g2p_input_mechanisms.sql`.
