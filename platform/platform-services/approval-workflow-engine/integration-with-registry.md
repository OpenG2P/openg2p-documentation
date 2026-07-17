# Integration with Registry

This page describes how AWE is wired into the OpenG2P Registry as the first concrete Caller integration. Registry integrates with AWE through **two artifact types**:

1. **Change requests** (`registry.change_request`) - staged mutations to existing register records.
2. **Intake form submissions** (`registry.intake_form`) - new registrations submitted via configurable intake forms.

Both use the same Caller contract (create request → task decisions → webhook terminal events) and share the same proxy, webhook handler, and policy-configuration machinery.

***

### Why Change Request is the right seam

The Registry already has:

* `G2PRegisterChangeRequest` with `approval_status: PENDING | APPROVED | REJECTED | CANCELLED`, `approved_by`, `approved_at`.
* `G2PRegisterChangeRequestPayload` with the proposed mutation as JSON.
* `POST /change-requests/approve_change_request` - historically flips a CR to `APPROVED` and writes to the live register in one step for anyone holding `changeRequest:approve`.
* `POST /change-requests/reject_change_request` - closes the CR without applying it.

AWE adds the **multi-stage approval gate** between creation and register write. The core CR machinery (history inserts, register upserts, document handling, domain `post_approve` hooks) is unchanged - terminal approval still runs through `_approve_change_request_core()`.

#### Why Intake Form is the second seam

Intake forms capture **new beneficiary registrations** before they exist in the live register:

* `G2PIntakeFormSubmission` with `draft_status: DRAFT | FINAL` and `approval_status: PENDING | APPROVED | REJECTED | CANCELLED`.
* Staff or agents fill sections while the submission is a **draft**; no AWE flow runs yet.
* On **finalize**, the submission moves to `FINAL` + `PENDING` approval and - if a policy is configured - AWE is opened.
* Terminal **`request_approved`** webhook sets `APPROVED` and enqueues **register ingest** (`register_ingest_process_status = PENDING`); a worker writes the record into the live register.
* Reject/cancel webhooks close the submission without ingest.

Intake and change requests share the approval UI components (`IntakeApprovalCard`, `useApprovalTasks`, `useSubmitApprovalDecision`) but differ in **when** AWE is opened (finalize vs create) and **what** happens on approval (ingest vs register upsert).

***

### End-to-end flow (as implemented)

```
  Staff submits CR / finalizes intake          Approver acts in Registry UI
              │                                           │
              ▼                                           ▼
  POST /change-requests/create_change_request    Approval sidebar (CR detail /
  or intake finalize                             IntakeApprovalCard)
              │                                           │
              ▼                                           ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ G2PAweIntegrationService                                                │
  │   start_change_request_workflow()  ──►  POST /v1/awe/requests           │
  │   start_intake_submission_workflow()                                    │
  │   stores awe_request_id + awe_request_status_summary on artifact row    │
  └─────────────────────────────────────────────────────────────────────────┘
              │                                           │
              │                                           ▼
              │                              POST /awe/submit-task-decision (proxy)
              │                                           │
              │                                           ▼
              │                              POST /v1/awe/tasks/{id}/decision
              │                              (approver JWT forwarded)
              ▼                                           │
  ┌──────────────────────────────┐                        │
  │ AWE                          │◄───────────────────────┘
  └──────────────┬───────────────┘
                 │ webhook (HMAC) on terminal / stage events
                 ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │ POST /awe/webhooks/decision  (G2PAWEWebhookController)                  │
  │   request_approved   → CR: approve_change_request_from_awe_webhook()    │
  │                        → _approve_change_request_core(skip_verification)│
  │                        → Intake: approve_submission_with_session()      │
  │                        → enqueue register ingest                        │
  │   request_rejected   → CR/submission REJECTED, no register write        │
  │   request_cancelled  → CR/submission CANCELLED, no register write       │
  │   other events       → log + update awe_request_status_summary          │
  └─────────────────────────────────────────────────────────────────────────┘
```

### Mapping AWE concepts to Registry concepts

| AWE concept            | Registry concept                     | Source                                                                                                                    |
| ---------------------- | ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------- |
| `policy_key`           | Which workflow governs this artifact | `g2p_registry_awe_policy_configurations.policy_key` - resolved by register + section / intake form / register scope       |
| `artifact_type`        | Constant                             | `"registry.change_request"` or `"registry.intake_form"`                                                                   |
| `artifact_id`          | CR or submission id                  | `change_request_id` / `submission_id`                                                                                     |
| `context`              | Data for policy rules                | Base fields (`register_mnemonic`, `section_mnemonic`, etc.) plus keys listed in `context_field_names` lifted from payload |
| `requester`            | Who submitted                        | `request.state.auth.sub`                                                                                                  |
| `callback_url`         | Registry webhook                     | Configured `awe_default_callback_url`                                                                                     |
| `callback_secret_id`   | HMAC secret reference                | Configured `awe_callback_secret_id`                                                                                       |
| Approver bearer to AWE | Approver's own JWT                   | Forwarded via staff-portal proxy (`/awe/submit-task-decision`)                                                            |

#### Policy configuration

| Field                           | Purpose                                               |
| ------------------------------- | ----------------------------------------------------- |
| `policy_scope`                  | `REGISTER`, `INTAKE_FORM`, or `SECTION`               |
| `register_id`                   | Which register                                        |
| `section_id` / `intake_form_id` | Scope-specific id (when applicable)                   |
| `policy_type`                   | `registry.change_request` or `registry.intake_form`   |
| `policy_key`                    | Must match an **active policy** in AWE                |
| `context_field_names`           | JSON list of payload keys to include in AWE `context` |

**Context fields by artifact type**

| Artifact       | Base `context` keys (always sent)                                           | Optional keys from `context_field_names`                   |
| -------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------- |
| Change request | `record_name`, `section_mnemonic`, `register_mnemonic`, `change_request_id` | Any keys from `change_payload` (e.g. `district`, `amount`) |
| Intake form    | `record_name`, `intake_form_mnemonic`, `register_mnemonic`, `submission_id` | Any keys from section `records` in the finalized payload   |

**Example policy keys**

| Scope        | `policy_type`             | Example `policy_key`                 |
| ------------ | ------------------------- | ------------------------------------ |
| REGISTER     | `registry.change_request` | `registry.change_request.individual` |
| INTAKE\_FORM | `registry.intake_form`    | `registry.intake_form.individual`    |

Each `policy_key` must have a matching **active policy** in AWE admin.

***

### Integration with Intake Forms

#### Lifecycle and when AWE opens

```
  Draft editing (no AWE)              Finalize                      Approval
        │                                  │                            │
        ▼                                  ▼                            ▼
  submission.draft_status=DRAFT    finalize_submission()        Approver uses
  (sections editable)              draft_status=FINAL           IntakeApprovalCard
                                   approval_status=PENDING              │
                                   awe_request_id set ◄── AWE create    │
                                                                        ▼
                                                              submit-task-decision
                                                                        │
                                   request_approved webhook ◄───────────┘
                                   → approve_submission_with_session()
                                   → register_ingest_process_status=PENDING
                                   → worker ingests into live register
```

AWE is **not** called when a draft is first created or while it is edited. It is called inside `finalize_submission_with_session()` after the submission is marked `FINAL`.

#### Intake-specific mapping

| AWE field       | Intake source                                                                                                                             |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `artifact_type` | `"registry.intake_form"`                                                                                                                  |
| `artifact_id`   | `submission_id`                                                                                                                           |
| `policy_key`    | From `g2p_registry_awe_policy_configurations` where `policy_scope=INTAKE_FORM` and `intake_form_id` matches, else REGISTER-level fallback |
| `requester`     | Finalizing user's `sub` (or `submission.created_by`)                                                                                      |
| Idempotency key | `intake-{submission_id}`                                                                                                                  |

#### Webhook terminal actions (intake)

| Event                                    | Registry action                                                                                                          |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `request_approved`                       | `G2PIntakeFormDataService.approve_submission_with_session()` - sets `APPROVED`, `register_ingest_process_status=PENDING` |
| `request_rejected`                       | `reject_submission_with_session()` - sets `REJECTED`, no ingest                                                          |
| `request_cancelled`                      | `cancel_submission_with_session()` - sets `CANCELLED`, no ingest                                                         |
| `stage_started`, `stage_completed`, etc. | Log + update `awe_request_status_summary` only                                                                           |

Webhook lookup resolves the submission by `artifact_id` (UUID) or falls back to `awe_request_id`.

#### Staff portal UI (intake)

* **Submission detail:** `IntakeFormSubmissionView` - shows form sections on the left; **`IntakeApprovalCard`** on the right when `draft_status != DRAFT`.
* **Approval card:** uses `useApprovalTasks(awe_request_id)` and `useSubmitApprovalDecision` with `artifact_type: registry.intake_form`.
* **Inbox:** `useMyTasks` supports `artifact_type=registry.intake_form` filter; task stats expose `intake_form_count`.
* **Permissions:** `approvalIntakeForm:view` / `approvalIntakeForm:create` gate the intake approval panel.

Decisions go through the **same AWE proxy** as change requests (`/awe/submit-task-decision`) - not through direct `approve_submission` / `reject_submission` API endpoints.

### Implementation in the Registry

#### 1. Model columns

**`G2PRegisterChangeRequest`** and **`G2PIntakeFormSubmission`**:

* `awe_request_id: str | None` - AWE request UUID; null if no AWE flow.
* `awe_request_status_summary: str | None` - Human-readable stage/status; updated from webhook event log.

#### 2. HTTP client - `AweHelper`

Location: `openg2p_registry_core/helpers/awe_helper.py`

Async httpx wrapper (in **registry-core**, reusable across APIs):

```python
# Key methods
create_request(...)
list_my_tasks(...) / list_tasks_for_request(...)
submit_decision(...)
cancel_request(...)          # requires AWE_ADMIN token
get_request(...) / get_request_events(...)
search_requests(...)
claim_task(...)
```

Config: `awe_base_url`, `awe_http_timeout_seconds` (via `get_awe_settings()`).

#### 3. Orchestration - `G2PAweIntegrationService`

Location: `openg2p_registry_core/services/g2p_awe_integration_service.py`

**On CR create** (`G2PRegisterChangeRequestService.create_change_request`):

1. Resolve policy via `G2PAwePolicyConfigurationService.find_effective_policy_configuration()`.
2. If no policy or `awe_enabled=false`, skip AWE.
3. Build `context` from base fields + `context_field_names`.
4. `POST /v1/awe/requests` with idempotency key `cr-{change_request_id}`.
5. Store `awe_request_id` and status summary on the CR row.
6. On AWE failure: transaction rolls back (fail-the-whole-thing for v1).

**On intake finalize** (`G2PIntakeFormDataService.finalize_submission_with_session`):

1. Mark submission `draft_status=FINAL`, flush.
2. Resolve policy with `policy_type=registry.intake_form` and `intake_form_id=submission.form_id`.
3. Build `context` from section records + `context_field_names`.
4. `POST /v1/awe/requests` with idempotency key `intake-{submission_id}`.
5. Store `awe_request_id` and status summary on the submission row.
6. On AWE failure: transaction rolls back (same fail-the-whole-thing rule as CR).

**Decisions:** handled by **`G2PAweProxyControllerService`** + staff portal UI - **not** by rewiring `approve_change_request()` / `reject_change_request()` or `approve_submission()` / `reject_submission()`.

#### 4. Webhook controller - `G2PAWEWebhookController`

* `POST /awe/webhooks/decision`
* Validates `X-Approval-Signature` HMAC, dedups on `X-Approval-Event-Id`
* No JWT - auth is signature only

**`G2PAweWebhookService` dispatch:**

| Event               | `registry.change_request`                                     | `registry.intake_form`                                       |
| ------------------- | ------------------------------------------------------------- | ------------------------------------------------------------ |
| `request_approved`  | `approve_change_request_from_awe_webhook()` → register upsert | `approve_submission_with_session()` → register ingest queued |
| `request_rejected`  | CR `REJECTED`                                                 | Submission `REJECTED`                                        |
| `request_cancelled` | CR `CANCELLED`                                                | Submission `CANCELLED`                                       |
| Other events        | Log + reconcile `awe_request_status_summary`                  | Same                                                         |

#### 5. Event log - `awe_req_events`

Table: `G2PAweReqEvent` - `event_id` PK, `request_id`, `event_type`, `artifact_type`, `artifact_id`, `status`, `stage_order`, `actor`, `occurred_at`, `received_at`, `applied`, `error`.

Purpose: webhook dedup, audit trail, status summary replay.

#### 6. AWE proxy (staff portal API)

`G2PAweProxyController` - JWT-authenticated proxy so approvers never call AWE directly:

| Registry route                     | AWE endpoint                              |
| ---------------------------------- | ----------------------------------------- |
| `POST /awe/list_my_tasks`          | `GET /v1/awe/tasks?assignee=me`           |
| `POST /awe/list_tasks_for_request` | `GET /v1/awe/tasks` (assignee=`me` + `*`) |
| `POST /awe/submit-task-decision`   | `POST /v1/awe/tasks/{id}/decision`        |
| `POST /awe/my_task_stats`          | `GET /v1/awe/tasks/stats`                 |
| `POST /awe/get_request`            | `GET /v1/awe/requests/{id}`               |
| `POST /awe/get_request_events`     | `GET /v1/awe/requests/{id}/events`        |
| `POST /awe/claim_task`             | `POST /v1/awe/tasks/{id}/claim`           |

Proxy validates artifact is still in-flight in Registry DB before calling AWE (stage guard, terminal status check).

#### 7. UI (staff portal)

**Shared (both artifact types):**

* **Inbox:** `useMyTasks` → `/api/awe/my-tasks` - filter by `registry.change_request` or `registry.intake_form`.
* **Decisions:** `useSubmitApprovalDecision` → `/api/awe/submit-task-decision` (passes `artifact_id`, `artifact_type`, `current_stage`).
* **Policy admin:** Configuration → AWE Policy Configuration.

**Change request:**

* `ChangeRequestDetailsView` - `ApprovalList` sidebar via `useApprovalTasks(awe_request_id)`.

**Intake form:**

* `IntakeFormSubmissionView` - `IntakeApprovalCard` sidebar (visible only when not draft).
* Artifact constant: `registry.intake_form` (`REGISTRY_INTAKE_FORM_ARTIFACT`).

#### 8. Configuration (`Settings`)

```python
awe_enabled: bool = False
awe_base_url: str = "http://localhost:8000"           # host only, no /v1/awe
awe_http_timeout_seconds: float = 30.0
awe_default_callback_url: str | None = None           # e.g. https://registry/awe/webhooks/decision
awe_callback_secret_id: str | None = None
awe_callback_hmac_secret: str | None = None
awe_webhook_timestamp_tolerance_seconds: int = 300
```

Env prefix: `registry_core_*` and/or `registry_staff_portal_api_*` (merged by `get_awe_settings()`).

### Deployment checklist

1. Set all `awe_*` env vars on staff-portal-api.
2. Create and **activate** AWE policies whose `policy_key` matches registry config rows.
3. Seed `g2p_registry_awe_policy_configurations` (per register variant).
4. Register callback secret in AWE; align `awe_callback_secret_id` + `awe_callback_hmac_secret`.
5. AWE Helm: `awe.keycloak.audience: ""` for v1 forwarded tokens.
6. Grant Registry service account `AWE_ADMIN` if outbound cancel is enabled.

***

### Reference: source-code pointers

(Paths relative to `registry-platform/` in the GEN2 OpenG2P monorepo.)

| Aspect                                      | Location                                                                                           |
| ------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| AWE HTTP client                             | `core/openg2p-registry-core/.../helpers/awe_helper.py`                                             |
| Create orchestration                        | `core/openg2p-registry-core/.../services/g2p_awe_integration_service.py`                           |
| Policy resolution                           | `core/openg2p-registry-core/.../services/g2p_awe_policy_configuration_service.py`                  |
| CR service + webhook approve                | `core/openg2p-registry-core/.../services/g2p_register_change_request_service.py`                   |
| Intake service + finalize + webhook approve | `core/openg2p-registry-core/.../services/intake_form_data_service.py`                              |
| Webhook service                             | `core/openg2p-registry-core/.../services/g2p_awe_webhook_service.py`                               |
| Intake submission model                     | `core/openg2p-registry-core/.../models/g2p_intake_form.py`                                         |
| Event log model                             | `core/openg2p-registry-core/.../models/g2p_awe_req_event.py`                                       |
| CR model                                    | `core/openg2p-registry-core/.../models/g2p_register_change_request.py`                             |
| Policy config model                         | `core/openg2p-registry-core/.../models/g2p_registry_awe_policy_configuration.py`                   |
| Webhook controller                          | `apis/openg2p-registry-staff-portal-api/.../controllers/g2p_awe_webhook_controller.py`             |
| AWE proxy controller                        | `apis/openg2p-registry-staff-portal-api/.../controllers/g2p_awe_proxy_controller.py`               |
| CR controller                               | `apis/openg2p-registry-staff-portal-api/.../controllers/g2p_register_change_request_controller.py` |
| Staff portal approval UI (shared)           | `ui/staff-portal-ui/src/features/approval/`                                                        |
| Intake submission + approval UI             | `ui/staff-portal-ui/src/features/intake-form/components/IntakeFormSubmissionView.tsx`              |
| Intake approval card                        | `ui/staff-portal-ui/src/features/approval/components/IntakeApprovalCard.tsx`                       |
| AWE policy config UI                        | `ui/staff-portal-ui/src/app/[locale]/configuration/awe-policy-config/`                             |
| NSR intake policy seed example              | `national-social-registry/nsr-extension/.../g2p_registry_awe_policy_configurations.sql`            |
| AWE service                                 | `awe/src/awe/` (separate repo path in monorepo: `awe/`)                                            |
| AWE audience config                         | `awe/helm/openg2p-awe/values.yaml`                                                                 |

***

### Related pages

* [API Reference](https://docs.openg2p.org/platform/platform-services/approval-workflow-engine/api-reference) - full AWE HTTP contract; Caller surface is five endpoints + one inbound webhook.
