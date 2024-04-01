---
description: ODK Central Deployment
---

# ODK Central

ODK is used mainly by the Registration Toolkit to collect data offline and online.

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* [PostgreSQL](postgresql.md)

## Installation

* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/odk-central](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/odk-central) directory.
*   Run:

    ```bash
    SANDBOX_HOSTNAME="openg2p.sandbox.net" \
        ./install.sh
    ```
*   Note: The above helm chart uses the following docker images built from [https://github.com/getodk/central/tree/v2023.1.0](https://github.com/getodk/central/tree/v2023.1.0), since ODK Central doesn't provide pre-built docker images for these.

    ```
    openg2p/odk-central-backend:v2023.1.0
    openg2p/odk-central-frontend:v2023.1.0
    openg2p/odk-central-enketo:v2023.1.0
    ```

## Post-installation

After installation is successful, ODK Central will be accessible at https://odk.openg2p.sandbox.net, depending on the hostname given above.

To create the first user, do this (Subsequent users can be created through UI.):

*   Exec into the service pod, and create a user (and promote if required).

    ```bash
    kubectl exec -it <service-pod> -- odk-cmd -u <email> user-create
    kubectl exec -it <service-pod> -- odk-cmd -u <email> user-promote
    ```

