---
description: MOSIP Keymanager Deployment
---

# Keymanager

MOSIP's Keymanager component is used by some OpenG2P modules (like PBMS and social registry) to store keys and perform cryptography operations.

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* [PostgreSQL](postgresql-server.md)
* [Keycloak](keycloak.md) for API Authentication
* HSM. By default, Softhsm will be installed, unless real HSM is available.

## Installation

* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/keymanager](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/keymanager) directory.
*   Run:

    ```bash
    SANDBOX_HOSTNAME="openg2p.sandbox.net" \
        ./install.sh
    ```

## Post-installation

After installation is successful, Keymanager APIs will be accessible at https://openg2p.sandbox.net/v1/keymanager, depending on the hostname given above.
