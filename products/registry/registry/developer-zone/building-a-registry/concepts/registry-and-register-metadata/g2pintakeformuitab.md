---
description: g2p_intake_form_ui_tabs - UI Configuration (Tabs) for Intake forms
---

# G2PIntakeFormUITab

Defines **tabs within an intake form**, mirroring the tabbed layout used for register record views.

Each row belongs to a [G2PIntakeFormDefinition](g2pintakeformdefinition.md).

***

### Attributes

| Attribute      | Description                                                                      |
| -------------- | -------------------------------------------------------------------------------- |
| **tab\_id**    | Primary key.                                                                     |
| **form\_id**   | Parent intake form. References `g2p_intake_form_definitions.form_id`.            |
| **tab\_label** | Label displayed for the tab (translated when language configuration is present). |
| **tab\_order** | Order within the form. Lower values appear first.                                |

***

### Related metadata

Sections under each tab are configured in G2PIntakeFormUITabSection, which references [G2PRegisterSection](g2pregistersection.md) definitions.
