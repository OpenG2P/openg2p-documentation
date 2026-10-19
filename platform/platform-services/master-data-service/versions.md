---
description: Version history of the OpenG2P Master Data Service (MDS).
---

# Versions

Every version, with its changes: [Master Data Service changelog](https://openg2p.github.io/versions/master-data-service/CHANGELOG.html).

All OpenG2P components are indexed at [openg2p.github.io/versions](https://openg2p.github.io/versions/).

MDS source code, Docker images, and the Helm chart all live in the single repository [`master-data-service`](https://github.com/OpenG2P/master-data-service). The `openg2p-master-data` chart and its images carry the same version. How versions are derived: [Helm & Docker Versioning Strategy and CI](../../../releases/helm-docker-versioning-and-ci/README.md).

Images publish to Docker Hub (`openg2p/master-data-api`, `openg2p/master-data-ui`, `openg2p/master-data-db-seed`) and the chart to [`openg2p-helm`](https://openg2p.github.io/openg2p-helm).

## Earlier versions

The changelog starts at 1.1.0 (01-Sep-2026). Earlier develop builds:

| Source / Helm Version | Runtimes | Last Modified | Comments |
| --------------------- | -------- | ------------- | -------- |
| [0.0.0-develop.8](https://github.com/OpenG2P/master-data-service/tree/develop/deployments/charts/openg2p-master-data) | [master-data-api:develop](https://hub.docker.com/r/openg2p/master-data-api/tags) | 10-Jul-2026 | Registry-DB integration + IAM auth for geo data-policy resolution; new geo-level APIs. |
| [0.0.0-develop](https://github.com/OpenG2P/master-data-service/tree/develop/deployments/charts/openg2p-master-data) | [master-data-api:develop](https://hub.docker.com/r/openg2p/master-data-api/tags) | 15-Jun-2026 | Single consolidated repository — API, UI, chart, and seeder in one repo. |

***

MDS is deployed through the **`commons-services`** umbrella chart, not as a standalone install. The version pinned there is what an environment actually runs — see [Deployment](deployment.md).
