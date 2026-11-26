---
description: Where Agents Registry releases and changelogs are published.
---

# Versions

Every version, with its changes: [Agents Registry changelog](https://openg2p.github.io/versions/agents-registry/CHANGELOG.html).

All OpenG2P components are indexed at [openg2p.github.io/versions](https://openg2p.github.io/versions/).

Every image and the Helm chart built from a commit carry the same version, set by the central CI pipeline. A chart version therefore tells you exactly which images it deploys.

## Release status

The Agents Registry has **no frozen release yet**. Only moving `0.0.0-develop.N` versions are published (the first, `0.0.0-develop.2`, on 2026-11-23). In Rancher, tick **Show pre-release versions** to see them.

## Two version lines

| Line | What | Where to look |
| --- | --- | --- |
| **This registry** | The `openg2p-agents-registry` chart and its images (`staff-api`, `partner-api`, `celery`, `db-seed`, `agent-portal-api`, `staff-ui`, `agent-ui`), always at the same version | The [Agents Registry changelog](https://openg2p.github.io/versions/agents-registry/CHANGELOG.html) |
| **Registry platform** | The `openg2p-registry` chart and images this registry extends (`0.0.0-develop.843` at the first build), pinned in the chart and the Dockerfiles together | The [Registry Platform changelog](https://openg2p.github.io/versions/registry-platform/CHANGELOG.html) |

The platform version moves only when it is bumped, in both places at once, with `scripts/bump-rp-version.sh` ([Domain registry charts](../../../products/registry/registry/deployment-and-extension/packaging-and-reference-registry.md#domain-registry-charts)). CI fails the build if the two drift.

How versions are derived, frozen and promoted: [Helm & Docker Versioning Strategy and CI](../../../releases/helm-docker-versioning-and-ci/README.md).
