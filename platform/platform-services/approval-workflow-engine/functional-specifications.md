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
policy  (policy_key, version, artifact_type, status)
  ├── stage 1  (stage_order=1, mode, sla_hours, skip_if, on_empty)
  │     ├── rule A  (rule_type, rule_value)
  │     ├── rule B  …
  │     └── rule C  …
  ├── stage 2  …
  └── …
```

* `policy_key` is the logical identifier — e.g. `registry.change_request`.
* `version` increments with every edit. At most one version has
  `status=active` per `policy_key` at any time.
* `artifact_type` is caller-defined (opaque to AWE).
* Stages are **strictly sequential**. Parallel gateways are explicitly not
  supported in v1.

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

| Rule type    | `rule_value` shape                        | Approvers resolved from                                                       |
| ------------ | ----------------------------------------- | ----------------------------------------------------------------------------- |
| `user`       | `{"user_id": "u-alice"}`                  | Literal — always that one user.                                               |
| `role`       | `{"role": "district-officer"}`            | Members of that Keycloak realm role (via admin API).                          |
| `group`      | `{"group": "/districts/A"}`               | Members of that Keycloak group path.                                          |
| `expression` | `{"logic": <JSONLogic>}`                  | JSONLogic evaluated against the request's context snapshot.                   |
| `http`       | `{"url": "https://caller/resolve"}`       | Caller POSTed at that URL — returns `{"user_ids":[...]}`.                     |

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
| `stage_skipped`     | `skip_if` true, or `on_empty=skip` + empty resolution             | (in timeline only) |
| `request_approved`  | Last stage completed with `approved`                               | ✅              |
| `request_rejected`  | Any stage completed with `rejected`, or `on_empty=block` triggered | ✅              |
| `request_cancelled` | `POST /requests/{id}/cancel`                                       | ✅              |
| `task_expired`      | SLA monitor finds an open/claimed task past `due_at`               | ✅              |

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

Each stage can specify `sla_hours`. When tasks are created for a stage,
`due_at` is set to `now + sla_hours`. The SLA monitor worker
(`awe.sla.check_interval_seconds`, default 300s) scans for
`status IN (open, claimed) AND due_at <= now()` and flips them to
`expired`.

**AWE's role is mechanism, not policy.** The monitor does exactly three
things: marks the task `expired`, appends a `task_expired` event, and
fires a webhook to the caller's `callback_url`. It does **not**
auto-reject the request, auto-reassign, auto-escalate, or send
reminders — all of that is domain-specific policy that belongs in the
caller (Registry, PBMS, …).

The webhook payload includes `task_id`, `stage_order`, `assignee`, and
`due_at`, giving the caller enough to decide:

* **Hard deadline** — cancel via `POST /v1/awe/requests/{id}/cancel`.
* **Nudge-then-escalate** — send a reminder email; if still open after
  another window, cancel.
* **Reassign to supervisor** — cancel and create a new request with a
  different `policy_key`.
* **Silent reminder** — send a nag email, leave the task alone.

A future iteration may add escalation rules on the policy itself
(auto-reassign on expiry, auto-reject after N expirations). For v1,
callers own the decision.

## Security posture

### Authentication

All runtime endpoints require a Keycloak-issued JWT bearer:

* **Service tokens** (client_credentials) — caller services use these
  for `POST /requests`, `GET /requests/{id}`, etc.
* **End-user tokens** — approver decisions (`POST /tasks/{id}/decision`)
  run with the user's token; `sub` becomes the `actor` on the decision.
* **Admin operations** (policy CRUD, `cancel`) require the `awe-admin`
  realm role.

Tokens are verified against Keycloak JWKS with issuer+audience checks
(`awe.keycloak.issuer`, `awe.keycloak.audience`). A dev mode
(`issuer=""`) skips signature verification for local development and is
**not reachable in the shipped Helm chart**.

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

## FAQ

**Can one AWE serve multiple modules?** The design deliberately runs one
AWE per module (`registry-awe`, `pbms-awe`, …). This keeps policy
namespaces clean, isolates load, and avoids a "tenant" dimension on
every table. The tradeoff is that approvers who act across modules have
separate inboxes.

**Why isn't there a unified approver inbox?** See above — deliberate
tradeoff. The approver's home is the caller's own UI, which proxies
`/v1/awe/tasks?assignee=me` and renders the artifact alongside.

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
