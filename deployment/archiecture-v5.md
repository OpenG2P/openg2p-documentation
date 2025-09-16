---
description: Modified deployment architecture more in tune with production deployment
---

# Archiecture V5

In V4 deployment architecture, we were installing all associated dependencies (like PostgreSQL, MinIO, OpenSearch, Kafka, Keymanager, etc. ) for a module as a single self-contained package, thus enabling a single click deployment for Registry, PBMS, G2P Bridge and SPAR and a clean separation of resources along with easier naming conventions, etc.  This is good to deploy a sandbox; however, in production, we find several instances of the Postgres server or MinIO.  Even Kafka being resource-hungry, it is preferred to have a single instance used by several services.  Therefore, having a set of common resources shared within an **environment** would not only be closer to a production scenario but also save us resources on our deployment as resources would be shared across the modules.  Hence, the new architecture offers a common resources layer - installed via "openg2p-commons" Helm Chart, and then each module, like Registry, PBMS etc, will continue to have their Helm packages with dependencies specific to the modules.

The new way of deployment offers a few challenges as databases of several sandboxes and instances of the module will reside in the same PostgreSQL server. We must ensure that every database and its users are properly named to avoid any name clashes.&#x20;

## Postgres

### Database initialization

## Work progress

{% embed url="https://openg2p.atlassian.net/browse/G2P-3267" %}
