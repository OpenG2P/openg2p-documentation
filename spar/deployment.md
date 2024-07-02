---
description: SPAR Deployment
---

# Deployment

The instructions here pertain to the deployment of all SPAR components on the Kubernetes cluster using[ Helm charts](../deployment/helm-charts.md).  The charts install SPAR components along with the Postgresql server specific to SPAR. All the components are installed in the same namespace. The deployment may be achieved by the following methods:

* Using Rancher UI&#x20;
* Using command line

## Prerequisites

Before you deploy SPAR, make sure the following are available:

* [Base infrastructure](../deployment/base-infrastructure/)
* [eSignet](../deployment/common-components/esignet.md) (required only if SPAR Self Service API is being installed)
* [Domain name requirements](../deployment/hardware-requirements.md#dns)
* SS certificate for the domain
* Cluster Owner permission on your cluster
* Namespace in which you would be installing the module, along with [Istio namespace setup](../deployment/base-infrastructure/openg2p-cluster/cluster-setup/istio.md#namespace-setup).

## Installation using Rancher UI

1. Log in to Rancher admin console.
2. Select your cluster.
3. Under _Apps -> Repositories_ click on _Create_ to add a repository.
4. Provide _Name_ as "openg2p" and target HTTPS _Index URL_ as [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) and click _Create_.
5. Select the namespace in which you would like to install SPAR, from the namespace filter on the top-right.
6. &#x20;Navigate to _Apps->Charts_ page on Rancher. You should see OpenG2P SPAR Helm chart listed.

<div align="left">

<figure><img src="../.gitbook/assets/spar-chart-on-rancher.png" alt="" width="302"><figcaption></figcaption></figure>

</div>

6. Click on the Helm chart, select the version to be installed, and click _Install_.
7. On the next screen, choose a name for installation, like `spar`. Select the checkbox _Customise Helm options before install_, and click _Next_.
8. Go through each app's configuration page, and configure accordingly:
   1. Choose to install all requirements (on the main _Questions_ page) unless not needed specifically.
   2. Configure a hostname for each app in the following way. `<appname>.<base-hostname>` , where base hostname is the wildcard hostname chosen during [Namespace Setup](../deployment/base-infrastructure/openg2p-cluster/cluster-setup/istio.md#namespace-setup).  Example: `spar.dev.openg2p.org` and `odk.dev.openg2p.org` , etc. Refer to [DNS requirements](../deployment/hardware-requirements.md#dns-requirements) for mapping the hostname.
   3. _Keycloak Base Url_ is your organization-wide Keycloak URL, which is now done along with Rancher Installation. If not Installed along with Rancher, refer to Keycloak Installation.
   4. Create a Keycloak client in your main Keycloak, wherever OIDC Client details are asked. Refer to [Keycloak Client Creation](../deployment/deployment-guide/keycloak-client-creation.md) guide.
9. Click Next and you should be taken to the _Helm Options_ page. Make sure to disable `wait` flag on the _Helm Options_ page. Click on Install.
10. Click _Next_ and then _Install_.

## Installation using the command line

* Install the following utilities on your machine:
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* Clone the [https://github.com/openg2p/openg2p-spar-deployment](https://github.com/OpenG2P/openg2p-spar-deployment/) repo. Switch to the branch of interest.  Navigate to `deployment` directory.
*   Run.&#x20;

    ```bash
    SPAR_HOSTNAME=spar.openg2p.sandbox.net \
      NS=openg2p \
      ./install.sh
    ```

## Access links

After installation, SPAR is accessible over following URLs based on the `SPAR_HOSTNAME` given above:

* SPAR Self Service UI:  _https://spar.openg2p.sandbox.net_
* SPAR Self Service API: _https://spar.openg2p.sandbox.net/spar/v1_
* SPAR Mapper: _https://spar.openg2p.sandbox.net/mapper/v1_

## Database

Postgresql is installed as part of the above procedure in the same namespace. The default database created is `spardb` .

## Onboard SPAR on eSignet

* Create OIDC Client for SPAR in eSignet. Follow the method suggested by the ID Provider.
  * If using mock eSignet, use this API to create OIDC client.
* During OIDC client creation, you will be asked for (or given) a client ID and private key JWK as client secret.
* Edit the SPAR DB, `login_provider` table and modify the `authorization_parameters` row of the first entry, with:
  * appropriate URLs for `authorize_endpoint` , `token_endpoint` , `validate_endpoint`, `jwks_endpoint`, and `redirect_uri` fields.
  * above client ID under the `client_id` field.
  * and above private key jwk under the `client_assertion_jwk` field.
* Seed/edit metadata of banks, wallets, branches, etc for the SPAR self-service portal in database. TODO: Elaborate.

## Sanity testing

TBD
