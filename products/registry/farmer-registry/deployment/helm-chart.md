---
description: >-
  The openg2p-farmer-registry chart — a thin wrapper over the platform chart,
  its images, and the values that make it the Farmer Registry.
---

# Helm chart

{% hint style="info" %}
**New home: GitLab.** **`farmer-registry`** is now developed at [gitlab.com/openg2p/registry/farmer-registry](https://gitlab.com/openg2p/registry/farmer-registry).

Any `github.com` links on this page refer to the **earlier GitHub repository**, which is now read-only. They are kept so that references to previous versions keep working.
{% endhint %}

The Farmer Registry is deployed by **`openg2p-farmer-registry`** ([`helm/openg2p-farmer-registry`](https://github.com/OpenG2P/farmer-registry/tree/develop/helm/openg2p-farmer-registry)), published to the [OpenG2P Helm repo](https://openg2p.github.io/openg2p-helm).

The chart **owns no templates**. It declares the platform chart as a pinned dependency and supplies a values overlay:

```yaml
# Chart.yaml
dependencies:
  - name: openg2p-registry
    alias: registry              # overlay nests under .Values.registry
    version: 0.0.0-develop.286   # HARDCODED — moved deliberately
    repository: https://openg2p.github.io/openg2p-helm
```

Every service template, IAM/Keycloak wiring and db-seed mechanism comes from that subchart. See [Packaging & the reference registry](../../registry/deployment-and-extension/packaging-and-reference-registry.md) for what the platform chart contains.

{% hint style="info" %}
**Why a wrapper and not just a values file.** A values-only install works, but the Farmer Registry needs its own catalogue entry, branding and version line in Rancher. The wrapper gives that without copying the ~50 template files.
{% endhint %}

## Two kinds of value

| Where | What | Why |
|---|---|---|
| `global.*` | Shared settings — hostnames, DB hosts, Keycloak, CM/PM/AWE/Audit URLs, the enforcement switches | Helm propagates `global` into subcharts automatically, so these are set at the top level |
| `registry.*` | Everything else — images, component toggles, `dbSeed.*`, `sanity.*` | These are the **subchart's** values, so they nest under the `registry` alias |

This is the one thing to remember when writing a values file for the Farmer Registry: a platform setting that was `dbSeed.loadSampleData` when installing the platform chart directly becomes `registry.dbSeed.loadSampleData` here.

## What it deploys

| Component | Image | Built in this repo? |
|---|---|---|
| Staff Portal API | `openg2p-farmer-registry-staff-api` | Yes |
| Partner API (DCI) | `openg2p-farmer-registry-partner-api` | Yes |
| Celery worker + beat | `openg2p-farmer-registry-celery` | Yes (one image, role selected by `CELERY_APP`) |
| DB seed | `openg2p-farmer-registry-db-seed` | Yes — see [Data seeding](data-seeding.md) |
| Sanity tests | `openg2p-farmer-registry-sanity-tests` | Yes — see [Sanity testing](sanity-testing.md) |
| Staff Portal UI | `openg2p-registry-staff-ui` | **No** — platform image, used as-is |
| Beneficiary Portal API | `openg2p-registry-bene-api` | **No** — platform image, used as-is |

Each farmer image is a few lines: `FROM` the matching platform image, `pip install farmer-extension`, and set `REGISTRY_EXTENSION_MODULE=openg2p_registry_farmer_extension`. The platform code is never vendored — it is already in the base image.

## Configuration form (Rancher)

The chart ships **no `questions.yaml` of its own**. Rancher reads questions only from the root of the chart being installed and ignores a subchart's, so the file is **generated at packaging time** from the pinned `openg2p-registry` dependency: every non-`global.` variable is prefixed with `registry.`, and each question's default is resolved from this chart's overlay first, then the platform's.

The practical effect: the Farmer Registry form offers exactly the platform's settings, already showing the farmer images and toggles, and it cannot drift from the pinned platform version.

## Consent Manager and Partner Management

The **partner-api** is the policy-enforcement point for DCI requests and depends on two commons-services components: **Partner Management** (source of partner public keys, used to verify the DCI envelope signature) and **Consent Manager** (the decision point — the partner-api calls `/validate` and clamps the response to the consented scopes).

| Parameter | Default | Purpose |
|---|---|---|
| `global.partnerSignatureValidationEnabled` | `true` | Verify the DCI envelope signature against the partner's PM key |
| `global.consentEnforcementEnabled` | `true` | Call CM `/validate` and clamp fields to the consented scopes |
| `global.partnerManagementApiUrl` | `http://commons-services-pm-partner-api` | Partner key lookup |
| `global.consentManagerUrl` | `http://commons-services-cm-partner-api` | The `/validate` endpoint |
| `global.registryCryptoBackend` | `partner-mgmt` | Partner-key backend: `partner-mgmt` \| `keymanager` \| `local` |

{% hint style="warning" %}
**Both switches default to `true` — the chart fails closed.** Turning either off opens real PII egress: with signature validation off the `signature` field is required but never inspected, and with consent enforcement off records are returned **unclamped** — every field the DCI template emits, to any caller. Either bypass is stamped into the DCI response header meta (`signature_validation` / `consent_enforcement`), which is the only outward signal.

Legitimate reasons to disable are performance testing, or a bring-up install before commons-services exists.
{% endhint %}

## Running more than one registry in a namespace

Names that would otherwise collide are scoped to the release, so a Farmer Registry and a [National Social Registry](../../national-social-registry/README.md) can coexist: the Keycloak staff client, the MinIO buckets, the keymanager app-id and the AWE callback-secret id all derive from `{{ .Release.Name }}`.

## Versions and CI

The chart and all farmer images are built by the **OpenG2P central pipeline** at **one version per commit** — see [Helm & Docker Versioning Strategy and CI](https://docs.openg2p.org/operations/deployment/helm-docker-versioning-and-ci) for the authoritative rules. The repo carries a single thin stub, [`.github/workflows/build-publish.yml`](https://github.com/OpenG2P/farmer-registry/blob/develop/.github/workflows/build-publish.yml), calling `openg2p-packaging@v1`.

Two version lines meet in this chart, and they move independently:

* **The Farmer Registry version** — the chart and the five farmer images, locked together and stamped by CI on every commit.
* **The platform version** — `RP_VERSION` in the Dockerfiles and the `openg2p-registry` dependency in `Chart.yaml`. These are **hardcoded and changed deliberately**, always as a pair. Move both together with `./scripts/bump-rp-version.sh` (`-n` to preview the latest published version, `<version>` to pin a specific one); a CI check fails the build if the two ever drift.

Released versions and what changed in each: [**Versions**](../versions/README.md).
