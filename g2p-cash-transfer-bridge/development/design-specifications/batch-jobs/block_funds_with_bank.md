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

# block\_funds\_with\_bank

### driver condition

<table><thead><tr><th width="235"></th><th></th></tr></thead><tbody><tr><td>frequency</td><td>hourly (specified by configuration yml)</td></tr><tr><td>retries</td><td>yes. subject to a configurable limit specified by configuration yml</td></tr><tr><td>driving table</td><td>disbursement_envelope_batch_status</td></tr><tr><td>eligible envelopes</td><td><p><mark style="color:blue;">disbursement_scchedule_date &#x3C;= today</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">cancellation_status = 'NOT_CANCELLED'</mark><br><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">funds_available_status = 'FUNDS_AVAILABLE'</mark></p><p><mark style="color:red;">AND</mark></p><p>(<br><mark style="color:blue;">( funds_block_status = "PENDING_CHECK"</mark> <mark style="color:purple;">AND</mark> <mark style="color:blue;">funds_block_retries &#x3C; retry_limit)</mark><br><mark style="color:orange;">OR</mark><br><mark style="color:blue;">(funds_block_status = 'FUNDS_BLOCK_FAILURE"</mark> <mark style="color:purple;">AND</mark> <mark style="color:blue;">funds_block_retries &#x3C; retry_limit)</mark><br>) </p></td></tr></tbody></table>

### Business logic

Pick up Eligible - disbursement\_envelope

Pick up Bank Details from table - benefit\_program

Get Bank Connector Instance - from Bank Connector Factory

Invoke - Block Funds API

**If Success and Funds are Blocked, update the following**

1. disbursement\_envelope\_batch\_status.funds\_blocked\_with\_bank = FUNDS\_BLOCK\_SUCCESS
2. disbursement\_envelope\_batch\_status.funds\_blocked\_latest\_timestamp = now()
3. disbursement\_envelope\_batch\_status.funds\_blocked\_latest\_error\_code = null
4. disbursement\_envelope\_batch\_status.funds\_blocked\_retries = +1
5. disbursement\_envelope\_batch\_status.funds\_blocked\_reference\_number = block reference number from bank

**If Success and Funds could not be blocked, update the following**

1. disbursement\_envelope\_batch\_status.funds\_blocked\_with\_bank = FUNDS\_BLOCK\_FAILURE
2. disbursement\_envelope\_batch\_status.funds\_blocked\_latest\_timestamp = now()
3. disbursement\_envelope\_batch\_status.funds\_blocked\_latest\_error\_code = error code from bank
4. disbursement\_envelope\_batch\_status.funds\_blocked\_retries = +1
5. disbursement\_envelope\_batch\_status.funds\_blocked\_reference\_number = blank

**If Failure, update the following**

1. disbursement\_envelope\_batch\_status.funds\_blocked\_with\_bank = FUNDS\_BLOCK\_FAILURE
2. disbursement\_envelope\_batch\_status.funds\_blocked\_latest\_timestamp = now()
3. disbursement\_envelope\_batch\_status.funds\_blocked\_latest\_error\_code = error code from bank
4. disbursement\_envelope\_batch\_status.funds\_blocked\_retries = +1
5. disbursement\_envelope\_batch\_status.funds\_blocked\_reference\_number = blank
