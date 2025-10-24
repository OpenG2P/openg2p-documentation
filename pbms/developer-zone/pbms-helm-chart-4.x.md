# PBMS Helm Chart 4.x

## Context

The Helm Chart for PBMS installation version 4.x and above are aligned new deployment model where a common layer "[OpenG2P Commons](../../deployment/concepts/openg2p-commons-helm-chart.md)" is installed within an environment that is shared by all the modules within the environment.  Learn more about the deployment architecture [here](../../deployment/concepts/openg2p-deployment-model.md).&#x20;

## Key updates to the chart

The changes made PBMS Helm Chart w.r.t previous versions (3.x and below) are similar to [Registry Helm Chart 3.x.](../../social-registry/developer-zone/registry-helm-chart-3.x.x.md)   Important reference and points to note are listed below:

1. [Helm Chart source code](https://github.com/OpenG2P/openg2p-pbms-gen2-deployment/tree/4.0)
2. [Postgres-init Helm chart ](../../social-registry/developer-zone/registry-helm-chart-3.x.x.md#postgres-init)added to initialize PBMS DB and Background Task DB (like in Registry)
3. Hard coding removed on several resource names and consequently templating used to resolve the names.  Refer to the variables under 'globals' in [values.yaml](https://github.com/OpenG2P/openg2p-pbms-gen2-deployment/blob/4.0/charts/openg2p-pbms/values.yaml).
4. Odoo Helm Chart version updated. This version was customized by OpenG2P to support overriding of templates.  [Learn more>>](../../social-registry/developer-zone/registry-helm-chart-3.x.x.md#modifications-to-the-original-odoo-chart).  The [\_helpers.tpl](https://github.com/OpenG2P/openg2p-pbms-gen2-deployment/blob/4.0/charts/openg2p-pbms/templates/_helper.tpl) template file was updated accordingly.
5. External DB initialized in Odoo. [Learn more>>](../../social-registry/developer-zone/registry-helm-chart-3.x.x.md#odoo).
6. Utlities like MinIO, Keymanager removed as they are now installed as common shared resources using OpenG2P Commons.
7. Separate users and their secrets created for PBMS DB and Background Task DB.

## Running the Helm Chart

Follow the instructions given [here](../deployment/pbms-deployment-instructions.md).

## Work items

The various work items, their status and known issues may be seen here:

{% @jira/embed url="https://openg2p.atlassian.net/browse/G2P-3424" %}

