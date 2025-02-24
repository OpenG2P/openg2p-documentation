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

# Background Tasks

You can use the Background Tasks infrastructure to perform - long duration tasks, in an asynchronous paradigm. To initiate a background task, you have to insert a record into the following table

**g2p\_que\_background\_task**

| column                     | usage / description                                                                                                                                                                                                                                                                  |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| id                         | primary key of this table. represents a unique task id for every task that needs to be performed                                                                                                                                                                                     |
| worker\_type               | <p>the asynchronous tasks are performed by celery workers. Every worker_type here is picked up a dedicated Celery Worker. For every business requirement, you have to write a new Celery Worker. <br>A model worker - called - EXAMPLE_WORKER has been provided in the baseline.</p> |
| worker\_payload            | this is the link between the registry odoo application and the worker module. This is the payload that will be used by the celery worker to perform/drive its business logic and then update the odoo-registry database with the result of that work.                                |
| task\_status               | PENDING, COMPLETE, FAILED                                                                                                                                                                                                                                                            |
| queued\_datetime           | date time - when the task was queued/created                                                                                                                                                                                                                                         |
| number\_of\_attempts       | the number of attempts that a worker has performed on this queue item                                                                                                                                                                                                                |
| last\_attempt\_datetime    | the date time stamp - of the latest attempt                                                                                                                                                                                                                                          |
| last\_attempt\_error\_code | error code - if any - for the latest attempt                                                                                                                                                                                                                                         |

The following diagram explains the background process

{% embed url="https://miro.com/app/board/uXjVLEvaZAs=/" %}
