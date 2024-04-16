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

# cancel\_disbursement\_envelope

| API Attributes |                        |
| -------------- | ---------------------- |
| Direction      | Inward                 |
| Invoked by     | PBMS                   |
| Mode           | Synchronous            |
| Tables         | disbursement\_envelope |

Using this API, the PBMS can cancel a disbursement\_envelope. With this API, the disbursement\_envelope.cancellation\_status will be set to "CANCELLED".

Once cancelled, no further processing of the envelope will be done.

### Validations & Exceptions

1. Cancellation will be allowed only prior to the "disbursement\_schedule\_date".

