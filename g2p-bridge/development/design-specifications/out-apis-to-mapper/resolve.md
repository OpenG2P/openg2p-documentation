---
description: >-
  Triggered by Celery Worker. Worker invoked through Rabbit MQ by
  "create_disbursements" API
---

# resolve

**Business logic**

1. **Payload received** - disbursement\_mapper\_resolution\_batch\_id
2. get a list of disbursement\_id, beneficiary\_id from disbursement\_batch\_control
3. Create a Map of \<beneficiary\_id, disbursement\_id>
4. Create Payload for Mapper - Resolve API - with List of Beneficiary IDs
5. Invoke Mapper - Resolve API, send the list of beneficiary IDs, receive Financial Address
6. Use the Map of \<beneficiary\_id, disbursement\_id> to insert into the table disbursement\_mapper\_resolution\_details
7. Update the table - disbursement\_mapper\_resolution\_batch\_status

<mark style="color:blue;">**SUCCESS (from Mapper Resolution API invoke)**</mark>

**Insert into table disbursement\_mapper\_resolution\_details**

mapper\_resolution\_batch\_id

disbursement\_id

beneficiary\_id

disbursement\_batch\_status.mapper\_resolved\_fa

disbursement\_batch\_status.mapper\_resolved\_phone\_number

disbursement\_batch\_status.mapper\_resolved\_name

**Update table - disbursement\_mapper\_resolution\_batch\_status**

mapper\_resolution\_batch\_id

resolution\_status = PROCESSED

resolution\_time\_stamp

resolution\_error\_code\_latest

resolution\_retries

<mark style="color:blue;">**FAILURE (from mapper resolution API invoke)**</mark>

**Update table - disbursement\_mapper\_resolution\_batch\_status**

mapper\_resolution\_batch\_id

resolution\_status = PENDING

resolution\_time\_stamp = BLANK

resolution\_error\_code\_latest = Error Code as received from API

resolution\_retries = increment by 1

In case of FAILURE from mapper, the worker retries to invoke the mapper for a specified number of retries (environment variable - MAPPER\_NUMBER\_OF\_RETRIES)
