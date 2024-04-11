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

<table><thead><tr><th width="235"></th><th></th></tr></thead><tbody><tr><td>frequency</td><td>hourly (specified by configuration yml)</td></tr><tr><td>retries</td><td>yes. subject to a configurable limit specified by configuration yml</td></tr><tr><td>driving table</td><td>disbursement_envelope_batch_status</td></tr><tr><td>eligible envelopes</td><td><p><mark style="color:blue;">disbursement_scchedule_date &#x3C;= today</mark><br><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">funds_available_status = 'FUNDS_AVAILABLE'</mark></p><p><mark style="color:red;">AND</mark></p><p>(<br><mark style="color:blue;">( funds_block_status = "pending_check"</mark> <mark style="color:purple;">AND</mark> <mark style="color:blue;">funds_block_retries &#x3C; retry_limit)</mark><br><mark style="color:orange;">OR</mark><br><mark style="color:blue;">(funds_available_status = 'not_available"</mark> <mark style="color:purple;">AND</mark> <mark style="color:blue;">retries &#x3C; retry_limit)</mark><br>) </p></td></tr></tbody></table>

