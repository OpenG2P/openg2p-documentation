---
description: >-
  Triggered by Celery Worker. Worker invoked through Rabbit MQ by
  "create_disbursements" API
---

# resolve

**Business logic**

1. **Payload received** - LIST\[Disbursements] -- List of Disbursement Objects (Persistent Object Model)
2. Create a Map of \<beneficiary\_id, disbursement\_id>
3. Create Payload for Mapper - Resolve API - with List of Beneficiary IDs
4. Invoke Mapper - Resolve API, send the list of beneficiary IDs, receive Financial Address
5. Use the Map of \<beneficiary\_id, disbursement\_id> to update the table disbursement\_batch\_status
6. The following attributes are updated

<mark style="color:blue;">**SUCCESS**</mark>

disbursement\_batch\_status.mapper\_resolved\_fa

disbursement\_batch\_status.mapper\_resolved\_phone\_number

disbursement\_batch\_status.mapper\_resolved\_name

disbursement\_batch\_status.mapper\_resolved\_timestamp

disbursement\_batch\_status.mapper\_resolved\_retries

<mark style="color:blue;">**FAILURE**</mark>

The following attributes are updated

disbursement\_batch\_status.mapper\_resolved\_retries

In case of FAILURE from mapper, the worker retries to invoke the mapper for a specified number of retries (environment variable - MAPPER\_NUMBER\_OF\_RETRIES)
