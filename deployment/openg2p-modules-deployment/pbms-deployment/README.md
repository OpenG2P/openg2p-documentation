# PBMS Deployment

## Introduction

OpenG2P PBMS is based on Odoo.

If you want to customize the Odoo addons in your OpenG2P PBMS, create a custom-packaged PBMS docker, using [Packaging Instructions](../../../guides/deployment-guide/packaging-openg2p-docker.md). \[Optional]

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* [PostgreSQL](../#postgresql)
* [MinIO](../#minio)

## Installation

* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/openg2p](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/openg2p) directory.
*   Run: (This installs the reference package dockers)

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```

    *   If use already have a custom-packaged docker image or tag use:

        ```bash
        SANDBOX_HOSTNAME=openg2p.sandbox.net \
        OPENG2P_ODOO_IMAGE_REPO=<docker image name> \
        OPENG2P_ODOO_IMAGE_TAG=<docker image tag> \
            ./install.sh
        ```

## Post-installation

After installation is successful, PBMS will be accessible directly at https://openg2p.sandbox.net, depending on the hostname given above.

Refer to [Post Install Configuration](post-install-instructions.md)
