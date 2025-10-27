# Registry Helm Chart 3.x

The guide here can be used to understand why[ Registry Helm chart](https://github.com/OpenG2P/openg2p-social-registry-deployment/tree/3.0/charts/openg2p-social-registry) 3.x has been designed the way it is.  There are also several other pointers to developing Helm chart. The source of the chart is available [here](https://github.com/OpenG2P/openg2p-social-registry-deployment/tree/3.0/charts/openg2p-social-registry).  Refer to packaing concepts.

Several modules that were installed in 2.x have been moved to [openg2p-commons](../../deployment/concepts/openg2p-commons-helm-chart.md).  Only the ones specific to Registry have been retained in this chart.&#x20;

## Context

A package of Registry module is offered as a Helm Chart that contains several other dependencies.

Refer to the packaging hierarchy here:

<figure><img src="../../.gitbook/assets/module-packaging (1).jpg" alt=""><figcaption></figcaption></figure>

At the highest level a package is synonymous to a Helm chart that collates all dependencies for a   "single-click" installation.  This "Module Package Helm Chart" contains several other dependent charts.  Each Helm chart typically contains one Docker (there may be more, but for simplicity let's consider a single Docker per Helm).  A Docker is a package in itself that may contain code from several Git repositories. A single Git repository may house multiple components like Odoo modules, FastAPI modules etc.&#x20;

The depencies are listed in `Chart.yaml` file of the Helm Chart.

## Odoo

### External database

In the current deployment architecture single instance of PostgreSQL is installed per environment (refer to [OpenG2P Commons](https://app.gitbook.com/o/bnTr6Kp4z4CXR4QVIPSa/s/JZcdob2emEcLMvLyIxqT/~/changes/1513/deployment/archiecture-v4.5/openg2p-commons-helm-chart)). This implies that the same PostgreSQL server will house databases from all the modules in that environment, including multiple instances of Registry (if any).  In [values.yaml ](https://github.com/OpenG2P/openg2p-social-registry-deployment/blob/3.0/charts/openg2p-social-registry/values.yaml)default database has been disabled and external database enabled:

`postgresql:`\
`enabled: false`

`externalDatabase:`\
`create: true`

Note that `create: true` is not really creating the DB - this is perhaps a known issue in Odoo Docker.  It expects DB and user name and secret to exist a priori.  Hence, we have created [posgtes-init](registry-helm-chart-3.x.x.md#postgres-init).

For production deployments, the PostgreSQL server is run directly (natively) on the VM. In this case, specifiy Postgres Host in Helm Charts as `host.docker.internal`  which is proxy for `localhost` as from within Docker of Odoo `localhost` will not be recognized.   Or if you are running PostgreSQL on a separate machine, specify the Host domain or IP.

### Modifications to the original Odoo chart

The original Bitnami chart 26.2.9 was modified to suit OpenG2P requirements. While most modifications were about [overriding a few templates](registry-helm-chart-3.x.x.md#overriding-odoo-templates), there were some changes in charts as well. The new version 26.3.0 is created maintained by OpenG2P.  The source code of the chart is available [here](https://github.com/OpenG2P/openg2p-deployment/tree/main/charts/odoo).  The following changes were made:

* **Secrets separated** - original Odoo Helm chart assumed that the same secret resource of Kubernetes contains keys for both -  Postgres admin and database user.  However, we would like to keep them separate as several instances of modules may be initialised and it wouldn't be a good practice to add them to the Postgres secret both from a management and security perspective. &#x20;

```
- name: POSTGRESQL_CLIENT_POSTGRES_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: {{ .Values.externalDatabase.existingPostgresSecret }}
                  key: {{ include "odoo.databaseSecretPostgresPasswordKey" . }}
```

* The above change is in `deployment.yaml` of Odoo chart - a new secret variable called `existingPostgresSecret` has been defined and accordingly some Odoo templates had to be modified (see section below).

### Use of globals

Several global are used in the Registry Helm chart.  Strictly speaking, globals are not required and we must try not to use them. However, here, they offer certain convenience.  To avoid hard coding of the same value of a param appearing in multiple places in the Helm chart, we use globals which are accessible to the sub-charts.  &#x20;

### Overriding Odoo templates

We have used  the function  `tpl` to ensure a value is resolved in `deployment.yaml` of Odoo such that values like .`Release.Name` can be used.  Some of the Odoo templates have been overridden in the Registry chart to enable templating. Refer to [`_helpers.tpl`](https://github.com/OpenG2P/openg2p-social-registry-deployment/blob/3.0/charts/openg2p-social-registry/templates/_helpers.tpl) for details on these overriden templates.

### Bootstrap modules

Modules that are pre-installed in Odoo are specified as a hard-coded list in the Registry Helm chart:

```
 ODOO_BOOTSTRAP_MODULES: >-
      base,
      g2p_app_filter,
      g2p_auth_oidc,
      g2p_auth_oidc_keycloak,
      g2p_registry
```

### Docker

Odoo Docker is packaged using the scripts in [`openg2p-packaging`](https://github.com/OpenG2P/openg2p-packaging/tree/main/packaging) repo.

* WAIT\_FOR\_PROGRESS:  This is passed from `values.yaml` to a  [wait-for-psql.py ](https://github.com/OpenG2P/openg2p-packaging/blob/main/packaging/docker-entrypoint.d/04-wait-for-postgres.sh)script before starting the Odoo Docker. If set to '-1', the script will not wait.&#x20;
* The conf file passed on to Odoo may be found inside the Docker at `/etc/odoo/odoo.conf.` You may 'enter' the Odoo Docker from Rancher - by executing shell for the Odoo Pod.
* Odoo Docker can take up to 8-10 minutes to come up as it creates several tables in the database.

## Postgres-init

In the previous Registry Helm chart (2.x.x) the initialization of DB was part of the Odoo installation where the DB for Odoo was initialized as part of the Postgres installation in Odoo's Helm chart.  For external database, we now have to initialise the DB, create the user and password.  Refer to Docker of postgres-init and its Helm chart [here](https://github.com/OpenG2P/postgres-init).  This is a general purpose Helm chart and can be used across modules. The functionality implemented are limited to the following:

* Creation of a DB in an existing Postgres server
* Creation of DB user
* Creation of DB user secret with password

The script is idempotent - which means if we run the init again, and if the database, user exist, it won't touch anything and just exit.

Postgres-init has ability to **initialise multiple databases.** The datebase has been specified as list item in  [values.yaml](https://github.com/OpenG2P/postgres-init/blob/develop/chart/values.yaml).

The database user [secret](https://github.com/OpenG2P/postgres-init/blob/develop/chart/templates/secret.yaml) created by this chart is set to 'keep' mode such that it doesn't get deleted if the Helm in uninstalled. This is important 'cause even if the Helm chart is uninstalled the database still exists in Postgres, and therefore the secret must also exist. If you would like to tear down entire Registry clean, refer to the [tear down](registry-helm-chart-3.x.x.md#tear-down) instructions below.

### Docker

The postgres-init Docker is published on [Docker Hub](https://hub.docker.com/r/openg2p/postgres-init).

To run the Docker from your machine on the cluster (for development and testing), use the following method:

* Port forward using `kubectl` to connect to Postgres server on the cluster
* Create an env file like this [example](https://github.com/OpenG2P/postgres-init/blob/develop/.env.example).  If Postgres is running directly on your machine and the host is `localhost`, For POSTGRES\_HOST  give the host name as `host.docker.internal`  otherwise from within Docker of Postgres-init  `localhost` won't be recognized.
* Run as given [here](https://github.com/OpenG2P/postgres-init/blob/develop/README.md).

{% hint style="warning" %}
<mark style="color:$warning;">If you would like to update the postgres-init Docker, DO NOT use Mac OS,  work on Linux machine otherwise you will run into architecture mismatch issues.</mark>
{% endhint %}

## ID Generator and mosip-kernel DB init

The ID Generator requires `mosip_kerne`l database to be created. <mark style="color:orange;">This is currently created under Registry, but ideally,</mark> <mark style="color:orange;"></mark><mark style="color:orange;">`mosip_kerne`</mark><mark style="color:orange;">l could be part of</mark> <mark style="color:orange;"></mark><mark style="color:orange;">`openg2p-commons`</mark> <mark style="color:orange;"></mark><mark style="color:orange;">(TBD)</mark>.

## Background tasks

The bg-tasks installed with this Helm require Redis which is also installed with this chart.  We would use one Redis per module instead of installing Redis for every application.&#x20;

Bg-tasks attempts to connect to Redis till Redis is up.  So if you see in the logs ‘unable’ to connect to Redis, it’s fine, as long as ultimately it gets connected.

## Running the Registry chart

The chart is available on Rancher.  Follow the [installation steps](../deployment/registry-installation.md). &#x20;

## Tear down&#x20;

Refer to instructions [here](../deployment/registry-installation.md#tear-down).
