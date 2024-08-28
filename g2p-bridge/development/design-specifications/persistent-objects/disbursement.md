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

| API Attributes |                                                   |
| -------------- | ------------------------------------------------- |
| Direction      | Inward                                            |
| Invoked by     | PBMS                                              |
| Mode           | Synchronous                                       |
| Tables         | <p>disbursement<br>disbursement_batch_control</p> |

A disbursement represents a single disbursement transaction under a disbursement\_envelope. A disbursement\_envelope will contain many hundreds/thousands of disbursements. Each such disbursement will be denoted by a unique disbursement\_id

## Object design

### disbursement

| Attribute                  | Datatype                                                                                                                           |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| disbursement\_envelope\_id | <p>The envelope under which this disbursement is being effected<br>Non Unique Index</p>                                            |
| disbursement\_id           | Unique identifier for each disbursement transaction - **Primary Key**                                                              |
| beneficiary\_id            | The Beneficiary ID to whom this disbursement is being targeted                                                                     |
| beneficiary\_name          | The name of the beneficiary as available in the PBMS / Social Registry records                                                     |
| disbursement\_amount       | The disbursement amount (in the currency specified in the envelope) for this cycle of the program                                  |
| narrative                  | The text that will be available in the Account Statement of the beneficiary's account against this disbursement credit transaction |
| receipt\_time\_stamp       | Time stamp of receipt of disbursement                                                                                              |
| cancellation\_status       | <p>Enum<br>NOT_CANCELLED<br>CANCELLED</p>                                                                                          |
| cancellation\_time\_stamp  | Time stamp of receipt of cancellation request                                                                                      |

### disbursement\_batch\_control

<table><thead><tr><th width="314">Attribute</th><th>Description</th></tr></thead><tbody><tr><td>disbursement_id</td><td>Unique identifier for each disbursement transaction<br><strong>Unique Index</strong></td></tr><tr><td>disbursement_envelope_id</td><td>The envelope under which this disbursement is being effected<br><strong>Non Unique Index</strong></td></tr><tr><td>beneficiary_id</td><td><strong>Non Unique Index</strong></td></tr><tr><td>bank_disbursement_batch_id</td><td>Uniquely represents the shipment bundle into which this disbursement is included.<br>Typically, the payment instruction API into the sponsor bank will be a bulk API, containing many disbursements. Depending on the number of disbursements, there will be many batches into the sponsor bank. This <strong>shipment_to_bank_batch_id</strong> facilitates identification of the exact shipment batch. <br><mark style="color:blue;">The shipment_batch_id is created by the sponsor_bank_dispatch_producer (celery beat producer)</mark><br><strong>Unique Index</strong></td></tr><tr><td>mapper_resolution_batch_id</td><td>Unique batch id - that represents batch control for ID-Mapper resolution<br>Multiple beneficiary ids will be sent to the  mapper resolve API in a single invocation<br>This batch id - represents that batch.<br>All records that are in a single batch_id - will be sent to the mapper resolution in a single API call<br><mark style="color:blue;">The mapper_resolution_batch_id - is created during "create_disbursements" inward API from PBMS. All disbursements received in a single API from PBMS are batched together with a single resolution batch id</mark><br><strong>Unique Index</strong></td></tr></tbody></table>

### bank\_disbursement\_batch\_status

<table><thead><tr><th width="311">Attribute</th><th>Description</th></tr></thead><tbody><tr><td><strong>bank_disbursement_batch_id</strong></td><td>Unique Index</td></tr><tr><td>disbursement_envelope_id</td><td>Non Unique Index</td></tr><tr><td>disbursement_status</td><td>Enum<br>PENDING<br>PROCESSED</td></tr><tr><td>disbursement_timestamp</td><td></td></tr><tr><td><mark style="color:red;">latest_error_code</mark></td><td></td></tr><tr><td><mark style="color:red;">disbursement_attempts</mark></td><td></td></tr></tbody></table>

### mapper\_resolution\_batch\_status

<table><thead><tr><th width="316">Attribute</th><th>Description</th></tr></thead><tbody><tr><td><p></p><p><strong>mapper_resolution_batch_id</strong></p></td><td>Unique Index</td></tr><tr><td>resolution_status</td><td>Enum<br>PENDING<br>PROCESSED</td></tr><tr><td>resolution_timestamp</td><td></td></tr><tr><td><mark style="color:red;">latest_error_code</mark></td><td></td></tr><tr><td><mark style="color:red;">resolution_attempts</mark></td><td></td></tr></tbody></table>

### create\_disbursements - Business Logic

Persist in the following tables

1. disbursements
2. disbursement\_batch\_control
3. bank\_disbursement\_batch\_status&#x20;
4. mapper\_resolution\_batch\_status
5. Every API invocation - will result in 1 record each in disbursement\_batch\_control & bank\_disbursement\_batch\_status & mapper\_resolution\_batch\_status
6. The mapper resolution - itself - is dependent on the disbursement\_envelope.id\_mapper\_resolution\_required attribute (true/false)

<mark style="color:blue;">Bulk Insert should be used to persist the tables - wherever multiple records are applicable</mark>

<mark style="color:blue;">Transaction Control - should be ALL or NONE, i.e. either everything should be inserted or none should be inserted.</mark>

#### Validations & exceptions

1. Ideally, disbursements should arrive before disbursement\_schedule\_date. However, system will not check this condition. System will anyway process an envelope, only when all the disbursements have arrived.
2. disbursement\_amount - valid non zero number
3. the total number of disbursements should not exceed the number specified in the envelope
4. the total\_disbursement\_amount should not exceed the number specified in the envelope
