# Farmer Registry Staff API - Performance Test Report

## Methodology

Test scenarios for `staff-portal-api` are exercised through 5 Locust
workflows, chosen to cover the read, create, and approve paths a real
case worker uses:

1. `register_read`
2. `cr_create`
3. `cr_read_and_approve`
4. `intake_create`
5. `intake_read_and_approve`

Each is run across a Volume-Tier × Pod-Scale matrix
(`smoke`/`primary`/`stretch`/`stress` × 1/2/3 pods). Step 2 (below) blends
all 5 at fixed weights:

- `register_read` — 40%
- `cr_read_and_approve` — 20%
- `intake_read_and_approve` — 20%
- `cr_create` — 10%
- `intake_create` — 10%

The matrix is filled in using a repeated 3-Step plan:

1. **Isolated** — one scenario per pod, ramped up until an endpoint's
   p95/p99 breaches its SLO or pod CPU crosses its threshold; the frozen
   user count/RPS at that point is the reported result, not a pass/fail
   verdict.
2. **Blended** — all 5 scenarios together at the weights above, same
   SLO-or-CPU-breach ramp/freeze logic as Step 1.
3. **Soak** — an 8-hour run at fixed concurrency, which does carry
   pass/fail: steady-state p95/p99 ≤ SLO and zero errors, sustained for
   the full 8h with no upward latency/memory trend.

Full detail — scenario definitions, the ramp/freeze mechanics, SLOs, and
the execution runbook — is in [`test-scenarios.md`](test-scenarios.md).

## Data Seeding

The database is seeded to a target Volume-Tier using a custom bulk
generator (`seeding/`) that populates a full generation DAG of related
tables (household, crops, change requests, etc.), not just the farmer
table itself:

- `smoke` — 10K farmer records (harness validation only)
- `primary` — 10M farmer records
- `stretch` — 50M farmer records
- `stress` — 100M farmer records (pending)

Measured total size (table + index), growth tracking the farmer-count
multiplier closely (~5.1× for a 5× target):

- `primary` — 139.3 GB (~203M rows across all tables)
- `stretch` — 715.1 GB (~1B rows across all tables)

Full detail is in [`seeding-design.md`](../seeding-design.md).

## Test Environment

**Nodes.** This test rig runs on a fixed 3-node AWS profile:

- Reverse Proxy — `t3a.medium` (2 vCPU / 4 GB), the public ingress hop.
- Compute — `m5a.4xlarge` (16 vCPU / 64 GB), a single RKE2 Kubernetes node
  running every application pod.
- Storage — `t3a.2xlarge` (8 vCPU / 32 GB), host PostgreSQL 16 (not a K8s
  pod) plus NFS.

**PODs.** The pod under test runs at a fixed spec, with HPA off and
`requests == limits`, so results reflect that pinned resource ceiling, not
autoscaling behavior:

- `staff-portal-api` (farmer-registry) — 2 vCPU / 2 GB
- AWE — 2 vCPU / 2 GB
- Keycloak — 1 vCPU / 1 GB

**PostgreSQL.** PostgreSQL is fronted by PgBouncer, since connection
pooling in front of the single host-Postgres VM is usually the real
ceiling on this topology.

Full node sizing, pod specs, and PostgreSQL/PgBouncer tuning are in
[`environment-topology.md`](../environment-topology.md).

## Measurements

**Real users (computed)** is derived, not directly measured, via Little's
Law (`Real users = RPS × Real time`), where `RPS` is each scenario's own
throughput (`Locust users ÷ Unit-time` for Isolated, `B ÷ Unit-time` for
Blended/Soak) and `Real time` is the real-world duration a case worker
would take to complete one such unit of work (30s or 60s, by scenario).

### Isolated

**Table-1: Ingress = End-to-End, Scenario = Register-Read, Run = Isolated**

| Volume-Tier | Pod-Scale | Unit-time | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 1 | 8.75s | 20 | 2.286 | 30s | 69 |
| Primary | 2 | 7.48s | 32 | 4.278 | 30s | 128 |
| Primary | 3 | 7.78s | 44 | 5.655 | 30s | 170 |
| Stretch | 1 | 8.57s | 20 | 2.334 | 30s | 70 |
| Stretch | 2 | 8.66s | 36 | 4.158 | 30s | 125 |
| Stretch | 3 | 9.63s | 56 | 5.812 | 30s | 174 |

**Table-2: Ingress = In-Cluster, Scenario = Register-Read, Run = Isolated**

| Volume-Tier | Pod-Scale | Unit-time | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 1 | 6.54s | 16 | 2.448 | 30s | 73 |
| Primary | 2 | 4.60s | 20 | 4.345 | 30s | 130 |
| Primary | 3 | 6.00s | 36 | 6.003 | 30s | 180 |
| Stretch | 1 | 6.62s | 16 | 2.418 | 30s | 73 |
| Stretch | 2 | 5.41s | 24 | 4.438 | 30s | 133 |
| Stretch | 3 | 5.96s | 36 | 6.042 | 30s | 181 |

**Table-3: Ingress = End-to-End, Scenario = CR-Create, Run = Isolated**

| Volume-Tier | Pod-Scale | Unit-time | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 1 | 1.11s | 20 | 18.083 | 30s | 542 |
| Primary | 2 | 1.02s | 32 | 31.249 | 30s | 937 |
| Primary | 3 | 1.14s | 48 | 42.007 | 30s | 1260 |
| Stretch | 1 | 1.31s | 24 | 18.353 | 30s | 551 |
| Stretch | 2 | 1.32s | 44 | 33.215 | 30s | 996 |
| Stretch | 3 | 1.38s | 56 | 40.594 | 30s | 1218 |

**Table-4: Ingress = In-Cluster, Scenario = CR-Create, Run = Isolated**

| Volume-Tier | Pod-Scale | Unit-time | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 1 | 0.64s | 12 | 18.785 | 30s | 564 |
| Primary | 2 | 0.63s | 20 | 31.747 | 30s | 952 |
| Primary | 3 | 1.01s | 44 | 43.512 | 30s | 1305 |
| Stretch | 1 | 1.48s | 28 | 18.866 | 30s | 566 |
| Stretch | 2 | 1.93s | 48 | 24.915 | 30s | 747 |
| Stretch | 3 | 1.91s | 52 | 27.204 | 30s | 816 |

**Table-5: Ingress = End-to-End, Scenario = CR-Read-and-Approve, Run = Isolated**

| Volume-Tier | Pod-Scale | Unit-time | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 1 | 2.70s | 16 | 5.927 | 30s | 178 |
| Primary | 2 | 2.40s | 28 | 11.688 | 30s | 351 |
| Primary | 3 | 2.62s | 48 | 18.327 | 30s | 550 |
| Stretch | 1 | 4.07s | 24 | 5.899 | 30s | 177 |
| Stretch | 2 | 2.98s | 32 | 10.734 | 30s | 322 |
| Stretch | 3 | 2.90s | 48 | 16.557 | 30s | 497 |

**Table-6: Ingress = In-Cluster, Scenario = CR-Read-and-Approve, Run = Isolated**

| Volume-Tier | Pod-Scale | Unit-time | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 1 | 2.01s | 12 | 5.961 | 30s | 179 |
| Primary | 2 | 1.06s | 12 | 11.337 | 30s | 340 |
| Primary | 3 | 1.63s | 28 | 17.132 | 30s | 514 |
| Stretch | 1 | 1.76s | 12 | 6.811 | 30s | 204 |
| Stretch | 2 | 0.99s | 12 | 12.082 | 30s | 362 |
| Stretch | 3 | 2.23s | 36 | 16.152 | 30s | 485 |

**Table-7: Ingress = End-to-End, Scenario = Intake-Create, Run = Isolated**

| Volume-Tier | Pod-Scale | Unit-time | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 1 | 4.12s | 20 | 4.854 | 60s | 291 |
| Primary | 2 | 3.20s | 28 | 8.759 | 60s | 526 |
| Primary | 3 | 3.63s | 44 | 12.138 | 60s | 728 |
| Stretch | 1 | 5.08s | 24 | 4.721 | 60s | 283 |
| Stretch | 2 | 3.61s | 32 | 8.864 | 60s | 532 |
| Stretch | 3 | 3.67s | 44 | 11.999 | 60s | 720 |

**Table-8: Ingress = In-Cluster, Scenario = Intake-Create, Run = Isolated**

| Volume-Tier | Pod-Scale | Unit-time | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 1 | 3.18s | 16 | 5.036 | 60s | 302 |
| Primary | 2 | 2.56s | 24 | 9.389 | 60s | 563 |
| Primary | 3 | 2.36s | 28 | 11.877 | 60s | 713 |
| Stretch | 1 | 3.16s | 16 | 5.057 | 60s | 303 |
| Stretch | 2 | 2.30s | 20 | 8.688 | 60s | 521 |
| Stretch | 3 | 3.01s | 36 | 11.957 | 60s | 717 |

**Table-9: Ingress = End-to-End, Scenario = Intake-Read-and-Approve, Run = Isolated**

| Volume-Tier | Pod-Scale | Unit-time | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 1 | 2.61s | 24 | 9.199 | 30s | 276 |
| Primary | 2 | 2.77s | 40 | 14.453 | 30s | 434 |
| Primary | 3 | 4.50s | 64 | 14.224 | 30s | 427 |
| Stretch | 1 | 5.03s | 24 | 4.774 | 30s | 143 |
| Stretch | 2 | 2.73s | 44 | 16.134 | 30s | 484 |
| Stretch | 3 | N/A | 64 | N/A | 30s | N/A |

**Table-10: Ingress = In-Cluster, Scenario = Intake-Read-and-Approve, Run = Isolated**

| Volume-Tier | Pod-Scale | Unit-time | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Primary | 1 | 3.70s | 16 | 4.330 | 30s | 130 |
| Primary | 2 | 2.27s | 28 | 12.337 | 30s | 370 |
| Primary | 3 | 8.71s | 80 | 9.181 | 30s | 275 |
| Stretch | 1 | 3.18s | 16 | 5.024 | 30s | 151 |
| Stretch | 2 | 3.35s | 24 | 7.161 | 30s | 215 |
| Stretch | 3 | 2.61s | 40 | 15.318 | 30s | 460 |

### Blended

**Table: Ingress = End-to-End, Volume-Tier = Primary, Pod-Scale = 1, Run = Blended**

| Scenario | Unit-time | Locust-users-actual | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Register-Read | 10.18s | 20 | 8.00 | 0.786 | 30s | 24 |
| CR-Create | 1.17s | 20 | 2.00 | 1.711 | 30s | 51 |
| CR-Read-and-Approve | 2.94s | 20 | 4.00 | 1.360 | 30s | 41 |
| Intake-Create | 3.98s | 20 | 2.00 | 0.503 | 60s | 30 |
| Intake-Read-and-Approve | 3.17s | 20 | 4.00 | 1.262 | 30s | 38 |
| **Total** | — | — | — | — | — | **184** |

**Table: Ingress = End-to-End, Volume-Tier = Primary, Pod-Scale = 2, Run = Blended**

| Scenario | Unit-time | Locust-users-actual | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Register-Read | 8.20s | 28 | 11.20 | 1.365 | 30s | 41 |
| CR-Create | 0.97s | 28 | 2.80 | 2.895 | 30s | 87 |
| CR-Read-and-Approve | 2.29s | 28 | 5.60 | 2.450 | 30s | 74 |
| Intake-Create | 3.37s | 28 | 2.80 | 0.831 | 60s | 50 |
| Intake-Read-and-Approve | 2.51s | 28 | 5.60 | 2.227 | 30s | 67 |
| **Total** | — | — | — | — | — | **319** |

**Table: Ingress = End-to-End, Volume-Tier = Primary, Pod-Scale = 3, Run = Blended**

| Scenario | Unit-time | Locust-users-actual | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Register-Read | 9.32s | 48 | 19.20 | 2.060 | 30s | 62 |
| CR-Create | 1.10s | 48 | 4.80 | 4.378 | 30s | 131 |
| CR-Read-and-Approve | 2.36s | 48 | 9.60 | 4.074 | 30s | 122 |
| Intake-Create | 3.73s | 48 | 4.80 | 1.287 | 60s | 77 |
| Intake-Read-and-Approve | 4.76s | 48 | 9.60 | 2.018 | 30s | 61 |
| **Total** | — | — | — | — | — | **453** |

**Table: Ingress = End-to-End, Volume-Tier = Stretch, Pod-Scale = 1, Run = Blended**

| Scenario | Unit-time | Locust-users-actual | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Register-Read | 9.70s | 20 | 8.00 | 0.825 | 30s | 25 |
| CR-Create | 1.17s | 20 | 2.00 | 1.714 | 30s | 51 |
| CR-Read-and-Approve | 3.97s | 20 | 4.00 | 1.007 | 30s | 30 |
| Intake-Create | 3.77s | 20 | 2.00 | 0.531 | 60s | 32 |
| Intake-Read-and-Approve | 4.56s | 20 | 4.00 | 0.877 | 30s | 26 |
| **Total** | — | — | — | — | — | **164** |

**Table: Ingress = End-to-End, Volume-Tier = Stretch, Pod-Scale = 2, Run = Blended**

| Scenario | Unit-time | Locust-users-actual | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Register-Read | 8.79s | 32 | 12.80 | 1.457 | 30s | 44 |
| CR-Create | 1.00s | 32 | 3.20 | 3.191 | 30s | 96 |
| CR-Read-and-Approve | 3.06s | 32 | 6.40 | 2.089 | 30s | 63 |
| Intake-Create | 3.51s | 32 | 3.20 | 0.911 | 60s | 55 |
| Intake-Read-and-Approve | 2.71s | 32 | 6.40 | 2.365 | 30s | 71 |
| **Total** | — | — | — | — | — | **329** |

**Table: Ingress = End-to-End, Volume-Tier = Stretch, Pod-Scale = 3, Run = Blended**

| Scenario | Unit-time | Locust-users-actual | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Register-Read | 10.65s | 52 | 20.80 | 1.954 | 30s | 59 |
| CR-Create | 1.21s | 52 | 5.20 | 4.285 | 30s | 129 |
| CR-Read-and-Approve | 2.98s | 52 | 10.40 | 3.485 | 30s | 105 |
| Intake-Create | 4.13s | 52 | 5.20 | 1.259 | 60s | 76 |
| Intake-Read-and-Approve | N/A | 52 | 10.40 | N/A | 30s | N/A |
| **Total (4 of 5 scenarios)** | — | — | — | — | — | **369** |

**Table: Ingress = In-Cluster, Volume-Tier = Primary, Pod-Scale = 1, Run = Blended**

| Scenario | Unit-time | Locust-users-actual | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Register-Read | 5.83s | 12 | 4.80 | 0.823 | 30s | 25 |
| CR-Create | 0.69s | 12 | 1.20 | 1.744 | 30s | 52 |
| CR-Read-and-Approve | 1.89s | 12 | 2.40 | 1.270 | 30s | 38 |
| Intake-Create | 2.12s | 12 | 1.20 | 0.567 | 60s | 34 |
| Intake-Read-and-Approve | 3.64s | 12 | 2.40 | 0.659 | 30s | 20 |
| **Total** | — | — | — | — | — | **169** |

**Table: Ingress = In-Cluster, Volume-Tier = Primary, Pod-Scale = 2, Run = Blended**

| Scenario | Unit-time | Locust-users-actual | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Register-Read | 4.42s | 16 | 6.40 | 1.448 | 30s | 43 |
| CR-Create | 0.57s | 16 | 1.60 | 2.827 | 30s | 85 |
| CR-Read-and-Approve | 1.14s | 16 | 3.20 | 2.810 | 30s | 84 |
| Intake-Create | 2.21s | 16 | 1.60 | 0.723 | 60s | 43 |
| Intake-Read-and-Approve | 2.42s | 16 | 3.20 | 1.322 | 30s | 40 |
| **Total** | — | — | — | — | — | **295** |

**Table: Ingress = In-Cluster, Volume-Tier = Primary, Pod-Scale = 3, Run = Blended**

| Scenario | Unit-time | Locust-users-actual | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Register-Read | 6.51s | 32 | 12.80 | 1.966 | 30s | 59 |
| CR-Create | 0.76s | 32 | 3.20 | 4.192 | 30s | 126 |
| CR-Read-and-Approve | 1.82s | 32 | 6.40 | 3.515 | 30s | 105 |
| Intake-Create | 2.96s | 32 | 3.20 | 1.080 | 60s | 65 |
| Intake-Read-and-Approve | 6.53s | 32 | 6.40 | 0.981 | 30s | 29 |
| **Total** | — | — | — | — | — | **384** |

**Table: Ingress = In-Cluster, Volume-Tier = Stretch, Pod-Scale = 1, Run = Blended**

| Scenario | Unit-time | Locust-users-actual | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Register-Read | 5.33s | 12 | 4.80 | 0.901 | 30s | 27 |
| CR-Create | 0.70s | 12 | 1.20 | 1.724 | 30s | 52 |
| CR-Read-and-Approve | 1.63s | 12 | 2.40 | 1.473 | 30s | 44 |
| Intake-Create | 2.58s | 12 | 1.20 | 0.466 | 60s | 28 |
| Intake-Read-and-Approve | 3.02s | 12 | 2.40 | 0.794 | 30s | 24 |
| **Total** | — | — | — | — | — | **175** |

**Table: Ingress = In-Cluster, Volume-Tier = Stretch, Pod-Scale = 2, Run = Blended**

| Scenario | Unit-time | Locust-users-actual | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Register-Read | 6.16s | 24 | 9.60 | 1.559 | 30s | 47 |
| CR-Create | 0.72s | 24 | 2.40 | 3.340 | 30s | 100 |
| CR-Read-and-Approve | 1.33s | 24 | 4.80 | 3.605 | 30s | 108 |
| Intake-Create | 2.68s | 24 | 2.40 | 0.896 | 60s | 54 |
| Intake-Read-and-Approve | 4.22s | 24 | 4.80 | 1.137 | 30s | 34 |
| **Total** | — | — | — | — | — | **343** |

**Table: Ingress = In-Cluster, Volume-Tier = Stretch, Pod-Scale = 3, Run = Blended**

| Scenario | Unit-time | Locust-users-actual | Locust users | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|---:|
| Register-Read | 8.45s | 44 | 17.60 | 2.084 | 30s | 63 |
| CR-Create | 1.05s | 44 | 4.40 | 4.175 | 30s | 125 |
| CR-Read-and-Approve | 2.48s | 44 | 8.80 | 3.541 | 30s | 106 |
| Intake-Create | 3.61s | 44 | 4.40 | 1.220 | 60s | 73 |
| Intake-Read-and-Approve | 4.63s | 44 | 8.80 | 1.899 | 30s | 57 |
| **Total** | — | — | — | — | — | **424** |

### Soak

**Table: Soak (Step 3) — In-Cluster, Pod-Scale 3, 8h**

| Volume-Tier | SOAK_USERS | SOAK_MAX_RPS | RPS (t=0.5h→8h) | p50 (t=0.5h→8h) | p95 (t=0.5h→8h) | p99 (t=0.5h→8h) | Max response time (t=0.5h→8h) | Memory (min→max) | Memory growth | Errors (count/%) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Primary | 36 | 172 | 166.6→169.7 | 140ms→110ms | 300ms→260ms | 530ms→530ms | 1.2s→31.0s | 362→400 MiB | +7–10% | 34/4,733,071 (0.0007%) |
| Stretch | 36 | 172 | 149.2→151.2 | 140ms→130ms | 300ms→300ms | 550ms→590ms | 210.0s→285.0s | 372→420 MiB | +5–10% | 37/4,315,002 (0.00086%) |

Locust recorded this run's stats every 1 second (`soak_stats_history.csv`,
28,800 rows over 8h); the five checkpoints above (t = 0.5h, 2h, 4h, 6h, 8h)
are a representative subset chosen for this summary.

**Watch items:**

1. **Memory** — still rising at the 8h mark, not plateaued, at both tiers (+7–10% Primary, +5–10% Stretch).
2. **p99 drift** — Stretch's p99 drifts up +23% over the run; Primary's stays flat.
3. **Max latency** — Primary climbs to 31.0s, not yet isolated to an endpoint/pod. Stretch reaches 285s, isolated to `search_in_a_register` (register_read) — an order of magnitude worse than Primary.
4. **DB connection counts** — not captured for either tier (gap vs. deliverable 7).

**Table: Soak — per-scenario unit-time and RPS (In-Cluster, Pod-Scale 3, A = 36 Locust users)**

*Primary:*

| Scenario | B (Locust users) | Unit-time | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|
| Register-Read | 14.40 | 5.972s | 2.411 | 30s | 72 |
| CR-Create | 3.60 | 0.712s | 5.055 | 30s | 152 |
| CR-Read-and-Approve | 7.20 | 1.739s | 4.141 | 30s | 124 |
| Intake-Create | 3.60 | 2.474s | 1.455 | 60s | 87 |
| Intake-Read-and-Approve | 7.20 | 6.532s | 1.102 | 30s | 33 |
| **Total** | **36.00** | — | — | — | **468** |

*Stretch:*

| Scenario | B (Locust users) | Unit-time | RPS | Real time | Real users (computed) |
|---|---:|---:|---:|---:|---:|
| Register-Read | 14.40 | 7.409s | 1.943 | 30s | 58 |
| CR-Create | 3.60 | 0.905s | 3.977 | 30s | 119 |
| CR-Read-and-Approve | 7.20 | 2.241s | 3.212 | 30s | 96 |
| Intake-Create | 3.60 | 2.811s | 1.281 | 60s | 77 |
| Intake-Read-and-Approve | 7.20 | 3.659s | 1.968 | 30s | 59 |
| **Total** | **36.00** | — | — | — | **409** |

## Conclusion
