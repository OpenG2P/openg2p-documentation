---
description: >-
  Policy model, stage modes, approver rule types, context semantics, skip
  rules, request lifecycle state machine, webhook contract, and FAQ.
---

# Functional Specifications

## Policy model

A **policy** is the blueprint for approving a given artifact type. It is
versioned: editing a policy creates a new draft; activating a new version
archives the previously active one; in-flight requests stay pinned to the
version they started with.

```
policy  (policy_key, version, artifact_type, status,
         forbid_self_approval, forbid_repeat_approvers)
  ├── stage 1  (stage_order, mode, sla_hours, skip_if, on_empty,
  │             parallel_group, on_breach, escalation_rules)
  │     ├── rule A  (rule_type, rule_value, kind, required)
  │     ├── rule B  …
  │     └── rule C  …
  ├── stage 2  …
  └── …
```

* `policy_key` is the logical identifier — e.g. `registry.change_request`.
* `version` increments with every edit. At most one version has
  `status=active` per `policy_key` at any time.
* `artifact_type` is caller-defined (opaque to AWE).
* Stages run **sequentially by default**, but two or more stages sharing the
  same `parallel_group` activate together; the next group only starts after
  every stage in the current group is approved. See
  [Parallel stages](#parallel-stages).
* `forbid_self_approval` and `forbid_repeat_approvers` are
  segregation-of-duties toggles — see
  [Segregation of duties](#segregation-of-duties).

### Status lifecycle

```
     (create)                (activate)                  (activate v+1)
  ─────────────►  draft  ───────────────►  active  ──────────────────►  archived
                   │
                   │ (edit in place — drafts only)
                   └───────────►  draft
```

Editing an active or archived version is rejected (`409 AWE-007`). To
change an active policy, add a new draft version (PUT
`/policies/{key}`), tweak as needed, then activate it.

## Stage modes

Each stage specifies *how many approvers* are required before the stage
completes:

| Mode           | `mode_value`     | Approval rule                                                                                       |
| -------------- | ---------------- | --------------------------------------------------------------------------------------------------- |
| `all`          | —                | Every resolved approver must approve. Any reject → stage rejected.                                  |
| `any-n`        | N (integer ≥ 1)  | First N approvals complete the stage. If approves + remaining open < N → stage rejected.            |
| `quorum`       | N                | Alias for `any-n`.                                                                                  |
| `percentage`   | P (1–100)        | `ceil(P/100 × approvers)` approvals required. Same rejection math as `any-n`.                       |

When a stage completes, remaining open tasks for that stage flip to
`skipped` and the next stage is resolved.

## Approver rule types

Each stage has ≥1 approver rule. Rules within a stage **union** — a user
is an eligible approver for the stage if any rule resolves them.

| Rule type    | `rule_value` shape                                                  | Approvers resolved from                                                       |
| ------------ | ------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| `user`       | `{"user_id": "u-alice"}`                                            | Literal — always that one user.                                               |
| `role`       | `{"role": "PROGRAM_MANAGER"[, "client": "registry-staff-portal"]}`  | Members of that Keycloak role. `client` optional: omit for a realm role, set to a `clientId` to resolve a client role. |
| `group`      | `{"group": "/districts/A"}`                                         | Members of that Keycloak group path.                                          |
| `expression` | `{"logic": <JSONLogic>}`                                            | JSONLogic evaluated against the request's context snapshot.                   |
| `http`       | `{"url": "https://caller/resolve"}`                                 | Caller POSTed at that URL — returns `{"user_ids":[...]}`.                     |

Each rule additionally carries:

* **`kind`** — `approver` (default) or `observer`. Observer-resolved users
  receive a task and can comment, but do not gate stage completion. See
  [Observers](#observers).
* **`required`** — boolean. When `true`, the resolved user(s) must approve
  before the stage can complete, even if the quorum mode would otherwise
  allow it. Ignored for observer rules. See [Required approvers](#required-approvers).

### When does a rule read the context?

Only `expression` and `http` rules consult `request.context`. The other
three are static at the time the stage is resolved. This matters when
designing a policy: if your approver set varies per request, you must
use `expression` or `http` (or design your Keycloak groups around the
variance).

### HTTP resolver contract

AWE sends:

```http
POST <caller-configured URL>
Content-Type: application/json

{"context": { ...the request's context snapshot... }}
```

Caller must respond:

```json
{"user_ids": ["u-alice", "u-bob"]}
```

Timeout: `awe.resolver.http_timeout_seconds` (default 5s). Failure
bubbles up as a stage-resolution error — the stage does not start;
operator must cancel or wait for the caller to recover.

## Context semantics

`context` is an arbitrary JSON object supplied by the caller at
`POST /v1/awe/requests`. AWE:

* **Stores it frozen** on the `approval_request` row at creation. It never
  changes over the lifetime of the request.
* **Passes it to `expression` and `http` rules** during stage resolution.
  Stage 2+ re-resolution sees the same snapshot — resolution is therefore
  deterministic and replayable.
* **Never parses or validates it.** There is no "context schema" in AWE.
  Field names are whatever your expressions or caller-side resolver
  agree on.

Example: if your Registry caller sends
`{"district": "D1", "amount": 15_000}`, that payload is stored as-is and
is only meaningful because your `expression` or `http` rule reads
`context.district` / `context.amount`.

### Who decides what context to send?

There is an **implicit contract between the policy author and the
Caller service** — AWE does not mediate it. Whether the Caller needs to
know anything about the policy depends on which rule types the policy
uses:

| Active policy uses…                                  | Caller awareness required?                                    |
| ---------------------------------------------------- | ------------------------------------------------------------- |
| Only `user`, `role`, `group`                         | None — `context: {}` is fine.                                  |
| Any `expression` (JSONLogic) rule                    | Yes — Caller must include the keys the JSONLogic reads.       |
| Any `http` rule                                      | Yes — Caller's resolver endpoint defines what it expects.     |
| `skip_if` JSONLogic on any stage                     | Yes — same as `expression`.                                    |

**Three patterns for managing this contract** (pick one per module):

1. **Fixed artifact-summary blob.** Caller always sends a known shape
   per `artifact_type` (e.g. for `registry.change_request`, always
   `{district, amount, beneficiary_id, requester_role}`). Policy authors
   may reference any of these keys; new rules using existing keys require
   no Caller change. Slight over-fetching, maximum resilience.
2. **Per-`policy_key` context spec.** Policy author publishes a small
   spec next to the policy ("`registry.cr.v1` expects:
   `district: str`, `amount: number`"). Caller code references it.
   Tighter coupling, smaller payloads.
3. **Simulate-driven discovery.** During development, ops runs
   `POST /policies/{key}/versions/{v}/simulate` with sample contexts to
   observe what fields the resolver actually consumes. Useful for
   verification, not as the production contract.

Because `context` is snapshotted on the request at creation time, the
contract only matters when a **new policy version is activated** that
references additional keys. In-flight requests continue resolving
against the snapshot they were created with — no retro-active reshaping.

## Skip rules

Two independent mechanisms skip a stage:

### `skip_if` (JSONLogic)

Evaluated when the stage becomes current. If truthy, the stage is marked
skipped (emits `stage_skipped`) and the engine advances to the next
stage without creating any tasks.

Example — "skip director sign-off if amount < 1000":

```json
{
  "skip_if": { "<": [ { "var": "amount" }, 1000 ] }
}
```

### `on_empty`

Applies when the stage's rules resolve to **zero approvers**:

* `on_empty: "skip"` — emit `stage_skipped` and advance.
* `on_empty: "block"` — flip the whole request to `rejected` with
  reason `no_approvers_resolved`. This is the default, so accidental
  mis-configuration can't accidentally auto-approve.

## Parallel stages

Two or more stages sharing the same `parallel_group` value activate
together when their group becomes current. The group is "complete" only
when **every stage in it is approved**. Any single stage rejecting
terminates the request.

```
group=1: [Stage 1: Legal]      ┐
         [Stage 2: Finance]    ┘  → group complete when both approved
group=2: [Stage 3: Director]      → activates next
```

A stage with `parallel_group = null` is its own group of one — i.e. the
default strictly-sequential behaviour. The engine ignores the literal
`stage_order` for ordering between groups; what matters is the order of
groups themselves (groups are evaluated by the smallest `stage_order`
within them).

## Required approvers

A rule with `required: true` adds a hard "must approve" gate on top of the
stage's quorum mode. The stage completes when **both** conditions hold:

1. The quorum mode (`all` / `any-n` / `quorum` / `percentage`) is satisfied.
2. Every user resolved by every `required` rule has approved.

If a required user has no remaining open task (e.g. it was reassigned to
someone else, then expired), the stage rejects.

Common pattern: `mode = any-n`, `mode_value = 2`, three rules where one is
marked `required` → "any 2 of 3 approve, but the third is mandatory."

## Observers

A rule with `kind: "observer"` resolves to users who get a task on the
stage but do **not** count toward stage completion. Observers can read the
request and post comments. Use this for stakeholders who need visibility
without veto power (Legal review, Audit, etc.).

Observer tasks are excluded from quorum / required-approver math, are not
filtered by segregation-of-duties rules, and are not affected by SLA
breaches (no `due_at` is set on observer tasks).

## Segregation of duties

Two policy-level toggles filter resolved approver lists at task-creation
time:

* `forbid_self_approval` — the request's `requester` is removed from every
  stage's approver list.
* `forbid_repeat_approvers` — anyone who has approved an earlier stage of
  the same request is removed from later stages' approver lists.

Filters apply only to `approver` rules; observers are never filtered. If
a stage loses every eligible approver because of a filter, its `on_empty`
setting decides whether to skip or block.

## Delegation (out-of-office)

A `user_delegation` row says: "for the window `[starts_at, ends_at)`,
redirect any new task that would go to `user_id` over to `delegate_to`."

When AWE creates tasks, it consults active delegations. If a resolved
approver has one, the task is created for the delegate instead, with
`delegated_from = original_user` recorded for audit. If multiple
delegations overlap for the same user, the most recently created one
wins.

Delegations apply to **new** tasks only — they never retroactively
reassign already-open tasks. For one-off retroactive moves, use the admin
**Reassign** action on the task.

## Reassignment

`POST /v1/awe/tasks/{id}/reassign` (admin-only) closes an open task with
status `reassigned` and creates a fresh task for the new user, preserving
the original `due_at`. The new task records `reassigned_from = old_user`.
The closed task's audit trail (claim history, etc.) is preserved.

Decisions are never moved across reassignments. Decision integrity is
per-task: if the original assignee never decided, the reassignment closes
the task without a decision.

## Request lifecycle (state machine)

```
     POST /requests                          last stage approved
    ─────────────────►  pending  ──────────►  in_review  ────────►  approved
                          │                      │
                          │                      │ any stage rejects
                          │                      └────────────────►  rejected
                          │
                          │ POST /requests/{id}/cancel
                          └────────────────────────────────────────►  cancelled
                                                                      (or expired
                                                                       via SLA)
```

Transitions emit events that drive webhooks (see below). Terminal states
(`approved`, `rejected`, `cancelled`, `expired`) are final — no further
transitions.

## Events and webhooks

Every status-changing transition appends to `approval_event` and,
if `callback_url` is set on the request, enqueues a `webhook_delivery`.

### Event types

| Event               | Emitted when                                                      | Fires webhook? |
| ------------------- | ----------------------------------------------------------------- | -------------- |
| `request_created`   | `POST /requests` succeeds                                          | ✅              |
| `stage_started`     | A stage is resolved and its tasks created                          | ✅              |
| `stage_completed`   | A stage reaches `approved` or `rejected`                           | ✅              |
| `stage_skipped`     | `skip_if` true, or `on_empty=skip` + empty resolution             | ✅              |
| `stage_escalated`   | SLA breach with `on_breach=escalate` added new approver tasks      | ✅              |
| `request_approved`  | Last stage completed with `approved`                               | ✅              |
| `request_rejected`  | Any stage completed with `rejected`, or `on_empty=block` triggered | ✅              |
| `request_cancelled` | `POST /requests/{id}/cancel`                                       | ✅              |
| `task_expired`      | SLA monitor finds an open/claimed task past `due_at`               | ✅              |
| `task_reassigned`   | Admin reassigned a task via `POST /tasks/{id}/reassign`            | ✅              |

### Webhook request format

```http
POST <request.callback_url>
Content-Type: application/json
X-Approval-Event-Id: 7f3e...
X-Approval-Timestamp: 1730000000
X-Approval-Signature: sha256=<hex HMAC>

{
  "event_id": "7f3e...",
  "event_type": "request_approved",
  "request_id": "r-abc-123",
  "artifact_type": "registry.change_request",
  "artifact_id": "cr-42",
  "status": "approved",
  "stage_order": 2,
  "actor": "u-director-X",
  "occurred_at": "2026-04-23T10:14:22Z"
}
```

### Signature scheme

```
HMAC_SHA256(
    key   = <the shared secret for this caller>,
    value = <X-Approval-Timestamp> + "." + <raw request body bytes>
)
```

The timestamp is included in the signed value so a captured body cannot
be replayed at a later time without invalidating the MAC. Callers should
reject deliveries whose timestamp is more than ~5 minutes off wall
clock.

### Retry schedule

Per-attempt HTTP timeout: `awe.webhook.timeout_seconds` (default 10s).

Non-2xx or network error → next attempt scheduled per
`awe.webhook.backoff_seconds`:

```
attempt 2:  +60s   (1m)
attempt 3:  +300s  (5m)
attempt 4:  +900s  (15m)
attempt 5:  +3600s (1h)
attempt 6:  +21600s (6h)   ← ~27h total window
```

After `awe.webhook.max_attempts` attempts (default 6), the delivery is
marked `exhausted`. Operators can manually retry via the admin UI /
ops API.

### Caller expectations

* Return any 2xx within the timeout.
* Dedup on `X-Approval-Event-Id` — AWE may re-deliver an event it
  already succeeded on (e.g. caller's 2xx response was lost to a network
  partition).
* Process events idempotently — `request_approved` for the same
  `request_id` may arrive twice and must not re-apply the artifact.

## Policy versioning: mutable drafts, immutable activated versions

* **Drafts** (status=`draft`) are mutable — edit metadata, add/remove
  stages, change rules via `PATCH /policies/{key}/versions/{v}`. No
  in-flight requests reference a draft, so in-place edits are safe.
* **Activated versions** (status=`active` or `archived`) are
  **immutable**. `PATCH` returns `409 AWE-007`. To propose changes, add
  a new draft via `PUT /policies/{key}` (pre-fills from the newest
  version in the admin UI), tweak, and activate.
* In-flight requests reference their starting version via
  `approval_request.policy_id`. Activating a new version does not
  re-route them.

### Which version runs when a Caller posts a request?

**The Caller does not specify a version.** `POST /v1/awe/requests`
accepts `policy_key` and has no `policy_version` field. The engine
resolves the one version with `status=active` for that key (the schema
guarantees at most one active version per `policy_key`) and pins the
new request to it.

Two implications:

* **"Active" is the selector, not "latest".** A policy can have
  v5=draft (newest), v4=archived, v3=active, v2=archived, v1=archived.
  New requests run under v3 — the single active version — not v5.
* **In-flight requests stay pinned to their starting version.** If you
  activate v6 tomorrow, today's v3 requests continue resolving stages
  under v3's rules; only *new* requests after that activation run under
  v6.

This is why `activate` / `deactivate` are the levers that change
behaviour for new requests. Callers stay version-agnostic.

## Idempotency

`POST /v1/awe/requests` accepts an optional `Idempotency-Key` request
header. AWE stores `(key, response_payload)` on first success; retries
with the same key replay the stored response rather than creating a
second request row. Keys are caller-defined — use a stable id (e.g.
`"{artifact_type}:{artifact_id}:{caller_request_id}"`).

Keys are retained forever in v1. A TTL-based sweeper can be added
later — meanwhile, storage is negligible (one row per
distinct caller retry).

## SLA and escalation

Each stage can specify `sla_hours`. When approver tasks are created for
the stage, `due_at` is set to `now + sla_hours`. The SLA monitor worker
(`awe.sla.check_interval_seconds`, default 300s) scans for
`status IN (open, claimed) AND due_at <= now()` and flips matching
approver tasks to `expired`. Observer tasks have no `due_at` and are
unaffected.

For each task that expires, AWE emits a `task_expired` event (which fires
a webhook). It then applies the stage's `on_breach` action **once per
stage per tick**, even if multiple tasks on the stage expire together:

| `on_breach`     | What AWE does                                                                                      |
| --------------- | -------------------------------------------------------------------------------------------------- |
| `notify` (default, also when null) | Nothing further. Caller decides what to do based on the `task_expired` events.       |
| `escalate`      | Resolves the stage's `escalation_rules` and adds those users as fresh approver tasks on the stage. Original expired tasks stay expired for audit. Emits `stage_escalated`. |
| `auto_approve`  | Synthesizes `approve` decisions for all remaining open tasks on the stage (`actor = sla-monitor`). Stage advances normally — including parallel-group completion checks. |
| `auto_reject`   | Symmetric — synthesizes `reject` decisions, terminating the request. |

The `notify` mode preserves the v1 behaviour where caller-side policy
owns the response. The other three are explicit opt-ins for AWE to take
the decision; they let policies that want fully automated SLA enforcement
avoid building parallel logic in every Caller.

When `escalate` cannot resolve any new approvers (rules return empty),
the action becomes a no-op — the original expired tasks remain expired
and the stage waits for caller intervention, the same as `notify`.

## Audit log

Every admin / ops mutation in AWE writes one row to `audit_action`. This
is **distinct from `approval_event`** (which captures the per-request
state machine for callers to consume via webhook): `audit_action`
records *who acted on shared configuration / state*, primarily for
forensic and compliance use.

### What gets recorded

| Action               | Trigger                                              | `before` snapshot       | `after` snapshot        |
| -------------------- | ---------------------------------------------------- | ----------------------- | ----------------------- |
| `policy.create`      | `POST /v1/awe/policies`                              | —                       | full PolicyOut          |
| `policy.add_version` | `PUT  /v1/awe/policies/{key}`                        | —                       | full PolicyOut          |
| `policy.update`      | `PATCH /v1/awe/policies/{key}/versions/{v}`          | full PolicyOut (pre)    | full PolicyOut (post)   |
| `policy.activate`    | `POST /v1/awe/policies/{key}/versions/{v}/activate`  | `{status,version}` of prior | `{status,version}` of new |
| `policy.deactivate`  | `POST /v1/awe/policies/{key}/versions/{v}/deactivate`| `{status: active}`      | `{status: archived}`    |
| `request.cancel`     | `POST /v1/awe/requests/{id}/cancel`                  | `{status: <prior>}`     | `{status: cancelled}`   |
| `delivery.retry`     | `POST /v1/awe/admin/deliveries/{id}/retry`           | `{status, attempt, …}`  | `{status: pending, …}`  |

Each row carries: `actor` (token `sub`), `actor_email`, `action`,
`resource_type`, `resource_id`, optional `summary` (UI-friendly), and
free-form `metadata` (cancel reason, request id, etc.).

### Reading the log

`GET /v1/awe/admin/audit?actor=&action=&resource_type=&resource_id=&since=&until=&limit=`

Accepts `AWE_VIEWER` or `AWE_ADMIN`. Newest rows first; max `limit=1000`.
The bundled admin SPA's "Audit Log" page renders this with filters and
expandable per-row diffs.

### What does NOT get recorded

* **Read endpoints** — `GET /policies`, `GET /requests/{id}/events`,
  `GET /admin/deliveries`, etc. Reads are not auditable for now; if you
  need access logs, source them from the Istio sidecar or the Keycloak
  audit stream.
* **Workflow events** — `request_created`, `stage_started`,
  `request_approved`, etc. Those live in `approval_event` (per-request
  timeline). Audit deals with *configuration* changes, not *workflow*
  state changes.
* **Caller `POST /requests`** — creating an approval request is a
  service-to-service operation, not an admin action; tracked instead in
  `approval_event` as `request_created`.

## Security posture

### Authentication

All runtime endpoints require a Keycloak-issued JWT bearer. AWE
operates under the shared **`staff`** realm (same realm as Registry /
PBMS / other OpenG2P modules — AWE does not own the realm, it just
provisions its own clients and roles inside it).

* **Service tokens** (client_credentials) — caller services use these
  for `POST /requests`, `GET /requests/{id}`, etc.
* **End-user tokens** — approver decisions (`POST /tasks/{id}/decision`)
  run with the user's token; `sub` becomes the `actor` on the decision.
* **Admin / viewer operations** — gated on two client roles provisioned
  on the `awe-admin-portal` client:

  | Role          | Grants                                                                                         |
  | ------------- | ---------------------------------------------------------------------------------------------- |
  | `AWE_ADMIN`   | Full read + write. Policy CRUD / activate / deactivate, request cancellation, delivery retry. |
  | `AWE_VIEWER`  | Read-only. List policies, requests, events, deliveries, and the audit log.                     |

  Roles are read from both `realm_access.roles` and
  `resource_access.<clientId>.roles` (the latter being the OpenG2P staff
  realm convention — see Registry for reference). Admins implicitly have
  viewer privileges; a call to a read endpoint with only `AWE_ADMIN`
  works.

Tokens are verified against Keycloak JWKS with an issuer check
(`awe.keycloak.issuer`). **Audience verification is disabled in v1**
(`awe.keycloak.audience` is empty in the shipped Helm values) so that
Caller integrations can forward an end-user's JWT to
`POST /tasks/{id}/decision` — that token's `aud` is the Caller's own
client (e.g. `registry-staff-portal`), not an AWE client, and would
otherwise be rejected. Signature + issuer are still enforced; only the
audience pin is relaxed. See
[Integration with Registry → the audience claim](integration-with-registry.md#the-audience-claim--current-decision-and-the-path-to-tighten-it)
for the rationale and the path to re-enabling it. A dev mode
(`issuer=""`) skips signature verification for local development and is
**not reachable in the shipped Helm chart**.

### Keycloak provisioning

The Helm chart uses the `keycloak-init` subchart to declare, in the
`staff` realm:

* **Client `awe-admin-portal`** — public OIDC client the admin SPA
  redirects to. Has two client roles, `AWE_ADMIN` and `AWE_VIEWER`. The
  commons-layer `admin` user is mapped to `AWE_ADMIN` on first install
  so operators can log into the SPA out of the box; grant `AWE_VIEWER`
  to read-only users via Keycloak admin UI as needed.
* **Client `awe-admin-resolver`** — confidential service-account client
  used by AWE to call Keycloak's admin API for `role:` and `group:`
  approver rule resolution. Its client secret lands in a Kubernetes
  Secret (named after the clientId, with key `client_secret`) that
  keycloak-init auto-syncs between Keycloak and K8s; AWE's Deployment
  injects it via `envVarsFrom`.

The resolver's service account (`service-account-awe-admin-resolver`,
auto-created by Keycloak) is granted `view-users` and `query-groups`
from the `realm-management` client — all declared in AWE's helm values
under `keycloak-init.realms.staff.users`, so no post-install manual
steps are required.

### Webhook signing secrets

Each caller service is provisioned with a shared HMAC secret
(`callback_secret`). The raw secret is delivered out-of-band (vault,
password manager); AWE stores only a hash. Rotation creates a new active
secret; the prior is marked `rotated`.

### PII

* AWE stores `artifact_type`, `artifact_id`, and the caller-supplied
  `context` on the request row. If the context carries PII, note that
  AWE is persisting it.
* Callers should avoid putting PII into context fields that aren't
  strictly required for approver resolution. If you only need
  `{"district": "D1"}` to pick approvers, don't also attach a full
  beneficiary record.

## Notifications (email, SMS, in-app, …)

**Sending notifications to approvers is the Caller's responsibility,
not AWE's.** This is the same "mechanism, not policy" stance applied to
SLA, post-approval business logic, and escalation. AWE provides the
trigger by firing a `stage_started` webhook with the resolved assignee
list; the Caller decides what channel(s) to use and what the message
looks like.

Why notifications belong in the Caller:

| Concern                             | Why the Caller, not AWE                                                                |
| ----------------------------------- | -------------------------------------------------------------------------------------- |
| Approver's email / phone            | Caller already has verified contact info per user; AWE only knows the Keycloak `sub`   |
| Channel choice                      | Email vs SMS vs in-app vs push depends on tenant config and user preference            |
| Message branding / localisation     | Different modules, environments, languages all want different copy                     |
| Deep links                          | Notifications should link to the Caller's own UI for the artifact, not to AWE          |
| Throttling / consolidation          | "5 approvals waiting" digest emails are a Caller policy decision                       |

A minimal SMTP notifier scaffold ships in
[`src/awe/services/notifier.py`](https://github.com/OpenG2P/awe/blob/develop/src/awe/services/notifier.py)
and is `enabled: false` by default. It exists only as a low-effort
fallback for trial deployments without a Caller-side notification
pipeline. Production deployments should leave it disabled and let the
Caller's webhook handler drive notifications.

## Caller integration surface

A Caller service (Registry, PBMS, …) talks to AWE through **two API
groups** plus webhook receipt. It does **not** touch the policy APIs —
those are for the admin UI and ops tooling.

| API surface                              | Who calls it                                                | When                                                            |
| ---------------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------- |
| `POST /v1/awe/requests`                  | Caller service (e.g. Registry)                              | When an artifact (CR, disbursement, …) is created and needs approval |
| `POST /v1/awe/requests/{id}/cancel`      | Caller service                                              | When the underlying artifact is withdrawn upstream              |
| `GET  /v1/awe/requests/{id}`             | Caller service                                              | Rarely — webhook usually keeps the local mirror fresh           |
| `GET  /v1/awe/requests/{id}/events`      | Caller service                                              | When showing an audit timeline for the artifact in the Caller's UI |
| `GET  /v1/awe/tasks?assignee=me`         | Caller service **proxying for an end-user approver**         | Approver opens their inbox in the Caller's UI                   |
| `POST /v1/awe/tasks/{id}/claim`          | Caller service proxying                                     | Approver clicks a task                                          |
| `POST /v1/awe/tasks/{id}/decision`       | Caller service proxying                                     | Approver clicks Approve / Reject                                |
| `POST <caller's callback handler>`       | **AWE** (outbound — Caller is the receiver)                 | Whenever a webhook-emitting state change occurs                 |
| `/v1/awe/policies/*`                     | Admin SPA / GitOps tooling — **not the Caller**             | Policy authors maintain rules                                   |
| `/v1/awe/health` `/version` `/config`    | Kubernetes probes / ops                                     | Continuous                                                      |

So the Caller's integration boils down to: implement one webhook
handler, call `/requests` for the artifact lifecycle, and proxy
`/tasks` on behalf of approvers. Policies are configured separately by
ops.

## Deferred / TODO

Items called out by the design but **not implemented in v1**. Tracked
here so they don't get lost — each will become a real ticket when
prioritised.

| Area                    | What's missing                                                                                                                                                                                  | Workaround for now                                                                          |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| **Webhook signing**     | No API or UI to provision / rotate `callback_secret` rows. The signing code reads them, but operators have no way to insert one.                                                                | For trial / internal mesh, leave the `callback_url` set without a `callback_secret_id`; deliveries go unsigned. Acceptable on a trusted network; not for production. |
| **Auto-escalation on SLA** | AWE marks tasks `expired` and fires a webhook, but doesn't auto-reassign or re-route. Caller decides response.                                                                                | Caller's webhook handler invokes `/v1/awe/requests/{id}/cancel` or creates a new request.   |
| **Parallel stages**     | Strictly sequential staging in v1. No BPMN-style gateways.                                                                                                                                      | Model parallel reviewers as multiple rules within a single stage in `all` mode.             |
| **Delegation / OOO**    | No "delegate to substitute when primary is away" support.                                                                                                                                       | Adjust the policy or add the substitute as an additional rule.                              |
| **Cross-module unified inbox** | Each Caller surfaces its own inbox in its own frontend, so an approver acting across modules sees them separately.                                                                                                                | Approver UIs in each Caller surface their own inbox via proxied `/v1/awe/tasks?assignee=me`. |
| **Attachments**         | Only `attachments_ref` URL stored; no upload/download.                                                                                                                                          | Files live in the Caller's storage; AWE just records the URL.                               |
| **Notification channels in AWE** | SMTP scaffold exists but is `enabled: false`; no SMS / push / in-app.                                                                                                                  | Notifications are the Caller's responsibility — see Notifications section.                  |
| **`expected_context_keys`** | No schema validation on the `context` blob sent in `POST /requests`.                                                                                                                      | Out-of-band coordination between policy author and Caller — see "Who decides what context to send?" |
| **Retire idempotency keys** | `idempotency_key` rows kept forever in v1; no TTL sweeper.                                                                                                                                  | Storage is negligible; sweep manually if needed.                                            |
| **Postman collection**  | Audit Manager ships one; AWE doesn't yet.                                                                                                                                                       | Hit the live Swagger UI at `/v1/awe/docs` for ad-hoc exploration.                           |

## FAQ

**Can one AWE serve multiple modules?** Yes — the default deployment is
**one shared instance per environment** serving all modules. The engine
is single-tenant (no `module` column); modules are separated by
`policy_key` namespacing (`registry.*`, `pbms.*`) rather than a schema
dimension, and webhooks route per-request. The trade-off is that admin is
global — any `AWE_ADMIN` can edit every module's policies — so a shared
instance suits a single central (commons) owner. Where modules need
isolated administration or blast-radius separation, deploy a dedicated
per-module instance instead. See
[Architecture → deployment topology](technical-architecture.md#deployment-topology-shared-per-environment-default).

**What does the `201` response from `POST /tasks/{id}/decision`
actually contain?** The newly-created decision row — its id, the
action, the actor, the comment, the timestamp. It is a *mechanical*
confirmation that the click was persisted; it does **not** carry the
updated request status (still in_review? approved? rejected?). That
state change is communicated to the Caller via the webhook — the
single source of truth. The decision response is useful for "your
approval was recorded" UX feedback; it is not a trigger for the
Caller's post-approval business logic.

**Why is a webhook needed at all? Couldn't the final 201 carry the
status?** In the happy approver-decision path, technically yes. But
three cases break that model: (1) **SLA expiry** is triggered by a
background loop with no HTTP call to piggyback on; (2) **admin
cancellation via the admin UI** sends the 200 to the admin, not the
Caller; (3) **process crashes** between the Caller receiving the 201
and persisting the side-effect cause silent divergence — webhook
retries make this recoverable. Webhooks give the Caller one consistent,
durable channel for every state change regardless of trigger.

**Where does the webhook code run?** Two sides. **Dispatch is in AWE** —
a background worker polls `webhook_delivery` and POSTs to whatever
`callback_url` was set on the request. **The handler is in the
Caller** — the Caller exposes one HTTP endpoint (e.g.
`POST /internal/approval-callbacks`) that accepts the POST, verifies
the HMAC signature, and triggers its own post-approval logic.

**Do approvers ever talk to AWE directly?** No — the Caller's UI is the
approver's only surface. Every `/v1/awe/tasks` call is the Caller's
service proxying on behalf of the approver. This keeps auth and CORS
simple and lets the Caller render the artifact alongside the task.

**What if SLA fires and a task expires — what does AWE do?** Marks the
task `expired`, appends a `task_expired` event, and fires a webhook to
the Caller. AWE itself does **not** auto-reject, auto-reassign, or
escalate — that's domain policy and lives in the Caller (cancel,
notify, reassign, etc.).

**Does AWE send approver notifications (email / SMS / push)?** No, by
design — that's the Caller's job. AWE fires `stage_started` with the
resolved assignee list; the Caller's webhook handler picks the channel,
template, and contact lookup. A disabled SMTP scaffold lives in
`src/awe/services/notifier.py` for low-effort fallbacks but is not the
recommended path for production.

**How does the Caller know what `context` keys to send?** Out-of-band —
AWE doesn't mediate it. If the active policy only uses `user` / `role` /
`group` rules, the Caller can send `context: {}`. If any rule type
reads from context (`expression`, `http`, or `skip_if`), the Caller
must send the keys those rules expect. See *"Who decides what context
to send?"* under Context semantics for the three management patterns
(fixed artifact blob, per-policy spec, simulate-driven discovery).

**Does the Caller specify which policy version to use?** No. The Caller
sends `policy_key` only; AWE resolves the currently `active` version
for that key and pins the request to it. "Active" (not "latest") is the
selector — a draft v5 won't be picked even if v3 is the active one.
In-flight requests stay on their starting version regardless of later
activations. See *"Which version runs when a Caller posts a
request?"* under Policy versioning.

**Are admin actions audited?** Yes. Every policy CRUD / activate /
deactivate, request cancellation, and delivery retry writes an
append-only row to `audit_action` capturing actor, action,
resource, before/after snapshots, and free-form metadata. Browse via
`GET /v1/awe/admin/audit` (or the Audit Log page in the admin SPA);
both accept `AWE_VIEWER` or `AWE_ADMIN`. Read operations and workflow
state transitions are NOT in this log — see "What does NOT get
recorded" under Audit log.

**What roles does AWE define?** Two: `AWE_ADMIN` (full read + write)
and `AWE_VIEWER` (read-only across policies / requests / events /
deliveries / audit log). Both are client roles on `awe-admin-portal`,
provisioned automatically by `keycloak-init`. Admin implies viewer
where it matters (a token with only `AWE_ADMIN` can hit read endpoints
that nominally accept `AWE_VIEWER`).

**Why isn't there a unified approver inbox?** Deliberate — the approver's
home is the caller's own UI, which proxies `/v1/awe/tasks?assignee=me`
and renders the artifact alongside. Each Caller surfaces its own inbox,
so an approver working across modules sees them separately regardless of
whether AWE is deployed shared or per-module.

**How do I support parallel approvals (e.g. two stages in parallel)?** v1
is strictly sequential. You can approximate parallelism by modeling both
reviewers as rules within a single stage in `all` mode — they'll both
get tasks concurrently and both must approve to complete the stage.

**What happens if Keycloak is down during stage resolution?** `role` /
`group` lookups fail, the stage does not start, the request stays in
`pending` or the prior-stage state. Retries happen via the webhook
dispatcher loop — no, the resolver doesn't auto-retry stage resolution
in v1. Operators can cancel and recreate, or wait and re-trigger by
touching a decision.

**Can a decision be reversed?** No — `approval_decision` is append-only.
To undo an approval, cancel the request and create a new one.

**What's stored about the artifact's content?** Only
`(artifact_type, artifact_id)` plus the caller-supplied context snapshot.
The artifact itself stays in the caller's DB. This is a deliberate
separation — AWE never becomes a mirror of caller state.

**Who edits policies?** Operations / policy authors with the Keycloak
`awe-admin` role. The bundled admin SPA at `/v1/awe/admin` is a typical
operator surface; the same endpoints are callable via API for
GitOps-style policy management.
