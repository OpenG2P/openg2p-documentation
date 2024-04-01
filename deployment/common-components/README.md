---
description: Deployment of Common Components
---

# Common Components

Several open-source components form the base infrastructure layer utilized by the OpenG2P modules. These components need to be installed before installing OpenG2P modules.  All components may not be required for all modules. See the matrix below on applicability.

| Component                                         | Required for                                                                                   |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| [PostgreSQL](postgresql.md)                       | All modules. (A single server instance may be used housing all databases.)                     |
| [Keycloak](keycloak.md)                           | PBMS, Social Registry                                                                          |
| [MinIO](minio.md)                                 | PBMS, GCTB                                                                                     |
| [ODK Central](odk-central.md)                     | [Registration Toolkit](../../utilities-and-tools/registration-tool-kit.md)                     |
| [Kafka](kafka.md)                                 | [Real-time reporting framework](../../monitoring-and-reporting/#real-time-reporting-framework) |
| [Logging & OpenSearch](logging-and-opensearch.md) |  Monitoring & Reporting                                                                        |
| [MOSIP Key Manager](keymanager.md)                | PBMS, Social Registry, SPAR                                                                    |
| [e-Signet](esignet.md)                            | SPAR, PBMS, Social Registry                                                                    |
