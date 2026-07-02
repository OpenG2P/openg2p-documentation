---
description: >-
  A generic, configurable multi-stage approval workflow engine for OpenG2P.
  Caller services post artifacts for approval; AWE resolves stages and
  approvers, tracks decisions, and notifies callers via sig
---

# Approval Workflow Engine (AWE)

## Overview

The Approval Workflow Engine (AWE) is the platform-level service that governs multi-stage approvals for OpenG2P modules — change requests in the Registry, disbursements in PBMS, and any other artifact that must pass through configurable, multi-stage sign-off before taking effect.

It is **not** a BPMN engine or a workflow orchestrator for arbitrary business processes. It does exactly one thing well: **resolve a chain of approvers, gate a caller-owned artifact on their decisions, and signal the caller when the outcome is known**.

Built with **FastAPI** + **async SQLAlchemy** + **PostgreSQL**. Designed for **horizontal scaling on Kubernetes** and deployed as **one shared instance per environment** serving all caller modules (Registry, PBMS, …). A dedicated per-module deployment remains an option where modules need isolated administration — see [Architecture → deployment topology](technical-architecture.md#deployment-topology-shared-per-environment-default).

> **Looking for "what scenarios can I model?"** — see the
> [Scenarios catalog](scenarios.md) for a one-page index of every
> approval pattern AWE handles, mapped to the configuration knob that
> produces it.

### Key capabilities

* **Caller-agnostic** — AWE doesn't know your artifact's shape. Callers pass `(artifact_type, artifact_id, context)` plus a callback URL; AWE only stores the identifier and a context snapshot used for approver resolution.
* **Versioned policies** — every edit to an active policy creates a new draft version. In-flight requests stay pinned to the version they started with, so policy changes never rewrite mid-flight approvals.
* **Flexible approver resolution** — five rule types per stage: literal `user`, Keycloak `role`, Keycloak `group`, `expression` (JSONLogic over the request context), and `http` (escape hatch calling the caller's resolver endpoint). Rules union within a stage.
* **Multiple decision modes** — `all`, `any-N`, `quorum:N`, `percentage:P`. Skip rules (`skip_if` JSONLogic, `on_empty`) handle conditional bypass and zero-approver stages.
* **Push notification via signed webhooks** — state changes are POSTed to the caller with an HMAC signature and timestamp; retries with exponential backoff (1m → 5m → 15m → 1h → 6h) over \~24 hours before giving up.
* **Idempotent request creation** — `Idempotency-Key` header dedups retried `POST /v1/awe/requests` calls so a caller's retry policy never creates duplicate approval flows.
* **Immutable audit log** — every state transition emits an `approval_event` row; the API exposes a full timeline per request.
* **Keycloak-native** — inbound bearer tokens verified against JWKS; approver/group lookups use the Keycloak admin API.

## Design at a glance

```
┌──────────────────────────┐
│  Caller service          │   POST /v1/awe/requests
│  (Registry, PBMS, …)     │ ────────────────────────────┐
│                          │ ◄─── webhook (HMAC) ─────┐  │
└──────────┬───────────────┘                          │  │
           │ proxies approver UI → /v1/awe/tasks      │  │
           ▼                                          │  │
┌──────────────────────────────────────────────────┐  │  │
│   Caller UI (module's own frontend)              │  │  │
└──────────────────────────────────────────────────┘  │  │
                                                      │  │
                                                      │  ▼
                                          ┌───────────────────────┐
                                          │  AWE (shared)         │
                                          │                       │
                                          │  Policy   Engine      │
                                          │  Resolver Webhook     │
                                          │  SLA monitor          │
                                          │                       │
                                          │  Admin UI at /admin   │
                                          └──────┬────────────────┘
                                                 │
                                      ┌──────────┼───────────┐
                                      ▼          ▼           ▼
                                 ┌────────┐ ┌────────┐ ┌──────────┐
                                 │Postgres│ │Keycloak│ │HTTP       │
                                 │        │ │(roles, │ │resolvers  │
                                 │ policy │ │groups, │ │(optional, │
                                 │ request│ │  JWT)  │ │caller-side)│
                                 │ task   │ └────────┘ └──────────┘
                                 │ event  │
                                 │webhook │
                                 └────────┘
```

Caller UI never talks to AWE directly — the caller service proxies `/v1/awe/tasks` and decision calls on behalf of its end users. That keeps auth and CORS simple and lets the caller enrich the approver inbox with its own artifact detail.

## Example — two-stage approval, happy path

**The policy** (`registry.cr.v1`) has two stages:

* **Stage 1 — "District officers"** — mode `any-N:1`, rule `group: /districts/D1` → resolves to **Alice** and **Bob**. Any one approval advances the stage.
* **Stage 2 — "State directors"** — mode `all`, rule `user: director-X` → resolves to **Director-X** only. Director-X's approval finalizes the request.

**The scenario**:

1. A change request `cr-42` (for district D1) **is created in Registry somehow** — by a field agent, a bulk import, an upstream system, a CSV upload; how and by whom is outside AWE's concern. Registry owns the CR.
2. Registry posts an approval request to AWE.
3. **Alice** (a district officer) logs into Registry, sees `cr-42` in her approval inbox, and approves — satisfying stage 1's `any-N:1`, which skips Bob's task.
4. **Director-X** logs into Registry, sees `cr-42` in his approval inbox, and approves — satisfying stage 2's `all` and finalizing the request.
5. AWE fires the final webhook, Registry applies the CR.

Alice and Director-X are **purely approvers** — they neither authored `cr-42` nor edit it; they only review and approve what's already there.

**Key point about the arrows**: approvers never talk to AWE directly — they interact with the Registry UI, and Registry proxies `/v1/awe/tasks` + decision calls to AWE on their behalf. Every approver action below is drawn as two hops: Alice → Registry → AWE, response back the same way.

```
┌───────┐   ┌──────────┐   ┌──────────┐   ┌─────────┐
│ Alice │   │Director-X│   │ Registry │   │   AWE   │
└───┬───┘   └────┬─────┘   └────┬─────┘   └────┬────┘
    │            │              │               │
    │            │              │ ── CR cr-42 is created in Registry by
    │            │              │    someone (not shown — not relevant
    │            │              │    to AWE). Registry persists it with
    │            │              │    local approval_status=pending.
    │            │              │               │
    │            │              │ POST /v1/awe/requests
    │            │              │ {policy_key: registry.cr.v1,
    │            │              │  artifact_id: cr-42,
    │            │              │  context: {district: "D1"}}
    │            │              ├──────────────►│
    │            │              │               │ resolve stage 1
    │            │              │               │  (group /districts/D1)
    │            │              │               │  → Alice, Bob
    │            │              │               │ persist request +
    │            │              │               │  2 tasks + events
    │            │              │ 201 {request_id,
    │            │              │      status: in_review,
    │            │              │      tasks: [alice, bob]}
    │            │              │◄──────────────┤
    │            │              │               │
    │            │              │ webhook: request_created
    │            │              │         + stage_started
    │            │              │◄──────────────┤
    │            │              │ mirror approval_status=in_review
    │            │              │               │
    │            │              │               │
    │ ═══════ Alice logs into Registry, opens her approval inbox ═══════
    │            │              │               │
    │ GET /registry/my-approvals│               │
    ├────────────┼─────────────►│               │
    │            │              │ Registry proxies Alice's AWE task list
    │            │              │ GET /v1/awe/tasks?assignee=me
    │            │              ├──────────────►│
    │            │              │ [alice's open task for cr-42]
    │            │              │◄──────────────┤
    │ inbox: [cr-42 pending your approval]
    │◄───────────┼──────────────┤               │
    │            │              │               │
    │ Alice clicks cr-42 → reviews the CR detail (from Registry's own DB)
    │ → clicks "Approve"        │               │
    ├────────────┼─────────────►│               │
    │            │              │ POST /v1/awe/tasks/{alice-task}
    │            │              │      /decision
    │            │              │ {action: approve}
    │            │              ├──────────────►│
    │            │              │               │ stage 1 (any-N:1) met
    │            │              │               │ → skip Bob's open task
    │            │              │               │ → resolve stage 2
    │            │              │               │    (user: director-X)
    │            │              │               │ → create dirX task
    │            │              │ 201 Decision  │
    │            │              │◄──────────────┤
    │ ok         │              │               │
    │◄───────────┼──────────────┤               │
    │            │              │               │
    │            │              │ webhook: stage_completed (s1)
    │            │              │         + stage_started (s2)
    │            │              │◄──────────────┤
    │            │              │               │
    │            │              │               │
    │            │ ═══════ Director-X logs into Registry, opens his approval inbox ═══
    │            │              │               │
    │            │ GET /registry/my-approvals   │
    │            ├─────────────►│               │
    │            │              │ GET /v1/awe/tasks?assignee=me
    │            │              ├──────────────►│
    │            │              │ [dirX's open task for cr-42]
    │            │              │◄──────────────┤
    │            │ inbox: [cr-42 pending your approval]
    │            │◄─────────────┤               │
    │            │              │               │
    │            │ Director-X clicks cr-42 → reviews → "Approve"
    │            ├─────────────►│               │
    │            │              │ POST /v1/awe/tasks/{dirX-task}
    │            │              │      /decision {action: approve}
    │            │              ├──────────────►│
    │            │              │               │ stage 2 ("all", 1 of 1)
    │            │              │               │ complete → last stage
    │            │              │               │ → request approved
    │            │              │ 201 Decision  │
    │            │              │◄──────────────┤
    │            │ ok           │               │
    │            │◄─────────────┤               │
    │            │              │               │
    │            │              │ webhook: stage_completed (s2)
    │            │              │         + request_approved
    │            │              │◄──────────────┤
    │            │              │ apply cr-42 to registry tables
    │            │              │ (Registry's own post-approval side-effect)
```

## Example — request is cancelled

```
┌─────────┐            ┌──────┐
│Registry │            │ AWE  │
└────┬────┘            └──┬───┘
     │ POST /requests     │
     ├───────────────────►│  creates request, stage 1 resolved
     │ 201                │
     │◄───────────────────┤
     │                    │
     │ (business reason — the underlying CR was withdrawn)
     │                    │
     │ POST /requests/{id}/cancel {reason:"withdrawn"}
     ├───────────────────►│  flips request.status = cancelled
     │ 200                │  skips remaining open tasks
     │◄───────────────────┤  emits request_cancelled event
     │                    │
     │ webhook: request_cancelled
     │◄───────────────────┤
```

## Detailed documentation

| Page                                                      | Description                                                                                                                                                                               |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Functional Specifications](functional-specifications.md) | Policy model, stage modes, approver rule types, context semantics, skip rules, request lifecycle state machine, webhook contract (signature, retry schedule), PII / security posture, FAQ |
| [API Reference](api-reference.md)                         | REST API endpoints rendered live from OpenAPI 3.1 — request/response shapes, status codes, error-code catalog                                                                             |
| [Technical Architecture](technical-architecture.md)       | Why this design over alternatives (Camunda, polling, multi-tenant), scalability model, delivery guarantees, engine state machine, approver-resolution caching                             |
| [Deployment](deployment.md)                               | Local dev with Docker Compose, Helm chart install, configuration reference, Keycloak prerequisites, operational runbook, security considerations                                          |
| [Testing](testing.md)                                     | Pytest smoke tests (hermetic, in-memory SQLite), test strategy, sample payloads                                                                                                           |

## Versions

| Helm Chart Version                                           | Docker Image                  | Date        | Comments           |
| ------------------------------------------------------------ | ----------------------------- | ----------- | ------------------ |
| [0.0.0-develop](https://github.com/OpenG2P/awe/tree/develop) | `openg2p/openg2p-awe:develop` | in progress | Active development |

## Source code

* GitHub: [https://github.com/OpenG2P/awe](https://github.com/OpenG2P/awe)

## Technology stack

| Component     | Choice                   | License                         |
| ------------- | ------------------------ | ------------------------------- |
| Language      | Python 3.11+             | PSF License (permissive)        |
| Web Framework | FastAPI                  | MIT                             |
| ASGI Server   | Uvicorn                  | BSD-3-Clause                    |
| DB Driver     | asyncpg                  | Apache 2.0                      |
| ORM           | SQLAlchemy 2.x (async)   | MIT                             |
| Config        | Pydantic Settings        | MIT                             |
| Auth          | Keycloak OIDC (JWT/JWKS) | Apache 2.0                      |
| Rule engine   | JSONLogic                | MIT                             |
| Admin UI      | React + Vite + TS        | MIT                             |
| Database      | PostgreSQL               | PostgreSQL License (permissive) |
| Deployment    | Kubernetes + Helm        | Apache 2.0                      |

All components use **permissive open-source licenses**. No copyleft (GPL) dependencies.
