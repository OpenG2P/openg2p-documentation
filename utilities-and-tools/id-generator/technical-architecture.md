---
description: >-
  Technical architecture of the ID Generator service — async stack, database
  design, concurrency patterns, and Kubernetes deployment.
---

# Technical Architecture

## Project structure

```
id-generator/
├── config/
│   └── default.yaml             # Default configuration
├── src/
│   └── id_generator/
│       ├── main.py              # FastAPI app entry point
│       ├── config.py            # Pydantic Settings (YAML + env vars)
│       ├── db.py                # Async SQLAlchemy engine
│       ├── models.py            # Table creation (table-per-ID-type)
│       ├── api/
│       │   ├── router.py        # API endpoints
│       │   └── schema.py        # MOSIP response envelope
│       ├── generator/
│       │   ├── engine.py        # ID generation pipeline
│       │   ├── filters.py       # 10 filter implementations
│       │   └── verhoeff.py      # Verhoeff checksum
│       └── pool/
│           ├── manager.py       # Background replenishment
│           └── issuer.py        # Issue & mark TAKEN
├── tests/                       # Integration test suite
├── charts/                      # Helm chart
├── Dockerfile
└── pyproject.toml
```

**Design principle**: The `generator` package (pure functions, no DB dependency) is separated from the `pool` package (DB-dependent). Filters and Verhoeff are independently testable.

## Database design

### Table-per-ID-type strategy

Each ID type gets its own table, auto-created on startup:

```sql
CREATE TABLE IF NOT EXISTS id_pool_{id_type} (
    id_value    VARCHAR(32)   PRIMARY KEY,
    status      VARCHAR(16)   NOT NULL DEFAULT 'AVAILABLE',
    created_at  TIMESTAMPTZ   NOT NULL DEFAULT now(),
    issued_at   TIMESTAMPTZ   NULL
);

CREATE INDEX IF NOT EXISTS idx_{id_type}_available
    ON id_pool_{id_type} (status) WHERE status = 'AVAILABLE';
```

### Why table-per-ID-type

| Aspect              | Single table                                     | Table-per-ID-type (chosen)                          |
| ------------------- | ------------------------------------------------ | --------------------------------------------------- |
| Query performance   | All types share one B-tree index                 | Each table has its own smaller index                |
| Bulk insert         | Inserting into 200M+ row table                   | Inserting into 50M row table — lighter              |
| VACUUM/maintenance  | One large table to vacuum                        | Smaller tables vacuum faster                        |
| Dropping a type     | Slow DELETE + WAL bloat                          | Instant `DROP TABLE`                                |

## Issuing IDs — concurrency-safe path

### SQL pattern

```sql
-- Atomic: select + lock in one step
SELECT id_value FROM id_pool_{id_type}
WHERE status = 'AVAILABLE'
LIMIT 1
FOR UPDATE SKIP LOCKED;

-- Mark as taken
UPDATE id_pool_{id_type}
SET status = 'TAKEN', issued_at = now()
WHERE id_value = :id;
```

Both statements execute in a single transaction.

### Why `FOR UPDATE SKIP LOCKED`

* With plain `FOR UPDATE`: if Pod A locks a row, Pod B **waits** (blocks).
* With `FOR UPDATE SKIP LOCKED`: Pod B **skips** the locked row and grabs the next one.
* Result: **zero contention** between pods.

{% hint style="info" %}
This is the standard PostgreSQL pattern for job queues and pool dispensers. It ensures every pod gets an instant response regardless of concurrent load.
{% endhint %}

### Deadlock retry

In rare cases under heavy load, deadlocks can occur between issuing and replenishment. The issuer includes retry logic: up to **3 retries** with **100ms delay**.

## Pool replenishment

### Background task

Every pod runs a periodic background task (default: every 30 seconds):

```
For each ID type in config:
    1. COUNT AVAILABLE IDs
    2. If count < pool_min_threshold:
         Try: pg_try_advisory_lock(hash(id_type))
         If lock acquired → generate + insert IDs
         If lock NOT acquired → skip (another pod is handling it)
```

### Why PostgreSQL advisory locks

* **No leader election needed** — any pod can generate, but only one at a time per ID type.
* **`pg_try_advisory_lock`** is non-blocking — if another pod holds the lock, skip instantly.
* **Database is the coordinator** — no Redis, ZooKeeper, or K8s leader election needed.
* **Per-ID-type locks** — Pod A generates for `farmer_id` while Pod B generates for `household_id` simultaneously.

### Sub-batch insertion

IDs are inserted in smaller sub-batches (100 rows per transaction) rather than one large batch:

* Avoids long-running transactions that hold locks.
* Reduces WAL pressure.
* Allows issuing operations to interleave without being blocked.

## ID generation pipeline

```
1. secrets.randbelow(upper_bound)
     → raw (length-1) digit string, zero-padded

2. Verhoeff checksum → append 1 digit
     → candidate ID

3. Run 10 filters (ordered cheapest-first):
     a. not_start_with       (string prefix)
     b. length               (string length)
     c. sequence             (scan)
     d. repeating_digit      (regex)
     e. repeating_block      (regex)
     f. conjugative_even     (regex)
     g. first_equals_last    (string slice)
     h. first_equals_reverse (string slice)
     i. restricted_numbers   (substring search)
     j. cyclic_numbers       (substring search)

4. If all pass → collect for DB insert
   If any fail → discard, generate next

5. INSERT ... ON CONFLICT DO NOTHING
     → silently skips duplicates
```

{% hint style="info" %}
**Filter ordering**: Cheapest and most-likely-to-reject filters run first (e.g., `not_start_with` rejects \~20% of candidates immediately) to fail fast.
{% endhint %}

## Startup behaviour

```
1. Connect to PostgreSQL
2. For each ID type:
     a. CREATE TABLE IF NOT EXISTS
     b. Count AVAILABLE IDs
     c. If count < threshold → generate IDs (blocking)
3. Mark startup complete
4. Start background replenishment loop
5. Begin accepting HTTP requests
```

{% hint style="warning" %}
The service **blocks until all ID types have their minimum pool generated**. This ensures no IDG-001 errors immediately after deployment. Initial startup may take time for large pools — the Kubernetes startup probe allows up to 5 minutes.
{% endhint %}

## Kubernetes deployment

```
┌───────────────────────────────────────────────┐
│              Kubernetes Cluster                │
│                                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Pod 1   │  │  Pod 2   │  │  Pod 3   │   │
│  │ FastAPI  │  │ FastAPI  │  │ FastAPI  │   │
│  │ + pool   │  │ + pool   │  │ + pool   │   │
│  │ manager  │  │ manager  │  │ manager  │   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       └──────────┬───┘─────────────┘          │
│                  │                            │
│          ┌───────▼────────┐                   │
│          │  PostgreSQL    │                   │
│          │  (single DB)   │                   │
│          └────────────────┘                   │
└───────────────────────────────────────────────┘
```

* **Every pod is identical** — runs both the API server and the background pool manager.
* **No leader pod** — PostgreSQL advisory locks coordinate generation naturally.
* **Horizontal scaling** — add pods for more API throughput.

### Probes

| Probe      | Endpoint                         | Purpose                                    |
| ---------- | -------------------------------- | ------------------------------------------ |
| Startup    | `GET /v1/idgenerator/health`     | Waits up to 5 min for pool generation      |
| Readiness  | `GET /v1/idgenerator/health`     | Only ready after startup is complete       |
| Liveness   | `GET /v1/idgenerator/health`     | Detect unhealthy processes                 |

## Key architectural decisions

| # | Decision                  | Choice                                            | Rationale                                               |
| - | ------------------------- | ------------------------------------------------- | ------------------------------------------------------- |
| 1 | Async stack               | FastAPI + asyncpg + SQLAlchemy async              | I/O-bound workload, no thread pool overhead             |
| 2 | Table strategy            | Table-per-ID-type                                 | Clean isolation, better maintenance, instant DROP        |
| 3 | Issuing concurrency       | `SELECT ... FOR UPDATE SKIP LOCKED`               | Zero contention between pods                            |
| 4 | Generation coordination   | PostgreSQL advisory locks                         | No external coordinator needed                          |
| 5 | Bulk insert               | Sub-batches (100 rows per transaction)            | Avoids long transactions, reduces WAL pressure          |
| 6 | Duplicate handling        | `INSERT ... ON CONFLICT DO NOTHING`               | Silently skips, no error handling needed                |
| 7 | Filter execution          | In-memory, cheapest-first, before DB insert       | Fail fast, no wasted DB writes                          |
| 8 | Startup behaviour         | Block until minimum pool generated                | No IDG-001 errors immediately after deployment          |
| 9 | Config management         | Pydantic Settings: YAML + env var overrides       | Flexible for K8s (ConfigMap + env vars)                 |
