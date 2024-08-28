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

# cancel\_disbursements

| API Attributes |              |
| -------------- | ------------ |
| Direction      | Inward       |
| Invoked by     | PBMS         |
| Mode           | Synchronous  |
| Tables         | disbursement |

Will update disbursement.cancellation\_status to CANCELLED

Will also decrement the following attributes in disbursement\_envelope\_batch\_status

* total\_disbursement\_amount\_received
* number\_of\_disbursements\_received

<mark style="color:blue;">Bulk Update should be used</mark>

<mark style="color:blue;">Transaction control should ALL or NONE - i.e. either all disbursements should be updated or none should be updated.</mark>

### Validations & exceptions

1. Cancellation is only possible before the disbursement\_envelope.disbursement\_schedule\_date
