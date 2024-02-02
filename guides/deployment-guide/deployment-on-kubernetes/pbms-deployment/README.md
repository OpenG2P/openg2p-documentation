# PBMS Deployment

## Prerequisites

The following components are required to be present on the cluster.

* [PostgreSQL](../#postgresql) \[REQUIRED]
* [MinIO](../#minio) \[Optional]

If you want to customize the Odoo addons in your OpenG2P PBMS, create a custom-packaged PBMS docker, using [Packaging Instructions](../../packaging-openg2p-docker.md). \[Optional]

## Installation

* Navigate to [kubernetes/openg2p](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/openg2p) directory.
*   Run: (This installs the reference package dockers)

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```

    *   If use already have a custom-packaged docker image or tag use:

        ```bash
        OPENG2P_HOSTNAME=openg2p.sandbox.net \
        OPENG2P_ODOO_IMAGE_REPO=<docker image name> \
        OPENG2P_ODOO_IMAGE_TAG=<docker image tag> \
            ./install.sh
        ```
* Post-installation: Refer to [Post Install Configuration](post-install-instructions.md)
