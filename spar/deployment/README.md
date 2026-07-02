---
description: Deploying OpenG2P SPAR on Kubernetes using Helm charts.
---

# Deployment

SPAR is deployed over Kubernetes infrastructure that offers **production-grade** deployment along with powerful security, access control and operational features. Learn more about the deployment architecture [here](../../deployment/openg2p-deployment-model.md).

Deployment is **largely automated**. Once the cluster and environment are in place, the entire SPAR subsystem — the Mapper Partner API, the Beneficiary Portal API, the PostgreSQL database/role and the Keycloak client — installs from a **single Helm chart** (`spar`) via the Rancher UI. No manual database, Keycloak or post-install configuration is required.

## Deployment steps

1. [Infrastructure setup](../../operations/deployment/infrastructure-setup/)
2. [Environment creation](../../operations/deployment/environment-setup-multi-node.md)
3. [SPAR installation](./#spar-installation)

## SPAR installation

After steps 1 and 2, Rancher is up and running, so it is recommended to deploy SPAR from the **Rancher UI**.

### Prerequisites

1. Infrastructure and environment are created as given above. The **commons** environment provides the shared services SPAR depends on — **PostgreSQL** and the **Istio** gateway. SPAR verifies partner signatures **in-process**, so it needs **no Keycloak or Keymanager**.
2. You have full admin rights to the cluster and the Rancher UI.

### Installation

1. Login to the Rancher console.
2. Select the cluster and namespace (environment).
3. Under **Apps → Repositories**, make sure the repository [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) is added.
4. Under **Apps → Charts**, refresh all repositories.
5. To show moving (pre-release) versions, click your user avatar (top-right) → **Preferences** → enable **Include Prerelease Versions**.
6. Select the **"OpenG2P SPAR"** chart.
7. Select the version (_3-digit versions denote frozen releases; versions with a `-develop` tag are moving versions_).
8. On Install Step 1:
   1. select the namespace;
   2. give the installation a name — `spar` recommended (the database and role are derived from this name);
   3. select **Customize Helm options before install**;
   4. Next.
9. On the **Helm Options** page, disable the `wait` flag, then **Install**.
10. Wait for all pods to come up successfully (`Running` / `Completed`).

### Post install check

With the default hostnames shown (namespace `trial`):

1. Open `https://spar.<namespace>.openg2p.org/api/mapper/docs` — the SPAR Mapper Partner API Swagger UI should load.
2. Open `https://beneficiary.<namespace>.openg2p.org/api/bene-portal/docs` — the Beneficiary Portal API Swagger UI should load.

{% hint style="info" %}
The bare API base path (e.g. `/api/mapper/`) returns a 404 by design — there is no route there. Use `/docs`, or a specific endpoint.
{% endhint %}

## Reference

* [Helm Chart](helm-charts.md) — what the chart contains, all parameters, and the command-line install option (for advanced / developer use).
* [Keycloak Client](keycloak-client.md) — why the OIDC client is required and how it is created.
* [Domain Names and Certificates](domain-names-and-certificates.md)
* [Teardown / Uninstall](teardown.md) — completely remove a release.
