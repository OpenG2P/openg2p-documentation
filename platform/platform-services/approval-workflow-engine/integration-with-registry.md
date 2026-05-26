# Integration with Registry

This page describes the design for wiring AWE into the OpenG2P Registry as
the first concrete Caller integration. The Registry's "Change Request"
(CR) machinery is the natural integration seam — every staged mutation
already passes through it; AWE inserts as the multi-stage approval gate
between "CR created" and "CR applied to the live register."

> **Status:** design only — no code has been written in the Registry
> repos yet. Open design choices are flagged at the end.

## Why Change Request is the right seam

Today the Registry already has:

* `G2PRegisterChangeRequest` with `approval_status: PENDING | APPROVED | REJECTED`,
  `approved_by`, `approved_at`.
* `G2PRegisterChangeRequestPayload` with the proposed mutation as JSON.
* A `POST /change-requests/approve_change_request` endpoint that, today,
  flips a CR to `APPROVED` and writes to the live register in one step
  for anyone holding the `changeRequest:approve` permission.
* A `POST /change-requests/reject_change_request` endpoint that closes
  the CR without applying it.

What's missing is a **multi-stage** approval gate. AWE provides exactly
that. The integration replaces the single-step approval with an AWE-
mediated workflow, while leaving the rest of the CR machinery (history
inserts, register upserts, document handling, domain `post_approve`
hooks) untouched.

## End-to-end flow

```
      Caller-staff submits a change                    Approvers act in Registry UI
                │                                                   │
                ▼                                                   ▼
  ┌──────────────────────────┐                       ┌──────────────────────────┐
  │ POST /change-requests/   │                       │ POST /change-requests/   │
  │   create_change_request  │                       │   approve_change_request │
  └──────────┬───────────────┘                       └──────────┬───────────────┘
             │ (existing)                                       │ (rewire)
             ▼                                                  ▼
  ┌────────────────────────────────────────────────────────────────────────────┐
  │ G2PRegisterService                                                          │
  │   create_change_request()  ──new──►  AWE: create approval request          │
  │   approve_change_request() ──new──►  AWE: record decision (forward JWT)    │
  │   reject_change_request()  ──new──►  AWE: record decision (forward JWT)    │
  └────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       │ HTTPS (bearer = the user's JWT)
                                       ▼
                        ┌──────────────────────────────┐
                        │ AWE                          │
                        └──────┬───────────────────────┘
                               │ webhook (HMAC) on terminal state
                               ▼
  ┌──────────────────────────────────────────────────────────────────────────┐
  │ NEW Registry controller: POST /awe/webhooks/decision                     │
  │   request_approved   → G2PRegisterService._approve_change_request_core() │
  │                        (skip_verification=True; AWE already gated it)    │
  │   request_rejected   → G2PRegisterService._reject_change_request_core()  │
  │   request_cancelled  → mark CR cancelled, no register write              │
  └──────────────────────────────────────────────────────────────────────────┘
```

## Mapping AWE concepts to Registry concepts

| AWE concept | Registry concept | Source field |
|--|--|--|
| `policy_key` | "which workflow governs this CR" | derived from `register_mnemonic + section_id`, e.g. `farmer.section-farmer-edit`. Template-driven. |
| `artifact_type` | constant | `"registry.change_request"` |
| `artifact_id` | CR id | `change_request_id` |
| `context` | resolution data the policy needs | small subset: `register`, `section`, `edit_action`, plus any policy-relevant business fields lifted from `change_payload` (district, amount, etc.). The section config picks which fields. |
| `requester` | who submitted the CR | `request.state.auth.sub` |
| `callback_url` | Registry webhook | configured `awe_default_callback_url` |
| `callback_secret_id` | HMAC secret reference | configured `awe_callback_secret_id` |
| approver bearer to AWE | the approver's own JWT | `request.state.auth.credentials` — **forwarded as-is** since both services trust the same Keycloak realm |

## Authentication and the token model

Two **different** tokens flow across the integration, on two different
calls. Getting this right is the crux of the integration — the table
below is the contract.

| Call | `Authorization` header | What it proves | Verified by AWE? |
|--|--|--|--|
| `POST /v1/awe/requests` (open a flow) | Registry's **service-account token** (client_credentials) | The *Registry system* is creating this flow | Yes — JWKS signature + issuer (+ audience, see below) |
| `requester` field in the `POST /requests` body | — (not a token; a plain string, e.g. `u-alice`) | Who *submitted* the CR — provenance only | **No** — stored as-is, never checked against Keycloak |
| `POST /v1/awe/tasks/{id}/decision` (approve / reject) | The **approver's own user JWT**, forwarded by Registry | That *this specific human* is deciding | Yes — JWKS-verified, and `sub` must match the task's assignee |

Key consequences:

* **Create is system-acting-for-a-human.** The human (`requester`) is
  data, not the caller. A string is enough because at create time
  nobody is *acting as* that user — the Registry is recording who
  initiated. AWE uses `requester` for guards like `forbid_self_approval`,
  but never trusts it as an authenticated identity.
* **Decide is the human acting directly.** This is the actual security
  gate — a forged "Alice approved" applies a real mutation. So AWE
  requires a proven identity (a real, signed token whose `sub` matches
  the assignee), not an assertion.
* **No AWE role is needed to approve.** The decision endpoint is gated on
  *being the task's assignee*, not on holding `AWE_VIEWER` / `AWE_ADMIN`.
  Those roles are only for the admin portal (policy CRUD, audit,
  deliveries). An approver's authority comes from having been resolved
  into the stage's approver set.

### This depends on a design choice

The table above reflects the **default model: forward the approver's
JWT.** It is not the only option — see
[Open design choices](#open-design-choices-to-confirm-before-coding),
item 1. The alternative ("trust the Registry's assertion of who
approved") collapses the decision row to a service token plus an
asserted user id. The trade-off:

* **Forward JWT (default):** strongest audit / non-repudiation; a
  compromised Registry cannot forge approvals; AWE stays an independent
  control. Cost: Registry must forward live user tokens, and the
  audience claim must line up (next section).
* **Trust the caller:** simplest; one service token does everything;
  works for approvals arriving over non-Keycloak channels (SMS, IVR,
  batch). Cost: AWE is only as trustworthy as the Registry — the
  independent gate becomes a caller-controlled bookkeeping table.

For OpenG2P, where approvals are a governance control, the default
(forward JWT) is recommended. If a "trusted-caller" mode is ever needed,
the clean shape is: a caller holding a specific role may pass
`acting_as: "<user_id>"` on the decision call, and AWE records the
decision as that user while logging that it was *asserted by* the
Registry (not directly proven).

### The audience claim — current decision and the path to tighten it

AWE verifies the inbound token's `aud` against its configured
`awe.keycloak.audience`. A **forwarded approver token was minted for the
Registry's client** (e.g. `registry-staff-portal`), so its `aud` is the
Registry client — **not** `awe-admin-portal`. If audience verification
were on, AWE would reject every forwarded approver token with `401`, even
though the user is valid and is the correct assignee.

`keycloak-init` already auto-adds an audience mapper to every client it
provisions, but it hardcodes the audience to the client's **own** id. So
Registry tokens carry `aud: registry-staff-portal` and nothing else —
there is no values-level hook today to add a second audience.

> **Decision (v1): we have gone with Option 2 — audience verification is
> disabled.** `awe.keycloak.audience` is set to `""` in AWE's Helm
> values, so AWE accepts any validly-signed token from the trusted
> `staff`-realm issuer. Signature and issuer are still enforced; only the
> audience pin is relaxed. This is a deliberate trade-off: it's the
> one-line change that lets forwarded approver tokens through without
> touching Registry's Keycloak setup. It is acceptable for v1 because
> every client lives in the same trusted realm.

The three options, for reference:

| Option | Where it's configured | Effort | Notes |
|--|--|--|--|
| **1. Add `awe` to Registry's token audience** | **Registry** Helm chart's `keycloak-init` | Higher | The stricter, "correct" fix — *deferred*. See "Tightening later" below. |
| **2. Relax AWE's audience check** *(chosen for v1)* | **AWE** Helm values: `awe.keycloak.audience: ""` | One line | AWE accepts any validly-signed token from the trusted `staff`-realm issuer. Simplest; weaker (any realm token is accepted). |
| **3. Token exchange** | Registry side | Highest | Registry exchanges the user token for an AWE-audienced token before forwarding. Cleanest in theory, most moving parts. |

#### Tightening later (moving to Option 1)

When stronger control is wanted, switch to Option 1. This is **not** an
AWE-side change alone — AWE doesn't own the Registry client. It requires:

1. **AWE side:** set `awe.keycloak.audience` back to the AWE client id
   (e.g. `awe-admin-portal`) in AWE's Helm values, re-enabling the
   audience pin.
2. **Registry side — the keycloak-init enhancement:** the Registry's
   tokens must carry `awe` (or `awe-admin-portal`) in their `aud` claim.
   keycloak-init currently emits only each client's *self-audience*
   mapper (`configure_mappers()` hardcodes `included.client.audience` to
   the client's own id), so it would need to grow one of:
   * support for **custom/extra protocol mappers** declared per-client in
     the keycloak-init values (so an `oidc-audience-mapper` adding `awe`
     can be attached to the Registry client), **or**
   * support for assigning a shared **client scope** that carries the
     audience mapper to the Registry client, **or**
   * a documented **manual/post-install** step that adds the mapper via
     the Keycloak admin API.

Until keycloak-init gains one of those, Option 1 cannot be expressed
declaratively — which is precisely why v1 uses Option 2.

## Code changes in the Registry

### 1. `G2PRegisterChangeRequest` model — one new column

* `awe_request_id: str | None` — the AWE request UUID; null if the CR
  was auto-approved (no AWE flow). Distinguishes AWE-gated CRs from
  legacy direct-approval CRs and lets the webhook handler look up the
  CR by AWE id.

### 2. New helper — `AWEClient`

Thin async httpx wrapper, mirroring the existing `WebsubHelper` style in
`openg2p_registry_core/helpers/websub_helper.py`:

```python
class AWEClient:
    async def create_request(policy_key, artifact_id, context, requester, bearer) -> dict
    async def list_my_open_tasks(awe_request_id, bearer) -> list[dict]
    async def submit_decision(task_id, action, comment, bearer) -> dict
    async def cancel_request(awe_request_id, reason, bearer) -> dict
```

Config-driven base URL (`_config.awe_base_url`). Same error-handling
style as existing httpx code (`raise_for_status`, propagate as a domain
exception).

### 3. `G2PRegisterService` — wire AWE in three places

**`create_change_request()`** — after the existing INSERTs:

* Look up the section's `awe_policy_key` (new section field, optional).
  If null and section has `auto_approval=True`, behave as today.
  Otherwise:
* Build `context` from `awe_context_fields` + base fields.
* Call `AWEClient.create_request(...)` using the requester's JWT.
* Store `awe_request_id` on the CR row.

**`approve_change_request()` / `reject_change_request()`** — when
`cr.awe_request_id` is set:

* Don't write `approval_status` directly.
* Find the approver's open task on this AWE request via
  `AWEClient.list_my_open_tasks`.
* Submit decision via `AWEClient.submit_decision`.
* Return the AWE response shape mapped into the Registry's existing
  response shape. The CR stays `PENDING` in Registry's view; the
  webhook is what flips it.

When `cr.awe_request_id` is null (legacy CR, or section without
`awe_policy_key`), the existing direct-approval path runs unchanged.

### 4. New controller — `G2PAWEWebhookController`

One endpoint:

* `POST /awe/webhooks/decision` — body is AWE's `WebhookEvent` schema;
  validates `X-Approval-Signature` HMAC and dedups on
  `X-Approval-Event-Id` against an `AWEWebhookEventLog` table.
* Dispatches by `event_type`:
  * `request_approved` →
    `G2PRegisterService._approve_change_request_core(cr_id, session, skip_verification=True, skip_sequence_check=False, approved_by=event.payload.actor)`.
    `skip_verification=True` is the key — AWE has already enforced the
    approval gate; the legacy verification counters don't apply.
  * `request_rejected` →
    `G2PRegisterService._reject_change_request_core(cr_id, reason=event.payload.reason, rejected_by=event.payload.actor)`
  * `request_cancelled` → mark CR `CANCELLED` (new enum value), no
    register write.
  * All other events (`stage_started`, `task_expired`, etc.) → log
    only, no state change.
* No permission decorator — auth = signature validation. Mirrors the
  JWT-signature pattern in
  `iam_core/partner_auth/jwt_signature_validator.py`.

### 5. New table — `AWEWebhookEventLog`

* `event_id PK`, `request_id`, `event_type`, `received_at`, `applied`,
  `error`.
* Purpose: dedup repeated webhook deliveries; audit trail. Tiny.

### 6. UI surface (Registry staff portal)

The existing CR list and detail pages keep working. To show "stages
and current approver" inline for AWE-gated CRs, add a small read-only
sidebar that calls
`GET /v1/awe/requests/{awe_request_id}` and
`GET /v1/awe/requests/{awe_request_id}/events` and renders inline.
This preserves the federated model (Caller owns UI; AWE owns state).

The approve/reject buttons stay where they are — they now proxy to AWE
under the hood.

### 7. Config additions to `Settings` (staff-portal `config.py`)

```python
awe_enabled: bool = False
awe_base_url: str | None = None                       # e.g. http://awe:80
awe_default_callback_url: str | None = None           # e.g. https://registry/awe/webhooks/decision
awe_callback_secret_id: str | None = None             # passed to AWE on create_request
awe_callback_hmac_secret: SecretStr | None = None     # local secret to verify inbound
awe_policy_key_template: str = "{register}.{section}"
```

### 8. Permissions

* Approvers acting on AWE-gated CRs need `changeRequest:decide` (new
  permission) — strictly distinct from `changeRequest:approve`, which
  becomes "direct admin override; bypasses AWE."
* The legacy `changeRequest:approve` should be tightened to admin-only
  and used only as break-glass.

### 9. Section-level toggle

Section config (`g2p_register_sections`) needs two small additions:

* `awe_policy_key: str | None` — if set, CRs on this section route
  through AWE; if null, the existing `auto_approval` / direct flow
  applies.
* `awe_context_fields: list[str]` — which keys to lift from
  `change_payload` into the AWE `context`.

This makes adoption gradual: turn AWE on per section, leave the rest
alone.

## What we explicitly do not touch

* `G2PRegisterService._approve_change_request_core()` internals — we
  still want all the section-hierarchy + history-insert + register-
  upsert logic, just called from the webhook handler instead of the
  approve endpoint.
* `G2PChangeRequestWorkerService` auto-approval flows — these keep
  working for CRs that don't go through AWE.
* The CR lifecycle exposed externally — to consumers,
  `approval_status` is still `PENDING → APPROVED | REJECTED`. The AWE
  detour is internal; the public field reflects only the final
  outcome.
* IAM / Keycloak setup — both services already share the same `staff`
  realm; AWE was provisioned with that in mind.
* WebSub publishing — orthogonal. Whatever publishes today on a CR
  approval keeps firing on the webhook-driven approval.

## Open design choices to confirm before coding

1. **Bearer-token forwarding vs. service-to-service token.**
   Forwarding the user JWT is simplest (Registry → AWE both trust
   Keycloak), but couples token lifetime to user session. A service
   token is more decoupled but loses approver identity unless we pass
   it explicitly in the request body. See
   [Authentication and the token model](#authentication-and-the-token-model)
   for the full trade-off (non-repudiation, blast radius, trusted-caller
   mode) and the audience-claim configuration this requires.
   **Recommendation:** forward user tokens for v1.

2. **Where `AWEClient` lives.**
   Adding it to `openg2p-registry-core` makes it reusable across
   staff-portal AND any partner API. Keeping it in staff-portal-api is
   simpler for v1.
   **Recommendation:** staff-portal-api for v1, promote to core later.

3. **Cancel propagation.**
   If a CR is cancelled in Registry, the Registry's cancel endpoint
   should call `AWEClient.cancel_request` when the CR has
   `awe_request_id`. Conversely, if AWE is cancelled by an admin in
   AWE's UI, the Registry reacts via the `request_cancelled` webhook
   handler. **Both directions need to work.**

4. **Failure modes of the `create_request` call.**
   If `POST /change-requests/create_change_request` succeeds at the
   Registry side but the subsequent AWE call fails, what state is the
   CR in? Options:
   * Fail the whole thing — rollback the CR. Cleanest; the Caller's
     existing idempotency handles the retry.
   * Create the CR with `awe_request_id=null` and a new
     `PENDING_AWE_PUSH` status, retry asynchronously. More complex;
     needs a worker.

   **Recommendation:** fail the whole thing for v1.

5. **Section migration.**
   Existing sections won't have `awe_policy_key`. The default behaviour
   stays "no AWE." Operators turn it on per section explicitly. Safe.

## Reference: Registry source-code pointers

(File paths relative to `/Users/puneet/Documents/OpenG2P/repos/openg2p-registry-gen2-docker/`.)

| Aspect | Location |
|--|--|
| CR controller | `openg2p-registry-gen2-apis/openg2p-registry-staff-portal-api/.../controllers/g2p_register_change_request_controller.py` |
| CR service (approval logic) | `openg2p-registry-gen2-core/openg2p-registry-core/.../services/g2p_register_service.py`, `_approve_change_request_core()` |
| CR model | `openg2p-registry-gen2-core/openg2p-registry-core/.../models/g2p_register_change_request.py` |
| Auth middleware | `openg2p-iam-service/iam-core/.../user_auth/middleware.py`, `AuthMiddleware` |
| `AuthPrincipal` schema | `openg2p-iam-service/iam-core/.../schemas/auth_principal.py` |
| Outbound httpx pattern | `openg2p-registry-gen2-core/openg2p-registry-core/.../helpers/websub_helper.py` |
| Inbound signature validation pattern | `openg2p-iam-service/iam-core/.../partner_auth/jwt_signature_validator.py` |
| Staff-portal config | `openg2p-registry-gen2-apis/openg2p-registry-staff-portal-api/.../config.py` |
| Staff-portal main / lifespan | `openg2p-registry-gen2-apis/openg2p-registry-staff-portal-api/.../main.py` |
