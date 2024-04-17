---
description: Triggered by Batch job
---

# resolve

driver condition

<table><thead><tr><th width="235"></th><th></th></tr></thead><tbody><tr><td>frequency</td><td>hourly (specified by configuration yml)</td></tr><tr><td>retries</td><td>yes. subject to a configurable limit specified by  configuration yml</td></tr><tr><td>driving table</td><td>disbursement_batch_status</td></tr><tr><td>eligible envelopes</td><td><p><mark style="color:blue;">envelope</mark>.<mark style="color:blue;">disbursement_schedule_date &#x3C; today</mark><br><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">envelope.cancellation_status = 'NOT_CANCELLED'</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">envelope.number_of_disbursements = batch_status.number_of_disbursements_received</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">envelope.total_disbursement_amount = batch_status.total_disbursement_amount_received</mark></p><p><mark style="color:red;">AND</mark><br><mark style="color:blue;">disbursement.cancellation_status = 'NOT_CANCELLED'</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">envelope_batch_status.id_resolution_required = TRUE</mark><br><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">disbursement.mapper_resolution_fa IS NULL</mark></p><p><mark style="color:red;">AND</mark></p><p><mark style="color:blue;">disbursement.mapper_resolution_retries &#x3C; retry_limit</mark></p></td></tr></tbody></table>

