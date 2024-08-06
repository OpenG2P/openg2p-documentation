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

# Reporting Framework

The Reporting Framework is an infrastructure to make database data available in searchable indexes for efficient slicing and dicing of data and real-time monitoring with visualization and reports. The framework utilizes open-source components to achieve this data pipeline and visualization capabilities.



{% embed url="https://miro.com/app/board/uXjVKY0ZdOQ=/?share_link_id=736231944012" %}

Postgres WAL contains events on the database, specifically, changes to any table fields. These events are read by Debezium and pushed to Kafka Topics.  Using a connector the fields are further pushed into OpenSearch indexes. These indexes may be searched by APIs or consumed by OpenSearch Dashboards for visualization.&#x20;

The salient features of the framework are the following:

<table><thead><tr><th width="323">Features</th><th>Benefits</th></tr></thead><tbody><tr><td>Searchable indexes in OpenSearch</td><td><ul><li><strong>No load on main DB</strong> esp when dataset is large and SQL queries get complex </li><li><strong>Real-time slicing and dicing</strong> of data with searchable indexes</li></ul></td></tr><tr><td>OpenSearch Dashboards</td><td><ul><li><strong>Ease</strong> of creation of dashboards and reports</li></ul></td></tr><tr><td>Authentication and authorisation using Keycloak  </td><td><ul><li><strong>Authorized access</strong> to dashboards</li><li><strong>Single sign-on</strong> with Keycloak</li></ul></td></tr><tr><td>PII data not available for search*</td><td><ul><li><strong>Privacy protection</strong></li></ul></td></tr></tbody></table>

{% hint style="info" %}
\* As a highly recommended practice PII data is not shunted to the search indexes_,_ however, the framework does not impose any restriction as such.
{% endhint %}

## Installation

Reporting framework is installed as part of modules' installation via the Helm chart that installs the modules.

## Post installation check

To ensure that all connectors are working login into Kafka UI (domain name is set during installation) and check the connectors' status.  Example:

<figure><img src="../.gitbook/assets/kafka-ui-kafka-connect.png" alt=""><figcaption></figcaption></figure>
