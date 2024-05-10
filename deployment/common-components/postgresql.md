---
description: PostgreSQL Server Deployment
---

# PostgreSQL

Postgresql server is required for all the modules. **The Helm charts of respective modules install a unique Postgresql server for each module** - this is to have a clean separation and management of modules. However, in a production setup, you may install only one Postgresql server  (in master-slave configuration) or use a Cloud-native database like Amazon RDS or Azure Postgres Service.&#x20;

The procedure below installs an instance of Postgresql using Helm charts if you wish to install Postgresql separately.

* Prerequisites:  the following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to the [kubernetes/postgresql](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/postgresql) directory.
*   Run:

    ```bash
    ./install.sh
    ```
