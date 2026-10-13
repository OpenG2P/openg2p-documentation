---
description: >-
  Deploying Agri Stack on a cluster: the order of installs and the
  settings for commons (Master Data with the Ethiopia pack and agriculture
  domain, PM, CM), the Farmer and Crop Sown registries, and the composite;
  the three-namespace exchange setup; uninstalling.
---

# Deploying on a Cluster

Agri Stack is installed into one environment (namespace) from OpenG2P Helm charts, through Rancher. This page lists the order and the settings that matter for Agri Stack; each chart's own documentation covers the rest.

## Order

| # | Install | Chart (Rancher name) | Release name |
| --- | --- | --- | --- |
| 0 | Infrastructure and environment | See [Deployment](../../deployment/README.md) | — |
| 1 | Commons: Keycloak, Postgres, … | `openg2p-commons-base` | `commons` (fixed) |
| 2 | Commons services: **Master Data**, **Partner Management**, **Consent Manager**, AWE, Audit Manager | `openg2p-commons-services` | `commons-services` (fixed) |
| 3 | Farmer Registry | `openg2p-farmer-registry` ("OpenG2P Farmer Registry") | `fr` |
| 4 | Crop Sown Registry | `openg2p-crop-sown-registry` ("OpenG2P Crop Sown Registry") | `csr` |
| 5 | PM and CM entries for the composite and the partners; the composite's signing Secret | — | — |
| 6 | Use-case composite | `openg2p-agri-composite` ("Agri Stack Composite") | e.g. `agri-composite` |
| 7 | Exchange setup and test | [Testing after install](testing-after-install.md) | — |

The composite has no default registry URLs: in step 6, give each registry's full partner API URL, e.g. `https://partner-fr.<dept-domain>/dci/registry/sync/search`. A registry in the same cluster can also be reached as `http://<release>-partner-api.<namespace>.svc.cluster.local/dci/registry/sync/search`.

## Commons services: Master Data, PM, CM

{% hint style="info" %}
Master Data (MDS) serves Agri Stack's **catalogues** (datasets such as lists of crops and seasons, reference entities, geography) for now. Proper catalogues are still to be designed; see [Layer 2: catalogues](../architecture/registry-model.md#layer-2-catalogues).
{% endhint %}

See the [Commons Helm Chart](../../deployment/openg2p-commons-helm-chart.md). In the `openg2p-commons-services` form:

| Group | Setting | Value for Agri Stack |
| --- | --- | --- |
| Country Pack | **Country Pack** (`masterData.geoSeed.countryPack`) | `ETH` (Ethiopia; the commons default) |
| Country Pack | **Dataset Themes** (`masterData.geoSeed.domains`) | `agriculture` (default) — needed by the Farmer Registry and the Crop Sown Registry: they read these lists live from Master Data, and without them their dropdowns are empty and every coded entry is rejected. Leave it as is; a pack without the `agriculture` domain skips it with a warning in the geo-seed Job log |
| Country Pack | **Load Datasets** (`masterData.geoSeed.load.codelists`) | on (default) |
| Country Pack | **Load Sample People** (`masterData.geoSeed.load.samples`) | on (default) — the registries' sample farmers and crop seasons are derived from them |
| Partner Management | **Install Partner Management?** (`partner-management.enabled`) | on |
| Consent Manager | **Install Consent Manager?** (`openg2p-consent-manager.enabled`) | on (default) |
| AWE | **Install AWE?** (`openg2p-awe.enabled`) | on (the registries' change requests use it; CM policy approvals only if switched on in the CM, off by default) |
| Keymanager | **Install Keymanager?** (`keymanager.enabled`) | **off** (the default) — Agri Stack does not use the standalone Keymanager (the registries check partner keys in Partner Management; eSignet, the mock identity system and Inji Certify have their own). Only PBMS needs it on |

The Audit Manager is part of commons-services; the composite sends its events to `http://commons-services-auditmanager:80`.

The ETH pack carries a licence obligation (CC BY-IGO, attribution required); see [Country Data Architecture](../../platform/country-data-architecture.md) and [Master Data Service](../../platform/platform-services/master-data-service/README.md). PM and CM details: [PM deployment](../../platform/platform-services/partner-management/deployment.md), [CM deployment](../../consent-management/deployment/README.md).

## Farmer Registry

Install as in [Farmer Registry → Deployment](../../products/registry/farmer-registry/deployment/README.md), release name `fr`. Settings that matter here (the registry questions are inherited from the platform chart; platform settings sit under `registry.`):

| Setting | Value |
| --- | --- |
| **Verify Partner Signature** (`global.partnerSignatureValidationEnabled`) | on (default) |
| **Enforce Consent** (`global.consentEnforcementEnabled`) | on (default) |
| **Load Sample Data** (`registry.dbSeed.loadSampleData`) | **off by default**; on for a demo (sample farmers from Master Data's sample people, lands numbered `LAND-<n>-<k>`) |

Not in the form, and right by default: the partner key backend (`global.registryCryptoBackend: partner-mgmt`), the Partner Management and Consent Manager URLs (`http://commons-services-pm-partner-api`, `http://commons-services-cm-partner-api`) and the consent data controller (`global.consentDataController`, the registry variant: `farmer-registry`). Change them in the YAML editor only if you know why.

See [Data seeding](../../products/registry/farmer-registry/deployment/data-seeding.md) and [Helm chart](../../products/registry/farmer-registry/deployment/helm-chart.md).

## Crop Sown Registry

The chart `openg2p-crop-sown-registry` is a values overlay over `openg2p-registry` ([source](https://github.com/OpenG2P/crop-sown-registry)); the form shows the platform's questions plus a "Crop Sown Registry" group. Install it the same way as the Farmer Registry, release name `csr`.

| Setting | Value |
| --- | --- |
| Signature and consent settings | As for the Farmer Registry (defaults); the consent data controller is `crop-sown-registry` |
| **Load Sample Data** (`registry.dbSeed.loadSampleData`) | **off by default**; on for a demo: loads the two sample clusters |
| **Load sample crop seasons** (`REGISTRY_CELERY_WORKERS_ACTIVITY_LOAD_SAMPLE_DATA`) | **off by default**; shown only when Load Sample Data is on. Records the sample crop seasons once, after install; needs the sample clusters and Master Data's sample people. Leave off for production. |
| **Pull submissions from ODK Central** (`REGISTRY_CELERY_WORKERS_ACTIVITY_ODK_ENABLED`) | off by default. When on, also activate the form in the register's Settings (ODK project and form ID) and create the ODK credentials Secret. It pulls from the commons ODK Central (`http://commons-services-odk-central-backend`; YAML only) |

* **No datasets (lists) are seeded** in the registry: they are read from Master Data's agriculture domain (set on commons-services, above).
* **No geo setting:** register forms read the country's geo levels from Master Data when they load; seed Jobs read Master Data through its API, never its database.
* **ID generator:** installed, with one pool, `cluster`, for the Cluster register's generated Cluster IDs (`registry.idgenerator.idGenerator.appConfig.idTypes`; nothing to set). Crop seasons have no functional IDs.
* **AWE:** nothing to set. The chart uses the shared AWE in commons-services; db-seed loads the Cluster approval policies and keycloak-init creates the approvers they name (`alex.carter`, `nina.patel`).
* **Sanity:** the platform's smoke tier runs on install; its e2e tier stays off (it seeds a record-register record, which this registry doesn't have). Activity-register checks run against a deployed instance with `scripts/e2e_smoke.py`.

## PM and CM entries, and the signing Secret

Before the composite can serve requests:

1. **Keys.** Generate the composite's key as a `.p12` (and, for testing, a partner key): `python scripts/partner_kit.py keys` writes both to `scripts/kit-out/` and prints the next steps.
2. **PM.** A PM administrator onboards and approves the composite as `PARTNER_AGRI_COMPOSITE` with its public key and `kid`, and each partner as `PARTNER_<ID>` ([partner guide, step 2](partner-guide.md#step-2-get-onboarded-in-partner-management)).
3. **Signing Secret** in the namespace:

   ```bash
   kubectl -n <ns> create secret generic agri-composite-signing \
     --from-file=composite.p12=./composite.p12 --from-literal=password='<p12 password>' \
     --from-literal=kid=agri-composite-2026-01 --from-literal=algorithm=auto
   ```

   `kid` must match the kid registered for the composite in PM (blank → the certificate's SHA-256 thumbprint). `algorithm: auto` takes it from the key type (EC → ES256, Ed25519 → EdDSA, RSA → RS256).
4. **CM.** The CM administrator creates, for each partner, a binding and a policy with each registry ([partner guide, step 3](partner-guide.md#step-3-get-a-binding-and-policy-for-each-registry)): at the exchange CM in exchange mode (the composite's default), at each registry's CM in passthrough mode. In exchange mode each department CM also needs a binding and policy for the composite (audience `agri-composite`) and trust of the exchange CM's receipts ([below](#three-namespace-setup-exchange-and-departments)).

The [exchange setup](exchange-setup.md) does this for the **composite** in one go: its key, its entries in each PM, the signing Secret, and its bindings and policies in each department CM. It does not onboard partners. The [partner test](partner-test.md) does steps 2 and 4 for a test partner.

## Use-case composite

Install **Agri Stack Composite** from the Rancher catalog. Settings ([composite configuration](composite-configuration.md#helm-values)):

* **General:** Composite Hostname (default `agri-composite.<namespace>.openg2p.org`, Istio internal gateway), Image Tag.
* **Integration:** Composite Partner ID (`agri-composite`), Partner Management URL, Audit Manager URL, the Farmer Registry and Crop Sown Registry search URLs (check them against your release names).
* **Agri Stack exchange:** Consent Mode (`exchange` by default; `passthrough` for a single install), Exchange Consent Manager URL (`http://commons-services-cm-partner-api`), its timeout, and Allowed Browser Origins (CORS; default the CM partner portal, `https://consent-partner-portal.<namespace>.openg2p.org`).
* **Console:** on by default: the staff [console](composite-console.md), with its hostname, IAM settings, its database `agri_composite` in the commons Postgres (created by a Job) and links to the PM and CM portals.
* **Signing key:** the Secret name (`agri-composite-signing`).
* **Scaling:** one replica by default; autoscaling (1–5 pods) is off unless switched on; workers per pod.
* **Use cases:** not in the form. Edit `composite.useCases` in **Edit YAML** (e.g. `allowed_partners` of `loan-profile`), or point `composite.existingUseCasesConfigMap` at your own ConfigMap.

The post-install sanity hook pings the API and lists the use cases; a failure fails the release.

## Three-namespace setup: exchange and departments

The [distributed deployment](../design/distributed-deployment-architecture.md#proving-it-three-namespaces) on one cluster: each namespace is installed as a separate organisation, and calls between namespaces use **external hostnames** only. A partner (e.g. `bank-a`) onboards and the farmer consents only at the exchange; each department still decides at its own boundary.

| Namespace | Install | Notes |
| --- | --- | --- |
| `trial` | commons-base, commons-services (default values), Farmer Registry `fr` | As in the sections above; no exchange settings in the registry |
| `dept1` | commons-base, commons-services (default values), Crop Sown Registry `csr` | Same (the crop department) |
| `agrix` | commons-base and commons-services with the **exchange choices** below, the composite (consent mode `exchange`, its default) | No registries |

Each namespace needs its own domain on its `internal` gateway (`*.trial.openg2p.org`, `*.dept1.openg2p.org`, `*.agrix.openg2p.org`), with DNS and TLS.


### What to install in `agrix`

The exchange is installed by hand in Rancher (Apps → Charts), from the unchanged commons charts and the composite chart. Department installs (`trial`, `dept1`) keep the commons defaults; only the exchange uses the choices below.

| Step | What | Release |
| --- | --- | --- |
| 1 | CM signing key Secret | — |
| 2 | **OpenG2P Commons Base** (`openg2p-commons-base`) | `commons` (fixed) |
| 3 | **OpenG2P Commons Services** (`openg2p-commons-services`) | `commons-services` (fixed) |
| 4 | Partner portal realm and users (script) | — |
| 5 | **Agri Stack Composite** (`openg2p-agri-composite`) | e.g. `agri-composite` |
| 6 | Exchange setup (script) | — |
| 7 | Test | — |

Install each one only after the previous one is ready (all pods running, release `deployed`).

#### 1. CM signing key

The exchange Consent Manager signs the consent receipts it gives each registry with your own key, not the chart's demo key. Department CMs trust it through the exchange CM's public JWKS. Create the Secret from your `.p12`:

```bash
kubectl -n agrix create secret generic agrix-cm-signing --from-file=cm_signing.p12=./cm_signing.p12 --from-literal=password='<p12 password>'
```

#### 2. Commons Base

In the form, change only these; leave everything else at its default (PostgreSQL, Keycloak, Redis, Kafka and Garage are all needed):

| Form field | Choose | Why |
| --- | --- | --- |
| Install Novu? | **No** | Notifications: only once the exchange sends farmers notifications or SMS confirmations (consent scenario 2) |
| Install Kafka UI? | **No** | Operations only (optional) |

#### 3. Commons Services

In the form:

| Form field | Choose | Default | Why |
| --- | --- | --- | --- |
| Install Master Data? | **Yes** | Yes | The catalogue. Country Pack `ETH`, Dataset Themes `agriculture`, Load Datasets on; **Load Sample People** on for testing (the mock identity system's identities are these people) |
| Install Partner Management? | **Yes** | Yes | Partners (banks, …) and the composite are onboarded here with their keys |
| Install Consent Manager? | **Yes** | Yes | Farmer consent, and the receipts for each registry |
| Require AWE Approval for Policy Widening? | **No** | No | No AWE in the exchange |
| Install AWE? | **No** | Yes | Only needed if approvals in the CM or Master Data are switched on |
| Install Staff Portal UI? | **No** | Yes | Registry staff home page |
| Install ODK Central? | **No** | Yes | Registry data collection |
| Install Superset? | **No** | Yes | Registry dashboards |
| Install Inji Certify? | **No** | Yes | Credentials for beneficiaries |
| Install eSignet? | **Yes** | Yes | The farmer's national-ID login in the partner portal (mandatory for assisted consent) |
| Install Mock Identity System? | **Yes** for testing | Yes | The identities eSignet checks against; replace with the real ID system (e.g. Fayda) in production |
| Install Artifactory? | **Yes** | Yes | eSignet and the mock identity system need it |
| Install Keymanager? | **No** | No | Not used by Agri Stack |
| Install WebSub? | **No** | Yes | Nothing in the exchange uses it yet |

Then **Edit YAML** and add the settings the form does not show (replace `<…>`):

```yaml
# Needed, not in the form (on by default; listed so they are not turned off)
openg2p-iam-service:
  enabled: true        # permissions for the admin screens
openg2p-audit-manager:
  enabled: true        # records the composite's and the CM's activity
keycloak-init:
  enabled: true        # Keycloak clients and roles of the services
# Not needed, not in the form
openg2p-inji-verify:
  enabled: false
# Consent Manager: exchange role, your signing key, partner portal
openg2p-consent-manager:
  global:
    aweEnabled: false
    consentSigningKid: <kid, e.g. agrix-cm-2026-01>
    agriStackExchange:
      enabled: true
      issuer: agri-stack-exchange-cm
      receiptPresenters: [agri-composite]
      receiptTtlSeconds: 900
      trustedReceiptIssuers: []
  consentManagerApi:
    signingKey:
      mode: existing
      secretName: agrix-cm-signing
      secretKey: cm_signing.p12
      passwordSecretName: agrix-cm-signing
      passwordSecretKey: password
  partnerPortal:
    enabled: true      # off by default
    compositeUrl: https://agri-composite.agrix.openg2p.org
    subjectAuth:
      enabled: true    # the farmer's national-ID login (eSignet); off by default
    requiredSubjectIdentifiers: [FARMER_ID]   # every consent request names the farmer
```

The partner portal is where partner users (e.g. bank staff) create consent requests, have the farmer log in with their national ID (eSignet) and upload the farmer's signed form ([consent collection](../../consent-management/design/consent-collection.md)); the forms are kept in Garage (bucket `consent-evidence`). A Job registers the CM's client in eSignet once eSignet is up ([national ID authentication](../../consent-management/deployment/README.md#national-id-authentication-of-the-subject-esignet)).

#### 4. Partner portal realm and users

The chart creates the `partner` realm and the portal's client; the roles, the `partner_id` attribute, its token mapper and the partner users need Keycloak's admin CLI. From the consent-manager repository:

```bash
./deployment/scripts/setup-partner-realm.sh --namespace agrix --user bank-a-operator:bank-a:PARTNER_OPERATOR
```

The user's password is in Secret `partner-user-bank-a-operator`.

#### 5. Composite

In the form, give the departments' registry search URLs:

| Form field | Value |
| --- | --- |
| Farmer Registry Search URL | `https://partner-fr.trial.openg2p.org/dci/registry/sync/search` |
| Crop Sown Registry Search URL | `https://partner-csr.dept1.openg2p.org/dci/registry/sync/search` |

Keep the defaults for the rest: consent mode `exchange`, the exchange CM URL `http://commons-services-cm-partner-api`, and the partner portal as an allowed browser origin. See [composite configuration](composite-configuration.md#helm-values).

#### 6. Exchange setup

Registers the composite's signing key in the exchange PM and each department PM, and gives the composite a binding and policy in each department CM:

```bash
python scripts/setup_exchange.py -n agrix --registry farmer-registry=trial --registry crop-sown-registry=dept1
```

See [exchange setup](exchange-setup.md).

#### 7. Test

Follow [testing after install](testing-after-install.md).

#### What each namespace holds afterwards

| Where | What |
| --- | --- |
| `agrix` PM | The composite (`PARTNER_AGRI_COMPOSITE`, its key) and each partner (`PARTNER_BANK_A`, …) |
| `agrix` CM | For each partner, a binding and policy **per registry** it reads (`farmer-registry`, `crop-sown-registry`): purposes, data scopes, subject ID types. The bank is onboarded **only here** |
| `trial` PM and `dept1` PM | The composite's public key (`PARTNER_AGRI_COMPOSITE`, same `kid`), so each registry verifies the composite's signature |
| `trial` CM and `dept1` CM | The **standing policy for the exchange**: a binding with audience `agri-composite` for the registry's controller, its allowed purposes, data scopes and subject ID types; and the exchange CM as a **trusted receipt issuer** — issuer `agri-stack-exchange-cm`, JWKS URL `https://consent-manager-partner.agrix.openg2p.org/api/consent-manager-partner/.well-known/jwks.json`, presenter `agri-composite` (CM chart, "Agri Stack exchange" group) |

The registries need no change: each keeps calling its own CM, which now accepts the exchange's receipts. A department's scopes for the exchange cap what any partner gets from it (receipt scopes ∩ standing policy). A denial from a department shows as that source's `denied` status with the registry's reason.

## Uninstalling

| What | Script | Notes |
| --- | --- | --- |
| Composite | [`scripts/uninstall-agri-composite.sh`](https://github.com/openg2p/agri-stack/blob/develop/scripts/uninstall-agri-composite.sh) `--namespace <ns> [--release agri-composite] [--keep-db] [--keep-iam] [--drop-signing-secret] [--force] [--dry-run] [--yes]` | Removes the release, leftover Jobs, ConfigMaps and Secrets labelled with the release; drops the console's database `agri_composite` and its role in `commons-postgresql` (unless `--keep-db`) and deletes the console's IAM rows (unless `--keep-iam`); the signing Secret only with `--drop-signing-secret`. Other options: `--console-db`, `--console-db-user`, `--console-mnemonic`, `--iam-db`, `--postgres-release`, `--postgres-namespace`, `--signing-secret`, `--force` (run while a Helm operation is in progress). Leaves the console's Keycloak client. No PVCs. |
| Crop Sown Registry | [`scripts/uninstall-registry.sh`](https://github.com/OpenG2P/crop-sown-registry/blob/develop/scripts/uninstall-registry.sh) `--namespace <ns> [--release csr] [--keep-iam] [--keep-pvs] [--dry-run] [--yes]` | Also drops the registry's database and role in `commons-postgresql`, its IAM rows, PVCs and their PVs |
| Farmer Registry | [`scripts/uninstall-registry.sh`](https://github.com/OpenG2P/farmer-registry/blob/develop/scripts/uninstall-registry.sh) `--namespace <ns> --release fr [--keep-iam] [--keep-dashboards] [--dry-run] [--yes]` | As above, and first removes the registry's Superset dashboards (its default release name is `registry`) |

Run each with `--dry-run` first. None of them touches Partner Management or the Consent Manager: remove the composite's and partners' PM entries and CM bindings there if needed.
