---
description: SPAR Deployment
---

# Deployment

SPAR deployment comprises deploying the following services on [Kubernetes cluster infrastructure](../deployment/infrastructure/).

* [SPAR Service](./#spar-service)&#x20;
* [SPAR ID Account Mapper](./#id-account-mapper)&#x20;
* [SPAR Self Service Portal](./#spar-self-service-portal) &#x20;

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* This module requires kubernetes infrastructure to be setup. For details, [click here](../deployment/infrastructure/)
* [PostgreSQL](../deployment/external-components-setup/postgresql-server-deployment.md)
* SPAR Self Service Portal needs an e-Signet instance to allow login through national ID. To install eSignet on the OpenG2P K8s cluster with mock ID system, use the [eSignet guide](../deployment/external-components-setup/esignet-deployment.md).

## Installation

* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/social-payments-account-registry](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/social-payments-account-registry) directory.
* Configure the values.yaml in this folder according to the components needed. Go over the comments to check what can be added/edited/removed.
*   Run:

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```

## Post-installation

After installation, SPAR Self Service portal will be accessible at https://spar.openg2p.sandbox.net, SPAR Service APIs will be accessible at https://spar.openg2p.sandbox.net/spar/v1, and SPAR ID Mapper APIs will be accessible at https://spar.openg2p.sandbox.net/mapper/v1, depending on the hostname given above.

Follow [SPAR Post Installation](broken-reference) Guide to finish setup.
