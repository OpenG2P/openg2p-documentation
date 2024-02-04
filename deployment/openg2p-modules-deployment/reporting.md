# Reporting

## Introduction

There are two models of generating Reporting and visualizing dashboards in OpenG2P currently. One is through [Apache Superset](https://superset.apache.org/) (which performs direct SQL queries on the Database to generate reports). Second is through [reporting framework](https://github.com/openg2p/openg2p-reporting), extended from MOSIP (which replicates all the data into OpenSearch in real-time). Weigh the pros and cons of both approaches here, before choosing one model.

TODO

## Installation using Superset

WIP

### Prerequisites

* [PostgreSQL](../external-components-setup/postgresql-server-deployment.md)
* [Keycloak](../external-components-setup/keycloak-deployment.md) for Authentication and Sign-in to OpenSearch Dashboards

### Installation

* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/superset](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/superset) directory.
*   Run:

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```

### Post-installation

After installation is successful, Superset can be accessed at https://superset.openg2p.sandbox.net, depending on the hostname given above.

Follow instructions given here to install sample [dashboards](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/superset/dashboards).

## Installation using Reporting Framework

WIP

### Prerequisites

* [PostgreSQL](../external-components-setup/postgresql-server-deployment.md)
* [Kafka](../external-components-setup/kafka-deployment.md)
* [Keycloak](../external-components-setup/keycloak-deployment.md) for Authentication and Sign-in to OpenSearch Dashboards
* [OpenSearch](../external-components-setup/logging-and-opensearch-deployment.md)

### Installation

* Clone the [https://github.com/openg2p/openg2p-reporting](https://github.com/openg2p/openg2p-reporting) repository, and navigate to [scripts](https://github.com/openg2p/openg2p-reporting/tree/develop/scripts) folder.
*   Run:

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```

### Post-installation

* Import Sample Dashboards from [dashboards](https://github.com/openg2p/openg2p-reporting/tree/develop/dashboards) folder into OpenSearch Dashboards through UI.
