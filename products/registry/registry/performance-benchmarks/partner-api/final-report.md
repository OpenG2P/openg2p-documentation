# Farmer Registry Partner API — Performance Test - Measurements & Analysis

Interpretation layer over [`raw-report.md`](raw-report.md) (every measurement, verbatim, no interpretation), against the test design in [`test-scenarios.md`](test-scenarios.md). Organized around the four DCI-compliant query types (`idtype-value`, `expression`, `graphql`, `predicate`), each run once sync and once async, plus the separate Ingest API. `idtype-value` is reported as Single Farmer Search using ID, using the `btree_fid` index-case measurements — functionally equivalent, via an equivalent expression search.

## Methodology

Two different run shapes are mixed together here, and they are not comparable to each other:

- **Single Farmer Search using ID** (`idtype-value`, reported via `btree_fid`'s measurements — see note below) and **Ingest** use the open-loop ramp shape (`locust/api/shared/slo_shape.py`, test-scenarios.md §5): search starts at 2 users and adds 2 every 30s, up to 100, and freezes when a step's RPS stops rising, the partner pod holds 1.85 cores for 2 polls, or p99 breaches its threshold for 2 windows. The frozen user count and its RPS are what's reported — a floor reached by that ramp, not a result independently verified at a higher concurrency.
- **`expression`, `predicate`, and `graphql`** instead run at a **fixed** concurrency — `POD_SCALE × 8` Locust users (8 / 16 / 24) — each user firing one request, waiting for the response, then firing the next (`run_case.sh`). This is a closed-loop throughput measurement over a fixed window (10-11 minutes, or 1 hour for the `_1h` runs), not a ramp-to-freeze.

Sync and async are not apples-to-apples on HTTP RPS. A sync request's response time is the full search; an async request's response time is only the ACK that the search was accepted — the actual result is published later over WebSub, outside this request. Records/min (see each query type's own one-liner below) is the comparable throughput number between sync and async; raw HTTP RPS is not.

Every DCI request shares the same envelope, only `query_type`/`query`/`pagination` change per case (`locustfile.py` `_criteria`/`_expression`):

```json
{
  "version": "1.0.0",
  "reg_type": "Farmer",
  "reg_record_type": "farmer",
  "query_type": "<expression | predicate | graphql | idtype-value>",
  "query": { "...": "shown per query type below" },
  "pagination": { "page_size": 100, "page_number": 1 }
}
```

`_p100`/`_p500` in a case name is Locust's own page size for that run (`DCI_PAGE_SIZE`), not a percentile. `_1h` is a longer confirmatory run (`RUN_MINUTES=60`) at the same fixed concurrency as the short run at that pod-scale, to check for drift. Pod and database configuration (2 vCPU partner pod, 2 Gunicorn workers, PgBouncer at `172.29.2.191:6432`, signature validation on / consent and audit off) is in [`test-scenarios.md`](test-scenarios.md) §2, not repeated here.

## DCI Compliant Search

### Query Type — Single Farmer Search using ID

`FID` equals `functional_record_id` — a single-record lookup, no range operator (test-scenarios.md §1).

Measured using an equivalent expression search `{"functional_record_id": {"$eq": <fid>}}`. This returns a single farmer record. This is functionally equivalent to Query Type - idtype-value.

**Sync**

| Pod-Scale | Users (frozen) | RPS | p50 | p90 | p95 | p99 | Max | Requests | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 16 | 47.59 | 260ms | 410ms | 460ms | 820ms | 5.5s | 20,494 | 2 (0.0098%) |
| 2 | 24 | 80.01 | 230ms | 350ms | 380ms | 480ms | 910ms | 38,472 | 7 (0.0182%) |
| 3 | 44 | 106.12 | 280ms | 460ms | 520ms | 640ms | 2.0s | 65,858 | 6 (0.0091%) |

**Async**

| Pod-Scale | Users (frozen) | RPS | p50 | p90 | p95 | p99 | Max | Requests | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 12 | 42.88 | 240ms | 410ms | 470ms | 610ms | 860ms | 16,750 | 2 (0.0119%) |
| 2 | 20 | 76.45 | 210ms | 380ms | 430ms | 580ms | 1.0s | 34,432 | 7 (0.0203%) |
| 3 | 20 | 101.17 | 150ms | 300ms | 340ms | 430ms | 1.1s | 46,585 | 7 (0.0150%) |

Both modes scale cleanly: sync 2.23× RPS for 3× pods (≈74% efficiency); async 2.36× (≈79%). Async's frozen user count does not grow Pod-2→Pod-3 (20→20, vs. sync's 24→44) — RPS still climbs because each already-frozen user is served faster. CPU plateaus at the 2 vCPU ceiling at every pod-scale, both modes; sync memory is flat (≈285-291 MiB), but async memory climbs within a run and carries forward across runs on the same pod identity (≈334→453 MiB by the Pod-1 run, already ≈477→553 MiB by the time the same pod reached the Pod-3 run) — the clearest watch item in this whole cycle, not plateaued across the async test session.

### Query Type — `expression` range

Date-of-birth filter only (`locustfile.py` `query_expression`):

```json
"query": {
  "type": "expression",
  "value": {
    "expression": {
      "query": {
        "$and": [
          { "birth_date": { "$gte": "<day>" } },
          { "birth_date": { "$lte": "<day+6>" } }
        ]
      }
    }
  }
}
```

**Sync** (page size 100 unless noted)

| Pod-Scale | Users | RPS | p50 | p90 | p95 | p99 | Max | Errors | Records/min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8 | 3.34 | 2.3s | 3.2s | 3.6s | 4.5s | 6.2s | 4 (0.200%) | 17,501 |
| 2 | 16 | 5.38 | 2.7s | 4.1s | 4.5s | 5.9s | 8.6s | 7 (0.217%) | 28,099 |
| 3 | 24 | 5.49 | 3.9s | 6.3s | 7.2s | 9.0s | 15.0s | 3 (0.091%) | 28,747 |
| 1, page size 500 | 8 | 0.76 | 9.9s | 14.0s | 16.0s | 18.0s | 22.0s | 3 (0.655%) | 18,593 |
| 2, 1h confirmatory | 16 | 4.91 | 3.2s | — | 5.1s | 6.2s | — | 18/17,686 (0.102%) | 27,772 |

**Async**

| Pod-Scale | Users | RPS | p50 | p90 | p95 | p99 | Max | Errors | Records/min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8 | 2.67 | 230ms | 1.3s | 1.8s | 2.8s | 3.4s | 67 (3.484%) | 14,077 |
| 2 | 16 | 2.78 | 120ms | 500ms | 840ms | 3.3s | 5.3s | 6 (0.351%) | 15,164 |
| 3 | 24 | 2.67 | 110ms | 440ms | 1.0s | 3.6s | 5.3s | 2 (0.125%) | 14,118 |
| 3, 1h confirmatory | 24 | 2.80 | 120ms | — | 590ms | 3.5s | — | 6/10,070 (0.060%) | 16,410 |

**How Records/min was measured for Async:** the HTTP response to an async request is only an ACK, so records/min for async is **not** read from Locust's stats — `fill_kafka_records.py` instead consumes the `PARTNER_STAFF_PORTAL` WebSub Kafka topic, counts `reg_records` in each published on-search envelope that belongs to this run (matched by `message.transaction_id` against the run's own ID), and logs the running total once a minute to `*_records.csv`.

5× the page size (page size 500, sync, Pod-1) roughly quadruples p50 (2.3s → 9.9s) for about the same records/min (17,501 vs. 18,593) — fewer, much bigger responses, not more work done. No Pod-2/Pod-3 or async page-500 run exists yet.

The 1-hour confirmatory runs: sync (Pod-2) drifts mildly worse over the hour (RPS 5.38→4.91, every percentile up, but records/min within 2%); async (Pod-3) is stable to slightly better (p95 actually drops, records/min up ≈16%). Neither resembles a late-run blowout.

**CPU / Memory** (representative pods, read off Grafana; not every pod/scale screenshotted): sync CPU falls from ≈1.5-1.7 cpu/pod at Pod-1 to ≈0.75-1.0 cpu/pod at Pod-3 as load spreads across more pods; memory sits far above Single Farmer Search using ID's baseline (≈437-444 MiB flat at Pod-1 sync; climbs 238→381 MiB within the Pod-3 run) — expected, since each response serializes up to 100 full farmer records instead of one. Async shows the same CPU-vs-scale shape (≈1.5-1.8 cpu/pod at Pod-1 → ≈0.6-0.8 cpu/pod at Pod-3) plus a within-run memory climb (238→477 MiB at Pod-1, 238→429 MiB at Pod-3).

### Query Type — `graphql` range

Date-of-birth filter only (`locustfile.py` `query_graphql`):

```json
"query": {
  "type": "graphql",
  "value": {
    "expression": "query { farmer(birth_date: { gte: \"<day>\", lte: \"<day+6>\" }) { functional_record_id } }"
  }
}
```

**Sync**

| Pod-Scale | Users | RPS | p50 | p90 | p95 | p99 | Max | Errors | Records/min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8 | 3.36 | 2.3s | 3.2s | 3.5s | 4.4s | 6.0s | 4 (0.198%) | 17,592 |
| 2 | 16 | 5.31 | 2.8s | 4.1s | 4.7s | 6.0s | 8.6s | 5 (0.157%) | 27,717 |
| 3 | 24 | 4.54 | 4.9s | 7.5s | 8.4s | 9.6s | 16.0s | 2 (0.083%) | 25,759 |

**Async**

| Pod-Scale | Users | RPS | p50 | p90 | p95 | p99 | Max | Errors | Records/min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8 | 2.67 | 180ms | 1.3s | 1.7s | 2.7s | 3.4s | 59 (3.052%) | 14,201 |
| 2 | 16 | 2.68 | 120ms | 480ms | 820ms | 3.4s | 5.3s | 2 (0.123%) | 14,400 |
| 3 | 24 | 2.65 | 120ms | 330ms | 770ms | 3.8s | 5.2s | 1 (0.063%) | 14,064 |

**How Records/min was measured for Async:** same Kafka-consumer method as `expression` above — the async HTTP response carries no records, so `fill_kafka_records.py` counts them off the `PARTNER_STAFF_PORTAL` WebSub topic instead.

`graphql` is the one query type that regresses outright at Pod-3, sync: RPS drops (5.31→4.54) and records/min drops (27,717→25,759) rather than plateauing like `expression`/`predicate` do — worse than Pod-2 on every axis, not just a smaller gain.

**CPU / Memory:** not separately screenshotted from `expression`'s — `graphql` shares the same locustfile base class, request shape, and page size, and its CPU/memory behavior was not distinguishable from `expression`'s in the captured graphs; see `expression`'s CPU/Memory note above.

### Query Type — `predicate` range

Date-of-birth filter only (`locustfile.py` `query_predicate`):

```json
"query": [
  {
    "seq_num": 1,
    "expression1": { "attribute_name": "birth_date", "operator": "ge", "attribute_value": "<day>" }
  },
  {
    "seq_num": 2,
    "expression1": { "attribute_name": "birth_date", "operator": "le", "attribute_value": "<day+6>" }
  }
]
```

(`predicate`'s `query` is a bare list of expression objects — the only one of the three range queries not wrapped in a `{"type": ..., "value": ...}` envelope.)

**Sync**

| Pod-Scale | Users | RPS | p50 | p90 | p95 | p99 | Max | Errors | Records/min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8 | 3.29 | 2.3s | 3.3s | 3.6s | 4.8s | 7.5s | 4 (0.202%) | 17,251 |
| 2 | 16 | 5.40 | 2.7s | 4.1s | 4.7s | 6.0s | 9.2s | 3 (0.092%) | 28,257 |
| 3 | 24 | 5.26 | 4.1s | 6.6s | 7.3s | 10.0s | 14.0s | 1 (0.032%) | 27,558 |

**Async**

| Pod-Scale | Users | RPS | p50 | p90 | p95 | p99 | Max | Errors | Records/min |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 8 | 2.67 | 210ms | 1.3s | 1.8s | 3.1s | 4.6s | 67 (3.536%) | 15,083 |
| 2 | 16 | 2.74 | 120ms | 600ms | 1.1s | 3.9s | 5.2s | 3 (0.181%) | 14,736 |
| 3 | 24 | 2.61 | 120ms | 360ms | 1.7s | 4.6s | 5.3s | 3 (0.190%) | 13,864 |

**How Records/min was measured for Async:** same Kafka-consumer method as `expression` above.

`predicate` plateaus the same way `expression` does from Pod-2 to Pod-3 (sync records/min essentially flat: 28,257→27,558), with p95/p99 getting noticeably worse at Pod-3 despite the flat throughput.

**CPU / Memory:** not separately screenshotted — same locustfile base class and request shape as `expression`/`graphql`; see `expression`'s CPU/Memory note above.

### Query types compared

All three range queries share one pattern: **sync out-throughputs async at every pod-scale**, despite async's much lower per-request latency (p50 110-230ms vs. sync's 2.3-4.9s) — because async's bottleneck is the downstream Kafka/WebSub publish path, not the partner pod, so its records/min barely moves across Pod-1/2/3 (≈14,000-15,200 throughout) while sync's climbs with pod count before plateauing (or, for `graphql`, reversing) past Pod-2. Async's error rate is also concentrated at Pod-1 specifically — 3.0-3.5% `HTTP 503` on all three query types at 8 users/1 pod, dropping to ≤0.35% at Pod-2/3 — while sync's error rate stays low and flat (≤0.22%) throughout. Every recorded failure, sync or async, any query type, is `HTTP 503` (`*_failures.csv`); no `*_exceptions.csv` has any rows anywhere in this results set.

## Ingest API

`POST /partner/ingest_data?data_model=IMPORT_FARMER_CSV` inserts one raw farmer payload per request — gender, marital status, education, income, language, crop, season, livestock, and ownership coding stay fixed (`MALE`/`MARRIED`/`BASIC`/`SOI_CROP_PRODUCTION`/`ENGLISH`/`WHEAT`/`WINTER`/`GOAT`/`OWNER`); names, birth date, foundational id, address, locality, postal code, land size, and head count change on every request (test-scenarios.md §6).

**Ingest only writes the raw payload** — it lands in `incoming_raw_data`, not the register. Turning that raw row into a classified, transformed, register-ingested farmer record is Celery's job, not this API's: see `ingest_data_classification`, `ingest_data_transformation`, and `ingest_data` in [`../celery/final-report-summary.md`](../celery/final-report-summary.md#partner-ingest) for those pipelines' own throughput measurements. This API's own numbers below are strictly the HTTP-layer insert — they say nothing about how fast that backlog actually drains.

### Measurements

Same open-loop ramp shape as Single Farmer Search using ID (test-scenarios.md §5: starts at 4 users, +4/30s).

| Pod-Scale | Users (frozen) | RPS | p50 | p90 | p95 | p99 | Max | Requests | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 20 | 85.74 | 190ms | 300ms | 330ms | 450ms | 860ms | 38,627 | 2 (0.0052%) |
| 2 | 32 | 141.13 | 170ms | 270ms | 300ms | 410ms | 5.4s | 76,281 | 5 (0.0066%) |
| 3 | 40 | 187.91 | 150ms | 240ms | 280ms | 400ms | 740ms | 112,894 | 3 (0.0027%) |

The cleanest scaling in this whole cycle: users and RPS both grow smoothly Pod-1→3 (2.19× RPS for 3× pods, ≈73% efficiency), and p95 actually *improves* as pods scale (330ms→300ms→280ms) rather than degrading. Pod-2's one 5.4s max is a single outlier (p99 is still 410ms), not reflected anywhere else in that run's percentiles. CPU oscillates at or near the 2 vCPU ceiling per pod at every pod-scale (sawtooth, not a clean plateau); memory is close to flat with a mild rise (≈274→286 MiB at Pod-1, ≈248→286 MiB at Pod-3).
