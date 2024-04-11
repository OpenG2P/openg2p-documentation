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

# create\_disbursements

<table><thead><tr><th width="235">attribute</th><th></th></tr></thead><tbody><tr><td>frequency</td><td>hourly (specified by configuration yml)</td></tr><tr><td>retries</td><td>yes. subject to a configurable limit specified by configuration yml</td></tr><tr><td>driving table</td><td>disbursement_envelope_batch_status</td></tr><tr><td>eligible envelopes</td><td><p><mark style="color:blue;">disbursement_schedule_date &#x3C;= today</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">cancellation_status = 'NOT_CANCELLED'</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">number_of_disbursements = number_of_disbursements_received</mark><br><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">funds_blocked_status = 'FUNDS_BLOCK_SUCCESS'</mark></p></td></tr></tbody></table>

Business logic

Pick up eligible disbursement\_envelope

For each eligible\_envelope, pick up disbursements, where shipment\_to\_bank\_status = 'PENDING'

In one batch, maximum number of disbursements is subject to configuration value specified - maximum\_disbursements\_in\_single\_api

get instance of bank connector using bank connector factory

invoke the disburse API and send the disbursement payload
