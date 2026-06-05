---
description: Black-box regression / sanity suite for an installed G2P Bridge
---

# Regression Sanity Suite

A Python (pytest) suite that checks the **sanity of an already-installed** G2P
Bridge by pointing at its live URLs. It verifies every API and the full
digital-cash end-to-end flow, and creates only clearly-marked, self-cleaning test
data — so it is safe to run against a **fresh** or an **in-use** environment.

It lives in the monorepo at [`test/sanity/`](https://github.com/OpenG2P/g2p-bridge/tree/develop/test/sanity).

{% hint style="info" %}
**Phase 1** — point-and-run against a deployed system. CI/CD automation (GitHub
workflow, auto-deploy, emailed reports) is a later phase; the suite already emits
CI-friendly JUnit XML to slot in.
{% endhint %}

## What it tests

| Level | Marker | What | Side effects |
| --- | --- | --- | --- |
| **L0** | `smoke` | `/ping` of every service, treasury seeded, SPAR reachable | none |
| **L1** | `contract` | **Every** Partner / Bene-Portal / Example-Bank endpoint responds for basic input | none |
| **L2** | `e2e` | Full cash lifecycle, **verified stage by stage** (see below) | creates `TEST_SANITY_*` data; SPAR links auto-unlinked |

### Endpoint coverage (L0/L1)

| System | Endpoints covered |
| --- | --- |
| Partner API | `ping`, `create_disbursement_envelopes`, `cancel_disbursement_envelope`, `amend_disbursement_envelope`†, `create_disbursements`†, `cancel_disbursements`†, `get_disbursement_status`, `get_disbursement_envelope_status`, `get_disbursement_batch_control`, `upload_mt940` |
| Bene-Portal | `ping`, `disbursement/get_all_disbursements`, `disbursement/get_disbursement_summary_till_date` |
| Example Bank | `ping`, `check_funds`, `block_funds`, `generate_account_statement`†, `initiate_payment`, `ussd` |

† Marked `xfail`: these currently return HTTP 500 `Unknown Error` on
not-found/invalid input instead of a graceful response (a Bridge / Example-Bank
robustness gap). They are still called and tracked, and will auto-pass once the
services handle those inputs gracefully.

### Business-rule negatives & error paths

Beyond basic reachability, the suite asserts the Bridge **rejects bad input with
a graceful G2P `ERROR` envelope** (consolidated from the retired functional-test
Postman/script artefacts):

| Test module | Covers |
| --- | --- |
| `test_l1_partner_negatives` | Disbursement validations: missing beneficiary, negative amount, total over the envelope sum, count over the envelope — all asserted as `ERROR`. Plus `xfail`-tracked gaps the Bridge does **not** yet reject (past schedule date, unknown program, duplicate beneficiary, disburse against a cancelled envelope) and the cancel endpoints' happy-path HTTP 500. |
| `test_l2_mt940_recon` | Uploads a crafted MT940 whose debit references an unknown reconciliation id and asserts the async processor records an `INVALID_RECONCILIATION_ID` reconciliation error, read back via `get_disbursement_status`. |

### End-to-end stage verification (L2)

A batch of disbursements is pushed through the whole chain and **each stage is
asserted independently**, so a failure pinpoints exactly where it stalled —
including the money actually reaching the bank (stage 5) and the bank distributing
it to beneficiaries (stage 6). Because each transition is driven by an
**asynchronous Celery beat/worker** (not a synchronous API call), the suite
**polls and waits** between stages — so this part takes a few minutes by design
(see [Run](#run) for expected timing):

| Stage | Verified via |
| --- | --- |
| 1. Envelope + disbursements created | partner response `SUCCESS` |
| 2. FA resolved (Bridge ↔ SPAR) | `get_disbursement_batch_control` → `fa_resolution_status == PROCESSED` |
| 3. Funds checked with bank | `get_disbursement_envelope_status` → `funds_available_with_bank == FUNDS_AVAILABLE` |
| 4. Funds blocked with bank | envelope status → `funds_blocked_with_bank == FUNDS_BLOCK_SUCCESS` |
| 5. Disbursed to bank | batch control → `sponsor_bank_dispatch_status == PROCESSED` |
| 6. **Bank distributes to beneficiaries** | Example Bank `check_funds(<beneficiary acct>)` → credited |
| 7. Reconciled (MT940 → Bridge) | `get_disbursement_status` → `disbursement_recon_records` populated |

## Relationship to the unit tests

This suite is **complementary** to the in-repo unit tests (e.g.
`core/partner-api/tests/`). Those are **white-box** tests that import the
controllers and mock the services/DB — fast, hermetic, run in CI on every commit
to catch code-logic regressions. This sanity suite is **black-box** against a
**deployed** system (real network, DB, Celery, SPAR, bank) to catch
integration/deployment regressions. Keep both — they catch different classes of bug.

## Test-data convention

Everything the suite creates is namespaced under a single prefix (default
`TEST_SANITY`) plus a per-run token, e.g. `TEST_SANITY_20260604T1015_a1b2c3`.

* The disbursement **program/benefit mnemonic is `TEST_SANITY`** — exclude test
  data from operational reports with a single filter:
  `benefit_program_mnemonic LIKE 'TEST_%'`.
* The **same beneficiary IDs** are used in both SPAR (`/link`) and the Bridge
  disbursement, so ID↔FA consistency is guaranteed by construction.
* SPAR links are unlinked at session end. Bridge disbursement rows persist (no
  delete API) but are invisible to reports by the filter above.

## Where the seed data lives

All editable sample/seed data lives in **`config.yaml`** — **not** in the test
scripts:

* **Static seed** (treasury account, currency, beneficiary bank code/branch, SPAR
  strategy id, batch size & amount, and the sample batch template —
  `benefit_program_id`, `benefit_code_id`, `disbursement_frequency`) → `config.yaml`.
* **Run-scoped identifiers** (beneficiary IDs, disbursement IDs, account numbers,
  request IDs) are **generated per run** (prefix + run token) — intentionally not
  static, so runs never collide.

To change what a run disburses, edit `config.yaml`; you should not need to touch
the Python.

## Results

Every run writes results to disk automatically (unless you pass your own
`--html` / `--junitxml`):

```
results/<test_prefix>_<UTC-timestamp>/
  ├── report.html     # self-contained human report
  └── junit.xml       # machine-readable (CI)
```

The output directory is printed at the end of the run. Toggle with
`write_results` / `results_dir` in `config.yaml`.

## Setup

```bash
cd test/sanity
python3 -m venv venv && source venv/bin/activate
pip install pytest pytest-html httpx pyyaml
cp config.example.yaml config.yaml   # then edit to point at your system
```

## Configure

Edit `config.yaml` (or override any value with a `SANITY_<UPPER_SNAKE>` env var —
env wins over the file). The most important values:

| Value | Meaning |
| --- | --- |
| `namespace` | Environment segment; the Bridge / Bene-Portal / Example-Bank hostnames derive from it. |
| `bridge_base_url` / `bene_portal_base_url` / `example_bank_base_url` | Override individual service URLs if non-standard. |
| `spar_mapper_base_url` | **Required for the e2e** and **not** derived — SPAR hostnames vary. The suite runs off-cluster, so this is SPAR's **public** ingress (e.g. `https://spar.<ns>.openg2p.org/api/mapper/mapper`), not the in-cluster service name the Bridge itself uses. |
| `verify_tls` | `false` for self-signed dev certs. |
| `treasury_account_number` / `treasury_currency` | Must match the chart's `sponsorBankConfigurations`. |
| `beneficiary_bank_code` | Use the Example Bank's simulator code for a deterministic happy path. |
| `spar_bank_strategy_id` | **Environment-dependent** — the id of SPAR's BANK construct/deconstruct strategy. Required for e2e seeding. |
| `run_e2e` | `false` to run only L0/L1 (zero data created). |
| `keymanager_auth_enabled` | Keep `false` (sanity profile). If the system enforces inbound signature validation, the write tests skip. |

## Run

```bash
# Everything (auto-writes results under results/):
pytest

# Only smoke + contract (no data created):
pytest -m "smoke or contract"

# Only the end-to-end flow:
pytest -m e2e

# Point at another environment on the fly:
SANITY_NAMESPACE=qa SANITY_VERIFY_TLS=false pytest -m smoke
```

{% hint style="info" %}
**Expect the run to take a few minutes — this is normal, not a hang.** Smoke +
contract tests are quick (seconds), but the **end-to-end flow is intentionally
slow**: each stage hands work to **asynchronous Celery jobs** that only run on a
periodic **beat schedule** (e.g. the Bridge funds-check / fund-block / disburse
beats and the Example Bank batching / payment beats fire roughly every
**10–30 seconds**). The suite cannot shortcut this — it **polls between every
stage** until the job has actually run, so you will see repeated log lines like
`poll 'funds blocked': satisfied on attempt 4` while it waits.

A full `pytest` run (smoke + contract + e2e) typically completes in
**~2–5 minutes** on a healthy cluster; it can take longer if the Celery beat
cadence is slower or the workers are busy. If a stage never completes it polls
until its timeout (`e2e_pipeline_timeout_seconds` / `e2e_recon_timeout_seconds`)
and then fails with the exact stage that stalled — see
[What happens if a run fails](#what-happens-if-a-run-fails).
{% endhint %}

## Teardown (manual fallback)

SPAR links are unlinked automatically at the end of each run. If a run crashed
and left links behind, each run writes a manifest under `.sanity-runs/`; clean it
up with the standalone script:

```bash
python teardown.py --list                # show pending run manifests
python teardown.py --all --dry-run       # preview
python teardown.py --all                 # unlink everything pending
python teardown.py --run-id <run-id>     # unlink one run
```

{% hint style="info" %}
The Bridge has no delete API for disbursements, so those rows are intentionally
left in place — namespaced under the `TEST_SANITY` program and excluded from
reports by the `TEST_%` filter.
{% endhint %}

## First-run tuning

* The e2e depends on SPAR having a **BANK strategy** configured; set
  `spar_bank_strategy_id` accordingly. If seeding fails, the
  `*_spar_seeded` test reports it clearly and later stages explain where it stalled.
* Pipeline / reconciliation timeouts (`e2e_pipeline_timeout_seconds`,
  `e2e_recon_timeout_seconds`) are generous defaults; tune them to your Celery beat
  frequencies after observing the first real run.

## Running in-cluster (Rancher, no CLI needed)

The suite is also packaged as a Docker image
(`openg2p/openg2p-g2p-bridge-sanity`) and ships in the `openg2p-bridge` chart as
an **optional component** (`sanity.enabled`, off by default).

### Ways to run — at a glance

| Method | How | When |
| --- | --- | --- |
| **Rancher (no CLI)** | Apps → release → **⋮ → Upgrade** (or **Redeploy**) | The standard path — runs on every install/upgrade |
| **`helm upgrade`** | `helm upgrade <release> <chart> -n <ns> --reuse-values` | CLI equivalent of the above |
| **Local (off-cluster)** | `pytest` from `test/sanity` (see [Run](#run)) | Debugging / development |

The in-cluster run is a **post-install/post-upgrade hook Job**, so any deploy of
the release triggers it; there is no separate "run" button.

* **Trigger** — a **post-install / post-upgrade hook Job**. It runs **every time
  the chart is installed or upgraded** — i.e. each time you click **Install**,
  **Upgrade** (or **Redeploy**) in the Rancher UI. No command line required. To
  re-run on demand, just **Upgrade**/Redeploy the release again.

* **Non-failing by default** — `sanity.failOnError=false` means a failing sanity
  run **never fails the deploy**; you read the report for pass/fail. Set
  `failOnError=true` only if you want a failed run to fail the install/upgrade
  (e.g. CI gating).

* **Scope** — the run executes **smoke + contract only** (creates no data), safe
  in any environment. Set `sanity.runE2e=true` to include the data-creating
  end-to-end flow (**test environments only**).

* **Config** — built entirely from the release's own values (component hostnames
  + their `openapiRootPath`, treasury account, SPAR strategy id). The SPAR mapper
  URL has no chart variable (separate deployment), so set
  `sanity.sparMapperBaseUrl` per environment. All of these are surfaced in the
  Rancher form under the **Sanity Suite** group.

* **Reports** — written to a results **PVC**; a small **nginx viewer**
  (`sanity.viewer.enabled`) serves them at
  `https://<release>-sanity.<namespace>.<domain>/` (browse runs → open
  `report.html`). The viewer hostname derives from the **release name**, so two
  releases in one namespace don't collide. JUnit + a summary are also in the Job
  pod logs (viewable in Rancher).

Enable it in the Rancher form (Sanity Suite group) or via values:

```yaml
sanity:
  enabled: true
  runE2e: false          # true only in non-prod test environments
  failOnError: false     # keep false so a sanity failure never breaks the deploy
  sparMapperBaseUrl: "https://spar.<ns>.openg2p.org/api/mapper/mapper"
  viewer:
    enabled: true        # requires ReadWriteMany storage for the results PVC
```

{% hint style="warning" %}
The results PVC is shared by the run Job (write) and the nginx viewer (read), so
with the viewer enabled it needs a **ReadWriteMany** storage class. If RWX is
unavailable, set `sanity.viewer.enabled=false` and read results from the Job
pod's logs in Rancher.
{% endhint %}

### From Rancher (no CLI)

1. In the install/upgrade form → **Sanity Suite** group → **Enable Sanity Suite**; set **SPAR Mapper Base URL**.
2. Click **Install** / **Upgrade** — the run starts automatically.
3. **Re-run any time:** **Upgrade** (or **Redeploy**) the release again.

### Viewing reports

| Want | Where |
| --- | --- |
| Full HTML report + history of all runs | The **viewer** at `https://<release>-sanity.<namespace>.<domain>/` → click a run folder → `report.html` |
| Quick pass/fail of the last run | **Rancher → Workloads → Pods → `<release>-sanity-…` → View Logs** |
| Machine-readable (CI) | `junit.xml`, alongside each run's `report.html` on the PVC |

The Job pod persists after it finishes (replaced on the next install/upgrade), so its logs stay viewable; the viewer keeps one folder per run on the PVC.

### What happens if a run fails

* **The deploy is not affected** (default, `sanity.failOnError=false`). The Job
  always exits 0, the pod ends as **Completed**, and the release stays healthy —
  you find pass/fail in the report, not in the deploy status.
* Set **`sanity.failOnError=true`** to make a failing run **fail the
  install/upgrade** (the release shows failed; use for strict CI gating).
* **`xfail` tests don't count as failures** — they're known gaps tracked in the
  report, not red.
* In the **e2e**, each stage is asserted independently, so a failure tells you
  **exactly where it stalled** (e.g. `stage5_disbursed_to_bank`); the stages after
  it are reported failed too. A stage that never completes polls until its budget
  (`e2e_pipeline_timeout_seconds` / `e2e_recon_timeout_seconds`) and then fails.
* **Where to see it:** the HTML report (red tests, with the failing assertion and
  the last status it saw) or the Job pod logs.

{% hint style="info" %}
A failure is almost always **the system under test**, not the suite — the e2e
walks real Bridge state, so a red stage points at the Bridge/SPAR/bank step that
didn't complete. The local-run section above lists the same checks for debugging
off-cluster.
{% endhint %}
