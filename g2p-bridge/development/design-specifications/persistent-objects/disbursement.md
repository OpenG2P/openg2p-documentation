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

| API Attributes |                                                  |
| -------------- | ------------------------------------------------ |
| Direction      | Inward                                           |
| Invoked by     | PBMS                                             |
| Mode           | Synchronous                                      |
| Tables         | <p>disbursement<br>disbursement_batch_status</p> |

A disbursement represents a single disbursement transaction under a disbursement\_envelope. A disbursement\_envelope will contain many hundreds/thousands of disbursements. Each such disbursement will be denoted by a unique disbursement\_id

## Object design

### disbursement

| Attribute                  | Datatype                                                                                                                           |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| disbursement\_envelope\_id | <p>The envelope under which this disbursement is being effected<br>Non Unique Index</p>                                            |
| disbursement\_id           | Unique identifier for each disbursement transaction - Primary Key                                                                  |
| beneficiary\_id            | The Beneficiary ID to whom this disbursement is being targeted                                                                     |
| beneficiary\_name          | The name of the beneficiary as available in the PBMS / Social Registry records                                                     |
| disbursement\_amount       | The disbursement amount (in the currency specified in the envelope) for this cycle of the program                                  |
| narrative                  | The text that will be available in the Account Statement of the beneficiary's account against this disbursement credit transaction |
| receipt\_time\_stamp       | Time stamp of receipt of disbursement                                                                                              |
| cancellation\_status       | <p>Enum<br>NOT_CANCELLED<br>CANCELLED</p>                                                                                          |
| cancellation\_time\_stamp  | Time stamp of receipt of cancellation request                                                                                      |

### disbursement\_batch\_status

| Attribute                       | Datatype                                                                                                                                                 |
| ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| disbursement\_id                | Unique identifier for each disbursement transaction - Primary Key                                                                                        |
| disbursement\_envelope\_id      | The envelope under which this disbursement is being effected                                                                                             |
| shipment\_to\_bank\_status      | <p>Enum<br>PENDING<br>PROCESSED</p>                                                                                                                      |
| shipment\_to\_bank\_time\_stamp | Time stamp of shipment to Sponsor bank                                                                                                                   |
| reply\_status\_from\_bank       | <p>Enum<br>SUCCESS<br>FAILURE</p>                                                                                                                        |
| reply\_from\_bank\_time\_stamp  | Time stamp of receipt of reply from Sponsor bank                                                                                                         |
| reply\_failure\_error\_code     | Error code from the downstream G2P chain participants (Sponsor bank, Payment switch, Destination banks) in case of a FAILURE (reply\_status\_from\_bank) |
| reply\_failure\_error\_message  | Error message describing the failure\_error\_code                                                                                                        |
| reply\_success\_fsp\_code       | If the disbursement is a success, the fsp (the financial service provider / destination bank) code - where the account was credited                      |
| reply\_success\_fa              | The full Financial Address (including account number, branch code / mobile number) where the disbursement was credited                                   |

#### Business Logic

Results in persistence of 1 record each in the tables - disbursement and disbursement\_batch\_status.

<mark style="color:blue;">Bulk Insert should be used to persist the disbursements</mark>

<mark style="color:blue;">Transaction Control - should be ALL or NONE, i.e. either everything should be inserted or none should be inserted.</mark>

#### Validations & Exceptions

1. Ideally, disbursements should arrive before disbursement\_schedule\_date. However, system will not check this condition. System will anyway process an envelope, only when all the disbursements have arrived.
2. disbursement\_amount - valid non zero number
3. the total number of disbursements should not exceed the number specified in the envelope
4. the total\_disbursement\_amount should not exceed the number specified in the envelope

