---
description: Version history of the OpenG2P Approval Workflow Engine (AWE).
---

# Versions

AWE source code, Docker images, and the Helm chart all live in the single repository [`awe`](https://github.com/OpenG2P/awe). On the `develop` branch the published chart version is `0.0.0-develop.<run-number>` and Docker images are tagged `develop`. Tagged releases carry semantic versions on both the git tag and the published artefacts.

Images publish to Docker Hub (`openg2p/openg2p-awe`, `openg2p/openg2p-awe-ui`) and the chart to [`openg2p-helm`](https://openg2p.github.io/openg2p-helm).

<!-- MAINTAINER NOTE: When you add a NEW version row, its Comments cell must
     briefly summarise the differences/additions relative to the PREVIOUS row
     (the older row below). Keep it terse. This table is the single source of
     truth — do not duplicate it on README.md. -->

| Source / Helm Version | Runtimes | Last Modified | Comments |
| --------------------- | -------- | ------------- | -------- |
| [0.0.0-develop.90](https://github.com/OpenG2P/awe/tree/develop) | [openg2p-awe:develop](https://hub.docker.com/r/openg2p/openg2p-awe/tags)<br><br>[openg2p-awe-ui:develop](https://hub.docker.com/r/openg2p/openg2p-awe-ui/tags) | 03-Sep-2026 | In progress. **Gunicorn** replaces Uvicorn. DB pool / query-cache tuning; `openg2p-fastapi-common` `1.2.0`. |
| [1.2.2](https://github.com/OpenG2P/awe/tree/1.2.2) | [openg2p-awe:1.2.2](https://hub.docker.com/r/openg2p/openg2p-awe/tags)<br><br>[openg2p-awe-ui:1.2.2](https://hub.docker.com/r/openg2p/openg2p-awe-ui/tags) | 02-Sep-2026 | Adds PostgreSQL `pg_trgm` for trigram text search on approval tasks. |
| [1.2.1](https://github.com/OpenG2P/awe/tree/1.2.1) | [openg2p-awe:1.2.1](https://hub.docker.com/r/openg2p/openg2p-awe/tags)<br><br>[openg2p-awe-ui:1.2.1](https://hub.docker.com/r/openg2p/openg2p-awe-ui/tags) | 01-Sep-2026 | Chart image tags pinned to `1.2.1`. |
| [1.2.0](https://github.com/OpenG2P/awe/tree/1.2.0) | [openg2p-awe:1.2.0](https://hub.docker.com/r/openg2p/openg2p-awe/tags)<br><br>[openg2p-awe-ui:1.2.0](https://hub.docker.com/r/openg2p/openg2p-awe-ui/tags) | 01-Sep-2026 | Multiple Keycloak issuers (`issuer` + `additional_issuers`); configurable SSL verify; policy view in the UI; IAM registration Job for the admin SPA; `keycloak-init` `1.2.0`; indexing on ApprovalTask / ApprovalDecision. Build/publish back on GitHub. |
| [1.1.0](https://github.com/OpenG2P/awe/tree/1.1.0) | [openg2p-awe:1.1](https://hub.docker.com/r/openg2p/openg2p-awe/tags)<br><br>[openg2p-awe-ui:1.1](https://hub.docker.com/r/openg2p/openg2p-awe-ui/tags) | 17-Jul-2026 | Keycloak user-management endpoints and UI. `assignee_name` on ApprovalTask. |
| [v1.0.0](https://github.com/OpenG2P/awe/tree/v1.0.0) | [openg2p-awe:v1.0.0](https://hub.docker.com/r/openg2p/openg2p-awe/tags)<br><br>[openg2p-awe-ui:v1.0.0](https://hub.docker.com/r/openg2p/openg2p-awe-ui/tags) | 19-Jun-2026 | First tagged release. Multi-stage approval engine with versioned policies, Keycloak-native approver resolution, signed webhook callbacks, admin UI, and Helm chart. Registry is the first caller integration. See [v1.0.0 release notes](releases/v1.0.0.md). |

{% hint style="info" %}
The **Last Modified** date for in-progress (`develop` / `0.0.0-develop.N`) versions is updated as work continues. Released versions carry the date of their git tag.
{% endhint %}

***

## Caller deployments

AWE is deployed **per caller module** — e.g. `registry-awe` for the Registry, `pbms-awe` for PBMS. Each deployment gets its own database, Keycloak clients, and Helm release name.

For Registry integration design, see [Integration with Registry](integration-with-registry.md).
