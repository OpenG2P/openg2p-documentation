---
description: >-
  A generic, configurable multi-stage approval workflow engine for OpenG2P.
  Caller services post artifacts for approval; AWE resolves stages and
  approvers, tracks decisions, and notifies callers via signed webhook
  callbacks when state changes.
---

# Approval Workflow Engine

## Overview

The Approval Workflow Engine (AWE) is the platform-level service that
governs multi-stage approvals for OpenG2P modules — change requests in
the Registry, disbursements in PBMS, and any other artifact that must
pass through configurable, multi-stage sign-off before taking effect.

It is **not** a BPMN engine or a workflow orchestrator for arbitrary
business processes. It does exactly one thing well: **resolve a chain of
approvers, gate a caller-owned artifact on their decisions, and signal
the caller when the outcome is known**.

Built with **FastAPI** + **async SQLAlchemy** + **PostgreSQL**. Designed for
**horizontal scaling on Kubernetes**, with **one AWE deployment per caller
module** (`registry-awe`, `pbms-awe`, …) for clean isolation.

### Key capabilities

* **Caller-agnostic** — AWE doesn't know your artifact's shape. Callers
  pass `(artifact_type, artifact_id, context)` plus a callback URL; AWE
  only stores the identifier and a context snapshot used for approver
  resolution.
* **Versioned policies** — every edit to an active policy creates a new
  draft version. In-flight requests stay pinned to the version they
  started with, so policy changes never rewrite mid-flight approvals.
* **Flexible approver resolution** — five rule types per stage: literal
  `user`, Keycloak `role`, Keycloak `group`, `expression` (JSONLogic
  over the request context), and `http` (escape hatch calling the
  caller's resolver endpoint). Rules union within a stage.
* **Multiple decision modes** — `all`, `any-N`, `quorum:N`,
  `percentage:P`. Skip rules (`skip_if` JSONLogic, `on_empty`) handle
  conditional bypass and zero-approver stages.
* **Push notification via signed webhooks** — state changes are POSTed
  to the caller with an HMAC signature and timestamp; retries with
  exponential backoff (1m → 5m → 15m → 1h → 6h) over ~24 hours before
  giving up.
* **Idempotent request creation** — `Idempotency-Key` header dedups
  retried `POST /v1/awe/requests` calls so a caller's retry policy
  never creates duplicate approval flows.
* **Immutable audit log** — every state transition emits an
  `approval_event` row; the API exposes a full timeline per request.
* **Keycloak-native** — inbound bearer tokens verified against JWKS;
  approver/group lookups use the Keycloak admin API.

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
                                          │  AWE (per module)     │
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

Caller UI never talks to AWE directly — the caller service proxies
`/v1/awe/tasks` and decision calls on behalf of its end users. That
keeps auth and CORS simple and lets the caller enrich the approver
inbox with its own artifact detail.

## Example — two-stage approval, happy path

```
┌─────────┐         ┌──────────┐         ┌──────────┐         ┌──────────┐
│Registry │         │   AWE    │         │ Postgres │         │  Alice   │
└────┬────┘         └────┬─────┘         └────┬─────┘         └────┬─────┘
     │                   │                    │                    │
     │ POST /requests    │                    │                    │
     │ {cr-42, ctx:{D1}} │                    │                    │
     ├──────────────────►│                    │                    │
     │                   │ resolve stage 1    │                    │
     │                   │ (district D1 grp)  │                    │
     │                   │ ─► Alice, Bob      │                    │
     │                   │ write request +    │                    │
     │                   │ 2 tasks + event    │                    │
     │                   ├───────────────────►│                    │
     │  201 {request_id, │                    │                    │
     │  status:in_review,│                    │                    │
     │  tasks:[alice,bob]│                    │                    │
     │◄──────────────────┤                    │                    │
     │                   │                    │                    │
     │                   │  webhook: request_created + stage_started
     │◄──────────────────┤                    │                    │
     │ set approval_     │                    │                    │
     │ status=in_review  │                    │                    │
     │                   │                    │                    │
     │                                                             │
     │ (Alice logs into Registry UI, Registry fetches her tasks)  │
     │                   │ GET /tasks?assignee=me                  │
     │                   │◄────────────────────────────────────────┤
     │                   │ [alice's open task]                    │
     │                   ├────────────────────────────────────────►│
     │                                                             │
     │                   │ POST /tasks/t-alice/decision            │
     │                   │ {action:approve}                        │
     │                   │◄────────────────────────────────────────┤
     │                   │ any-1 satisfied                         │
     │                   │ skip bob's task                         │
     │                   │ resolve stage 2                         │
     │                   │ ─► director-X                           │
     │                   ├───────────────────►│                    │
     │                   │                    │                    │
     │  webhook: stage_completed + stage_started (stage 2)         │
     │◄──────────────────┤                    │                    │
     │                                                             │
     │   … director-X approves (stage 2 is `all` with 1 approver) │
     │                                                             │
     │   webhook: stage_completed + request_approved              │
     │◄──────────────────┤                    │                    │
     │ apply CR to       │                    │                    │
     │ registry tables   │                    │                    │
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

| Page                                                      | Description                                                                                                                                                          |
| --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Functional Specifications](functional-specifications.md) | Policy model, stage modes, approver rule types, context semantics, skip rules, request lifecycle state machine, webhook contract (signature, retry schedule), PII / security posture, FAQ |
| [API Reference](api-reference.md)                         | REST API endpoints rendered live from OpenAPI 3.1 — request/response shapes, status codes, error-code catalog                                                        |
| [Technical Architecture](technical-architecture.md)       | Why this design over alternatives (Camunda, polling, multi-tenant), scalability model, delivery guarantees, engine state machine, approver-resolution caching        |
| [Deployment](deployment.md)                               | Local dev with Docker Compose, Helm chart install, configuration reference, Keycloak prerequisites, operational runbook, security considerations                     |
| [Testing](testing.md)                                     | Pytest smoke tests (hermetic, in-memory SQLite), test strategy, sample payloads                                                                                      |

## Versions

| Helm Chart Version                                         | Docker Image                    | Date        | Comments            |
| ---------------------------------------------------------- | ------------------------------- | ----------- | ------------------- |
| [0.0.0-develop](https://github.com/OpenG2P/awe/tree/develop) | `openg2p/openg2p-awe:develop` | in progress | Active development  |

## Source code

* GitHub: [https://github.com/OpenG2P/awe](https://github.com/OpenG2P/awe)

## Technology stack

| Component        | Choice                   | License                         |
| ---------------- | ------------------------ | ------------------------------- |
| Language         | Python 3.11+             | PSF License (permissive)        |
| Web Framework    | FastAPI                  | MIT                             |
| ASGI Server      | Uvicorn                  | BSD-3-Clause                    |
| DB Driver        | asyncpg                  | Apache 2.0                      |
| ORM              | SQLAlchemy 2.x (async)   | MIT                             |
| Config           | Pydantic Settings        | MIT                             |
| Auth             | Keycloak OIDC (JWT/JWKS) | Apache 2.0                      |
| Rule engine      | JSONLogic                | MIT                             |
| Admin UI         | React + Vite + TS        | MIT                             |
| Database         | PostgreSQL               | PostgreSQL License (permissive) |
| Deployment       | Kubernetes + Helm        | Apache 2.0                      |

All components use **permissive open-source licenses**. No copyleft (GPL)
dependencies.
