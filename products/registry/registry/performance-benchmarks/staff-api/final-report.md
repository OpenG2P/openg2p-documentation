# Final Report

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

Items **5, 7, 8, and 10** are what reviewers/funders care about most: the
scaling factor, proof of no time-decay, the DB ceiling, and the sizing
formula.

Async pipeline throughput (Celery) is **not** a current deliverable — see
[`test-scenarios.md`](test-scenarios.md) §1/§2.

## The capacity / sizing model (headline output)

Once primary-tier data exists, the sizing statement takes this form:

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

Not yet computable — requires primary-tier ramp-to-failure data (§4-§7
below).

## Report structure

Sections are organized **Ingress › Volume-Tier › Capacity Calculations**,
mirroring [`raw-report.md`](raw-report.md)'s own hierarchy (see the
methodology note in §2) — a tier's Capacity Calculations subsection fills
in once that tier's run exists, with no separate status prose needed per
tier. End-to-end Smoke and Primary both have Step 1 (isolated, §4) data;
Primary also has Step 2 (blended) raw data, not yet synthesized into a
scaling curve (§5). Building out the pipeline surfaced one real
methodology bug and one upstream bug (§2), plus two real findings that
stand independent of any single tier's numbers: the AWE-hop bottleneck
(§4, §8) and a reported throughput improvement from the iam-core
JWKS/OIDC-metadata cache fix — though that fix does not appear in this
checkout's history (§8, item 3). Sections 6-7 (soak, `db-sweep`) and 9-11
(pass/fail, sizing) are pending those runs.

### 1. Executive summary
- **Reported improvement, code confirmed applied:** the iam-core
  JWKS/OIDC-metadata cache fix was reported to raise Pod-1 (2 vCPU / 2 GB)
  capacity from ~10 to 30+ concurrent Locust users. The fix (`iam` commit
  `4c1888b`, G2P-5647) is in this checkout — `iam` is now on its
  `performance-test` branch — see §8, item 3.
- **Headline:** Pod-Scale 1 (spec: [`environment-topology.md`](../environment-topology.md)) sustains **≥66.3 RPS** blended (Step 2) over Volume-Tier `primary` at p95 ≈420ms, near-zero failures — measured at a **fixed 20-user load**, not a ramp-to-failure, so this is a floor, not the SLO-confirmed ceiling (§5).
- **Scaling:** Pod-Scale 3 → **122.3 RPS** (efficiency **≈61%** of linear; Pod-2 → 93.4 RPS, ≈70%) — from the same fixed-concurrency data (§5).
- **DB ceiling:** **___ RPS** (`db-sweep`, tuned + PgBouncer), limited by **______**.
- **Sizing model:** to serve **T RPS** over **V M** records → **___ app pods + DB `___`**.
- **Verdict vs SLO/NFR:** PASS / FAIL — _____.

### 2. Environment & methodology
- Chart version / image tags / git SHA: ______ (Prep step 1, not yet done).
- Nodes: compute `m5a.4xlarge` (16/64), storage host-PG `t3a.2xlarge` (8/32, T3-unlimited: __), RP `t3a.medium` — see [`environment-topology.md`](../environment-topology.md).
- Pod under test: spec + `requests==limits`/HPA-off posture in [`environment-topology.md`](../environment-topology.md) ("Pod configuration"); workers = __ (Prep step 6, not yet done — worker-count sweep pending).
- PostgreSQL 16: tuning + PgBouncer config — see §3 (PostgreSQL & PgBouncer configuration); `max_connections` isn't set in either checked-in config file and still needs recording per run.
- Volume-Tier(s) / Pod-Scale(s) tested: `smoke` and `primary`, Pod-Scale 1-3, Step 1 (isolated); `primary` also has Step 2 (blended) raw data (§5). `stretch`/`stress` and Step 3 (soak) pending.
- Load tool: Locust 2.46.3; run location: external host against the public perftest hostname (`STAFF_API_BASE`), i.e. **end-to-end** ingress, not in-cluster — Prep step 7 calls for an in-cluster Locust deployment for per-pod/scaling figures, still pending.
- **Methodology finding from the dry run:** the results-folder/template ingress label was initially wrong (`in-cluster` when the run actually went `end-to-end` through the public perftest hostname) — corrected; results are now segmented by ingress at the top level (`results/staff-api/<ingress>/...`) specifically so in-cluster and end-to-end runs of the same cell can never silently overwrite each other.
- **Known upstream bug, resolved by exclusion:** in the `smoke` dry run, `register_read`'s `get_record_history` call failed 33/33 (`SYS-ERR-001`) — see [`seeding-design.md`](../seeding-design.md) (`change_request_source.value` on a plain `String` column). Decision made: the call was dropped from `register_read`'s task code rather than blocking on the upstream fix (`locust/api/env.sh`, `locust/api/shared/slo_shape.py`) — it doesn't appear in the Smoke or Primary runs and needs no further tracking.

### 3. Pod & database configuration

Pod specs (`staff-portal-api` 2 vCPU / 2 GB, AWE 2 vCPU / 2 GB, Keycloak
1 vCPU / 1 GB) and the PostgreSQL/PgBouncer tuning are now maintained in one
place — see [`environment-topology.md`](../environment-topology.md)'s "Pod
configuration" and "PostgreSQL & PgBouncer configuration" sections — rather
than duplicated here. This is the spec the End-to-End Smoke and Primary
Pod-Scale 1/2/3 runs (§4) actually ran against, and matches §2's pod-under-test
spec.

### 4. Per-scenario capacity (Step 1: isolated)

Organized **Ingress › Volume-Tier › Capacity Calculations**, mirroring
[`raw-report.md`](raw-report.md)'s own hierarchy — a tier's Capacity
Calculations subsection is filled in once that tier's isolated run exists;
an untested tier is a placeholder, not a paragraph explaining its absence.
Full per-endpoint numbers for every populated cell: the `Step: 1-isolated`
sections of [`raw-report.md`](raw-report.md); curated headline-endpoint
SLO/PASS-FAIL: `synthesize_templates/isolated-capacity.csv` (after running
`scripts/synthesize_report.py --step isolated ...`). Latency-vs-RPS "knee"
charts (one per endpoint, across ramp steps) are pending — a single-step
run doesn't produce a ramp.

#### Real-life concurrent-user estimates: methodology

Locust's `wait_time` only paces between `@task` picks, not between the
individual API calls inside one task — a Locust "user" fires a whole
scenario's calls back-to-back, unlike a real case worker. Converting
Locust throughput into a real-user-equivalent figure uses Little's Law:

```
Real concurrent users = (unit completions/sec) × (real completion time, seconds)
```

**The unit is one fully-handled record, not one `@task` iteration** — the
realistic single-record journey a case worker actually performs: search,
land on one record, fire every API that record's detail view needs, then
(where applicable) act on it:

| Scenario | One unit of work |
|---|---|
| register_read | search → zoom into 1 record → every tab, every pending CR on that tab, every version date on that tab |
| cr_create | search → pick 1 record → its tabs/sections → edit 1 section → create the CR |
| cr_read_and_approve | search → pick 1 CR → its documents/schema/dedup/tasks → approve |
| intake_create | render the form → save every section → fetch → finalize |
| intake_read_and_approve | search → pick 1 submission → its documents/dedup/tasks → approve |

For each API in a unit's chain, its contribution to "total time for 1
unit" is **its own average response time × how many times it actually
fires per unit** (`endpoint's Request Count ÷ anchor's Request Count`,
both from the same pod's CSV) — not counted once each, since several of
these calls are structurally repeated per record (a record has several
tabs; a tab has however many pending items it has) or repeated by the
test's own search/candidate-discovery process. `T_real` (assumed real
completion time — unchanged from before) is then multiplied by the
anchor's own RPS, not a session/summary endpoint's.

`cr_create` is the one scenario whose anchor is two mutually exclusive
endpoints — every CR creation calls exactly one of `create_change_request`
or `create_change_request_for_core_data`, never both. The two are combined
differently depending on what's being computed: each variant's average
response time is folded into "total time for 1 unit" as a share-weighted
average (it's a single chain step whose cost depends on which variant
fires), but "RPS to serve 1 change request created" is their **sum**, not
a weighted average — the variants are disjoint completions of the same
event, so the combined completion rate is their total, not an average
between them.

#### End-to-End

##### Volume-Tier: Smoke

###### Capacity Calculations

Two effects are visible in this tier's data.

Endpoints that stay inside registry-platform improve as pods scale, as
expected — less contention per pod:

| Endpoint | Pod-1 p95 | Pod-2 p95 | Pod-3 p95 |
|---|---|---|---|
| `get_change_request` | 860ms | 790ms | 620ms |
| `get_deduplication_register_results` | 780ms | 760ms | 600ms |

Endpoints that call out to AWE get worse as pods scale — the bottleneck is
the AWE hop, not registry-platform's own DB/CPU (root cause in §8):

| Endpoint | Pod-1 p95 | Pod-2 p95 | Pod-3 p95 |
|---|---|---|---|
| `list_tasks_for_request` | 920ms | 1100ms | 1100ms |
| `submit_task_decision` | 910ms | 980ms | 1000ms |

**register_read** — 1 register record fully read:

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
| **Total time for 1 register record** | **15.45s** | **16.66s** | **13.45s** |

| | Pod-1 | Pod-2 | Pod-3 |
|---|---|---|---|
| Locust users (peak, this run) | 28 | 48 | 56 |
| RPS to serve 1 register record (`get_subject_record`) | 1.007 | 1.494 | 2.088 |
| T_real | 30s | 30s | 30s |
| Real concurrent users | 30 | 45 | 63 |

**cr_create** — 1 change request effected:

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
| **Total time for 1 change request effected** | **1.75s** | **1.50s** | **1.32s** |

| | Pod-1 | Pod-2 | Pod-3 |
|---|---|---|---|
| Locust users (peak, this run) | 24 | 36 | 36 |
| RPS to serve 1 change request created (`create_change_request` + `create_change_request_for_core_data`) | 7.272 | 11.823 | 13.127 |
| T_real | 30s | 30s | 30s |
| Real concurrent users | 218 | 355 | 394 |

**cr_read_and_approve** — 1 change request approved:

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
| **Total time for 1 change request approved** | **11.30s** | **6.76s** | **4.27s** |

| | Pod-1 | Pod-2 | Pod-3 |
|---|---|---|---|
| Locust users (peak, this run) | 28 | 48 | 32 |
| RPS to serve 1 change request approved (`submit_task_decision`) | 1.437 | 3.939 | 4.367 |
| T_real | 30s | 30s | 30s |
| Real concurrent users | 43 | 118 | 131 |

**intake_create** — 1 intake submission created:

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `render_intake_form` | 257ms (×1.03) | 205ms (×1.02) | 162ms (×1.02) |
| `save_intake_form_submission` | 530ms (×9.17) | 407ms (×9.12) | 304ms (×9.13) |
| `get_intake_form_submission` | 383ms (×1.01) | 298ms (×1.00) | 225ms (×1.00) |
| `finalize_intake_form_submission` | 734ms (×1.00) | 613ms (×1.00) | 510ms (×1.00) |
| **Total time for 1 intake submission created** | **6.24s** | **4.84s** | **3.67s** |

| | Pod-1 | Pod-2 | Pod-3 |
|---|---|---|---|
| Locust users (peak, this run) | 20 | 28 | 28 |
| RPS to serve 1 intake submission created (`finalize_intake_form_submission`) | 1.612 | 2.734 | 3.390 |
| T_real | 60s | 60s | 60s |
| Real concurrent users | 97 | 164 | 203 |

**intake_read_and_approve** — 1 intake submission approved:

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_intake_form_submissions` | 547ms (×16.71) | 556ms (×8.84) | 332ms (×1.61) |
| `get_intake_form_submission` | 160ms (×1.05) | 213ms (×1.08) | 233ms (×1.22) |
| `get_intake_form_documents` | 107ms (×1.05) | 145ms (×1.08) | 161ms (×1.22) |
| `get_deduplication_intake_form_register_results` | 114ms (×1.05) | 151ms (×1.08) | 162ms (×1.22) |
| `get_deduplication_intake_form_intake_form_results` | 114ms (×1.05) | 147ms (×1.08) | 161ms (×1.22) |
| `list_tasks_for_request` | 175ms (×1.05) | 226ms (×1.08) | 294ms (×1.22) |
| `submit_task_decision` | 217ms (×1.00) | 280ms (×1.00) | 342ms (×1.00) |
| **Total time for 1 intake submission approved** | **10.07s** | **6.14s** | **2.11s** |

| | Pod-1 | Pod-2 | Pod-3 |
|---|---|---|---|
| Locust users (peak, this run) | 24 | 40 | 32 |
| RPS to serve 1 intake submission approved (`submit_task_decision`) | 1.130 | 3.012 | 7.733 |
| T_real | 30s | 30s | 30s |
| Real concurrent users | 34 | 90 | 232 |

**All five scenarios now scale up with Pod-Scale** under this corrected,
per-record unit — including `cr_read_and_approve` and
`intake_read_and_approve`, which the session/summary-anchored version of
this table had shown shrinking at Pod-Scale 3. That earlier drop was an
artifact of the old anchor choice, not a real capacity regression: once
throughput is measured as "records/CRs/submissions actually completed per
second" instead of "outer search-and-drain sessions completed per
second," both scenarios scale cleanly.

This does **not** contradict the separate peak-concurrency-ceiling finding
from this conversation's cr_read_and_approve re-analysis (the ramp shape
still freezes at a lower user count at Pod-Scale 3 than Pod-Scale 2, and
AWE still logs connection-reset errors under load) — that is a tail/ceiling
effect visible in the ramp shape's own ramp-to-breach behavior, not in
this typical-case, whole-run throughput number. The two findings answer
different questions: this table says "the typical CR/submission is handled
faster and more of them get done per second as pods scale"; the
peak-concurrency finding says "the *ceiling* before things start failing
is still capped by AWE's fixed capacity." Both are true at once.

**Step-by-step: theoretical capacity (server time only, before think-time)**

The tables above give "real concurrent users" from the *measured* RPS
(Locust's own completions ÷ elapsed time, think-time and all). This is a
second, independent derivation of the same quantity, built the other
direction — starting from pure server-side cost and this run's actual
concurrency, then substituting a realistic human pace for the test's own
think-time:

```
records/sec (1 user, zero pauses)   = 1 ÷ (seconds per record, from the per-API tables above)
total records/sec (server capacity) = N (peak concurrent users this run reached) × records/sec (1 user)
realistic users                     = total records/sec × T_real
```

`N` is each scenario's peak `User Count` from its own `_stats_history.csv`
— the highest concurrency the ramp shape reached before freezing at its
SLO breach, i.e. the actual number of simulated users generating load
when this pod's numbers above were recorded.

| Scenario | Pod | Seconds/record | Records/sec (1 user) | N (peak users) | Total records/sec | T_real | Realistic users |
|---|---|---|---|---|---|---|---|
| register_read | Pod-1 | 15.45s | 0.0647 | 28 | 1.812 | 30s | **54** |
| register_read | Pod-2 | 16.66s | 0.0600 | 48 | 2.880 | 30s | **86** |
| register_read | Pod-3 | 13.45s | 0.0744 | 56 | 4.164 | 30s | **125** |
| cr_create | Pod-1 | 1.75s | 0.5725 | 24 | 13.741 | 30s | **412** |
| cr_create | Pod-2 | 1.50s | 0.6652 | 36 | 23.948 | 30s | **718** |
| cr_create | Pod-3 | 1.32s | 0.7548 | 36 | 27.171 | 30s | **815** |
| cr_read_and_approve | Pod-1 | 11.30s | 0.0885 | 28 | 2.478 | 30s | **74** |
| cr_read_and_approve | Pod-2 | 6.76s | 0.1480 | 48 | 7.104 | 30s | **213** |
| cr_read_and_approve | Pod-3 | 4.27s | 0.2342 | 32 | 7.495 | 30s | **225** |
| intake_create | Pod-1 | 6.24s | 0.1602 | 20 | 3.204 | 60s | **192** |
| intake_create | Pod-2 | 4.84s | 0.2068 | 28 | 5.790 | 60s | **347** |
| intake_create | Pod-3 | 3.67s | 0.2722 | 28 | 7.623 | 60s | **457** |
| intake_read_and_approve | Pod-1 | 10.07s | 0.0993 | 24 | 2.384 | 30s | **72** |
| intake_read_and_approve | Pod-2 | 6.14s | 0.1627 | 40 | 6.509 | 30s | **195** |
| intake_read_and_approve | Pod-3 | 2.11s | 0.4746 | 32 | 15.187 | 30s | **456** |

**Why these numbers are higher than the measured-RPS table above them,
scenario by scenario:**

- `register_read`'s gap (54/86/125 here vs. 30/45/63 measured-RPS) is
  fully explained: this method strips out the locustfile's own 1-3s
  inter-tab sleep and 0.5-2s base `wait_time`, which together account for
  essentially all of the difference (worked through in this
  conversation — the two reconcile to within ~3-15% at every pod).
- The other four scenarios have no per-tab sleep, only Locust's 0.5-2s
  base `wait_time` between `@task` iterations — a small, arbitrary
  pacing choice for the test, not a stand-in for real think-time. Their
  gap (roughly 1.7-2x higher here than the measured-RPS table) is that
  same effect at a smaller scale: this method replaces that ~0.5-2s
  artificial pause with the realistic `T_real` (30s/60s) instead of
  leaving it mixed into the measured rate.

**These numbers are not a replacement for the measured-RPS table — they
answer a different question and depend on an assumption the measured
table doesn't need.** The measured-RPS table needs no assumption about
`N`; it reads directly off what Locust actually observed. This table
needs `N` (peak concurrent users) as an input, and its result is only as
good as that number — `N` is a single peak sample from a 1-second-resolution
history file, not a controlled, sustained concurrency level. Treat this
table as a cross-check that confirms the same scaling pattern from a
different angle (server-time-only capacity, independent of the test's own
pacing), not as a more-precise replacement for the directly measured
figures above. **Once the locustfiles are changed to remove artificial
pauses and re-run, the measured-RPS table and this table should converge**
— at that point, re-derive "real concurrent users" directly from the new
measured RPS × `T_real`, the same way the measured-RPS table already
does, rather than re-doing this N/T reconstruction.

##### Volume-Tier: Primary

###### Capacity Calculations

**register_read** — 1 register record fully read:

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
| **Total time for 1 register record** | **8.75s** | **7.48s** | **7.78s** |

| | Pod-1 | Pod-2 | Pod-3 |
|---|---|---|---|
| Locust users (peak, this run) | 20 | 32 | 44 |
| RPS to serve 1 register record (`get_subject_record`) | 1.609 | 2.742 | 3.496 |
| T_real | 30s | 30s | 30s |
| Real concurrent users | 48 | 82 | 105 |

**cr_create** — 1 change request effected:

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
| **Total time for 1 change request effected** | **1.11s** | **1.02s** | **1.14s** |

| | Pod-1 | Pod-2 | Pod-3 |
|---|---|---|---|
| Locust users (peak, this run) | 20 | 32 | 48 |
| RPS to serve 1 change request created (`create_change_request` + `create_change_request_for_core_data`) | 11.785 | 18.701 | 23.946 |
| T_real | 30s | 30s | 30s |
| Real concurrent users | 354 | 561 | 718 |

**cr_read_and_approve** — 1 change request approved:

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
| **Total time for 1 change request approved** | **2.70s** | **2.40s** | **2.62s** |

| | Pod-1 | Pod-2 | Pod-3 |
|---|---|---|---|
| Locust users (peak, this run) | 16 | 28 | 48 |
| RPS to serve 1 change request approved (`submit_task_decision`) | 4.541 | 8.340 | 12.266 |
| T_real | 30s | 30s | 30s |
| Real concurrent users | 136 | 250 | 368 |

**intake_create** — 1 intake submission created:

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `render_intake_form` | 192ms (×1.06) | 160ms (×1.01) | 175ms (×1.01) |
| `save_intake_form_submission` | 364ms (×9.06) | 280ms (×9.05) | 319ms (×9.04) |
| `get_intake_form_submission` | 271ms (×1.00) | 214ms (×1.00) | 240ms (×1.00) |
| `finalize_intake_form_submission` | 350ms (×1.00) | 289ms (×1.00) | 326ms (×1.00) |
| **Total time for 1 intake submission created** | **4.12s** | **3.20s** | **3.63s** |

| | Pod-1 | Pod-2 | Pod-3 |
|---|---|---|---|
| Locust users (peak, this run) | 20 | 28 | 44 |
| RPS to serve 1 intake submission created (`finalize_intake_form_submission`) | 2.915 | 4.759 | 6.272 |
| T_real | 60s | 60s | 60s |
| Real concurrent users | 175 | 286 | 376 |

**intake_read_and_approve** — 1 intake submission approved:

| API | Pod-1 avg ms (×/unit) | Pod-2 avg ms (×/unit) | Pod-3 avg ms (×/unit) |
|---|---|---|---|
| `search_in_intake_form_submissions` | 190ms (×1.85) | 222ms (×1.54) | 198ms (×14.37) |
| `get_intake_form_submission` | 227ms (×2.37) | 237ms (×2.45) | 205ms (×1.90) |
| `get_intake_form_documents` | 159ms (×2.37) | 166ms (×2.45) | 139ms (×1.90) |
| `get_deduplication_intake_form_register_results` | 161ms (×2.37) | 166ms (×2.44) | 140ms (×1.90) |
| `get_deduplication_intake_form_intake_form_results` | 161ms (×2.37) | 168ms (×2.44) | 141ms (×1.90) |
| `list_tasks_for_request` | 162ms (×2.37) | 170ms (×2.44) | 148ms (×1.90) |
| `submit_task_decision` | 197ms (×1.00) | 206ms (×1.00) | 182ms (×1.00) |
| **Total time for 1 intake submission approved** | **2.61s** | **2.77s** | **4.50s** |

Pod-3's `search_in_intake_form_submissions` ratio (×14.37, vs. ×1.85/×1.54
at Pod-1/Pod-2) is an outlier worth confirming on re-run before trusting
this pod's total — everything else in the chain moves in the expected
direction.

| | Pod-1 | Pod-2 | Pod-3 |
|---|---|---|---|
| Locust users (peak, this run) | 24 | 40 | 64 |
| RPS to serve 1 intake submission approved (`submit_task_decision`) | 4.069 | 6.966 | 5.752 |
| T_real | 30s | 30s | 30s |
| Real concurrent users | 122 | 209 | 173 |

##### Volume-Tier: Stretch

_(pending — no Stretch-tier run yet)_

##### Volume-Tier: Stress

_(pending — no Stress-tier run yet)_

#### In-Cluster

_(pending — no in-cluster run yet; see
[`environment-topology.md`](../environment-topology.md) §5 for why
in-cluster and end-to-end numbers must be measured and reported
separately, and `test-scenarios.md`'s Prep step 7 for the in-cluster
Locust deployment this needs)_

These are still `1-isolated` runs, each scenario measured with the pod
running only that workload — each figure is that scenario's ceiling in
isolation, not additive. A pod serving the real mixed workload contends
for the same DB connections, CPU, and AWE capacity across all five
scenarios at once, so the real mixed-workload concurrent-user number is
lower than each isolated figure.

### 5. Blended capacity, scaling, and data-volume sensitivity (Step 2)

Primary-tier raw data exists — Pod-Scale 1/2/3, `Step: 2-blended` (see
[`raw-report.md`](raw-report.md)) — but it's a **fixed-concurrency** run
(20/28/48 simulated users respectively), not a ramp-to-failure, so it
gives a measured floor on each pod's blended capacity, not the confirmed
SLO ceiling `test-scenarios.md` calls for:

| Pod-Scale | Concurrent users | Requests | Failures | p95 | Aggregated RPS |
|---|---|---|---|---|---|
| Pod-1 | 20 | 29,216 | 2 | 420ms | 66.26 |
| Pod-2 | 28 | 50,486 | 3 | 440ms | 93.39 |
| Pod-3 | 48 | 62,520 | 2 | 290ms | 122.26 |

Horizontal scaling efficiency from this floor: Pod-2 ≈70% of linear
(93.39 ÷ (2×66.26)), Pod-3 ≈61% of linear (122.26 ÷ (3×66.26)) — both
below the isolated-tier scaling seen in §4, consistent with AWE being a
shared, fixed-capacity bottleneck under the blended mix (§4, §8).
Synthesizing this into the curated `blended-capacity.csv` and a proper
scaling/volume-sensitivity chart is still pending — see
[`test-scenarios.md`](test-scenarios.md) §3.

### 6. Endurance / soak (Step 3)
Pending — no soak run exists yet. Planned: 8h at 80% of this cell's Step 2
max RPS, once that figure exists, reading RPS/p95/error-rate/pod-memory/DB-conns
time series from [`raw-report.md`](raw-report.md)'s `Step: 3-soak` sections
(Locust's `_stats_history.csv`).

### 7. Database ceiling (`db-sweep`)
Pending — no `db-sweep` run exists yet. Planned source:
[`raw-report.md`](raw-report.md)'s `Step: 4-db-sweep` sections
(hand-recorded readings), a latency-vs-volume chart, and the top
`pg_stat_statements`.

### 8. Bottlenecks & tuning

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
    see item 5's continuation below and the original finding in this
    conversation: the 60s cache absorbs repeat calls, but a cold cache or
    TTL expiry under load still pays the full sequential-scan cost, and
    concurrent misses aren't coalesced (a stampede risk `fastapi-cache`'s
    `@cache` doesn't address). The proposed
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
diff. Same caveat as item 3: this is still the contributor behind §4's
`list_tasks_for_request` p95 growth and needs confirming before it's
cited as resolved.

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
`max_client_conn = 200`; see §3 for the full settings table. This is an
infra-level change — no application code references PgBouncer directly,
app pods connect to `:6432` instead of Postgres' own port — addressing
[`environment-topology.md`](../environment-topology.md)'s note that
connection pooling in front of the host Postgres is "usually the real
ceiling" on this topology. Whether it actually raises that ceiling isn't
validated yet: that's exactly what `db-sweep` (§7, still pending) is for.

**Also confirmed while auditing the above (not in the original list):**
`155463b` added several more indexes on AWE's own tables
(`ApprovalTask`, `ApprovalRequest`, `ApprovalDecision`, `ApprovalEvent`,
`UserDelegation`), switched `list_tasks`/`decide` from `selectinload` to
`joinedload` to fold a decision's owning-request lookup into one query
instead of a second `session.get()`, reduced `search_requests`'s max
`limit` from 500 to 100, and added a 5-minute in-process TTL cache for
`_load_policy` (`engine.py`). `resolver.py`'s dead `_ResolutionCache` and
`auth_id_type_config_cache`'s `ContextVar` bug (both flagged earlier in
this conversation) remain unaddressed — real gaps for `role`/`group`
approver rules and for the sibling `auth_models` package respectively, but
a no-op on the current `rule_type='user'` seed data.

### 9. Pass / fail vs SLO/NFR
Pending overall PASS/FAIL — no ramp-to-failure SLO run exists yet (§4 has
Smoke and Primary isolated data, and §5 a fixed-concurrency Primary
blended floor; neither is a ramp). No failing endpoints in either tier's
data — `register_read`'s `get_record_history` (§2's upstream
`SYS-ERR-001` bug) was dropped from the task code after the Smoke dry run
and doesn't appear in any run since.

### 10. Recommendations & sizing guide
- **Production sizing:** partially computable. Primary-tier blended data
  exists (§5): Pod-Scale 1 sustains **≥66.3 RPS** blended over `primary`
  at p95 ≈420ms with near-zero failures — but at a **fixed 20-user load**,
  not a ramp-to-failure, so this is a measured floor on `R`, not the
  SLO-confirmed ceiling `test-scenarios.md` defines. A fully validated
  sizing figure still needs (a) a ramp-to-failure blended run per
  Volume-Tier/Pod-Scale cell, and (b) the DB ceiling `D` from `db-sweep`
  (§7, not yet run) to bound total pods against.
- **Config recommendations:** item 3 (JWKS/OIDC cache fix) is confirmed
  active now that `iam` is checked out on `performance-test`; confirm
  item 7 actually landed (it doesn't appear in any `awe` branch checked)
  before treating it as done; the remaining open items from §8 — moving
  AWE-request creation onto Celery (item 6), the
  `get_register_summary_data` approximate-count fix (item 5), and
  validating PgBouncer's effect under load (item 9, `db-sweep`) — are
  still open.
- **Follow-ups / known limits:** async-pipeline throughput for the
  AWE-request-creation queue (item 6 above) is separate from the existing
  ingest-pipeline Celery deployment and not covered by this round's
  scenarios ([`test-scenarios.md`](test-scenarios.md) §1/§2).

### 11. Appendix
- Raw Locust CSVs, Grafana dashboard exports, `pg_stat_statements` dumps.
- Locust config + seed manifest + exact postgresql.conf diffs.

## Conventions

- Always report **p95 and p99** (not p95 alone) and **error rate by type**.
- Every number carries its **pinned config** (Pod-Scale, worker count,
  Volume-Tier, DB tuning) — a bare "RPS" is meaningless without it.
- Report **median of ≥2 runs** plus spread; flag any run-to-run variance
  > ~10%.
- State the **ingress point** (in-cluster vs end-to-end) for every figure.
