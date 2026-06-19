---
description: A hands-on, manual Postman walkthrough of the disbursement APIs (also a trainer)
---

# API Walkthrough (Postman)

A **guided, manual** run through the G2P Bridge disbursement APIs that an
implementer can do from their own laptop after installing **G2P Bridge + SPAR +
the Example Bank**. It pushes a realistic batch of beneficiaries through the
**complete digital-cash lifecycle** — link in SPAR, create an envelope, create
disbursements, watch the asynchronous pipeline advance, and reconcile — and
**shows the result at every step** in Postman's console and test panel.

It doubles as **training**: the seed data is a CSV you edit (change the schedule
date, the amounts, add or remove beneficiaries), and the requests are plain,
readable G2PConnect bodies you can inspect and reuse.

It lives in the monorepo at
[`test/api-walkthrough/`](https://github.com/OpenG2P/g2p-bridge/tree/develop/test/api-walkthrough).

{% hint style="info" %}
**Walkthrough vs. Sanity Suite.** The [Regression Sanity Suite](regression-sanity-suite.md)
is the *automated* pass/fail check of an installed system. This walkthrough is
the *manual, learn-by-doing* counterpart — same flow, but you drive it and watch
each stage. Use the sanity suite to verify; use the walkthrough to learn and demo.
{% endhint %}

## What you need

* **G2P Bridge + SPAR + Example Bank** installed and reachable on public URLs.
* **[Postman](https://www.postman.com/downloads/)** (desktop app). No other local
  installation is required.
* **Auth disabled** — the walkthrough assumes signature / keymanager validation
  is **off** (the default for a try-out environment). If your environment
  enforces signed requests, this walkthrough will not pass as-is.

## Files

Download these three from
[`test/api-walkthrough/`](https://github.com/OpenG2P/g2p-bridge/tree/develop/test/api-walkthrough):

| File | What it is |
| --- | --- |
| `G2P-Bridge-API-Walkthrough.postman_collection.json` | The collection (5 folders, ready to import). |
| `G2P-Bridge.postman_environment.json` | The environment template (URLs + run settings). |
| `beneficiaries.csv` | The **seed data** — edit this. One row per beneficiary. |

## The seed data (`beneficiaries.csv`)

The CSV is the Collection Runner **data file**. Each row is one beneficiary; the
collection iterates over it. Columns:

| Column | Meaning |
| --- | --- |
| `beneficiary_id` | Unique id, used in SPAR and on the disbursement. |
| `beneficiary_name` | Display name. |
| `account_number`, `branch_code`, `bank_code` | The beneficiary's bank financial address. |
| `mobile`, `email` | Contact details (carried on the FA). |
| `amount`, `currency` | The disbursement amount. |
| `scenario` | Drives what the walkthrough does with the row — see below. |

The shipped file has **25 beneficiaries** — enough to look like a real batch,
small enough to finish in under a minute — deliberately mixing **success and
failure** so you see both:

| `scenario` | Rows | What it demonstrates |
| --- | --- | --- |
| `happy` | 20 | Linked in SPAR at the Example Bank, valid account → **paid and reconciled**. |
| `missing_from_spar` | 3 | **Not linked** in SPAR → FA resolution skips them → **never disbursed** ("ID missing from SPAR"). |
| `bad_account` | 2 | Linked at a **foreign bank** (`OTHER-BANK`) → the payment is routed to a clearing account, so the beneficiary's **own account is never credited** (the simulator also reverses ~30% of foreign-bank payments outright). |

**Edit freely.** Change the `amount`s, change the beneficiaries, add or remove
rows. The only rule: keep the envelope counts in sync (next section).

{% hint style="warning" %}
**About the `bad_account` case.** The bundled Example Bank is a *simulator*: it
auto-creates a beneficiary account on credit and only fails foreign-bank payments
**randomly (~30%)**, so there is no per-account hard-fail switch. The reliable,
observable effect is that a foreign-bank beneficiary's **own account is never
credited** (the money lands in the bank's clearing account). That is what the
walkthrough checks. The explicit reversals you may also see in reconciliation
(`ACCOUNT_CLOSED`, `ACCOUNT_NOT_FOUND`, …) are simulated probabilistically.
{% endhint %}

## Setup (once)

1. **Import** both JSON files into Postman: *Import* → drop in the collection and
   the environment.
2. **Select** the environment (top-right dropdown): *G2P Bridge - Walkthrough*.
3. **Point it at your deployment.** Edit these environment variables (they
   default to the `trial` namespace):
   * `bridge_base_url` — `https://g2p-bridge.<ns>.<domain>/api/g2p-bridge`
   * `spar_base_url` — `https://spar.<ns>.<domain>/api/mapper/mapper`
   * `example_bank_base_url` — `https://example-bank.<ns>.<domain>/api/example-bank`
4. **Match the envelope counts to your CSV** (only needed if you changed the CSV):
   * `num_disbursements` — the number of rows.
   * `total_amount` — the **sum** of the `amount` column.
   * The shipped CSV is `25` rows × `1000` = `25000` (already preset).
5. *(Optional)* set `schedule_date` (defaults to today), and
   `sample_happy_account` / `sample_bad_account` to two account numbers from your
   CSV for the "was it credited?" checks in step 4.

## Run it (in order)

Open the **Console** (View → Show Postman Console) before you start — every step
logs a readable line there.

### Folder 1 · Health checks — *run once*

Select the folder → **Run**. Confirms the Bridge and Example Bank are reachable
and the treasury (sponsor) account is funded for the whole batch.

### Folder 2 · Create disbursement envelope — *run once*

Select the folder → **Run** (no data file). Creates one `CASH_DIGITAL` envelope
and stores its `envelope_id`. This also starts a fresh **campaign** (a unique
`run_id`) so you can re-run the walkthrough without id collisions.

### Folder 3 · Seed SPAR + create disbursements — *run with the CSV*

This is **data-driven**. In the **Collection Runner**:

1. Select the **folder** "3 · Seed SPAR + create disbursements".
2. Under **Data**, choose **`beneficiaries.csv`** (Postman shows a preview and the
   iteration count).
3. **Run**. It iterates once per row — link the beneficiary in SPAR (rows marked
   `missing_from_spar` are left unmapped on purpose), then create one
   disbursement against the envelope.

### Folder 4 · Observe the pipeline — *run manually, RE-RUN repeatedly*

The disbursement pipeline is **asynchronous** — background workers move it
forward over time — so this folder is meant to be **re-run every ~15–30 seconds**
while you watch the stages advance (in the Console / test panel):

```
FA resolution → funds available → funds blocked → sponsor dispatch
              → beneficiaries credited → reconciled
```

The five requests show, in order: the batch's **FA-resolution & dispatch**
status; the envelope's **funds** status and how many disbursements it has
received; per-disbursement **reconciliation** progress; and whether a
**successful** vs a **bad-account** beneficiary actually got credited.

With the shipped CSV, the end state is: **20 reconciled**, **2** never credited
to their own account (`bad_account`), **3** never disbursed (`missing_from_spar`).

{% hint style="info" %}
Why re-run instead of "wait"? Postman fires requests back-to-back, but the
pipeline advances on background beats. Re-running is how you *watch it happen* —
which is the point of the walkthrough. (The automated sanity suite does this
polling for you.)
{% endhint %}

### Folder 5 · Cleanup — unlink SPAR — *run with the CSV*

Data-driven, same as folder 3: select the folder + `beneficiaries.csv` → **Run**
to remove the ID→FA links you created. The disbursement records stay in the
Bridge (namespaced by `run_id`) — you can keep exploring them, including in the
[Superset dashboards](../../deployment/dashboards.md).

## See it on the dashboards

Everything you just created shows up in the read-only
[Superset dashboards](../../deployment/dashboards.md): totals and by-stage on the
**Operations Overview**, the `missing_from_spar` / reversed disbursements on
**Failures & Exceptions**, and the SPAR links on the **SPAR** dashboard. The
walkthrough is a quick way to populate a fresh environment with demonstrable data.

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| Requests time out or 404 | Wrong base URLs. Re-check the three `*_base_url` variables and your namespace/domain. |
| Folder 4 never progresses past **FA resolution** | The envelope is not full: `num_disbursements` / `total_amount` don't match the disbursements actually created. They must equal your CSV's row count and amount sum. |
| `SPAR link` fails with an `ERROR` status | Check `spar_strategy_id` (default `5`) matches a BANK strategy whose deconstruct format the Bridge understands — see [Address resolver with SPAR](../../../products/g2p-bridge/tech-guides/address-resolver/account-mapper-resolution.md). |
| HTTP 401 / signed-request errors | This environment enforces auth. The walkthrough assumes auth is disabled. |
| Re-running creates duplicate-id errors | Always start a campaign from **folder 2** — it mints a fresh `run_id` used by the disbursement ids. |

## For maintainers

The three artifacts are generated from a single script,
[`test/api-walkthrough/build_collection.py`](https://github.com/OpenG2P/g2p-bridge/blob/develop/test/api-walkthrough/build_collection.py)
(the source of truth — like `provision_dashboards.py` for the dashboards). It
mirrors the request shapes used by the [sanity suite](regression-sanity-suite.md).
After editing it, regenerate:

```bash
cd test/api-walkthrough
python3 build_collection.py
```
