---
description: >-
  How the Disability Registry is packaged, where its source and artifacts live,
  and what each published image contains.
---

# Deployment

The Disability Registry is **not** a registry built from scratch. It is a thin
**extension** of the [OpenG2P Registry Platform](../../registry/deployment-and-extension/README.md),
which publishes the runnable Docker images and the `openg2p-registry` Helm chart.
This repository adds only the disability domain on top.

{% hint style="info" %}
The packaging model — why the platform publishes the artifacts and a domain
registry extends them — is described once, in the platform docs:
[**Deployment and Extension**](../../registry/deployment-and-extension/README.md).
This section covers only what is disability-specific.
{% endhint %}

## Where everything lives

| Artifact | Location |
|---|---|
| **Source code** | [gitlab.com/openg2p/registry/disability-registry](https://gitlab.com/openg2p/registry/disability-registry) |
| **Docker images** | `registry.gitlab.com/openg2p/registry/disability-registry/<name>` — the project's own GitLab container registry |
| **Helm chart** | `openg2p-disability-registry`, published to the shared [`openg2p/charts`](https://gitlab.com/openg2p/charts) Helm registry (project `84460547`, channel `stable`) |
| **Platform chart it extends** | `openg2p-registry`, same registry, pinned as a dependency |
| **CI** | GitLab CI, including [`openg2p/packaging`](https://gitlab.com/openg2p/packaging)`@v1` — all versioning, build and publish logic is central |

One pipeline derives **one version from git** for the whole commit, builds every
image, rewrites the chart's image tags to that version, generates
`questions.yaml` from the pinned platform chart, and publishes. Images and chart
therefore always ship at the same version.

## Published images

Five images are built here. Each is a ~10-line `FROM` of the matching platform
image plus the domain package; the runtime, entrypoint and CMD are inherited.

| Image | Runs as | Contains |
|---|---|---|
| `staff-api` | Staff Portal API | The domain model + the platform's staff API. Serves the staff portal; **runs the database migration** on start |
| `partner-api` | Partner API | The domain model + the platform's partner API. Answers DCI searches — renders records through the outbound template and clamps them to the consented scopes |
| `celery` | Worker **and** beat | Both celery codebases; which one runs is chosen at deploy time by `CELERY_APP`. Drains the completion-score queue and computes the `SUPPORT_NEED` score |
| `db-seed` | Install/upgrade Job | The seed SQL (registers, screens, code lists, approval policies), the DCI templates, the sample-data loader, and this registry's reporting views + `reporting.yaml` |
| `sanity-tests` | Post-install Job | The platform's test harness and generic tests, overlaid with this registry's field-specific e2e tests |

Two more are consumed **as-is** from the platform, because they carry no domain
code: `staff-ui` (the staff portal front end) and `bene-api`.

{% hint style="info" %}
`db-seed` ships its **own** sample-data loader and image uploader. The platform's
are written against the reference registry's tables and would crash-loop here.
Genuinely generic parts — the entrypoint, geo loader, code-list loader,
geo-widget sync, template uploader — are inherited unchanged.
{% endhint %}

## The chart

`openg2p-disability-registry` is a wrapper: a **pinned dependency** on
`openg2p-registry` plus a values overlay. It owns no service templates —
deployments, services, ingress, IAM/Keycloak wiring and the db-seed machinery all
come from the subchart.

It does own the **analytics** layer, because the reporting views and dashboards
are written against this registry's schema and the platform has no concept of
them:

| Template | Purpose |
|---|---|
| `analytics-jobs.yaml` | Reporting-views and dashboard-import Jobs |
| `reporting-views-refresh.yaml` | CronJob refreshing the materialized views hourly |
| `dashboard-bundle-configmap.yaml` | Ships `dr-dashboards.zip` into the cluster |
| `maps-content-configmap.yaml` | Map queries and page for G2P Insights |
| `superset-service-account-secret.yaml` | The Superset service account |

## Version pinning

The platform version is pinned in **two places that move together**: `RP_VERSION`
in each Dockerfile (the base image tag) and the `openg2p-registry` dependency in
`Chart.yaml`. Nothing about the platform is vendored or copied.

```bash
./scripts/bump-rp-version.sh -n          # preview the latest safe version
./scripts/bump-rp-version.sh <version>   # move both together
```

`test/test_rp_pin_lockstep.py` fails the build if they ever drift — a chart on
one platform version with images built against another lands the sanity overlay
on a harness it does not match.

## Install order

Helm hook weights sequence the whole install:

| Weight | Job | Does |
|---|---|---|
| 10 | `db-seed` | Registers, screens, code lists, templates, approval policies, sample data |
| 19–20 | `iam-register` | Registers the roles→permissions catalogue into IAM |
| 25 | `sanity` | The e2e suite |
| 45 | `reporting-views` | Hand-written views, then the generated ones |
| 49–50 | `dashboards` | Imports the Superset bundle and enables embedding |

The analytics chain sits **above** the sanity suite deliberately: the suite
asserts against its own injected fixture, and rebuilding the views underneath it
would change what it is checking.

{% hint style="warning" %}
The db-seed Job waits for AWE to be healthy before it runs. If AWE is down,
db-seed blocks, Helm's install timeout expires, and the release is marked failed
**before the sanity Job is ever created**. If you see no sanity Job at all, check
`db-seed` and commons-services first.
{% endhint %}

## Next

* [**Deploying on Rancher**](rancher.md) — step-by-step install
* [**Dashboards and maps**](../dashboards.md) — what the analytics layer produces
* [**Customisation**](../customisation.md) — adapting it to your country
