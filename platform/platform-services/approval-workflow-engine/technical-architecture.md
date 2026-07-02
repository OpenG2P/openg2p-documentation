---
description: >-
  Design choices behind the Approval Workflow Engine — why each alternative was
  rejected, scalability model, delivery guarantees, engine state machine, and
  approver-resolution caching.
---

# Technical Architecture

## Why this design

We made several non-obvious choices. Each section below states the
alternative we considered and why we rejected it.

### Why a dedicated approval service and not per-module approval logic?

OpenG2P modules have overlapping approval needs: Registry needs change-
request sign-off, PBMS needs disbursement sign-off, new modules will
need their own. Building approvals ad-hoc inside each service means:

* Every module reimplements stage modes, approver resolution, audit
  trail, SLA, retry.
* Bug fixes (e.g. idempotent stage transitions) don't propagate.
* No uniform API for approver UIs across modules.

AWE centralises the generic parts. Each module keeps its domain logic
and plugs into AWE for the approval gate.

### Why AWE owns policies, and callers are policy-agnostic?

Callers pass `policy_key` and `context`. AWE resolves stages and
approvers. The caller never needs to know the stage count, the approver
identities, or whether a stage was skipped.

This matters for a common case: **zero-stage or all-skipped policies**.
The caller sends a request, AWE resolves "no stages apply" → instantly
flips the request to `approved` → fires the webhook. The caller's code
path is the same whether approvals are needed or not:

```python
# In the caller
awe.create_request(...)           # fire and forget
# … later, webhook arrives with status=approved  → apply the CR
```

Without this, every caller would branch: "is this artifact subject to
approval? if yes, send; if no, apply directly." That branching logic
would drift over time; worse, policy changes in AWE wouldn't update
caller behaviour until the caller redeployed.

### Why Camunda / Flowable were rejected

BPMN engines solve a much larger problem: arbitrary workflow
orchestration with timers, gateways, sub-processes, compensating
transactions, human tasks, script tasks, message events, and more. Pure
approval needs — "one artifact, N sequential stages of human sign-off" —
don't justify a JVM engine, a BPMN modeler, or a second persistence
runtime alongside our Python stack.

We reserve the right to revisit Camunda if the scope genuinely grows:
cross-service orchestration, long-running SLAs with compensation, BPMN
gateways. None of that is on our roadmap.

### Why push webhooks and not pull?

Callers must know when an approval completes. The pull model
(caller polls `GET /requests/{id}`) has two problems:

* **Every list / read path fans out to AWE.** Rendering a list of 50
  change requests requires 50 AWE calls to fetch status.
* **Latency / freshness** — how often do you poll? Slow polling delays
  business logic; fast polling wastes both sides.

Push gives the caller a local mirror (`approval_status` column on the
caller's own row) that's kept fresh via webhook. List/read paths stay
purely local. Integration cost is ~50 lines per caller for the webhook
handler plus a column — implemented once in a shared client library.

### Why DB-as-queue instead of Redis / Kafka?

`webhook_delivery` is a table with `status`, `next_attempt_at`, and
`attempt` columns. The dispatcher worker claims rows via
`SELECT … WHERE status='pending' AND next_attempt_at <= now() … FOR
UPDATE SKIP LOCKED`.

Why this is enough:

* **Volume is low.** Webhooks fire on state transitions, not on every
  artifact. A busy module emits a few thousand deliveries per day, not
  per second.
* **Postgres SKIP LOCKED handles multi-replica dispatch correctly.** No
  second datastore to operate.
* **Retry schedule is simple arithmetic.** No need for a scheduler
  service.
* **At-least-once is easy.** Any failed update simply re-appears on the
  next tick. Callers must already be idempotent on `event_id`.

Kafka / Redis would add operational complexity for no measurable gain
at our volume. If volume grows 100×, we can introduce them later
without reshaping the API.

### Deployment topology: shared per environment (default)

**The engine is deliberately single-tenant** — there is no `module`
column on any table, and no per-module filtering in queries. That
simplicity is intentional and is what makes both deployment models below
possible; module separation, where needed, is achieved by `policy_key`
namespacing (`registry.*`, `pbms.*`) rather than by a schema dimension.

**Default: one shared instance per environment.** A single AWE serves all
caller modules. This works cleanly because webhooks route per-request via
each request's `callback_url`, `policy_key` namespaces policies by module,
and approver authorities are just policy data. It's the natural fit for a
commons deployment — one release, one database, one admin surface — and
avoids N deployments + N databases.

The cost of sharing, given the single-tenant schema, is **admin
isolation**: `AWE_ADMIN` / `AWE_VIEWER` are global roles, so any admin can
edit *every* module's policies and the audit log mixes all modules. That
is fine when a single central (commons) team owns all approvals; it is a
governance risk when modules have separate owners.

**Alternative: a dedicated per-module instance.** Deploying a separate AWE
per module (`registry-awe`, `pbms-awe`, …) buys:

* **Clean blast radius.** A `registry-awe` outage affects Registry only.
* **Independent scaling.** PBMS can run 2 replicas, Registry 8.
* **Admin isolation.** Each module's admins see only their own policies
  and audit log — no global-role bleed.

The tradeoff either way: approvers who work across modules see separate
inboxes when instances are separate — acceptable because approver UIs live
in the caller's own frontend regardless.

Guidance:

* **Single owner / commons deployment** → shared per environment
  (default). Hold `AWE_ADMIN` with the central team; namespace
  `policy_key` by module.
* **Separate governance owners per module** → dedicated per-module
  instance for admin + blast-radius isolation.
* **Shared *with* strict isolation** → would require adding a `module`
  column, module-scoped admin roles, and audit filtering. Not built
  today; only worth it if you need one deployment *and* hard separation.
* **Hybrid** → dedicated AWE for high-stakes modules (e.g. PBMS
  disbursements), shared for the rest.

## Scalability model

```
                      ┌────────────────┐
 HTTP from callers ──►│  Istio / LB    │
                      └────┬───────────┘
                           │
                 ┌─────────┴────────────────┐
                 ▼                          ▼
           ┌──────────┐              ┌──────────┐
           │ AWE pod 1│     …        │ AWE pod N│    ← HPA on CPU/mem
           │  FastAPI │              │  FastAPI │      (default 2-8)
           │ dispatch │              │ dispatch │
           │ sla mon. │              │ sla mon. │
           └─────┬────┘              └─────┬────┘
                 │                         │
                 └───────┐      ┌──────────┘
                         ▼      ▼
                      ┌──────────┐
                      │Postgres  │    ← shared state + DB-as-queue
                      └──────────┘
```

Every replica runs the full set: HTTP, webhook dispatcher, SLA monitor.
DB-as-queue with SKIP LOCKED ensures no two replicas deliver the same
webhook twice. Scaling is "add another pod"; no leader election
required.

Theoretical ceilings:

* **HTTP ingest**: bounded by Postgres write throughput on
  `approval_request` / `approval_task`. Single modest Postgres
  comfortably handles the transactional rate typical of approval flows.
* **Webhook dispatch**: bounded by caller response time and
  `awe.webhook.batch_size`. Grows near-linearly with replicas.

## Engine state machine

```
apply_decision(request, task, action)
  ├── guard: request.status in {pending, in_review}
  ├── guard: task.status in {open, claimed}
  ├── guard: task.stage_order == request.current_stage_order
  │
  ├── mark task completed
  ├── count decisions for this stage
  │
  ├── evaluate_stage() → "open" | "approved" | "rejected"
  │
  ├── if "open":   return                          (wait for more decisions)
  ├── if "rejected":
  │     mark remaining stage tasks = skipped
  │     request.status = rejected
  │     emit stage_completed{outcome: rejected}
  │     emit request_rejected
  │
  └── if "approved":
        mark remaining stage tasks = skipped
        emit stage_completed{outcome: approved}
        if last stage:
            request.status = approved
            emit request_approved
        else:
            advance_to_stage(current + 1)
              ├── evaluate skip_if on target stage
              ├── if truthy: emit stage_skipped, try next
              ├── resolve approvers from rules
              ├── if empty + on_empty=skip: emit stage_skipped, try next
              ├── if empty + on_empty=block:
              │     request.status = rejected
              │     emit request_rejected{reason: no_approvers}
              └── else: create tasks, emit stage_started
```

Stage evaluation is **decision-count based**, not task-status based:

```
if stage.mode == "all":
    if rejects > 0: rejected
    elif approves == total: approved
    else: open
if stage.mode in ("any-n", "quorum"):
    if approves >= N: approved
    elif approves + remaining_open < N: rejected   # can't reach N any more
    else: open
if stage.mode == "percentage":
    needed = ceil(P/100 * total)
    same math with `needed` in place of N
```

## Approver resolution caching

Within a single request's lifecycle, every rule is cached by
`(rule_id, context_hash)`. This matters when a stage 2 rule resolves to
the same underlying Keycloak group as a stage 1 rule: the Keycloak
admin API is hit once, not twice. The cache is scoped per-request, so
concurrent requests don't share resolutions.

Across requests, there is no caching in v1 — every stage resolution
calls Keycloak fresh. This is a deliberate starting point: Keycloak is
the source of truth, and a TTL cache introduces staleness bugs that are
much more expensive to debug than a few extra admin API calls. If
Keycloak admin-API load becomes real, we can add a short-TTL cache
(30-60s) at the resolver boundary.

## Delivery guarantees

### HTTP API

Policy CRUD and request creation are **synchronous** transactions on
Postgres. A 2xx response means the state change is durably committed.

`POST /requests` is **idempotent via `Idempotency-Key` header** — retries
replay the stored response without creating a second request row.

### Webhooks

**At-least-once.** Duplicates are possible (caller's 2xx response lost to
a network partition → AWE retries → caller sees the same event
twice). Callers dedup on `event_id`.

**Durability.** Every webhook delivery is a row in
`webhook_delivery`. If AWE crashes mid-attempt, the row's `status` stays
`pending`; the next replica that ticks the dispatcher picks it up.

**Ordering.** Not guaranteed across delivery attempts to a single caller
— the retry of event A might overtake event B. Callers should use
`occurred_at` on the webhook body to sequence events for a given
`request_id`; this is monotone per request because state transitions are
serialized through a single DB transaction.

## Audit and observability

* **Every state transition** appends to `approval_event`. The table is
  append-only; `approval_decision` is too. Investigation queries walk
  the event timeline via `GET /requests/{id}/events`.
* **Webhook outcomes** are in `webhook_delivery` — `status`,
  `last_status_code`, `last_error`, attempt count. Surfaces via the
  admin UI's Webhook Deliveries page.
* **Structured logs** — lifespan, dispatcher, SLA monitor log to stdout
  in standard Python format; pair with OpenG2P's [Audit Manager](../audit-manager/)
  for long-term forensic retention of admin policy changes.
