---
description: >-
  Deploying Open Agri Stack on a cluster: the order of installs and the
  settings for commons (Master Data with the Ethiopia pack and agriculture
  domain, PM, CM), the Farmer and Crop Sown registries, and the composite;
  uninstalling.
---

# Deploying on a Cluster

Open Agri Stack is installed into one environment (namespace) from OpenG2P Helm charts, through Rancher. This page lists the order and the settings that matter for Open Agri Stack; each chart's own documentation covers the rest.

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
| 7 | Test | [End-to-end test](end-to-end-test.md) | — |

The release names `fr` and `csr` match the composite's default registry URLs (`http://fr-partner-api/…`, `http://csr-partner-api/…`); with other names, change `composite.registries` in step 6.

## Commons services: Master Data, PM, CM

{% hint style="info" %}
Master Data (MDS) serves Open Agri Stack's **catalogues** (code lists, reference entities, geography) for now. Proper catalogues are still to be designed; see [Layer 2: catalogues](../architecture/registry-model.md#layer-2-catalogues).
{% endhint %}

See the [Commons Helm Chart](../../deployment/openg2p-commons-helm-chart.md). In the `openg2p-commons-services` form:

| Group | Setting | Value for Open Agri Stack |
| --- | --- | --- |
| Country Pack | **Country Pack** (`masterData.geoSeed.countryPack`) | `ETH` (Ethiopia; the commons default) |
| Country Pack | **Domain Code Lists** (`masterData.geoSeed.domains`) | `agriculture` (default) — needed by the Farmer Registry and the Crop Sown Registry: they read these lists live from Master Data, and without them their dropdowns are empty and every coded entry is rejected. Leave it as is; a pack without the `agriculture` domain skips it with a warning in the geo-seed Job log |
| Country Pack | **Load Code Lists** (`masterData.geoSeed.load.codelists`) | on (default) |
| Country Pack | **Load Sample People** (`masterData.geoSeed.load.samples`) | on (default) — the registries' sample farmers and crop seasons are derived from them |
| Partner Management | **Install Partner Management?** (`partner-management.enabled`) | on |
| Consent Manager | **Install Consent Manager?** (`openg2p-consent-manager.enabled`) | **on** (the Rancher form defaults it off) |
| AWE | **Install AWE?** (`openg2p-awe.enabled`) | on (the registries' change requests and CM policy approvals use it) |

The Audit Manager is part of commons-services; the composite sends its events to `http://commons-services-auditmanager:80`.

The ETH pack carries a licence obligation (CC BY-IGO, attribution required); see [Country Data Architecture](../../platform/country-data-architecture.md) and [Master Data Service](../../platform/platform-services/master-data-service/README.md). PM and CM details: [PM deployment](../../platform/platform-services/partner-management/deployment.md), [CM deployment](../../consent-management/deployment/README.md).

## Farmer Registry

Install as in [Farmer Registry → Deployment](../../products/registry/farmer-registry/deployment/README.md), release name `fr`. Settings that matter here (the registry questions are inherited from the platform chart; platform settings sit under `registry.`):

| Setting | Value |
| --- | --- |
| **Verify Partner Signature** (`global.partnerSignatureValidationEnabled`) | on (default) |
| **Enforce Consent** (`global.consentEnforcementEnabled`) | on (default) |
| **Partner Key Verification Backend** (`global.registryCryptoBackend`) | `partner-mgmt` (default) |
| **Partner Management URL** (`global.partnerManagementApiUrl`) | `http://commons-services-pm-partner-api` (default) |
| **Consent Manager URL** (`global.consentManagerUrl`) | `http://commons-services-cm-partner-api` (default) |
| **Consent data controller** (`global.consentDataController`) | `farmer-registry` (defaults to the registry variant) |
| **Load Sample Data** (`registry.dbSeed.loadSampleData`) | **off by default**; on for a demo (sample farmers from Master Data's sample people, lands numbered `LAND-<n>-<k>`) |

See [Data seeding](../../products/registry/farmer-registry/deployment/data-seeding.md) and [Helm chart](../../products/registry/farmer-registry/deployment/helm-chart.md).

## Crop Sown Registry

The chart `openg2p-crop-sown-registry` is a values overlay over `openg2p-registry` ([source](https://github.com/OpenG2P/crop-sown-registry)); the form shows the platform's questions plus a "Crop Sown Registry" group. Install it the same way as the Farmer Registry, release name `csr`.

| Setting | Value |
| --- | --- |
| Signature, consent, PM and CM settings | As for the Farmer Registry (defaults) |
| **Consent data controller** (`global.consentDataController`) | `crop-sown-registry` (defaults to the registry variant) |
| **Load Sample Data** (`registry.dbSeed.loadSampleData`) | **off by default**; on for a demo: loads the two sample clusters |
| **Load sample crop seasons** (`REGISTRY_CELERY_WORKERS_ACTIVITY_LOAD_SAMPLE_DATA`) | **off by default**; shown only when Load Sample Data is on. Records the sample crop seasons once, after install; needs the sample clusters and Master Data's sample people. Leave off for production. |
| **Pull submissions from ODK Central** (`REGISTRY_CELERY_WORKERS_ACTIVITY_ODK_ENABLED`) | off by default. When on, also activate the form in the register's Settings (ODK project and form ID) and create the ODK credentials Secret |
| **ODK Central URL** (`REGISTRY_CELERY_WORKERS_ACTIVITY_ODK_BASE_URL`) | `http://commons-services-odk-central-backend` |

* **No code lists are seeded** in the registry: they are read from Master Data's agriculture domain (set on commons-services, above).
* **No geo setting:** register forms read the country's geo levels from Master Data when they load; seed Jobs read Master Data through its API, never its database.
* **ID generator:** installed, with one pool, `cluster`, for the Cluster register's generated Cluster IDs (`registry.idgenerator.idGenerator.appConfig.idTypes`; nothing to set). Crop seasons have no functional IDs.
* **AWE:** nothing to set. The chart uses the shared AWE in commons-services; db-seed loads the Cluster approval policies and keycloak-init creates the approvers they name (`alex.carter`, `nina.patel`).
* **Sanity:** the platform's smoke tier runs on install; its e2e tier stays off (it seeds a record-register record, which this registry doesn't have). Activity-register checks run against a deployed instance with `scripts/e2e_smoke.py`.

## PM and CM entries, and the signing Secret

Before the composite can serve requests:

1. **Keys.** Generate the composite's key as a `.p12` (and, for testing, a partner key): `python composite/scripts/partner_kit.py keys` writes both to `scripts/kit-out/` and prints the next steps.
2. **PM.** A PM administrator onboards and approves the composite as `PARTNER_AGRI_COMPOSITE` with its public key and `kid`, and each partner as `PARTNER_<ID>` ([partner guide, step 2](partner-guide.md#step-2-get-onboarded-in-partner-management)).
3. **Signing Secret** in the namespace:

   ```bash
   kubectl -n <ns> create secret generic agri-composite-signing \
     --from-file=composite.p12=./composite.p12 --from-literal=password='<p12 password>' \
     --from-literal=kid=agri-composite-2026-01 --from-literal=algorithm=auto
   ```

   `kid` must match the kid registered for the composite in PM (blank → the certificate's SHA-256 thumbprint). `algorithm: auto` takes it from the key type (EC → ES256, Ed25519 → EdDSA, RSA → RS256).
4. **CM.** The CM administrator creates, for each partner, a binding and a policy with each registry ([partner guide, step 3](partner-guide.md#step-3-get-a-binding-and-policy-for-each-registry)).

The [end-to-end test](end-to-end-test.md) does steps 1–4 for a test partner in one go.

## Use-case composite

Install **Agri Stack Composite** from the Rancher catalog. Settings ([composite configuration](composite-configuration.md#helm-values)):

* **General:** Composite Hostname (default `agri-composite.<namespace>.openg2p.org`, Istio internal gateway), Image Tag.
* **Integration:** Composite Partner ID (`agri-composite`), Partner Management URL, Audit Manager URL, the Farmer Registry and Crop Sown Registry search URLs (check them against your release names).
* **Signing key:** the Secret name (`agri-composite-signing`).
* **Scaling:** autoscaling (1–5 pods), workers per pod.
* **Use cases:** not in the form. Edit `composite.useCases` in **Edit YAML** (e.g. `allowed_partners` of `loan-profile`), or point `composite.existingUseCasesConfigMap` at your own ConfigMap.

The post-install sanity hook pings the API and lists the use cases; a failure fails the release.

## Uninstalling

| What | Script | Notes |
| --- | --- | --- |
| Composite | [`composite/deployment/scripts/uninstall-agri-composite.sh`](https://github.com/openg2p/agri-stack/blob/develop/composite/deployment/scripts/uninstall-agri-composite.sh) `--namespace <ns> [--release agri-composite] [--drop-signing-secret] [--dry-run] [--yes]` | Removes the release, leftover hook Jobs, ConfigMaps and Secrets labelled with the release; the signing Secret only with `--drop-signing-secret`. The composite has no database or PVCs. |
| Crop Sown Registry | [`scripts/uninstall-registry.sh`](https://github.com/OpenG2P/crop-sown-registry/blob/develop/scripts/uninstall-registry.sh) `--namespace <ns> [--release csr] [--keep-iam] [--keep-pvs] [--dry-run] [--yes]` | Also drops the registry's database and role in `commons-postgresql`, its IAM rows, PVCs and their PVs |
| Farmer Registry | [`scripts/uninstall-registry.sh`](https://github.com/OpenG2P/farmer-registry/blob/develop/scripts/uninstall-registry.sh) `--namespace <ns> --release fr [--keep-iam] [--keep-dashboards] [--dry-run] [--yes]` | As above, and first removes the registry's Superset dashboards (its default release name is `registry`) |

Run each with `--dry-run` first. None of them touches Partner Management or the Consent Manager: remove the composite's and partners' PM entries and CM bindings there if needed.
