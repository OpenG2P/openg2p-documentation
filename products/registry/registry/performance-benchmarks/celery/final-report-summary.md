# Farmer Registry Celery — Performance Test Report

## Methodology

One scenario at a time: beat held at 1 pod, worker pods stepped 1 → 2 → 3, against a fixed backlog re-seeded to `PENDING` before each worker count (test-scenarios.md §3/§6). A collector counts `pending`/`in_progress`/`done` on that scenario's status column once a minute until both `pending` and `in_progress` reach 0, or minute 30. There is no latency SLO and no PASS/FAIL gate here — unlike the staff-api tiers, this is a pure drain-time and scaling measurement (test-scenarios.md §5).

## Data Seeding

All scenarios ran against the register already seeded to the **`stretch`** volume tier (50M farmer records — see `../staff-api/final-report-summary.md`), left at that state after the staff-api cycle. The per-scenario queue backlog is **not** a uniform 50,000 across every scenario — it varies by table:

| Scenario | Backlog at mark 0 |
|---|---:|
| `ingest_data_classification` | 50,000 rows |
| `ingest_data_transformation` | 10,000 rows |
| `ingest_data` | 40,000 rows |
| `change_request_ingest` | 50,000 rows |
| `outgest_data_transformation` | 10,000 rows |
| `outgest_data_publish` | 50,000 rows |
| `intake_register_ingest` | 10,000 rows |
| `functional_id_allocation` | 50,000 rows |
| `score_compute` | 100,000 rows |
| `completion_score` | 100,000 rows |
| `import_file_process` | 20,000 records (2 files × 10,000) |

50,000 is the single most common value (4 of 11 scenarios), not the backlog for every scenario — `score_compute`/`completion_score` ran at 100,000, the three transformation/intake-sized queues at 10,000, `ingest_data` at 40,000, and `import_file_process` at 20,000 records across 2 files.

## Test Environment

Celery beat and worker both run as a single container, image `vin0dkhichar/ofr-staff-celery:performance-test`, namespace `perftest`, on the same shared `m5a.4xlarge` (16 vCPU/64 GB) compute node every other service runs on (`environment-topology.md`). Beat pod: 2 vCPU / 4 GB, `requests == limits`, 1 replica throughout. Worker pod: 2 vCPU / 4 GB, `requests == limits`, `--concurrency=2` (2 processes/pod), stepped 1 → 2 → 3 replicas per scenario. PostgreSQL is the same host-based instance (`172.29.2.191`) the staff-api tests used.

## Measurements

Beat frequency and per-scenario pickup size below were read directly off the live `farmer-registry-celery-beat-producer` deployment's env vars on the compute node — not the `cases.py` code defaults (which are a 20s/30s fallback that isn't what's actually deployed here). Every producer on this cluster fires every **10s**; CPU/Memory are peak values read off the Grafana pod graphs across the pod-1/2/3 runs (`final-report.md` §6 has the full per-pod-scale breakdown).

### Partner ingest

**`ingest_data_classification`**

- CPU peak — beat: ~1.7 cpu; worker: ~2.0 cpu (of a 2-vCPU pod limit)
- Memory peak — beat: ~286 MiB; worker: ~477 MiB (of a 4 GiB pod limit)
- Beat frequency: 10s
- Beat pickup size: 3,000 tasks/tick

| Rate/min — Pod-1 | Rate/min — Pod-2 | Rate/min — Pod-3 |
|---:|---:|---:|
| 2,185 | 3,607 | 3,977 |

**`ingest_data_transformation`**

- CPU peak — beat: ~0.6 cpu; worker: ~2.0 cpu (of a 2-vCPU pod limit)
- Memory peak — beat: ~267 MiB; worker: ~572 MiB (of a 4 GiB pod limit)
- Beat frequency: 10s
- Beat pickup size: 3,000 tasks/tick

| Rate/min — Pod-1 | Rate/min — Pod-2 | Rate/min — Pod-3 |
|---:|---:|---:|
| 658 | 1,206 | 1,703 |

**`ingest_data`**

- CPU peak — beat: ~1.1 cpu; worker: ~1.4 cpu (of a 2-vCPU pod limit)
- Memory peak — beat: ~238 MiB; worker: ~381 MiB (of a 4 GiB pod limit)
- Beat frequency: 10s
- Beat pickup size: 20,000 tasks/tick

| Rate/min — Pod-1 | Rate/min — Pod-2 | Rate/min — Pod-3 |
|---:|---:|---:|
| 1,718 | 3,154 | 4,112 |

**`change_request_ingest`**

- CPU peak — beat: ~1.5 cpu; worker: ~1.7 cpu (of a 2-vCPU pod limit)
- Memory peak — beat: ~330 MiB; worker: ~330 MiB (of a 4 GiB pod limit)
- Beat frequency: 10s
- Beat pickup size: 20,000 tasks/tick

| Rate/min — Pod-1 | Rate/min — Pod-2 | Rate/min — Pod-3 |
|---:|---:|---:|
| 3,353 | 5,801 | 6,300 |

### Outgest

**`outgest_data_transformation`**

- CPU peak — beat: ~0.55 cpu; worker: ~2.0 cpu (of a 2-vCPU pod limit)
- Memory peak — beat: ~286 MiB; worker: ~310 MiB (of a 4 GiB pod limit)
- Beat frequency: 10s
- Beat pickup size: 20,000 tasks/tick

| Rate/min — Pod-1 | Rate/min — Pod-2 | Rate/min — Pod-3 |
|---:|---:|---:|
| 368 | 728 | 1,015 |

**`outgest_data_publish`**

- CPU peak — beat: ~1.65 cpu; worker: ~1.5 cpu (of a 2-vCPU pod limit)
- Memory peak — beat: ~335 MiB; worker: ~345 MiB (of a 4 GiB pod limit)
- Beat frequency: 10s
- Beat pickup size: 20,000 tasks/tick

| Rate/min — Pod-1 | Rate/min — Pod-2 | Rate/min — Pod-3 |
|---:|---:|---:|
| 2,396 | 3,680 | 4,217 |

### Intake ingest

**`intake_register_ingest`**

- CPU peak — beat: ~1.0 cpu; worker: ~1.5 cpu (of a 2-vCPU pod limit)
- Memory peak — beat: ~265 MiB; worker: ~310 MiB (of a 4 GiB pod limit)
- Beat frequency: 10s
- Beat pickup size: 3,000 tasks/tick

| Rate/min — Pod-1 | Rate/min — Pod-2 | Rate/min — Pod-3 |
|---:|---:|---:|
| 566 | 962 | 1,313 |

### Functional ID

**`functional_id_allocation`**

- CPU peak — beat: ~1.4 cpu; worker: ~1.4 cpu (of a 2-vCPU pod limit)
- Memory peak — beat: ~286 MiB; worker: ~381 MiB (of a 4 GiB pod limit)
- Beat frequency: 10s
- Beat pickup size: 3,000 tasks/tick

| Rate/min — Pod-1 | Rate/min — Pod-2 | Rate/min — Pod-3 |
|---:|---:|---:|
| 1,959 | 3,469 | 4,453 |

### Scores

**`score_compute`**

- CPU peak — beat: ~1.0 cpu; worker: ~2.0 cpu (of a 2-vCPU pod limit)
- Memory peak — beat: ~270 MiB; worker: ~381 MiB (of a 4 GiB pod limit)
- Beat frequency: 10s
- Beat pickup size: 3,000 tasks/tick

| Rate/min — Pod-1 | Rate/min — Pod-2 | Rate/min — Pod-3 |
|---:|---:|---:|
| 6,307 | 8,771 | 8,584 |

**`completion_score`**

- CPU peak — beat: ~1.1 cpu; worker: ~1.4 cpu (of a 2-vCPU pod limit)
- Memory peak — beat: ~286 MiB; worker: ~477 MiB (of a 4 GiB pod limit)
- Beat frequency: 10s
- Beat pickup size: 3,000 tasks/tick

| Rate/min — Pod-1 | Rate/min — Pod-2 | Rate/min — Pod-3 |
|---:|---:|---:|
| 6,239 | 9,001 | 8,949 |

### Import file

**`import_file_process`**

- CPU peak — beat: ~0.07 cpu; worker: ~2.0 cpu (of a 2-vCPU pod limit)
- Memory peak — beat: ~191 MiB; worker: ~382 MiB (of a 4 GiB pod limit)
- Beat frequency: 10s
- Beat pickup size: 20,000 tasks/tick

| Rate/min — Pod-1 | Rate/min — Pod-2 | Rate/min — Pod-3 |
|---:|---:|---:|
| 1,398 | — | — |

## Conclusion
