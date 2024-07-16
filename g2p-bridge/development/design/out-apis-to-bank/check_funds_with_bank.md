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

# check\_funds\_with\_bank

## Trigger

* check\_funds\_with\_bank API invoked by bank\_check\_funds\_worker (Celery worker task)
* Worker invoked by
  1. check\_funds\_with\_bank\_beat\_producer (Celery beat producer)

## check\_funds\_with\_bank\_beat\_producer

### Business logic

<table><thead><tr><th width="235"></th><th></th></tr></thead><tbody><tr><td>frequency</td><td>hourly (specified by configuration yml)</td></tr><tr><td>retries</td><td>yes. subject to a configurable limit specified by  configuration yml</td></tr><tr><td><mark style="color:purple;">driving table</mark></td><td><mark style="color:purple;">disbursement_envelope_batch_status</mark></td></tr><tr><td>eligible envelopes</td><td><p><mark style="color:blue;">envelope</mark>.<mark style="color:blue;">disbursement_schedule_date &#x3C; today</mark><br><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">envelope.cancellation_status = 'NOT_CANCELLED'</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">envelope.number_of_disbursements = batch_status.number_of_disbursements_received</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">envelope.total_disbursement_amount = batch_status.total_disbursement_amount_received</mark></p><p><mark style="color:red;">AND</mark></p><p>(<br><mark style="color:blue;">( funds_available_status = "pending_check"</mark> <mark style="color:purple;">AND</mark> <mark style="color:blue;">funds_available_attempts &#x3C; retry_limit)</mark><br><mark style="color:orange;">OR</mark> <br><mark style="color:blue;">( funds_available_status = 'not_available"</mark> <mark style="color:purple;">AND</mark> <mark style="color:blue;">funds_available_attempts &#x3C; retry_limit)</mark><br>) </p></td></tr></tbody></table>

1. Pick up Eligible - disbursement\_envelope
2. Delegate a task to bank\_check\_funds\_worker
3. Payload - disbursement\_envelope\_id

## check\_funds\_with\_bank\_worker

1. Payload - disbursement\_envelope\_id
2. get the details of the disbursement\_envelope - total funds needed for this envelope
3. get details from benefit\_program\_configuration
4. get the instance of BankConnector (implementing BankConnectorInterface) from BankConnectorFactory
5. BankConnectorInterface - There will be a connector (implementation of the BankConnectorInterface) for every Sponsor Bank
6. Invoke - Check Funds API

<mark style="color:blue;">**SUCCESS and FUNDS\_AVAILABLE, update the following**</mark>

1. disbursement\_envelope\_batch\_status.funds\_available\_with\_bank = funds\_available
2. disbursement\_envelope\_batch\_status.funds\_available\_latest\_timestamp = now()
3. disbursement\_envelope\_batch\_status.funds\_available\_latest\_error\_code = null
4. disbursement\_envelope\_batch\_status.funds\_available\_attempts+ = 1

<mark style="color:blue;">**SUCCESS and FUNDS\_UNAVAILABLE, update the following**</mark>

1. disbursement\_envelope\_batch\_status.funds\_available\_with\_bank = funds\_not\_available
2. disbursement\_envelope\_batch\_status.funds\_available\_latest\_timestamp = now()
3. disbursement\_envelope\_batch\_status.funds\_available\_latest\_error\_code = null
4. disbursement\_envelope\_batch\_status.funds\_available\_attempts+ = 1

<mark style="color:blue;">**FAILURE, update the following**</mark>

1. disbursement\_envelope\_batch\_status.funds\_available\_with\_bank = pending\_check
2. disbursement\_envelope\_batch\_status.funds\_available\_latest\_timestamp = now()
3. disbursement\_envelope\_batch\_status.funds\_available\_latest\_error\_code = error\_code
4. disbursement\_envelope\_batch\_status.funds\_available\_attempts+ = 1
