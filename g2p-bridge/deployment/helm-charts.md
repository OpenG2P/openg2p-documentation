---
description: The single, consolidated G2P Bridge Helm chart
---

# Helm Chart

The entire G2P Bridge subsystem — and everything it depends on — installs from a
**single Helm chart**, [`openg2p-bridge`](https://github.com/OpenG2P/g2p-bridge/tree/develop/deployment/charts/openg2p-bridge),
in the `g2p-bridge` repository. There are no longer separate charts per service
or a separate chart for the Example Bank; one `helm install` brings up the
complete, working subsystem.

{% hint style="info" %}
This page describes the chart itself. For the end-to-end install flow
(Infrastructure → Environment → G2P Bridge), follow the
[Deployment](README.md) guide — it assumes the Kubernetes infrastructure and the
**commons** environment are already set up. The commons release provides the
shared **PostgreSQL**, **Keycloak**, **Keymanager** and **Istio** gateway that
this chart depends on.
{% endhint %}

## Versions

For the chart version, runtime image tags, last-modified date and change history
(including legacy versions), see the main [Versions](../versions.md) page.

## Key features

* **One chart, complete install.** Partner API, Beneficiary-Portal API, Celery
  beat producer and Celery workers, Redis, the PostgreSQL database/role and the
  Keycloak client are all created by this one chart.
* **Bundled Example Bank simulator** (toggle with `exampleBank.enabled`) so the
  end-to-end digital-cash flow can be demonstrated out of the box.
* **Digital cash without PBMS or Registry.** For pure digital cash transfer the
  chart needs neither the PBMS nor the Registry database. The sponsor/treasury
  account is set in Helm values, and the same values seed the Example Bank.
  In-kind disbursements (goods/services) — which do need PBMS/Registry — are
  gated behind a single switch, `global.g2pBridgeInKindEnabled`.
* **Keycloak client provisioning** through the `keycloak-init` subchart (creates
  the `g2p-bridge` OIDC client). See [Keycloak Client](keycloak-client.md).
* **Namespace-derived hostnames.** Set `global.namespace` and every ingress
  hostname is derived from it (e.g. `g2p-bridge.<namespace>.openg2p.org`).
* **Single Celery image** run as either beat producer or worker, selected by the
  chart at runtime.
* **Rancher-ready** — ships a `questions.yaml` so all changeable values are
  exposed as a form in the Rancher catalog UI.

## What the chart contains

### Workloads deployed

| Component | Image | Notes |
| --- | --- | --- |
| Partner API | `openg2p/openg2p-bridge-partner-api` | REST API consumed by upstream systems (e.g. PBMS) to hand over disbursement instructions. |
| Bene-Portal API | `openg2p/openg2p-bridge-bene-portal-api` | REST API for the OpenG2P Beneficiary Portal. |
| Celery Beat Producer | `openg2p/openg2p-bridge-celery` | Single replica. Schedules periodic tasks. |
| Celery Workers | `openg2p/openg2p-bridge-celery` | Same image as beat; scale horizontally for volume. |
| Example Bank API | `openg2p/openg2p-bridge-example-bank-api` | Bundled simulator (only if `exampleBank.enabled`). |
| Example Bank Celery (beat + workers) | `openg2p/openg2p-bridge-example-bank-celery-beat-producers`, `openg2p/openg2p-bridge-example-bank-celery-workers` | Bundled simulator background tasks. |

### Dependency subcharts

| Subchart | Purpose | Condition |
| --- | --- | --- |
| `common` | OpenG2P common Helm library (naming, images, istio helpers). | always |
| `postgres-init` | Creates the Bridge database + role (and the Example Bank DB when enabled) inside the shared `commons-postgresql`. | `postgres-init.enabled` |
| `redis` | Broker/result backend for Celery. | `redis.enabled` |
| `keycloak-init` | Creates the `g2p-bridge` OIDC client and stores its secret. | `keycloak-init.enabled` |

{% hint style="info" %}
**Database naming follows the NSR convention.** The Bridge database and role are
derived from the Helm **release name** (dashes become underscores) — e.g. a
release named `g2p-bridge` gets the database `g2p_bridge` and role
`g2p_bridge_user`. The Bridge does **not** create its own PostgreSQL instance; it
uses the shared `commons-postgresql` in the namespace.
{% endhint %}

## Key parameters to change

All changeable values are surfaced in `questions.yaml` (the Rancher form) and
documented in `values.yaml`. The most important ones:

### General

| Value | Default | Description |
| --- | --- | --- |
| `global.namespace` | `trial` | Environment segment used to derive all ingress hostnames. |
| `global.g2pBridgeHostname` | `g2p-bridge.<namespace>.openg2p.org` | Partner API hostname. |
| `global.benePortalHostname` | `g2p-bridge-bene-portal.<namespace>.openg2p.org` | Beneficiary Portal API hostname. |

### Disbursement mode (digital cash vs in-kind)

| Value | Default | Description |
| --- | --- | --- |
| `global.g2pBridgeInKindEnabled` | `false` | `false` = pure digital cash (no PBMS/Registry needed). `true` enables geo targeting, warehouse & agency allocation and requires the PBMS and Registry databases. |
| `global.sponsorBankConfigurations.default` | (see below) | Sponsor/treasury account used for digital cash. Single source of truth — also used to seed the Example Bank. |
| `global.seedTreasuryAccount` | `true` | Seed the treasury account into the bundled Example Bank (it has no account-creation API). |

The `sponsorBankConfigurations.default` block:

```yaml
global:
  sponsorBankConfigurations:
    default:
      sponsor_bank_code: EXAMPLE
      program_account_number: "SPONSOR0001"
      program_account_branch_code: ""
      account_currency: USD
      available_balance: "10000000"   # opening balance seeded into Example Bank
      account_holder_name: Program Treasury
```

See [Example Bank & Treasury Account](deployment-of-example-bank.md) for how this
single block drives both the Bridge and the Example Bank.

### Example Bank

| Value | Default | Description |
| --- | --- | --- |
| `exampleBank.enabled` | `true` | Deploy the bundled simulator. **Disable for production** (you connect a real sponsor bank instead). |
| `global.exampleBankHostname` | `example-bank.<namespace>.openg2p.org` | Example Bank API hostname. |

### Keycloak / authentication

| Value | Default | Description |
| --- | --- | --- |
| `keycloak-init.enabled` | `true` | Create the `g2p-bridge` OIDC client + secret. |
| `global.keycloakBaseUrl` | `https://keycloak.<namespace>.openg2p.org` | Keycloak base URL. |
| `global.keycloakRealm` | `staff` | Realm in which the client lives. |
| `global.g2pBridgeAuthClientId` | `g2p-bridge` | OIDC client id. |
| `global.g2pBridgeKeymanagerAuthEnabled` | `false` | When `true`, the Bridge authenticates to Keymanager using the client above. Enable in production. |

See [Keycloak Client](keycloak-client.md) for why this client is needed.

### Databases (in-kind only)

`global.PBMSDB*` and `global.registryDB*` point at the PBMS and Registry
databases. They are only consulted when `g2pBridgeInKindEnabled: true`, and the
corresponding questions are hidden in the Rancher form otherwise.

## How it is run

The recommended path is the **automated, Rancher-driven** flow described in the
[Deployment](README.md) guide (Infrastructure → Environment → install the
"OpenG2P Bridge" chart from the Rancher UI). The form is generated from this
chart's `questions.yaml`, so all changeable values above appear as fields.

The command-line install below is intended for **advanced / developer** use.

### Using the CLI

```bash
# 1. Clone the consolidated repo
git clone https://github.com/OpenG2P/g2p-bridge.git
cd g2p-bridge/deployment/charts/openg2p-bridge

# 2. Build chart dependencies (common, postgres-init, redis, keycloak-init)
helm dependency build

# 3. Install (release name 'g2p-bridge' -> DB 'g2p_bridge', role 'g2p_bridge_user')
helm install g2p-bridge . -n <namespace> --set global.namespace=<namespace>

# Override more values with your own file:
helm install g2p-bridge . -n <namespace> -f my-values.yaml
```

Upgrade after changing values (a values/route-only change needs no pod restart):

```bash
helm upgrade g2p-bridge . -n <namespace> -f my-values.yaml
```

Check status:

```bash
helm status g2p-bridge -n <namespace>
kubectl get pods,svc -n <namespace>
```

### Access links

With `global.namespace=trial` and default hostnames:

* Partner API — `https://g2p-bridge.trial.openg2p.org/api/g2p-bridge` (Swagger at `/api/g2p-bridge/docs`, health at `/api/g2p-bridge/ping`)
* Bene-Portal API — `https://g2p-bridge-bene-portal.trial.openg2p.org/api/bene-portal`
* Example Bank API — `https://example-bank.trial.openg2p.org/api/example-bank` (Swagger at `/api/example-bank/docs`)

{% hint style="warning" %}
The bare API base path (e.g. `/api/g2p-bridge/`) returns a 404 — there is no
route there by design. Use `/docs`, `/ping`, or a specific endpoint such as
`/create_disbursement_envelopes`.
{% endhint %}

### Post-install: load the dashboards (optional)

If the environment runs the platform Superset and you want the bridge monitoring
dashboards, enable the read-only analytics role and have an admin import the
bundle:

```yaml
# values.yaml — chart creates the superset_ro role + a <release>-superset-ro Secret
supersetReadOnly:
  enabled: true
```

Then, as a Superset admin:

1. Download `g2p-bridge-dashboards.zip` (GitHub Release asset, or `deployment/superset/`).
2. Read the read-only password:
   `kubectl -n <ns> get secret <release>-superset-ro -o jsonpath='{.data.password}' | base64 -d`
3. Superset → **Settings → Import Dashboards** → upload the ZIP → tick **Overwrite existing** → paste the password (only on the first import).

The five dashboards, re-import behaviour and renamed-release notes are documented
in [Dashboards (Superset)](dashboards.md).

## Teardown

To completely remove a release — including the PostgreSQL database/role that
`helm uninstall` leaves behind — use the bundled uninstall script. See
[Teardown / Uninstall](teardown.md).
