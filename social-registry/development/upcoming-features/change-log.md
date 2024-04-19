---
description: WORK IN PROGRESS
---

# Change Log

Changes to specific fields by admin/operators/end-users must be logged in the system for query as well as auditing

## Logging methods

### Log files

This is a simple method where the Python logging module is used to write event logs in JSON format in log files directly.  These log files are shunted to OpenSearch for indexing, searching and querying. See System Logs under Monitoring and Reporting for further details on this data pipeline.

### Changed field records in OpenSearch

Reporting infrastructure may be harnessed to record all changes in DB fields and shunted them to OpenSearch for indexing, searching and querying.  See details on reporting infrastructure [here](../../functionality/monitoring-and-reporting/).

### Design

Change log can be build using the Odoo OCA package [Audit Log](https://github.com/OCA/server-tools/tree/16.0/auditlog). This would be set of changes in any field(s) for the registry.

### Multiple versions of data

Multiple version of a person's record might come in the following scenarios

* Change in field value
* New updated record coming in for the person which would be termed as a named version (typically surveys)
* Feedback call from the connected applications

**Proposed solution:** Utilizing Elasticsearch as the backbone, we aim to implement a robust solution for managing multiple versions efficiently. Below are the key technology components and strategies discussed:

* **Debezium configuration:** Debezium will be configured to capture real-time changes from the database's Write-Ahead Logs (WALs), ensuring that any modifications or additions to the data are promptly recorded.
* **Elasticsearch setup:** Elasticsearch will serve as the primary destination for streaming the captured changes. Leveraging its indexing capabilities, Elasticsearch will efficiently organize and store the data, facilitating quick retrieval and analysis.
* **Indexing strategy:** An indexing strategy will be devised to optimize the storage and retrieval of captured data. This strategy will accommodate multiple versions of records, ensuring that historical data remains accessible and searchable.
* **Authorization implementation:** Authorization mechanisms will be implemented within Elasticsearch. This will control access to the API endpoints, ensuring that only authorized users can interact with the data.&#x20;
* **API Endpoints configuration:** API endpoints will be configured in Elasticsearch to expose the captured data to authorized users. These endpoints will provide seamless access to multiple versions of records, enabling users to retrieve and analyze data as needed. Client should be in a position to fetch based on named version or any other parameter like timeframe.
