---
description: >-
  g2p_register_ui_tabs - UI Configuration (Tabs) for Registers & Program
  Registers
---

# G2PRegisterUITab

The [`g2p_register_tabs`](https://github.com/OpenG2P/openg2p-registry-gen2-core/blob/develop/openg2p-registry-core/src/openg2p_registry_core/models/g2p_register_metadata.py) table stores **tab definitions for registers** within the OpenG2P Registry platform.

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

## Attributes

<table data-full-width="true"><thead><tr><th width="124.8968505859375">Attribute</th><th>Description</th></tr></thead><tbody><tr><td><strong>tab_id</strong></td><td>Primary key of the table. Uniquely identifies a tab definition across the platform.</td></tr><tr><td><strong>register_id</strong></td><td>Identifier of the register to which the tab definition belongs.</td></tr><tr><td><strong>tab_label</strong></td><td>The label displayed for the tab in the UI. The Staff UI automatically translates this label based on the user's language preference.</td></tr><tr><td><strong>tab_order</strong></td><td>Determines the order in which the tab appears for the register. Tabs with lower values appear earlier in the UI.</td></tr></tbody></table>

***

## Intake Form Configuration

The following attributes apply when the tab is used as an **Intake Form**.

<table data-full-width="true"><thead><tr><th width="246.15106201171875">Attribute</th><th>Description</th></tr></thead><tbody><tr><td><strong>used_for_new_intake_form</strong></td><td>Indicates whether the tab represents an <strong>intake form</strong> used to create new records in a REGISTER or PROGRAM_REGISTER.</td></tr><tr><td><strong>intake_form_name</strong></td><td>Name of the intake form. When multiple intake forms exist for a register, this name helps users distinguish between them when initiating a new intake process.</td></tr><tr><td><strong>intake_form_description</strong></td><td>A short description explaining the purpose of the intake form.</td></tr><tr><td><strong>no_of_verifications_required</strong></td><td>Specifies the number of verification steps required before the intake form submission can be approved.</td></tr><tr><td><strong>intake_form_auto_approve</strong></td><td>Indicates whether submissions from this intake form are <strong>automatically approved</strong> or require manual verification and approval before a change request is created.</td></tr></tbody></table>

***

## Lifecycle Configuration

<table data-full-width="true"><thead><tr><th width="113.23358154296875">Attribute</th><th>Description</th></tr></thead><tbody><tr><td><strong>is_active</strong></td><td>Indicates whether the tab or intake form is currently active. This allows administrators to <strong>retire forms that are no longer in use</strong> without deleting their configuration.</td></tr></tbody></table>

***

## UI Behavior

The Registry Staff UI uses this metadata to dynamically:

* Render **tabbed views** for registers
* Present **intake forms** for record creation
* Determine **form workflows and verification requirements**
* Control **tab ordering and visibility**

This metadata-driven approach allows implementation teams to **configure UI workflows without modifying application code**.

***

## Reference Implementation

Reference implementation of this table for a Farmer Registry can be found in the Farmer Extension repository - [here](https://github.com/OpenG2P/openg2p-registry-gen2-extensions/blob/develop/openg2p-registry-farmer-extension/src/openg2p_registry_farmer_extension/db_scripts/register-metadata/g2p_register_ui_tabs.sql).
