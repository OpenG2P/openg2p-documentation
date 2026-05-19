# AWE Integration

## Overview

The OpenG2P Registry integrates with the [Approval Workflow Engine (AWE)](https://docs.openg2p.org/platform/platform-services/approval-workflow-engine) to gate change requests behind configurable, multi-stage human approval. Before this integration, the registry managed approvals internally through a simple `approval_status` column and a fixed verifier model. The AWE integration replaces and extends that model: AWE becomes the authority on whether a change request may be applied, and the registry acts as a caller service — submitting requests, proxying approver task interactions, and reacting to final outcomes via webhook.

AWE handles all approval-routing logic — stage modes, approver resolution, SLA enforcement, and delegation. The registry retains full ownership of its data and business logic; AWE is an external gate, not an internal workflow engine.

## Key design principles

| Principle                                 | Description                                                                                                                                                                                                                                   |
| ----------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Registry owns the data                    | AWE never reads or writes registry records. It only knows `artifact_type`, `artifact_id`, and a context snapshot. All register mutations happen inside the registry on webhook receipt.                                                       |
| AWE is the approval authority             | Once a change request is submitted to AWE, its `approval_status` in the registry follows AWE's terminal outcome (`approved` / `rejected` / `cancelled`). Manual approval via the old registry path is disabled for AWE-gated change requests. |
| Policy binding is configuration, not code | Admins map AWE policy keys to registers, intake forms, or sections through the `g2p_registry_awe_policy_configurations` table. No code changes are needed to change which policy governs a given artifact type.                               |
| Approvers interact via the registry UI    | The staff portal proxies task listing and decision calls to AWE on behalf of logged-in approvers. Approvers never call AWE directly.                                                                                                          |
| Webhook drives final state                | The registry's `approval_status` column is updated only when AWE delivers a terminal-state webhook (`request_approved`, `request_rejected`, `request_cancelled`). This keeps the local record consistent without polling.                     |

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  Staff Portal UI (openg2p-registry-gen2-staff-portal-ui)         │
│                                                                  │
│  My Tasks.       ──── GET /registry/awe/tasks ──────────────────┐│
│  Task Detail     ──── POST /registry/awe/tasks/{id}/decision ───┘│
└────────────────────────────────┬─────────────────────────────────┘
                                 │ proxied with approver's JWT
                                 ▼
┌──────────────────────────────────────────────────────────────────┐
│  Registry Staff Portal API (openg2p-registry-staff-portal-api)   │
│                                                                  │
│  G2PAWEWebhookController  POST /awe/webhooks/decision  ─────────┐│
│  (task proxy controllers) GET/POST /awe/tasks/*        ─────────┘│
└────────────────────────────────┬─────────────────────────────────┘
                                 │                      ▲
               service token     │                      │ HMAC-signed webhook
                                 ▼                      │
┌──────────────────────────────────────────────────────────────────┐
│  AWE  (openg2p-awe)                                              │
│                                                                  │
│  Policy: registry.change_request.*                               │
│  Resolves approvers, manages tasks, enforces SLA                 │
│  Fires webhook on terminal state                                 │
└──────────────────────────────────────────────────────────────────┘
```

## Data model changes

### `g2p_register_change_requests` (extended)

Two columns are added to the existing change request table to track the correlation with AWE:

| Column                       | Type                         | Description                                                                                              |
| ---------------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------- |
| `awe_request_id`             | `String` (nullable, indexed) | The `request_id` returned by AWE when the change request is submitted. `NULL` until AWE responds.        |
| `awe_request_status_summary` | `Text` (nullable)            | Free-text summary of the last AWE status update, written by the webhook handler for operator visibility. |

The existing `approval_status` column (`PENDING` / `APPROVED` / `REJECTED`) is retained and remains the source of truth for the registry. AWE's terminal webhook sets it.

### `g2p_registry_awe_policy_configurations` (new)

Stores the admin-configured bindings between registry artefacts and AWE policies.

| Column                 | Type                         | Description                                                                        |
| ---------------------- | ---------------------------- | ---------------------------------------------------------------------------------- |
| `awe_policy_config_id` | `String` (PK, UUID)          | Primary key                                                                        |
| `policy_scope`         | `AwePolicyScopeEnum`         | Granularity of the binding: `REGISTER`, `INTAKE_FORM`, or `SECTION`                |
| `register_id`          | `String` (indexed)           | Target register                                                                    |
| `intake_form_id`       | `String` (nullable, indexed) | Set only when `policy_scope = INTAKE_FORM`                                         |
| `section_id`           | `String` (nullable, indexed) | Set only when `policy_scope = SECTION`                                             |
| `policy_type`          | `String`                     | Caller-defined type label (e.g. `"change_request"`)                                |
| `policy_key`           | `String` (indexed)           | AWE policy key passed to `POST /v1/awe/requests`                                   |
| `context_field_names`  | `JSON` (nullable)            | List of field names from the change payload to include in the AWE context snapshot |

#### Policy scope resolution

When a change request is created, the registry resolves the most specific binding that applies:

1. `SECTION` — binding for the exact `section_id` of the change request
2. `INTAKE_FORM` — binding for the `intake_form_id` associated with the change request
3. `REGISTER` — fallback binding for the whole register

If no binding is found, the change request proceeds through the existing local approval flow (no AWE submission).

## Change request lifecycle with AWE

```
Staff portal creates change request
           │
           ▼
  g2p_register_change_requests
  approval_status = PENDING
  awe_request_id  = NULL
           │
           │  AweHelper.create_request()
           │  POST /v1/awe/requests
           ▼
        AWE creates approval flow
        (resolves stage 1 approvers → creates tasks)
           │
           │  AWE returns request_id
           ▼
  awe_request_id = "<awe-uuid>"        ← stored on change request
           │
           │
           │  Approver opens inbox in staff portal
           │  GET /registry/awe/tasks
           │  (proxied as GET /v1/awe/tasks?assignee=me)
           │
           │  Approver clicks Approve / Reject
           │  POST /registry/awe/tasks/{id}/decision
           │  (proxied as POST /v1/awe/tasks/{id}/decision)
           │
           │  ... multi-stage flow runs inside AWE ...
           │
           │  AWE reaches terminal state
           │  POST /awe/webhooks/decision  (HMAC-signed)
           ▼
  G2PAWEWebhookController.receive_decision()
           │
           ├── request_approved  → approval_status = APPROVED
           │                       approve_change_request() called
           │                       register record updated
           │
           ├── request_rejected  → approval_status = REJECTED
           │
           └── request_cancelled → approval_status = REJECTED
                                   (or domain-specific handling)
```

## Components

### `AweHelper` (`openg2p_registry_core.helpers.awe_helper`)

An async HTTP client singleton wrapping every AWE runtime endpoint the registry needs. Callers obtain it via `AweHelper.get_component()`.

| Method                                         | AWE endpoint                        | Purpose                                                                                                                                            |
| ---------------------------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `create_request(...)`                          | `POST /v1/awe/requests`             | Submit a new change request to AWE. Returns `request_id`.                                                                                          |
| `list_my_open_tasks(token, ...)`               | `GET /v1/awe/tasks?assignee=me`     | Approver inbox — tasks assigned to the current user. Supports `artifact_type`, `policy_key`, `page`, `page_size` filters. Returns `PagedTasksOut`. |
| `list_all_open_tasks(token, ...)`              | `GET /v1/awe/tasks?assignee=*`      | Admin view — all open tasks. Requires `AWE_ADMIN` token.                                                                                           |
| `submit_decision(token, task_id, action, ...)` | `POST /v1/awe/tasks/{id}/decision`  | Record `approve` / `reject` / `abstain` on behalf of an approver.                                                                                  |
| `claim_task(token, task_id)`                   | `POST /v1/awe/tasks/{id}/claim`     | Optional intent-to-act marker.                                                                                                                     |
| `cancel_request(token, request_id, ...)`       | `POST /v1/awe/requests/{id}/cancel` | Cancel an in-flight approval when the change request is withdrawn.                                                                                 |
| `get_request(token, request_id)`               | `GET /v1/awe/requests/{id}`         | Fetch full approval state for a single request.                                                                                                    |
| `get_request_events(token, request_id)`        | `GET /v1/awe/requests/{id}/events`  | Fetch the audit event timeline for display in the artifact detail page.                                                                            |
| `search_requests(token, ...)`                  | `GET /v1/awe/requests`              | Search requests by `artifact_type`, `artifact_id`, or `status`.                                                                                    |

All methods forward the bearer token as-is. Service-to-AWE calls use a client-credentials token; approver calls use the approver's own JWT so AWE's `sub`-based task assignment and decision authoring works correctly.

Error responses from AWE are surfaced as `AWEClientError(status_code, error_code, message)`.

### `G2PAwePolicyConfigurationService` (`openg2p_registry_core.services`)

CRUD service for `g2p_registry_awe_policy_configurations`. Used by admin APIs in the staff portal to manage policy bindings at runtime without code changes.

Key validation rules enforced by the service:

* `REGISTER` scope: `intake_form_id` and `section_id` must be absent.
* `INTAKE_FORM` scope: `intake_form_id` required; `section_id` must be absent.
* `SECTION` scope: `section_id` required.
* `register_id` must reference an existing register definition.

### `G2PAWEWebhookController` (`openg2p_registry_staff_portal_api.controllers`)

Receives inbound AWE webhooks at `POST /awe/webhooks/decision`. No JWT is required on this endpoint — authentication is entirely via HMAC signature verification (`X-Approval-Signature`, `X-Approval-Timestamp`, `X-Approval-Event-Id`).

The controller delegates to `G2PAweWebhookService` for:

1. Signature verification via `AweWebhookSignatureHelper`.
2. Deduplication on `X-Approval-Event-Id` — the same event may be delivered more than once if AWE does not receive a 2xx in time.
3. Dispatching to the appropriate registry action based on `event_type`:
   * `request_approved` → calls `approve_change_request()`, which writes the change to the register table.
   * `request_rejected` → flips `approval_status = REJECTED`.
   * `request_cancelled` → flips `approval_status = REJECTED` (or domain-specific handling).

The controller returns `200` for successfully processed events and `422` / `500` for processing failures. AWE retries non-2xx responses on its backoff schedule (1m → 5m → 15m → 1h → 6h).

## Context snapshot

When Registry submits a change request to AWE, it builds an AWE `context` dict from the change payload. The fields included are controlled by the `context_field_names` list on the matching `g2p_registry_awe_policy_configurations` row.

Example for a farmer register change request:

```json
{
  "policy_key": "registry.change_request.farmer.v1",
  "artifact_type": "registry.change_request",
  "artifact_id": "cr-<change_request_id>",
  "context": {
    "district": "D1",
    "amount": 15000,
    "register_id": "farmer-register-uuid"
  }
}
```

AWE policy rules (`expression`, `http`) read fields from this context to resolve approvers dynamically. For policies using only `user`, `role`, or `group` rules, `context` can be an empty object — no `context_field_names` configuration is needed.

## Staff portal proxy endpoints

The staff portal exposes pass-through endpoints that forward approver interactions to AWE. The approver's own Keycloak JWT is forwarded unchanged so AWE's `sub`-based task ownership is preserved.

| Staff portal endpoint                    | Proxied to AWE                     | Notes                                                                                                                                                                                                                                                                                                    |
| ---------------------------------------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /registry/awe/tasks`                | `GET /v1/awe/tasks`                | Approver inbox. Supports `artifact_type`, `policy_key`, `page`, `page_size`. Returns `PagedTasksOut` envelope with `items`, `total`, `page`, `page_size`, `pages`. Each task item carries `context`, `artifact_type`, and `policy_key` so the UI can enrich the inbox without a separate request lookup. |
| `POST /registry/awe/tasks/{id}/claim`    | `POST /v1/awe/tasks/{id}/claim`    | Optional — marks intent to act.                                                                                                                                                                                                                                                                          |
| `POST /registry/awe/tasks/{id}/decision` | `POST /v1/awe/tasks/{id}/decision` | Records `approve` / `reject` / `abstain`.                                                                                                                                                                                                                                                                |
| `GET /registry/awe/requests/{id}/events` | `GET /v1/awe/requests/{id}/events` | Approval event timeline for the artifact detail page.                                                                                                                                                                                                                                                    |

## Configuration

| Config key (env prefix `registry_core_`) | Default                 | Description                                                   |
| ---------------------------------------- | ----------------------- | ------------------------------------------------------------- |
| `awe_base_url`                           | `http://localhost:8000` | Base URL of the AWE service reachable from the registry pods. |
| `awe_http_timeout_seconds`               | `30.0`                  | Per-request HTTP timeout for outbound AWE calls.              |

## Error handling

| Scenario                                                              | Behaviour                                                                                                                                                     |
| --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AWE is unreachable when submitting a change request                   | `AWEClientError` is raised. The change request remains `PENDING` with `awe_request_id = NULL`. The caller receives a `503`-equivalent response and can retry. |
| AWE returns a non-2xx on submit                                       | Same — `AWEClientError` surfaced to the caller. No partial state is written.                                                                                  |
| Webhook arrives with invalid HMAC                                     | `401 Unauthorized` returned. AWE retries.                                                                                                                     |
| Webhook body references an unknown `request_id` / `change_request_id` | `422` returned. AWE retries up to its backoff limit.                                                                                                          |
| `approve_change_request()` fails inside the webhook handler           | `422` returned. AWE retries. The change request remains `PENDING`. Operators can inspect the AWE admin UI and the registry audit log to diagnose.             |
| Duplicate webhook delivery (same `event_id`)                          | Deduped by the webhook service. Returns `200` without reprocessing.                                                                                           |

## Sequence diagram — happy path (two-stage approval)

```
Staff portal    Registry API         AWE              Approver A       Approver B
     │               │                │                    │                │
     │ Submit CR     │                │                    │                │
     ├──────────────►│                │                    │                │
     │               │ create_request │                    │                │
     │               ├───────────────►│                    │                │
     │               │ {request_id}   │ resolve stage 1    │                │
     │               │◄───────────────│ → tasks for A, B   │                │
     │               │                │                    │                │
     │               │ store awe_request_id on CR          │                │
     │ 201 CR created │               │                    │                │
     │◄──────────────┤                │                    │                │
     │               │                │                    │                │
     │               │                │  Approver A opens inbox             │
     │               │◄───────────────────-────────────────┤                │
     │               │ list_my_open_tasks (JWT=A)          │                │
     │               ├───────────────►│                    │                │
     │               │ PagedTasksOut  │                    │                │
     │               │◄───────────────│                    │                │
     │               ├───────────────────────-────────────►│                │
     │               │                │                    │                │
     │               │                │  Approver A approves                │
     │               │◄───────────────────────────-────────┤                │
     │               │ submit_decision (JWT=A, approve)    │                │
     │               ├───────────────►│                    │                │
     │               │                │ stage 1 → approved │                │
     │               │                │ resolve stage 2    │                │
     │               │                │ → task for B       │                │
     │               │◄───────────────│                    │                │
     │               │                │                    │    Approver B opens inbox
     │               │◄───────────────────────────────-───────────────────┤  │
     │               │ list_my_open_tasks (JWT=B)          │              │  │
     │               ├───────────────►│                    │              │  │
     │               │ PagedTasksOut  │                    │              │  │
     │               │◄───────────────│                    │              │  │
     │               ├───────────────────────────────────-───────────────►│  │
     │               │                │                    │              │  │
     │               │                │  Approver B approves              │  │
     │               │◄───────────────────────────────-───────────────────┤  │
     │               │ submit_decision (JWT=B, approve)    │                 │
     │               ├───────────────►│                    │                 │
     │               │                │ request → approved │                 │
     │               │                │ POST /awe/webhooks/decision          │
     │               │◄───────────────│ {event_type: request_approved}       │
     │               │                │                    │                 │
     │               │ approve_change_request()            │                 │
     │               │ approval_status = APPROVED          │                 │
     │               │ register record written             │                 │
     │               ├───────────────►│ 200 OK             │                 │
```

## Related pages

* [Change Management](https://docs.openg2p.org/products/registry/registry/design/change-management.md) — the existing change request model that AWE gates.
* [Approval Workflow Engine](https://docs.openg2p.org/platform/platform-services/approval-workflow-engine) — AWE functional specifications, API reference, and deployment guide.
* [Change Management & Approval Workflow](https://docs.openg2p.org/products/registry/registry/features/change-management-and-approval-workflow.md) — feature-level description of how approvers interact with change requests in the staff portal.
