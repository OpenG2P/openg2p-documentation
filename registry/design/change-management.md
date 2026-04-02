---
description: Change request workflow -- how every registry mutation flows through approval before being committed.
---

# Change Management

## Overview

Every modification to registry data flows through a **change request** (internally called a change log). This is a core design principle of the OpenG2P Registry: no record, whether newly created or updated, is written to the master register table until the corresponding change request has been approved. This model provides full auditability, supports multi-level verification, and enables concurrent review of pending changes.

## Change log

The `g2p_register_change_log` table is the central staging area for all proposed changes.

| Column | Description |
| --- | --- |
| `change_log_id` | Primary key |
| `register_id` | The target register |
| `internal_record_id` | The target record (NULL for new-record operations) |
| `operation_id` | The section/operation being modified |
| `change_payload` | JSONB document containing the proposed field values |
| `source_channel_id` | Identifies the origin channel (staff portal, partner API, ingestion pipeline) |
| `changed_at` | Timestamp when the change request was created |
| `changed_by` | Identity of the initiator |
| `approval_status` | Current status (pending, approved, rejected) |
| `approved_at` | Timestamp of approval or rejection |
| `approved_by` | Identity of the approver |

## Supporting documents

Change requests may include supporting documents stored in the `g2p_register_change_log_documents` table.

| Column | Description |
| --- | --- |
| `document_id` | Primary key |
| `change_log_id` | Foreign key to the parent change log |

Documents are stored in MinIO and referenced by their document identifier.

## Verification

Before a change request can be approved, it may require one or more verifications. The number of required verifications is configured per section (operation). Verifications are recorded in the `g2p_register_verifications` table.

| Column | Description |
| --- | --- |
| `verification_id` | Primary key |
| `register_id` | The target register |
| `internal_record_id` | The target record |
| `operation_id` | The section/operation being verified |
| `change_log_id` | Foreign key to the change log being verified |
| `verified_by` | Identity of the verifier |
| `verified_at` | Timestamp of verification |
| `verification_observations` | Free-text observations recorded by the verifier |
| `is_ok` | Boolean indicating whether the verification passed |

Multiple verifications can be configured per section. All required verifications must pass before the change request becomes eligible for approval.

## Approval flow

When a change request is approved, the following operations are executed within a single transaction:

1. **Insert into history table** -- a snapshot of the approved state is written to the domain-specific history table using dynamic SQL.
2. **Upsert into register table** -- the approved values are written to the domain-specific register table. For new records this is an insert; for updates it is an upsert.
3. **Update change log status** -- the `approval_status`, `approved_at`, and `approved_by` fields are updated on the change log record.

{% hint style="info" %}
Auto-approval can be configured per section per source channel. When auto-approval is enabled, the change request is created and immediately approved without manual intervention. This is commonly used for trusted ingestion channels.
{% endhint %}

## Service methods

`g2p_register_service` is the base service class that provides the change management API. All domain register services extend this class.

| Method | Description |
| --- | --- |
| `create_change_log` | Creates a new change request with payload and optional documents |
| `get_change_logs` | Retrieves change logs with filtering and pagination |
| `delete_change_log` | Removes a pending change request |
| `add_change_log_verification` | Records a verification against a change log |
| `get_change_log_verifications` | Retrieves verifications for a given change log |
| `approve_change_log` | Executes the three-step approval flow (history insert, register upsert, status update) using dynamic SQL resolved from the register mnemonic |
| `validate_change_log` | Abstract method. Domain-specific register services implement this to apply business validations on the change payload before approval. |

The `validate_change_log` method is intentionally abstract. Each domain model class implements its own validation logic based on domain-specific attributes and business rules.

{% content-ref url="../features/change-management-and-approval-workflow.md" %}
change-management-and-approval-workflow.md
{% endcontent-ref %}
