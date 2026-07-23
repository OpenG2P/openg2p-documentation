---
description: >-
  The openg2p-nsr chart — a thin wrapper over the platform chart, its images,
  and the values that make it the National Social Registry.
---

# Helm chart

The National Social Registry is deployed by **`openg2p-nsr`** ([`helm/openg2p-nsr`](https://github.com/OpenG2P/national-social-registry/tree/develop/helm/openg2p-nsr)), published to the [OpenG2P Helm repo](https://openg2p.github.io/openg2p-helm).

The chart **owns no templates**. It declares the platform chart as a pinned dependency and supplies a values overlay:

```yaml
# Chart.yaml
dependencies:
  - name: openg2p-registry
    alias: registry              # overlay nests under .Values.registry
    version: 0.0.0-develop.288   # HARDCODED — moved deliberately
    repository: https://openg2p.github.io/openg2p-helm
```

Every service template, IAM/Keycloak wiring, db-seed mechanism and the sanity suite come from that subchart. See [Packaging & the reference registry](../../registry/deployment-and-extension/packaging-and-reference-registry.md) for what the platform chart contains.

{% hint style="info" %}
**This replaces the previous self-sufficient chart.** NSR used to own all ~40 templates and its own `questions.yaml`. Those now live once, in the platform chart.
{% endhint %}

## Two kinds of value

| Where | What | Why |
|---|---|---|
| `global.*` | Shared settings — hostnames, DB hosts, Keycloak, CM/PM/AWE/Audit URLs, the enforcement switches | Helm propagates `global` into subcharts automatically, so these are set at the top level |
| `registry.*` | Everything else — images, component toggles, `dbSeed.*`, `sanity.*`, `idgenerator.*` | These are the **subchart's** values, so they nest under the `registry` alias |

A platform setting that was `dbSeed.loadSampleData` when installing the platform chart directly becomes `registry.dbSeed.loadSampleData` here.

## What it deploys

| Component | Image | Built in this repo? |
|---|---|---|
| Staff Portal API | `openg2p-nsr-staff-api` | Yes |
| Partner API (DCI) | `openg2p-nsr-partner-api` | Yes |
| Celery worker + beat | `openg2p-nsr-celery` | Yes (one image, role selected by `CELERY_APP`) |
| DB seed | `openg2p-nsr-db-seed` | Yes — see [Data seeding](data-seeding.md) |
| Staff Portal UI | `openg2p-registry-staff-ui` | **No** — platform image, used as-is |
| Beneficiary Portal API | `openg2p-registry-bene-api` | **No** — platform image, used as-is |
| Sanity tests | `openg2p-nsr-sanity-tests` | Yes — see [Sanity testing](sanity-testing.md) |

Each NSR backend image is a few lines: `FROM` the matching platform image, `pip install nsr-extension`, and set `REGISTRY_EXTENSION_MODULE=openg2p_registry_nsr_extension`. The platform code is never vendored — it is already in the base image.

## What the overlay actually sets

Deliberately small:

* **Images** — the five NSR-built repositories above.
* **`global.registryVariant: nsr`** and the ingress hostname.
* **`registry.dbSeed.load*`** — the loaders, which the platform defaults off.
* **`registry.iamRegister.applicationDescription`** — the name of this registry's tile in IAM. The roles/permissions catalog itself is registry-agnostic and comes from the subchart.
* **`registry.idgenerator...idTypes`** — the functional-ID pools, `individual` (12) and `household` (10).
* **`registry.sanity`** — the NSR sanity image and the seeded record's search text; the register id, tab and section are already correct as subchart defaults.

## Configuration form (Rancher)

The chart ships **no `questions.yaml` of its own**. Rancher reads questions only from the root of the chart being installed and ignores a subchart's, so the file is **generated at packaging time** from the pinned `openg2p-registry` dependency: every non-`global.` variable is prefixed with `registry.`, and each question's default is resolved from this chart's overlay first, then the platform's. The NSR form therefore offers exactly the platform's settings and cannot drift from the pinned version.

## Consent Manager and Partner Management

The **partner-api** is the policy-enforcement point for DCI requests and depends on two commons-services components: **Partner Management** (source of partner public keys, used to verify the DCI envelope signature) and **Consent Manager** (the decision point — the partner-api calls `/validate` and clamps the response to the consented scopes).

| Parameter | Default | Purpose |
|---|---|---|
| `global.partnerSignatureValidationEnabled` | `true` | Verify the DCI envelope signature against the partner's PM key |
| `global.consentEnforcementEnabled` | `true` | Call CM `/validate` and clamp fields to the consented scopes |
| `global.partnerManagementApiUrl` | `http://commons-services-pm-partner-api` | Partner key lookup |
| `global.consentManagerUrl` | `http://commons-services-cm-partner-api` | The `/validate` endpoint |

{% hint style="warning" %}
**Both switches default to `true` — the chart fails closed.** Turning either off opens real PII egress: with signature validation off the `signature` field is required but never inspected, and with consent enforcement off records are returned **unclamped**. Either bypass is stamped into the DCI response header meta (`signature_validation` / `consent_enforcement`), which is the only outward signal.
{% endhint %}

## Running more than one registry in a namespace

Names that would otherwise collide are scoped to the release, so an NSR and a [Farmer Registry](../../farmer-registry/README.md) can coexist: the Keycloak staff client, the MinIO buckets, the keymanager app-id and the AWE callback-secret id all derive from `{{ .Release.Name }}`.

## Versions and CI

The chart and all NSR images are built by the **OpenG2P central pipeline** at **one version per commit** — see [Helm & Docker Versioning Strategy and CI](https://docs.openg2p.org/operations/deployment/helm-docker-versioning-and-ci) for the authoritative rules. The repo carries a single thin stub, [`.github/workflows/build-publish.yml`](https://github.com/OpenG2P/national-social-registry/blob/develop/.github/workflows/build-publish.yml), calling `openg2p-packaging@v1`. This replaces the previous branch-derived chart versioning and the separate per-image workflows.

Two version lines meet in this chart, and they move independently:

* **The NSR version** — the chart and the five NSR images, locked together and stamped by CI on every commit.
* **The platform version** — `RP_VERSION` in the Dockerfiles and the `openg2p-registry` dependency in `Chart.yaml`. These are **hardcoded and changed deliberately**, always as a pair.

Released versions and what changed in each: [**Versions**](../versions/README.md).
