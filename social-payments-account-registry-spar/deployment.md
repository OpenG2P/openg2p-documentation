---
description: SPAR Deployment
---

# Deployment

The instructions here pertain to the deployment of all SPAR components on the Kubernetes cluster.

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* This module requires kubernetes infrastructure to be setup. For details, [click here](../deployment/infrastructure/)
* [PostgreSQL](../deployment/external-components-setup/postgresql-server-deployment.md)
* SPAR Self Service Portal needs an e-Signet instance to allow login through national ID. To install eSignet on the OpenG2P K8s cluster with mock ID system, use the [eSignet guide](../deployment/external-components-setup/esignet-deployment.md).

## Installation

* Clone the [https://github.com/openg2p/openg2p-spar-deployment](https://github.com/OpenG2P/openg2p-spar-deployment/) repo and navigate to `scripts` directory.
* Configure the `values.yaml` in this folder according to the components needed. Go over the comments to check what can be added/edited/removed.
*   Run:

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```

## Post-installation

After installation, SPAR Self Service portal will be accessible at https://spar.openg2p.sandbox.net, SPAR Service APIs will be accessible at https://spar.openg2p.sandbox.net/spar/v1, and SPAR ID Mapper APIs will be accessible at https://spar.openg2p.sandbox.net/mapper/v1, depending on the hostname given above.

Follow [SPAR Post Installation](broken-reference) Guide to finish setup.
