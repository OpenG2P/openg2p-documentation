---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Performance & Scale

**SPAR** is a lightweight, high-throughput platform built on the **FastAPI** framework, ensuring rapid and efficient data processing. Designed for horizontal scalability, SPAR leverages **Kubernetes pod scaling** to dynamically adjust resources based on demand.

Performance tests demonstrate exceptional throughput, with the SPAR-mapper achieving:

* **11,000 ID resolutions per second** on a single pod (1 CPU, 2 GB RAM)
* **26,000 ID resolutions per second** with two pods
* **34,000 ID resolutions per second** with four pods

These tests were conducted using a single PostgreSQL pod (1 CPU, 1 GB RAM), underscoring the platform’s efficiency and scalability.

For comprehensive performance metrics and testing details, refer to the [**Performance Testing**](https://docs.openg2p.org/spar/development/testing/performance-testing) page under Development.
