---
description: Version history of the OpenG2P Approval Workflow Engine (AWE).
---

# Versions

AWE source code, Docker images, and the Helm chart all live in the single repository [`awe`](https://github.com/OpenG2P/awe), now on **GitLab**. On the `develop` branch the Helm chart version is `0.0.0-develop` and Docker images are tagged with the branch name. Tagged releases carry semantic versions on both the git tag and the published artefacts.

Since the move, images publish to the project's **GitLab Container Registry**
(`openg2p/openg2p-awe/…`) and the chart to the shared
[`openg2p-helm`](https://openg2p.github.io/openg2p-helm) catalogue. **`v1.0.0`
predates the move** — its artefacts remain on Docker Hub and the GitHub Helm repo,
and the links below still point there.

| Source / Helm Version | Runtimes | Last Modified | Comments |
| --------------------- | -------- | ------------- | -------- |
| [v1.0.0](https://github.com/OpenG2P/awe/tree/v1.0.0) | [openg2p-awe:v1.0.0](https://hub.docker.com/r/openg2p/openg2p-awe/tags)<br><br>[openg2p-awe-ui:v1.0.0](https://hub.docker.com/r/openg2p/openg2p-awe-ui/tags) | 19-Jun-2026 | First tagged release. Multi-stage approval engine with versioned policies, Keycloak-native approver resolution, signed webhook callbacks, admin UI, and Helm chart. Registry is the first caller integration. See [v1.0.0 release notes](releases/v1.0.0.md). |
| [0.0.0-develop](https://github.com/OpenG2P/awe/tree/develop) | openg2p/openg2p-awe-openg2p-awe:develop<br><br>openg2p/openg2p-awe-openg2p-awe-ui:develop | 19-Jun-2026 | In progress. Active development branch; chart and images tagged `develop`. Published to GitLab since the move. |

{% hint style="info" %}
The **Last Modified** date for in-progress (`develop` / `0.0.0-develop`) versions is updated as work continues. Released versions carry the date of their git tag.
{% endhint %}

***

## Caller deployments

AWE is deployed **per caller module** — e.g. `registry-awe` for the Registry, `pbms-awe` for PBMS. Each deployment gets its own database, Keycloak clients, and Helm release name.

For Registry integration design, see [Integration with Registry](integration-with-registry.md).
