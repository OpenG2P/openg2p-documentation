---
description: >-
  A service that generates unique, random numeric IDs for multiple consuming
  applications — based on MOSIP's UIN generator with extensions for
  multi-ID-type support.
---

# ID Generator

## Overview

The ID Generator service produces unique, random numeric IDs for applications such as social registries, farmer registries, health systems, and more. Each consuming application operates within its own **ID type**, with an independent pool of pre-generated IDs.

The service is built with **FastAPI**, uses **PostgreSQL** for storage, and is designed for **horizontal scaling on Kubernetes**.

### Key capabilities

* **Multi-ID-type support** — Each application (farmer ID, household ID, national ID, etc.) gets an independent ID pool with configurable ID length.
* **Pre-generated pool** — IDs are generated in advance and stored in PostgreSQL, ensuring fast issuance with no generation delay at request time.
* **MOSIP-compliant filters** — 10 filter rules (based on [MOSIP UIN generation filters](https://docs.mosip.io/1.2.0/id-lifecycle-management/supporting-components/commons/id-generator#uin-generation-filters)) plus Verhoeff checksum ensure ID quality.
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

## Source code

* GitHub: [https://github.com/OpenG2P/id-generator](https://github.com/OpenG2P/id-generator)

## Technology stack

| Component      | Choice                        | License                              |
| -------------- | ----------------------------- | ------------------------------------ |
| Language        | Python 3.11+                  | PSF License (permissive)             |
| Web Framework   | FastAPI                       | MIT                                  |
| ASGI Server     | Uvicorn                       | BSD-3-Clause                         |
| DB Driver       | asyncpg                       | Apache 2.0                           |
| ORM             | SQLAlchemy 2.x (async)        | MIT                                  |
| Config          | Pydantic Settings             | MIT                                  |
| Database        | PostgreSQL                    | PostgreSQL License (permissive)      |
| Deployment      | Kubernetes + Helm             | Apache 2.0                           |

All components use **permissive open-source licenses**. No copyleft (GPL) dependencies.
