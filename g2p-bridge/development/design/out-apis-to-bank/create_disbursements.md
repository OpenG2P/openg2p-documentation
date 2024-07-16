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

