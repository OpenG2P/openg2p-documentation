---
description: PostgreSQL Server Deployment
---

# PostgreSQL Server

This guide provides instructions to install PostgreSQL Server on the Kubernetes cluster. However, if you already have PostgreSQL server installed, or are using Cloud hosted Postgres, then you may skip the server installation. The instructions to initialize OpenG2P component databases are provided as part of the component installation instructions.

## Databases

Module/component-wise listing of databases is given below

<table><thead><tr><th width="349">Module/Component</th><th>Database Name</th></tr></thead><tbody><tr><td>PBMS</td><td><code>openg2pdb</code></td></tr><tr><td>Keycloak</td><td><code>keycloakdb</code></td></tr><tr><td>ODK</td><td><code>odkdb</code></td></tr><tr><td>SPAR</td><td><code>spardb</code></td></tr><tr><td>G2P Cash Transfer Bridge</td><td><code>gctbdb</code></td></tr><tr><td>MOSIP Key Manager</td><td><code>mosip_keymgr</code></td></tr></tbody></table>

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.

## Installation

* Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/openg2p/openg2p-deployment) repo and navigate to [kubernetes/postgresql](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/postgresql) directory.
*   Run:

    ```bash
    ./install.sh
    ```
