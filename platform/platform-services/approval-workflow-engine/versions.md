---
description: Version history of the OpenG2P Approval Workflow Engine (AWE).
---

# Versions

Every version, with its changes: [AWE changelog](https://openg2p.github.io/versions/awe/CHANGELOG.html).

All OpenG2P components are indexed at [openg2p.github.io/versions](https://openg2p.github.io/versions/).

AWE source code, Docker images, and the Helm chart all live in the single repository [`awe`](https://github.com/OpenG2P/awe). The `openg2p-awe` chart and its images carry the same version. How versions are derived: [Helm & Docker Versioning Strategy and CI](../../../releases/helm-docker-versioning-and-ci/README.md).

Images publish to Docker Hub (`openg2p/openg2p-awe`, `openg2p/openg2p-awe-ui`) and the chart to [`openg2p-helm`](https://openg2p.github.io/openg2p-helm).

## Earlier versions

The changelog starts at 1.1.0 (17-Jul-2026). Earlier release:

| Source / Helm Version | Runtimes | Last Modified | Comments |
| --------------------- | -------- | ------------- | -------- |
| [v1.0.0](https://github.com/OpenG2P/awe/tree/v1.0.0) | [openg2p-awe:v1.0.0](https://hub.docker.com/r/openg2p/openg2p-awe/tags)<br><br>[openg2p-awe-ui:v1.0.0](https://hub.docker.com/r/openg2p/openg2p-awe-ui/tags) | 19-Jun-2026 | First tagged release. Multi-stage approval engine with versioned policies, Keycloak-native approver resolution, signed webhook callbacks, admin UI, and Helm chart. Registry is the first caller integration. See [v1.0.0 release notes](releases/v1.0.0.md). |

***

## Caller deployments

AWE is deployed **per caller module** — e.g. `registry-awe` for the Registry, `pbms-awe` for PBMS. Each deployment gets its own database, Keycloak clients, and Helm release name.

For Registry integration design, see [Integration with Registry](integration-with-registry.md).
