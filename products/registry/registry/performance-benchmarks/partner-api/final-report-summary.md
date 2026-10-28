# Farmer Registry Partner API - Performance Test Report

## Methodology

Organized around the four DCI-compliant query types — `idtype-value`, `expression`, `graphql`, `predicate` — each run once as **sync** (`POST /dci/sync/search`, full response) and once as **async** (`POST /dci/async/search`, ACK only, result published later over WebSub), plus the separate Ingest API. `idtype-value` is reported as Single Farmer Search using ID, using `btree_fid`'s measurements — functionally equivalent, via an equivalent expression search. Single Farmer Search using ID and Ingest use the open-loop ramp-and-freeze shape shared with staff-api (`locust/api/shared/slo_shape.py`) — freeze on a flat RPS step, 1.85 cores held for 2 polls, or a p99 breach — and report the frozen user count/RPS. `expression`/`predicate`/`graphql` instead run at a **fixed** closed-loop concurrency of `Pod-Scale × 8` users for ~10-11 minutes (page size 100), plus one page-size-500 run and two 1-hour confirmatory runs. Full detail is in [`final-report.md`](final-report.md); every raw number is in [`raw-report.md`](raw-report.md).

**Records/min**, read from each DCI run's `*_records.csv`, is the one throughput figure comparable between sync and async — HTTP RPS is not, since an async request's response time is only the ACK.

## Test Environment

Partner pod: 2 vCPU limit, 2 Gunicorn workers (`docker/ofr-partner/Dockerfile`), `requests == limits`. App database through PgBouncer (`172.29.2.191:6432`, SQLAlchemy pool 12 + overflow 18), same as staff-api; master data stays on Postgres `5432` directly. Signature validation on, consent enforcement off, audit emission off. Compute/Storage node spec is the same shared 3-node profile as every other service — see `../environment-topology.md`.

## DCI Compliant Search

### Query Type — Single Farmer Search using ID

`FID` equals `functional_record_id` — a single-record lookup, no range.

Measured using an equivalent expression search `{"functional_record_id": {"$eq": <fid>}}`. This returns a single farmer record. This is functionally equivalent to Query Type - idtype-value.

| Mode | Pod-1 | Pod-2 | Pod-3 |
|---|---:|---:|---:|
| Sync users / RPS | 16 / 47.59 | 24 / 80.01 | 44 / 106.12 |
| Async users / RPS | 12 / 42.88 | 20 / 76.45 | 20 / 101.17 |

Both modes scale cleanly (sync ≈74%, async ≈79% efficiency Pod-1→3). Async's frozen user count stalls at 20 from Pod-2 onward (sync keeps growing to 44) — RPS still rises because each frozen user is served faster. Async memory climbs within a run and **carries forward across runs** on the same pod (≈334→453 MiB by Pod-1, already ≈477→553 MiB by Pod-3) — the clearest watch item this cycle; sync memory stays flat (≈285-291 MiB).

### Query Type — `expression` range

```json
"query": { "type": "expression", "value": { "expression": { "query": {
  "$and": [ { "birth_date": { "$gte": "<day>" } }, { "birth_date": { "$lte": "<day+6>" } } ]
} } } }
```

| Mode | Pod-1 | Pod-2 | Pod-3 |
|---|---:|---:|---:|
| Sync RPS / records-min | 3.34 / 17,501 | 5.38 / 28,099 | 5.49 / 28,747 |
| Async RPS / records-min | 2.67 / 14,077 | 2.78 / 15,164 | 2.67 / 14,118 |
| Sync p95 | 3.6s | 4.5s | 7.2s |
| Async p95 | 1.8s | 840ms | 1.0s |
| Sync error % | 0.200 | 0.217 | 0.091 |
| Async error % | **3.484** | 0.351 | 0.125 |

| Variant | RPS | p95 | p99 | Error % | Records/min |
|---|---:|---:|---:|---:|---:|
| Page size 100, Sync Pod-1 (baseline) | 3.34 | 3.6s | 4.5s | 0.200 | 17,501 |
| Page size 500, Sync Pod-1 | 0.76 | 16.0s | 18.0s | 0.655 | 18,593 |
| Sync Pod-2, short run (11 min) | 5.38 | 4.5s | 5.9s | 0.217 | 28,099 |
| Sync Pod-2, 1h confirmatory | 4.91 | 5.1s | 6.2s | 0.102 | 27,772 |
| Async Pod-3, short run (11 min) | 2.67 | 1.0s | 3.6s | 0.125 | 14,118 |
| Async Pod-3, 1h confirmatory | 2.80 | 590ms | 3.5s | 0.060 | 16,410 |

Page size 500 trades throughput for far larger, slower responses (≈4× the p100 latency for about the same records/min); over the full hour, sync drifts mildly worse while async stays stable to slightly better than its own short run.

**Records/min for Async** is read from Kafka, not the HTTP response: `fill_kafka_records.py` consumes the `PARTNER_STAFF_PORTAL` WebSub topic and counts `reg_records` per published on-search envelope, logging the running total once a minute.

### Query Type — `graphql` range

```json
"query": { "type": "graphql", "value": {
  "expression": "query { farmer(birth_date: { gte: \"<day>\", lte: \"<day+6>\" }) { functional_record_id } }"
} }
```

| Mode | Pod-1 | Pod-2 | Pod-3 |
|---|---:|---:|---:|
| Sync RPS / records-min | 3.36 / 17,592 | 5.31 / 27,717 | **4.54 / 25,759** |
| Async RPS / records-min | 2.67 / 14,201 | 2.68 / 14,400 | 2.65 / 14,064 |
| Sync p95 | 3.5s | 4.7s | 8.4s |
| Async p95 | 1.7s | 820ms | 770ms |
| Sync error % | 0.198 | 0.157 | 0.083 |
| Async error % | **3.052** | 0.123 | 0.063 |

**Records/min for Async** measured the same way as `expression`, above (Kafka, not HTTP). The only query type that regresses outright at Pod-3 sync — worse than Pod-2 on RPS, records/min, and every percentile, not just a plateau.

### Query Type — `predicate` range

```json
"query": [
  { "seq_num": 1, "expression1": { "attribute_name": "birth_date", "operator": "ge", "attribute_value": "<day>" } },
  { "seq_num": 2, "expression1": { "attribute_name": "birth_date", "operator": "le", "attribute_value": "<day+6>" } }
]
```

| Mode | Pod-1 | Pod-2 | Pod-3 |
|---|---:|---:|---:|
| Sync RPS / records-min | 3.29 / 17,251 | 5.40 / 28,257 | 5.26 / 27,558 |
| Async RPS / records-min | 2.67 / 15,083 | 2.74 / 14,736 | 2.61 / 13,864 |
| Sync p95 | 3.6s | 4.7s | 7.3s |
| Async p95 | 1.8s | 1.1s | 1.7s |
| Sync error % | 0.202 | 0.092 | 0.032 |
| Async error % | **3.536** | 0.181 | 0.190 |

**Records/min for Async** measured the same way as `expression`, above (Kafka, not HTTP). Plateaus Pod-2→Pod-3 like `expression` (sync records/min essentially flat), with p95/p99 still getting worse despite the flat throughput.

**Headline, all three query types:** sync out-throughputs async at every pod-scale despite async's much lower per-request latency — async's bottleneck is the downstream Kafka/WebSub publish path, not the partner pod, so its records/min barely moves across Pod-1/2/3. Async error rate is concentrated at Pod-1 (3.0-3.5%, dropping to ≤0.35% at Pod-2/3); sync's stays ≤0.22% throughout. Every failure anywhere in this results set is `HTTP 503`.

## Ingest API

`POST /partner/ingest_data?data_model=IMPORT_FARMER_CSV` — one raw farmer payload per request (gender/marital status/education/income/language/crop/season/livestock/ownership coded and fixed; names, birth date, foundational id, address, land size, head count change every request). **Ingest only writes the raw payload**, to `incoming_raw_data` — turning it into a classified, transformed, register-ingested farmer is Celery's job, not this API's: see `ingest_data_classification`/`ingest_data_transformation`/`ingest_data` in [`../celery/final-report-summary.md`](../celery/final-report-summary.md#partner-ingest) for that throughput.

### Measurements

Open-loop ramp (starts 4 users, +4/30s).

| Pod-Scale | Users (frozen) | RPS | p95 | p99 | Error % |
|---:|---:|---:|---:|---:|---:|
| 1 | 20 | 85.74 | 330ms | 450ms | 0.0052 |
| 2 | 32 | 141.13 | 300ms | 410ms | 0.0066 |
| 3 | 40 | 187.91 | 280ms | 400ms | 0.0027 |

Cleanest scaling of the cycle (≈73% efficiency Pod-1→3) — p95 *improves* as pods scale rather than degrading. CPU sits at/near the 2 vCPU ceiling per pod at every scale; memory close to flat.
