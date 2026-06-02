---
description: The single, consolidated SPAR Helm chart
---

# Helm Chart

The entire SPAR subsystem — and everything it depends on — installs from a
**single Helm chart**, [`spar`](https://github.com/OpenG2P/openg2p-spar/tree/develop/deployment/charts/spar),
in the consolidated `openg2p-spar` repository. There are no longer separate charts
per service; one `helm install` brings up the complete, working subsystem.

{% hint style="info" %}
This page describes the chart itself. For the end-to-end install flow
(Infrastructure → Environment → SPAR), follow the [Deployment](README.md) guide —
it assumes the Kubernetes infrastructure and the **commons** environment are
already set up. The commons release provides the shared **PostgreSQL**,
**Keycloak**, **Keymanager** and **Istio** gateway that this chart depends on.
{% endhint %}

## Versions

For the chart version, runtime image tags, last-modified date and change history
(including legacy versions), see the main [Versions](../versions.md) page. The
current moving version is `0.0.0-develop`.

## Key features

* **One chart, complete install.** The Mapper Partner API, the Beneficiary Portal
  API, the PostgreSQL database/role and the Keycloak client are all created by
  this one chart.
* **Uses the shared commons PostgreSQL.** SPAR does **not** install its own
  database server; the `postgres-init` subchart creates the SPAR database and
  role inside the namespace's `commons-postgresql`.
* **Keycloak client provisioning** through the `keycloak-init` subchart (creates
  the `openg2p-spar` OIDC client). See [Keycloak Client](keycloak-client.md).
* **Rancher-ready** — ships a `questions.yaml` so all changeable values are
  exposed as a form in the Rancher catalog UI.

## What the chart contains

### Workloads deployed

| Component | Image | Route | Notes |
| --- | --- | --- | --- |
| Mapper Partner API | `openg2p/openg2p-spar-mapper-partner-api` | `/api/mapper` | G2P-Connect-compliant ID ↔ Financial Address mapper API consumed by partner systems. |
| Beneficiary Portal API | `openg2p/openg2p-spar-bene-portal-api` | `/api/bene-portal` | REST API backing the OpenG2P Beneficiary Portal (DFSP directory + FA self-update). |

### Dependency subcharts

| Subchart | Purpose | Condition |
| --- | --- | --- |
| `common` | OpenG2P common Helm library (naming, images, istio helpers). | always |
| `postgres-init` | Creates the SPAR database + role inside the shared `commons-postgresql`. | `postgres-init.enabled` |
| `keycloak-init` | Creates the `openg2p-spar` OIDC client and stores its secret. | `keycloak-init.enabled` |

{% hint style="info" %}
**Database naming follows the NSR convention.** The SPAR database and role are
derived from the Helm **release name** (dashes become underscores) — e.g. a
release named `spar` gets the database `spar` and role `spar_user`. SPAR does
**not** create its own PostgreSQL instance; it uses the shared `commons-postgresql`
in the namespace.
{% endhint %}

## Key parameters to change

All changeable values are surfaced in `questions.yaml` (the Rancher form) and
documented in `values.yaml`. The most important ones:

### Hostnames

| Value | Default | Description |
| --- | --- | --- |
| `sparMapperAPI.sparHostname` | `spar.trial.openg2p.org` | Mapper Partner API hostname. |
| `benePortalAPI.benePortalHostname` | `beneficiary.trial.openg2p.org` | Beneficiary Portal API hostname. |

### Keycloak / authentication

| Value | Default | Description |
| --- | --- | --- |
| `keycloak-init.enabled` | `true` | Create the `openg2p-spar` OIDC client + secret. |
| `global.keycloakBaseUrl` | `https://keycloak.<namespace>.openg2p.org` | Keycloak base URL used for the OIDC issuer/token URL. |
| `global.keycloakRealm` | `staff` | Realm in which the client lives / tokens are issued. |
| `global.authClientId` | `openg2p-spar` | OIDC client id (also the name of the K8s secret holding its password). |
| `global.authClientSecretKey` | `client_secret` | Key inside that secret. |

See [Keycloak Client](keycloak-client.md) for why this client is needed.

### Keymanager

| Value | Default | Description |
| --- | --- | --- |
| `global.keymanagerInstallationName` | `commons-services-keymanager` | Internal service name of the shared MOSIP Keymanager, used by the Mapper API for partner signature (JWT) verification. |

### Database

| Value | Default | Description |
| --- | --- | --- |
| `global.postgresqlHost` | `commons-postgresql` | Shared PostgreSQL host the SPAR DB/role are created in. |

The database name, user, secret and password key are derived from the release
name (see the note above) and normally don't need changing.

## How it is run

The recommended path is the **automated, Rancher-driven** flow described in the
[Deployment](README.md) guide (Infrastructure → Environment → install the
"OpenG2P SPAR" chart from the Rancher UI). The form is generated from this
chart's `questions.yaml`, so all changeable values above appear as fields.

The command-line install below is intended for **advanced / developer** use.

### Using the CLI

```bash
# 1. Clone the consolidated repo
git clone https://github.com/OpenG2P/openg2p-spar.git
cd openg2p-spar/deployment/charts/spar

# 2. Build chart dependencies (common, postgres-init, keycloak-init)
helm dependency build

# 3. Install (release name 'spar' -> DB 'spar', role 'spar_user')
helm install spar . -n <namespace>

# Override values with your own file:
helm install spar . -n <namespace> -f my-values.yaml
```

Upgrade after changing values (a values/route-only change needs no pod restart):

```bash
helm upgrade spar . -n <namespace> -f my-values.yaml
```

Check status:

```bash
helm status spar -n <namespace>
kubectl get pods,svc -n <namespace>
```

### Access links

With the default hostnames:

* Mapper Partner API — `https://spar.<namespace>.openg2p.org/api/mapper` (Swagger at `/api/mapper/docs`)
* Beneficiary Portal API — `https://beneficiary.<namespace>.openg2p.org/api/bene-portal` (Swagger at `/api/bene-portal/docs`)

{% hint style="warning" %}
The bare API base path (e.g. `/api/mapper/`) returns a 404 — there is no route
there by design. Use `/docs`, or a specific endpoint.
{% endhint %}

## Teardown

To completely remove a release — including the PostgreSQL database/role that
`helm uninstall` leaves behind — use the bundled uninstall script. See
[Teardown / Uninstall](teardown.md).
