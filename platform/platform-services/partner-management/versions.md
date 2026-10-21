---
description: Version history of the OpenG2P Partner Management service.
---

# Versions

Every version, with its changes: [Partner Management changelog](https://openg2p.github.io/versions/partner-management/CHANGELOG.html).

All OpenG2P components are indexed at [openg2p.github.io/versions](https://openg2p.github.io/versions/).

Partner Management source code, Docker images, and the Helm chart all live in the single repository [`partner-management`](https://github.com/OpenG2P/partner-management). The `partner-management` chart and its images (`partner-management-staff-portal-api`, `-partner-api`, `-staff-portal-ui`) carry the same version. How versions are derived: [Helm & Docker Versioning Strategy and CI](../../../releases/helm-docker-versioning-and-ci/README.md).

Partner Management is a single, shared platform service: all OpenG2P modules
(g2p-bridge, consent-manager, …) fetch partner public keys and access policies
from the one `partner-api`, and admins onboard partners, rotate keys and change
policies through the one staff-portal. See [Technical Architecture](technical-architecture.md) for the
component breakdown.
