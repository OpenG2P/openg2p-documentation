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

Note that `create: true` is not really creating the DB - this is perhaps a known issue in Odoo Docker.  It expects DB and user name and secret to exist a priori.  Hence, we have created posgtes-init (see below section)

## Postgres Init

&#x20;In the previous Helm chart (2.x.x) the initialization of DB was part of the Odoo installation where the DB for Odoo was initialized as part of the Postgres installation in Odoo's Helm chart.  For external database, we now have to initialise the DB, create the user and password.  Refer to Docker of postgres-init and its Helm chart [here](https://github.com/OpenG2P/postgres-init).  This is a general purpose Helm chart and can be used across modules. The functionality implemented are limited to the following:

* Creation of a DB in an existing Postgres server
* Creation of DB user
* Creation of DB user secret with password

The script is idempotent - which means if we run the init again, and if the database, user exist, it won't touch anything and just exit.

### Docker

The postgres-init Docker is published on [Docker Hub](https://hub.docker.com/r/openg2p/postgres-init).

To run the Docker from your machine on the cluster (for development and testing), use the following method:

* Port forward using `kubectl` to connect to Postgres server on the cluster
* Create an env file like this [example](https://github.com/OpenG2P/postgres-init/blob/develop/.env.example). For POSTGRES\_HOST  give the host name as `host.docker.internal`  otherwise from within Docker `localhost` won't be recognized.
* Run as given [here](https://github.com/OpenG2P/postgres-init/blob/develop/README.md).

{% hint style="warning" %}
If you would like to update the postgres-init Docker, DO NOT use Mac OS,  work on Linux machine otherwise you will run into architecture mismatch issues.
{% endhint %}

## Odoo

### Modifications to original Odoo chart

* Original Odoo chart as certain assumptions a
* New version 26.3.0 created maintained by OpenG2P
* Secrets separated - original Odoo Helm chart assumed that the same secret resource of Kubernetes contains keys for both -  Postgres admin and database user.  However, we would like to keep them separate as several instances of modules may be initialised and it wouldn't be good practices to add them to the Postgres secret both from a management and security perspective. &#x20;

```
- name: POSTGRESQL_CLIENT_POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: {{ .Values.externalDatabase.existingPostgresSecret }}
                  key: {{ include "odoo.databaseSecretPostgresPasswordKey" . }}
```

* The above change is in `deployment.yaml` - a new secret variable called `existingPostgresSecret` has been defined.
* Since we want variable names for registry, users, etc that are based on release names rather than hard-coded names, the deployment.yaml of Odoo had to be modified to use `'tpl'` function rather than directly rendering the values. The `tpl` enables use to pass on a value like  '.Release.Name' which will get resolved in `deployment.yaml` of Odoo chart.

### Use of globals

Several global are used in the Registry Helm chart.  Strictly speaking, globals are not required and we must try not to use them.  However, here, they offer certain convenience.  To avoid hard coding of the same value of a param appearing in multiple places in the Helm chart, we use globals which are accessible to the sub-charts.  &#x20;

### Overriding Odoo templates

* Use of `tpl` to ensure a value is resolved in `deployment.yaml` of Odoo.

### Secrets

* "keep" method
*

## &#x20;values.yaml

* WAIT\_FOR\_PROGRESS
*



## Tear down

* Secret for user does not get deleted (and rightly so)
* If you re-run the helm while database still exists, it just brings up Odoo without any issues - it does not re-initalize the database.
*



&#x20;



