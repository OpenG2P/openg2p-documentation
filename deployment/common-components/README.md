---
description: Deployment of Common Components
---

# Common Components

Several open-source components are installed over the base infrastructure layer that is utilized by the OpenG2P modules. These components need to be installed before installing OpenG2P modules.  All components may not be required for all modules. See the table below on applicability.

| Component                                                                 | Required for                                                                             |
| ------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| [PostgreSQL](postgresql.md)                                               | All modules. (A single server instance may house all databases.)                         |
| [Keycloak](keycloak.md)                                                   | [PBMS](../../pbms/), Social Registry                                                     |
| [MinIO](minio.md)                                                         | PBMS, [G2P Bridge](../../g2p-bridge/)                                                    |
| [ODK Central](odk-central.md)                                             | [Registration Toolkit](../../utilities-and-tools/registration-tool-kit.md)               |
| [Kafka](kafka.md)                                                         | [Reporting Framework](../../monitoring-and-reporting/reporting-framework.md)             |
| [OpenSearch](../base-infrastructure/fluentd-and-opensearch/opensearch.md) | Logging and [Reporting Framework](../../monitoring-and-reporting/reporting-framework.md) |
| [MOSIP Key Manager](keymanager.md)                                        | PBMS, Social Registry, [SPAR](../../spar/)                                               |
| [e-Signet](esignet.md)                                                    | SPAR, PBMS, Social Registry                                                              |
| [Apache Superset](apache-superset.md)                                     | [Reporting dashboards](../../monitoring-and-reporting/apache-superset.md)                |
| [Fluentd](../base-infrastructure/fluentd-and-opensearch/fluentd.md)       | [Logging](../../pbms/monitoring-and-reporting/logging.md)                                |
| [Debezium](debezium.md)                                                   | [Reporting Framework](../../monitoring-and-reporting/reporting-framework.md)             |
