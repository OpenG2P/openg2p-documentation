---
description: The single, consolidated SPAR Helm chart
---

# Helm Chart

The entire SPAR subsystem — and everything it depends on — installs from a
**single Helm chart**, [`openg2p-spar`](https://github.com/OpenG2P/spar/tree/develop/deployment/charts/openg2p-spar),
in the consolidated `spar` repository. There are no longer separate charts
per service; one `helm install` brings up the complete, working subsystem.

{% hint style="info" %}
This page describes the chart itself. For the end-to-end install flow
(Infrastructure → Environment → SPAR), follow the [Deployment](README.md) guide —
it assumes the Kubernetes infrastructure and the **commons** environment are
already set up. The commons release provides the shared **PostgreSQL** and
**Istio** gateway that this chart depends on. (SPAR verifies partner signatures
in-process, so it needs no Keycloak or Keymanager.)
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

### Partner Signatures

SPAR verifies the JWS signature on inbound Mapper Partner API requests. The
mechanism lives in `openg2p-fastapi-common` (see
[PyJWTCryptoHelper](../../platform/platform-services/privacy-and-security/pyjwtcryptohelper.md)).
SPAR **only verifies — it never signs**, so there is no signing key / `.p12`.

| Value | Default | Description |
| --- | --- | --- |
| `global.sparCryptoBackend` | `partner-mgmt` | Verify backend. SPAR fetches partner public keys from the Partner Manager (PM) service — no local key store, no Keymanager. (`local`/`keymanager` are legacy.) |
| `global.partnerManagementApiUrl` | `http://commons-services-pm-partner-api` | PM key-fetch base URL (unauthenticated) SPAR verifies against. |
| `global.sparJwtAuthEnabled` | `true` | Verify a partner JWS signature on every Mapper Partner API request. |
| `global.sparCryptoAllowedAlgorithms` | `RS256` | Allowed JWS algorithms (RS256 only; `none`/HMAC always rejected). |

Partners are onboarded **in Partner Manager**, not in SPAR. For the trial, the G2P
Bridge chart's `pm-seed` Job onboards the Bridge as `PARTNER_G2P_BRIDGE` (plus the
sanity/walkthrough test partners) in PM, so a signed Bridge → SPAR resolve call
verifies out of the box. To trust a real partner, onboard it in PM (see the G2P
Bridge **Onboarding Partners** guide).

### Keymanager (legacy backend only)

Not used by the default `local` backend. Applies only if you switch
`global.sparCryptoBackend` to the legacy `keymanager` backend (SPAR 1.0.0's
mechanism), which also requires `keycloak-init.enabled: true`.

| Value | Default | Description |
| --- | --- | --- |
| `global.keymanagerInstallationName` | `commons-services-keymanager` | Internal service name of the shared MOSIP Keymanager (legacy `keymanager` backend only). |

### Database

| Value | Default | Description |
| --- | --- | --- |
| `global.postgresqlHost` | `commons-postgresql` | Shared PostgreSQL host the SPAR DB/role are created in. |

The database name, user, secret and password key are derived from the release
name (see the note above) and normally don't need changing.

## Seeding reference data

SPAR uses **strategies** to construct and deconstruct Financial Addresses (and
IDs) — see [FA and ID Strategy](../development/tech-guides.md#fa-and-id-strategy)
for the concept (and the important "never delete a strategy" rule). The chart
seeds a default set of strategies into the `strategy`
table so a fresh install is immediately usable.

### Defaults

| `id` | `strategy_type` | Description |
| --- | --- | --- |
| 1 | ID | Keycloak — builds the ID from the `sub` auth claim. |
| 2 | FA | Bank account (bank/branch/account fields). |
| 3 | FA | Email wallet. |
| 4 | FA | Phone / mobile wallet. |

These are defined under `seedData.strategies` in `values.yaml`, each with a pinned
`id` and its `construct_strategy` (format string) and `deconstruct_strategy`
(regex).

### How the seeding works

`seedData.enabled` (default `true`) renders the strategies into a ConfigMap of
SQL, and a Job runs it. The Job:

* is a Helm **`post-install` and `post-upgrade` hook**, so it runs on first install
  **and on every `helm upgrade`** (the Job name carries the release revision, so a
  fresh Job runs each time);
* **waits** for the database to be reachable and for the `strategy` table to exist
  (the table is created by the API `migrate` step), so it is resilient to ordering;
* inserts each row with **`INSERT … ON CONFLICT (id) DO NOTHING`**, which makes the
  seeding **additive and idempotent** — existing rows are never modified or
  deleted, only missing `id`s are inserted.

| Value | Default | Description |
| --- | --- | --- |
| `seedData.enabled` | `true` | Seed the `strategy` table on install/upgrade. |
| `seedData.image` | `jbergknoff/postgresql-client` | Image (with `psql`/`pg_isready`) used by the seed Job. |
| `seedData.strategies` | (4 defaults) | List of strategies to seed; each item has `id`, `description`, `strategy_type`, `construct_strategy`, `deconstruct_strategy`. |

{% hint style="warning" %}
The regex (`deconstruct_strategy`) and format string (`construct_strategy`) must
be **single-quoted** YAML scalars — they contain `\`, `$`, `{` and `:`. (In
single quotes, backslashes are literal and Helm leaves single-brace `{field}`
placeholders untouched.)
{% endhint %}

### Adding a strategy in production

Because strategies are **append-only and never deleted** (existing mappings depend
on their regex to resolve — see the danger note in the
[concept](../development/tech-guides.md#fa-and-id-strategy)),
adding one is a small, safe, two-step change:

1. **Append** a new entry with a **new `id`** to `seedData.strategies` in your values
   (leave all existing entries unchanged):

   ```yaml
   seedData:
     strategies:
       # ... existing id 1-4 unchanged ...
       - id: 5
         description: New Wallet Provider
         strategy_type: FA
         construct_strategy: 'mobile_number:{mobile_number}.wallet_provider_code:{wallet_provider_code}.fa_type:{fa_type}'
         deconstruct_strategy: '^mobile_number:(?P<mobile_number>.*)\.wallet_provider_code:(?P<wallet_provider_code>.*)\.fa_type:(?P<fa_type>.*)$'
   ```

2. Run **`helm upgrade`**. The seed Job re-runs; ids 1–4 are skipped
   (`ON CONFLICT DO NOTHING`) and only id 5 is inserted. Nothing is deleted and the
   API pods are not restarted (their specs are unchanged).

{% hint style="danger" %}
Never reuse or repurpose an existing `id`, and never remove a strategy that has
been used — that would break `resolve` for every FA already stored with it. Always
add a **new** `id`.
{% endhint %}

There is intentionally **no runtime API to create strategies**: they are
security-sensitive (the regex parses financial addresses), change rarely, and must
keep stable ids — so they are managed declaratively via the chart (GitOps), with
the values file as the single source of truth.

## How it is run

The recommended path is the **automated, Rancher-driven** flow described in the
[Deployment](README.md) guide (Infrastructure → Environment → install the
"OpenG2P SPAR" chart from the Rancher UI). The form is generated from this
chart's `questions.yaml`, so all changeable values above appear as fields.

The command-line install below is intended for **advanced / developer** use.

### Using the CLI

```bash
# 1. Clone the consolidated repo
git clone https://github.com/OpenG2P/spar.git
cd spar/deployment/charts/openg2p-spar

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
