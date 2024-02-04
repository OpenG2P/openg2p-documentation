# Minio Deployment

## Introduction

MinIO is used by some components of OpenG2P store documents.

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* [Keycloak](keycloak-deployment.md) for Authentication and Sign-in to UI

## Installation

* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/minio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/minio) directory.
*   Run:

    ```bash
    SANDBOX_HOSTNAME="openg2p.sandbox.net" \
        ./install.sh
    ```

## Post-installation

After installation is successful, MinIO console will be accessible at https://minio.openg2p.sandbox.net, depending on the hostname given above.

Once OpenG2P PBMS is installed, do the following:

* Navigate to OpenG2P Documents (From OpenG2P Menu) -> Document Store.
* Configure URL and password for this backend service (Like `http://minio.minio:9000`). Password and account-id/username can be obtained from the secrets in minio namespace.
