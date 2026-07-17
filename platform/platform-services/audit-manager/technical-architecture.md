---
description: >-
  Design choices behind the Audit Manager — why each alternative was rejected,
  scalability model, reliability & delivery guarantees, and the partitioning /
  retention strategy.
---

# Technical Architecture

## Why this design

We deliberately chose this shape over several simpler alternatives. Each
section below explains what we rejected and why.

### Why a dedicated audit service and not just structured application logs?

Logs and audits have fundamentally different requirements:

| Concern        | Application logs  | Audit events               |
| -------------- | ----------------- | -------------------------- |
| Volume         | High, noisy       | Lower, signal              |
| Retention      | Days to weeks     | Years (compliance)         |
| Mutability     | Rotated, deleted  | Append-only, forensic      |
| Access         | Developers & ops  | Compliance & investigators |
| Schema         | Free-form strings | Strict, typed              |
| Loss tolerance | Some loss OK      | Loss is a serious incident |

Mixing the two produces bad outcomes on both sides: audits get lost in the
log pipeline's noise and retention policies, and logs become bloated and
slow because every service dumps structured business events into them.

### Why HTTP and not a shared Python library that publishes directly to Kafka?

The library approach couples every emitter to Python (and to the specific
async runtime). OpenG2P services include **Odoo** (Python, but its own
environment and ORM), plus potential non-Python components, webhooks from
external systems, CLI tools, and ad-hoc scripts. A library-only approach
would force every integration to solve Python version / dependency
problems.

HTTP is the universal integration surface. Every language speaks it; every
system can call it; every developer knows how to test it with `curl`.

The trade-off is an extra network hop compared to direct-to-Kafka, but
because the HTTP endpoint returns `202` from an in-memory queue in
sub-millisecond time, the caller-visible cost is negligible.

### Why Kafka in the middle and not direct HTTP → Postgres?

Three failure modes motivate Kafka:

1. **Postgres slowness or downtime** must not stop OpenG2P services from
   auditing their actions. Without a buffer, ingest pods would start
   returning `503` and callers would either drop events or block on the
   hot path.
2. **Horizontal scaling of writers** requires coordination. Kafka's
   consumer group protocol solves this for free — every replica joins the
   same group and is automatically assigned a subset of partitions with no
   custom code.
3. **Replayability**. If a schema migration or a bug corrupts the write
   path, events stay in Kafka and can be replayed. Without Kafka, a bad
   deploy loses events.

The cost is one extra dependency. OpenG2P already runs Kafka, so this cost
is zero here.

### Why not ClickHouse / OpenSearch / S3 instead of Postgres?

Considered and rejected for OpenG2P's scale:

* **Postgres** is already operated by every OpenG2P deployment. No new
  platform, no new backup story, no new expertise. OpenG2P's audit volume
  is typically in the millions-per-day range, not billions — Postgres
  handles this easily with monthly partitioning.
* **ClickHouse** is the right answer *at scale* (tens of billions of rows,
  aggressive analytical queries) but introduces a whole new database tier.
  If volume grows, the Kafka topic stays the same — only the consumer's
  sink changes. We can add ClickHouse later without touching producers.
* **OpenSearch / Elasticsearch** is great for free-text search but weaker
  for structured forensic queries, more expensive to operate, and harder
  to guarantee as authoritative storage.
* **S3 / object storage** is cheap for archival but painful for the kind
  of point queries (all events for beneficiary X) that investigators need.

The chosen design lets you **start on Postgres and migrate the sink later**
without changing a line of producer code.

### Why tables created at runtime instead of Alembic migrations?

Matches the OpenG2P convention established by
[openg2p/id-generator](https://github.com/OpenG2P/id-generator): Helm runs
`postgres-init` to create the DB and user, the service creates its own
tables and indexes at startup with `CREATE TABLE IF NOT EXISTS`.

For a service whose schema is essentially a single partitioned table with
ongoing partition maintenance, Alembic adds ceremony without benefit.
Schema evolution is handled inside `src/audit_manager/models.py` — future
migrations (e.g. a new index) can be added there as idempotent DDL.

### Why one service rather than separate ingest/consumer/query services?

For OpenG2P's scale, operational simplicity beats premature separation.

One codebase, one image, one Helm chart, one set of metrics. Every replica
does ingest and consumer work concurrently; the Kafka consumer group
handles coordination. A query API, if needed, can be added later as a
separate deployable (different auth boundary) — the audit data model
doesn't change.

## Scalability

### Scaling model

Every pod runs both sides of the pipeline:

* **HTTP ingest** — stateless. Kubernetes Service round-robins across
  pods. Adding pods linearly increases ingest capacity.
* **Kafka consumer** — coordinated via consumer group
  `openg2p-audit-consumer`. Kafka auto-assigns partitions to group members
  and rebalances on pod changes. No custom coordination code.

### Partition count bounds consumer parallelism

The Kafka topic has a fixed partition count (default 12). That number is
the ceiling on concurrent consumers — additional pods beyond
`partition_count` do ingest work but sit idle on the consumer side. Keep
`HPA.maxReplicas ≤ partitions`.

Partition count can be **increased** later (`kafka-topics.sh --alter`),
never decreased. Twelve partitions is comfortable headroom for typical
OpenG2P volume.

### Horizontal Pod Autoscaler

Enabled by default, CPU-based (70% target, 2–12 replicas). For more
accurate scaling, consider adding a custom metric on **Kafka consumer
lag** via KEDA or a custom metrics adapter — CPU alone can lag behind a
traffic spike if the ingest path is very fast (which it is, by design).

### Capacity envelope (rough numbers)

With default settings on modest hardware (2 CPU / 512 MiB per pod):

* **HTTP ingest:** ~5–10k events/sec per pod before queuing becomes
  significant (the endpoint is doing nothing but pydantic validation and a
  queue put).
* **Consumer → Postgres:** ~2–5k rows/sec per partition consumer with
  batched inserts, dominated by Postgres write throughput.
* **Ceiling:** determined by Postgres, not by this service. A single
  Postgres instance with appropriate hardware handles tens of thousands of
  audit-event inserts per second sustained.

For higher sustained throughput, move the consumer sink to ClickHouse or
TimescaleDB compression — the service design doesn't change.

## Reliability & delivery guarantees

### What we promise

* **At-least-once delivery** from Kafka to Postgres.
* **Idempotent insert** on `(id, occurred_at)` — duplicate delivery
  produces no duplicate rows.
* **No ack-without-queue-slot** — HTTP callers get `503` under
  backpressure, never a silent drop.
* **Crash-safe persistence** — Kafka offsets are committed only after the
  Postgres transaction commits, so a crash between Kafka read and DB write
  results in re-delivery, not loss.

### What we do *not* promise

* **Durability across an ingest-pod crash between HTTP accept and Kafka
  produce.** The in-process queue is in memory. If a pod crashes with
  events still in its queue, those events are lost. Mitigations:
  * Run ≥2 replicas; a random crash affects only one pod's in-flight events.
  * For workloads where this tradeoff is unacceptable, replace the
    `asyncio.Queue` in `kafka/producer.py` with a local durable spool
    (SQLite WAL, BoltDB, or similar). The interface is unchanged — only
    the queue implementation swaps.
* **Strong delivery order across partitions.** Events are keyed by
  `subject` (falling back to `actor.id`), so all events for a given entity
  land on the same partition and are ordered. Cross-partition ordering is
  not guaranteed — which is correct for audits (each entity's timeline is
  consistent; global ordering is not meaningful).

### Failure modes

| Failure                                         | Behaviour                                                                                    |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------- |
| Kafka broker unreachable                        | Queue fills → 503 to callers; service alerts                                                 |
| Postgres down                                   | Consumer stops committing offsets; events stay in Kafka; consumer catches up when DB returns |
| Malformed event arrives                         | Rejected at HTTP layer with `400`                                                            |
| Malformed event already in Kafka (schema drift) | Logged, skipped, forwarded to `openg2p.audit.dlq`                                            |
| Consumer pod crash                              | Kafka rebalances partitions; uncommitted offsets redelivered                                 |
| HTTP pod crash mid-queue                        | In-memory events in that pod's queue are lost                                                |

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

The standard CloudEvents fields (id, source, type, time, subject, trace)
and the three core `data` fields (actor, action, outcome) plus `reason`
are **promoted to flat columns**. This keeps the common audit queries as
plain SQL — no JSON operators needed for 95% of investigation work.

`details` is a nullable JSONB column that carries only the event-type-specific
extras — the full `resource` object (with any attributes beyond type/id
like `amount`, `currency`, `beneficiary_id`, `program_id`), the
`changes[]` diff on updates, and `context{}` for bank codes, MFA methods,
approval levels, correlation ids. Plain logins that have no extras get
`details = NULL`.

We deliberately don't store a full copy of the CloudEvents envelope. The
promoted columns already capture every envelope field; `details` holds
what they don't. Kafka still carries the full CloudEvent, so forensic
replay is possible from the topic if ever needed.

**Indexes** are defined on the parent table and propagated automatically
to every monthly child partition by Postgres:

| Index                                                  | Used by                                                                            |
| ------------------------------------------------------ | ---------------------------------------------------------------------------------- |
| **PRIMARY KEY (`id`, `occurred_at`)**                  | Point lookups by event id; also the dedup key for the consumer's idempotent `INSERT ... ON CONFLICT DO NOTHING`. |
| `(occurred_at DESC)`                                   | Time-range scans (e.g. retention sweeps, "events in the last hour").               |
| `(actor_id, occurred_at DESC)`                         | "Show me everything actor X did" — primary forensic query.                         |
| `(resource_type, resource_id, occurred_at DESC)`       | "Show me everything that happened to beneficiary Y / payment Z".                   |
| `(type, occurred_at DESC)`                             | Filter or count by CloudEvents type — e.g. "all `*.created` calls last week".      |
| `(trace_id) WHERE trace_id IS NOT NULL`                | Cross-system correlation via the W3C `traceparent` header.                         |

These five indexes plus the primary key cover every query pattern in the
[Operational runbook](deployment.md#operational-runbook) without further
tuning. They're applied at startup via `CREATE INDEX IF NOT EXISTS`, so
existing deployments inherit them on the next pod restart.

#### Indexes deliberately NOT added (avoid premature optimization)

| Could-be index                                         | Why we skip it                                                                                                                                                              |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `(outcome, occurred_at DESC)`                          | `outcome` has only three values; Postgres typically does a Bitmap Index Scan via `(occurred_at)` plus an in-memory filter. Add only if "all denied events ever" becomes hot *without* a tight time window. |
| GIN expression on `details->'actor'->>'session_id'`    | Login / session queries already filter by `actor_id` first, which hits the existing actor index and prunes 99 % of rows. Worth adding only if you ever query session_id *across all actors*. |

If a real query plan turns up a slow scan, run `EXPLAIN ANALYZE`. Add a
new index then, in [`src/audit_manager/models.py`](https://gitlab.com/openg2p/audit-manager/-/blob/develop/src/audit_manager/models.py)
under `_PARENT_INDEXES` — it's `CREATE INDEX IF NOT EXISTS`, so the next
service restart picks it up across every existing partition.

### Partition maintenance

A background loop (every hour by default) runs inside the service and:

1. Creates monthly partitions for the current month and the next N-1
   months (default N = 3, so 3 months of headroom at all times).
2. Drops partitions older than the retention window (default 7 years,
   settable to 0 to disable).

Dropping a monthly partition is effectively instant (no row-by-row
delete), making long retention cheap in both storage and operational
effort.

### Why partition by month

* **Simple mental model** for investigators (`audit_events_2026_04`).
* **Fast retention enforcement** — `DROP TABLE` rather than mass `DELETE`.
* **Query pruning** — Postgres restricts scans to relevant partitions when
  queries include an `occurred_at` filter.
* **Compression-ready** — if you later adopt TimescaleDB or pg\_partman,
  the partition layout is already compatible.
