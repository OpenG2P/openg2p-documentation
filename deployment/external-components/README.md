---
description: Deployment of External Components
---

# External Components

This guide provides instructions to deploy external components on the Kubernetes (K8s) cluster upon which OpenG2P components rely (Refer to [Deployment Architecture](broken-reference)).

<table data-full-width="false"><thead><tr><th width="220">Module/Component</th><th width="52">All</th><th width="82">PBMS</th><th width="145" align="center">Social Registry</th><th width="79">GCTB</th><th width="162">Registration Toolkit</th><th>Monitoring and Re</th><th>SPAR</th></tr></thead><tbody><tr><td><a href="postgresql-server.md">PostgreSQL</a></td><td></td><td></td><td align="center"></td><td></td><td></td><td></td><td></td></tr><tr><td><a href="keycloak.md">Keycloak</a></td><td></td><td></td><td align="center"></td><td></td><td></td><td></td><td></td></tr><tr><td><a href="minio.md">MinIO</a></td><td></td><td></td><td align="center"></td><td></td><td></td><td></td><td></td></tr><tr><td><a href="odk-central-deployment.md">ODK Central</a></td><td></td><td></td><td align="center"></td><td></td><td></td><td></td><td></td></tr><tr><td><a href="kafka-deployment.md">Kafka</a></td><td></td><td></td><td align="center"></td><td></td><td></td><td></td><td></td></tr><tr><td><a href="logging-and-opensearch.md">Logging &#x26; OpenSearch</a></td><td></td><td></td><td align="center"></td><td></td><td></td><td></td><td></td></tr><tr><td><a href="keymanager.md">MOSIP Key Manager</a></td><td></td><td></td><td align="center"></td><td></td><td></td><td></td><td></td></tr><tr><td><a href="esignet.md">e-Signet</a></td><td></td><td></td><td align="center"></td><td></td><td></td><td></td><td></td></tr></tbody></table>

| Module/Component                                  | Comments                                                                                 |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| [PostgreSQL](postgresql-server.md)                | Required for all components. A single server instance may be used housing all databases. |
| [Keycloak](keycloak.md)                           | Required for PBMS, Social Registry                                                       |
| [MinIO](minio.md)                                 | Required for PBMS and GCTB only                                                          |
| [ODK Central](odk-central-deployment.md)          | Required for Registration Toolkit                                                        |
| [Kafka](kafka-deployment.md)                      | Required for Monitoring & Reporting                                                      |
| [Logging & OpenSearch](logging-and-opensearch.md) | Required for Monitoring & Reporting                                                      |
| [MOSIP Key Manager](keymanager.md)                | Required for PBMS, Social Registry                                                       |
| [e-Signet](esignet.md)                            | Required for SPAR and optionally for PBMS                                                |
