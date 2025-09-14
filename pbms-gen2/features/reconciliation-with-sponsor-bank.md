---
layout:
  width: default
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
  metadata:
    visible: true
---

# Reconciliation with Sponsor Bank

PBMS ensures accurate reconciliation of cash disbursements by processing account statements from sponsor banks in the MT940 format. Each disbursement is tracked using a unique Disbursement ID, and PBMS generates atomic payment instructions corresponding to each ID. Depending on configuration, these instructions can be grouped into single or multiple payloads. The reconciliation process is carried out in the G2P Bridge component of the OpenG2P platform, ensuring that every disbursement is matched and validated against actual banking transactions.
