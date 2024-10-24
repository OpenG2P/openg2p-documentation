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

# Account Mapper Resolution

The upstream Program Management (MIS) systems provide a disbursement list for every disbursement cycle. While many MIS systems currently store beneficiary financial address, the DPI paradigm seeks to abstract this financial address information into a de-coupled purpose built account mapper service. This design ensures that the beneficiary has to ensure his correct financial address (either a bank account or a mobile wallet) only in one single place as opposed to registering his financial address in every Program.

Based on this, the G2P Bridge is designed to receive Beneficiary IDs from the upstream MIS systems. The G2P Bridge&#x20;
