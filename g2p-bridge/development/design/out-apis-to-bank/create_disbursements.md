---
description: Triggered by Batch job
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

# disburse\_funds\_from\_bank

## Trigger

* disburse\_funds\_from\_bank API invoked by disburse\_funds\_from\_bank\_worker (Celery worker task)
* Worker invoked by
  1. disburse\_funds\_from\_bank\_beat\_producer (Celery beat producer)

## disburse\_funds\_from\_bank\_beat\_producer

### Business logic

<table><thead><tr><th width="235"></th><th></th></tr></thead><tbody><tr><td>frequency</td><td>hourly (specified by configuration yml)</td></tr><tr><td>attempts</td><td>yes. subject to a configurable limit specified by configuration yml</td></tr><tr><td>driving table</td><td>bank_disbursement_batch_status</td></tr><tr><td>eligible envelopes</td><td><p><mark style="color:blue;">disbursement_schedule_date &#x3C;= today</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">cancellation_status = 'NOT_CANCELLED'</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">number_of_disbursements = number_of_disbursements_received</mark><br><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">funds_blocked_status = 'FUNDS_BLOCK_SUCCESS'</mark></p></td></tr></tbody></table>

1. Pick up eligible disbursement\_envelopes
2. For each disbursement\_envelope
   1. Pick up all the bank\_disbursement\_batch\_status records where disbursement\_status = PENDING&#x20;
   2. For each bank\_disbursement\_batch\_status record
      1. Delegate task to disburse\_funds\_from\_bank\_worker
      2. Payload -- bank\_disbursement\_batch\_id

## disburse\_funds\_from\_bank\_worker

1. Payload -- bank\_disbursement\_batch\_id
2. Get the benefit\_program\_configuration (for remitting account details)
3. For this bank\_disbursement\_batch\_id, get the disbursement\_envelope\_id from bank\_disbursement\_batch\_status
4. Get the records - disbursement\_envelope & disbursement\_envelope\_batch\_status
5. For this bank\_disbursement\_batch\_id, create a List\<disbursement\_id> from disbursement\_batch\_control
6. create List\<Disbursement> with select from disbursements for this List\<disbursement\_id>
7. get the instance of BankConnector (implementing BankConnectorInterface) from BankConnectorFactory
8. BankConnectorInterface - There will be a connector (implementation of the BankConnectorInterface) for every Sponsor Bank
9. Invoke - Disburse API

<mark style="color:blue;">**SUCCESS**</mark>

update bank\_disbursement\_batch\_status

1. disbursement\_status = 'PROCESSED'
2. disbursement\_timestamp = now()
3. disbursement\_attempts+ = 1

<mark style="color:blue;">**FAILURE**</mark>

update bank\_disbursement\_batch\_status

1. disbursement\_status = 'PENDING'
2. disbursement\_timestamp = now()
3. latest\_error\_code = as received from sponsor bank API response
4. disbursement\_attempts+ = 1

&#x20;
