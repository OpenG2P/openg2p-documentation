---
description: >-
  Staff API to onboard partner bindings, set the versioned policy that caps
  everything a partner can be granted, drive AWE approvals, and read the audit log.
---

# Partner &amp; Policy API

Staff endpoints used to onboard and govern partners. See
[Partner onboarding &amp; policy](../design/partner-onboarding-and-policy.md) for the model.

**Audience:** **staff-api**. **Auth:** Keycloak (**staff realm**) bearer token — the
**`CONSENT_MANAGER_ADMIN`** role for partner/policy management, and the
**`CONSENT_MANAGER_APPROVER`** role for AWE approval decisions. **Base path:** `/consent/v1`.

Signing keys are **not** managed here — they live in **Partner Management (PM)**. A CM partner is a
**binding** that references a PM record and layers a CM policy on top.

## Partners (bindings)

### `POST /partners`

Create a partner binding.

`partner_mgmt_id` references the partner's record in **Partner Management** (the source of signing
keys); if omitted it falls back to the `audience`. `name` is an optional display label
(`org_name` no longer exists).

```json
// request
{ "name": "Partner A",
  "partner_mgmt_id": "PM-PARTNER-A",
  "audience": "PARTNER_SYSTEM_A", "controller_id": "REGISTRY_TENANT_1" }
// response 201
{ "id": "8c0b...", "name": "Partner A",
  "partner_mgmt_id": "PM-PARTNER-A",
  "audience": "PARTNER_SYSTEM_A", "controller_id": "REGISTRY_TENANT_1",
  "status": "active", "created_at": "2025-04-01T00:00:00Z" }
```

> The binding's identifier is returned as `id` (used as `{partner_id}` in the policy paths).

### `GET /partners`

List partner bindings. Filters: `controller_id`, `status`. Paginated (see
[conventions](README.md#conventions)).

### `GET /partners/{partner_id}`

Return the partner binding (no secrets).

### `PATCH /partners/{partner_id}`

Update mutable fields (`name`, `partner_mgmt_id`) or `status` (`active` / `suspended`). Suspending a
partner causes all its consent objects to fail with `unknown_partner`.

```json
{ "status": "suspended" }
```

## Policy

The policy is **versioned**. A `PUT` upserts the policy; **widening** it (adding scopes/purposes,
longer validity, etc.) creates a **`pending`** version routed through AWE approval, while a
non-widening change becomes `active` immediately. Prior versions are retained.

### `PUT /partners/{partner_id}/policy`

Durations are **ISO-8601** strings (`P1Y`, `P30D`).

```json
// request
{
  "allowed_data_scopes": ["farmer_profile.basic", "farmer_profile.crops"],
  "allowed_purposes": ["share_farm_profile", "subsidy_eligibility"],
  "allowed_subject_id_types": ["national_id", "farmer_id"],
  "max_validity_duration": "P1Y",
  "fetch_type": "oneshot",
  "max_fetch_frequency": null,
  "data_life": "P30D",
  "allowed_signing_algs": ["EdDSA", "ES256"]
}
// response 200 — widening: a pending version awaiting approval
{ "policy_id": "p-78", "version": 5, "status": "pending",
  "awe_request_id": "req-4412", "effective_from": null }
```

A non-widening change returns `"status": "active"` with an `effective_from` timestamp and no
`awe_request_id`.

### `GET /partners/{partner_id}/policy`

Return the **active** policy version.

### `GET /partners/{partner_id}/policies`

List **all** policy versions for the partner, each with its lifecycle `status`
(`pending` | `active` | `superseded` | `rejected`) and, where applicable, the `awe_request_id`
that drove approval.

```json
// response 200
[
  { "policy_id": "p-78", "version": 5, "status": "pending",
    "awe_request_id": "req-4412", "effective_from": null },
  { "policy_id": "p-77", "version": 4, "status": "active",
    "awe_request_id": "req-4390", "effective_from": "2025-06-26T00:00:00Z" },
  { "policy_id": "p-70", "version": 3, "status": "superseded",
    "awe_request_id": null, "effective_from": "2025-04-01T00:00:00Z" }
]
```

## AWE approvals (approver proxy)

Staff-api proxies the shared **Approval Workflow Engine (AWE)** so approvers can act on pending
policy widenings without a direct AWE login. These require the **`CONSENT_MANAGER_APPROVER`** role.

### `GET /awe/tasks`

List approval tasks assigned to / claimable by the caller.

### `POST /awe/tasks/{task_id}/claim`

Claim a task so it is assigned to the caller. Returns the updated task.

### `POST /awe/tasks/{task_id}/decision`

Record the approver's decision.

```json
// request
{ "action": "approve", "comment": "Scope widening reviewed against DPA" }
// response 200
{ "task_id": "task-991", "action": "approve", "status": "completed" }
```

`action` ∈ `approve | reject`.

### `GET /awe/requests/{request_id}`

Return the approval request (e.g. the one referenced by a policy's `awe_request_id`).

### `GET /awe/requests/{request_id}/events`

Return the request's event/audit trail.

### `POST /awe/webhooks/decision`

AWE calls this back when a request is decided. **HMAC-only** (signed body, **no bearer token**) —
see the AWE integration design. On approval the pending policy version flips to `active`; on
rejection it becomes `rejected`.

## Audit — decisions

### `GET /decisions`

Read the CM decision audit log. Filters: `partner_id`, `decision`; `limit` caps the page size.

```json
// response 200
[
  { "consent_id": "CONSENT-123456", "partner_id": "8c0b...", "decision": "permit",
    "reason_code": "ok", "policy_version": 4, "evaluated_at": "2025-05-01T12:02:12Z" }
]
```

## Errors

Standard HTTP codes with a problem body (see [conventions](README.md#decision--error-model)).
`404` for unknown partner/policy/task/request; `422` for an invalid policy (e.g. unknown scope or
non-ISO-8601 duration).
