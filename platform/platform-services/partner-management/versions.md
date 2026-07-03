---
description: Version history of the OpenG2P Partner Management service.
---

# Versions

Partner Management source code, Docker images, and the Helm chart all live in the single repository [`partner-management`](https://github.com/OpenG2P/partner-management). On the `develop` branch the Helm chart version is `0.0.0-develop.<run-number>` and Docker images are tagged with the branch name. Tagged releases carry semantic versions on both the git tag and the published artefacts.

<!-- MAINTAINER NOTE: When you add a NEW version row, its Comments cell must briefly
     summarise the differences/additions relative to the PREVIOUS version (not a
     full description) — e.g. "Adds AWE-gated approval; removes local self-approval."
     Keep the note terse. The oldest row keeps "Initial version. WIP." -->

| Source / Helm Version | Runtimes | Last Modified | Comments |
| --------------------- | -------- | ------------- | -------- |
| [0.0.0-develop.N](https://github.com/OpenG2P/partner-management/tree/develop) | partner-management-staff-portal-api:develop<br><br>partner-management-partner-api:develop<br><br>partner-management-staff-portal-ui:develop | 03-Jul-2026 | Initial version. WIP. |

{% hint style="info" %}
The **Last Modified** date for in-progress (`develop` / `0.0.0-develop.N`) versions is updated as work continues. Released versions carry the date of their git tag.
{% endhint %}

***

Partner Management is a single, shared platform service: all OpenG2P modules
(g2p-bridge, consent-manager, …) fetch partner public keys from the one
`partner-api`, and admins onboard partners and rotate keys through the one
staff-portal. See [Technical Architecture](technical-architecture.md) for the
component breakdown.
