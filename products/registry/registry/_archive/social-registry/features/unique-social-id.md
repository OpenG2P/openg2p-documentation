# Unique Social ID

### Description <a href="#description" id="description"></a>

OpenG2P's Social Registry supports the feature of generating randomized unique IDs both individuals and households that may be used to issue a "Social ID", "Family ID", "Famer ID", or any way that uniquely identifies a record in the SR.  This is essential for ensuring accurate and efficient tracking and updating of records.  The need arose to enhance data consistency and integration with other systems within the registry. We use MOSIP's sophisticated ID generator  which applies several rules before assigning an ID to a record.  Learn more about ID generator here:

{% embed url="https://docs.mosip.io/1.2.0/modules/commons/id-generator" %}

### Technical design

* The ID generation is implemented as a [Background Task](../developer-zone/background-tasks.md).
* New Registrants are inserted into a table — `g2p_que_background_task` - with&#x20;
  * `status = PENDING`
  * `worker_type = id_generation_request_worker`
  * `worker_payload = {"registrant_id"="XXX"}`
* The celery beat producer - a cron based beat producer - periodically scans this table for PENDING records and emits queue item (id) one by one
* The celery worker - "ID\_GENERATION\_WORKER" listening on this beat - picks up these queue IDs - Each worker picks up one queue ID at a time
* To scale, the celery worker POD can be spawned into multiple PODs
* The worker requests MOSIP ID Generator for an ID and on receipt of the ID - updates the res\_partner table in the Social Registry Postgre Database - "res\_partner.unique\_id". The worker also updates the g2p\_que\_id\_generation.status to "COMPLETED"
* In turn, the worker inserts another record in g2p\_queue\_background\_task with
  * status = PENDING
  * worker\_type = id\_generation\_update\_worker
  * worker\_payload = {"registrant\_id"="XXX"}
  * This queue item - is picked up the Beat Producer / id\_generation\_update\_worker
  * This worker - calls the MOSIP ID Generator - REST API - to update the status of the ID as "UTILIZED"
* Any failure during this process, the worker updates the g2p\_que\_id\_generation - retry attempts. If the attempts cross a specified threshold, the g2p\_que\_id\_generation - status is updated as FAILED
* Till the g2p\_que\_id\_generation - status is updated to FAILED, the beat producer will regularly pick up that record for retries

### Source Code

[openg2p-registry-bg-tasks](https://github.com/OpenG2P/openg2p-registry-bg-tasks)

[openg2p-registry-bg-tasks-deployment](https://github.com/OpenG2P/openg2p-registry-bg-tasks-deployment)

