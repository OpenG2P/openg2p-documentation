---
description: Provides a Technical Overview of the SPAR Subsystem
---

# Technical Overview

The following picture provides a technical architecture of SPAR

<figure><img src="../../../.gitbook/assets/Gitbook-SPAR-Technical-Architecture.jpg" alt=""><figcaption></figcaption></figure>

The SPAR subsystem consists of the following technology components

* **openg2p-spar-ui-self-service** -- This is a ReactJS based **web-ui layer** that enables a beneficiary to login into the Self Service System of SPAR and view and update his financial address.
* **openg2p-spar-ms-self-service-fastapi** -- This is a FastAPI based python **microservice** that provides REST APIs to the UI layer. This microservice facilitates maintenance of financial address to a beneficiary by providing search APIs for banks, branches and wallet providers, so that a beneficiary can provide his/her complete financial address in the registry. This microservices uses a Postgresql persistence layer.
* **openg2p-spar-ms-mapper-fastapi** -- This is a FastAPI based python **microservice** that serves as the id-mapper registry service. This microservice provides G2P-Connect compliant APIs to update and retrieve financial address information
* **openg2p-spar-lib-mapper-interface** -- This is python **library** that specifies interface APIs to connect to an account-mapper service.
* **openg2p-spar-lib-spar-mapper-connector** -- This is a **library** that provides an OpenG2P implementation of the mapper-interface that connects to the openg2p-spar-ms-mapper-fastapi microservice using REST APIs.
