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
| disbursement\_id           | Unique identifier for each disbursement transaction - **Primary Key**                                                              |
| beneficiary\_id            | The Beneficiary ID to whom this disbursement is being targeted                                                                     |
| beneficiary\_name          | The name of the beneficiary as available in the PBMS / Social Registry records                                                     |
| disbursement\_amount       | The disbursement amount (in the currency specified in the envelope) for this cycle of the program                                  |
| narrative                  | The text that will be available in the Account Statement of the beneficiary's account against this disbursement credit transaction |
| receipt\_time\_stamp       | Time stamp of receipt of disbursement                                                                                              |
| cancellation\_status       | <p>Enum<br>NOT_CANCELLED<br>CANCELLED</p>                                                                                          |
| cancellation\_time\_stamp  | Time stamp of receipt of cancellation request                                                                                      |

### disbursement\_batch\_control

<table><thead><tr><th width="314">Attribute</th><th>Description</th></tr></thead><tbody><tr><td>disbursement_id</td><td>Unique identifier for each disbursement transaction - Primary Key</td></tr><tr><td>disbursement_envelope_id</td><td>The envelope under which this disbursement is being effected</td></tr><tr><td>beneficiary_id</td><td></td></tr><tr><td>shipment_to_bank_batch_id</td><td>Uniquely represents the shipment bundle into which this disbursement is included.<br>Typically, the payment instruction API into the sponsor bank will be a bulk API, containing many disbursements. Depending on the number of disbursements, there will be many batches into the sponsor bank. This <strong>shipment_to_bank_batch_id</strong> facilitates identification of the exact shipment batch. <br><mark style="color:blue;">The shipment_batch_id is created by the sponsor_bank_dispatch_producer (celery beat producer)</mark></td></tr><tr><td>mapper_resolution_batch_id</td><td>Unique batch id - that represents batch control for ID-Mapper resolution<br>Multiple beneficiary ids will be sent to the  mapper resolve API in a single invocation<br>This batch id - represents that batch.<br>All records that are in a single batch_id - will be sent to the mapper resolution in a single API call</td></tr></tbody></table>

### disbursement\_bank\_shipment\_batch\_status

<table><thead><tr><th width="311">Attribute</th><th>Description</th></tr></thead><tbody><tr><td><strong>shipment_to_bank_batch_id</strong></td><td></td></tr><tr><td>shipment_to_bank_status</td><td></td></tr><tr><td>shipment_to_bank_timestamp</td><td></td></tr><tr><td>shipment_to_bank_ack_status</td><td></td></tr><tr><td>shipment_to_bank_ack_timestamp</td><td></td></tr><tr><td>shipment_to_bank_retries</td><td></td></tr></tbody></table>

### disbursement\_mapper\_resolution\_status

| Attribute                        | Description |
| -------------------------------- | ----------- |
| disbursement\_id                 |             |
| beneficiary\_id                  |             |
| mapper\_resolved\_fa             |             |
| mapper\_resolved\_phone\_number  |             |
| mapper\_resolved\_email\_address |             |
| mapper\_resolved\_name           |             |
| mapper\_resolved\_timestamp      |             |



#### Business Logic

Results in persistence of 1 record each in the tables - disbursement and disbursement\_batch\_status.

<mark style="color:blue;">Bulk Insert should be used to persist the disbursements</mark>

<mark style="color:blue;">Transaction Control - should be ALL or NONE, i.e. either everything should be inserted or none should be inserted.</mark>

Once "disbursements" and "disbursement\_batch\_status" - tables are persisted, the List\[Disbursements] payload should be handed off to RabbitMQ (via Celery Producer) to a Celery Worker (Task) - called - "IdMapperResolveTask".

However, this delegation to the "IdMapperResolveTask" is only required - if ID-Account Resolution is required.

This attribute - whether - id & account resolution is required or not - is maintained in a configuration table - "benefit\_program\_configurations". There is a record for every "benefit\_program\_mnemonic" in this table.

This "IdMapperResolveTask" - will resolve the Financial Address (Account Number and Financial Institution details) for all the Beneficiary IDs in the payload and update the disbursement table.&#x20;

#### Validations & Exceptions

1. Ideally, disbursements should arrive before disbursement\_schedule\_date. However, system will not check this condition. System will anyway process an envelope, only when all the disbursements have arrived.
2. disbursement\_amount - valid non zero number
3. the total number of disbursements should not exceed the number specified in the envelope
4. the total\_disbursement\_amount should not exceed the number specified in the envelope

