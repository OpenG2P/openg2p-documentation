---
description: >-
  g2p_intake_form_ui_tab_sections - UI Tab Configuration (Sections) for Intake
  forms
---

# G2PIntakeFormUITabSections

Junction table associating [G2PRegisterSection](g2pregistersection.md) definitions with [G2PIntakeFormUITab](g2pintakeformuitab.md) definitions. Defines which sections appear on each intake form tab and in what order.

***

### Attributes

| Attribute            | Description                                                      |
| -------------------- | ---------------------------------------------------------------- |
| **tab\_section\_id** | Primary key.                                                     |
| **tab\_id**          | Intake form tab. References `g2p_intake_form_ui_tabs.tab_id`.    |
| **section\_id**      | Register section. References `g2p_register_sections.section_id`. |
| **section\_order**   | Order within the tab. Lower values appear first.                 |

***

### Relationship model

```mermaid
erDiagram
    G2PIntakeFormDefinition ||--o{ G2PIntakeFormUITab : "has"
    G2PIntakeFormUITab ||--o{ G2PIntakeFormUITabSection : "has"
    G2PRegisterSection ||--o{ G2PIntakeFormUITabSection : "reuses"

    G2PIntakeFormDefinition {
        uuid form_id PK
        uuid register_id FK
        string form_mnemonic
        int number_of_verifications
    }

    G2PIntakeFormUITab {
        uuid tab_id PK
        uuid form_id FK
        string tab_label
        int tab_order
    }

    G2PIntakeFormUITabSection {
        uuid tab_section_id PK
        uuid tab_id FK
        uuid section_id FK
        int section_order
    }

    G2PRegisterSection {
        uuid section_id PK
        uuid register_id
        uuid section_register_id
        string section_mnemonic
    }
```

Intake forms **reuse** section definitions from register metadata. Submitting the form creates change requests against the referenced sections.
