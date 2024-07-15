---
description: >-
  Triggered by Celery Worker. Worker invoked through Rabbit MQ by
  "create_disbursements" API
---

# resolve

### Object design

### mapper\_resolution\_batch\_status

<table><thead><tr><th width="316">Attribute</th><th>Description</th></tr></thead><tbody><tr><td><p></p><p><strong>mapper_resolution_batch_id</strong></p></td><td>Unique Index</td></tr><tr><td>resolution_status</td><td>Enum<br>WORK_IN_PROGRESS<br>PENDING<br>PROCESSED</td></tr><tr><td>resolution_timestamp</td><td></td></tr><tr><td><mark style="color:red;">latest_error_code</mark></td><td></td></tr><tr><td><mark style="color:red;">resolution_attempts</mark></td><td></td></tr></tbody></table>

### **mapper\_resolution\_details**

<table><thead><tr><th width="316">Attribute</th><th>Description</th></tr></thead><tbody><tr><td>mapper_resolution_batch_id</td><td>Non Unique Index</td></tr><tr><td>disbursement_id</td><td>Unique Index</td></tr><tr><td>beneficiary_id</td><td>Non Unique Index</td></tr><tr><td>mapper_resolved_fa</td><td></td></tr><tr><td>mapper_resolved_phone_number</td><td></td></tr><tr><td>mapper_resolved_email_address</td><td></td></tr><tr><td>mapper_resolved_name</td><td></td></tr></tbody></table>

**Business logic**

1. **Payload received** - disbursement\_mapper\_resolution\_batch\_id
2. get a list of disbursement\_id, beneficiary\_id from disbursement\_batch\_control
3. Create a Map of \<beneficiary\_id, disbursement\_id>
4. Create Payload for Mapper - Resolve API - with List of Beneficiary IDs
5. Invoke Mapper - Resolve API, send the list of beneficiary IDs, receive Financial Address
6.
7. Insert into table - disbursement\_mapper\_resolution\_batch\_status

<mark style="color:blue;">**SUCCESS (from Mapper Resolution API invoke)**</mark>

1. Use the Map of \<beneficiary\_id, disbursement\_id> to insert into the table disbursement\_mapper\_resolution\_details
2. Insert into table - mapper\_resolution\_batch\_status (resolution\_status = PROCESSED, resolution\_attempts+ = 1)

<mark style="color:blue;">**FAILURE (from mapper resolution API invoke)**</mark>

1. Insert into table - mapper\_resolution\_batch\_status (resolution\_status = PENDING, latest\_error\_code, resolution\_attempts+ = 1)

<mark style="color:orange;">**These PENDING records will be picked up the Mapper Resolution Celery Beat Producer**</mark>

**Mapper Resolution Celery Beat Producer**

1. Come up on configured Time Intervals
2. Pick up all "PENDING" records from mapper\_resolution\_batch\_status
3. Dispatch a Task to Resolution Worker Task with Payload = mapper\_resolution\_batch\_id







