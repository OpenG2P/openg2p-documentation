---
description: >-
  A service that generates unique, random numeric IDs for multiple consuming
  applications with pre-generated pools, Verhoeff checksum, and multi-ID-type
  support.
---

# ID Generator

## Overview

The ID Generator service produces unique, random numeric IDs for applications such as social registries, farmer registries, health systems, and more. Each consuming application operates within its own **ID type**, with an independent pool of pre-generated IDs.

The service is built with **FastAPI**, uses **PostgreSQL** for storage, and is designed for **horizontal scaling on Kubernetes**.

### Key capabilities

* **Multi-ID-type support** — Each application (farmer ID, household ID, national ID, etc.) gets an independent ID pool with configurable ID length.
* **Pre-generated pool** — IDs are generated in advance and stored in PostgreSQL, ensuring fast issuance with no generation delay at request time.
* **10 filter rules** — Comprehensive ID quality filters (inspired by [MOSIP UIN generation filters](https://docs.mosip.io/1.2.0/id-lifecycle-management/supporting-components/commons/id-generator#uin-generation-filters)) plus Verhoeff checksum ensure ID quality.
* **Kubernetes-native** — Horizontally scalable with zero-contention ID issuance and coordinated pool replenishment across pods.
* **Structural validation** — Downstream systems can validate any ID without a database lookup.

### How it works

```
1. On startup → create tables, fill ID pools to minimum threshold
2. On request → atomically issue one pre-generated ID (AVAILABLE → TAKEN)
3. In background → monitor pool levels, replenish when low
```

### ID lifecycle

IDs follow a simple two-state model:

```
AVAILABLE  →  TAKEN
```

* **AVAILABLE** — In pool, ready to be issued.
* **TAKEN** — Issued to a caller; permanently consumed. Never re-issued.

## Detailed documentation

| Page                                                      | Description                                                                                      |
| --------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| [Functional Specifications](functional-specifications.md) | ID types, generation rules, 10 filter rules, pool management, exhaustion handling, configuration |
| [API Reference](api-reference.md)                         | REST API endpoints, request/response formats, error codes, OpenAPI spec                          |
| [Technical Architecture](technical-architecture.md)       | Async stack, database design, concurrency patterns, Kubernetes deployment                        |
| [Deployment](deployment.md)                               | Helm chart installation, Docker setup, local development, environment variables                  |
| [Testing](testing.md)                                     | Test categories, execution commands, HTML reporting                                              |

## Versions

| Helm Chart Version                                                 | Docker Image                           | Date        | Comments       |
| ------------------------------------------------------------------ | -------------------------------------- | ----------- | -------------- |
| [1.0.0](https://github.com/OpenG2P/id-generator/tree/1.0.0)        | `openg2p/openg2p-id-generator:1.0.0`   | 2026-04-17  | Stable version |
| [1.0](https://github.com/OpenG2P/id-generator/tree/1.0)            | `openg2p/openg2p-id-generator:1.0`     | in progress | Moving version |
| [0.0.0-develop](https://github.com/OpenG2P/id-generator/tree/main) | `openg2p/openg2p-id-generator:develop` | in progress | —              |

## Source code

* GitHub: [https://github.com/OpenG2P/id-generator](https://github.com/OpenG2P/id-generator)

## Technology stack

| Component     | Choice                 | License                         |
| ------------- | ---------------------- | ------------------------------- |
| Language      | Python 3.11+           | PSF License (permissive)        |
| Web Framework | FastAPI                | MIT                             |
| ASGI Server   | Uvicorn                | BSD-3-Clause                    |
| DB Driver     | asyncpg                | Apache 2.0                      |
| ORM           | SQLAlchemy 2.x (async) | MIT                             |
| Config        | Pydantic Settings      | MIT                             |
| Database      | PostgreSQL             | PostgreSQL License (permissive) |
| Deployment    | Kubernetes + Helm      | Apache 2.0                      |

All components use **permissive open-source licenses**. No copyleft (GPL) dependencies.
