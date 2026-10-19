---
description: Software versions of the OpenG2P Master Data Service (MDS) and its changelog.
---

# Software Versions

Every version, with its changes: [Master Data Service changelog](https://openg2p.github.io/versions/master-data-service/CHANGELOG.html).

All OpenG2P components are indexed at [openg2p.github.io/versions](https://openg2p.github.io/versions/).

MDS source code, Docker images, and the Helm chart all live in the single repository [`master-data-service`](https://github.com/OpenG2P/master-data-service). The `openg2p-master-data` chart and its images carry the same version. How versions are derived: [Helm & Docker Versioning Strategy and CI](../../../releases/helm-docker-versioning-and-ci/README.md).

Images publish to Docker Hub (`openg2p/master-data-api`, `openg2p/master-data-ui`, `openg2p/master-data-db-seed`) and the chart to [`openg2p-helm`](https://openg2p.github.io/openg2p-helm).

Which version an environment runs is the one pinned in `commons-services`; see [Deployment](deployment.md).
