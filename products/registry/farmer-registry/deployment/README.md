---
description: Deploying the Farmer Registry on Kubernetes using its Helm chart.
---

# Deployment

The Farmer Registry is deployed on Kubernetes from its own **self-sufficient** Helm chart, [`openg2p-farmer-registry`](https://github.com/OpenG2P/farmer-registry/tree/develop/helm/openg2p-farmer-registry) — there is no base registry chart to install first. See the [deployment architecture](../../../../deployment/openg2p-deployment-model.md) for the wider picture.

* [**Helm chart**](helm-chart.md) — components, dependencies, parameters, CM/PM integration and versions.
* [**Data seeding**](data-seeding.md) — seed sources, the db-seed image and the flags that drive it.

## Deployment steps

1. [Infrastructure setup](../../../../operations/deployment/infrastructure-setup/)
2. [Environment creation](../../../../operations/deployment/environment-setup-multi-node.md)
3. Farmer Registry installation (below)

## Prerequisites

1. Infrastructure and environment created as above.
2. Full admin rights to the cluster and the Rancher UI.
3. **commons-services** deployed in the environment — the Farmer Registry does not bundle Keycloak, master-data, Consent Manager, Partner Management or the Approval Workflow Engine; it points at those shared services. See [Helm chart → Integrating Consent Manager and Partner Management](helm-chart.md#integrating-consent-manager-and-partner-management).

## Installation

Since Rancher is already running after steps 1–2, installing from the Rancher UI is recommended.

### Using Rancher (recommended)

1. Log in to the Rancher console.
2. Select the cluster and namespace (environment).
3. Under **Apps → Repositories**, ensure the repository [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) is added.
4. Under **Apps → Charts**, refresh all repositories.
5. Select the **OpenG2P Farmer Registry** chart.
6. Select the version. *Three-digit versions are frozen; versions carrying a `-develop` suffix are moving.* Rancher hides pre-release versions by default — tick **Show pre-release versions** to see `0.0.0-develop.N`.
7. On Install step 1: select the namespace, give the installation a name (`farmer-registry` is a reasonable default — the name is free, and it scopes the resources so more than one registry can share a namespace), tick **Customize Helm options before install**, then **Next**.
8. Review the values. Typically only **ID Generator** (your ID types) needs changing — the Consent Manager / Partner Management switches are on by default and should stay on.
9. **Install**, and wait for all pods to come up.

### Using Helm CLI

```bash
helm repo add openg2p https://openg2p.github.io/openg2p-helm
helm repo update

helm install farmer-registry openg2p/openg2p-farmer-registry \
  --namespace <namespace> --create-namespace \
  --version <chart-version> \
  -f values-custom.yaml
```

Use `--devel` to resolve a moving `0.0.0-develop.N` version.

## Post-install check

1. The install runs ordered hook Jobs — `db-seed`, the sanity seeds, then the `sanity` suite. Check they completed: `kubectl -n <namespace> get jobs`.
2. Open `farmer-registry.<your-domain>` in a browser. This should present the Keycloak login page.
3. Log in with the credentials provisioned by `keycloak-init` and change the password when prompted.
4. You should land on the Farmer Registry home/dashboard page.
5. Review the sanity Job logs — by default it reports results but never fails the install: `kubectl -n <namespace> logs job/<release>-sanity`.

## Before going to production

* Leave `global.partnerSignatureValidationEnabled` and `global.consentEnforcementEnabled` **on** (the default) — they govern real PII egress, and the chart fails closed. Only disable them for performance testing or a bring-up install without commons-services. See [Helm chart](helm-chart.md#integrating-consent-manager-and-partner-management).
* Turn **off** the sample-data seeding flags (`dbSeed.loadSampleData`, `loadImages`, `loadGeoData`) — see [Data seeding](data-seeding.md).
