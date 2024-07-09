---
description: >-
  Triggered by Celery Worker. Worker invoked through Rabbit MQ by
  "create_disbursements" API
---

# resolve

Business logic

**Payload received** - LIST\[Disbursements] -- List of Disbursement Objects (Persistent Object Model)

Create a Map of \<beneficiary\_id, disbursement\_id>

Create Payload for Mapper - Resolve API - with List of Beneficiary IDs

Call Mapper - Resolve, receive Financial Address

Use the Map of \<beneficiary\_id, disbursement\_id> to update the table disbursement\_batch\_status&#x20;

The following attributes are updated

disbursement\_batch\_status.mapper\_resolved\_fa

disbursement\_batch\_status.mapper\_resolved\_phone\_number

disbursement\_batch\_status.mapper\_resolved\_name

disbursement\_batch\_status.mapper\_resolved\_timestamp

disbursement\_batch\_status.mapper\_resolved\_retries

<mark style="color:blue;">**FAILURE**</mark>

The following attributes are updated

disbursement\_batch\_status.mapper\_resolved\_retries
