# PBMS Helm Chart 4.x

## Context

The Helm Chart for PBMS installation version 4.x and above are aligned new deployment model where a common layer "[OpenG2P Commons](../../deployment/openg2p-commons-helm-chart.md)" is installed within an environment that is shared by all the modules within the environment. Learn more about the deployment architecture [here](../../deployment/openg2p-deployment-model.md).

## Key updates to the chart

The changes made PBMS Helm Chart w.r.t previous versions (3.x and below) are similar to [Registry Helm Chart 3.x.](../../products/registry/registry/_archive/social-registry/deployment/registry-helm-chart-3.x.x.md) Important reference and points to note are listed below:

1. **Consolidation of dependents charts** into single PBMS charts. This was done because all the dependent charts are not useful on their own, so Helm chart for each of them was an overkill and adding to the maintance. See

{% @jira/embed url="https://openg2p.atlassian.net/browse/G2P-3614" %}

2. [Postgres-init Helm chart ](../../products/registry/registry/_archive/social-registry/deployment/registry-helm-chart-3.x.x.md#postgres-init)added to initialize PBMS DB and Background Task DB (like in Registry)
3. Hard coding removed on several resource names and consequently templating used to resolve the names. Refer to the variables under 'globals' in [values.yaml](https://github.com/OpenG2P/openg2p-pbms-gen2-deployment/blob/4.0/charts/openg2p-pbms/values.yaml).
4. Odoo Helm Chart version updated. This version was customized by OpenG2P to support overriding of templates. [Learn more>>](../../products/registry/registry/_archive/social-registry/deployment/registry-helm-chart-3.x.x.md#modifications-to-the-original-odoo-chart). The [\_helpers.tpl](https://github.com/OpenG2P/openg2p-pbms-gen2-deployment/blob/4.0/charts/openg2p-pbms/templates/_helper.tpl) template file was updated accordingly.
5. External DB initialized in Odoo. [Learn more>>](../../products/registry/registry/_archive/social-registry/deployment/registry-helm-chart-3.x.x.md#odoo).
6. Utlities like MinIO, Keymanager removed as they are now installed as common shared resources using OpenG2P Commons.
7. Separate users and their secrets created for PBMS DB and Background Task DB.

All PBMS components — Odoo, API, Celery Beat Producers, and Celery Workers — connect to PostgreSQL using these templated credentials via their respective `envVars` sections. This allows consistent configuration and automatic secret injection across sub-charts.

By maintaining separate databases under a shared PostgreSQL service, the Helm chart provides both **operational isolation** (between synchronous and asynchronous workloads) and **deployment simplicity**, while leveraging Kubernetes Secrets for secure credential management.

## Source code

[Helm Chart source code](https://github.com/OpenG2P/openg2p-pbms-gen2-deployment/tree/4.0)

## Running the Helm Chart

Follow the instructions given [here](../../products/pbms/_archive/previous-generation/deployment/pbms-deployment-instructions.md).

## Work items

The various work items, their status and known issues may be seen here:

{% @jira/embed url="https://openg2p.atlassian.net/browse/G2P-3424" %}
