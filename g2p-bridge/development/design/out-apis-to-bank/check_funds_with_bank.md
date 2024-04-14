---
description: Triggered by Batch job
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

# check\_funds\_with\_bank

### driver condition

<table><thead><tr><th width="235"></th><th></th></tr></thead><tbody><tr><td>frequency</td><td>hourly (specified by configuration yml)</td></tr><tr><td>retries</td><td>yes. subject to a configurable limit specified by  configuration yml</td></tr><tr><td>driving table</td><td>disbursement_envelope_batch_status</td></tr><tr><td>eligible envelopes</td><td><p><mark style="color:blue;">disbursement_scchedule_date &#x3C;= today</mark><br><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">disbursement_cancellation_status = 'NOT_CANCELLED'</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">number_of_disbursements = number_of_disbursements_received</mark></p><p><mark style="color:red;">AND</mark></p><p>(<br><mark style="color:blue;">( funds_available_status = "pending_check"</mark> <mark style="color:purple;">AND</mark> <mark style="color:blue;">funds_available_retries &#x3C; retry_limit)</mark><br><mark style="color:orange;">OR</mark> <br><mark style="color:blue;">( funds_available_status = 'not_available"</mark> <mark style="color:purple;">AND</mark> <mark style="color:blue;">funds_available_retries &#x3C; retry_limit)</mark><br>) </p></td></tr></tbody></table>

### Business Logic

Pick up Eligible - disbursement\_envelope

Pick up Bank Details from table - benefit\_program

Get Bank Connector Instance - from Bank Connector Factory

Invoke - Check Funds API

**If Success and Funds are available, update the following**

1. disbursement\_envelope\_batch\_status.funds\_available\_with\_bank = funds\_available
2. disbursement\_envelope\_batch\_status.funds\_available\_latest\_timestamp = now()
3. disbursement\_envelope\_batch\_status.funds\_available\_latest\_error\_code = null
4. disbursement\_envelope\_batch\_status.funds\_available\_retries = +1

**If Success and Funds are Unavailable, update the following**

1. disbursement\_envelope\_batch\_status.funds\_available\_with\_bank = funds\_not\_available
2. disbursement\_envelope\_batch\_status.funds\_available\_latest\_timestamp = now()
3. disbursement\_envelope\_batch\_status.funds\_available\_latest\_error\_code = null
4. disbursement\_envelope\_batch\_status.funds\_available\_retries = +1

**If Failure, update the following**

1. disbursement\_envelope\_batch\_status.funds\_available\_with\_bank = pending\_check
2. disbursement\_envelope\_batch\_status.funds\_available\_latest\_timestamp = now()
3. disbursement\_envelope\_batch\_status.funds\_available\_latest\_error\_code = error\_code
4. disbursement\_envelope\_batch\_status.funds\_available\_retries = +1
