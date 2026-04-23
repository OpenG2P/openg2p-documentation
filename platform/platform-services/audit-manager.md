# OpenG2P Audit Manager

A centralised audit-event service for OpenG2P. Accepts structured audit events
from any OpenG2P service (FastAPI, Odoo, external/webhook sources) over HTTP,
buffers them through Kafka, and persists them to a partitioned PostgreSQL
table for long-term retention and forensic querying.

Audit events are **not application logs** (INFO/ERROR) — they are the
authoritative record of *who did what, when, and whether it succeeded*:
logins, permission checks, beneficiary updates, payment approvals, admin
actions, system reversals, and so on. This service exists so those records
cannot be lost, cannot be rewritten, and cannot be confused with diagnostic
logging.

---

## Table of contents

- [Why this service exists](#why-this-service-exists)
- [Design at a glance](#design-at-a-glance)
- [Why this design](#why-this-design)
- [Event schema](#event-schema)
- [API](#api)
- [Scalability](#scalability)
- [Reliability & delivery guarantees](#reliability--delivery-guarantees)
- [Retention & partitioning](#retention--partitioning)
- [Local development](#local-development)
- [Testing](#testing)
- [Deployment](#deployment)
- [Configuration reference](#configuration-reference)
- [Operational runbook](#operational-runbook)
- [Security considerations](#security-considerations)
- [FAQ](#faq)

---

## Why this service exists

OpenG2P deployments process sensitive social-protection data: beneficiary
records, eligibility decisions, payment disbursements, account modifications.
Auditability is a regulatory and operational necessity — when something goes
wrong (a missing payment, a contested eligibility decision, a possible fraud
case), investigators need a clean, tamper-evident timeline of every action
that touched the data.

Application logs are not a substitute. They are noisy, unstructured,
short-lived, and typically not treated as evidence. Audit events are the
opposite: **few**, **structured**, **long-lived**, and **authoritative**.

This service provides a single ingestion point and a single store for them
across the whole OpenG2P stack.

---

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

**Three key properties:**

1. **Callers are never blocked.** HTTP `202 Accepted` is returned the
   moment an event lands in an in-process queue. Kafka and Postgres latency
   are fully hidden from callers.
2. **Horizontally scalable.** Every replica runs both ingest (stateless)
   and consumer (coordinated via Kafka consumer group). Add pods to scale.
3. **No runtime coupling.** If Kafka is slow or Postgres is down, the
   caller still gets `202`. Events pile up in Kafka's durable log and drain
   when downstream recovers.

---

## Why this design

We deliberately chose this shape over several simpler alternatives.
Each section below explains what we rejected and why.

### Why a dedicated audit service and not just structured application logs?

Logs and audits have fundamentally different requirements:

| Concern            | Application logs         | Audit events                          |
| ------------------ | ------------------------ | ------------------------------------- |
| Volume             | High, noisy              | Lower, signal                         |
| Retention          | Days to weeks            | Years (compliance)                    |
| Mutability         | Rotated, deleted         | Append-only, forensic                 |
| Access             | Developers & ops         | Compliance & investigators            |
| Schema             | Free-form strings        | Strict, typed                         |
| Loss tolerance     | Some loss OK             | Loss is a serious incident            |

Mixing the two produces bad outcomes on both sides: audits get lost in the
log pipeline's noise and retention policies, and logs become bloated and
slow because every service dumps structured business events into them.

### Why HTTP and not a shared Python library that publishes directly to Kafka?

The library approach couples every emitter to Python (and to the specific
async runtime). OpenG2P services include **Odoo** (Python, but its own
environment and ORM), plus potential non-Python components, webhooks from
external systems, CLI tools, and ad-hoc scripts. A library-only approach
would force every integration to solve Python version / dependency problems.

HTTP is the universal integration surface. Every language speaks it; every
system can call it; every developer knows how to test it with `curl`.

The trade-off is an extra network hop compared to direct-to-Kafka, but
because the HTTP endpoint returns `202` from an in-memory queue in
sub-millisecond time, the caller-visible cost is negligible.

### Why Kafka in the middle and not direct HTTP → Postgres?

Three failure modes motivate Kafka:

1. **Postgres slowness or downtime** must not stop OpenG2P services from
   auditing their actions. Without a buffer, ingest pods would start returning
   `503` and callers would either drop events or block on the hot path.
2. **Horizontal scaling of writers** requires coordination. Kafka's consumer
   group protocol solves this for free — every replica joins the same group
   and is automatically assigned a subset of partitions with no custom code.
3. **Replayability**. If a schema migration or a bug corrupts the write
   path, events stay in Kafka and can be replayed. Without Kafka, a bad
   deploy loses events.

The cost is one extra dependency. OpenG2P already runs Kafka, so this cost
is zero here.

### Why not ClickHouse / OpenSearch / S3 instead of Postgres?

Considered and rejected for OpenG2P's scale:

- **Postgres** is already operated by every OpenG2P deployment. No new
  platform, no new backup story, no new expertise. OpenG2P's audit volume is
  typically in the millions-per-day range, not billions — Postgres handles
  this easily with monthly partitioning.
- **ClickHouse** is the right answer *at scale* (tens of billions of rows,
  aggressive analytical queries) but introduces a whole new database tier.
  If volume grows, the Kafka topic stays the same — only the consumer's
  sink changes. We can add ClickHouse later without touching producers.
- **OpenSearch / Elasticsearch** is great for free-text search but weaker
  for structured forensic queries, more expensive to operate, and harder to
  guarantee as authoritative storage.
- **S3 / object storage** is cheap for archival but painful for the kind of
  point queries (all events for beneficiary X) that investigators need.

The chosen design lets you **start on Postgres and migrate the sink later**
without changing a line of producer code.

### Why tables created at runtime instead of Alembic migrations?

Matches the OpenG2P convention established by
[openg2p/id-generator](https://github.com/OpenG2P/id-generator): Helm runs
`postgres-init` to create the DB and user, the service creates its own
tables and indexes at startup with `CREATE TABLE IF NOT EXISTS`.

For a service whose schema is essentially a single partitioned table with
ongoing partition maintenance, Alembic adds ceremony without benefit. Schema
evolution is handled inside `src/audit_manager/models.py` — future
migrations (e.g. a new index) can be added there as idempotent DDL.

### Why one service rather than separate ingest/consumer/query services?

For OpenG2P's scale, operational simplicity beats premature separation.

One codebase, one image, one Helm chart, one set of metrics. Every replica
does ingest and consumer work concurrently; the Kafka consumer group handles
coordination. A query API, if needed, can be added later as a separate
deployable (different auth boundary) — the audit data model doesn't change.

---

## Event schema

All events follow the **CloudEvents v1.0** specification
(https://cloudevents.io/ — CNCF graduated standard). The envelope is
canonical across all OpenG2P services; the `data` block is event-type
specific.

### Envelope (required attributes)

| Field             | Type     | Purpose                                                   |
| ----------------- | -------- | --------------------------------------------------------- |
| `specversion`     | string   | Always `"1.0"`                                            |
| `id`              | string   | Unique event id (ULID or UUIDv7 recommended); dedup key   |
| `source`          | string   | Emitting service, e.g. `/openg2p/beneficiary-service`     |
| `type`            | string   | Reverse-DNS event type, e.g. `org.openg2p.auth.login`     |
| `time`            | RFC3339  | When the event occurred, as seen by the emitter           |
| `datacontenttype` | string   | Always `application/json`                                 |
| `data`            | object   | OpenG2P-specific payload (see below)                      |

Optional top-level fields:

| Field         | Purpose                                                   |
| ------------- | --------------------------------------------------------- |
| `subject`     | Primary object acted on, e.g. `beneficiary/b_1029384756`  |
| `traceparent` | W3C trace-context header for correlating with logs/traces |

### `data` block — OpenG2P conventions

Three sub-fields are **always required**, giving every event a consistent
"who did what, and did it work" triple:

| Field     | Type     | Values                                               |
| --------- | -------- | ---------------------------------------------------- |
| `actor`   | object   | Who triggered the event (user/system/service)        |
| `action`  | string   | Verb: `login`, `read`, `update`, `approve`, ...      |
| `outcome` | enum     | `success` \| `failure` \| `denied`                   |

One sub-field is **strongly recommended when applicable**:

| Field      | Type   | Purpose                                           |
| ---------- | ------ | ------------------------------------------------- |
| `resource` | object | The object acted on, e.g. beneficiary, payment    |

Anything else (`changes`, `reason`, `context`, domain-specific fields)
lives in `data` as event-type-specific attributes.

### Mapping from CloudEvents to Postgres columns

The service validates the full CloudEvents input and then persists a flat
row. Some envelope fields are validated but **not stored** (they don't add
signal to a forensic query). The `audit_events` table has exactly 15
columns — every input field either maps to one of them or is dropped.

| CloudEvents input field       | Stored as (DB column) | Notes                                                          |
| ----------------------------- | --------------------- | -------------------------------------------------------------- |
| `specversion`                 | — (dropped)           | Validated (`"1.0"`), not stored — same for every row.          |
| `datacontenttype`             | — (dropped)           | Always `application/json` — no information to preserve.        |
| `id`                          | `id`                  | Primary key (together with `occurred_at`) — dedup on replay.   |
| `source`                      | `source`              | Which service emitted the event.                               |
| `type`                        | `type`                | Reverse-DNS event type.                                        |
| `time`                        | `occurred_at`         | Renamed on store — consistent with `ingested_at` naming.       |
| `subject`                     | `subject`             | Primary object acted on; nullable.                             |
| `traceparent`                 | `trace_id`            | Only the 16-byte trace id is extracted from the W3C header.    |
| `data.actor.type`             | `actor_type`          | `user` \| `system` \| `service` \| `anonymous`.                |
| `data.actor.id`               | `actor_id`            | Stable actor identifier.                                       |
| `data.actor.*` (other fields) | `details.actor.*`     | Remaining actor fields (name, roles, ip, session_id) preserved under `details`. |
| `data.action`                 | `action`              | Verb.                                                          |
| `data.outcome`                | `outcome`             | `success` \| `failure` \| `denied`.                            |
| `data.reason`                 | `reason`              | Promoted — common filter for failure / denied outcomes.        |
| `data.resource.type`          | `resource_type`       | Nullable (login events have no resource).                      |
| `data.resource.id`            | `resource_id`         | Nullable.                                                      |
| `data.resource.*` (extras)    | `details.resource.*`  | Remaining resource attributes (amount, currency, program_id, etc.). |
| `data.changes` / `data.context` / other event-specific fields | `details.*`           | Event-type-specific extras carried in `details` JSONB.         |
| — (server-assigned)           | `ingested_at`         | `DEFAULT now()` at insert time; useful for "recent arrivals" queries distinct from `occurred_at`. |

**Columns in the DB that aren't input fields:** only `ingested_at`, set by
Postgres `DEFAULT now()` at insert time.

**Input fields that don't produce a column:** `specversion`, `datacontenttype`
(both are always the same value and carry no forensic signal).

### Actor shape

```json
{
  "type": "user",              // "user" | "system" | "service" | "anonymous"
  "id": "u_4421",              // stable identifier
  "name": "fatima.k",          // optional display name
  "roles": ["program.operator"],
  "ip": "10.2.14.88",
  "session_id": "sess_93ka..."
}
```

### Example events

**Login (no data changed):**
```json
{
  "specversion": "1.0",
  "id": "01HXQ9R...",
  "source": "/openg2p/auth",
  "type": "org.openg2p.auth.login",
  "time": "2026-04-22T14:03:21Z",
  "data": {
    "actor":   { "type": "user", "id": "u_4421", "name": "fatima.k" },
    "action":  "login",
    "outcome": "success",
    "context": { "ip": "10.2.14.88", "mfa": "totp" }
  }
}
```

**Beneficiary update with diff:**
```json
{
  "specversion": "1.0",
  "id": "01HXQ9S...",
  "source": "/openg2p/beneficiary-service",
  "type": "org.openg2p.beneficiary.updated",
  "subject": "beneficiary/b_1029384756",
  "time": "2026-04-22T14:05:12Z",
  "data": {
    "actor":    { "type": "user", "id": "u_4421" },
    "action":   "update",
    "outcome":  "success",
    "resource": { "type": "beneficiary", "id": "b_1029384756" },
    "changes":  [
      { "field": "phone", "from": "+91...21", "to": "+91...88" }
    ]
  }
}
```

**System-initiated payment reversal:**
```json
{
  "specversion": "1.0",
  "id": "01HXQ9T...",
  "source": "/openg2p/payment-recon",
  "type": "org.openg2p.payment.reversed",
  "time": "2026-04-22T02:00:00Z",
  "data": {
    "actor":    { "type": "system", "id": "reconciliation-job" },
    "action":   "reverse",
    "outcome":  "success",
    "resource": { "type": "payment", "id": "pay_55231" },
    "reason":   "bank_rejection",
    "context":  { "job_run_id": "r_20260422_0200", "bank_code": "E102" }
  }
}
```

### Naming conventions for `type`

- Lowercase, reverse-DNS: `org.openg2p.<domain>.<past_participle_verb>`
- One type = one fixed `data` shape. To change the shape, bump the type
  (`org.openg2p.beneficiary.updated.v2`). Never repurpose a type.
- Canonical verbs: `created`, `updated`, `deleted`, `viewed`, `login`,
  `logout`, `login_failed`, `approved`, `rejected`, `reversed`, `enrolled`.

### PII handling

- **Never** put PII in `type`, `subject`, `actor.id` prefix, or any other
  field that is indexed or logged.
- PII belongs inside `data.resource` / `data.changes`, where it can be
  redacted or encrypted per field before emit.
- Event-type-specific extras (diffs, amounts, context) are stored in the
  `details` JSONB column. Access to `details` should be restricted in
  production since it may carry PII from `changes[]`.

---

## API

Base path: `/v1/auditmanager/`

### `POST /events`

Ingest a single CloudEvent. Returns `202 Accepted` synchronously after the
event is enqueued — **does not wait for Kafka or Postgres.**

Request body: a single CloudEvent JSON object (see schema above).

Responses:

| Status | Meaning                                                          |
| ------ | ---------------------------------------------------------------- |
| `202`  | Accepted into the ingest queue. The `id` is echoed in response.  |
| `400`  | Malformed or schema-invalid event.                               |
| `503`  | Ingest queue full (backpressure) **or** service not ready.       |

### `POST /events/batch`

Ingest up to `ingest.max_batch_size` events in one request. Same 202
semantics, returns the list of accepted ids.

### `GET /health`

Liveness + readiness. Returns `200 {"status": "UP"}` when:
1. Startup is complete
2. Postgres is reachable

Returns `503` otherwise.

### `GET /version`

Build metadata — service version, git commit, build time.

### `GET /config`

Non-sensitive effective configuration, useful for diagnostics.

### `GET /docs` / `GET /redoc` / `GET /openapi.json`

Served at `/v1/auditmanager/docs`, `/v1/auditmanager/redoc`, and
`/v1/auditmanager/openapi.json` so they sit under the same Istio
VirtualService prefix as the rest of the API.

Standard FastAPI-provided OpenAPI surfaces.

---

## Scalability

### Scaling model

Every pod runs both sides of the pipeline:

- **HTTP ingest** — stateless. Kubernetes Service round-robins across pods.
  Adding pods linearly increases ingest capacity.
- **Kafka consumer** — coordinated via consumer group
  `openg2p-audit-consumer`. Kafka auto-assigns partitions to group members
  and rebalances on pod changes. No custom coordination code.

### Partition count bounds consumer parallelism

The Kafka topic has a fixed partition count (default 12). That number is the
ceiling on concurrent consumers — additional pods beyond `partition_count`
do ingest work but sit idle on the consumer side. Keep
`HPA.maxReplicas ≤ partitions`.

Partition count can be **increased** later (`kafka-topics.sh --alter`),
never decreased. Twelve partitions is comfortable headroom for typical
OpenG2P volume.

### Horizontal Pod Autoscaler

Enabled by default, CPU-based (70% target, 2–12 replicas). For
more accurate scaling, consider adding a custom metric on **Kafka consumer
lag** via KEDA or a custom metrics adapter — CPU alone can lag behind a
traffic spike if the ingest path is very fast (which it is, by design).

### Capacity envelope (rough numbers)

With default settings on modest hardware (2 CPU / 512 MiB per pod):

- **HTTP ingest:** ~5–10k events/sec per pod before queuing becomes
  significant (the endpoint is doing nothing but pydantic validation and a
  queue put).
- **Consumer → Postgres:** ~2–5k rows/sec per partition consumer with
  batched inserts, dominated by Postgres write throughput.
- **Ceiling:** determined by Postgres, not by this service. A single
  Postgres instance with appropriate hardware handles tens of thousands of
  audit-event inserts per second sustained.

For higher sustained throughput, move the consumer sink to ClickHouse or
TimescaleDB compression — the service design doesn't change.

---

## Reliability & delivery guarantees

### What we promise

- **At-least-once delivery** from Kafka to Postgres.
- **Idempotent insert** on `(id, occurred_at)` — duplicate delivery produces
  no duplicate rows.
- **No ack-without-queue-slot** — HTTP callers get `503` under backpressure,
  never a silent drop.
- **Crash-safe persistence** — Kafka offsets are committed only after the
  Postgres transaction commits, so a crash between Kafka read and DB write
  results in re-delivery, not loss.

### What we do *not* promise

- **Durability across an ingest-pod crash between HTTP accept and Kafka
  produce.** The in-process queue is in memory. If a pod crashes with
  events still in its queue, those events are lost. Mitigations:
  - Run ≥2 replicas; a random crash affects only one pod's in-flight
    events.
  - For workloads where this tradeoff is unacceptable, replace the
    `asyncio.Queue` in `kafka/producer.py` with a local durable spool
    (SQLite WAL, BoltDB, or similar). The interface is unchanged — only
    the queue implementation swaps.
- **Strong delivery order across partitions.** Events are keyed by
  `subject` (falling back to `actor.id`), so all events for a given
  entity land on the same partition and are ordered. Cross-partition
  ordering is not guaranteed — which is correct for audits (each entity's
  timeline is consistent; global ordering is not meaningful).

### Failure modes

| Failure                      | Behaviour                                             |
| ---------------------------- | ----------------------------------------------------- |
| Kafka broker unreachable     | Queue fills → 503 to callers; service alerts         |
| Postgres down                | Consumer stops committing offsets; events stay in Kafka; consumer catches up when DB returns |
| Malformed event arrives      | Rejected at HTTP layer with `400`                    |
| Malformed event already in Kafka (schema drift) | Logged, skipped, forwarded to `openg2p.audit.dlq` |
| Consumer pod crash           | Kafka rebalances partitions; uncommitted offsets redelivered |
| HTTP pod crash mid-queue     | In-memory events in that pod's queue are lost        |

---

## Retention & partitioning

The `audit_events` table is range-partitioned on `occurred_at` per month:

```sql
CREATE TABLE audit_events (
    id             TEXT        NOT NULL,
    occurred_at    TIMESTAMPTZ NOT NULL,
    ingested_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
    source         TEXT        NOT NULL,
    type           TEXT        NOT NULL,
    subject        TEXT,
    actor_type     TEXT        NOT NULL,
    actor_id       TEXT        NOT NULL,
    resource_type  TEXT,
    resource_id    TEXT,
    action         TEXT        NOT NULL,
    outcome        TEXT        NOT NULL,
    reason         TEXT,
    trace_id       TEXT,
    details        JSONB,
    PRIMARY KEY (id, occurred_at)
) PARTITION BY RANGE (occurred_at);
```

**Design choice — flat columns + nullable `details` JSONB.**

The standard CloudEvents fields (id, source, type, time, subject, trace) and
the three core `data` fields (actor, action, outcome) plus `reason` are
**promoted to flat columns**. This keeps the common audit queries as plain
SQL — no JSON operators needed for 95% of investigation work.

`details` is a nullable JSONB column that carries only the event-type-specific
extras — the full `resource` object (with any attributes beyond type/id like
`amount`, `currency`, `beneficiary_id`, `program_id`), the `changes[]` diff
on updates, and `context{}` for bank codes, MFA methods, approval levels,
correlation ids. Plain logins that have no extras get `details = NULL`.

We deliberately don't store a full copy of the CloudEvents envelope. The
promoted columns already capture every envelope field; `details` holds what
they don't. Kafka still carries the full CloudEvent, so forensic replay is
possible from the topic if ever needed.

**Indexes** (propagated automatically to child partitions):

- `(occurred_at DESC)` — time-range scans
- `(actor_id, occurred_at DESC)` — everything a given actor did
- `(resource_type, resource_id, occurred_at DESC)` — everything that happened to a given resource
- `(type, occurred_at DESC)` — counts / traces by event type
- `(trace_id) WHERE trace_id IS NOT NULL` — cross-system correlation

### Partition maintenance

A background loop (every hour by default) runs inside the service and:

1. Creates monthly partitions for the current month and the next N-1 months
   (default N = 3, so 3 months of headroom at all times).
2. Drops partitions older than the retention window (default 7 years,
   settable to 0 to disable).

Dropping a monthly partition is effectively instant (no row-by-row delete),
making long retention cheap in both storage and operational effort.

### Why partition by month

- **Simple mental model** for investigators (`audit_events_2026_04`).
- **Fast retention enforcement** — `DROP TABLE` rather than mass `DELETE`.
- **Query pruning** — Postgres restricts scans to relevant partitions when
  queries include an `occurred_at` filter.
- **Compression-ready** — if you later adopt TimescaleDB or pg_partman, the
  partition layout is already compatible.

---

## Local development

### With Docker Compose (one command)

```bash
docker compose up --build
```

Starts Postgres, Kafka (KRaft single-node), and the audit-manager service.
After a few seconds:

- API:      http://localhost:8000/v1/auditmanager/
- Swagger:  http://localhost:8000/v1/auditmanager/docs
- Health:   http://localhost:8000/v1/auditmanager/health

### Smoke test

```bash
curl -sX POST http://localhost:8000/v1/auditmanager/events \
  -H 'content-type: application/json' -d '{
    "specversion": "1.0",
    "id": "demo-1",
    "source": "/demo",
    "type": "org.openg2p.auth.login",
    "time": "2026-04-22T14:03:21Z",
    "data": {
      "actor":   { "type": "user", "id": "u_1", "name": "demo" },
      "action":  "login",
      "outcome": "success"
    }
  }'
```

Expected: `202 Accepted` immediately. Within a few seconds the row appears in
Postgres:

```bash
docker compose exec postgres psql -U postgres -d auditmanager \
  -c "SELECT id, type, actor_id, outcome, occurred_at FROM audit_events ORDER BY ingested_at DESC LIMIT 5;"
```

### Running outside Docker

```bash
pip install -e .
export DB_HOST=localhost DB_NAME=auditmanager DB_USER=postgres DB_PASSWORD=postgres
export AUDIT_MANAGER__KAFKA__BOOTSTRAP_SERVERS=localhost:9092
uvicorn audit_manager.main:app --reload
```

---

## Testing

Three layers, each proving a different thing. Full details in
[`tests/README.md`](https://github.com/OpenG2P/audit-manager/blob/main/tests/README.md).

### 1. Unit tests — schema validation (no infra needed)

Sub-second, pure pydantic. Validates every sample event, enforces required
fields, covers enum constraints and the Postgres column mapping.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"
pytest tests/unit/ -v                # 28 tests
```

### 2. Smoke test — end-to-end against `docker compose`

Posts every sample event shape, posts the batch, triggers an expected 4xx,
waits for Kafka → Postgres settle, then queries Postgres to verify every
expected id landed. Also verifies idempotency (repost = no duplicate row).

```bash
docker compose up --build -d
tests/smoke.sh
```

Overrides: `AUDIT_URL`, `SETTLE_SECONDS`, `COMPOSE_PG_SERVICE`.

### 3. Load test — concurrent POSTs, no-drop verification

Sends N unique events with C concurrent workers, then confirms all N are in
Postgres.

```bash
N=1000 C=20 tests/load.sh
```

### Postman collection

Import [`tests/postman/OpenG2P-Audit-Manager.postman_collection.json`](https://github.com/OpenG2P/audit-manager/blob/main/tests/postman/OpenG2P-Audit-Manager.postman_collection.json)
into Postman, Bruno, or Insomnia. Folders:

- Service endpoints (`/v1/auditmanager/health`, `/v1/auditmanager/version`, `/v1/auditmanager/config`, `/v1/auditmanager/docs`)
- Single events — success paths (login, views, updates with diff, payment approve/reverse)
- Single events — failure / denied outcomes
- Batch ingestion
- Negative tests with assertions

Each request ships with test-script assertions (`202 Accepted`, expected
ids, 4xx on invalid). Use the **Runner** to fire the whole collection.

### Sample events

Nine JSON fixtures under [`tests/sample-events/`](https://github.com/OpenG2P/audit-manager/tree/main/tests/sample-events)
cover every realistic OpenG2P audit shape — reusable as `curl -d @file.json`:

```bash
curl -sX POST http://localhost:8000/v1/auditmanager/events \
  -H 'content-type: application/json' \
  --data-binary @tests/sample-events/04-beneficiary-updated.json
```

---

## Deployment

### Prerequisites

- A Kubernetes cluster with the OpenG2P `common` and `postgres-init` charts
  available (they are pulled from https://openg2p.github.io/openg2p-helm).
- A running Kafka cluster reachable from the target namespace.
- A PostgreSQL instance reachable from the target namespace.

### Install

```bash
helm repo add openg2p https://openg2p.github.io/openg2p-helm
helm repo update

helm install audit-manager openg2p/openg2p-audit-manager \
  -n openg2p --create-namespace \
  -f values-<env>.yaml
```

### Minimal per-environment values file

```yaml
# values-prod.yaml
global:
  auditManagerHostname: auditmanager.prod.openg2p.org
  postgresqlHost: commons-postgresql.database.svc.cluster.local
  kafkaBootstrapServers: "kafka-0.kafka.svc:9092,kafka-1.kafka.svc:9092,kafka-2.kafka.svc:9092"

auditManager:
  image:
    tag: "1.0.0"
  autoscaling:
    minReplicas: 3
    maxReplicas: 12
  topicInit:
    partitions: 12
    replicationFactor: 3
```

### What the chart provisions, in order

1. **`postgres-init`** subchart creates the `auditmanager` DB + user
   (Helm hook, weight 0).
2. **Kafka topic init Job** (`topicInit.enabled: true`, hook weight 10)
   creates `openg2p.audit.events` and `openg2p.audit.dlq` with the
   configured partitions, replication factor, and retention. Idempotent —
   creates if missing, grows partitions if below target.
3. **ConfigMap** rendering `config/config.yaml` from `auditManager.appConfig.*`.
4. **Deployment** with:
   - `postgres-checker` initContainer that blocks until the DB is reachable.
   - Main container running `uvicorn audit_manager.main:app`.
   - Startup / liveness / readiness probes on `/v1/auditmanager/health`.
   - Rolling update strategy.
5. **Service** (ClusterIP) + **Istio VirtualService** routing
   `/v1/auditmanager/` to the service.
6. **HorizontalPodAutoscaler** (CPU-based, 2–12 replicas by default).

### Kafka topic management alternatives

If topics are managed outside this chart (e.g. a Strimzi `KafkaTopic` CR or
a separate platform-level GitOps repo), set:

```yaml
auditManager:
  topicInit:
    enabled: false
```

---

## Configuration reference

All configuration is layered, highest priority first:

1. Environment variables (with `__` as nested key delimiter)
2. YAML config file at `$CONFIG_PATH` (default `/app/config/config.yaml` in
   the container)
3. Built-in defaults in `src/audit_manager/config.py`

### Environment variables

| Variable                                       | Purpose                              | Default         |
| ---------------------------------------------- | ------------------------------------ | --------------- |
| `DB_HOST` / `DB_PORT` / `DB_NAME`              | Postgres connection                  | localhost/5432/auditmanager |
| `DB_USER` / `DB_PASSWORD`                      | Postgres credentials                 | postgres/postgres (dev only) |
| `AUDIT_MANAGER__KAFKA__BOOTSTRAP_SERVERS`      | Kafka brokers                        | `kafka:9092`    |
| `AUDIT_MANAGER__KAFKA__TOPIC`                  | Audit events topic                   | `openg2p.audit.events` |
| `AUDIT_MANAGER__INGEST__QUEUE_MAX_SIZE`        | In-process queue bound               | `10000`         |
| `AUDIT_MANAGER__DATABASE__PARTITION_RETENTION_MONTHS` | Retention in months           | `84` (7 years)  |
| `CONFIG_PATH`                                  | YAML config path                     | `config/default.yaml` |
| `UVICORN_HOST` / `UVICORN_PORT` / `UVICORN_WORKERS` | Uvicorn server settings         | 0.0.0.0 / 8000 / 1 |
| `UVICORN_LOG_LEVEL`                            | Log level                            | `info`          |

### YAML config

See [`config/default.yaml`](https://github.com/OpenG2P/audit-manager/blob/main/config/default.yaml) for the full reference. Top-level keys:

- `audit_manager.ingest.*`  — queue size, batch limits
- `audit_manager.kafka.*`   — topic, DLQ, producer/consumer tuning
- `audit_manager.database.*` — partition maintenance knobs

### Helm values

See [`helm/openg2p-audit-manager/values.yaml`](https://github.com/OpenG2P/audit-manager/blob/main/helm/openg2p-audit-manager/values.yaml) and
[`helm/openg2p-audit-manager/questions.yaml`](https://github.com/OpenG2P/audit-manager/blob/main/helm/openg2p-audit-manager/questions.yaml) for
the full schema of user-facing values and their Rancher UI groupings.

---

## Operational runbook

### "Audit events are being rejected with 503"

Check in order:

1. `GET /v1/auditmanager/health` — if it returns 503, the service itself is
   unhealthy (startup incomplete or DB unreachable).
2. Pod logs for `Audit ingest queue full — backpressure` — indicates the
   in-process queue is full. Root causes, in order of likelihood:
   - Kafka is slow or unreachable. Check broker health.
   - Consumer is lagging, causing producer back-pressure (rare here —
     producer and consumer are independent).
   - Instantaneous traffic spike. Scale replicas or raise
     `ingest.queue_max_size`.

### "Consumer lag is growing"

1. Check Postgres health — most common cause.
2. Check consumer group:
   ```
   kafka-consumer-groups.sh --bootstrap-server <broker> \
     --group openg2p-audit-consumer --describe
   ```
3. If lag persists after Postgres recovers, increase replicas
   (up to partition count) or optimize Postgres (indexes, disk IO).

### "Schema-invalid events in Kafka"

Check the DLQ topic `openg2p.audit.dlq` and service logs. Common causes:

- Emitter sending pre-1.0 payloads
- Missing required fields (`actor`, `action`, `outcome`)
- Non-RFC3339 timestamps

The consumer drops malformed events so the main pipeline keeps flowing.
Fix the emitter, then optionally replay from the DLQ.

### "Need to investigate a specific incident"

Indexed query patterns:

```sql
-- Everything a specific actor did in a window
SELECT occurred_at, type, action, outcome, resource_type, resource_id
FROM audit_events
WHERE actor_id = 'u_4421'
  AND occurred_at >= '2026-04-01' AND occurred_at < '2026-05-01'
ORDER BY occurred_at;

-- Everything that happened to a specific resource
SELECT occurred_at, actor_id, action, outcome, reason
FROM audit_events
WHERE resource_type = 'beneficiary' AND resource_id = 'b_1029384756'
ORDER BY occurred_at;

-- All denied or failed events in the last 24h (uses flat `outcome` + `reason`)
SELECT occurred_at, actor_id, type, outcome, reason
FROM audit_events
WHERE outcome IN ('denied', 'failure')
  AND occurred_at > now() - interval '24 hours'
ORDER BY occurred_at DESC;

-- Correlate across services via trace id
SELECT occurred_at, source, type, action, outcome
FROM audit_events
WHERE trace_id = '4bf92f3577b34da6a3ce929d0e0e4736'
ORDER BY occurred_at;

-- Drill into structured extras — show field diffs for a beneficiary update
SELECT id, occurred_at, actor_id, details->'changes' AS changes
FROM audit_events
WHERE type = 'org.openg2p.beneficiary.updated'
  AND resource_id = 'b_1029384756'
ORDER BY occurred_at DESC;

-- All payments above 10k INR (uses details.resource.amount)
SELECT id, occurred_at, actor_id, details->'resource' AS resource
FROM audit_events
WHERE type = 'org.openg2p.payment.approved'
  AND (details->'resource'->>'currency') = 'INR'
  AND (details->'resource'->>'amount')::numeric > 10000
ORDER BY occurred_at DESC;
```

### "Need to grow the Kafka partition count"

The `topicInit` Job idempotently grows partitions on the next `helm upgrade`.
To trigger manually:

```bash
helm upgrade audit-manager openg2p/openg2p-audit-manager \
  -n openg2p -f values-<env>.yaml \
  --set auditManager.topicInit.partitions=24
```

Remember to raise `autoscaling.maxReplicas` accordingly.

### "Need to change retention"

Set `auditManager.appConfig.database.partitionRetentionMonths` and
`helm upgrade`. The partition maintainer picks it up on its next run
(hourly by default).

---

## Security considerations

- **Authentication:** not built in. Deploy behind Istio / an API gateway
  that enforces service-to-service auth (JWT, mTLS). Direct internet
  exposure of this service is not supported.
- **Authorization:** there is no per-caller authorization at the audit
  service. Any caller with network access can emit events. If that is a
  concern, require a signed JWT at the Istio layer.
- **PII:** see [PII handling](#pii-handling). The `details` JSONB column
  may carry structured PII (e.g. field diffs in `changes[]`); access to
  `details` should be restricted to compliance / investigators.
- **DB role:** the service's DB user needs only `CONNECT`, `USAGE`,
  `INSERT`, `SELECT` on its schema. A separate read-only role is
  recommended for investigators (no `INSERT` / `UPDATE` / `DELETE` — audits
  are append-only).
- **Tamper evidence:** this first release stores events as-is. If
  compliance requires cryptographic non-repudiation, a subsequent release
  can add hash-chaining at the sink (each row stores `prev_hash` and
  `hash(prev_hash || event)`).
- **Secret handling:** DB password comes from a Kubernetes Secret created
  by the `postgres-init` chart. Never baked into the image. `docs/` never
  contains configuration.

---

## FAQ

**Can I emit events from Odoo?**
Yes — Odoo makes an HTTP POST to `/v1/auditmanager/events`. Use Odoo's
`queue_job` (OCA) so the call is async and retried on transient failure.
The same CloudEvents payload works unchanged.

**What if my service is not Python?**
HTTP is the universal integration. Any language that can POST JSON works.
We may publish small SDKs later for convenience, but they are not required.

**Can I query the audit store from a UI?**
Not from this service. Audit data is intentionally not exposed via a UI in
this release; investigators query Postgres directly. A separate, read-only
`audit-query` service (different auth boundary) can be added when a real
need appears.

**What happens if I replay a Kafka message?**
Nothing user-visible. Inserts use `ON CONFLICT (id, occurred_at) DO NOTHING`
so duplicates are silently absorbed.

**Can I change the event schema for one type?**
No — treat schemas as immutable once in production. To evolve, create a
new type (`org.openg2p.beneficiary.updated.v2`). Old events stay queryable;
new consumers handle both. This keeps the forensic record honest.

**Does this service log the events it audits?**
No. It logs operational events (startup, shutdown, errors, DLQ). It does
not log the audit payloads themselves — those would duplicate the audit
store into the regular log pipeline, which is exactly what we're trying
to avoid.

---

## License

SPDX-License-Identifier: MPL-2.0

Part of the [OpenG2P](https://www.openg2p.org/) platform.
