# Test Scenarios for staff-api

## 1. Objectives

Establish, with reproducible evidence on the production-equivalent 3-node
deployment ([`environment-topology.md`](../environment-topology.md)):

1. **Per-pod API capacity** — the max RPS each of the 5 scenarios (and the
   blended mix of all 5) sustains before any endpoint's p95/p99 SLO or the
   pod's CPU headroom is exhausted — for Step 1 (isolated), not a
   failure-rate threshold (§3, §6).
2. **Time-stability** — that capacity holds over an 8-hour soak at 80% of the
   discovered blended max (no memory leak, connection leak, latency creep, or
   error growth).
3. **Horizontal scaling factor** — how the blended max RPS changes from
   Pod-Scale 1 → 2 → 3, and the scaling efficiency (actual ÷ ideal-linear),
   derived from repeating Step 2 at each Pod-Scale, not run separately.
4. **Database ceiling** — RPS and latency vs PostgreSQL tuning/sizing
   (`db-sweep`, §7) — structurally different from 1–3 (§3).
5. **Capacity / sizing model** — the headline output (see [`final-report.md`](final-report.md)).

**Async pipeline throughput (Celery ingestion/outgestion/dedup) is out of
scope for this round**; revisit once the Volume-Tier × Pod-Scale matrix below
is done.

## 2. Scope

This document covers **staff-api only**. `partner-api` and `celery` each have
their own test-scenarios doc —
[`../partner-api/test-scenarios.md`](../partner-api/test-scenarios.md) and
[`../celery/test-scenarios.md`](../celery/test-scenarios.md).

**In scope**
- Synchronous APIs of `staff-portal-api` (§4).
- Host PostgreSQL on the storage node, as a tuning target (`db-sweep`).
- Auth on the hot path (Keycloak OIDC token validation).

**Out of scope**
- Staff Portal UI (Next.js) rendering.
- Keycloak / MinIO / Kafka internal scaling — provided dependencies,
  monitored, not tested.
- `bene-portal-api` (disabled by default).
- Chaos/failover/DR testing.

## 3. The model: two axes, a repeated 3-Step plan, plus a separate db-sweep

Every capacity/soak run sits at a point in a **Volume-Tier × Pod-Scale**
matrix. The same 3 Steps repeat at whichever cells matter for the question at
hand — skip the rest. `db-sweep` is a separate exercise outside this matrix
(below).

### Volume-Tier

The seeded data size — see [`seeding-design.md`](../seeding-design.md) for the
generator. `smoke` is harness validation, not a capacity figure — it may
still appear in [`raw-report.md`](raw-report.md) and, labeled as a
methodology sample, in [`final-report.md`](final-report.md) §3, but isn't a
real ceiling.

| Volume-Tier | Farmer records |
|---|---:|
| `smoke` | 10K |
| `primary` | 10M |
| `stretch` | 50M |
| `stress` | 100M |

### Pod-Scale

The number of `staff-portal-api` replicas under test, HPA off,
`requests == limits`. Pod spec (vCPU/RAM): see
[`environment-topology.md`](../environment-topology.md) ("Pod configuration")
— the single source for this, not repeated here.

| Pod-Scale | Replicas |
|---|---|
| `1`, `2`, `3` | see [`environment-topology.md`](../environment-topology.md) — all share one compute node |

### The 3 Steps (repeated at each Volume-Tier × Pod-Scale cell you choose to run)

| Step | What it does | Duration |
|---|---|---|
| **1 — Isolated** | One of the 5 scenarios (§4) at a time. Ramp `+step_users` every `step_seconds`; each tracked endpoint's own p95/p99 SLO (§5) is checked every step. The ramp stops — freezing at whatever user count it has reached — the first time *either* an endpoint's SLO is breached for `SLO_BREACH_STEPS` consecutive windows *or* the pod's CPU crosses `CPU_BREACH_CORES` for `CPU_BREACH_POLLS` consecutive polls (quorum: 2-of-3+ pods, else 1-of-1-2). Failures are logged, not a stop condition (§6). The frozen level then holds for `SUSTAIN_MINUTES` — that steady-state window, not the ramp itself, is what's reported. | Ramp-until-freeze, then hold |
| **2 — Blended** | An 80:20 read:write mix across all 5 scenarios, by weight (§4). Driven by `BlendedRampShape`, a subclass of Step 1's `SLOStepRampShape` with no logic changes — identical ramp/freeze mechanics, just spawning the weighted mix instead of one scenario. | Ramp-until-freeze, then hold |
| **3 — Soak** | The blended mix again, but at a **fixed** load — 80% of *this same cell's* Step 2 result — run continuously. Not discovering a new ceiling; checking the Step-2 ceiling holds over time. | Fixed, 8h |

Which Steps run at which Volume-Tier × Pod-Scale:

| Volume-Tier | Pod-Scale | Steps |
|---|---|---|
| Smoke | 1, 2, 3 | 1-isolated (harness validation only) |
| Primary | 1, 2, 3 | 1-isolated, 2-blended, 3-soak, 4-db-sweep |
| Stretch | 3 | 1-isolated, 2-blended |
| Stress | 3 | 1-isolated, 2-blended |

`smoke` and `primary` run at every Pod-Scale because their Step-2 results feed
the scaling-factor calculation below, which needs the same tier at Pod-Scale
1, 2, and 3. `stretch`/`stress` only need to answer "does this still hold at
higher data volume", so they run once, at Pod-Scale 3 (the
production-representative scale) — not across all three.

**Derived from the matrix, not run as separate tests:**

- **Scaling factor.** After Step 2 has run at Pod-Scale 1, 2, and 3 for the
  same Volume-Tier (`primary`), take each cell's blended max RPS from
  `blended-capacity.csv` and compute, for N = 2 and N = 3:
  - `scaling_factor(N) = max_rps(pod_scale=N) / max_rps(pod_scale=1)`
  - `scaling_efficiency(N) = scaling_factor(N) / N` — 1.0 is perfect linear
    scaling; a value below 1.0 quantifies how much throughput is lost to
    contention (DB connections, shared node CPU, etc.) as pods are added.
- **Data-volume sensitivity.** After Step 1 or Step 2 has run at a fixed
  Pod-Scale across two or more Volume-Tiers, take each tier's max RPS and p95
  latency from `isolated-capacity.csv` / `blended-capacity.csv` and compute
  the change tier-to-tier (e.g. `primary` → `stretch` → `stress`):
  - `Δ max_rps % = (max_rps(tier_b) - max_rps(tier_a)) / max_rps(tier_a) * 100`
  - `Δ p95_ms = p95(tier_b) - p95(tier_a)`
  A material drop in RPS or rise in p95 as data volume grows points to a
  volume-dependent bottleneck (index depth, table scan cost) rather than a
  request-rate one.

Both calculations reuse numbers already captured while running Steps 1–2 at
each matrix cell — no separate load-generation run produces them.

### `db-sweep` — a separate exercise, not part of the matrix

`db-sweep` repeats the **same blended load** (Step 2's methodology) while
varying **PostgreSQL-side configuration** — a third dimension that isn't
Volume-Tier or Pod-Scale and doesn't get repeated across the matrix the way
Steps 1–3 do. Typically run at one fixed, already-identified-as-DB-stressed
cell (e.g. `stress`/`1`), sweeping:

- baseline `postgresql.conf` → tuned (`shared_buffers`, `work_mem`,
  `effective_cache_size`, `max_connections`, autovacuum) → tuned + PgBouncer
- optionally: DB VM resize, gp3 IOPS bump

It answers a different question than the matrix does: once the app tier
isn't the bottleneck, what caps throughput on the DB side — raw config,
connection pooling, or disk? See §7 for the procedure.

## 4. Test scenarios (`locust/api/staff-api/`)

The endpoints below are the **real routes** of the OpenG2P Registry platform
(`registry-platform/apis/...`), POST JSON unless noted. Each scenario is a
standalone Locust `User` class, run in isolation for Step 1 (§3). For Step 2
(§3, §7), the same 5 `User` classes are spawned together as a weighted mix by
[`blended/blended_locustfile.py`](../../locust/api/staff-api/blended/blended_locustfile.py)
— no separate scenario code, just each class's `weight` set so Locust's
spawner draws users in that ratio:

| Scenario | Weight | Share of users | Read/Write |
|---|---:|---:|---|
| `register_read` | 40 | 40% | read |
| `cr_read_and_approve` | 20 | 20% | read |
| `intake_read_and_approve` | 20 | 20% | read |
| `cr_create` | 10 | 10% | write |
| `intake_create` | 10 | 10% | write |

40 + 20 + 20 = 80% read, 10 + 10 = 20% write — the "80:20 read:write mix"
referenced throughout this doc. All 5 acquire one OIDC token per simulated
user at `on_start`, cached and refreshed on expiry.

Each endpoint has its **own** p95/p99 SLO — see §5. The Class column is only
a scenario grouping, not a shared latency budget.

### `register_read/` — browse + version-history read, including change requests per tab

Purpose: the dominant read path — search, then drill into one record's
detail across every tab, including that tab's pending change requests and
its full version history.

APIs fired, in order:

| # | API Endpoint | URL | Class | Notes |
|---|---|---|---|---|
| 1 | `get_register_summary_data` | `/register-data/get_register_summary_data` | Register-Read | Register-level overview/counts. |
| 2 | `search_in_a_register` | `/register-data/search_in_a_register` | Register-Search | The dominant read; exercises text + attribute filters. Anchored `search_text` (sticky per user), random page. |
| 3 | `get_subject_record` | `/register-data/get_subject_record` | Register-Read | Fetch one record by id. |
| 4 | `get_all_tabs` | `/register-tab-metadata/get_all_tabs` | Metadata-Read | |
| 4a | `get_tab_sections` | `/register-tab-metadata/get_sections` | Metadata-Read | Repeats once per tab. |
| 4b | `get_tab_records` | `/register-data/get_tab_records` | Register-Read | Tab materialisation. Repeats once per tab. |
| 4c | `get_number_of_pending_change_requests` | `/change-requests/get_number_of_pending_change_requests` | Change-Request-Read | Repeats once per tab. |
| 4d | `get_change_requests` | `/change-requests/get_change_requests` | Change-Request-Read | Paginated; walks every page. Repeats once per tab. |
| 4da | `get_change_request_documents` | `/documents/get_change_request_documents` | Document-Fetch | Repeats once per change request found in 4d. |
| 4db | `get_section_ui_schema` | `/register-section-metadata/get_section_ui_schema` | Metadata-Read | Conditional — only if the change request's `section_id` is present. Repeats once per change request. |
| 4dc | `get_change_request` | `/change-requests/get_change_request` | Change-Request-Read | Fetch one CR by id. Repeats once per change request. |
| 4dd | `check_change_request_sequence` | `/change-requests/check_change_request_sequence` | Change-Request-Read | Repeats once per change request. |
| 4de | `list_tasks_for_request` | `/awe/list_tasks_for_request` | Workflow-Read | AWE task list for the CR's `awe_request_id`. Conditional — only if `awe_request_id` is present. Repeats once per change request. |
| 4df | `get_deduplication_change_request_results` | `/register-data/get_deduplication_change_request_results` | Change-Request-Read | Simple fetch of results Celery already crunched, not fuzzy-match compute. Repeats once per change request. |
| 4dg | `get_deduplication_register_results` | `/register-data/get_deduplication_register_results` | Register-Read | Same caveat as above. Repeats once per change request. |
| 4f | `get_number_of_versions` | `/register-data/get_number_of_versions` | Register-Read | Version/history read (joins `*_history`). Repeats once per tab. |
| 4g | `get_version_dates` | `/register-data/get_version_dates` | Register-Read | Version/history read (joins `*_history`). Repeats once per tab. |
| 4ga | `get_versions_for_a_date` | `/register-data/get_versions_for_a_date` | Register-Read | Repeats once per date returned by 4g (every date, not a sample). |

Search anchoring: at `on_start`, the user picks one random 4-char anchor from
`seed_manifest.json`'s `search_terms` and stays sticky to it all session.
`current_page` is randomized within the last search's `number_of_pages`, so
reads spread across the result set.

### `cr_create/` — change-request creation against the Farmer register

Purpose: the change-request write path, including document upload for
sections that require it.

APIs fired:

| # | API Endpoint | URL | Class | Notes |
|---|---|---|---|---|
| 1 | `get_register_summary_data` | `/register-data/get_register_summary_data` | Register-Read | Register-level overview/counts. |
| 2 | `search_in_a_register` | `/register-data/search_in_a_register` | Register-Search | Anchored, random page. |
| 3 | `get_subject_record` | `/register-data/get_subject_record` | Register-Read | Fetch one record by id. |
| 4 | `get_all_sections` | `/register-section-metadata/get_all_sections` | Metadata-Read | Register-wide — also the source of `documents_required` per section. |
| 5 | `get_all_tabs` | `/register-tab-metadata/get_all_tabs` | Metadata-Read | |
| 5a | `get_tab_sections` | `/register-tab-metadata/get_sections` | Metadata-Read | Repeats once per tab. Response embeds each section's `section_ui_schema` (`section_data.section_ui_schema`) — verified the staff-portal UI reads it from here rather than calling `get_section_ui_schema` separately, so this locustfile does the same; no dedicated `get_section_ui_schema` call in this scenario. |
| 5b | `get_tab_records` | `/register-data/get_tab_records` | Register-Read | Tab materialisation. Repeats once per tab. |
| 5c | `get_attribute_values` | `/attributes/get_attribute_values` | Metadata-Read | Conditional — only if the field's enum is API-sourced. Repeats once per tab. |
| 5d | `upload_documents` | `/documents/upload_documents` | Document-Upload | Streams to MinIO, raw multipart. Conditional — only if the chosen section's `documents_required` is true; 3 files in one call. Repeats once per tab. |
| 5e | `create_change_request` or `create_change_request_for_core_data` | `/change-requests/create_change_request` or `/change-requests-core-data/create_change_request_for_core_data` | Change-Request-Write | EDIT route; writes record + `*_history`. Core vs. non-core section decides which; uploaded documents attached via `documents` field. Repeats once per tab (one CR per tab). |

Search anchoring: same sticky-per-user pattern as `register_read`.

### `cr_read_and_approve/` — approve pending change requests

Purpose: the change-request read-and-approve workflow, plus dedup checks.

APIs fired:

| # | API Endpoint | URL | Class | Notes |
|---|---|---|---|---|
| 1 | `get_register_change_request_summary_data` | `/change-requests/get_register_change_request_summary_data` | Change-Request-Read | Register-wide pending/approved/total counts. Once. |
| 2 | `search_in_change_request` | `/change-requests/search_in_change_request` | Register-Search | Anchored, walks **every** page, not just one. |
| 3 | `get_change_request_documents` | `/documents/get_change_request_documents` | Document-Fetch | Repeats once per pending CR. |
| 4 | `get_section_ui_schema` | `/register-section-metadata/get_section_ui_schema` | Metadata-Read | Conditional — only if the CR's `section_id` is present. Repeats once per pending CR. |
| 5 | `get_change_request` | `/change-requests/get_change_request` | Change-Request-Read | Fetch one CR by id. Repeats once per pending CR. |
| 6 | `get_deduplication_change_request_results` | `/register-data/get_deduplication_change_request_results` | Change-Request-Read | Simple fetch of results Celery already crunched, not fuzzy-match compute. Repeats once per pending CR. |
| 7 | `get_deduplication_register_results` | `/register-data/get_deduplication_register_results` | Register-Read | Same caveat as above. Repeats once per pending CR. |
| 8 | `list_tasks_for_request` | `/awe/list_tasks_for_request` | Workflow-Read | AWE task list for the CR's `awe_request_id`. Conditional — only if `awe_request_id` is present. Repeats once per pending CR. |
| 9 | `submit_task_decision` | `/awe/submit_task_decision` | Workflow-Write | Approves the first open/claimed AWE task found in step 8. Conditional — only if such a task exists. Repeats once per pending CR; still enforces the sequence check server-side (an earlier pending CR on the same `internal_record_id` blocks). |

No client-side `check_change_request_sequence` call — multiple pending CRs on
the same section are no longer possible, so the advisory pre-check can't
block anything and was removed. Processing still goes oldest-first
(`sort_pending_oldest_first`) since `submit_task_decision`'s server-side
check is scoped by `internal_record_id`, not `section_id` — broader than the
new invariant, and unchanged as of this pull.

Search anchoring: sticky per user, same as `register_read`. Finds matches
once `cr_create` has run and created change requests against the anchored
data.

### `intake_create/` — new farmer intake submission, one section at a time

Purpose: the intake write path — the flow that actually seeds new,
live-created (not bulk-generated) farmer data other scenarios read from.

APIs fired:

| # | API Endpoint | URL | Class | Notes |
|---|---|---|---|---|
| 1 | `get_intake_form_submissions_summary` | `/intake-form-data/get_intake_form_submissions_summary` | Intake-Submission-Read | Register-wide summary counts. Once. |
| 2 | `render_intake_form` | `/intake-form-metadata/render_intake_form` | Metadata-Read | Full tab + section structure for the form in one call, filtered to the Farmer intake tab; sections carry `documents_required` directly. |
| 3 | `upload_documents` | `/documents/upload_documents` | Document-Upload | Streams to MinIO, raw multipart. Conditional — per section, only if `documents_required`; 3 files. |
| 4 | `save_intake_form_submission` | `/intake-form-data/save_intake_form_submission` | Intake-Submission-Write | Per-section INSERT route. Repeats once per section (3–4 repeat as a group); `documents` attached if uploaded. |
| 5 | `get_intake_form_submission` | `/intake-form-data/get_intake_form_submission` | Intake-Submission-Read | Fetch one submission by id. Once, after all sections are saved. |
| 6 | `finalize_intake_form_submission` | `/intake-form-data/finalize_intake_form_submission` | Intake-Submission-Write | Commits the record + history — this is where the real register row is actually written. |

Search anchoring: not sticky — each generated farmer's `first_name` gets one
anchor chosen at random and spliced in, same as the bulk generator
([`seeding-design.md`](../seeding-design.md) "Search-text anchors"). This
lets `cr_read_and_approve`/`intake_read_and_approve` find live-created data
too, not just bulk-seeded rows.

Household linkage: `link_internal_record_id` for the household-lookup section
comes from `choose_household_id()`, a random pick from `seed_manifest.json`'s
`household_ids`.

One of 9 known-editable attributes (across sections) is randomized per
invocation; everything else in that section keeps a fixed baseline value.

### `intake_read_and_approve/` — approve pending intake submissions

Purpose: the intake read-and-approve workflow, plus dedup checks.

APIs fired:

| # | API Endpoint | URL | Class | Notes |
|---|---|---|---|---|
| 1 | `get_intake_form_submissions_summary` | `/intake-form-data/get_intake_form_submissions_summary` | Intake-Submission-Read | Register-wide summary counts. Once. |
| 2 | `search_in_intake_form_submissions` | `/intake-form-data/search_in_intake_form_submissions` | Register-Search | Anchored, walks every page. |
| 3 | `get_intake_form_submission` | `/intake-form-data/get_intake_form_submission` | Intake-Submission-Read | Fetch one submission by id. Repeats once per pending submission. |
| 4 | `get_intake_form_documents` | `/documents/get_intake_form_documents` | Document-Fetch | Repeats once per pending submission. |
| 5 | `get_deduplication_intake_form_register_results` | `/intake-form-data/get_deduplication_intake_form_register_results` | Intake-Submission-Read | Repeats once per pending submission. |
| 6 | `get_deduplication_intake_form_intake_form_results` | `/intake-form-data/get_deduplication_intake_form_intake_form_results` | Intake-Submission-Read | Repeats once per pending submission. |
| 7 | `list_tasks_for_request` | `/awe/list_tasks_for_request` | Workflow-Read | AWE task list for the submission's `awe_request_id`. Conditional — only if `awe_request_id` is present. Repeats once per pending submission. |
| 8 | `submit_task_decision` | `/awe/submit_task_decision` | Workflow-Write | Approves the first open/claimed AWE task found in step 7. Conditional — only if such a task exists. Repeats once per pending submission. |

Search anchoring: sticky per user; finds real matches once `intake_create`
has run (same reasoning as `cr_read_and_approve`).

`get_file_url` (`/documents/get_file_url`, Document-Fetch class) isn't fired
by any of the 5 scenarios yet — its SLO (§5) is reserved for future use.

## 5. Service-Level Objectives (per endpoint)

Each Locust `name=` has its own p95/p99 in `locust/api/env.sh` (`ENDPOINT_SLOS`).
The ramp checks that pair, not a class-wide number. For Step 1, this is the
exact pair `SLOStepRampShape` (`locust/api/shared/slo_shape.py`) evaluates
every ramp step against — see §3/§6/§7 for how a breach here (or on the pod's
CPU) freezes the ramp.

Bands (primary isolated stats):

| Kind | p95 | p99 | Applies to |
|------|----:|----:|---|
| Read | 800 ms | 1000 ms | Metadata, register/CR/intake GETs, document fetch, `list_tasks_for_request` |
| Search | 900 ms | 1000 ms | `search_in_a_register`, `search_in_change_request`, `search_in_intake_form_submissions` |
| Write | 1000 ms | 1200 ms | `save_intake_form_submission`, `upload_documents` |
| Write + AWE | 1200 ms | 1400 ms | `create_change_request`, `create_change_request_for_core_data`, `finalize_intake_form_submission`, `submit_task_decision` |

## 6. Pass / fail criteria

**Steps 1–2 (isolated, blended).** Both are driven by the same shape
(`SLOStepRampShape` for Step 1; `BlendedRampShape` — an unmodified subclass
— for Step 2), so both follow the same rule. The ramp does not stop on
failures — 5xx/timeouts are logged per endpoint but never freeze the ramp
or feed the p95/p99 that's checked (only successful request times count;
see `slo_shape.py`'s `_on_request`). Instead, the ramp freezes the first
time *either*:
- an endpoint's own p95 **or** p99 crosses its SLO (§5) for
  `SLO_BREACH_STEPS` (2) consecutive 30s windows — each window needs
  ≥`min_requests_for_check` (100) successful samples for that endpoint
  before it's evaluated at all, so one slow outlier can't trigger it — **or**
- the pod's CPU crosses `CPU_BREACH_CORES` (1.85, out of a 2 vCPU / 2000m
  limit) for `CPU_BREACH_POLLS` (2) consecutive 10s `kubectl top` polls,
  with quorum (2-of-3+ replicas hot, or 1-of-1-2).

For Step 2, "an endpoint's own SLO" means any endpoint fired by *any* of the
5 weighted scenarios (§4) — a breach in one scenario's traffic (e.g.
`cr_create`'s `create_change_request` at only 10% weight) freezes the whole
blended ramp, not just that scenario's share.

The **reported result** for a cell is the frozen user count and its RPS —
the level the ramp had reached when the breach was confirmed — held for
`SUSTAIN_MINUTES` afterward so the reported endpoint stats come from a
steady-state window, not mid-ramp. Which condition triggered the freeze
(which endpoint's SLO, or CPU) is recorded as the saturating factor.
Reaching `MAX_USERS` with no breach freezes and holds the same way, with
`max_users` itself as the result.

**Step 3 (soak).** Not yet built (§7) — runs at a **fixed** load (80% of
Step 2's frozen RPS for this cell) rather than ramping, so this is a
different, simpler pass/fail: at steady state, p95 (and p99) ≤ the endpoint
SLO **and** error rate = 0 (no 5xx, no timeouts, no DB-connection errors)
**and** both hold for the full 8h with no upward memory/latency trend.

## 7. Execution runbook

### Prep (once, before entering any matrix cell)

1. **Freeze versions** — chart version, image tags, git SHA, Postgres version.
2. **Seed data** to whichever Volume-Tier(s) you'll test per
   [`seeding-design.md`](../seeding-design.md); `ANALYZE`; verify indexes; warm
   cache.
3. **De-burst the DB node** — enable T3 Unlimited on the storage node, or move
   PG to a non-burstable instance for the duration.
4. **Stand up observability** — Prometheus/Grafana for pod+node CPU/mem;
   `postgres_exporter` + `pg_stat_statements` on the storage node. Confirm
   dashboards show live data.
5. **Pin the pod under test** — `replicas` = the Pod-Scale you're about to
   run, HPA off, `requests == limits` at the spec in
   [`environment-topology.md`](../environment-topology.md) ("Pod
   configuration"). Sweep gunicorn/uvicorn `NO_OF_WORKERS ∈ {1,2,4}` at a
   fixed moderate load and keep the value with best RPS-at-SLO; record it.
6. **Deploy Locust** in-cluster (for per-pod/scaling) and/or on an external
   host (for end-to-end). Load the seed manifest. Validate one of each
   request type returns 2xx before load.

### Step 1 — Isolated (per Volume-Tier × Pod-Scale cell)

Driven by a custom Locust shape, `SLOStepRampShape`
(`locust/api/shared/slo_shape.py`), not a manually-stepped ramp. For each of
the 5 scenarios in §4:
1. Warm up at `warmup_users` for `warmup_seconds`; this window's samples are
   discarded so cold-start latency can't trigger a breach.
2. Ramp `+step_users` every `step_seconds` — no per-user RPS cap, each
   simulated user fires its scenario's calls back-to-back, as fast as the
   API answers. Every step, check the p95/p99 of each endpoint this
   scenario actually fires (§5) against that endpoint's own SLO, and poll
   pod CPU via `kubectl top` (§6).
3. The ramp freezes — no step-down — the first time an SLO breach or a CPU
   breach is *confirmed* (§6's consecutive-window/poll rule, so a one-off
   spike doesn't trigger it). Failures (5xx, timeouts) are logged per
   endpoint throughout but never trigger the freeze.
4. Once frozen, hold the **same** user count for `SUSTAIN_MINUTES`, still
   recording — this steady-state window, not the ramp itself, is where the
   reported numbers come from. Reaching `MAX_USERS` with no breach freezes
   and holds the same way.
5. Record: RPS, p50/p90/p95/p99/max, error count by type (logged, not
   gating), pod CPU (from the same `kubectl top` polls that drove the
   freeze), DB connections, DB CPU/IO.
6. Repeat each point ≥ 2× on separate runs; report median + spread.

Deliverable: raw per-endpoint numbers for this cell in
[`raw-report.md`](raw-report.md) (regenerate via `create_raw_report.py`),
plus the curated `isolated-capacity.csv` (per-scenario capacity table + the
latency-vs-RPS "knee" chart) via `synthesize_report.py`.

### Step 2 — Blended (per Volume-Tier × Pod-Scale cell)

Run [`blended/blended_locustfile.py`](../../locust/api/staff-api/blended/blended_locustfile.py)
instead of a single scenario's locustfile — same ramp/warmup/freeze/hold
procedure as Step 1 (§6, `BlendedRampShape` changes no logic, only which
`User` classes are spawned), but Locust draws simulated users from all 5
scenarios by weight instead of running one at a time:

| Scenario | Weight | Share of users | Read/Write |
|---|---:|---:|---|
| `register_read` | 40 | 40% | read |
| `cr_read_and_approve` | 20 | 20% | read |
| `intake_read_and_approve` | 20 | 20% | read |
| `cr_create` | 10 | 10% | write |
| `intake_create` | 10 | 10% | write |

The ramp tracks every endpoint fired by any of the 5 (their union), so a
breach caused by a low-weight scenario (e.g. `intake_create` at 10%) still
freezes the whole run — see §6.

Deliverable: raw numbers in [`raw-report.md`](raw-report.md), plus the
curated `blended-capacity.csv` for this cell. Comparing this across
Pod-Scale 1→2→3 (fixed tier) gives the **scaling factor**; comparing it
across Volume-Tier (fixed pod-scale) gives **data-volume sensitivity** — see
§3.

### Step 3 — Soak (typically one cell — the production-representative one)

1. Set load to **80% of this cell's Step 2 max RPS**.
2. Run **8 hours** continuously (blended mix).
3. Watch for: upward memory trend (leak), growing DB connections
   (pool/handle leak), latency creep, any errors.
4. Pass = SLOs hold + 0 errors + flat memory for the full window.

Deliverable: the time series in [`raw-report.md`](raw-report.md) (from
Locust's `_stats_history.csv`, RPS/p95/error rate), plus pod memory/DB conns
recorded manually into `soak.csv` for this cell.

### `db-sweep` (separate from the matrix — see §3)

For each scenario below, drive the blended load from enough app pods to push
the DB, raising it to the **point of failure** (errors / p95 breach /
connection exhaustion / IOPS saturation); record the threshold RPS and the
first bottleneck. Held at one fixed Volume-Tier/Pod-Scale cell unless the
scenario itself sweeps Volume-Tier:

1. **Tuning sweep** (same VM): baseline postgresql.conf → tuned
   (`shared_buffers` ≈ 25% RAM, `effective_cache_size` ≈ 50–75% RAM,
   `work_mem`, `max_connections`, autovacuum) → **+ PgBouncer** (transaction
   pooling).
2. **Volume-Tier sweep:** `smoke` → `primary` → `stretch` → `stress`
   (re-`ANALYZE`/warm each), pod-scale held fixed.
3. **VM resize (optional):** storage 8/32 → 16/64 (non-burstable).
4. **I/O (optional):** raise gp3 IOPS/throughput if disk-bound.

Deliverable: `db-sweep.csv` (threshold RPS + first bottleneck per scenario) +
latency-vs-volume chart + top `pg_stat_statements` offenders. Not Locust-fired,
so there's no auto-generated raw table — drop the readings as a CSV (schema:
`raw_report_templates/db-sweep.csv`) into the `4-db-sweep` results folder and
`create_raw_report.py` will pick it up into [`raw-report.md`](raw-report.md) verbatim.

### Synthesis

1. Regenerate [`raw-report.md`](raw-report.md) (`scripts/create_raw_report.py`),
   then assemble all tables/graphs into [`final-report.md`](final-report.md).
2. Derive the **capacity / sizing model**.
3. List bottlenecks found and the tuning that moved them.
4. Map results to the SLOs/NFR targets → pass/fail summary.

## 8. Risks and mitigations

- Burstable `t3a` storage node throttling under sustained DB load → enable T3
  Unlimited or use non-burstable for `db-sweep`/Step 3.
- Shared single compute node → other platform pods add noise; run in quiet
  windows, capture node-level metrics, record co-tenants.
- gunicorn worker count vs the pod's actual vCPU
  ([`environment-topology.md`](../environment-topology.md)) → tune, don't
  accept the default 8.
- DB connection exhaustion (pods × workers × pool) → size pools, use
  PgBouncer.
- Benchmarking through the 2-vCPU RP for end-to-end runs → RP can cap
  throughput; separate that finding from the microservice's own capacity.
- Token endpoint accidentally under test → mitigated: tokens cached in the
  load script, one per simulated user (§4).
- DB grows during write phases → pre-size or measure write throughput
  separately.
