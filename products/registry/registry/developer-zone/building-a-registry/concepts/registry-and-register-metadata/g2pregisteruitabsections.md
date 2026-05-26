---
description: g2p_register_ui_tab_sections - UI Tab Configuration (Sections) for Registers
---

# G2PRegisterUITabSections

Junction table associating G2PRegisterSection definitions with G2PRegisterUITab definitions. Defines **section ordering within a tab**.

Sections are defined once in `g2p_register_sections`; this table controls **where** each section appears and **in what order**.

***

### Attributes

| Attribute            | Description                                                   |
| -------------------- | ------------------------------------------------------------- |
| **tab\_section\_id** | Primary key. Uniquely identifies the tab–section association. |
| **register\_id**     | Register identifier (stored for query convenience).           |
| **tab\_id**          | References `g2p_register_ui_tabs.tab_id`.                     |
| **section\_id**      | References `g2p_register_sections.section_id`.                |
| **section\_order**   | Order within the tab. Lower values appear first.              |

***

### Relationship model

{% code lineNumbers="true" %}
```mermaid
erDiagram
    G2PRegisterUITab ||--o{ G2PRegisterUITabSection : "has"
    G2PRegisterSection ||--o{ G2PRegisterUITabSection : "included in"

    G2PRegisterUITab {
        uuid tab_id PK
        uuid register_id
        string tab_label
        int tab_order
    }

    G2PRegisterUITabSection {
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
{% endcode %}

A section definition may appear in multiple tabs via multiple junction rows.
