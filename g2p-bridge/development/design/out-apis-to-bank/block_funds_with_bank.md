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

# block\_funds\_with\_bank

## Trigger

* block\_funds\_with\_bank API invoked by bank\_block\_funds\_worker (Celery worker task)
* Worker invoked by
  1. block\_funds\_with\_bank\_beat\_producer (Celery beat producer)

## block\_funds\_with\_bank\_beat\_producer

### Business logic

<table><thead><tr><th width="235"></th><th></th></tr></thead><tbody><tr><td>frequency</td><td>hourly (specified by configuration yml)</td></tr><tr><td>attempts</td><td>yes. subject to a configurable limit specified by configuration yml</td></tr><tr><td>driving table</td><td>disbursement_envelope_batch_status</td></tr><tr><td>eligible envelopes</td><td><p><mark style="color:blue;">disbursement_schedule_date &#x3C;= today</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">cancellation_status = 'NOT_CANCELLED'</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">number_of_disbursements = number_of_disbursements_received</mark><br><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">funds_available_status = 'FUNDS_AVAILABLE'</mark></p><p><mark style="color:red;">AND</mark></p><p>(<br><mark style="color:blue;">( funds_block_status = "PENDING_CHECK"</mark> <mark style="color:purple;">AND</mark> <mark style="color:blue;">funds_block_retries &#x3C; retry_limit)</mark><br><mark style="color:orange;">OR</mark><br><mark style="color:blue;">(funds_block_status = 'FUNDS_BLOCK_FAILURE"</mark> <mark style="color:purple;">AND</mark> <mark style="color:blue;">funds_block_retries &#x3C; retry_limit)</mark><br>) </p></td></tr></tbody></table>

1. Pick up Eligible - disbursement\_envelope
2. Delegate a task to bank\_block\_funds\_worker
3. Payload - disbursement\_envelope\_id

## block\_funds\_with\_bank\_worker

1. Payload - disbursement\_envelope\_id
2. get the details of the disbursement\_envelope - total funds needed for this envelope
3. get details from benefit\_program\_configuration
4. get the instance of BankConnector (implementing BankConnectorInterface) from BankConnectorFactory
5. BankConnectorInterface - There will be a connector (implementation of the BankConnectorInterface) for every Sponsor Bank
6. Invoke - Block Funds API

<mark style="color:blue;">**SUCCESS and FUNDS\_BLOCKED, update the following**</mark>

1. disbursement\_envelope\_batch\_status.funds\_blocked\_with\_bank = FUNDS\_BLOCK\_SUCCESS
2. disbursement\_envelope\_batch\_status.funds\_blocked\_latest\_timestamp = now()
3. disbursement\_envelope\_batch\_status.funds\_blocked\_latest\_error\_code = null
4. disbursement\_envelope\_batch\_status.funds\_blocked\_retries = +1
5. disbursement\_envelope\_batch\_status.funds\_blocked\_reference\_number = block reference number from bank

<mark style="color:blue;">**SUCCESS and FUNDS\_NOT\_BLOCKED, update the following**</mark>

1. disbursement\_envelope\_batch\_status.funds\_blocked\_with\_bank = FUNDS\_BLOCK\_FAILURE
2. disbursement\_envelope\_batch\_status.funds\_blocked\_latest\_timestamp = now()
3. disbursement\_envelope\_batch\_status.funds\_blocked\_latest\_error\_code = error code from bank
4. disbursement\_envelope\_batch\_status.funds\_blocked\_retries = +1
5. disbursement\_envelope\_batch\_status.funds\_blocked\_reference\_number = blank

<mark style="color:blue;">**FAILURE**</mark>

1. disbursement\_envelope\_batch\_status.funds\_blocked\_with\_bank = FUNDS\_BLOCK\_FAILURE
2. disbursement\_envelope\_batch\_status.funds\_blocked\_latest\_timestamp = now()
3. disbursement\_envelope\_batch\_status.funds\_blocked\_latest\_error\_code = error code from bank
4. disbursement\_envelope\_batch\_status.funds\_blocked\_retries = +1
5. disbursement\_envelope\_batch\_status.funds\_blocked\_reference\_number = blank
