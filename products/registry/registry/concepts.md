---
description: >-
  Core concepts of the OpenG2P Registry platform -- Registry, Register, Table,
  Programme Register, records, identifiers, change requests, hierarchy, and
  metadata-driven configuration.
---

# Concepts

This page explains the foundational concepts of the OpenG2P Registry. Understanding these concepts is essential before working with the platform's features, APIs, or developer tools.

## Registry

A **Registry** is a deployed instance of the OpenG2P Registry platform. It serves as an authoritative, governed data platform for a specific domain or set of related domains. A single Registry instance can host multiple Registers, Tables, and Programme Registers, all sharing common infrastructure for change management, version history, encryption, and interoperability.

Examples of registries that can be built on the platform include a Farmer Registry, a National Social Registry, a Household Registry, a Vehicle Registry, and a Disability Registry.

## Register

A **Register** is a formally managed dataset within a Registry. It represents the core purpose of the Registry and typically assigns a **functional identifier** to every record it contains. This functional ID is a domain-meaningful identifier -- for example, a Farmer ID, a Household ID, or a Vehicle ID.

A single Registry instance may contain multiple Registers. For example, a Household Registry might include:

* A **Household Register** to manage household-level records
* An **Individual Register** to manage the members belonging to those households

Registers are governed through formal approval workflows. Any modification to a record is treated as a **change request**, which must be supported by appropriate documentation, verified, and approved by authorised registry personnel before it is applied.

## Table

A **Table** is a supporting dataset within a Registry. Tables store additional attributes related to records in a Register, particularly when a single register record needs to be associated with multiple related entries.

For example, an Individual Register might need a Table to record the public utility services an individual has subscribed to:

* Electricity connections
* Water connections
* Internet subscriptions
* Library memberships

Unlike Registers, **Tables do not assign functional identifiers** to their records. They exist solely to provide structured, supporting information for records stored in a parent Register.

## Programme register

A **Programme Register** is used to collect and manage applications from individuals or households for a specific benefit programme. Government or implementing agencies announce application windows for programmes, and eligible members of the population submit their information along with supporting documentation.

Similar to Registers, records in a Programme Register undergo verification and approval workflows. Within the OpenG2P ecosystem, a Programme Register commonly serves as the base register for benefit programmes managed by the Programme and Benefit Management System (PBMS). Eligibility rules defined in the programme configuration are evaluated against the records in the Programme Register to determine which applicants qualify for benefits.

### Comparison: Register vs Table vs Programme Register

| Aspect                | Register               | Table                   | Programme Register        |
| --------------------- | ---------------------- | ----------------------- | ------------------------- |
| **Has functional ID** | Yes (e.g. Farmer ID)   | No                      | Yes (e.g. Application ID) |
| **Change management** | Full approval workflow | Follows parent register | Full approval workflow    |
| **Version history**   | Yes                    | Follows parent register | No                        |
| **Deduplication**     | Supported              | Not applicable          | Supported                 |

## Records and identifiers

Every record in the Registry is identified by a combination of system-generated and domain-meaningful identifiers.

**internal\_record\_id** -- A UUID generated automatically by the system for every record. This is the primary key used internally for all database operations, relationships, and history tracking. It is stable and never changes once assigned.

**functional\_record\_id** -- A domain-meaningful identifier assigned to records in Registers and Programme Registers. This is the identifier that has significance in the real world -- for example, a Farmer ID, a Household ID, or an Application ID. The functional ID is unique within its Register and can be generated according to configurable rules.

**application\_reference** -- A human-readable unique identifier assigned when an **intake-form submission** is created. Staff Portal labels it **Application Reference**. It is how operators track a draft or submitted form before (and after) the record exists in a Register. It is not a Functional ID: `functional_record_id` is assigned later, after approval and ingest. The format is configurable; see [Application Reference](design/application-reference.md).

**link\_internal\_record\_id** -- Used to establish a parent-child relationship between records in different Registers within the same Registry. A record in a child Register uses this field to point to the `internal_record_id` of its parent record in the primary Register. For example, a record in the Land Holdings Register would use `link_internal_record_id` to reference the Farmer it belongs to.

## Change requests

All modifications to registry data pass through a **change request workflow**, regardless of the source channel. Whether a change originates from the Staff Portal, the Beneficiary Portal, the Agency App, or the Partner API, it follows the same governed process:

1. **Proposed** -- A change request is created containing the proposed modifications and any supporting documents.
2. **Verified** -- One or more verifiers review the change request and record their observations. The number of verifications required is configurable per register and operation type.
3. **Approved** -- An authorised approver reviews the verified change request and either approves or rejects it. On approval, the change is applied to the register data, and the previous version is preserved in the history table.

This approach ensures that no data enters the Registry without going through a controlled process, providing a complete chain of accountability for every change.

## Registers hierarchy

Registers within a Registry are organised in a parent-child hierarchy. A **primary register** is one whose `master_register_id` is NULL -- it sits at the top of the hierarchy. Child registers are linked to a parent register via the `link_internal_record_id` field on their records.

Consider a Farmer Registry as an example:

* **Farmer Register** -- primary register (master\_register\_id = NULL). Each farmer has one record with a unique Farmer ID.
* **Land Holdings** -- child register linked to the Farmer Register. A farmer may have multiple land holdings.
* **Crops** -- can be a child of Land Holdings, creating a third level. Each land holding may have multiple crops.
* **Family Members** -- child register linked to the Farmer Register.

This structure supports up to three levels of hierarchy where needed (for example, Farmer -> Land -> Crops), though most registries use two levels.

A Registry can technically have multiple primary Registers -- for example, a Household Registry might have both a Household Register and an Individual Register at the primary level -- though a single primary Register is the more common pattern.

## Metadata-driven configuration

The OpenG2P Registry is configured through **metadata tables** rather than code changes. Register definitions, sections, tabs, and UI schemas are all stored as metadata that the platform reads at runtime to determine:

* Which registers exist and how they relate to each other
* How the UI is rendered for each register (sections, tabs, field layouts)
* What validation rules and approval workflows apply
* How API routes are configured for each register

This design means that building a new registry for a new domain -- say, moving from a Farmer Registry to a Vehicle Registry -- is primarily a matter of defining new metadata rather than writing new application code.

For detailed guidance on configuring registers through metadata, see [Building a Registry](developer-zone/building-a-registry/).

## Version history and encryption

**Version history** -- Every approved change to a Register record results in a new version being stored in a corresponding history table. The previous state of the record is preserved along with a reference to the change request that caused the update. This allows querying the state of any record at any point in its history, which is essential for grievance redressal and audit.

**Encryption at rest** -- Sensitive data fields can be encrypted at the column level in the database. This ensures that even with direct database access, protected fields remain unreadable without the appropriate decryption keys. Encryption is configurable per field, allowing each registry to define its own data protection policy based on the sensitivity of the data it holds.
