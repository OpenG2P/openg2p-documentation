# eSignet Deployment

## Introduction

This doc provides instructions on installing eSignet on the OpenG2P cluster.

This is only required for sandbox/pilot environments. Or when eSignet is not present or is not provided by the ID Provider. If an eSignet instance is already available, OpenG2P Modules can just connect to that instance.

This doc only provides instructions to install eSignet with Mock ID System (for integration with real ID system, refer to [eSignet docs](https://docs.esignet.io)).

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* [PostgreSQL](postgresql-server.md)
* [Keycloak](keycloak-deployment.md) for API Authentication
* [Keymanager](keymanager-deployment.md)

## Installation

* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/esignet](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/esignet) directory.
*   Run:

    ```bash
    SANDBOX_HOSTNAME="openg2p.sandbox.net" \
        ./install.sh
    ```

## Post-installation

After installation is successful, eSignet can be accessed at https://esignet.openg2p.sandbox.net, depending on the hostname given above.

To seed more data of beneficiaries into the mock ID system APIs, use the APIs available at https://esignet.openg2p.sandbox.net/v1/mock-identity-system/swagger-ui/index.html.&#x20;

Or edit and use this script [https://github.com/OpenG2P/openg2p-data/blob/develop/scripts/upload\_data\_to\_mock\_esignet.py](https://github.com/OpenG2P/openg2p-data/blob/develop/scripts/upload\_data\_to\_mock\_esignet.py) to upload data. TODO: elaborate.
