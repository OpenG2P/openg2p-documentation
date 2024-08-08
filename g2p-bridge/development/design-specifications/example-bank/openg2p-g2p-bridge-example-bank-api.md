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

# openg2p-g2p-bridge-example-bank-api

This a FastAPI based microservice and provides the following REST APIs

1. check\_funds
2. block\_funds
3. initiate\_payment
4. generate\_account\_statement

The first 3 APIs, viz. check\_funds, block\_funds and initiate\_payment - will be invoked by the g2p-bridge subsystem, through the example\_bank\_connector (BankInterface).
