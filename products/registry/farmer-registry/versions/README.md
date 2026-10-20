---
description: Where to find Farmer Registry chart and image versions, and what changed in each.
---

# Versions

Every version, with its changes: [Farmer Registry changelog](https://openg2p.github.io/versions/farmer-registry/CHANGELOG.html).

All OpenG2P components are indexed at [openg2p.github.io/versions](https://openg2p.github.io/versions/).

## What is published

The Farmer Registry publishes its own Docker images and Helm chart. Every image and the chart built from a commit carry the same version. A chart version tells you exactly which images it deploys.

| Artifact | Where |
|---|---|
| Helm chart `openg2p-farmer-registry` | [`openg2p-helm`](https://openg2p.github.io/openg2p-helm) |
| Docker images | Docker Hub `openg2p/openg2p-farmer-registry-<name>`: `staff-api`, `partner-api`, `celery`, `db-seed`, `sanity-tests`, `agent-portal-api` |

## The two version lines

This registry's chart and images share one version. The platform version it extends moves separately, only when it is bumped ([Domain registry charts](../../registry/deployment-and-extension/packaging-and-reference-registry.md#domain-registry-charts)). Platform changes: [Registry Platform changelog](https://openg2p.github.io/versions/registry-platform/CHANGELOG.html).

How versions are derived, frozen and promoted: [Helm & Docker Versioning Strategy and CI](../../../../releases/helm-docker-versioning-and-ci/README.md).

## Earlier versions

The changelog lists every release. Develop builds and release candidates from earlier periods are listed in the older catalogues:

| Earlier catalogue | What it holds |
|---|---|
| [GitLab catalogue](https://openg2p.gitlab.io/versions/registry-farmer-registry/CHANGELOG.html) | develop builds and release candidates from the GitLab period |
| [previous GitHub catalogue](https://openg2p.github.io/openg2p-packaging/farmer-registry/CHANGELOG) | develop builds and release candidates from before that |
