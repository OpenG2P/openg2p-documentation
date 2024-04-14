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

# Features

The module will support the following functionalities at a high level

1. Ingestion (API as well as File based) of Benefit Transfers from upstream MIS/PBMS systems (compliant to G2PConnect and similar standards) - with extensibility to create custom interfaces with upstream MIS/PBMS systems.
2. Handoff (API as well as File based) to Downstream Sponsor Banks (with G2PConnect and similar standards) with extensibility to create custom interfaces with Sponsor Banks
3. Ingestion (API as well as File based) from Downstream Sponsor Banks of Reconciliation information (success/failure with appropriate reason codes) against every disbursement transaction - Reconciliation
4. A lookup to resolve / fetch the Financial Address using the Beneficiary ID using a G2P-Connect standard API interface)
5. Reporting - On Current and Historical Data with Search features on Disbursement Transactions based on Benefit Programs, Date/Month/Year of Disbursement, Beneficiary ID, Reconciliation Statuses etc.
6. Notifications to Beneficiaries on
   1. Receipt of Disbursement List for a Benefit program/disbursement cycle
   2. Receipt of Reconciliation failures from Sponsor Bank (originating from Destination banks)&#x20;
