---
description: Keycloak Deployment
---

# Keycloak

## Introduction

Keycloak is used in OpenG2P to provide single sign-on to some of the apps.

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* [PostgreSQL](postgresql-server.md)

## Installation

* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/keycloak](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/keycloak) directory.
*   Run:

    ```bash
    SANDBOX_HOSTNAME="openg2p.sandbox.net" \
        ./install.sh
    ```

## Post-installation

After installation is successful, Keycloak Admin console will be accessible at https://keycloak.openg2p.sandbox.net, depending on the hostname given above.
