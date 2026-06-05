# Functional Testing

Functional testing of the G2P Bridge has two parts:

* **Manual, PBMS-driven scenarios** — exercised through the PBMS UI and the wider
  integration (SPAR, Example Bank). These are listed below.
* **API-level functional scenarios** (Rest API negatives, the downstream batch
  lifecycle, and MT940 reconciliation-error handling) — these were previously
  standalone Postman collections and a script under `test/functional-test/`, and
  have now been **automated in the** [**Regression Sanity Suite**](regression-sanity-suite.md).
  Run them with the rest of the suite (`pytest`) instead of by hand.

## Testing scenarios

### From PBMS (Manual Testing)

1. Vanilla happy path - Program has 100 beneficiaries, we enrol all 100 beneficiaries into a new cycle and disburse the payments. All 100 beneficiaries should have their IDs mapped in SPAR. Batch size = 100, so that all disbursements happen in a single batch
2. Repeat scenario 1 with a reduced batch size of 10. You should see 10 batches between G2P MIS and G2P Bridge
3. Repeat scenario 1 with 2 beneficiary IDs removed from SPAR. Check failure handling for the 2 missing beneficiaries
4. Create a new cycle and enrol only 50 beneficiaries into the cycle. Disburse and reconcile the envelope numbers and the disbursement numbers.
5. Check Envelope Summary for all scenarios and check PDF rendering from the pop up page.
6. Check payment from PBMS - when SPAR services are not available for some time
7. Check payment from PBMS - when Example Bank services are not available for some time

## API-level scenarios (now automated in the sanity suite)

The scenarios below used to be run manually via Postman / a script. They are now
covered automatically by the [Regression Sanity Suite](regression-sanity-suite.md);
this table maps each legacy scenario to where it now lives.

| Legacy scenario | Now covered by |
| --- | --- |
| Create envelope — happy path | L2 e2e (`test_l2_e2e_cash`) |
| Create disbursements — invalid envelope ID | `test_l1_partner_api` |
| Create disbursements — no beneficiary ID | `test_l1_partner_negatives` (enforced → ERROR) |
| Create disbursements — negative amount | `test_l1_partner_negatives` (enforced → ERROR) |
| Create disbursements — total exceeds envelope sum | `test_l1_partner_negatives` (enforced → ERROR) |
| Create disbursements — count exceeds envelope | `test_l1_partner_negatives` (enforced → ERROR) |
| Cancel envelope — already cancelled | `test_l1_partner_negatives` (enforced → ERROR) |
| Create envelope — past schedule date / unknown program; duplicate beneficiary; disburse against cancelled envelope | `test_l1_partner_negatives` (marked **xfail** — the Bridge does not yet validate these; they flip to real passes once it does) |
| Cancel envelope / cancel disbursements — happy & partial-invalid | `test_l1_partner_negatives` (marked **xfail** — these endpoints currently return HTTP 500 even on success) |
| Downstream batch lifecycle (create → disburse → reconcile) | L2 e2e, verified stage by stage |
| MT940 reconciliation error (unmatched debit) | `test_l2_mt940_recon` (asserts `INVALID_RECONCILIATION_ID`) |

{% hint style="info" %}
Two legacy MT940 negative cases are **not** reproduced as automated tests, for
concrete reasons: a **reversal** (`RD`) line is rejected outright by the MT940
parser (so it cannot be ingested via `upload_mt940`), and **duplicate-debit**
detection needs a *previously successful* reconciliation, which depends on a
completed happy-path e2e run. Both are documented in `test_l2_mt940_recon`.
{% endhint %}
