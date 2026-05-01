---
description: >-
  A centralised audit-event service for OpenG2P. Accepts structured audit events
  over HTTP, buffers through Kafka, and persists them to a partitioned
  PostgreSQL table for long-term retention and forensi
---

# Audit Manager

## Overview

The Audit Manager is the authoritative record of _who did what, when, and whether it succeeded_ across the OpenG2P stack — logins, permission checks, beneficiary updates, payment approvals, admin actions, system reversals, and more. It is **not** a replacement for application logs; its audits are **few, structured, long-lived, and authoritative** — designed so that investigators can reconstruct a clean timeline of every action that touched sensitive social-protection data.

It is built with **FastAPI**, uses **Kafka** as a durable buffer, and **PostgreSQL** (monthly-partitioned) for persistent storage. Designed for **horizontal scaling on Kubernetes**.

### Key capabilities

* **Callers are never blocked.** HTTP `202 Accepted` is returned the moment an event lands in an in-process queue — Kafka and Postgres latency are fully hidden from the caller.
* **CloudEvents-compliant** — every event follows the CNCF CloudEvents 1.0 envelope. Services in any language can emit by POSTing JSON.
* **Horizontally scalable** — every replica runs both ingest and consumer, coordinated automatically via Kafka consumer groups.
* **No runtime coupling** — if Kafka is slow or Postgres is down, callers still get `202`. Events pile up in Kafka's durable log and drain when downstream recovers.
* **At-least-once delivery + idempotent inserts** — replays are safe; no duplicate rows.
* **Long retention made cheap** — `audit_events` is range-partitioned by month. Dropping retired partitions is effectively instant.

## Design at a glance

```
┌──────────────────────┐
│  OpenG2P services    │   (FastAPI services, Odoo modules, CLI tools,
│  and external tools  │    external webhooks, third-party integrations)
└──────────┬───────────┘
           │  HTTP POST /v1/auditmanager/events     (returns 202 immediately)
           ▼
┌──────────────────────────────────────────────────────────────────┐
│              openg2p-audit-manager  (horizontally scaled)        │
│                                                                  │
│   FastAPI ingest                                                 │
│     │                                                            │
│     ▼                                                            │
│   asyncio.Queue (bounded — 503 on overflow, never silent drop)   │
│     │                                                            │
│     ▼                                                            │
│   Kafka producer (aiokafka, batched, keyed by subject)           │
│     │                                                            │
│     ▼                                                            │
│   ┌──────────────────────────────────────────────┐               │
│   │ Kafka topic:  openg2p.audit.events  (12 parts)│◄─────────┐   │
│   └──────────────────────────────────────────────┘          │   │
│     │                                                       │   │
│     ▼                                                       │   │
│   Kafka consumer (same service, same process)               │   │
│     │                                                       │   │
│     ▼                                                       │   │
│   Batched INSERT ... ON CONFLICT DO NOTHING                 │   │
│     │                                                       │   │
└─────┼───────────────────────────────────────────────────────┼───┘
      ▼                                                       │
┌──────────────────────────┐             Bad message ─────────┘
│  PostgreSQL              │             → openg2p.audit.dlq
│    audit_events          │
│    (partitioned by month,│
│     7-year retention)    │
└──────────────────────────┘
```

## Detailed documentation

| Page                                                      | Description                                                                                                                                                                                                             |
| --------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Functional Specifications](functional-specifications.md) | Event schema (CloudEvents envelope, `data` block, actor/resource shape), mapping to DB columns, how to emit audit events from API calls with 3 examples and a middleware snippet, naming conventions, PII handling, FAQ |
| [API Reference](api-reference.md)                         | REST API endpoints rendered live from OpenAPI 3.1 — request/response shapes, status codes, error-code catalog                                                                                                           |
| [Technical Architecture](technical-architecture.md)       | Why this design was chosen over alternatives, scalability model, reliability & delivery guarantees, partitioning strategy                                                                                               |
| [Deployment](deployment.md)                               | Local dev with Docker Compose, Helm chart install, configuration reference, operational runbook, security considerations                                                                                                |
| [Testing](testing.md)                                     | Unit tests, smoke test, load test, Postman collection, sample events                                                                                                                                                    |
| [Integration with Registry](integration-with-registry/)   | How OpenG2P services emit audit events to the Audit Manager. Includes a complete local-install guide for the Registry Staff Portal API as the reference integration.                                                    |

## Versions

| Helm Chart Version                                                     | Docker Image                            | Date        | Comments           |
| ---------------------------------------------------------------------- | --------------------------------------- | ----------- | ------------------ |
| [0.0.0-develop](https://github.com/OpenG2P/audit-manager/tree/develop) | `openg2p/openg2p-audit-manager:develop` | in progress | Active development |

## Source code

* GitHub: [https://github.com/OpenG2P/audit-manager](https://github.com/OpenG2P/audit-manager)

## Technology stack

| Component      | Choice                 | License                         |
| -------------- | ---------------------- | ------------------------------- |
| Language       | Python 3.11+           | PSF License (permissive)        |
| Web Framework  | FastAPI                | MIT                             |
| ASGI Server    | Uvicorn                | BSD-3-Clause                    |
| Kafka Client   | aiokafka               | Apache 2.0                      |
| DB Driver      | asyncpg                | Apache 2.0                      |
| ORM            | SQLAlchemy 2.x (async) | MIT                             |
| Config         | Pydantic Settings      | MIT                             |
| Event envelope | CloudEvents 1.0 (CNCF) | Apache 2.0                      |
| Message bus    | Apache Kafka           | Apache 2.0                      |
| Database       | PostgreSQL             | PostgreSQL License (permissive) |
| Deployment     | Kubernetes + Helm      | Apache 2.0                      |

All components use **permissive open-source licenses**. No copyleft (GPL) dependencies.
