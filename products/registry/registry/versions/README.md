---
description: Where to find Registry Platform chart and image versions, and what changed in each.
---

# Versions

Every version, with its changes: [Registry Platform changelog](https://openg2p.github.io/versions/registry-platform/CHANGELOG.html).

All OpenG2P components are indexed at [openg2p.github.io/versions](https://openg2p.github.io/versions/).

## What is published

The Registry Platform publishes its own Docker images and Helm chart. Every image and the chart built from a commit carry the same version. A chart version tells you exactly which images it deploys.

| Artifact | Where |
|---|---|
| Helm chart `openg2p-registry` | [`openg2p-helm`](https://openg2p.github.io/openg2p-helm) |
| Docker images | Docker Hub `openg2p/openg2p-registry-<name>` |

For what these artifacts are and how a domain registry extends them, see [Deployment and Extension](../deployment-and-extension/README.md).

How versions are derived, frozen and promoted: [Helm & Docker Versioning Strategy and CI](../../../../releases/helm-docker-versioning-and-ci/README.md).

## Earlier versions

The changelog starts at 1.2.0. Earlier releases:

| Version | Date | Release notes |
|---|---|---|
| Registry Platform 1.1.0 | 06-Jul-2026 | [Release notes](registry-platform-release-notes-v1.1.0.md) |
| Registry Platform 1.0.0 | 19-Jun-2026 | [Release notes](registry-platform-release-notes-v1.0.0.md) |
| Registry 4.1.0 (legacy chart) | 08-May-2026 | [Release notes](registry-release-notes-v4.1.0.md) |
| Registry 4.0.0 (legacy chart) | 17-Apr-2026 | [Release notes](registry-release-notes-v4.0.0.md) |

Develop builds and release candidates from earlier periods are listed in the older catalogues:

| Earlier catalogue | What it holds |
|---|---|
| [GitLab catalogue](https://openg2p.gitlab.io/versions/registry-registry-platform/CHANGELOG.html) | develop builds and release candidates from the GitLab period |
| [Previous GitHub catalogue](https://openg2p.github.io/openg2p-packaging/registry-platform/CHANGELOG) | develop builds and release candidates from before that |
