# External Components Setup

## Introduction

This guide provides instructions to deploy external components on the Kubernetes (K8s) cluster upon which OpenG2P components reply (Refer to [Deployment Architecture](../deployment-architecture.md)).

| Module/Component                                                                          | Comments                                                                                 |
| ----------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| [PostgreSQL](../../guides/deployment-guide/deployment-on-kubernetes/postgresql-server.md) | Required for all components. A single server instance may be used housing all databases. |
| [Keycloak](keycloak-deployment.md)                                                        | Required for PBMS, Social Registry                                                       |
| [MinIO](minio-deployment.md)                                                              | Required for PBMS and GCTB only                                                          |
| [ODK Central](odk-central-deployment.md)                                                  | Required for Registration Toolkit                                                        |
| [Kafka](kafka-deployment.md)                                                              | Required for Monitoring & Reporting                                                      |
| [Logging & OpenSearch](logging-and-opensearch-deployment.md)                              | Required for Monitoring & Reporting                                                      |
| [MOSIP Key Manager](keymanager-deployment.md)                                             | Required for PBMS, Social Registry                                                       |
| [e-Signet](e-signet-deployment.md)                                                        | Required for SPAR and optionally for PBMS                                                |
