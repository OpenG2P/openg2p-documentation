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

# batch jobs

check\_funds\_with\_sponsor\_bank

<table><thead><tr><th width="235"></th><th></th></tr></thead><tbody><tr><td>frequency</td><td>hourly (specified by configuration yml)</td></tr><tr><td>retries</td><td>yes. subject to a configurable limit specified by configuration yml</td></tr><tr><td>driving table</td><td>disbursement_envelope_batch_status</td></tr><tr><td>eligible envelopes</td><td><p><mark style="color:blue;">disbursement_scchedule_date &#x3C;= today</mark><br><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">disbursement_cancellation_status = 'NOT_CANCELLED'</mark></p><p>(<br><mark style="color:blue;">( funds_available_status = "pending_check" AND retries &#x3C; retry_limit)</mark><br>OR<br><mark style="color:blue;">(funds_available_status = 'not_available" AND retries &#x3C; retry_limit)</mark><br>) </p></td></tr><tr><td></td><td></td></tr></tbody></table>



block\_funds\_with\_sponsor\_bank

create\_disbursements
