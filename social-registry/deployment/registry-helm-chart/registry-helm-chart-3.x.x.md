---
description: >-
  [Work in Progress] Detailed tips and tricks for understanding Registry's Helm
  chart
---

# Registry Helm Chart - 3.x.x

The guide here can be used to understand why[ Registry Helm chart](https://github.com/OpenG2P/openg2p-social-registry-deployment/tree/3.0/charts/openg2p-social-registry) has been designed the way it is.  There are also several other pointers to developing Helm chart. The source of the chart is available [here](https://github.com/OpenG2P/openg2p-social-registry-deployment/tree/3.0/charts/openg2p-social-registry).

## External database for Odoo

In the [4.5 deployment architecture](../../../deployment/archiecture-v4.5/),  single instance of PostgreSQL is installed per environment (refer to [OpenG2P Commons](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/JZcdob2emEcLMvLyIxqT/~/changes/1513/deployment/archiecture-v4.5/openg2p-commons-helm-chart)).  This implies that the same PostgreSQL server will house databases from all the modules per environment, including multiple instances of Registry (if any).  In [values.yaml ](https://github.com/OpenG2P/openg2p-social-registry-deployment/blob/3.0/charts/openg2p-social-registry/values.yaml)default database has been disabled and external database enabled:

`postgresql:`\
`enabled: false`

`externalDatabase:`\
`create: true`

TBD: What does create: true do?

## Postgres Init

In the [4.5 deployment architecture](../../../deployment/archiecture-v4.5/),  single instance of PostgreSQL is installed per environment (refer to [OpenG2P Commons](../../../deployment/archiecture-v4.5/openg2p-commons-helm-chart.md)).    In the previous Helm chart (2.x.x) the initialization of DB was part of the Odoo installation where the DB for Odoo was initialized as part of the Posgres installation in Odoo's Helm chart.

&#x20;



