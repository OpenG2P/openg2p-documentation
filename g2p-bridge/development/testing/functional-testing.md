---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Functional Testing

## Testing scenarios

### From PBMS

### Independent of PBMS

#### Rest API

1. Create envelope - Happy path
2. Create envelope - with non-existent Program Mnemonic
3. Create envelope - with schedule date in the past
4. Create Disbursements - Happy path
5. Create Disbursements - with invalid envelope ID
6. Create Disbursements - with cancelled envelope
7. Create Disbursements - with no beneficiary ID
8. Create Disbursements - with duplicate beneficiary ID
9. Create Disbursements - with negative disbursal amount
10. Create Disbursements - where the total of all disbursements cross the sum specified in the envelope&#x20;
11. Create Disbursements - where number of disbursements cross the number specified in the envelope
12. Cancel Envelope - Happy path
13. Cancel Envelope - Invalid envelope ID
14. Cancel Envelope - already cancelled envelope
15. Cancel Disbursements - Happy path
16. Cancel Disbursements - Invalid disbursement ID in a batch - 1 is invalid whereas other disbursement IDs are valid

#### Downstream Batch Testing - Single Scenario covering multiple use cases

1. Create 1 envelope with 1002 disbursements, totalling upto USD 502,503 - disbursement amounts as 1, 2, 3....upto 1002 - schedule date should be in the future. The disbursement with USD 1002 - should have an invalid Beneficiary ID - Beneficiary ID should not be present in mapper
2. Cancel 1 disbursement in this envelope, the disbursement with USD 1001
3. Now check disbursement\_envelope\_status - it should show 1001 disbursements with amount as 500,500 + 1002 = 501,502
4. Manually update the envelope schedule date to TODAY - so that the downstream batch picks up the envelope for shipment
5. Give it 5 minutes - Now check disbursement\_envelope\_status - it should show 1000 disbursements as shipped (1 is cancelled, 1 is invalid beneficiary ID)
6. Wait for 10 minutes
7. Iteratively check all 1002 - disbursement\_status. Disbursement IDs - 1 to 1000 should show reconciled. Some of them should show reversed (about 30%) -- ID 1001 should show cancelled and ID 1002 - should show ??

#### Negative conditions for MT940

1. In Example Bank for the above Envelope add Wrong entries in accounting log
2. Add duplicate Debit for Disbursement ID - 1 - DUPLICATE\_DEBIT
3. Add a Debit for Disbursement ID - 1003 - INVALID\_DISBURSEMENT\_ID
4. Add a Reversal Debit for Disbursement ID - 1002 (which had invalid beneficiary ID)
5.  Generate Account Statement and upload into Bridge. Check for Reconciliation Errors. There should be these 3 entries that should show up in Recon Errors.

















