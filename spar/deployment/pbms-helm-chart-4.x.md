# SPAR Helm Chart 2.x

## Context

The Helm Chart for SPAR installation version 2.x and above are aligned new deployment model where a common layer "[OpenG2P Commons](../../deployment/concepts/openg2p-commons-helm-chart.md)" is installed within an environment that is shared by all the modules within the environment. Learn more about the deployment architecture [here](../../deployment/concepts/openg2p-deployment-model.md).

## Key updates to the chart

The changes made SPAR Helm Chart w.r.t previous versions (1.x and below) are similar to [Registry Helm Chart 3.x.](../../products/registry/registry/social-registry/deployment/registry-helm-chart-3.x.x.md) Important reference and points to note are listed below:

1. **Consolidation of dependents charts** into single SPAR charts. This was done because all the dependent charts are not useful on their own, so Helm chart for each of them was an overkill and adding to the maintance. See

{% @jira/embed url="https://openg2p.atlassian.net/browse/G2P-3635" %}

2. Postgres-init Helm chart added to initialize SPAR DB (`spar_db)`
3. Hard coding removed on several resource names and consequently templating used to resolve the names. Refer to the variables under 'globals' in [values.yaml](https://github.com/OpenG2P/openg2p-pbms-gen2-deployment/blob/4.0/charts/openg2p-pbms/values.yaml). Several variables that are no longer required as globals removed from the globals' list.
4. Separate users and their secrets created for `spar_db`.
5. All database credentials passed via Kubernetes secrets.

## Source code

[SPAR Helm Chart](https://github.com/OpenG2P/openg2p-spar-deployment/tree/2.0/charts/spar)

## Running the Helm Chart

Follow the instructions given [here](../../pbms/previous-generation/deployment/pbms-deployment-instructions.md).
