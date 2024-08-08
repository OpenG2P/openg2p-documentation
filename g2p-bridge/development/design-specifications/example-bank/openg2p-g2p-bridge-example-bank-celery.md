---
description: openg2p-g2p-bridge-example-bank-celery
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

# example-bank-celery

This is a celery based microservice. This microservice has the following

1. A celery beat producer - process\_payments\_beat\_producer - that picks up all "PENDING" <mark style="color:blue;">**initiate\_payment\_batch\_requests**</mark> and delegates the batch\_id to a celery worker
2. A celery worker - <mark style="color:blue;">**process\_payments\_worker**</mark> - that receives the batch\_id from the beat producer.&#x20;
   1. It then picks up all the individual payments for that batch\_id and creates book keeping entries for the remitter side (debit leg) for every payment
   2. It updates the <mark style="color:blue;">**account.book\_balance**</mark> and <mark style="color:blue;">**account.available\_balance**</mark> accordingly for each payment
   3. It also randomly produces some reversal entries for every payment transaction
3. A celery worker - <mark style="color:blue;">**account\_statement\_generator**</mark> - that receives <mark style="color:blue;">**account\_statement.id**</mark> from the generate\_statement controller API
   1. It generates an MT940 account statement for that account and persists that statement (as a TEXT) in <mark style="color:blue;">**account\_statement.lob**</mark>

