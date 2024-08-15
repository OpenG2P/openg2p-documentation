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

Refer to [Installation Guide and Post Installation Check](user-guides/installation-and-troubleshooting.md).

## Accessing OpenSearch dashboards

* Pick the URL provided during the installation of the Helm chart of the module (like SR, PBMS)
* Add Keycloak roles to the user who is accessing the dashboard (as given [here](user-guides/installation-and-troubleshooting.md#assigning-roles-to-users)).
* Confirm that the number of indexed records in OpenSearch matches the number of rows in the DB (_guide TBD_). This check confirms that the reporting pipeline is working fine.

## Creating dashboards

* [Create connectors](user-guides/connector-creation-guide.md).
* [Create Dashboards](user-guides/dashboards-creation-guide.md).
