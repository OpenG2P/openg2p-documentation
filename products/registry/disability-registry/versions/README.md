---
description: Where Disability Registry releases and changelogs are published.
---

# Versions

Every version, with its changes: [Disability Registry changelog](https://openg2p.github.io/versions/disability-registry/CHANGELOG.html).

All OpenG2P components are indexed at [openg2p.github.io/versions](https://openg2p.github.io/versions/).

The Disability Registry has no frozen release yet. Only `0.0.0-develop.N` versions are published.

Every image and the Helm chart built from a commit carry the same version. A chart version tells you exactly which images it deploys.

## Two version lines

This registry's version and the platform's move independently:

* **This registry's version** — the wrapper chart and its five images, locked
  together and stamped by CI on every commit.
* **Platform version** — the `openg2p-registry` chart and images it extends,
  pinned deliberately and changed as a pair. See the
  [Registry Platform changelog](https://openg2p.github.io/versions/registry-platform/CHANGELOG.html).

How versions are derived, frozen and promoted: [Helm & Docker Versioning Strategy and CI](../../../../releases/helm-docker-versioning-and-ci/README.md).
