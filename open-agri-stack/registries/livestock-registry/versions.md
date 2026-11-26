---
description: Where Livestock Registry releases and changelogs are published.
---

# Versions

Every version, with its changes: [Livestock Registry changelog](https://openg2p.github.io/versions/live-stock-registry/CHANGELOG.html).

All OpenG2P components are indexed at [openg2p.github.io/versions](https://openg2p.github.io/versions/).

Every image and the Helm chart built from a commit carry the same version, set by the central CI pipeline. A chart version therefore tells you exactly which images it deploys.

## Release status

The Livestock Registry has **no frozen release yet**. Only moving `0.0.0-develop.N` versions are published. In Rancher, tick **Show pre-release versions** to see them.

## Two version lines

| Line | What | Where to look |
| --- | --- | --- |
| **This registry** | The `openg2p-livestock-registry` chart and its five images (`staff-api`, `partner-api`, `celery`, `db-seed`, `staff-ui`), always at the same version | The [Livestock Registry changelog](https://openg2p.github.io/versions/live-stock-registry/CHANGELOG.html) |
| **Registry platform** | The `openg2p-registry` chart and images this registry extends, pinned in the chart and the Dockerfiles together | The [Registry Platform changelog](https://openg2p.github.io/versions/registry-platform/CHANGELOG.html) |

The platform version moves only when it is bumped, in both places at once, with `scripts/bump-rp-version.sh` ([Domain registry charts](../../../products/registry/registry/deployment-and-extension/packaging-and-reference-registry.md#domain-registry-charts)). CI fails the build if the two drift.

The search of a farmer's animals under consent needs a Registry Platform with per-register consent subject fields (`REGISTRY_PARTNER_API_DCI_CONSENT_SUBJECT_FIELDS`); on an older platform such a search is refused.

How versions are derived, frozen and promoted: [Helm & Docker Versioning Strategy and CI](../../../releases/helm-docker-versioning-and-ci/README.md).
