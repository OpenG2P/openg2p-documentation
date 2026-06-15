---
description: About Postgres Init Helm Chart
---

# Postgres Init Helm Chart

## Context

The [**postgres-init**](https://github.com/openg2p/postgres-init) Helm Chart was created to conveniently create a **database** on an existing PostgreSQL installation. Important to note that the Chart here assumes that PostgreSQL server is already available. The motivation to create this chart were the following:

* In new OpenG2P deployment model, there is only one instance PostgreSQL server for a given sandbox/deployment/namespace. All databases are created within this server. In previous installations of Registry and PBMS, the Odoo chart would create its own instance of PostgreSQL running as a Pod on cluster. Now that we have externalized the databases, we needed a script to create database aprioriy and then install the respective modules.
* Harmonising database creation across all modules such that there is a uniform way of creating datasbases.

## Functionality

Following functionality is supported:

* Creation of one or more databases (DB) on an existing PostgreSQL server
* Creation of one DB user
* Creation of DB user secret with password on Kuberenetes cluster.
* Installation of any database extensions like `pg_trgm`.

The script is idempotent - which means if we run the init again, and if the database, user exist, it won't touch anything and just exit.

For multiple databases the same need to be specified as list item in [values.yaml](https://github.com/OpenG2P/postgres-init/blob/develop/chart/values.yaml).

The database user [secret](https://github.com/OpenG2P/postgres-init/blob/develop/chart/templates/secret.yaml) created by this chart is set to 'keep' mode such that it doesn't get deleted if the Helm is uninstalled. This is important 'cause even if the Helm chart is uninstalled the database still exists, and therefore the secret must also exist. If you would like to tear down entire module clean, refer to the [**tear down**](postgres-init-helm-chart.md#tear-down) instructions below.

## Source code

Code of the script, Docker and Helm chart are available [here](https://github.com/openg2p/postgres-init).

## Run

Instructions here pertain to running the Helm chart on command line.

{% hint style="info" %}
_Note that you generally will not need to run this Helm from command line as it is alreay embedded in the deployment Helm charts of respective modules._
{% endhint %}

* Update / override following params in values.yaml

```
postgresql:
  host: "commons-postgresql"
  port: 5432
  # -- Existing secret with PostgreSQL superuser credentials
  user: postgres
  existingSecret: commons-postgresql
  existingSecretPostgresPasswordKey: "postgres-password"
```

{% hint style="info" %}
In **production** the PostgreSQL server is the **external host instance on the Storage node**, so set `host` to that node's address rather than an in-cluster service name. The `commons-postgresql` secret (created by the environment stage) holds the superuser credentials the init Job uses to create databases and roles.
{% endhint %}

* Add list of databases you wish to create:

```
databases:
  - name: your_db
    user: your_db_user
    # Generated randomly in secrets.yaml. Don't assign it here
    password: ""
    secret: 'your-user-secret'
    secretUserPasswordKey: 'your-user-password-key'
    # List of extensions to install (comma-separated or list). Example
    # - 'pg_trgm'
    extensions: []
```

* You may add extensions as list like:

```
extensions:
  - 'pg_trgm'
```

* Run

```
$ helm -n <your namespace> install postgres-init .
```

* Verify that the database, users, extensions and secrets mentioned in `values.yaml` have been created,

## Tear down

* Uninstall the Helm chart

```
$ helm -n <your namespace> uninstall postgres-init
```

* The above **does not** delete the database, users and secrets. Delete all these manually:
  * database (via psql)
  * db user (via psql)
  * secret on cluster (via kubectl or Rancher)

## Versions

<table><thead><tr><th width="100">Helm Chart Version</th><th width="100">Last modified</th><th>Contents</th></tr></thead><tbody><tr><td><a href="https://github.com/OpenG2P/postgres-init/tree/develop">0.0.0-develop</a></td><td>14-Jun-2026</td><td><p><strong>Development version</strong></p><ul><li>Job is now a Helm pre-install/pre-upgrade hook with <code>helm.sh/hook-delete-policy: before-hook-creation</code>. Fixes the "jobs.batch &#x3C;name> already exists" install failure when a leftover Job from a previous attempt is still in the namespace. See <a href="https://openg2p.atlassian.net/browse/G2P-5127">G2P-5127</a>.</li><li>Added GitHub Actions workflows to build &#x26; push the Docker image and publish the Helm chart.</li><li>Fixed issue with overly long generated Job name.</li></ul></td></tr><tr><td><a href="https://github.com/OpenG2P/postgres-init/tree/v1.1.0">1.1.0</a></td><td>23-Jan-2026</td><td><p><strong>Stable version</strong></p><ul><li>Added feature to optionally install Postgres extensions like pg_trgm .</li><li>Bug related to running as an upgrade fixed (in secrets.yaml)</li></ul></td></tr><tr><td><a href="https://github.com/OpenG2P/postgres-init/tree/v1.0.0">1.0.0</a></td><td>09-Jan-2026</td><td><p><strong>Stable version</strong> with following base features:</p><ul><li>Creation of one or more databases (DB) on an existing Postgres server</li><li>Creation of DB user</li><li>Creation of DB user secret with password</li></ul></td></tr></tbody></table>
