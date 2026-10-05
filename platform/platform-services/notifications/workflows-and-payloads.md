---
description: >-
  The 16 notification workflows. Audience, channels, copy, buttons, and
  the full payload catalog for each event.
---

# Workflows and payloads

There are 16 workflows. Eight belong to Registry. Eight belong to AWE. The catalog below is the implementer set: every field the sender should put on the payload, not only the fields today's email happens to print.

Event keys are dotted. Novu trigger ids replace `.` and `_` with `-`. `NOTIFICATION_WORKFLOWS` binds the two. Templates read `{{payload.field}}`. Python does not render the copy.

Registrant copy stays plain language. It uses `record_name`, `register_subject`, `registry_name`, and `application_reference`. It does not print internal ids. Staff titles use the same friendly fields (`stage_name`, `policy_name`, `artifact_type_label`, display names). Ids stay on the payload for links and for the notification id. They do not belong in the title.

Email bodies are HTML. This page records the subject, the SMS line, the in-app title and body, and the buttons. It does not paste the HTML.

How to add a key is in [Implementing a send](implementing.md). How the workflows are seeded is in [Novu](novu.md).

## Registrant contact in an extension

Registry does not read email and phone itself. [`resolve_registrant_contact`](https://github.com/OpenG2P/registry-platform/blob/develop/core/openg2p-registry-core/src/openg2p_registry_core/helpers/registrant_contact.py) loads the register mnemonic and calls that mnemonic's domain service:

```python
await service.resolve_contact(session, internal_record_id)
```

The base method on [`G2PRegisterDomainService`](https://github.com/OpenG2P/registry-platform/blob/develop/core/openg2p-registry-core/src/openg2p_registry_core/services/g2p_register_domain_service.py) loads the ORM row and uses `contact_from_record`. That helper reads `email` or `emails`, and `phone` or `phone_numbers`. A list uses the item with `is_primary`, otherwise the first item. It returns `RegistrantContact(person_id, email, phone, name)`.

Override `resolve_contact` when the row is not the person. Return `RegistrantContact` yourself. Household does this: load the household, read `household_head_internal_record_id`, then ask the Individual domain service for that head's contact. Source: [NSR household domain service](https://github.com/OpenG2P/national-social-registry/blob/develop/nsr-extension/src/openg2p_registry_nsr_extension/register_domain/services/g2p_register_domain_service_household.py).

```python
async def resolve_contact(self, session, internal_record_id):
    household = await self.load_register_row(session, internal_record_id)
    head_id = getattr(household, "household_head_internal_record_id", None) if household else None
    if not head_id:
        return None
    factory = G2PRegisterDomainFactory.get_component()
    individual = factory.get_domain_service("Individual") if factory else None
    if individual is None:
        return None
    return await individual.resolve_contact(session, str(head_id))
```

No email and no phone means `has_channel()` is false and the registrant send is skipped. A lookup error is logged and also skips the send. Intake can still notify when the domain service returns nothing: it scans section records on the submission for an email or phone.

## All 16 workflows

| Event key | Trigger id | Name | Audience | Channels |
| --- | --- | --- | --- | --- |
| `change_request.created` | `change-request-created` | Change request created | Registrant | Email, SMS |
| `change_request.approved` | `change-request-approved` | Change request approved | Registrant | Email, SMS |
| `change_request.rejected` | `change-request-rejected` | Change request rejected | Registrant | Email, SMS |
| `intake_form.submission_created` | `intake-form-submission-created` | Intake form submission created | Registrant | Email, SMS |
| `intake_form.submission_approved` | `intake-form-submission-approved` | Intake form submission approved | Registrant | Email, SMS |
| `intake_form.submission_rejected` | `intake-form-submission-rejected` | Intake form submission rejected | Registrant | Email, SMS |
| `register_export.completed` | `register-export-completed` | Register export completed | Staff who requested the export | In-app, email |
| `register_export.failed` | `register-export-failed` | Register export failed | Staff who requested the export | In-app, email |
| `approval.stage_started` | `approval-stage-started` | Approval stage started | Stage approvers | In-app, email |
| `approval.task_reassigned` | `approval-task-reassigned` | Approval task reassigned | New assignee | In-app, email |
| `approval.stage_escalated` | `approval-stage-escalated` | Approval stage escalated | Added approvers | In-app, email |
| `approval.task_expired` | `approval-task-expired` | Approval task expired | Expired assignee | In-app, email |
| `approval.request_approved` | `approval-request-approved` | Approval request approved | Requester | In-app, email |
| `approval.request_rejected` | `approval-request-rejected` | Approval request rejected | Requester | In-app, email |
| `approval.request_cancelled` | `approval-request-cancelled` | Approval request cancelled | Requester | In-app, email |
| `approval.stage_quorum_skipped` | `approval-stage-quorum-skipped` | Approval stage quorum skipped | Skipped approvers | In-app only |

Registrant workflows have no in-app step and no buttons. Export has one button, **Open register**, at `{{payload.staff_portal_base_url}}/en/register/{{payload.register_mnemonic}}`. Every AWE workflow has **View task** at `{{payload.staff_portal_base_url}}/en{{payload.task_path}}` and **Show all tasks** at `{{payload.staff_portal_base_url}}/en{{payload.tasks_list_path}}`. Quorum skipped has those buttons and no email or SMS.

## Registry events

Source: [`notification.py`](https://github.com/OpenG2P/registry-platform/blob/develop/core/openg2p-registry-core/src/openg2p_registry_core/helpers/notification.py). A failed send is logged and does not fail the business action.

| Event key | Where it is sent |
| --- | --- |
| `change_request.created` | Staff API `create_change_request`, after commit. Celery change-request ingest |
| `change_request.approved` | Staff API `approve_change_request`, after commit. AWE webhook `request_approved`, after commit |
| `change_request.rejected` | Staff API `reject_change_request`, after commit. AWE webhook `request_rejected`, after commit |
| `intake_form.submission_created` | Staff API `finalize_submission`, after commit |
| `intake_form.submission_approved` | Staff API `approve_submission`, after commit. AWE webhook `request_approved` for `registry.intake_form` |
| `intake_form.submission_rejected` | Staff API `reject_submission`, after commit. AWE webhook `request_rejected` for `registry.intake_form` |
| `register_export.completed` | Celery register-export worker |
| `register_export.failed` | Celery register-export worker |

A webhook that is already applied returns before these notify calls. Direct approve and reject on the staff API are a separate path from the webhook. Both send.

The webhook reject path sets `remarks`. It does not copy a reason into `rejection_reason`. The rejected template's reason clause stays empty for that path unless `rejection_reason` was already stored. The direct `reject_change_request` API does set `rejection_reason`.

### Change-request copy

All three change-request workflows share one payload. They differ in subject, SMS, and whether the reason is shown.

| Event | Email subject | SMS |
| --- | --- | --- |
| Created | We received your change request for `{{payload.record_name}}` | Change request received for `{{payload.record_name}}`. We will message you when it is approved or rejected. |
| Approved | Your change request for `{{payload.record_name}}` was approved | Approved: your change request for `{{payload.record_name}}` is now complete. |
| Rejected | Your change request for `{{payload.record_name}}` was not approved | Not approved: change request for `{{payload.record_name}}`. Reason when `rejection_reason` is set |

The email greets `record_name`, names the register as `register_subject`, then `registry_name`, then `register_mnemonic`, and shows `created_at` or `approved_at`. Rejected email and SMS add `rejection_reason` only when it is set.

### Change-request payload

`change_request_payload` fills every field below. A missing related row leaves the display field empty. The send continues. `registry_name` comes from `resolve_registry_name()` on the singleton registry configuration row.

| Field | Meaning |
| --- | --- |
| `change_request_id` | Change request id |
| `record_name` | Human name of the record. Falls back to "your record" |
| `register_id` | Register definition id |
| `register_mnemonic` | Stable register key |
| `register_subject` | Friendly register title |
| `register_description` | Longer register description |
| `registry_name` | Friendly name of this registry |
| `tab_id` | Tab the change targets |
| `section_id` | Section the change targets |
| `section_mnemonic` | Section key from the section row |
| `section_register_id` | Section-scoped register binding |
| `internal_record_id` | Internal record id of the subject |
| `functional_record_id` | Public record id when one exists |
| `approval_status` | `pending`, `approved`, or `rejected` |
| `no_of_verifications_required` | Verifications required |
| `no_of_verifications_done` | Verifications completed |
| `created_by` | Who created the change |
| `created_at` | Creation time, ISO |
| `approved_by` | Who took the terminal decision |
| `approved_at` | Decision time, ISO |
| `change_request_source` | Origin channel |
| `source_partner_id` | Partner id when the source is a partner |
| `remarks` | Free-text remarks |
| `rejection_reason` | Reason stored on the row. Empty on the webhook reject path unless already set |
| `awe_request_id` | Correlated AWE request id |
| `awe_request_status_summary` | Compact AWE status |
| `deduplication_register_status` | Dedup against the live register |
| `deduplication_register_failure_reason` | Register dedup failure detail |
| `deduplication_change_request_status` | Dedup against other change requests |
| `deduplication_change_request_failure_reason` | Change-request dedup failure detail |

### Intake copy

All three intake workflows share one payload.

| Event | Email subject | SMS |
| --- | --- | --- |
| Created | Application `{{payload.application_reference}}` received | Application `{{payload.application_reference}}` received for `{{payload.record_name}}`. We will message you with the decision. |
| Approved | Application `{{payload.application_reference}}` approved | Approved: application `{{payload.application_reference}}` for `{{payload.record_name}}`. |
| Rejected | Application `{{payload.application_reference}}` was not approved | Not approved: application `{{payload.application_reference}}`. Reason when `rejection_reason` is set |

The email shows the reference, the applicant (`record_name`), the register (`register_subject`, then `registry_name`, then `register_mnemonic`), and the form mnemonic. Created also shows `finalized_at`. Approved and rejected show `approved_at`. Rejected prefers `rejection_reason` and falls back to `remarks`.

### Intake payload

`intake_form_submission_payload` fills every field below.

| Field | Meaning |
| --- | --- |
| `submission_id` | Submission id |
| `application_reference` | Public application reference |
| `record_name` | Applicant name from the sections. Falls back to "your record" |
| `register_id` | Register definition id |
| `register_mnemonic` | Stable register key |
| `register_subject` | Friendly register title |
| `register_description` | Longer register description |
| `registry_name` | Friendly name of this registry |
| `intake_form_mnemonic` | Form key |
| `form_id` | Form definition id |
| `internal_record_id` | Subject record id, when the submission resolves one |
| `functional_record_id` | Public record id when one exists |
| `approval_status` | Approval status |
| `draft_status` | Draft or final |
| `created_by` | Who created the submission |
| `first_created_at` | First create time, ISO |
| `last_updated_at` | Last update time, ISO |
| `finalized_at` | Finalize time, ISO |
| `approved_by` | Who took the terminal decision |
| `approved_at` | Decision time, ISO |
| `remarks` | Free-text remarks |
| `rejection_reason` | Reason stored on the row |
| `submission_source` | Origin channel |
| `partner_id` | Partner id when the source is a partner |
| `awe_request_id` | Correlated AWE request id |
| `awe_request_status_summary` | Compact AWE status |
| `number_of_verifications_required` | Verifications required |
| `number_of_verifications_done` | Verifications completed |
| `register_ingest_process_status` | Ingest status |
| `register_ingest_processed_timestamp` | Last ingest time, ISO |
| `register_ingest_process_attempts` | Ingest attempts |
| `register_ingest_process_last_error_code` | Last ingest error |
| `deduplication_status_vs_intake_forms` | Dedup against other intake forms |
| `deduplication_intake_forms_process_timestamp` | That dedup time, ISO |
| `deduplication_intake_forms_attempts` | That dedup attempts |
| `deduplication_intake_forms_error` | That dedup error |
| `deduplication_status_vs_register` | Dedup against the live register |
| `deduplication_register_process_timestamp` | That dedup time, ISO |
| `deduplication_register_forms_attempts` | That dedup attempts |
| `deduplication_register_error` | That dedup error |

### Export copy

| Event | In-app title | In-app body | Email subject |
| --- | --- | --- | --- |
| Completed | Export ready | Your `{{payload.export_format}}` export of `{{payload.register_mnemonic}}` is ready (`{{payload.total_records_exported}}` records). | Export ready: `{{payload.register_mnemonic}}` (`{{payload.export_format}}`) |
| Failed | Export failed | Your `{{payload.export_format}}` export of `{{payload.register_mnemonic}}` failed, plus `export_latest_error_code` when set | Export failed: `{{payload.register_mnemonic}}` (`{{payload.export_format}}`) |

There is no SMS. The completed email links `file_presigned_url` and shows `file_url_expires_at`, `export_id`, and `register_subject`. The failed email shows `export_latest_error_code` and `export_no_of_attempts`, and links Open register.

`staff_portal_base_url` is `NOTIFICATION_STAFF_PORTAL_BASE_URL` with one trailing slash removed. It is set only on export payloads among the registry events.

### Export payload

`register_export_payload` fills every field below. `selected_record_count` is the length of the selected id list. The id list itself is not sent.

| Field | Meaning |
| --- | --- |
| `export_id` | Export id |
| `register_id` | Register definition id |
| `register_mnemonic` | Stable register key |
| `register_subject` | Friendly register title |
| `export_format` | File format |
| `export_status` | Queue status |
| `selection_mode` | How rows were chosen |
| `selected_record_count` | Number of selected ids |
| `total_records_exported` | Rows written |
| `export_latest_error_code` | Last error code |
| `export_no_of_attempts` | Attempts |
| `export_latest_timestamp` | Last attempt time, ISO |
| `file_object_name` | Object name in storage |
| `file_presigned_url` | Download URL |
| `file_url_expires_at` | When that URL expires, ISO |
| `requested_by` | Staff username. This is also the Novu subscriber id |
| `queued_at` | Queue time, ISO |
| `staff_portal_base_url` | Staff UI origin |
| `batch_size` | Worker batch size |
| `last_processed_offset` | Resume offset |
| `search_text` | Search the export used |
| `sort_by` | Sort the export used |
| `filter_by` | Filter the export used |
| `policy_mnemonics` | Policies applied to the export |

## AWE events

Source: [`awe/src/awe/services/notification.py`](https://github.com/OpenG2P/awe/blob/develop/src/awe/services/notification.py).

AWE notifies staff. It does not notify the registrant. Registry still does that on the webhook, in the table above.

`collect()` runs inside the engine transaction. `flush()` sends after commit. `discard()` drops intents on rollback.

| Event key | Recipient |
| --- | --- |
| `approval.stage_started` | `approvers` on the stage. Observers are not included |
| `approval.task_reassigned` | `to` |
| `approval.stage_escalated` | `added_approvers` |
| `approval.task_expired` | `assignee` |
| `approval.request_approved` | Requester, when that id is not the source service |
| `approval.request_rejected` | Requester, same rule |
| `approval.request_cancelled` | Requester, same rule |
| `approval.stage_quorum_skipped` | `skipped_assignees` |

These engine events do not notify: `request_created`, `stage_skipped`, a plain `stage_completed`, and observers.

### Links

| Field | Value |
| --- | --- |
| `staff_portal_base_url` | `NOTIFICATION_STAFF_PORTAL_BASE_URL`, trailing slash removed |
| `task_path` | Change request: `/tasks/change-request/{artifact_id}`. Intake: `/tasks/intake-form/{mnemonic}/{artifact_id}` |
| `tasks_list_path` | `/tasks/change-request` or `/tasks/intake-form` |

The mnemonic is lowercased. An empty mnemonic or a missing artifact id uses the list path for both links. The host is the registry staff UI, not the AWE admin host.

### AWE copy

In-app and email name the subject as `record_name`, then `application_reference`, then `artifact_type_label`. The register line is `register_subject`, then `register_mnemonic`. The policy line is `policy_name`, then `policy_key`. Actor lines prefer `actor_name`, then `actor`.

| Event | In-app title | Email subject |
| --- | --- | --- |
| Stage started | Approval needed: `{{payload.stage_name}}` | Action required: approve `{{payload.stage_name}}` |
| Task reassigned | Approval task reassigned to you | Approval task reassigned to you: `{{payload.stage_name}}` |
| Stage escalated | Escalated approval needs you | Escalated approval: `{{payload.stage_name}}` needs you |
| Task expired | Your approval task expired | Your approval task expired: `{{payload.stage_name}}` |
| Request approved | Request approved | Approved: subject, using the same fallback as the title |
| Request rejected | Request rejected | Rejected: subject |
| Request cancelled | Request cancelled | Cancelled: subject |
| Quorum skipped | No action needed | No email |

Stage started mentions `due_at` when set, and the requester as `requester_name` then `requester`. Reassigned names `reassigned_from_name` then `reassigned_from`, the actor, and `reason`. Escalated and expired mention `due_at` and `on_breach`. Rejected and cancelled add `reason` when set. Quorum skipped says the task was closed because quorum was already met.

### AWE payload

Every AWE payload includes the request and the link fields. Stage events also include stage and task fields. Each event then adds the extras in the next table.

| Field | Meaning |
| --- | --- |
| `request_id` | AWE request id |
| `artifact_type` | `registry.change_request` or `registry.intake_form` |
| `artifact_type_label` | "Change request" or "Intake form" |
| `artifact_id` | Caller artifact id |
| `change_request_id` | From request context, or `artifact_id` for a change request |
| `submission_id` | From request context, or `artifact_id` for an intake form |
| `application_reference` | From request context. Empty when the caller did not stamp it |
| `register_mnemonic` | From request context |
| `register_subject` | From request context. Empty when the caller did not stamp it |
| `record_name` | From request context |
| `section_mnemonic` | From request context |
| `intake_form_mnemonic` | From request context |
| `staff_portal_base_url` | Staff UI origin |
| `task_path` | Relative task path |
| `tasks_list_path` | Relative list path |
| `policy_key` | Policy key on the request |
| `policy_id` | Policy id |
| `policy_name` | Policy name. Empty when the row is missing |
| `policy_description` | Policy description |
| `policy_version` | Policy version |
| `source_service` | Caller service id |
| `requester` | Staff username of the requester |
| `requester_name` | Display name from the catalog. Today's `flush()` does not set it |
| `request_status` | Request status |
| `current_stage_order` | Current stage order |
| `request_created_at` | Request create time, ISO |
| `completed_at` | Completion time, ISO |

Stage events (`stage_started`, `task_reassigned`, `stage_escalated`, `task_expired`, `stage_quorum_skipped`) also send:

| Field | Meaning |
| --- | --- |
| `stage_id` | Stage id |
| `stage_name` | Stage name. The engine event name wins when it is set |
| `stage_order` | Stage order |
| `stage_mode` | Decision mode |
| `stage_mode_value` | Mode parameter |
| `sla_hours` | SLA hours |
| `on_breach` | What the stage does on SLA breach |
| `on_empty` | What the stage does with no approver |
| `parallel_group` | Parallel group |
| `due_at` | Due time, ISO |
| `task_id` | Task id, when the event carries one |
| `assignee` | Task assignee username |
| `assignee_name` | Task assignee name stored on the task |
| `task_kind` | Task kind |
| `task_status` | Task status |
| `delegated_from` | Delegation source |
| `claimed_at` | Claim time, ISO |

Event-specific fields:

| Event | Extra fields |
| --- | --- |
| Stage started | `approvers` |
| Task reassigned | `reassigned_from`, `reassigned_from_name`, `actor`, `actor_name`, `reason`, `new_task_id` |
| Stage escalated | `actor`, `actor_name`, `added_approvers` |
| Task expired | `assignee` when the task row did not already set it |
| Request approved | `actor`, `actor_name`, `decision_id`, `decision_comment` |
| Request rejected | `actor`, `actor_name`, `reason` (engine reason, else the rejecting decision comment), `decision_id`, `decision_comment` |
| Request cancelled | `actor`, `actor_name`, `reason` |
| Quorum skipped | `skipped_assignees`, `skipped_assignee_names` |

### Fields the catalog lists that the helper does not fill yet

The payload lists above include names a template may read before the helper sets them. Today's `flush()` does not look up Keycloak display names, because `collect()` must not do HTTP and `flush()` only looks up email and name for the **recipient**, not for every actor on the payload.

| Field | Status |
| --- | --- |
| `requester_name`, `actor_name`, `reassigned_from_name`, `skipped_assignee_names` | Not set. Templates fall back to the username fields |
| `decision_id`, `decision_comment` | Not set. Reject uses `reason`, filled from the decision comment when the event has no reason |
| `register_subject`, `application_reference` | Set only when the caller stamped them on `ApprovalRequest.context` |

Missing values are empty strings. The send still goes out.
