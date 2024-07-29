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

# System Logging

**System logs** generated across all components can be monitored via the logging pipeline shown below. The logs can be searched, sliced and diced for analytics.  **Fluentd** and **OpenSearch** are used to collect, parse, display and search logs.

## Logging pipeline

{% embed url="https://miro.com/app/board/uXjVKZsLZhk=/?share_link_id=963470704519" %}
Logging Pipeline
{% endembed %}

## Log files

This is a simple method where the Python logging module is used to write system event logs in JSON or other format  in log files directly.  These log files are shunted to OpenSearch for indexing, searching and querying. See System Logs under Monitoring and Reporting for further details on this data pipeline.

## Dashboards

Several dashboards can be created using [OpenSearch Dashboards](https://opensearch.org/docs/latest/dashboards/). Some default dashboards are provided by OpenG2P and may be customized.

<figure><img src="../.gitbook/assets/opensearch-log-dashboard.png" alt=""><figcaption></figcaption></figure>

## Installation

Refer to [Deployment->Fluentd & Opensearch](../deployment/base-infrastructure/openg2p-cluster/fluentd-and-opensearch/).
