---
description: Core data model of OpenG2P Registry -- registers, records, versioning, and domain extension patterns.
---

# Data Model

The OpenG2P Registry data model is built around a small set of abstract base classes that every domain register extends. This section describes the core entities, their relationships, and the pattern used to add domain-specific registers without modifying platform code.

## Core entities

### Register definition

The `g2p_register_definition` table stores metadata about every register in the instance.

| Column | Description |
| --- | --- |
| `register_id` | Primary key |
| `register_mnemonic` | Short unique name (e.g. `farmer`, `crop`, `worker`) |
| `register_description` | Human-readable description |
| `master_register_id` | Foreign key to the parent register. `NULL` for primary registers. |
| `program_application` | Boolean flag indicating whether this register holds program application data |

Key methods on the definition model:

1. **`get_primary_registers`** -- returns all registers where `master_register_id` is `NULL`.
2. **`get_child_registers(master_register_id)`** -- returns registers linked to the given parent.
3. **`get_program_application_registers`** -- returns registers flagged as program application registers.

## Register (abstract base)

`g2p_register` is the abstract base class extended by every domain register model (e.g. `farmer_register`, `crop_register`). It defines the common columns present in all register tables.

| Column | Notes |
| --- | --- |
| `internal_record_id` | Primary key -- UUID |
| `functional_record_id` | Unique index. External-facing identifier (e.g. a national ID). |
| `link_record_id` | Foreign key to the parent register record (`internal_record_id`). Applicable only for child registers, not primary registers. Non-unique index. |
| `created_at` | Timestamp of record creation |
| `last_updated_at` | Timestamp of last approved update |
| `last_approved_by` | Identity of the last approver |
| `search_text` | `TEXT` column with trigram indexing for full-text search across the record |

## Version history

`g2p_register_history` is the abstract base class for per-register history tables. Each time a change request is approved, the approved state is written to the corresponding history table, creating a complete audit trail.

| Column | Notes |
| --- | --- |
| `history_record_id` | Primary key -- UUID |
| `internal_record_id` | Non-unique index linking to the register record |
| `change_log_id` | Non-unique index linking to the originating change request |
| `link_record_id` | Non-unique index. Only for child registers. |
| `created_by` | Identity of the user or system that created the change |
| `approved_by` | Identity of the approver |

{% hint style="info" %}
Program application registers do not have history tables. History tracking applies only to primary and child registers.
{% endhint %}

## Sections and tabs

Register data is organised into **sections** (`g2p_register_sections`) that are grouped into **tabs** (`g2p_register_tabs`). Each section is the primary unit of modification -- a change request targets a specific section, and the JSON form schema attached to that section drives the staff portal form rendering.

Sections also control approval rules: verification requirements, auto-approval settings, and required documents are all configured at the section level.

{% hint style="info" %}
For full details on section and tab metadata configuration, refer to the developer documentation.
{% endhint %}

## Domain extension pattern

A domain register (e.g. `farmer_register`) extends the abstract `g2p_register` class and sets its `register_mnemonic` (e.g. `"farmer"`). Based on this mnemonic, the parent class methods resolve the concrete table names for dynamic SQL operations:

* `g2p_register_farmer` -- the register table
* `g2p_register_history_farmer` -- the history table

The `change_log` and `verifications` tables are shared across all registers and do not require per-domain tables.

A **`register_factory`** is provided that accepts a `register_mnemonic` and returns the appropriate register class instance. Controllers use this factory to dispatch operations without hard-coding domain knowledge.

{% content-ref url="../developer-zone/building-a-registry/" %}
building-a-registry
{% endcontent-ref %}
