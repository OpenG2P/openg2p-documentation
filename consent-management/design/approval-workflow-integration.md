---
description: >-
  How the Consent Manager integrates the shared Approval Workflow Engine (AWE) to
  gate data-share policy changes behind human approval, with approvers acting in
  CM's own UI.
---

# Approval Workflow (AWE) Integration

The Consent Manager (CM) integrates the shared **Approval Workflow Engine (AWE)** to gate
**data-share policy changes** behind configurable, multi-stage human approval. Widening a partner's
policy — granting more scopes, purposes, subject-id types, signing algs, or longer validity /
`data_life` — does not take effect until AWE delivers an approved outcome. CM acts as a **caller
service**: it submits requests, proxies approver task interactions on behalf of its own users, and
reacts to terminal outcomes via a webhook.

{% hint style="info" %}
This integration governs **policy changes only**. Partner identity, keys, and onboarding live in
the Partner Management service (see
[Partner Management Integration](partner-management-integration.md)) — AWE does **not** gate partner
onboarding in CM.
{% endhint %}

{% hint style="warning" %}
**Deployment note:** AWE is installed **once per environment** (part of `commons-services`), not
bundled with each CM. CM points `awe_base_url` at the environment's AWE and registers its own
per-CM callback secret into the shared AWE database out-of-band. Because callbacks are addressed
per request (each caller passes its own callback URL and `callback_secret_id`), one shared AWE
serves the registry, SPAR, CM, and other callers in the same environment.
{% endhint %}

## Two distinct "policies"

The word *policy* means two different things here — do not conflate them:

| Term | What it is | Where it lives |
| --- | --- | --- |
| **CM data-share policy** | The artefact / rules: `allowed_data_scopes`, purposes, subject-id types, signing algs, validity, fetch semantics, `data_life`. Versioned per partner binding. | CM (`PartnerPolicy`) |
| **AWE approval policy** (`policy_key`) | The workflow: stages, approvers, SLA, delegation. | AWE |

A **change to the CM data-share policy** is the *artifact* that is routed through an **AWE approval
policy** (the *workflow*). CM references the approval policy by its `policy_key`.

## End-to-end flow

```mermaid
sequenceDiagram
  participant Admin as CM Admin
  participant CM as Consent Manager
  participant AWE as AWE
  participant Approver as Approver (CM UI)

  Admin->>CM: upsert widening policy
  CM->>CM: new PartnerPolicy version (status=pending); prior active stays in force
  CM->>AWE: POST /v1/awe/requests (service token)
  AWE-->>CM: {request_id}
  Approver->>CM: open approver inbox (own JWT)
  CM->>AWE: GET /v1/awe/tasks?assignee=me (approver JWT proxied)
  AWE-->>CM: tasks
  Approver->>CM: submit decision
  CM->>AWE: POST /v1/awe/tasks/{id}/decision (approver JWT proxied)
  AWE->>CM: terminal webhook (HMAC-signed)
  CM->>CM: request_approved → version active + supersede prior<br/>request_rejected/cancelled → version rejected
```

1. **Widen** — an admin upserts a policy that grants more than the current active version (the first
   policy also counts as widening). CM creates a new `PartnerPolicy` version in status `pending`.
   The **prior active version stays in force** — the hot path is unaffected.
2. **Submit to AWE** — CM (using a **service token**) calls
   `POST {awe_base_url}/v1/awe/requests` with `policy_key=<AWE approval policy>`,
   `artifact_type=consent_manager.policy_change`, `artifact_id=<policy version id>`, a **context
   snapshot** (partner label, controller, and the scope/purpose diff), and a **callback URL**. AWE
   returns a `request_id`, which CM stores on the pending version.
3. **Approver acts in CM's UI** — approvers use CM's own **approver inbox**, never AWE's UI. CM
   **proxies** AWE's task-list and decision calls, forwarding the **approver's own Keycloak JWT** so
   AWE's `sub`-based task ownership works.
4. **Terminal webhook** — when the workflow completes, AWE POSTs a terminal event to CM's callback
   URL:
   * `request_approved` → the pending version becomes **`active`** and **supersedes** the prior
     version.
   * `request_rejected` / `request_cancelled` → the version is marked **`rejected`**; the prior
     active version remains in force.

A pure narrowing change, or an environment with AWE disabled, skips steps 2–4 and activates
immediately.

## Two token types

CM talks to AWE with two different tokens depending on the call:

| Token | Used for |
| --- | --- |
| **Service token** (client-credentials) | `create_request` — submitting the policy change to AWE. |
| **Approver's own JWT** (forwarded unchanged) | All proxied approver calls: list my tasks, submit decision, claim a task, get a request + its events. |

The approver's bearer is extracted at the HTTP layer and passed through untouched so AWE resolves
task ownership by the approver's `sub`.

## Approver proxy &amp; inbox

AWE ships only an `/admin` operator UI — it has **no approver UI**. CM therefore exposes an
**approver inbox** in its own console and proxies the approver-facing AWE calls under
`/consent/v1/awe/…` (plain REST):

| CM proxy route | Proxies to AWE | Token |
| --- | --- | --- |
| `GET /consent/v1/awe/tasks` | `GET /v1/awe/tasks?assignee=me` | approver JWT |
| `POST /consent/v1/awe/tasks/{id}/decision` | submit decision | approver JWT |
| `POST /consent/v1/awe/tasks/{id}/claim` | claim task | approver JWT |
| `GET /consent/v1/awe/requests/{id}` | get request | approver JWT |
| `GET /consent/v1/awe/requests/{id}/events` | get request events | approver JWT |

The proxy routes are gated on the CM approver role (`CONSENT_MANAGER_APPROVER`). The context sent on
`create_request` carries business-meaning fields (partner label, controller, policy version,
scope/purpose diff) so the inbox can render a meaningful task, not just an opaque artifact id.

## Inbound webhook (HMAC)

The terminal callback from AWE is **HMAC-only — no bearer token**. AWE signs the request:

```
X-Approval-Signature: sha256=HMAC_SHA256(secret, "<X-Approval-Timestamp>." + raw_body)
```

CM verifies the signature against the **raw request bytes**, rejects stale timestamps (outside the
allowed skew), and **deduplicates** by event id so a redelivered webhook is idempotent. The
per-caller callback secret is registered into the shared AWE database out-of-band and looked up by
`callback_secret_id`; CM holds the same raw secret to verify. Terminal events:
`request_approved`, `request_rejected`, `request_cancelled`.

## Configuration

AWE integration is off by default (`consent_manager_awe_enabled = false` → policy changes activate
immediately, legacy behaviour). Relevant keys:

| Key | Purpose |
| --- | --- |
| `consent_manager_awe_enabled` | Master switch. When `false`, all policy changes activate immediately. |
| `awe_base_url` | Base URL of the environment's shared AWE. |
| `awe_policy_change_policy_key` | The AWE approval `policy_key` (workflow) used for policy-change requests. |
| `awe_callback_url` | The URL AWE POSTs terminal webhooks to (in-cluster CM API + `/consent/v1/awe/webhooks/decision`). |
| `awe_callback_secret_id` / `awe_callback_hmac_secret` | The `callback_secret_id` AWE looks up, and the raw HMAC secret CM verifies with. |
| `awe_client_id` / `awe_client_secret` (or a static token) | Client-credentials creds for the service token used on `create_request`. |
| `auth_approver_role` | The CM role that gates the approver inbox / proxy routes (`CONSENT_MANAGER_APPROVER`). |

## Related pages

* [Partner policy binding &amp; approval](partner-onboarding-and-policy.md) — the policy model and
  what "widening" means.
* [Architecture](architecture.md) — the PDP/PEP model and where the policy engine sits.
* [Approval Workflow Engine (AWE)](https://docs.openg2p.org/platform/platform-services/approval-workflow-engine)
  — AWE functional specs, API reference, and deployment guide.
