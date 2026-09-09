---
description: Version history of the OpenG2P Master Data Service (MDS).
---

# Versions

MDS source code, Docker images, and the Helm chart all live in the single repository [`master-data-service`](https://github.com/OpenG2P/master-data-service). On the `develop` branch the published chart version is `0.0.0-develop.<run-number>` and Docker images are tagged `develop`. Tagged releases carry semantic versions on both the git tag and the published artefacts.

Images publish to Docker Hub (`openg2p/master-data-api`, `openg2p/master-data-ui`, `openg2p/master-data-db-seed`) and the chart to [`openg2p-helm`](https://openg2p.github.io/openg2p-helm).

<!-- MAINTAINER NOTE: When you add a NEW version row, its Comments cell must
     briefly summarise the differences/additions relative to the PREVIOUS row
     (the older row below). Keep it terse. This table is the single source of
     truth — do not duplicate it on README.md. -->

| Source / Helm Version | Runtimes | Last Modified | Comments |
| --------------------- | -------- | ------------- | -------- |
| [0.0.0-develop.69](https://github.com/OpenG2P/master-data-service/tree/develop/deployments/charts/openg2p-master-data) | [master-data-api:develop](https://hub.docker.com/r/openg2p/master-data-api/tags)<br><br>[master-data-ui:develop](https://hub.docker.com/r/openg2p/master-data-ui/tags)<br><br>[master-data-db-seed:develop](https://hub.docker.com/r/openg2p/master-data-db-seed/tags) | 01-Sep-2026 | In progress. `openg2p-fastapi-common` `1.2.0`. |
| [1.1.3](https://github.com/OpenG2P/master-data-service/tree/1.1.3/deployments/charts/openg2p-master-data) | [master-data-api:1.1.3](https://hub.docker.com/r/openg2p/master-data-api/tags)<br><br>[master-data-ui:1.1.3](https://hub.docker.com/r/openg2p/master-data-ui/tags)<br><br>[master-data-db-seed:1.1.3](https://hub.docker.com/r/openg2p/master-data-db-seed/tags) | 04-Sep-2026 | Chart and image tags pinned to `1.1.3`. |
| [1.1.2](https://github.com/OpenG2P/master-data-service/tree/1.1.2/deployments/charts/openg2p-master-data) | [master-data-api:1.1.2](https://hub.docker.com/r/openg2p/master-data-api/tags)<br><br>[master-data-ui:1.1.2](https://hub.docker.com/r/openg2p/master-data-ui/tags)<br><br>[master-data-db-seed:1.1.2](https://hub.docker.com/r/openg2p/master-data-db-seed/tags) | 04-Sep-2026 | DB connection pooling via shared `get_async_session_maker`; `openg2p-fastapi-common` `1.2.1`; `iam-core` `1.4.2`. |
| [1.1.1](https://github.com/OpenG2P/master-data-service/tree/1.1.1/deployments/charts/openg2p-master-data) | [master-data-api:1.1.1](https://hub.docker.com/r/openg2p/master-data-api/tags)<br><br>[master-data-ui:1.1.1](https://hub.docker.com/r/openg2p/master-data-ui/tags)<br><br>[master-data-db-seed:1.1.1](https://hub.docker.com/r/openg2p/master-data-db-seed/tags) | 03-Sep-2026 | Geo endpoints added to CSRF-excluded paths for registry ↔ MDS server-to-server validation calls. |
| [1.1.0](https://github.com/OpenG2P/master-data-service/tree/1.1.0/deployments/charts/openg2p-master-data) | [master-data-api:1.1.0](https://hub.docker.com/r/openg2p/master-data-api/tags)<br><br>[master-data-ui:1.1.0](https://hub.docker.com/r/openg2p/master-data-ui/tags)<br><br>[master-data-db-seed:1.1.0](https://hub.docker.com/r/openg2p/master-data-db-seed/tags) | 01-Sep-2026 | First tagged 1.1 release. Master Data API + UI + geo seeder; geo hierarchy with data-policy support; country-pack seeding; `get_all_g2p_geo_levels` API. |
| [0.0.0-develop.8](https://github.com/OpenG2P/master-data-service/tree/develop/deployments/charts/openg2p-master-data) | [master-data-api:develop](https://hub.docker.com/r/openg2p/master-data-api/tags) | 10-Jul-2026 | Registry-DB integration + IAM auth for geo data-policy resolution; new geo-level APIs. |
| [0.0.0-develop](https://github.com/OpenG2P/master-data-service/tree/develop/deployments/charts/openg2p-master-data) | [master-data-api:develop](https://hub.docker.com/r/openg2p/master-data-api/tags) | 15-Jun-2026 | Single consolidated repository — API, UI, chart, and seeder in one repo. |

{% hint style="info" %}
The **Last Modified** date for in-progress (`develop` / `0.0.0-develop.N`) versions is updated as work continues. Released versions carry the date of their git tag.
{% endhint %}

***

MDS is deployed through the **`commons-services`** umbrella chart, not as a standalone install. The version pinned there is what an environment actually runs — see [Deployment](README.md#deployment).
