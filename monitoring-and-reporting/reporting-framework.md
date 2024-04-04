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

The benefits of using the framework are the following:



| Features                                          | Benefits                                                                                                                                                                                           |
| ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Searchable indexes in OpenSearch                  | <ul><li><strong>No load on main DB</strong> esp when dataset is large and SQL queries get complex </li><li><strong>Real-time slicing and dicing</strong> of data with searchable indexes</li></ul> |
| OpenSearch Dashboards                             | <ul><li><strong>Ease</strong> of creation of dashboards and reports</li></ul>                                                                                                                      |
| Authentication and authorisation using Keycloak   | <ul><li><strong>Authorized access</strong> to dashboards</li><li><strong>Single sign-on</strong> with Keycloak</li></ul>                                                                           |
| PII data not available for search\*               | <ul><li><strong>Privacy protection</strong></li></ul>                                                                                                                                              |

{% hint style="info" %}
\* As a highly recommended practice PII data is not shunted to the search indexes_,_ however, the framework does not impose any restriction as such.
{% endhint %}

## Installation&#x20;

### Prerequisites

* [PostgreSQL](../deployment/common-components/postgresql.md)
* [Kafka](../deployment/common-components/kafka.md)
* [Keycloak](../deployment/common-components/keycloak.md)&#x20;
* [OpenSearch](../deployment/common-components/opensearch.md)

### Installation

* Clone the [https://github.com/openg2p/openg2p-reporting](https://github.com/openg2p/openg2p-reporting) repository, and navigate to [scripts](https://github.com/openg2p/openg2p-reporting/tree/develop/scripts) folder.
*   Run:

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```

### Post-installation

* Import Sample Dashboards from the [dashboards](https://github.com/openg2p/openg2p-reporting/tree/develop/dashboards) folder into OpenSearch Dashboards through UI.
