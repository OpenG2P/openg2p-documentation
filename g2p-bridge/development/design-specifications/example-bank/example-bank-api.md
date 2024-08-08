---
description: openg2p-g2p-bridge-example-bank-api
layout:
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# example-bank-api

This a FastAPI based microservice and provides the following REST APIs

1.  **check\_funds**

    This API checks <mark style="color:blue;">**account.available\_balance**</mark> against the amount provided for the account and returns the status - whether FUNDS\_AVAILABLE or FUNDS\_NOT\_AVAILABLE
2.  **block\_funds**

    This API checks <mark style="color:blue;">**account.available\_balance**</mark> against the amount provided for the account\
    If funds are available, it creates a record in <mark style="color:blue;">**fund\_blocks**</mark> - with a block\_reference\_number

    It also updates the <mark style="color:blue;">**account.blocked\_amount**</mark> and accordingly adjusts <mark style="color:blue;">**account.available\_balance**</mark> (book\_balance - blocked\_amount)

    Returns - block\_reference\_numberi
3.  **initiate\_payment**

    This API accepts a List\<InitiatePaymentRequests>

    All "initiate\_payment\_requests" within a single request - are grouped under a single batch\_id

    Creates a new record (single record) in initiate\_payment\_batch (for the batch\_id)

    Creates new records (one record for every initiate\_payment\_request)

    Returns an acknowledgement - that the request has been received and registered
4.  **generate\_account\_statement**

    This API accepts an Account Number (the funding account for the benefit program)

    It creates a record in <mark style="color:blue;">**account\_statement**</mark> - generates a new ID for this record

    It does not generate the account statement synchronously - but delegates this ID to a celery task

    Returns this ID as response

    The celery worker - picks up this ID and generates an MT940 and persists this MT940 in <mark style="color:blue;">**account\_statement.statement\_lob**</mark>

The first 3 APIs, viz. check\_funds, block\_funds and initiate\_payment - will be invoked by the g2p-bridge subsystem, through the example\_bank\_connector (BankInterface).

The last API - generate\_account\_statement is to be invoked manually - whenever we need to generate the account statement for the benefit\_program account. In a real life scenario, the sponsor bank will generate this MT940 at the end of every business day and dispatch it to the account holder (in our case - the government department that administers the benefit program)
