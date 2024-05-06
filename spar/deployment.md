---
description: SPAR Deployment
---

# Deployment

The instructions here pertain to the deployment of all SPAR components on the Kubernetes cluster using Helm charts. The Helm charts may be installed with the following methods:

* Using Rancher UI&#x20;
* Using command line

## Installation from Rancher UI

Make sure you have the Cluster Owner permission to your Kubernetes cluster&#x20;

1. Logging to Rancher admin console
2. Select your cluster
3. Under _Apps -> Repositories_ click on _Create_ to add a repository.
4. Provide _Name_ as "openg2p" and target HTTPS _Index URL_ as [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) and click on _Create_.
5. &#x20;Navigate to _Apps->Charts_ page. You should see OpenG2P SPAR Helm chart

<div align="left">

<figure><img src="../.gitbook/assets/spar-chart-on-rancher.png" alt="" width="302"><figcaption></figcaption></figure>

</div>

6. Click on the helm chart, select the version to be installed and click on _Install_.
7. Select the namespace in which you would like the chart to be installed (you will need to create a namespace upfront if it does not already exist) and select the checkbox _Customise Helm options before install._
8. Provide _Global Hostname_ of the installation. Refer to [DNS requirements](../deployment/hardware-requirements.md#dns-requirements) for mapping the hostname.
9. Select the components to be installed and the eSignet base URL. The latter is required only if you are installing SPAR Self Service API. &#x20;
10. Click on _Next_ and then _Install_.  &#x20;

## Installation using the command line

* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* This module requires kubernetes infrastructure to be setup. For details, [click here](broken-reference)
* [PostgreSQL](../deployment/common-components/postgresql.md)
* SPAR Self Service Portal needs an e-Signet instance to allow login through national ID. To install eSignet on the OpenG2P K8s cluster with mock ID system, use the [eSignet guide](../deployment/common-components/esignet.md).

### Installation

* Clone the [https://github.com/openg2p/openg2p-spar-deployment](https://github.com/OpenG2P/openg2p-spar-deployment/) repo and navigate to `scripts` directory.
* Configure the `values.yaml` in this folder according to the components needed. Go over the comments to check what can be added/edited/removed.
*   Run:

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```

## Post-installation

After installation, SPAR Self Service portal will be accessible at https://spar.openg2p.sandbox.net, SPAR Service APIs will be accessible at https://spar.openg2p.sandbox.net/spar/v1, and SPAR ID Mapper APIs will be accessible at https://spar.openg2p.sandbox.net/mapper/v1, depending on the hostname given above.

## Onboard SPAR on eSignet

* Create OIDC Client for SPAR in eSignet. Follow the method suggested by the ID Provider.
  * If using mock eSignet, use this API to create OIDC client.
* During OIDC client creation, you will be asked for (or given) a client ID and private key JWK as client secret.
* Edit the SPAR DB, `login_provider` table and modify the `authorization_parameters` row of the first entry, with:
  * appropriate URLs for `authorize_endpoint` , `token_endpoint` , `validate_endpoint`, `jwks_endpoint`, and `redirect_uri` fields.
  * above client ID under the `client_id` field.
  * and above private key jwk under the `client_assertion_jwk` field.
* Seed/edit metadata of banks, wallets, branches, etc for the SPAR self-service portal in database. TODO: Elaborate.
