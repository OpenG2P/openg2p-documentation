---
description: The openg2p-farmer-registry Helm chart — components, parameters and versions.
---

# Helm chart

The Farmer Registry is deployed by a single self-sufficient chart, **`openg2p-farmer-registry`**, in [`helm/openg2p-farmer-registry`](https://github.com/OpenG2P/farmer-registry/tree/develop/helm/openg2p-farmer-registry). "Self-sufficient" means the chart installs the registry outright — there is no base registry wrapper chart to install first, and the [registry platform](https://github.com/openg2p/registry-platform) ships no chart of its own.

Published to the [OpenG2P Helm repo](https://openg2p.github.io/openg2p-helm) by the central CI pipeline.

## What it deploys

| Component | Image | Built in this repo? |
| --------- | ----- | ------------------- |
| Staff Portal API | `openg2p-farmer-registry-staff-portal-api` | Yes |
| Partner API (DCI) | `openg2p-farmer-registry-partner-api` | Yes |
| Celery worker + beat producer | `openg2p-farmer-registry-celery` | Yes (one image, mode selected at runtime) |
| DB seed | `openg2p-farmer-registry-db-seed` | Yes — see [Data seeding](data-seeding.md) |
| Sanity | `openg2p-farmer-registry-sanity` | Yes |
| Staff Portal UI | `openg2p-registry-staff-portal-ui` | No — platform image |
| Beneficiary Portal API | `openg2p-registry-bene-portal-api` | No — platform image |

The registry code is not vendored: each backend image installs the [registry-platform](https://github.com/OpenG2P/registry-platform) packages plus this repo's `farmer-extension` at build time, from pinned git refs.

## Dependencies

Pulled from the [OpenG2P Helm repo](https://openg2p.github.io/openg2p-helm):

* **common** — shared templates/helpers
* **postgres-init** — creates the registry databases and users
* **redis** — Celery broker/result backend
* **openg2p-id-generator** (alias `idgenerator`) — functional ID generation
* **keycloak-init** — realms, clients and demo users

All except `common` sit behind an `enabled` condition, so they can be switched off when the environment already provides them. Shared services — **Keycloak**, **master-data**, **Consent Manager**, **Partner Management** and the **Approval Workflow Engine (AWE)** — are *not* bundled: they come from **commons-services** and the chart is pointed at them via `global.*` URLs.

## Install-time jobs

Ordered `post-install,post-upgrade` hooks:

| Weight | Job | Purpose |
| ------ | --- | ------- |
| 10 | `db-seed` | Register definitions, geo, sample data, templates, AWE seed |
| 11 | `sanity-pm-seed` | Register the sanity test partner's key in Partner Management |
| 12 | `sanity-cm-seed` | Create the sanity partner's Consent Manager binding + policy |
| 13 | `sanity-data-seed` | Provision the sanity test user, inject its test farmer, register it as an AWE approver |
| 15 | `sanity` | Run the in-cluster [sanity suite](sanity-testing.md) against the partner-api |

The three `sanity-*-seed` Jobs only render when `sanity.runE2e` is on — which it is **not** by default, so a normal install creates no test fixtures at all and runs only the suite's smoke tier. Finished pods are retained (`hook-delete-policy: before-hook-creation`) so their logs stay readable. By default the sanity Job exits 0 even when tests fail, so it never blocks an install — set `sanity.failOnError: true` to gate a deployment on it.

## Integrating Consent Manager and Partner Management

The **partner-api** is the policy-enforcement point for DCI requests, and it depends on two commons-services components:

* **Partner Management (PM)** — the source of partner **public keys**. The partner-api fetches the key named by the request's `kid` and verifies the DCI envelope signature against it.
* **Consent Manager (CM)** — the policy decision point. The partner-api calls CM `/validate` with the consent object embedded in the request, and **clamps the returned fields to the consented data scopes**.

Both are installed once per environment as part of commons-services; the registry only needs the URLs.

| Parameter | Default | Purpose |
| --------- | ------- | ------- |
| `global.partnerSignatureValidationEnabled` | `true` | Verify the DCI envelope signature against the partner's PM key |
| `global.consentEnforcementEnabled` | `true` | Call CM `/validate` and clamp fields to the consented scopes |
| `global.partnerManagementApiUrl` | `http://commons-services-pm-partner-api` | PM partner-api — partner key lookup |
| `global.consentManagerUrl` | `http://commons-services-cm-partner-api` | CM partner-api — the `/validate` PDP endpoint |
| `global.consentManagerTimeoutSeconds` | `5` | CM call timeout |
| `global.registryCryptoBackend` | `partner-mgmt` | Partner-key backend: `partner-mgmt` \| `keymanager` \| `local` |

{% hint style="warning" %}
**Both switches default to `true` — the chart fails closed**, matching the registry platform's own defaults. Turning either off is a deliberate choice that opens real PII egress: with signature validation off the `signature` field is required but never inspected (any string passes), and with consent enforcement off the Consent Manager is never called and records are returned **unclamped** — every field the DCI template emits, to any caller. Either bypass is logged and stamped into the DCI response header meta (`signature_validation` / `consent_enforcement`), which is the only outward signal.

Legitimate reasons to disable are performance testing, or a bring-up install where commons-services is not yet deployed — until it is, the DCI search will reject requests.
{% endhint %}

A further set — `global.partnerManagementAdminApiUrl`, `global.consentManagerStaffUrl`, `global.consentManagerAuthClientId` and `global.pmSeedClientId` — is used **only by the sanity e2e**, to seed its test partner into PM and its binding into CM. These are not needed for normal registry operation.

## Running more than one registry in a namespace

Names that would otherwise collide are scoped to the release, so a Farmer Registry and a [National Social Registry](../../national-social-registry/README.md) can coexist in one namespace: the Keycloak staff client, the MinIO buckets (including `registrant-photos`), the keymanager app-id and the AWE callback-secret id all derive from `{{ .Release.Name }}`. The release name is freely choosable — the chart pins neither the release name nor a display name.

## Configuration

Everything is in [`values.yaml`](https://github.com/OpenG2P/farmer-registry/blob/develop/helm/openg2p-farmer-registry/values.yaml), which is commented throughout. The blocks worth knowing before a real install:

* **`global.*`** — external service URLs (Keycloak, master-data, CM, PM, AWE), database hosts, shared secrets, and the CM/PM switches above.
* **`idgenerator.*`** — your ID types; usually the one block that must change.
* **`dbSeed.*`** — seeding flags; set the sample-data flags to `false` in production (see [Data seeding](data-seeding.md)).
* **`sanity.*`** — `enabled`, `runE2e`, `failOnError`.
* **per-component** — `replicaCount`, `resources`, `autoscaling`, `envVars` and worker counts for each API and the Celery pods.

## Versions and CI

**Changelog — what changed in each version:** [openg2p-packaging/farmer-registry/CHANGELOG](https://openg2p.github.io/openg2p-packaging/farmer-registry/CHANGELOG).

The chart and images are built and published by the **OpenG2P central build/versioning/publish pipeline** — see [Helm & Docker Versioning Strategy and CI](../../../../releases/helm-docker-versioning-and-ci/) for the authoritative description. The repo carries a single thin stub, [`.github/workflows/build-publish.yml`](https://github.com/OpenG2P/farmer-registry/blob/develop/.github/workflows/build-publish.yml), calling `openg2p/openg2p-packaging/.github/workflows/build-publish.yml@v1`; all versioning, build/promote, publish and changelog logic lives centrally behind `@v1`.

**One version per commit.** Every image and the chart built from a commit carry the **same** version, derived purely from git — the branch/tag and the commit count `N` (`git rev-list --count HEAD`) — never from a file in the working tree:

| You are on…               | Version produced                                              | Frozen? | Chart published?     |
| ------------------------- | ------------------------------------------------------------ | ------- | -------------------- |
| `develop`                 | `0.0.0-develop.N`                                             | no      | yes (rolling)        |
| release line branch `1.0` | `1.0.0-rc.N` (then `1.0.1-rc.N` after `1.0.0` is tagged)       | no      | yes                  |
| **tag** `1.0.0`           | `1.0.0` (promoted from the tested RC — a retag, not a rebuild) | **yes** | yes                  |
| any other branch          | `0.0.0-<branch>.N`                                            | no      | **no** (images only) |

Release tags are the **bare** version (`1.0.0`, no `v` prefix). To cut a release you create a release-line branch (`1.0`, publishing `1.0.0-rc.N`) and then **tag** the blessed commit `1.0.0` — you do not create a `1.0.0` branch. Each immutable version is published exactly once and never overwritten.

The underlying **platform version** is the version of the [`registry-platform`](https://github.com/openg2p/registry-platform) repository the registry is built from. Because the images track its moving `develop` branch, each build **pins** it: the Dockerfiles declare `REGISTRY_PLATFORM_REF`, `FASTAPI_COMMON_REF` and `IAM_CORE_REF` (and `OPENG2P_DATA_BRANCH` for db-seed) as `ARG`s, and the pipeline resolves each ref to a **commit SHA before the build**, passes it as the build-arg, and records it as an `org.openg2p.pin.<arg>` OCI label. So `docker inspect` on any Farmer Registry image reveals the exact platform commits it was built from, and a given commit always reproduces the same image.
