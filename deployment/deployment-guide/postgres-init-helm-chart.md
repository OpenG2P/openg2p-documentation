---
description: About Postgres Init Helm Chart
---

# Postgres Init Helm Chart

## Context

The **postgres-init** Helm Chart was created to conveniently create a **database** on an existing PostgreSQL installation. Important to note that the Chart here assumes that PostgreSQL server is already available. The motivation to create this chart were the following:

* In new OpenG2P deployment model, there is only instance PostgreSQL server for a given sandbox/deployment/namespace. All databases are created within this server.  In previous installations of Registry and PBMS, the Odoo chart would create its own instance of PostgreSQL running as a Pod on cluster. Now that we have externalized the databases, we needed a script to create database aprioriy and then install the respective modules.&#x20;
* Harmonising database creation across all modules such that there is a uniform way of creating datasbases.

## Functionality&#x20;

* Creation of one or more databases (DB) on an existing Postgres server
* Creation of DB user
* Creation of DB user secret with password

The script is idempotent - which means if we run the init again, and if the database, user exist, it won't touch anything and just exit.

For multiple databases the same need to be specified as list item in  [values.yaml](https://github.com/OpenG2P/postgres-init/blob/develop/chart/values.yaml).

The database user [secret](https://github.com/OpenG2P/postgres-init/blob/develop/chart/templates/secret.yaml) created by this chart is set to 'keep' mode such that it doesn't get deleted if the Helm is uninstalled. This is important 'cause even if the Helm chart is uninstalled the database still exists in Postgres, and therefore the secret must also exist. If you would like to tear down entire module clean, refer to the **tear down** instructions of the respective modules.

## Source code

Code of the script, Docker and Helm chart available [here](https://github.com/openg2p/postgres-init).

## Run

TBD

## Versions

<table><thead><tr><th width="100">Version</th><th width="100">Published Date</th><th>Contents</th></tr></thead><tbody><tr><td>1.0</td><td>09-Jan-2026</td><td><p>Stable version with following base features: </p><ul><li>Creation of one or more databases (DB) on an existing Postgres server</li><li>Creation of DB user</li><li>Creation of DB user secret with password</li></ul></td></tr><tr><td></td><td></td><td></td></tr><tr><td></td><td></td><td></td></tr></tbody></table>
