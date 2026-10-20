---
description: Where Crop Sown Registry releases and changelogs are published.
---

# Versions

Every version, with its changes: [Crop Sown Registry changelog](https://openg2p.github.io/versions/crop-sown-registry/CHANGELOG.html).

All OpenG2P components are indexed at [openg2p.github.io/versions](https://openg2p.github.io/versions/).

Every image and the Helm chart built from a commit carry the same version, set by the central CI pipeline. A chart version therefore tells you exactly which images it deploys.

## Release status

The Crop Sown Registry has **no frozen release yet**. Only moving `0.0.0-develop.N` versions are published. In Rancher, tick **Show pre-release versions** to see them.

## Two version lines

| Line | What | Where to look |
| --- | --- | --- |
| **This registry** | The `openg2p-crop-sown-registry` chart and its four images (`staff-api`, `partner-api`, `celery`, `db-seed`), always at the same version | The [Crop Sown Registry changelog](https://openg2p.github.io/versions/crop-sown-registry/CHANGELOG.html) |
| **Registry platform** | The `openg2p-registry` chart and images this registry extends, pinned in the chart and the Dockerfiles together | The [Registry Platform changelog](https://openg2p.github.io/versions/registry-platform/CHANGELOG.html) |

The platform version is pinned in `Chart.yaml` and the Dockerfiles together, and moves only when it is bumped ([Domain registry charts](../../registry/deployment-and-extension/packaging-and-reference-registry.md#domain-registry-charts)).

How versions are derived, frozen and promoted: [Helm & Docker Versioning Strategy and CI](../../../../releases/helm-docker-versioning-and-ci/README.md).

## Upgrading an early install

Installs from before the Cluster ID was generated are brought up to date on upgrade by `meta_data/zz-upgrades/`: it adds the **Programme Cluster Code** field, turns on ID generation and updates the Cluster screens and search. Existing clusters keep their typed codes as Cluster IDs, since activities refer to them, and the code is also copied into the Programme Cluster Code.
