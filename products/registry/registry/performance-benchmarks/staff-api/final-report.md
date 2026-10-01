# Farmer Registry Staff API - Performance Test - Measurements & Analysis

Interpretation layer over [`raw-report.md`](raw-report.md) (every
measurement, verbatim, no interpretation) and, for the curated headline
endpoints, the `synthesize_templates/` CSVs under
[`../locust/api/templates/staff-api/`](../locust/api/templates/staff-api/)
once `scripts/synthesize_report.py` has run. See
[`test-scenarios.md`](test-scenarios.md) §3 for the Volume-Tier × Pod-Scale
matrix and the 3-Step + `db-sweep` model these map to.

**Pipeline:** raw Locust `--csv` output → `scripts/create_raw_report.py` →
[`raw-report.md`](raw-report.md) (all endpoints, no judgement) →
`scripts/synthesize_report.py` → curated `synthesize_templates/*.csv`
(headline endpoints + SLO + PASS/FAIL) → this document (interpretation,
cites both).

## The deliverables

| # | Output | Form | Source |
|---|--------|------|---|
| 1 | **Per-scenario capacity table** — endpoint, method, max sustainable RPS @ SLO, p50/p90/p95/p99/max, error %, saturating resource, per Volume-Tier/Pod-Scale cell | table | Step 1 (raw: [`raw-report.md`](raw-report.md); curated: `isolated-capacity.csv`) |
| 2 | **Per-pod resource profile** at max RPS (pod CPU, mem, DB conns) | table + graphs | Step 1 |
| 3 | **Latency-vs-RPS ("knee") and RPS-vs-users curves** | charts | Step 1 |
| 4 | **Blended capacity table**, per cell | table | Step 2 (raw: [`raw-report.md`](raw-report.md); curated: `blended-capacity.csv`) |
| 5 | **Horizontal scaling table + curve** — blended max RPS at Pod-Scale 1/2/3, same tier; efficiency; limiting factor | table + chart | *derived* — compare Step 2 across Pod-Scale |
| 6 | **Data-volume sensitivity** — capacity/latency vs Volume-Tier, same pod-scale | chart | *derived* — compare Step 1/2 across Volume-Tier |
| 7 | **Soak/endurance report** — RPS, p95, error rate, pod memory, DB conns over 8h; memory-trend verdict | time-series graphs | Step 3 (raw: [`raw-report.md`](raw-report.md); curated: `soak.csv`) |
| 8 | **DB capacity table** — threshold RPS + first bottleneck per tuning/volume/VM scenario; top slow queries | table | `db-sweep` (raw: [`raw-report.md`](raw-report.md); curated: `db-sweep.csv`) |
| 9 | **Bottleneck & tuning findings** — what saturated first; config changes that moved it (worker count, pool size, indexes, PgBouncer, max_connections, gp3 IOPS) | narrative | all |
| 10 | **Capacity / sizing model** — the headline business output (below) | formula/table | Synthesis |
| 11 | **Pass/fail vs SLO/NFR** | table | Synthesis |
| 12 | **Methodology + reproducible assets** — Locust scripts, env spec, versions, seed manifest | doc + repo | all |

Async pipeline throughput (Celery) is **not** a current deliverable — see
[`test-scenarios.md`](test-scenarios.md) §1/§2.

## The capacity / sizing model (headline output)

> *On the 3-node production profile (compute `m5a.4xlarge`, host-PG
> `t3a.2xlarge`), one `staff-portal-api` pod (spec:
> [`environment-topology.md`](../environment-topology.md)) sustains **R** RPS of
> the blended workload (Step 2) at p95 ≤ SLO over the `primary` (10M farmer)
> Volume-Tier. At Pod-Scale 3 that becomes **R₃** RPS (efficiency **e**). The
> host PostgreSQL becomes the bottleneck at **D** RPS (`db-sweep`, tuned +
> PgBouncer), driven by `<bottleneck>`. Therefore, to serve a target of **T**
> RPS over **V** million records at the SLOs, provision **⌈T/R⌉** app pods
> (bounded by the DB ceiling D) and a DB of **`<size>`** with
> **`<max_connections>`** via PgBouncer.*

Not yet computable — requires a ramp-to-failure blended run (Measurements,
below) and the DB-ceiling sweep (`db-sweep`, still pending).

### 1. Executive summary
- **Reported improvement, code confirmed applied:** the iam-core
  JWKS/OIDC-metadata cache fix was reported to raise Pod-1 (2 vCPU / 2 GB)
  capacity from ~10 to 30+ concurrent Locust users. The fix (`iam` commit
  `4c1888b`, G2P-5647) is in this checkout — `iam` is now on its
  `performance-test` branch — see §6, item 3.
- **Headline:** Pod-Scale 1 (spec: [`environment-topology.md`](../environment-topology.md)) sustains **≥71.0 RPS** in-cluster / **≥66.3 RPS** end-to-end blended (Step 2) over Volume-Tier `primary`, near-zero to zero failures — both measured at a **fixed concurrency** (12 / 20 users respectively), not a ramp-to-failure, so these are floors, not the SLO-confirmed ceiling (Measurements → Blended).
- **Scaling:** Pod-Scale 3 → **123.7 RPS** in-cluster / **122.3 RPS** end-to-end (efficiency **≈58%** / **≈61%** of linear) — both from the same fixed-concurrency data (§5); the two ingresses reach almost the same RPS ceiling, so the RP isn't yet the limiting factor at this load.
- **Data-volume sensitivity (`primary` 10M → `stretch` 50M):** blended
  throughput/p95 are essentially flat at end-to-end and at in-cluster
  Pod-1 (§5); in-cluster Pod-3 shows a real ≈18% RPS drop (123.7→101.5)
  and ≈14% p95 increase. The more striking signal is in the soak data
  (Measurements → In-Cluster → Soak): tail latency (max response time)
  reaches 285s at `stretch` vs. 31s at `primary` over the same 8h window,
  with a real p99 creep `primary` didn't show — throughput and p50/p95
  hold, but the tail degrades meaningfully at 5× the record count.
- **DB ceiling:** **___ RPS** (`db-sweep`, tuned + PgBouncer), limited by **______**.
- **Sizing model:** to serve **T RPS** over **V M** records → **___ app pods + DB `___`**.
- **Verdict vs SLO/NFR:** PASS / FAIL — _____.

### 2. Environment & methodology
Nodes, pod specs, and PostgreSQL/PgBouncer configuration —
see [`environment-topology.md`](../environment-topology.md).

Tested this round: `smoke` (end-to-end only), and `primary`/`stretch`
(both end-to-end and in-cluster), Pod-Scale 1-3, Step 1 (isolated) and
Step 2 (blended, fixed-concurrency — Measurements below). Step 3 (soak):
in-cluster Pod-3 at both `primary` and `stretch`, full 8h each. `stress`
and `db-sweep` pending. Load tool: Locust 2.46.3.

- **Methodology finding from the dry run:** the results-folder/template
  ingress label was initially wrong (`in-cluster` when the run actually
  went `end-to-end` through the public perftest hostname) — corrected;
  results are now segmented by ingress at the top level
  (`results/staff-api/<ingress>/...`).
- **Known upstream bug, resolved by exclusion:** in the `smoke` dry run,
  `register_read`'s `get_record_history` call failed 33/33 (`SYS-ERR-001`)
  — see [`seeding-design.md`](../seeding-design.md)
  (`change_request_source.value` on a plain `String` column). The call was
  dropped from `register_read`'s task code (`locust/api/env.sh`,
  `locust/api/shared/slo_shape.py`) — it doesn't appear in the Smoke or
  Primary runs.

### 3. Pod & database configuration
Pod specs (`staff-portal-api` 2 vCPU / 2 GB, AWE 2 vCPU / 2 GB, Keycloak
1 vCPU / 1 GB) and PostgreSQL/PgBouncer tuning — see
[`environment-topology.md`](../environment-topology.md)'s "Pod
configuration" and "PostgreSQL & PgBouncer configuration" sections.

### 4. Methodology: capacity calculations
Converting Locust throughput into a real-user-equivalent figure uses
Little's Law:

```
Real concurrent users = (unit completions/sec) × (real completion time, seconds)
```

**The unit is one fully-handled record, not one `@task` iteration** — the
realistic single-record journey a case worker performs: search, land on
one record, fire every API that record's detail view needs, then (where
applicable) act on it:

| Scenario | One unit of work |
|---|---|
| register_read | search → zoom into 1 record → every tab, every pending CR on that tab, every version date on that tab |
| cr_create | search → pick 1 record → its tabs/sections → edit 1 section → create the CR |
| cr_read_and_approve | search → pick 1 CR → its documents/schema/dedup/tasks → approve |
| intake_create | render the form → save every section → fetch → finalize |
| intake_read_and_approve | search → pick 1 submission → its documents/dedup/tasks → approve |

Each API's contribution to "total time for 1 unit" is its own average
response time × how many times it fires per unit (`endpoint's Request
Count ÷ anchor's Request Count`, same pod's CSV) — several calls are
structurally repeated per record (a record has several tabs; a tab has
however many pending items) or repeated by the test's own
search/candidate-discovery process.

**RPS = Locust users (peak) ÷ Total time for 1 unit** — not the anchor
endpoint's own directly-measured Requests/s. `shared/base_user.py`'s
`wait_time = between(0.5, 2.0)` pauses every simulated user between
`@task` iterations, throttling any directly-observed Requests/s figure
without that pause reflecting anything about `T_real`. Summing each API's
own average response time excludes `wait_time` by construction (the pause
falls between tasks, never inside a response time), so `Locust users ÷
Total time for 1 unit` gives the zero-wait rate directly. This method is
used for every scenario and every Step, isolated and blended alike (the
blended variant is in Measurements → Blended → Estimating Real Concurrent
Users).

`cr_create`'s anchor is two mutually exclusive endpoints
(`create_change_request` / `create_change_request_for_core_data` — every
CR creation calls exactly one). Each variant's average response time is
folded into "total time for 1 unit" as a share-weighted average; no
separate RPS handling is needed since `Total time` already accounts for
both variants.

`N` (each scenario's `Locust users (peak, this run)`) is that scenario's
own peak `User Count` from its `_stats_history.csv`.

Isolated-tier figures below are each scenario's ceiling **in isolation** —
the pod runs only that workload. A pod serving the real mixed workload
contends for the same DB connections, CPU, and AWE capacity across all
five scenarios at once, so the real mixed-workload concurrent-user number
is lower than each isolated figure — that's what Step 2 (blended) below
measures directly. Separately, this per-record throughput figure is a
distinct question from the ramp shape's own breach ceiling: the ramp still
freezes at a lower user count at Pod-Scale 3 than Pod-Scale 2, and AWE
logs connection-reset errors under load — a ceiling effect, not visible in
this typical-case throughput number. Both are true at once: more
records/CRs/submissions get handled per second as pods scale, while the
ceiling before failures start is still capped by AWE's fixed capacity.

## Measurements

Per-endpoint source: `Step: 1-isolated` / `2-blended` sections of
[`raw-report.md`](raw-report.md); curated headline-endpoint SLO/PASS-FAIL:
`synthesize_templates/isolated-capacity.csv` /
`blended-capacity.csv` (after `scripts/synthesize_report.py`).
Latency-vs-RPS "knee" charts are pending — a single-step run doesn't
produce a ramp. Every Blended (Step 2) figure below is a
**fixed-concurrency floor**, not a ramp-to-failure SLO ceiling, unless
noted otherwise.

### End-to-End

#### Volume-Tier: Smoke

##### Isolated (Step 1)
Two effects are visible in this tier's data.

Endpoints that stay inside registry-platform improve as pods scale, as
expected — less contention per pod:

| Endpoint | Pod-1 p95 | Pod-2 p95 | Pod-3 p95 |
|---|---|---|---|
| `get_change_request` | 860ms | 790ms | 620ms |
| `get_deduplication_register_results` | 780ms | 760ms | 600ms |

Endpoints that call out to AWE get worse as pods scale — the bottleneck is
the AWE hop, not registry-platform's own DB/CPU (root cause in §6):

| Endpoint | Pod-1 p95 | Pod-2 p95 | Pod-3 p95 |
|---|---|---|---|
| `list_tasks_for_request` | 920ms | 1100ms | 1100ms |
| `submit_task_decision` | 910ms | 980ms | 1000ms |

###### register_read — 1 register record fully read

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_a_register` | 370ms (×1.00) | 374ms (×1.00) | 339ms (×1.00) |
| `get_subject_record` | 244ms (×1.00) | 241ms (×1.00) | 208ms (×1.00) |
| `get_all_tabs` | 263ms (×1.00) | 256ms (×1.00) | 214ms (×1.00) |
| `get_tab_sections` | 270ms (×6.73) | 266ms (×6.81) | 224ms (×6.84) |
| `get_tab_records` | 320ms (×6.72) | 312ms (×6.80) | 262ms (×6.83) |
| `get_number_of_pending_change_requests` | 244ms (×6.70) | 240ms (×6.80) | 201ms (×6.82) |
| `get_change_requests` | 268ms (×6.69) | 266ms (×6.79) | 222ms (×6.82) |
| `get_change_request_documents` | 220ms (×1.87) | 237ms (×2.49) | 201ms (×1.96) |
| `get_section_ui_schema` | 223ms (×1.86) | 235ms (×2.49) | 201ms (×1.96) |
| `get_change_request` | 266ms (×1.86) | 288ms (×2.48) | 250ms (×1.95) |
| `list_tasks_for_request` | 268ms (×1.86) | 307ms (×2.48) | 291ms (×1.95) |
| `get_deduplication_change_request_results` | 224ms (×1.86) | 241ms (×2.48) | 207ms (×1.95) |
| `get_deduplication_register_results` | 234ms (×1.86) | 234ms (×2.48) | 205ms (×1.95) |
| `get_number_of_versions` | 262ms (×6.68) | 259ms (×6.77) | 214ms (×6.80) |
| `get_version_dates` | 258ms (×6.68) | 250ms (×6.77) | 209ms (×6.80) |
| `get_versions_for_a_date` | 263ms (×3.99) | 270ms (×4.22) | 220ms (×4.36) |
| **Total time for 1 unit** | **15.45s** | **16.66s** | **13.45s** |
| Locust users (peak, this run) | 28 | 48 | 56 |
| **RPS (Locust users ÷ Total time)** | **1.812** | **2.880** | **4.164** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **54** | **86** | **125** |

###### cr_create — 1 change request effected

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_a_register` | 382ms (×0.36) | 336ms (×0.35) | 296ms (×0.36) |
| `get_subject_record` | 291ms (×0.18) | 226ms (×0.18) | 178ms (×0.18) |
| `get_all_sections` | 602ms (×0.18) | 516ms (×0.18) | 422ms (×0.18) |
| `get_all_tabs` | 285ms (×0.18) | 246ms (×0.18) | 185ms (×0.18) |
| `get_tab_sections` | 298ms (×1.25) | 248ms (×1.26) | 196ms (×1.28) |
| `get_tab_records` | 354ms (×1.25) | 294ms (×1.25) | 232ms (×1.27) |
| `get_attribute_values` | 273ms (×0.05) | 245ms (×0.05) | 195ms (×0.04) |
| `create_change_request` | 564ms (93% of CRs) | 509ms (94% of CRs) | 518ms (94% of CRs) |
| `create_change_request_for_core_data` | 584ms (7% of CRs) | 566ms (6% of CRs) | 543ms (6% of CRs) |
| **Total time for 1 unit** | **1.75s** | **1.50s** | **1.32s** |
| Locust users (peak, this run) | 24 | 36 | 36 |
| **RPS (Locust users ÷ Total time)** | **13.741** | **23.948** | **27.171** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **412** | **718** | **815** |

###### cr_read_and_approve — 1 change request approved

_Captured before the change that limits `cr_read_and_approve` to pending
tasks only — expect the ×/unit ratios below (and the derived RPS/real-user
figures) to shift once this scenario is re-run._

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_change_request` | 374ms (×2.17) | 415ms (×1.01) | 314ms (×1.17) |
| `get_change_request_documents` | 306ms (×5.09) | 295ms (×3.07) | 166ms (×3.03) |
| `get_section_ui_schema` | 306ms (×5.09) | 296ms (×3.07) | 164ms (×3.03) |
| `get_change_request` | 374ms (×5.07) | 360ms (×3.06) | 205ms (×3.03) |
| `get_deduplication_change_request_results` | 312ms (×5.06) | 302ms (×3.06) | 168ms (×3.03) |
| `get_deduplication_register_results` | 312ms (×5.06) | 299ms (×3.06) | 167ms (×3.02) |
| `list_tasks_for_request` | 364ms (×5.05) | 370ms (×3.05) | 294ms (×3.02) |
| `submit_task_decision` | 480ms (×1.00) | 453ms (×1.00) | 377ms (×1.00) |
| **Total time for 1 unit** | **11.30s** | **6.76s** | **4.27s** |
| Locust users (peak, this run) | 28 | 48 | 32 |
| **RPS (Locust users ÷ Total time)** | **2.478** | **7.104** | **7.495** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **74** | **213** | **225** |

###### intake_create — 1 intake submission created

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `render_intake_form` | 257ms (×1.03) | 205ms (×1.02) | 162ms (×1.02) |
| `save_intake_form_submission` | 530ms (×9.17) | 407ms (×9.12) | 304ms (×9.13) |
| `get_intake_form_submission` | 383ms (×1.01) | 298ms (×1.00) | 225ms (×1.00) |
| `finalize_intake_form_submission` | 734ms (×1.00) | 613ms (×1.00) | 510ms (×1.00) |
| **Total time for 1 unit** | **6.24s** | **4.84s** | **3.67s** |
| Locust users (peak, this run) | 20 | 28 | 28 |
| **RPS (Locust users ÷ Total time)** | **3.204** | **5.790** | **7.623** |
| T_real | 60s | 60s | 60s |
| **Real concurrent users** | **192** | **347** | **457** |

###### intake_read_and_approve — 1 intake submission approved

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_intake_form_submissions` | 547ms (×16.71) | 556ms (×8.84) | 332ms (×1.61) |
| `get_intake_form_submission` | 160ms (×1.05) | 213ms (×1.08) | 233ms (×1.22) |
| `get_intake_form_documents` | 107ms (×1.05) | 145ms (×1.08) | 161ms (×1.22) |
| `get_deduplication_intake_form_register_results` | 114ms (×1.05) | 151ms (×1.08) | 162ms (×1.22) |
| `get_deduplication_intake_form_intake_form_results` | 114ms (×1.05) | 147ms (×1.08) | 161ms (×1.22) |
| `list_tasks_for_request` | 175ms (×1.05) | 226ms (×1.08) | 294ms (×1.22) |
| `submit_task_decision` | 217ms (×1.00) | 280ms (×1.00) | 342ms (×1.00) |
| **Total time for 1 unit** | **10.07s** | **6.14s** | **2.11s** |
| Locust users (peak, this run) | 24 | 40 | 32 |
| **RPS (Locust users ÷ Total time)** | **2.384** | **6.509** | **15.187** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **72** | **195** | **456** |

#### Volume-Tier: Primary

##### Isolated (Step 1)
###### register_read — 1 register record fully read

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_a_register` | 171ms (×1.00) | 159ms (×1.00) | 174ms (×1.00) |
| `get_subject_record` | 155ms (×1.00) | 138ms (×1.00) | 140ms (×1.00) |
| `get_all_tabs` | 126ms (×1.00) | 107ms (×1.00) | 114ms (×1.00) |
| `get_tab_sections` | 172ms (×6.94) | 149ms (×6.94) | 155ms (×6.95) |
| `get_tab_records` | 206ms (×6.94) | 175ms (×6.94) | 182ms (×6.95) |
| `get_number_of_pending_change_requests` | 157ms (×6.94) | 134ms (×6.94) | 139ms (×6.94) |
| `get_change_requests` | 175ms (×6.93) | 149ms (×6.93) | 155ms (×6.94) |
| `get_change_request_documents` | 135ms (×0.08) | 139ms (×0.03) | 134ms (×0.04) |
| `get_section_ui_schema` | 121ms (×0.08) | 161ms (×0.03) | 132ms (×0.04) |
| `get_change_request` | 168ms (×0.08) | 204ms (×0.03) | 179ms (×0.04) |
| `list_tasks_for_request` | 149ms (×0.08) | 175ms (×0.03) | 164ms (×0.04) |
| `get_deduplication_change_request_results` | 137ms (×0.08) | 154ms (×0.03) | 130ms (×0.04) |
| `get_deduplication_register_results` | 135ms (×0.08) | 156ms (×0.03) | 144ms (×0.04) |
| `get_number_of_versions` | 168ms (×6.93) | 144ms (×6.93) | 149ms (×6.94) |
| `get_version_dates` | 164ms (×6.93) | 139ms (×6.93) | 144ms (×6.94) |
| `get_versions_for_a_date` | 172ms (×5.83) | 148ms (×5.91) | 152ms (×5.92) |
| **Total time for 1 unit** | **8.75s** | **7.48s** | **7.78s** |
| Locust users (peak, this run) | 20 | 32 | 44 |
| **RPS (Locust users ÷ Total time)** | **2.286** | **4.278** | **5.655** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **69** | **128** | **170** |

###### cr_create — 1 change request effected

`get_attribute_values` recorded 0 requests in this run (unlike Smoke) and
is excluded from the chain below rather than assumed absent going forward.

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_a_register` | 210ms (×0.39) | 191ms (×0.39) | 222ms (×0.39) |
| `get_subject_record` | 177ms (×0.20) | 162ms (×0.20) | 179ms (×0.20) |
| `get_all_sections` | 191ms (×0.20) | 186ms (×0.20) | 201ms (×0.20) |
| `get_all_tabs` | 136ms (×0.20) | 125ms (×0.20) | 138ms (×0.20) |
| `get_tab_sections` | 190ms (×1.40) | 173ms (×1.40) | 193ms (×1.40) |
| `get_tab_records` | 225ms (×1.40) | 208ms (×1.40) | 228ms (×1.40) |
| `create_change_request` | 341ms (93% of CRs) | 320ms (93% of CRs) | 361ms (93% of CRs) |
| `create_change_request_for_core_data` | 359ms (7% of CRs) | 353ms (7% of CRs) | 395ms (7% of CRs) |
| **Total time for 1 unit** | **1.11s** | **1.02s** | **1.14s** |
| Locust users (peak, this run) | 20 | 32 | 48 |
| **RPS (Locust users ÷ Total time)** | **18.083** | **31.249** | **42.007** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **542** | **937** | **1260** |

###### cr_read_and_approve — 1 change request approved

_Captured before the change that limits `cr_read_and_approve` to pending
tasks only — expect the ×/unit ratios below (and the derived RPS/real-user
figures) to shift once this scenario is re-run._

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_change_request` | 260ms (×0.32) | 287ms (×0.32) | 380ms (×0.28) |
| `get_change_request_documents` | 158ms (×2.41) | 152ms (×2.20) | 186ms (×1.95) |
| `get_section_ui_schema` | 158ms (×2.41) | 151ms (×2.20) | 186ms (×1.94) |
| `get_change_request` | 196ms (×2.41) | 188ms (×2.20) | 229ms (×1.94) |
| `get_deduplication_change_request_results` | 160ms (×2.41) | 155ms (×2.20) | 189ms (×1.94) |
| `get_deduplication_register_results` | 165ms (×2.41) | 154ms (×2.20) | 189ms (×1.94) |
| `list_tasks_for_request` | 165ms (×2.40) | 159ms (×2.19) | 192ms (×1.94) |
| `submit_task_decision` | 201ms (×1.00) | 198ms (×1.00) | 236ms (×1.00) |
| **Total time for 1 unit** | **2.70s** | **2.40s** | **2.62s** |
| Locust users (peak, this run) | 16 | 28 | 48 |
| **RPS (Locust users ÷ Total time)** | **5.927** | **11.688** | **18.327** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **178** | **351** | **550** |

###### intake_create — 1 intake submission created

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `render_intake_form` | 192ms (×1.06) | 160ms (×1.01) | 175ms (×1.01) |
| `save_intake_form_submission` | 364ms (×9.06) | 280ms (×9.05) | 319ms (×9.04) |
| `get_intake_form_submission` | 271ms (×1.00) | 214ms (×1.00) | 240ms (×1.00) |
| `finalize_intake_form_submission` | 350ms (×1.00) | 289ms (×1.00) | 326ms (×1.00) |
| **Total time for 1 unit** | **4.12s** | **3.20s** | **3.63s** |
| Locust users (peak, this run) | 20 | 28 | 44 |
| **RPS (Locust users ÷ Total time)** | **4.854** | **8.759** | **12.138** |
| T_real | 60s | 60s | 60s |
| **Real concurrent users** | **291** | **526** | **728** |

###### intake_read_and_approve — 1 intake submission approved

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_intake_form_submissions` | 190ms (×1.85) | 222ms (×1.54) | 198ms (×14.37) |
| `get_intake_form_submission` | 227ms (×2.37) | 237ms (×2.45) | 205ms (×1.90) |
| `get_intake_form_documents` | 159ms (×2.37) | 166ms (×2.45) | 139ms (×1.90) |
| `get_deduplication_intake_form_register_results` | 161ms (×2.37) | 166ms (×2.44) | 140ms (×1.90) |
| `get_deduplication_intake_form_intake_form_results` | 161ms (×2.37) | 168ms (×2.44) | 141ms (×1.90) |
| `list_tasks_for_request` | 162ms (×2.37) | 170ms (×2.44) | 148ms (×1.90) |
| `submit_task_decision` | 197ms (×1.00) | 206ms (×1.00) | 182ms (×1.00) |
| **Total time for 1 unit** | **2.61s** | **2.77s** | **4.50s** |
| Locust users (peak, this run) | 24 | 40 | 64 |
| **RPS (Locust users ÷ Total time)** | **9.199** | **14.453** | **14.224** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **276** | **434** | **427** |

Pod-3's `search_in_intake_form_submissions` ratio (×14.37, vs. ×1.85/×1.54
at Pod-1/Pod-2) is an outlier worth confirming on re-run before trusting
this pod's total — everything else in the chain moves in the expected
direction.

##### Blended (Step 2)
| Pod-Scale | Concurrent users | Requests | Failures | p95 | Aggregated RPS |
|---|---|---|---|---|---|
| Pod-1 | 20 | 29,216 | 2 | 420ms | 66.26 |
| Pod-2 | 28 | 50,486 | 3 | 440ms | 93.39 |
| Pod-3 | 48 | 62,520 | 2 | 290ms | 122.26 |

Scaling efficiency vs. Pod-1: Pod-2 ≈70% of linear (93.39 ÷ (2×66.26)),
Pod-3 ≈61% of linear (122.26 ÷ (3×66.26)) — both below the isolated-tier
scaling seen above, consistent with AWE being a shared, fixed-capacity
bottleneck under the blended mix.

**Estimating real concurrent users:** the blended run reports one pool of
Locust users; it doesn't break down which real-user-equivalent load that
represents, since (unlike the isolated tables above) its per-endpoint
stats mix requests from all 5 scenarios. Two known quantities are enough
to estimate it: the blend's **weight distribution** (register_read 40%,
cr_read_and_approve 20%, intake_read_and_approve 20%, cr_create 10%,
intake_create 10% — Locust spawns users by weight, so a blended run frozen
at `A` total Locust users has `weight × A` simulated users of each
scenario type), and each scenario's **per-unit server time**, computed the
same way as §4 (summing each API's own average response time, weighted by
fires-per-unit) for the same `wait_time`-independence reason given there:

```
A = total Locust users in the blended run (this cell)
B (per scenario) = weight(scenario) × A
C (per scenario) = Σ [ avg ms(endpoint) × fires-per-unit(endpoint, scenario) ] over that scenario's chain
D (per scenario) = B ÷ C           — RPS implied by B simulated users each taking C seconds/unit
E (per scenario) = T_real(scenario)
real_users(scenario) = D × E
real_users(blended cell) = Σ real_users(scenario)
```

`C` is measured **from the blended run itself** (`raw-report.md`'s
`2-blended` table), so it reflects actual blended-load contention (all 5
scenarios sharing DB/CPU/AWE capacity), not isolated-tier conditions. Each
endpoint's **fires-per-unit ratio** still comes from isolated data (§4's
×N.NN multiplier) and can't be avoided: several endpoints are shared
across scenarios in the blend (`get_subject_record` in register_read *and*
cr_create; `submit_task_decision` in cr_read_and_approve *and*
intake_read_and_approve), so the blended run's raw request *counts* for
those endpoints mix multiple scenarios' traffic with no way to attribute a
call back to its scenario — a ratio computed from blended counts would be
contaminated. Average response time doesn't have this problem (an
endpoint's latency under blended load is the same regardless of which
scenario's user called it), so only `C` is sourced from the blended run;
the fires-per-unit structure stays from isolated data as a workflow
constant.

*Pod-1 (A = 20):*

| Scenario | B (Locust users) | C (time, blended) | D = B÷C (RPS) | E (T_real) | Real users = D×E |
|---|---:|---:|---:|---:|---:|
| register_read | 8.00 | 10.18s | 0.786 | 30s | 23.6 |
| cr_create | 2.00 | 1.17s | 1.712 | 30s | 51.4 |
| cr_read_and_approve | 4.00 | 2.94s | 1.360 | 30s | 40.8 |
| intake_create | 2.00 | 3.98s | 0.503 | 60s | 30.2 |
| intake_read_and_approve | 4.00 | 3.17s | 1.262 | 30s | 37.9 |
| **Total** | **20.00** | — | — | — | **≈183.8** |

Blended ratio: 183.8 ÷ 20 = **9.2×**

*Pod-2 (A = 28):*

| Scenario | B (Locust users) | C (time, blended) | D = B÷C (RPS) | E (T_real) | Real users = D×E |
|---|---:|---:|---:|---:|---:|
| register_read | 11.20 | 8.20s | 1.365 | 30s | 41.0 |
| cr_create | 2.80 | 0.97s | 2.895 | 30s | 86.9 |
| cr_read_and_approve | 5.60 | 2.29s | 2.450 | 30s | 73.5 |
| intake_create | 2.80 | 3.37s | 0.831 | 60s | 49.9 |
| intake_read_and_approve | 5.60 | 2.51s | 2.227 | 30s | 66.8 |
| **Total** | **28.00** | — | — | — | **≈318.0** |

Blended ratio: 318.0 ÷ 28 = **11.4×**

*Pod-3 (A = 48):*

| Scenario | B (Locust users) | C (time, blended) | D = B÷C (RPS) | E (T_real) | Real users = D×E |
|---|---:|---:|---:|---:|---:|
| register_read | 19.20 | 9.32s | 2.060 | 30s | 61.8 |
| cr_create | 4.80 | 1.10s | 4.378 | 30s | 131.4 |
| cr_read_and_approve | 9.60 | 2.36s | 4.074 | 30s | 122.2 |
| intake_create | 4.80 | 3.73s | 1.287 | 60s | 77.2 |
| intake_read_and_approve | 9.60 | 4.76s | 2.018 | 30s | 60.6 |
| **Total** | **48.00** | — | — | — | **≈453.1** |

Blended ratio: 453.1 ÷ 48 = **9.4×**

#### Volume-Tier: Stretch

##### Isolated (Step 1)
###### register_read — 1 register record fully read

Pod-1's run found **zero pending change requests on any tab** — all 6
CR-related endpoints (`get_change_request_documents` through
`get_deduplication_register_results`) recorded no calls at all, so this
pod's chain, and its "Total time," excludes them entirely (understating
the true per-record cost for this pod specifically). Pod-2/Pod-3 found
them, at a much lower ratio (×0.01, vs. Primary's ×1.86-2.49) — at 50M
records the CR backlog this scenario's tabs encounter is sparse relative
to the record count, a real data-volume effect, not a bug.

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_a_register` | 196ms (×1.00) | 230ms (×1.00) | 398ms (×1.00) |
| `get_subject_record` | 154ms (×1.00) | 160ms (×1.00) | 175ms (×1.00) |
| `get_all_tabs` | 126ms (×1.00) | 120ms (×1.00) | 138ms (×1.00) |
| `get_tab_sections` | 170ms (×6.92) | 171ms (×6.94) | 187ms (×6.94) |
| `get_tab_records` | 205ms (×6.92) | 208ms (×6.93) | 222ms (×6.94) |
| `get_number_of_pending_change_requests` | 153ms (×6.92) | 152ms (×6.93) | 171ms (×6.94) |
| `get_change_requests` | 171ms (×6.91) | 172ms (×6.93) | 188ms (×6.93) |
| `get_change_request_documents` | — (0 calls) | 150ms (×0.01) | 195ms (×0.00) |
| `get_section_ui_schema` | — (0 calls) | 182ms (×0.01) | 171ms (×0.00) |
| `get_change_request` | — (0 calls) | 235ms (×0.01) | 256ms (×0.00) |
| `list_tasks_for_request` | — (0 calls) | 201ms (×0.01) | 219ms (×0.00) |
| `get_deduplication_change_request_results` | — (0 calls) | 168ms (×0.01) | 180ms (×0.00) |
| `get_deduplication_register_results` | — (0 calls) | 178ms (×0.01) | 280ms (×0.00) |
| `get_number_of_versions` | 168ms (×6.91) | 166ms (×6.93) | 184ms (×6.93) |
| `get_version_dates` | 162ms (×6.91) | 161ms (×6.93) | 177ms (×6.93) |
| `get_versions_for_a_date` | 168ms (×5.84) | 170ms (×5.88) | 186ms (×5.88) |
| **Total time for 1 unit** | **8.57s** | **8.66s** | **9.63s** |
| Locust users (peak, this run) | 20 | 36 | 56 |
| **RPS (Locust users ÷ Total time)** | **2.334** | **4.158** | **5.812** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **70** | **125** | **174** |

###### cr_create — 1 change request effected

`get_attribute_values` again recorded 0 requests (as at Primary tier) and
is excluded.

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_a_register` | 815ms (×0.40) | 262ms (×0.20) | 523ms (×0.20) |
| `get_subject_record` | 169ms (×0.20) | 221ms (×0.20) | 222ms (×0.20) |
| `get_all_sections` | 181ms (×0.20) | 229ms (×0.20) | 257ms (×0.20) |
| `get_all_tabs` | 124ms (×0.20) | 168ms (×0.20) | 174ms (×0.20) |
| `get_tab_sections` | 178ms (×1.40) | 235ms (×1.40) | 240ms (×1.40) |
| `get_tab_records` | 215ms (×1.40) | 281ms (×1.40) | 277ms (×1.40) |
| `create_change_request` | 333ms (93% of CRs) | 422ms (93% of CRs) | 417ms (93% of CRs) |
| `create_change_request_for_core_data` | 360ms (7% of CRs) | 454ms (7% of CRs) | 445ms (7% of CRs) |
| **Total time for 1 unit** | **1.31s** | **1.32s** | **1.38s** |
| Locust users (peak, this run) | 24 | 44 | 56 |
| **RPS (Locust users ÷ Total time)** | **18.353** | **33.215** | **40.594** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **551** | **996** | **1218** |

Pod-1's `search_in_a_register` ratio (×0.40, double Pod-2/Pod-3's ×0.20) is
an outlier worth confirming on re-run.

###### cr_read_and_approve — 1 change request approved

_Captured before the change that limits `cr_read_and_approve` to pending
tasks only — expect the ×/unit ratios below (and the derived RPS/real-user
figures) to shift once this scenario is re-run._

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_change_request` | 199ms (×1.25) | 189ms (×0.61) | 320ms (×0.43) |
| `get_change_request_documents` | 180ms (×3.20) | 155ms (×2.75) | 182ms (×2.22) |
| `get_section_ui_schema` | 179ms (×3.20) | 154ms (×2.75) | 180ms (×2.22) |
| `get_change_request` | 222ms (×3.20) | 192ms (×2.75) | 225ms (×2.22) |
| `get_deduplication_change_request_results` | 185ms (×3.20) | 156ms (×2.75) | 183ms (×2.22) |
| `get_deduplication_register_results` | 184ms (×3.20) | 156ms (×2.75) | 184ms (×2.22) |
| `list_tasks_for_request` | 179ms (×3.19) | 157ms (×2.75) | 189ms (×2.21) |
| `submit_task_decision` | 212ms (×1.00) | 200ms (×1.00) | 229ms (×1.00) |
| **Total time for 1 unit** | **4.07s** | **2.98s** | **2.90s** |
| Locust users (peak, this run) | 24 | 32 | 48 |
| **RPS (Locust users ÷ Total time)** | **5.899** | **10.734** | **16.557** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **177** | **322** | **497** |

###### intake_create — 1 intake submission created

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `render_intake_form` | 244ms (×1.01) | 168ms (×1.01) | 171ms (×1.01) |
| `save_intake_form_submission` | 450ms (×9.07) | 319ms (×9.03) | 323ms (×9.03) |
| `get_intake_form_submission` | 334ms (×1.00) | 241ms (×1.00) | 246ms (×1.00) |
| `finalize_intake_form_submission` | 422ms (×1.00) | 323ms (×1.00) | 333ms (×1.00) |
| **Total time for 1 unit** | **5.08s** | **3.61s** | **3.67s** |
| Locust users (peak, this run) | 24 | 32 | 44 |
| **RPS (Locust users ÷ Total time)** | **4.721** | **8.864** | **11.999** |
| T_real | 60s | 60s | 60s |
| **Real concurrent users** | **283** | **532** | **720** |

###### intake_read_and_approve — 1 intake submission approved

**Pod-3 completed zero approvals during this isolated run** —
`submit_task_decision` and every other endpoint in this scenario's chain
recorded 0 calls, despite 64 Locust users running for the full step. This
is a genuine capacity finding, not a missing-data artifact: at 50M
records and Pod-Scale 3, the search-and-approve workflow never found (or
never finished processing) a single approvable submission in the window.
No RPS/real-user figure is computable for this cell.

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_intake_form_submissions` | 248ms (×3.49) | 194ms (×2.70) | — (0 calls) |
| `get_intake_form_submission` | 277ms (×3.67) | 235ms (×2.24) | — (0 calls) |
| `get_intake_form_documents` | 198ms (×3.67) | 163ms (×2.24) | — (0 calls) |
| `get_deduplication_intake_form_register_results` | 202ms (×3.67) | 165ms (×2.24) | — (0 calls) |
| `get_deduplication_intake_form_intake_form_results` | 202ms (×3.66) | 165ms (×2.24) | — (0 calls) |
| `list_tasks_for_request` | 194ms (×3.66) | 165ms (×2.24) | — (0 calls) |
| `submit_task_decision` | 226ms (×1.00) | 203ms (×1.00) | — (0 calls) |
| **Total time for 1 unit** | **5.03s** | **2.73s** | **N/A** |
| Locust users (peak, this run) | 24 | 44 | 64 |
| **RPS (Locust users ÷ Total time)** | **4.774** | **16.134** | **N/A** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **143** | **484** | **N/A** |

##### Blended (Step 2)
| Pod-Scale | Concurrent users | Requests | Failures | p95 | Aggregated RPS |
|---|---|---|---|---|---|
| Pod-1 | 20 | 29,886 | 0 | 410ms | 66.25 |
| Pod-2 | 32 | 59,436 | 4 | 590ms | 94.14 |
| Pod-3 | 52 | 67,102 | 1 | 290ms | 124.13 |

Scaling efficiency vs. Pod-1: Pod-2 ≈71% of linear (94.14 ÷ (2×66.25)),
Pod-3 ≈62% of linear (124.13 ÷ (3×66.25)) — close to Primary tier's.

**Estimating real concurrent users** (method above):

*Pod-1 (A = 20):*

| Scenario | B (Locust users) | C (time, blended) | D = B÷C (RPS) | E (T_real) | Real users = D×E |
|---|---:|---:|---:|---:|---:|
| register_read | 8.00 | 9.70s | 0.825 | 30s | 24.7 |
| cr_create | 2.00 | 1.17s | 1.715 | 30s | 51.5 |
| cr_read_and_approve | 4.00 | 3.97s | 1.007 | 30s | 30.2 |
| intake_create | 2.00 | 3.77s | 0.531 | 60s | 31.9 |
| intake_read_and_approve | 4.00 | 4.56s | 0.877 | 30s | 26.3 |
| **Total** | **20.00** | — | — | — | **≈164.6** |

Blended ratio: 164.6 ÷ 20 = **8.2×**

*Pod-2 (A = 32):*

| Scenario | B (Locust users) | C (time, blended) | D = B÷C (RPS) | E (T_real) | Real users = D×E |
|---|---:|---:|---:|---:|---:|
| register_read | 12.80 | 8.79s | 1.457 | 30s | 43.7 |
| cr_create | 3.20 | 1.00s | 3.191 | 30s | 95.7 |
| cr_read_and_approve | 6.40 | 3.06s | 2.089 | 30s | 62.7 |
| intake_create | 3.20 | 3.51s | 0.911 | 60s | 54.7 |
| intake_read_and_approve | 6.40 | 2.71s | 2.365 | 30s | 70.9 |
| **Total** | **32.00** | — | — | — | **≈327.7** |

Blended ratio: 327.7 ÷ 32 = **10.2×** — built on the same broken Pod-2
blended run flagged in §5 below; treat as unreliable until Pod-2 is
re-run.

*Pod-3 (A = 52):*

`intake_read_and_approve` isn't computable here — Pod-3's isolated run
above completed zero approvals, so there's no fires-per-unit structure to
build `C` from. The total below is a **partial sum over 4 of 5
scenarios**, not a complete estimate for this cell.

| Scenario | B (Locust users) | C (time, blended) | D = B÷C (RPS) | E (T_real) | Real users = D×E |
|---|---:|---:|---:|---:|---:|
| register_read | 20.80 | 10.65s | 1.954 | 30s | 58.6 |
| cr_create | 5.20 | 1.21s | 4.285 | 30s | 128.6 |
| cr_read_and_approve | 10.40 | 2.98s | 3.485 | 30s | 104.6 |
| intake_create | 5.20 | 4.13s | 1.259 | 60s | 75.6 |
| intake_read_and_approve | 8.80 | — | — | 30s | N/A |
| **Total (4 of 5 scenarios)** | **41.60 of 52.00** | — | — | — | **≈367.3** |

Blended ratio: not meaningful with a scenario missing — do not divide this
total by 52.

#### Volume-Tier: Stress

_(pending — no Stress-tier run yet)_

### In-Cluster

#### Volume-Tier: Primary

##### Isolated (Step 1)
###### register_read — 1 register record fully read

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_a_register` | 133ms (×1.00) | 102ms (×1.00) | 118ms (×1.00) |
| `get_subject_record` | 119ms (×1.00) | 79ms (×1.00) | 104ms (×1.00) |
| `get_all_tabs` | 87ms (×1.00) | 58ms (×1.00) | 76ms (×1.00) |
| `get_tab_sections` | 127ms (×6.94) | 90ms (×6.96) | 114ms (×6.94) |
| `get_tab_records` | 155ms (×6.94) | 111ms (×6.96) | 140ms (×6.94) |
| `get_number_of_pending_change_requests` | 113ms (×6.94) | 78ms (×6.96) | 101ms (×6.94) |
| `get_change_requests` | 127ms (×6.93) | 90ms (×6.95) | 115ms (×6.93) |
| `get_change_request_documents` | 109ms (×0.27) | 71ms (×0.24) | 101ms (×0.36) |
| `get_section_ui_schema` | 110ms (×0.27) | 70ms (×0.24) | 103ms (×0.36) |
| `get_change_request` | 140ms (×0.27) | 99ms (×0.24) | 135ms (×0.36) |
| `list_tasks_for_request` | 114ms (×0.27) | 81ms (×0.24) | 110ms (×0.36) |
| `get_deduplication_change_request_results` | 115ms (×0.27) | 73ms (×0.24) | 103ms (×0.36) |
| `get_deduplication_register_results` | 113ms (×0.27) | 71ms (×0.24) | 104ms (×0.36) |
| `get_number_of_versions` | 122ms (×6.93) | 86ms (×6.95) | 112ms (×6.93) |
| `get_version_dates` | 117ms (×6.92) | 82ms (×6.95) | 107ms (×6.93) |
| `get_versions_for_a_date` | 122ms (×6.02) | 88ms (×5.86) | 114ms (×5.97) |
| **Total time for 1 unit** | **6.54s** | **4.60s** | **6.00s** |
| Locust users (peak, this run) | 16 | 20 | 36 |
| **RPS (Locust users ÷ Total time)** | **2.448** | **4.345** | **6.003** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **73** | **130** | **180** |

###### cr_create — 1 change request effected

`get_attribute_values` recorded 0 requests in this run, same as Primary
end-to-end, and is excluded from the chain below.

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_a_register` | 122ms (×0.38) | 141ms (×0.39) | 201ms (×0.39) |
| `get_subject_record` | 91ms (×0.20) | 91ms (×0.20) | 154ms (×0.20) |
| `get_all_sections` | 82ms (×0.20) | 80ms (×0.20) | 137ms (×0.20) |
| `get_all_tabs` | 67ms (×0.20) | 66ms (×0.20) | 117ms (×0.20) |
| `get_tab_sections` | 103ms (×1.40) | 99ms (×1.40) | 170ms (×1.40) |
| `get_tab_records` | 127ms (×1.40) | 121ms (×1.40) | 202ms (×1.40) |
| `create_change_request` | 221ms (93% of CRs) | 218ms (93% of CRs) | 330ms (93% of CRs) |
| `create_change_request_for_core_data` | 237ms (7% of CRs) | 240ms (7% of CRs) | 353ms (7% of CRs) |
| **Total time for 1 unit** | **0.64s** | **0.63s** | **1.01s** |
| Locust users (peak, this run) | 12 | 20 | 44 |
| **RPS (Locust users ÷ Total time)** | **18.785** | **31.747** | **43.512** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **564** | **952** | **1305** |

###### cr_read_and_approve — 1 change request approved

_Captured before the change that limits `cr_read_and_approve` to pending
tasks only — expect the ×/unit ratios below (and the derived RPS/real-user
figures) to shift once this scenario is re-run._

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_change_request` | 159ms (×0.24) | 153ms (×0.16) | 152ms (×0.29) |
| `get_change_request_documents` | 108ms (×2.67) | 69ms (×2.07) | 102ms (×2.21) |
| `get_section_ui_schema` | 106ms (×2.67) | 67ms (×2.07) | 101ms (×2.21) |
| `get_change_request` | 138ms (×2.67) | 93ms (×2.07) | 133ms (×2.21) |
| `get_deduplication_change_request_results` | 110ms (×2.66) | 70ms (×2.07) | 104ms (×2.21) |
| `get_deduplication_register_results` | 109ms (×2.66) | 69ms (×2.07) | 103ms (×2.20) |
| `list_tasks_for_request` | 111ms (×2.63) | 79ms (×2.07) | 112ms (×2.13) |
| `submit_task_decision` | 159ms (×1.00) | 110ms (×1.00) | 153ms (×1.00) |
| **Total time for 1 unit** | **2.01s** | **1.06s** | **1.63s** |
| Locust users (peak, this run) | 12 | 12 | 28 |
| **RPS (Locust users ÷ Total time)** | **5.961** | **11.337** | **17.132** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **179** | **340** | **514** |

###### intake_create — 1 intake submission created

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `render_intake_form` | 114ms (×1.01) | 88ms (×1.00) | 79ms (×1.01) |
| `save_intake_form_submission` | 284ms (×9.05) | 229ms (×9.02) | 210ms (×9.03) |
| `get_intake_form_submission` | 205ms (×1.00) | 164ms (×1.00) | 152ms (×1.00) |
| `finalize_intake_form_submission` | 284ms (×1.00) | 239ms (×1.00) | 228ms (×1.00) |
| **Total time for 1 unit** | **3.18s** | **2.56s** | **2.36s** |
| Locust users (peak, this run) | 16 | 24 | 28 |
| **RPS (Locust users ÷ Total time)** | **5.036** | **9.389** | **11.877** |
| T_real | 60s | 60s | 60s |
| **Real concurrent users** | **302** | **563** | **713** |

###### intake_read_and_approve — 1 intake submission approved

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_intake_form_submissions` | 197ms (×2.81) | 103ms (×10.02) | 210ms (×35.63) |
| `get_intake_form_submission` | 197ms (×4.14) | 134ms (×2.33) | 158ms (×1.94) |
| `get_intake_form_documents` | 131ms (×4.14) | 84ms (×2.33) | 102ms (×1.94) |
| `get_deduplication_intake_form_register_results` | 131ms (×4.14) | 84ms (×2.33) | 102ms (×1.94) |
| `get_deduplication_intake_form_intake_form_results` | 131ms (×4.14) | 84ms (×2.33) | 102ms (×1.94) |
| `list_tasks_for_request` | 131ms (×4.14) | 92ms (×2.33) | 108ms (×1.94) |
| `submit_task_decision` | 158ms (×1.00) | 123ms (×1.00) | 126ms (×1.00) |
| **Total time for 1 unit** | **3.70s** | **2.27s** | **8.71s** |
| Locust users (peak, this run) | 16 | 28 | 80 |
| **RPS (Locust users ÷ Total time)** | **4.330** | **12.337** | **9.181** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **130** | **370** | **275** |

Pod-3's `search_in_intake_form_submissions` ratio (×35.63, vs. ×2.81/×10.02
at Pod-1/Pod-2) is a larger outlier than the same scenario's End-to-End
Primary run — worth confirming on re-run before trusting this pod's total.

##### Blended (Step 2)
| Pod-Scale | Concurrent users | Requests | Failures | p95 | Aggregated RPS |
|---|---|---|---|---|---|
| Pod-1 | 12 | 28,469 | 0 | 220ms | 71.03 |
| Pod-2 | 16 | 40,560 | 0 | 270ms | 89.98 |
| Pod-3 | 32 | 49,486 | 0 | 140ms | 123.70 |

Scaling efficiency vs. Pod-1: Pod-2 ≈63% of linear (89.98 ÷ (2×71.03)),
Pod-3 ≈58% of linear (123.70 ÷ (3×71.03)) — close to End-to-End's, so the
sub-linear scaling itself isn't an RP artifact.

**Estimating real concurrent users** (method above):

*Pod-1 (A = 12):*

| Scenario | B (Locust users) | C (time, blended) | D = B÷C (RPS) | E (T_real) | Real users = D×E |
|---|---:|---:|---:|---:|---:|
| register_read | 4.80 | 5.83s | 0.823 | 30s | 24.7 |
| cr_create | 1.20 | 0.69s | 1.745 | 30s | 52.3 |
| cr_read_and_approve | 2.40 | 1.89s | 1.270 | 30s | 38.1 |
| intake_create | 1.20 | 2.12s | 0.567 | 60s | 34.0 |
| intake_read_and_approve | 2.40 | 3.64s | 0.659 | 30s | 19.8 |
| **Total** | **12.00** | — | — | — | **≈168.9** |

Blended ratio: 168.9 ÷ 12 = **14.1×**

*Pod-2 (A = 16):*

| Scenario | B (Locust users) | C (time, blended) | D = B÷C (RPS) | E (T_real) | Real users = D×E |
|---|---:|---:|---:|---:|---:|
| register_read | 6.40 | 4.42s | 1.448 | 30s | 43.4 |
| cr_create | 1.60 | 0.57s | 2.828 | 30s | 84.8 |
| cr_read_and_approve | 3.20 | 1.14s | 2.810 | 30s | 84.3 |
| intake_create | 1.60 | 2.21s | 0.723 | 60s | 43.4 |
| intake_read_and_approve | 3.20 | 2.42s | 1.322 | 30s | 39.7 |
| **Total** | **16.00** | — | — | — | **≈295.6** |

Blended ratio: 295.6 ÷ 16 = **18.5×**

*Pod-3 (A = 32):*

| Scenario | B (Locust users) | C (time, blended) | D = B÷C (RPS) | E (T_real) | Real users = D×E |
|---|---:|---:|---:|---:|---:|
| register_read | 12.80 | 6.51s | 1.966 | 30s | 59.0 |
| cr_create | 3.20 | 0.76s | 4.192 | 30s | 125.8 |
| cr_read_and_approve | 6.40 | 1.82s | 3.515 | 30s | 105.4 |
| intake_create | 3.20 | 2.96s | 1.080 | 60s | 64.8 |
| intake_read_and_approve | 6.40 | 6.53s | 0.981 | 30s | 29.4 |
| **Total** | **32.00** | — | — | — | **≈384.4** |

Blended ratio: 384.4 ÷ 32 = **12.0×**

Pod-3's `intake_read_and_approve` contribution (29.4, that cell's smallest
of the five) is built on a `C` that inherits the same
`search_in_intake_form_submissions` Pod-3 outlier flagged above — its
fires-per-unit ratio is structurally inflated there, so this figure should
be treated as a lower bound until that isolated scenario is re-run.

##### Soak (Step 3)
Run via [`k8s/soak-job.yaml`](../../locust/api/k8s/soak-job.yaml) /
[`soak_locustfile.py`](../../locust/api/staff-api/blended/soak_locustfile.py),
full 8h (28,800s), same 80:20 weighted mix as Step 2 — a fixed
`SOAK_USERS` count (ramped at `-r 2`) held for the full 8h, not a ramp, so
there's no adaptive freeze point. Total HTTP throughput is capped at
`SOAK_MAX_RPS` so CPU doesn't climb back to the ramp's closed-loop ceiling
once latency settles.

`SOAK_USERS=36` capped at `SOAK_MAX_RPS=172` (`k8s/soak-job.yaml`) were
chosen to hold pod CPU near 1.7-1.8 of the 2-vCPU limit, and the run
sustained ~154-170 RPS throughout at that setting.

**Throughput and latency:** stable for the full 8h, no decay —

| t (h) | RPS | p50 | p95 | p99 | max |
|---|---|---|---|---|---|
| 0.5 | 166.6 | 140ms | 300ms | 530ms | 14.0s |
| 2.0 | 168.3 | 130ms | 290ms | 560ms | 16.0s |
| 4.0 | 165.1 | 110ms | 270ms | 540ms | 16.0s |
| 6.0 | 167.2 | 110ms | 260ms | 530ms | 28.0s |
| 8.0 | 169.7 | 110ms | 260ms | 530ms | 31.0s |

p50/p95 actually *improve* slightly over the run (140→110ms / 300→260ms);
p99 is flat at ~530-560ms — no latency creep on the percentiles the SLOs
are defined against. The **max** (100th percentile) is the one metric
that visibly grows — 1.2s in the first half-hour to 14-16s by hour 2, then
28-31s from hour 6 on — a small number of increasingly severe tail-latency
outliers, not visible in p99. Worth isolating (which endpoint, which pod,
timed with what else) before dismissing as noise.

**Errors:** 34 failures out of 4,733,071 requests over 8h (0.0007%),
arriving in a scattered trickle throughout the run (`soak_failures.csv`),
not concentrated or accelerating toward the end — two distinct causes:
- **24 of 34** are `AWE-ERR-006` connection resets talking to AWE
  (`list_tasks_for_request`, `submit_task_decision`,
  `finalize_intake_form_submission`) — direct, fresh evidence for the
  AWE-hop bottleneck already flagged from isolated-tier data (Measurements
  above, §6).
- **10 of 34** are `SYS-ERR-001` on `create_change_request` — a **new**
  finding, not the same bug as `get_record_history`'s (different endpoint,
  different code path; `SYS-ERR-001` is a generic wrapper code, not
  evidence of a shared root cause). Not yet investigated.

**Memory:** pod CPU/memory panels for all 3 Pod-3 replicas
(`locust/api/results/staff-api/in-cluster/primary/pod-3/3-soak/pod-*.png`)
show CPU oscillating 1.5-2 of the 2-vCPU limit throughout (matching the
`SOAK_MAX_RPS` design target), and memory climbing **steadily and
near-linearly on all three pods** — roughly 362→385-400 MiB over the 8h
(~7-10% growth), never plateauing. This is a real, consistent trend across
replicas, not a one-off — but it's modest and still rising at the 8h mark,
so it's a **borderline result**: neither a flat pass nor an unambiguous
leak. A longer soak (or a heap/object-count profile) is needed to tell
"grows then plateaus" (fine) from "unbounded" (not). DB connection counts
weren't captured for this run (not part of `soak_stats_history.csv` or the
pod dashboards pulled) — a gap against deliverable 7's own definition.

**Per-scenario unit-time and RPS:** `raw-report.md`'s soak per-endpoint
totals (`soak_stats.csv`) let this run be broken out by scenario the same
way as Blended (§4 methodology; `A` = 36, the steady-state `SOAK_USERS`):

| Scenario | B (Locust users) | C (unit-time) | D (RPS) | T_real | Real users |
|---|---:|---:|---:|---:|---:|
| register_read | 14.40 | 5.972s | 2.411 | 30s | 72 |
| cr_create | 3.60 | 0.712s | 5.055 | 30s | 152 |
| cr_read_and_approve | 7.20 | 1.739s | 4.141 | 30s | 124 |
| intake_create | 3.60 | 2.474s | 1.455 | 60s | 87 |
| intake_read_and_approve | 7.20 | 6.532s | 1.102 | 30s | 33 |
| **Total** | **36.00** | — | — | — | **468** |

**Verdict:** provisional PASS on throughput/error-rate/percentile-latency
stability; **memory trend is a watch item, not a clean pass**.

#### Volume-Tier: Stretch

##### Isolated (Step 1)
###### register_read — 1 register record fully read

Pod-1 **and** Pod-3 found zero pending change requests on any tab this
run (all 6 CR-related endpoints, 0 calls); only Pod-2 found any, at a
sparse ×0.01 ratio — the same data-volume effect noted for End-to-End
Stretch, here hitting two of the three pods instead of one.

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_a_register` | 153ms (×1.00) | 128ms (×1.00) | 166ms (×1.00) |
| `get_subject_record` | 120ms (×1.00) | 100ms (×1.00) | 109ms (×1.00) |
| `get_all_tabs` | 88ms (×1.00) | 71ms (×1.00) | 77ms (×1.00) |
| `get_tab_sections` | 131ms (×6.96) | 107ms (×6.95) | 118ms (×6.95) |
| `get_tab_records` | 160ms (×6.95) | 133ms (×6.95) | 145ms (×6.94) |
| `get_number_of_pending_change_requests` | 116ms (×6.95) | 93ms (×6.95) | 104ms (×6.94) |
| `get_change_requests` | 132ms (×6.95) | 108ms (×6.95) | 119ms (×6.94) |
| `get_change_request_documents` | — (0 calls) | 105ms (×0.01) | — (0 calls) |
| `get_section_ui_schema` | — (0 calls) | 104ms (×0.01) | — (0 calls) |
| `get_change_request` | — (0 calls) | 143ms (×0.01) | — (0 calls) |
| `list_tasks_for_request` | — (0 calls) | 101ms (×0.01) | — (0 calls) |
| `get_deduplication_change_request_results` | — (0 calls) | 94ms (×0.01) | — (0 calls) |
| `get_deduplication_register_results` | — (0 calls) | 100ms (×0.01) | — (0 calls) |
| `get_number_of_versions` | 129ms (×6.95) | 104ms (×6.94) | 114ms (×6.94) |
| `get_version_dates` | 122ms (×6.95) | 99ms (×6.94) | 109ms (×6.94) |
| `get_versions_for_a_date` | 131ms (×5.90) | 106ms (×5.91) | 117ms (×5.88) |
| **Total time for 1 unit** | **6.62s** | **5.41s** | **5.96s** |
| Locust users (peak, this run) | 16 | 24 | 36 |
| **RPS (Locust users ÷ Total time)** | **2.418** | **4.438** | **6.042** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **73** | **133** | **181** |

###### cr_create — 1 change request effected

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_a_register` | 291ms (×0.20) | 355ms (×0.20) | 567ms (×0.20) |
| `get_subject_record` | 248ms (×0.20) | 337ms (×0.20) | 341ms (×0.20) |
| `get_all_sections` | 198ms (×0.20) | 285ms (×0.20) | 284ms (×0.20) |
| `get_all_tabs` | 188ms (×0.20) | 251ms (×0.20) | 252ms (×0.20) |
| `get_tab_sections` | 265ms (×1.40) | 365ms (×1.40) | 363ms (×1.40) |
| `get_tab_records` | 321ms (×1.40) | 410ms (×1.40) | 391ms (×1.40) |
| `create_change_request` | 475ms (93% of CRs) | 598ms (93% of CRs) | 567ms (94% of CRs) |
| `create_change_request_for_core_data` | 504ms (7% of CRs) | 575ms (7% of CRs) | 559ms (6% of CRs) |
| **Total time for 1 unit** | **1.48s** | **1.93s** | **1.91s** |
| Locust users (peak, this run) | 28 | 48 | 52 |
| **RPS (Locust users ÷ Total time)** | **18.866** | **24.915** | **27.204** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **566** | **747** | **816** |

###### cr_read_and_approve — 1 change request approved

_Captured before the change that limits `cr_read_and_approve` to pending
tasks only — expect the ×/unit ratios below (and the derived RPS/real-user
figures) to shift once this scenario is re-run._

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_change_request` | 142ms (×0.34) | 139ms (×0.26) | 251ms (×0.29) |
| `get_change_request_documents` | 104ms (×2.39) | 74ms (×1.77) | 133ms (×2.33) |
| `get_section_ui_schema` | 103ms (×2.39) | 72ms (×1.77) | 133ms (×2.33) |
| `get_change_request` | 134ms (×2.39) | 99ms (×1.77) | 171ms (×2.33) |
| `get_deduplication_change_request_results` | 106ms (×2.39) | 75ms (×1.77) | 136ms (×2.33) |
| `get_deduplication_register_results` | 105ms (×2.39) | 74ms (×1.77) | 135ms (×2.32) |
| `list_tasks_for_request` | 107ms (×2.30) | 82ms (×1.68) | 139ms (×2.32) |
| `submit_task_decision` | 147ms (×1.00) | 121ms (×1.00) | 186ms (×1.00) |
| **Total time for 1 unit** | **1.76s** | **0.99s** | **2.23s** |
| Locust users (peak, this run) | 12 | 12 | 36 |
| **RPS (Locust users ÷ Total time)** | **6.811** | **12.082** | **16.152** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **204** | **362** | **485** |

###### intake_create — 1 intake submission created

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `render_intake_form` | 117ms (×1.01) | 75ms (×1.01) | 102ms (×1.01) |
| `save_intake_form_submission` | 282ms (×9.05) | 206ms (×9.04) | 269ms (×9.04) |
| `get_intake_form_submission` | 211ms (×1.00) | 147ms (×1.00) | 194ms (×1.00) |
| `finalize_intake_form_submission` | 282ms (×1.00) | 217ms (×1.00) | 282ms (×1.00) |
| **Total time for 1 unit** | **3.16s** | **2.30s** | **3.01s** |
| Locust users (peak, this run) | 16 | 20 | 36 |
| **RPS (Locust users ÷ Total time)** | **5.057** | **8.688** | **11.957** |
| T_real | 60s | 60s | 60s |
| **Real concurrent users** | **303** | **521** | **717** |

###### intake_read_and_approve — 1 intake submission approved

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_intake_form_submissions` | 211ms (×2.69) | 161ms (×5.17) | 126ms (×11.67) |
| `get_intake_form_submission` | 176ms (×3.84) | 169ms (×3.96) | 144ms (×2.03) |
| `get_intake_form_documents` | 117ms (×3.84) | 107ms (×3.96) | 85ms (×2.03) |
| `get_deduplication_intake_form_register_results` | 116ms (×3.84) | 106ms (×3.96) | 85ms (×2.03) |
| `get_deduplication_intake_form_intake_form_results` | 117ms (×3.84) | 107ms (×3.96) | 85ms (×2.03) |
| `list_tasks_for_request` | 116ms (×3.84) | 111ms (×3.96) | 94ms (×2.03) |
| `submit_task_decision` | 151ms (×1.00) | 146ms (×1.00) | 137ms (×1.00) |
| **Total time for 1 unit** | **3.18s** | **3.35s** | **2.61s** |
| Locust users (peak, this run) | 16 | 24 | 40 |
| **RPS (Locust users ÷ Total time)** | **5.024** | **7.161** | **15.318** |
| T_real | 30s | 30s | 30s |
| **Real concurrent users** | **151** | **215** | **460** |

Pod-3's `search_in_intake_form_submissions` ratio (×11.67) is again the
largest swing in this scenario (consistent with the same pattern flagged
at Primary tier) — treat its total with the same caution.

##### Blended (Step 2)
| Pod-Scale | Concurrent users | Requests | Failures | p95 | Aggregated RPS |
|---|---|---|---|---|---|
| Pod-1 | 12 | 28,419 | 0 | 220ms | 70.87 |
| Pod-2 | 24 | 47,308 | 3 | 950ms | 72.02 |
| Pod-3 | 44 | 40,719 | 0 | 160ms | 101.54 |

**Pod-2's cell looks broken, not just worse:** its request count (47,308)
divided by its own RPS (72.02) implies a ~657s run, while Pod-1 and Pod-3
both come out to ~401s — this run took ~64% longer than its neighbors at
the same fixed-concurrency setting, and its p95 (950ms) is 4-6× the other
two pods'. Something specific to this run (not a Pod-Scale-2
characteristic) — re-run before trusting Pod-2's Stretch blended numbers
for anything, including the scaling/sensitivity comparisons in §5.

Scaling efficiency vs. Pod-1: Pod-2 ≈51% of linear (72.02 ÷ (2×70.87)) —
unreliable, Pod-2 is the broken run and it's this figure's own numerator.
Pod-3 ≈48% (101.54 ÷ (3×70.87)) doesn't involve Pod-2 at all (only Pod-1
and Pod-3, both clean runs), so it stands on its own — and it's noticeably
below Primary's ≈58% at the same pod (§5).

**Estimating real concurrent users** (method above):

*Pod-1 (A = 12):*

| Scenario | B (Locust users) | C (time, blended) | D = B÷C (RPS) | E (T_real) | Real users = D×E |
|---|---:|---:|---:|---:|---:|
| register_read | 4.80 | 5.33s | 0.901 | 30s | 27.0 |
| cr_create | 1.20 | 0.70s | 1.721 | 30s | 51.6 |
| cr_read_and_approve | 2.40 | 1.63s | 1.473 | 30s | 44.2 |
| intake_create | 1.20 | 2.58s | 0.466 | 60s | 27.9 |
| intake_read_and_approve | 2.40 | 3.02s | 0.794 | 30s | 23.8 |
| **Total** | **12.00** | — | — | — | **≈174.6** |

Blended ratio: 174.6 ÷ 12 = **14.6×**

*Pod-2 (A = 24):*

| Scenario | B (Locust users) | C (time, blended) | D = B÷C (RPS) | E (T_real) | Real users = D×E |
|---|---:|---:|---:|---:|---:|
| register_read | 9.60 | 6.16s | 1.559 | 30s | 46.8 |
| cr_create | 2.40 | 0.72s | 3.341 | 30s | 100.2 |
| cr_read_and_approve | 4.80 | 1.33s | 3.605 | 30s | 108.2 |
| intake_create | 2.40 | 2.68s | 0.896 | 60s | 53.8 |
| intake_read_and_approve | 4.80 | 4.22s | 1.137 | 30s | 34.1 |
| **Total** | **24.00** | — | — | — | **≈343.1** |

Blended ratio: 343.1 ÷ 24 = **14.3×** — same broken-run caveat as above;
this cell's `C` values come from that same anomalous run and should be
re-derived once it's repeated.

*Pod-3 (A = 44):*

| Scenario | B (Locust users) | C (time, blended) | D = B÷C (RPS) | E (T_real) | Real users = D×E |
|---|---:|---:|---:|---:|---:|
| register_read | 17.60 | 8.45s | 2.084 | 30s | 62.5 |
| cr_create | 4.40 | 1.05s | 4.176 | 30s | 125.3 |
| cr_read_and_approve | 8.80 | 2.49s | 3.541 | 30s | 106.2 |
| intake_create | 4.40 | 3.61s | 1.220 | 60s | 73.2 |
| intake_read_and_approve | 8.80 | 4.63s | 1.899 | 30s | 57.0 |
| **Total** | **44.00** | — | — | — | **≈424.2** |

Blended ratio: 424.2 ÷ 44 = **9.6×**

##### Soak (Step 3)
Same [`k8s/soak-job.yaml`](../../locust/api/k8s/soak-job.yaml) setup as
Primary tier, targeting the same ~1.7-1.8 of the 2-vCPU CPU band: **reused
with identical `SOAK_USERS=36`/`SOAK_MAX_RPS=172` values**, not
recalculated for this tier's own Step 2 result (Pod-3 blended measured
124.13 RPS at **52** users here, above) — the run sustained ~140-152 RPS
throughout at that setting.

**Throughput and latency:**

| t (h) | RPS | p50 | p95 | p99 | max |
|---|---|---|---|---|---|
| 0.5 | 149.2 | 140ms | 300ms | 550ms | 210.0s |
| 2.0 | 150.2 | 140ms | 300ms | 550ms | 267.0s |
| 4.0 | 151.3 | 140ms | 300ms | 560ms | 267.0s |
| 6.0 | 141.4 | 130ms | 300ms | 580ms | 285.0s |
| 8.0 | 151.2 | 130ms | 300ms | 590ms | 285.0s |

RPS is stable (no decay), and p50/p95 are flat throughout. **p99 shows a
real, if modest, upward drift** — 480ms at the 0.01h mark to 590ms by
hour 8 (+23%) — unlike the Primary-tier soak, where p99 stayed flat. The
**max** (100th percentile) is the standout: it reaches **210 seconds**
within the first 30 minutes and climbs to **285 seconds** (4.75 minutes)
by hour 5.5, staying there — one or more individual requests took over
four and a half minutes to complete. This is an order of magnitude worse
than the Primary-tier soak's worst max (31s) and, combined with the real
p99 creep, is the clearest data-volume-sensitivity signal in this report:
tail latency under sustained load degrades meaningfully going from 10M to
50M records, even though the percentiles that gate pass/fail (p50/p95) do
not. **Isolated to one endpoint:** `raw-report.md`'s soak per-endpoint
totals (`soak_stats.csv`, added on regeneration) show `search_in_a_register`
— `register_read`'s own anchor — with a Max Response Time of
285,209ms, matching the 285s aggregate figure exactly. Every other
endpoint's max stays under ~2.3s. `register_read`'s own unit-time is also
the largest of the five scenarios at this tier (7.41s, Measurements
above), consistent with the outlier sitting in this scenario's chain.

**Errors:** 37 failures out of 4,315,002 requests over 8h (0.00086%),
arriving as a scattered trickle, not concentrated toward the end — the
same two causes as the Primary-tier soak, in a similar split:
- **28 of 37** are `AWE-ERR-006` connection resets (`list_tasks_for_request`,
  `submit_task_decision`, `finalize_intake_form_submission`) — the AWE-hop
  bottleneck finding, now confirmed at a second Volume-Tier.
- **9 of 37** are `SYS-ERR-001` on `create_change_request` — the same
  unexplained error as Primary tier's soak, now recurring at a second
  tier. Reproducing at two independent 8h runs makes this look like a
  real, findable bug rather than a one-off; it still hasn't been
  root-caused (§6).

**Memory:** pod CPU/memory panels for all 3 Pod-3 replicas
(`locust/api/results/staff-api/in-cluster/stretch/pod-3/3-soak/pod-*.png`)
show the same pattern as Primary tier — CPU oscillating 1.5-2 of the
2-vCPU limit, memory climbing steadily and near-linearly on every replica
checked (≈372→391 MiB and ≈381→420 MiB on the two pods inspected, ~5-10%
growth, not plateaued at 8h). Same borderline verdict as Primary: a real,
consistent trend, but too modest and still-rising to call an unbounded
leak from one 8h run. DB connection counts still aren't captured by this
harness (same gap as Primary).

**Per-scenario unit-time and RPS:** same method as Primary tier above
(`A` = 36):

| Scenario | B (Locust users) | C (unit-time) | D (RPS) | T_real | Real users |
|---|---:|---:|---:|---:|---:|
| register_read | 14.40 | 7.409s | 1.943 | 30s | 58 |
| cr_create | 3.60 | 0.905s | 3.977 | 30s | 119 |
| cr_read_and_approve | 7.20 | 2.241s | 3.212 | 30s | 96 |
| intake_create | 3.60 | 2.811s | 1.281 | 60s | 77 |
| intake_read_and_approve | 7.20 | 3.659s | 1.968 | 30s | 59 |
| **Total** | **36.00** | — | — | — | **409** |

`register_read`'s `C` (7.41s) is the largest of the five scenarios at
this tier — consistent with it carrying the 285s tail-latency outlier
(above).

**Verdict:** throughput and p50/p95 latency hold for the full 8h; **p99
shows a real upward drift this tier didn't show at Primary, and tail
latency (max) is dramatically worse** — both are watch items, not a clean
pass, and both point at data-volume sensitivity as the driver rather than
pure duration (Primary's 8h run didn't show this). Memory trend is the
same borderline call as Primary.

### 5. Scaling, data-volume sensitivity & ingress comparison
Consolidated blended (Step 2) scaling picture, all four cells measured so
far (per-cell tables and derivations: Measurements above):

| Ingress | Volume-Tier | Pod-1 RPS | Pod-2 RPS (eff. vs. linear) | Pod-3 RPS (eff. vs. linear) |
|---|---|---:|---:|---:|
| End-to-End | Primary | 66.26 | 93.39 (≈70%) | 122.26 (≈61%) |
| End-to-End | Stretch | 66.25 | 94.14 (≈71%) | 124.13 (≈62%) |
| In-Cluster | Primary | 71.03 | 89.98 (≈63%) | 123.70 (≈58%) |
| In-Cluster | Stretch | 70.87 | 72.02 (≈51%, broken run) | 101.54 (≈48%) |

**Ingress comparison:** at every Pod-Scale, In-Cluster reaches essentially
the same (Pod-1, Pod-3) or slightly lower (Pod-2) RPS as End-to-End, but
with roughly 35-45% fewer concurrent users doing it (Pod-1: 12 vs 20;
Pod-2: 16 vs 28; Pod-3: 32 vs 48, Primary tier) and zero measured failures
throughout versus End-to-End's handful. This is the RP-hop latency
[`environment-topology.md`](../environment-topology.md) calls out — it adds
per-request latency (so Little's Law needs more concurrent users to sustain
the same RPS end-to-end) without capping the throughput ceiling itself at
this load level; the two ingresses' near-equal RPS ceilings say the RP
(`t3a.medium`, 2 vCPU) isn't yet the bottleneck at these cells.

**In-Cluster Stretch Pod-2 is a broken run**, not a clean data point (~64%
longer duration than its neighbors, p95 4-6× higher — detail in
Measurements → In-Cluster → Stretch → Blended); excluded from the
comparisons below.

**Data-volume sensitivity, Primary (10M) → Stretch (50M), blended, same
ingress/Pod-Scale:**
- **End-to-End: essentially flat.** RPS moves <2% at every pod
  (66.26→66.25, 93.39→94.14, 122.26→124.13); p95 is flat at Pod-1/Pod-3
  (420→410ms, 290→290ms). Pod-2's p95 jump (440→590ms) is very likely the
  same broken-run pattern as In-Cluster Pod-2, not a real data-volume
  effect.
- **In-Cluster: flat at Pod-1, real drop at Pod-3.** Pod-1 is flat
  (71.03→70.87 RPS, 220→220ms p95). Pod-3 drops a genuine ~18% in RPS
  (123.70→101.54) with p95 up ~14% (140→160ms) — small but real; Pod-2
  can't be used as a clean middle data point given the anomaly above.

**Soak tail latency (Measurements → In-Cluster → Primary/Stretch → Soak)
is the more striking data-volume signal:** max response time reaches 285s
at `stretch` vs. 31s at `primary` over the same 8h window, with a real p99
creep `primary` didn't show — throughput and p50/p95 hold at both tiers,
but the tail degrades meaningfully at 5× the record count.

### 6. Bottlenecks & tuning
Nine changes were reported as identified/applied against this list; each
is checked here against the actual commit history in the `registry-platform`,
`awe`, `iam`, and `openg2p-fastapi-common` repos (this `venky-github`
checkout, which is ahead of `openg2p-github` on all four) rather than taken
at face value.

**1. AWE worker/pool tuning — applied, but not literally Gunicorn.**
`awe` commit `072e943` ("Increase UVICORN workers...") raised
`UVICORN_WORKERS` 1→2 in the `Dockerfile`. `docker-entrypoint.sh` still
runs `exec uvicorn awe.main:app --workers "${UVICORN_WORKERS}"` directly —
there is no `gunicorn` dependency or invocation anywhere in the `awe` repo,
so this is uvicorn's own multi-worker flag, not a Gunicorn-managed
uvicorn-worker setup. The same commit also changed `db.py`'s *default*
pool_size/max_overflow (used only when the env vars are unset) from 20/15
back to 10/5 — but the deployed values come from
`helm/openg2p-awe/values.yaml`, which an earlier same-day commit
(`155463b`) set to `DB_POOL_SIZE=5`/`DB_POOL_MAX_OVERFLOW=10`. Net effect
in production: total connection ceiling is unchanged at 15, just
re-split (smaller persistent pool, larger overflow) and now
environment-configurable instead of hardcoded (see item 8).

**2. Composite index in registry-platform — applied.**
`ix_change_requests_lookup` on
`g2p_register_change_requests(register_id, internal_record_id, tab_id, created_at)`,
added in `59209d7` (G2P-5507, backing `get_change_requests_flattened`) and
extended with `approval_status` in `5c0a396` (G2P-5510, backing
`get_number_of_pending_change_requests`). A separate, non-composite index
was also added on `g2p_registers.last_approved_at` in `c8efcac` (G2P-5513,
`search_in_a_register`). None of this touches the `get_register_summary_data`
count path — see item 5.

**3. iam-core oidc_client/jwks ContextVar fix — applied.** `iam` commit
`4c1888b` (G2P-5647, "Implement caching for JWKS and OIDC metadata")
replaces both `jwks_cache` and `server_metadata_cache` — previously plain
`ContextVar`s, the same copy-per-asyncio-Task bug flagged earlier in this
conversation — with `fastapi_cache` `@cache` decorators on `get_jwks`
(`jwks_helper.py`) and `get_server_metadata` (`oidc_client.py`), keyed by
issuer/`jwks_uri` and login-provider id respectively, each with its own
5-minute TTL (`auth_jwks_cache_ttl_seconds` / `auth_oidc_metadata_cache_ttl_seconds`).
Backed by `FastAPICache.init(InMemoryBackend(), prefix="iam-cache")`
(`iam_core/user_auth/cache.py`) — genuinely process-wide, unlike the
`ContextVar` it replaces — and covered by tests
(`test_helpers_and_middleware.py`, `test_oidc_and_adapters.py`). `iam` is
now checked out on `performance-test` (the branch this fix lives on,
matching `registry-platform` and this repo), confirming the ~1000ms
`get_subject_record` cost reported earlier is fixed at the code level.

**4. Connection pooling via singleton session-maker — applied.**
`openg2p-fastapi-common` commit `17057b7` (G2P-5620) replaced the
per-call `async_sessionmaker(dbengine.get())` construction with
`get_async_session_maker()`, backed by `GlobalVar` (a plain instance
attribute, not a `ContextVar` — genuinely process-wide) and memoized after
first build. Pool size/overflow are now `Settings` fields
(`db_pool_size`/`db_pool_max_overflow`, defaults 5/10). `registry-platform`
adopted it the same day (`41147a9`, G2P-5620) across its services.

**5. Registry-platform caching changes, Aug 12 – Sep 2 (this checkout) —
applied, mixed effect.** In commit order:
  - `59209d7`/`5c0a396`/`c8efcac`/`4342369`/`7ade042`/`3fa183e` (G2P-5507–5513,
    Aug 12): per-endpoint tuning for `get_change_requests_flattened`,
    `get_number_of_pending_change_requests`, `get_subject_record`,
    `get_all_tabs`, `get_version_dates`, `get_versions_for_a_date`,
    `search_in_a_register` — mostly the indexes in item 2 plus new cached
    helpers `_get_register_definition`/`_require_register_definition` and
    `_get_tab_sections` (`single_id_key_builder`/`pair_id_key_builder`),
    reused across several of these methods instead of re-querying inline.
  - `b852f24` (G2P-5514): wrapped `get_register_summary_data` itself in
    `@cache(key_builder=data_policies_key_builder)` (TTL fixed at 60s in
    `0699d12`), and moved tab→sections assembly in
    `g2p_register_metadata_service` behind a similar cache, replacing an
    N-per-section validation loop with one join query. **This masks but
    does not fix** the underlying per-register N+1 unindexed `COUNT(*)` —
    the 60s cache absorbs repeat calls, but a cold cache or TTL expiry
    under load still pays the full sequential-scan cost, and concurrent
    misses aren't coalesced (a stampede risk `fastapi-cache`'s `@cache`
    doesn't address). The proposed
    `pg_stat_user_tables.n_live_tup` approximate-count fix was not applied.
  - `0699d12` (G2P-5609): namespaced, invalidated `@cache` on AWE-policy
    resolution (`policy_lookup_key_builder`, explicit
    `FastAPICache.clear(namespace=...)` on create/update/delete) — correctly
    designed and covered by unit tests (cache-hit, cache-miss-on-different-key,
    invalidation-on-write).
  - `37284e2`: the same thin-cached-wrapper-plus-`_assemble_*` pattern
    extended to intake-form services (`render_intake_form`, `get_all_tabs`,
    `get_all_sections`).
  - `2ef461b`: validation-method refactors in the same services, no new
    caching primitives.

**6. Async AWE-request creation for `create_cr`/`finalize_intake` —
identified as a candidate, not yet applied.** Both still call AWE
synchronously to create the workflow. A Celery worker/beat setup already
exists in this codebase (`celery/openg2p-registry-celery-beat`) for the
data-ingest pipeline, but nothing yet routes AWE request creation through
a queue table or a Celery task.

**7. Second AWE call in `list_tasks_for_request` — not found in the repo.**
`awe_helper.py`'s `list_tasks_for_request` still makes two sequential
`_list_tasks` calls (`assignee="*"` then `assignee="me"`) — unchanged
since it was introduced (`0ac9dce`), across all branches, no uncommitted
diff. Same caveat as item 3: this is still the contributor behind
`list_tasks_for_request`'s p95 growth (Measurements above) and needs
confirming before it's cited as resolved.

**8. AWE connection-pool parameters made configurable — applied.**
`DB_POOL_SIZE`/`DB_POOL_MAX_OVERFLOW`/`DB_POOL_RECYCLE` env vars, added in
`155463b` and adjusted in `072e943` (both `awe`) — see item 1 for the
actual deployed numbers.

**9. PgBouncer added for connection pooling — applied, infra-level, not
yet load-tested.**
[`postgres-settings/pgbouncer-config.txt`](../../postgres-settings/pgbouncer-config.txt)
(added `0520f97`, alongside the Primary-tier seed) configures a PgBouncer
instance in front of the host PostgreSQL — `pool_mode = transaction`,
`listen_port = 6432`, `default_pool_size = 50`, `min_pool_size = 10`,
`reserve_pool_size = 10` (`reserve_pool_timeout = 5s`),
`max_client_conn = 200`; see
[`environment-topology.md`](../environment-topology.md)'s "PostgreSQL &
PgBouncer configuration" section for the full settings table. This is an
infra-level change — no application code references PgBouncer directly,
app pods connect to `:6432` instead of Postgres' own port — addressing
[`environment-topology.md`](../environment-topology.md)'s note that
connection pooling in front of the host Postgres is "usually the real
ceiling" on this topology. Whether it actually raises that ceiling isn't
validated yet: that's exactly what the `db-sweep` exercise (still
pending) is for.

**Also confirmed while auditing the above (not in the original list):**
`155463b` added several more indexes on AWE's own tables
(`ApprovalTask`, `ApprovalRequest`, `ApprovalDecision`, `ApprovalEvent`,
`UserDelegation`), switched `list_tasks`/`decide` from `selectinload` to
`joinedload` to fold a decision's owning-request lookup into one query
instead of a second `session.get()`, reduced `search_requests`'s max
`limit` from 500 to 100, and added a 5-minute in-process TTL cache for
`_load_policy` (`engine.py`). `resolver.py`'s dead `_ResolutionCache` and
`auth_id_type_config_cache`'s `ContextVar` bug remain unaddressed — real
gaps for `role`/`group` approver rules and for the sibling `auth_models`
package respectively, but a no-op on the current `rule_type='user'` seed
data.
