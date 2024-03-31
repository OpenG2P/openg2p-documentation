---
description: Deployment of External Components
---

# External Components

OpenG2P utilizes several components that are not built by OpenG2P but are available in open source. These components may not be required for all modules. See the matrix below.

| Component                                         | Required for                                                               |
| ------------------------------------------------- | -------------------------------------------------------------------------- |
| [PostgreSQL](postgresql.md)                       | All modules. (A single server instance may be used housing all databases.) |
| [Keycloak](keycloak.md)                           | PBMS, Social Registry                                                      |
| [MinIO](minio.md)                                 | PBMS, GCTB                                                                 |
| [ODK Central](odk-central.md)                     | Registration Toolkit                                                       |
| [Kafka](kafka.md)                                 |  Monitoring & Reporting                                                    |
| [Logging & OpenSearch](logging-and-opensearch.md) |  Monitoring & Reporting                                                    |
| [MOSIP Key Manager](keymanager.md)                | PBMS, Social Registry, SPAR                                                |
| [e-Signet](esignet.md)                            | SPAR, PBMS, Social Registry                                                |
