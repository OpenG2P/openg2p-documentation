---
description: Deployment of Apache Superset
---

# Apache Superset

### Prerequisites

* [PostgreSQL](postgresql.md)
* [Keycloak](keycloak.md) for Authentication and Sign-in to OpenSearch Dashboards

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
