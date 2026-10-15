---
description: IAM Service Versions
---

# Versions

Every version, with its changes: [IAM changelog](https://openg2p.github.io/versions/iam/CHANGELOG.html).

All OpenG2P components are indexed at [openg2p.github.io/versions](https://openg2p.github.io/versions/).

Source, images, and the Helm chart live in [`iam`](https://github.com/OpenG2P/iam) (the former `iam-service` repository is archived). The `openg2p-iam-service` chart and its images (`iam-staff-portal-api`, `iam-agent-portal-api`, `iam-staff-ui`) carry the same version. How versions are derived: [Helm & Docker Versioning Strategy and CI](../../../releases/helm-docker-versioning-and-ci/README.md).

## Earlier versions

The changelog starts at 1.4.0 (01-Sep-2026). Earlier releases:

<table><thead><tr><th width="123.34967041015625">Helm version</th><th width="247.93975830078125">IAM Runtime Versions</th><th width="133.2740478515625">Last modified</th><th>Description</th></tr></thead><tbody>
<tr><td><a href="https://github.com/OpenG2P/iam/tree/v1.3.0/deployments/charts/openg2p-iam-service">v1.3.0</a></td><td><a href="https://hub.docker.com/r/openg2p/iam-staff-portal-api/tags">iam-staff-portal-api:1.3.0</a></td><td>17-Jul-2026</td><td><ol><li>Refresh tokens persisted in Redis with auto-refresh in middleware; logout + configurable refresh TTL</li><li>CSRF protection for authenticated requests</li><li><code>DataPolicyMiddleware</code> and data-policy role helpers</li><li>Staff portal app-registration auth/CSRF fixes; operational roles for register metadata and reference data</li></ol></td></tr>
<tr><td><a href="https://github.com/OpenG2P/iam/tree/v1.2.1">v1.2.1</a></td><td><a href="https://hub.docker.com/layers/openg2p/iam-staff-portal-api/1.2.1/images/sha256-d99f2cec33e9cf48b4c01e318b69df0e84116204c29d53121f96ffa3a56b1b74">iam-staff-portal-api:v1.2.1</a></td><td>19-Jun-2026</td><td><ol><li>Auth middleware fix — <code>AuthMiddleware</code> now correctly resolves nested FastAPI routes (needed for FastAPI 0.137+), so permission checks hit the right endpoint handler</li><li>Dependency bump — <code>openg2p-fastapi-common</code> updated from <code>v1.1.6</code> → <code>v1.1.7</code> in Dockerfiles, CI workflows, and Helm chart</li></ol></td></tr>
<tr><td><a href="https://github.com/OpenG2P/iam/tree/v1.2.0">v1.2.0</a></td><td><a href="https://hub.docker.com/layers/openg2p/iam-staff-portal-api/1.2.0/images/sha256-2e7810ef82a501e9a581a24ff037d08663a0a230c488c9a83a1adeded5da1bbd">iam-staff-portal-api:v1.2.0</a></td><td>15-Jun-2026</td><td><ol><li>Added Auth verify as optional parameter</li><li>Restructured the codebase and deployment</li></ol></td></tr>
<tr><td><a href="https://github.com/OpenG2P/openg2p-iam-service-deployment/tree/1.0.0">1.1.0</a></td><td><a href="https://hub.docker.com/layers/openg2p/iam-staff-portal-api/1.0.1/images/sha256-47a7dff1ba5c12f214c920d22b89f1901a141e714995db4aa46fe38f3d927059">iam-staff-portal-api:v1.1.0</a></td><td>08-May-2026</td><td><ol><li>Removed user_type and all the business logic depending on it</li><li>Improvement in middleware handling</li><li>OIDC specification refinement</li></ol></td></tr>
<tr><td><a href="https://github.com/OpenG2P/openg2p-iam-service-deployment/tree/1.0.0">1.0.0</a></td><td><a href="https://hub.docker.com/layers/openg2p/iam-staff-portal-api/1.0.1/images/sha256-47a7dff1ba5c12f214c920d22b89f1901a141e714995db4aa46fe38f3d927059">iam-staff-portal-api:v1.0.1</a></td><td>17-Apr-2026</td><td><ol><li>IAM Staff Portal API - gateway for Staff Login using the Staff Portal - Interfaces with ID Providers for Token issuance and validation</li><li>Bug fixes as part of QA<br></li></ol></td></tr>
</tbody></table>
