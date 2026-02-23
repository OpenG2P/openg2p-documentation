# Organization of codebase

<div data-full-width="true"><figure><img src="../../../.gitbook/assets/Registry-Code-Organization.jpg" alt=""><figcaption><p>Organization of the Registry codebase in github. The labels in green are the repo names</p></figcaption></figure></div>

The registry codebase is organized into several repositories.

### openg2p-registry-staff-portal-ui

This repository contains the ReactJS UI <mark style="color:blue;">**runtime**</mark> for the Staff Portal functionalities of the Registry. This UI is available as a Docker image with the docker creation scripts in the repo - openg2p-registry-docker. This runtime is accessible from within the openg2p-staff-portal-ui, a common staff-portal for all the staff functionalities relating to PBMS, Registry, Bridge and SPAR.

### **openg2p-registry-apis**

This repository contains the API <mark style="color:blue;">**runtimes**</mark> for the registry. This houses the following runtimes. These 4 runtimes are made available as Docker images. These docker creation scripts are available in the repo - openg2p-registry-docker.

1. <mark style="color:blue;">openg2p-registry-staff-portal-api</mark> — Providing REST APIs for the Registry Staff Portal UI (openg2p-registry-staff-portal-ui)
2. <mark style="color:blue;">openg2p-registry-beneficiary-portal-api</mark> — Provding Registry REST APIs for the Unified Beneficiary Beneficiary Portal UI
3. <mark style="color:blue;">openg2p-registry-agency-portal-api</mark> — Providing Registry REST APIs for the Unified Agency App
4. <mark style="color:blue;">openg2p-registry-partner-api</mark> — Providing Registry REST APIs for the partner ecosystem.

### &#x20;**openg2p-registry-celery**

This repository contains the Celery <mark style="color:$success;">**runtimes**</mark> for the registry. OpenG2P Registry uses the Celery framework to perform several asynchronous tasks on the registry. The celery framework consists of two runtimes

1. <mark style="color:blue;">openg2p-registry-celery-beat-producers</mark> — This runtime provides periodic beats for specific tasks. Almost all of these beat producers are based on Queues (implemented as Postgres Tables) with a specific column (typically xyz\_status = "PENDING") serving as the selection criteria for these beats. <mark style="color:orange;">To avoid multiple beats picking up the same records, it is necessary that we provision exactly ONE instance (POD) of the beat producer.</mark>
2. <mark style="color:blue;">openg2p-registry-celery-workers</mark> — This runtime hosts the workers that receive the tasks emitted by the beat producer. There are multiple workers, each worker processing exactly one business task. The worker typically receives a unique queue\_id from the beat. Each POD is configured to run "NN" workers. <mark style="color:purple;">It is recommended to scale up the worker instances (PODs) to handle higher volumes.</mark>

### openg2p-registry-core

This repository, packaged as a <mark style="color:$success;">**library**</mark>, contains the core registry codebase. It contains the ORM Models, Pydantic schemas and the core business logic of the registry platform. This library need does not require a separate installation. All the runtimes package this as a library within themselves.

openg2p
