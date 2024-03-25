---
description: WORK IN PROGRESS
---

# Change Log

Changes to specific fields by admin/operators/end-users must be logged in the system for query as well as auditing

## Logging methods

### Log files

This is a simple method where the Python logging module is used to write event logs in JSON format in log files directly.  These log files are shunted to OpenSearch for indexing, searching and querying. See System Logs under Monitoring and Reporting for further details on this data pipeline.

### Changed field records in OpenSearch

Reporting infrastructure may be harnessed to record all changes in DB fields and shunted them to OpenSearch for indexing, searching and querying.  See details on reporting infrastructure [here](../../monitoring-and-reporting/).
