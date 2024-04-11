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

# disbursement

disbursement represents a single disbursement transaction under a disbursement\_envelope. A disbursement\_envelope will contain many hundreds/thousands of disbursements. Each such disbursement will be denoted by a unique disbursement\_id

## Object design

| Attribute                  | Datatype                                                                                                                           |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| disbursement\_envelope\_id | <p>The envelope under which this disbursement is being effected<br>Non Unique Index</p>                                            |
| disbursement\_id           | Unique identifier for each disbursement transaction - Primary Key                                                                  |
| beneficiary\_id            | The Beneficiary ID to whom this disbursement is being targeted                                                                     |
| beneficiary\_name          | The name of the beneficiary as available in the PBMS / Social Registry records                                                     |
| narrative                  | The text that will be available in the Account Statement of the beneficiary's account against this disbursement credit transaction |
| receipt\_time\_stamp       | Time stamp of receipt of disbursement                                                                                              |
| cancellation\_status       | <p>Enum<br>NOT_CANCELLED<br>CANCELLED</p>                                                                                          |
| cancellation\_time\_stamp  | Time stamp of receipt of cancellation request                                                                                      |

## APIs on disbursement

### create\_disbursement

| API Attributes |              |
| -------------- | ------------ |
| Direction      | Inward       |
| Invoked by     | PBMS         |
| Mode           | Synchronous  |
| Tables         | disbursement |

#### Business Logic

Results in persistence in disbursement table with following additional attributes

| Attribute                       | Datatype                                                                                                                                                 |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| disbursement\_id                | Unique identifier for each disbursement transaction                                                                                                      |
| disbursement\_envelope\_id      | The envelope under which this disbursement is being effected                                                                                             |
| shipment\_to\_bank\_status      | <p>Enum<br>PENDING<br>PROCESSED</p>                                                                                                                      |
| shipment\_to\_bank\_time\_stamp | Time stamp of shipment to Sponsor bank                                                                                                                   |
| reply\_status\_from\_bank       | <p>Enum<br>SUCCESS<br>FAILURE</p>                                                                                                                        |
| reply\_from\_bank\_time\_stamp  | Time stamp of receipt of reply from Sponsor bank                                                                                                         |
| failure\_error\_code            | Error code from the downstream G2P chain participants (Sponsor bank, Payment switch, Destination banks) in case of a FAILURE (reply\_status\_from\_bank) |
| failure\_error\_message         | Error message describing the failure\_error\_code                                                                                                        |

### cancel\_disbursement

| API Attributes |              |
| -------------- | ------------ |
| Direction      | Inward       |
| Invoked by     | PBMS         |
| Mode           | Synchronous  |
| Tables         | disbursement |

Will update disbursement.cancellation\_status to CANCELLED

Cancellation is possible before the disbursement\_envelope.disbursement\_schedule\_date
