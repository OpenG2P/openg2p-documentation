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

# resolve

## Trigger

1. resolve API invoked by mapper\_resolution\_worker (Celery worker task)
2. Worker invoked by mapper\_resolution\_beat\_producer (Celery beat producer)

## **mapper\_resolution\_details**

<table><thead><tr><th width="316">Attribute</th><th>Description</th></tr></thead><tbody><tr><td>mapper_resolution_batch_id</td><td>Non Unique Index</td></tr><tr><td>disbursement_id</td><td>Unique Index</td></tr><tr><td>beneficiary_id</td><td>Non Unique Index</td></tr><tr><td>mapper_resolved_fa</td><td></td></tr><tr><td>mapper_resolved_phone_number</td><td></td></tr><tr><td>mapper_resolved_email_address</td><td></td></tr><tr><td>mapper_resolved_name</td><td></td></tr></tbody></table>

## **mapper\_resolution\_beat\_producer**

1. Come up on configured Time Intervals
2. Pick up all "PENDING" records from mapper\_resolution\_batch\_status
3. Dispatch a Task to Resolution Worker Task with Payload = mapper\_resolution\_batch\_id

## mapper\_resolution\_worker

1. **Payload received** - disbursement\_mapper\_resolution\_batch\_id
2. get a list of disbursement\_id, beneficiary\_id from disbursement\_batch\_control
3. Create a Map of \<beneficiary\_id, disbursement\_id>
4. Create Payload for Mapper - Resolve API - with List of Beneficiary IDs
5. Invoke Mapper - Resolve API, send the list of beneficiary IDs, receive Financial Address

<mark style="color:blue;">**SUCCESS (from mapper resolution API invoke)**</mark>

1. Use the Map of \<beneficiary\_id, disbursement\_id> to insert into the table disbursement\_mapper\_resolution\_details
2. Update table - mapper\_resolution\_batch\_status (resolution\_status = PROCESSED, resolution\_attempts+ = 1)
3. Insert resolution details into mapper\_resolution\_details (use the map of \<beneficiary\_id, disbursement\_id> for this

<mark style="color:blue;">**FAILURE (from mapper resolution API invoke)**</mark>

1. Update table - mapper\_resolution\_batch\_status (resolution\_status = PENDING, latest\_error\_code, resolution\_attempts+ = 1)





