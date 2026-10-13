---
description: >-
  How the Crop Sown Registry is packaged: its images, its Helm chart, the
  pinned registry platform version, and what happens on install.
---

# Deployment

The Crop Sown Registry is a thin **extension** of the [OpenG2P Registry Platform](../../registry/deployment-and-extension/README.md). The platform publishes the runnable images and the `openg2p-registry` Helm chart. This repository adds the crop domain on top.

{% hint style="info" %}
The packaging model is described once, in the platform docs: [Deployment and Extension](../../registry/deployment-and-extension/README.md). This page covers only what is specific to the Crop Sown Registry.
{% endhint %}

## Where everything lives

| Artifact | Location |
| --- | --- |
| **Source code** | [github.com/OpenG2P/crop-sown-registry](https://github.com/OpenG2P/crop-sown-registry) |
| **Docker images** | `openg2p/openg2p-crop-sown-registry-<name>` on Docker Hub |
| **Helm chart** | `openg2p-crop-sown-registry` (Rancher: **OpenG2P Crop Sown Registry**), in the [`openg2p-helm`](https://openg2p.github.io/openg2p-helm) repository |
| **Platform chart it extends** | `openg2p-registry`, pinned as a dependency under the alias `registry` |
| **CI** | GitHub Actions, calling [`openg2p-packaging`](https://github.com/OpenG2P/openg2p-packaging)`@v1` |

One pipeline builds every image from a commit, gives them all the same version, writes that version into the chart, and publishes. The chart's Rancher form is generated from the pinned platform chart, plus this chart's own questions.

A second workflow runs checks without Docker:

* the generated seed SQL matches `scripts/activity_definitions.py`;
* the platform version is the same in the Dockerfiles and the chart;
* every list and code the activity definitions use is in the shipped country pack (ETH).

## Images

Four images are built here. Each is a few lines: `FROM` the matching platform image, plus the `crop-sown-extension` package.

| Image | Runs as | Adds |
| --- | --- | --- |
| `staff-api` | Staff portal API | The crop domain. Creates the activity tables and the Cluster tables on start |
| `partner-api` | Partner API | The crop domain: partner activities, DCI search, data scopes |
| `celery` | Celery worker **and** beat | The crop domain. Runs the activity outbox (crop season status, season summaries), the ODK pull and the sample crop seasons |
| `db-seed` | Install and upgrade Job | The seed SQL, the DCI templates, the Cluster approval policies and the sample cluster loader |

The staff portal UI, the sanity tests and the other platform components are used as published by the platform.

## The chart

`openg2p-crop-sown-registry` has **no templates**. It is a values overlay on `openg2p-registry`. It sets:

* the registry variant, `crop-sown-registry`, which is also the consent data controller;
* the four crop-sown images;
* sample data off, templates on;
* the ODK pull and sample crop seasons switches, both off;
* the ID generator on, with one pool, `cluster`;
* IAM registration as a regular Job, not a Helm hook;
* the platform's smoke tests on, its end-to-end tests off;
* the object store at the commons Garage (`commons-garage:3900`).

The chart has no Superset dashboards and no reporting-view Jobs. The reporting views are plain SQL views, created by db-seed.

## Platform version

The platform version is pinned in two places that must move together: `RP_VERSION` in each Dockerfile and the `openg2p-registry` dependency in `Chart.yaml`.

```bash
./scripts/bump-rp-version.sh -n          # show the newest version with both chart and images published
./scripts/bump-rp-version.sh <version>   # move both
```

`test/test_rp_pin_lockstep.py` fails the build if they differ.

## What happens on install

| Order | Job | Does |
| --- | --- | --- |
| Hook, weight 10 | `<release>-db-seed` | Waits for the APIs and for AWE. Loads the registers, activity types, indicators, ODK mapping, Cluster screens, reporting views, DCI templates and Cluster approval policies. With **Load Sample Data**, the two sample clusters |
| Hook, weight 20 | `<release>-activity-samples` | Only with **Load sample crop seasons**. Records the sample crop seasons. **Fails the release** if any cannot be loaded |
| Hook, weight 25 | `<release>-sanity` | The platform's smoke tests: the partner API is up and serves DCI search |
| Regular Job | iam-register | Registers the staff portal's roles and permissions in IAM. A failure here does not fail the release |

The seed is idempotent. On upgrade, activity types, indicators and the ODK mapping are updated in place. Cluster screens are inserted once; changes to them need an upgrade script (see [Customisation](../customisation.md#clusters)).

{% hint style="warning" %}
db-seed waits for AWE. If AWE in commons-services is down, db-seed blocks, the install times out, and the later Jobs are never created. If you see no sanity Job, check db-seed and commons-services first.
{% endhint %}

## Next

* [Deploying on Rancher](rancher.md): prerequisites, form fields, sample data, ODK, checks after install
* [Customisation](../customisation.md): what a country changes
