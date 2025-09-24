---
description: Modified deployment architecture more in tune with production deployment
---

# Archiecture V4.5

In the (previous) [V4 deployment architecture](./#v4-deployment-architecture), we install all associated dependencies (like PostgreSQL, MinIO, OpenSearch, Kafka, Keymanager, etc. ) for a module as a single self-contained package, thus enabling a single click deployment for Registry, PBMS, G2P Bridge and SPAR and a clean separation of resources along with easier naming conventions, etc.  This is good to deploy a sandbox; however, in production, we seldom find more than one instance of the Postgres server or MinIO.  Even Kafka being resource-hungry, is preferred to have a single instance used by several services.  Therefore, having a set of common resources shared within an **environment** would not only be closer to a production scenario but also save us resources on our deployment as resources would be shared across the modules.  The new **architecture 4.5** offers a common resources layer - installed via "openg2p-commons" Helm Chart, and then each module, like Registry, PBMS etc, will continue to have their Helm packages with dependencies specific to the modules.

The new way of deployment offers a few challenges as databases of several sandboxes and instances of the module reside in the same PostgreSQL server. We must ensure that every database and its users are properly named to avoid any name clashes and allocated sufficient resources to the Postgres server. The tear down of modules also gets complicated as footprints or each module reside in the common components and they need to be removed manually or via scripts.

## Postgres

* Postgres is installed using openg2p-commons
* Originally the chart of Postgres would create database for the module along with an admin user of the database.
* Now the database and user has to be created by each module before installation
* Postgres-init Helm Chart has been created for this purpose
* This chart must be added to the dependency of module Helm and sufficient time must be given for the module to wait until the database is created.  There is `wait_for_psql.py` in Docker of modules like Registry and PBMS. The timeout there needs to be increased to ensure that enough time is given for the postgres-init to run and create the database

### Database initialization

## Work progress

{% embed url="https://openg2p.atlassian.net/browse/G2P-3290" %}
