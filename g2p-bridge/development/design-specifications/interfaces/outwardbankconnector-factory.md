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

# OutwardBankConnector Factory

This Factory will written a OutwardBankConnector Class Instance

OutwardBankConnector class will implement the OutwardBankInterface

The Factory will return the Connector based on the "benefit\_program.sponsor\_bank\_code"

<mark style="color:blue;">def get\_outward\_bank\_connector (sponsor\_bank\_code : string) -> OutwardBankInterface</mark>
