# Reporting Deployment

## Introduction

There are two models of generating Reporting and visualizing dashboards in OpenG2P currently. One is through [Apache Superset](https://superset.apache.org/) (which performs direct SQL queries on the Database to generate reports). Second is through [reporting framework](https://github.com/openg2p/openg2p-reporting), extended from MOSIP (which replicates all the data into OpenSearch in real-time). Weigh the pros and cons of both approaches here, before choosing one model.

TODO

## Installation of Apache Superset

### Prerequisites

* [PostgreSQL](../deployment/external-components/postgresql.md)
* [Keycloak](../deployment/external-components/keycloak.md) for Authentication and Sign-in to OpenSearch Dashboards

### Installation

* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/superset](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/superset) directory.
*   Run:

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```

### Post-installation

After installation is successful, Superset can be accessed at [https://superset.openg2p.sandbox.net](https://superset.openg2p.sandbox.net), depending on the hostname given above.

Import [pre-configured dashboards](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/superset/dashboards) via Superet's console. During import provide password `postgres` user.

Follow the instructions given here to install pre-configured [dashboards](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/superset/dashboards).

## Installation of Reporting Framework

### Prerequisites

* [PostgreSQL](../deployment/external-components/postgresql.md)
* [Kafka](../deployment/external-components/kafka.md)
* [Keycloak](../deployment/external-components/keycloak.md) for Authentication and Sign-in to OpenSearch Dashboards
* [OpenSearch](../deployment/external-components/logging-and-opensearch.md)

### Installation

* Clone the [https://github.com/openg2p/openg2p-reporting](https://github.com/openg2p/openg2p-reporting) repository, and navigate to [scripts](https://github.com/openg2p/openg2p-reporting/tree/develop/scripts) folder.
*   Run:

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```

### Post-installation

* Import Sample Dashboards from the [dashboards](https://github.com/openg2p/openg2p-reporting/tree/develop/dashboards) folder into OpenSearch Dashboards through UI.
