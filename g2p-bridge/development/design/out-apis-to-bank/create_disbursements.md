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

<table><thead><tr><th width="235"></th><th></th></tr></thead><tbody><tr><td>frequency</td><td>hourly (specified by configuration yml)</td></tr><tr><td>retries</td><td>yes. subject to a configurable limit specified by configuration yml</td></tr><tr><td>driving table</td><td>disbursement_envelope_batch_status</td></tr><tr><td>eligible envelopes</td><td><p><mark style="color:blue;">disbursement_schedule_date &#x3C;= today</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">cancellation_status = 'NOT_CANCELLED'</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">number_of_disbursements = number_of_disbursements_received</mark><br><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">funds_blocked_status = 'FUNDS_BLOCK_SUCCESS'</mark></p></td></tr></tbody></table>

1. Pick up eligible disbursement\_envelopes
2. For each disbursement\_envelope
   1. Pick up disbursement\_batch\_control
   2. Delegate task to disburse\_funds\_from\_bank\_worker
   3. Payload -- shipment\_to\_bank\_batch\_id

Pick up eligible disbursement\_envelopes

For each eligible\_envelope, pick up disbursements, where shipment\_to\_bank\_status = 'PENDING'

In one batch, maximum number of disbursements is subject to configuration value specified - maximum\_disbursements\_in\_single\_api

get instance of bank connector using bank connector factory

invoke the disburse API and send the disbursement payload

on success response, update disbursement\_batch\_status.shipment\_to\_bank\_status = 'PROCESSED'
