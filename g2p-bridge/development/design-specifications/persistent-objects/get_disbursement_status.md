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

# get\_disbursement\_status

| API Attributes |                                                       |
| -------------- | ----------------------------------------------------- |
| Direction      | Inward                                                |
| Invoked by     | PBMS                                                  |
| Mode           | Synchronous                                           |
| Tables         | <p>disbursement_recon<br>disbursement_error_recon</p> |

This API accepts a List\[disbursement\_id]

For every disbursement\_id in the request, this API fetches the records from the following tables

1. disbursement\_recon (there can be a max of 1 record for a disbursement\_id)
2. disbursement\_error\_recon (there may be 1 or many records)

The API returns records from these two tables for every disbursement\_id

It returns a **List\[DisbursementStatusPayload]**

**DisbursementStatusPayload**

<mark style="color:blue;">disbursement\_id</mark>

* <mark style="color:blue;">DisbursementRecon - max of 1 record, can be 0 records</mark>
* <mark style="color:blue;">List\[DisbursementErrorRecon] - may be 0, 1 or many records</mark>





