---
description: >-
  How the Farmer Registry is packaged as an extension of the Registry Platform,
  and how to deploy it on Kubernetes.
---

# Deployment

{% hint style="info" %}
**New home: GitLab.** **`farmer-registry`** is now developed at [gitlab.com/openg2p/registry/farmer-registry](https://gitlab.com/openg2p/registry/farmer-registry).

Any `github.com` links on this page refer to the **earlier GitHub repository**, which is now read-only. They are kept so that references to previous versions keep working.
{% endhint %}

The Farmer Registry is **not** a registry built from scratch. It is a thin **extension** of the [OpenG2P Registry Platform](../../registry/deployment-and-extension/README.md), which publishes the runnable Docker images and the `openg2p-registry` Helm chart. This repository adds only the farmer domain on top.

{% hint style="info" %}
The packaging model — why the platform publishes the artifacts and a domain registry extends them — is described once, in the platform docs: [**Deployment and Extension**](../../registry/deployment-and-extension/README.md). This section covers only what is farmer-specific.
{% endhint %}

## How the Farmer Registry is packaged

Three layers, each inherited from the platform and narrowed by this repo:

| Layer | Platform provides | Farmer Registry adds |
|---|---|---|
| **Code** | The runtime images (`openg2p-registry-*`) — core, APIs, celery, UI | `farmer-extension` — domain models, schemas, services, seed metadata. Thin `FROM`-image Dockerfiles select it at runtime via `REGISTRY_EXTENSION_MODULE`. |
| **Deployment** | The `openg2p-registry` chart — every template, service, IAM/Keycloak wiring | `openg2p-farmer-registry` — a wrapper chart with **no templates**: a pinned dependency plus a values overlay. See [Helm chart](helm-chart.md). |
| **Tests** | The sanity harness + the extension-independent tests | Only the farmer **field-specific** tests. See [Sanity testing](sanity-testing.md). |

The platform version is **pinned in two places that move together**: `RP_VERSION` in each Dockerfile (the base image tag) and the `openg2p-registry` dependency version in the wrapper chart's `Chart.yaml`. Nothing about the platform is vendored or copied.

* [**Helm chart**](helm-chart.md) — the wrapper chart, what it deploys, and how it is configured.
* [**Data seeding**](data-seeding.md) — the seed content this repo owns and the inherited machinery that applies it.
* [**Sanity testing**](sanity-testing.md) — the two-part test model and what the Farmer Registry contributes.

## Where the artifacts are

| Artifact | Location |
|---|---|
| Source | [`OpenG2P/farmer-registry`](https://github.com/OpenG2P/farmer-registry) |
| Helm chart | [`helm/openg2p-farmer-registry`](https://github.com/OpenG2P/farmer-registry/tree/develop/helm/openg2p-farmer-registry), published to [`openg2p.github.io/openg2p-helm`](https://openg2p.github.io/openg2p-helm) |
| Docker images | Docker Hub, the `openg2p/openg2p-farmer-registry-*` repositories |
| Versions & changelog | [openg2p-packaging/farmer-registry/CHANGELOG](https://openg2p.github.io/openg2p-packaging/farmer-registry/CHANGELOG) — see [Versions](../versions/README.md) |

## Deployment steps

1. [Infrastructure setup](../../../../operations/deployment/infrastructure-setup/)
2. [Environment creation](../../../../operations/deployment/environment-setup-multi-node.md)
3. Farmer Registry installation (below)

## Prerequisites

1. Infrastructure and environment created as above.
2. Full admin rights to the cluster and the Rancher UI.
3. **commons-services** deployed in the environment. The registry bundles none of the shared services — Keycloak, master-data, Consent Manager, Partner Management, the Approval Workflow Engine (AWE) and Audit Manager all come from commons-services and are reached through `global.*` URLs.

{% hint style="warning" %}
The db-seed Job waits for AWE to be healthy before it runs. If AWE is down, db-seed blocks, Helm's install timeout expires, and the release is marked failed **before the sanity Job is ever created**. Confirm commons-services is healthy first.
{% endhint %}

## Installation

### Using Rancher (recommended)

1. Log in to the Rancher console and select the cluster and namespace.
2. Under **Apps → Repositories**, ensure [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) is added.
3. Under **Apps → Charts**, refresh repositories and select **OpenG2P Farmer Registry**.
4. Choose the version. Three-digit versions are frozen; `-develop` versions are moving — tick **Show pre-release versions** to see `0.0.0-develop.N`.
5. Give the installation a name (the release name is free and scopes the resources, so more than one registry can share a namespace), tick **Customize Helm options before install**, then **Next**.
6. Review the values and **Install**.

The configuration form shows the **same questions as the platform chart** — they are inherited from the pinned `openg2p-registry` dependency at packaging time rather than duplicated here, so they never drift. Platform-level settings appear under the `registry` key; `global.*` settings are unchanged.

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

1. The install runs ordered hook Jobs — `db-seed` → the sanity seeds → `iam-register` → `sanity` → and, when analytics is on,
   `bulk-sample` → `reporting-views` → `dashboards`. Check they all completed: `kubectl -n <namespace> get jobs`.
   Helm stops at the first failure, so a job that never appears means an **earlier** one failed — see the
   [install sequence](data-seeding.md#install-sequence) for the full order and what each step does.
2. Open `<release>.<your-domain>` in a browser; you should get the Keycloak login page.
3. Log in with the credentials provisioned by `keycloak-init` and change the password when prompted.
4. Review the sanity Job logs — by default it reports results but never fails the install: `kubectl -n <namespace> logs job/<release>-sanity`.

## Before going to production

* Leave `global.partnerSignatureValidationEnabled` and `global.consentEnforcementEnabled` **on** (the default) — they govern real PII egress and the chart fails closed. See [Helm chart](helm-chart.md#consent-manager-and-partner-management).
* Turn **off** the sample-data loaders (`registry.dbSeed.loadSampleData`, `loadImages`, `loadGeoData`) — see [Data seeding](data-seeding.md).
