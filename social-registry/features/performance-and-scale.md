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

The **Social Registry** is designed to efficiently handle millions of records, ensuring seamless scalability and performance. At its core, the platform leverages **PostgreSQL** with optimized indexing strategies to maintain high-speed data processing without degradation.

To enhance efficiency, the system utilizes an asynchronous background processing framework powered by **Celery**, which operates independently of the **Odoo** platform. This decoupled architecture enables scalable background job execution using **Kubernetes** pod scaling, ensuring optimal resource utilization. Critical tasks such as unique ID generation, PMT score calculation, and deduplicatio**n** are managed through this robust framework.

**Optimized Search and Data Synchronization**

In addition to PostgreSQL, the registry maintains a synchronized copy of its records in **OpenSearch** for enhanced search performance. Updates to the registry are seamlessly streamed from PostgreSQL **Write-Ahead Logs (WAL)** into OpenSearch via **Kafka**, leveraging the [**OpenG2P reporting framework**](https://docs.openg2p.org/monitoring-and-reporting/reporting-framework). This approach ensures real-time data consistency while enabling faster and more efficient search capabilities compared to PostgreSQL.

For in-depth insights into system performance and benchmarking, refer to the [**Performance Testing**](https://docs.openg2p.org/social-registry/developer-zone/performance-testing) section in the Developer Zone.
