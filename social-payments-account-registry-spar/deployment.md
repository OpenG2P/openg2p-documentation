---
description: SPAR Deployment
---

# Deployment

The instructions here pertain to the deployment of all SPAR components on the Kubernetes cluster.

## Prerequisites

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* This module requires kubernetes infrastructure to be setup. For details, [click here](broken-reference)
* [PostgreSQL](../deployment/common-components/postgresql.md)
* SPAR Self Service Portal needs an e-Signet instance to allow login through national ID. To install eSignet on the OpenG2P K8s cluster with mock ID system, use the [eSignet guide](../deployment/common-components/esignet.md).

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

### Onboard SPAR on eSignet

* Create OIDC Client for SPAR in eSignet. Follow the method suggested by the ID Provider.
  * If using mock eSignet, use this API to create OIDC client.
* During OIDC client creation, you will be asked for (or given) a client ID and private key JWK as client secret.
* Edit the SPAR DB, `login_provider` table and modify the `authorization_parameters` row of the first entry, with:
  * appropriate URLs for `authorize_endpoint` , `token_endpoint` , `validate_endpoint`, `jwks_endpoint`, and `redirect_uri` fields.
  * above client ID under the `client_id` field.
  * and above private key jwk under the `client_assertion_jwk` field.
* Seed/edit metadata of banks, wallets, branches, etc for the SPAR self-service portal in database. TODO: Elaborate.
