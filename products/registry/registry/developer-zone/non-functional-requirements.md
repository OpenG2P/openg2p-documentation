---
description: Performance & Security - Design & Approach
---

# Non Functional Requirements

### Performance Testing

Registry uses FastAPI based microservice architecture with Postgresql database.

Gen-1 of Registry used Odoo and Postgresql. A high volume performance test with 50 million records (40 million individuals and 10 million households) was performed and various User Action Measurements were recorded. Detailed findings were recorded with recommendations [here](../_archive/social-registry/developer-zone/performance-and-scale-1.md).

Gen2 of Registry has completely moved out of Odoo. Gen2 of Registry is built using FastAPI microservice architecture with React based User Interface for the Staff Portal.

This FastAPI microservice architecture has also been adopted in other OpenG2P products - G2P Bridge and SPAR.

A detailed performance benchmark was conducted on SPAR - and the results of that performance exercise is available [here](../../../../spar/development/testing/performance-testing/).

Learnings from both these independent exercises have been incorporated in the Gen2 Registry Design and Architecture.

A detailed performance testing will be independently conducted on the Registry Platform in the upcoming releases.

The broad approach for this exercise will be on these lines:

* Deploy Registry with a Domain Extension - let's say Farmer Registry
* Load high volume of records in all the Registers and corresponding Tables

#### API POD

* Configure single PODs for Registry Microservices (no scaling) and a single POD of Postgresql - with a fixed resource allocation - such that we can cater to a specified number concurrent users with continuous threads running and achieve near 100% throttle without failure and reasonable response times (95% percentiles and 99% percentiles)
* Increase Scaling and see if Scaling achieves corresponding increase in concurrency. Measure the corresponding increase in DB resource utilization.
* Determine the number of API PODs that we can scale to -- that will achieve 75% resource utilization in the Postgres database
* Do this separately with Read and Write APIs

#### Celery POD

For Asynchronous background jobs, start with a single Worker POD and determine completion time for a given number of tasks. Use 2 or 3 different tasks (deduplication, score computation and id-generation).

Measure the time taken for completion of the tasks with near 100% utilization in the Worker POD.

### Infrastructure Scaling

Registry Gen2 (and all other products from the OpenG2P stable) is deployed on a Kubernetes Cluster based on the design and architecture defined [here](../../../../deployment/openg2p-deployment-model.md).

### Security Testing

The OpenG2P Platform was subjected to a Security Audit by a 3rd party in June 2025. The security Audit certified the OpenG2P platform as A+ (highest rating). The detailed findings and reports of this audit can be found [here](https://www.openg2p.org/post/openg2p-achieves-highest-security-rating)

This audit included the security audit of the applications as well as the deployment architecture.

All the learnings of this audit have been incorporated in the Registry Gen2 design and Architecture.

We plan to repeat the security audit on the OpenG2P Platform as part of the upcoming releases.
