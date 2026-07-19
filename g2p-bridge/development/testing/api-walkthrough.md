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
[`test/api-walkthrough/`](https://gitlab.com/openg2p/g2p-bridge/g2p-bridge/-/tree/develop/test/api-walkthrough).

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
* **Signed requests (default).** The walkthrough **signs** every Bridge and SPAR
  request as a detached JWS, so it works against the secure-by-default deployment
  (**Verify Partner Signatures** ON). It ships with the bundled **test-partner** key,
  which the trial already trusts — no setup needed. To run against **your own** key,
  or against an **unsigned** environment, see [Request signing](#request-signing).

## Files

Download these three from
[`test/api-walkthrough/`](https://gitlab.com/openg2p/g2p-bridge/g2p-bridge/-/tree/develop/test/api-walkthrough):

| File | What it is |
| --- | --- |
| `G2P-Bridge-API-Walkthrough.postman_collection.json` | The collection (6 folders, ready to import). |
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

## Request signing

The G2P Bridge (and SPAR) verify a **detached JWS** signature on every request when
signature validation is on — which is the **secure-by-default** setting. A collection
**pre-request script** signs each request automatically, so the walkthrough works
against a default install with no extra steps.

**How it works:** the script signs the canonical JSON body with an RSA key and sends
the signature in the **`Signature`** header as `base64url(header)..base64url(sig)`
(empty payload segment), `alg: RS256`. The Bridge derives the partner from
`sender_app_mnemonic` and verifies against that partner's onboarded public
public key (fetched from the Partner Manager service as `PARTNER_<MNEMONIC>`).

Controlled by these environment variables:

| Variable | Default | Meaning |
| --- | --- | --- |
| `sign_requests` | `true` | Set `false` to send **unsigned** (only for an environment with validation off). |
| `signing_private_pem` | bundled **test-partner** PEM | The RSA private key used to sign. |
| `signing_kid` | test-partner thumbprint | JWS `kid` header (the cert's SHA-256 thumbprint). |
| `sender_app` | `TRAINING` | The partner mnemonic → Bridge verifies `PARTNER_TRAINING`. |
| `jsrsasign_url` | CDN | The signing library the pre-request script loads. |

The shipped key signs as `sender_app = TRAINING`, and the bundled trial seeds that
test certificate as `PARTNER_TRAINING`, so it verifies out of the box.

### Use your own key

1. Export your `.p12`'s **private key** to PEM (Postman's sandbox can't read a
   password-protected `.p12`):
   ```bash
   openssl pkcs12 -in your-key.p12 -nodes -nocerts -out your-key.key.pem
   ```
2. Paste the PEM into `signing_private_pem`, and set `signing_kid` to your cert's
   SHA-256 thumbprint (and `sender_app` to your mnemonic).
3. **Onboard your public certificate in Partner Manager** as `PARTNER_<sender_app>`
   (see [Onboarding Partners](../../deployment/onboarding-partners.md#onboard-a-partner-that-calls-the-bridge-inbound)).
   Without this the Bridge can't fetch your key and rejects the signature.

### Unsigned environment

If your deployment has **Verify Partner Signatures** off, set `sign_requests` to
`false` and the pre-request script sends plain requests.

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

### Folder 3 · Link beneficiaries in SPAR — *run with the CSV*

This is **data-driven**. In the **Collection Runner**:

1. Select the **folder** "3 · Link beneficiaries in SPAR".
2. Under **Data**, choose **`beneficiaries.csv`** (Postman shows a preview and the
   iteration count).
3. **Run**. It iterates once per row — link the beneficiary in SPAR (rows marked
   `missing_from_spar` are left unmapped on purpose) and **adds that
   beneficiary's disbursement to the batch** that step 4 will send.

### Folder 4 · Create disbursements (one batch) — *run once*

Select the folder → **Run** (no data file). It sends **all** the disbursements
built in step 3 in a **single `create_disbursements` call**, under one
batch-control id.

{% hint style="info" %}
**Why one call, not one-per-beneficiary?** The Bridge creates **one
batch-control record per `create_disbursements` call**, so a batch must be sent
together — calling it once per beneficiary with the same batch id collides and
fails. Sending the whole batch in one call is also how a real partner integrates.
{% endhint %}

### Folder 5 · Observe the pipeline — *run manually, RE-RUN repeatedly*

The disbursement pipeline is **asynchronous** — background workers move it
forward over time — so this folder is meant to be **re-run every ~15–30 seconds**
while you watch the stages advance (in the Console / test panel):

```
FA resolution → funds available → funds blocked → sponsor dispatch
              → beneficiaries credited → reconciled
```

The five requests show, in order: the batch's **FA-resolution & dispatch**
status (queried by `batch_control_id`); the envelope's **funds** status and how
many disbursements it has received; per-disbursement **reconciliation** progress
(reconciled OK / reconciled with an error / not yet); and whether a
**successful** vs a **bad-account** beneficiary actually got credited.

With the shipped CSV, the end state is: **~20 reconciled OK**, **up to 2**
reconciled with an error / never credited to their own account (`bad_account`),
**3** never disbursed (`missing_from_spar`).

{% hint style="info" %}
Why re-run instead of "wait"? Postman fires requests back-to-back, but the
pipeline advances on background beats. Re-running is how you *watch it happen* —
which is the point of the walkthrough. (The automated sanity suite does this
polling for you.)
{% endhint %}

### Folder 6 · Cleanup — unlink SPAR — *run with the CSV*

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
| Folder 5 never progresses past **FA resolution** | The envelope is not full: `num_disbursements` / `total_amount` don't match the disbursements actually created. They must equal your CSV's row count and amount sum. |
| Dispatch reaches **PROCESSED** but **nothing reconciles** | Reconciliation parses the MT940 the Example Bank pushes back; the `disbursement_id` rides in the MT940 `:61:` reference (**max 16 chars**). The collection keeps ids short on purpose (`D` + token + index) — only relevant if you change the id scheme. |
| `SPAR link` fails with an `ERROR` status | Check `spar_strategy_id` (default `5`) matches a BANK strategy whose deconstruct format the Bridge understands — see [Address resolver with SPAR](../../../products/g2p-bridge/tech-guides/address-resolver/account-mapper-resolution.md). |
| Requests rejected with an invalid-signature / `rjct.jwt.invalid` error | The Bridge doesn't trust the signing key. Either the partner cert for `sender_app` (`PARTNER_<sender_app>`) isn't onboarded on the Bridge, or `signing_private_pem` / `signing_kid` don't match it — see [Request signing](#request-signing). For an unsigned environment set `sign_requests=false`. |
| Re-running creates duplicate-id errors | Always start a campaign from **folder 2** — it mints a fresh `run_id` / `run_token` used by the disbursement ids. |

## For maintainers

The three artifacts are generated from a single script,
[`test/api-walkthrough/build_collection.py`](https://gitlab.com/openg2p/g2p-bridge/g2p-bridge/-/blob/develop/test/api-walkthrough/build_collection.py)
(the source of truth — like `provision_dashboards.py` for the dashboards). It
mirrors the request shapes used by the [sanity suite](regression-sanity-suite.md).
After editing it, regenerate:

```bash
cd test/api-walkthrough
python3 build_collection.py
```

The collection also runs **headless** (for a quick end-to-end check / CI) with
[newman](https://github.com/postmanlabs/newman) — the signing pre-request works in
newman's sandbox as well as the Postman app. Point it at a live deployment and drive
the data-driven folders with the CSV:

```bash
npx newman run G2P-Bridge-API-Walkthrough.postman_collection.json \
  -e G2P-Bridge.postman_environment.json -d beneficiaries.csv \
  --env-var num_disbursements=1 --env-var total_amount=1000
```

(One CSV row per iteration behaves as a self-contained mini-campaign — envelope →
link → disburse — so it exercises every signed Bridge **and** SPAR call and asserts
each response. For the full "one batch of N" flow, run the folders in order in the
Postman **Collection Runner** as described above.)
