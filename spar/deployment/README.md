---
description: SPAR Deployment
---

# Deployment

The instructions here pertain to the deployment of all SPAR components on the Kubernetes cluster using [Helm charts](https://docs.openg2p.org/spar/deployment/helm-charts).  The charts install SPAR components along with the Postgresql server specific to SPAR. All the components are installed in the same namespace. The deployment may be achieved by the following methods:

* [Using Rancher UI ](./#installation-using-rancher-ui)
* [Using command line](./#installation-using-the-command-line)

## Prerequisites

Before you deploy, make sure the following are in place:

* ✅ **Kubernetes cluster** is up and running
* ✅ **Nginx server is configured** (skip this for OpenG2P-in-a-box)
* ✅ **Namespace is created** (via Rancher under a Project)
* ✅ **Project Owner access** on the OpenG2P namespace
* ✅ **Istio gateway** is set up in the namespace

## Installation using Rancher UI

1. Log in to Rancher admin console.
2. Select your cluster.
3. Under **Apps -> Repositories** click the **Create** to add a repository.
4. Provide **Name** as "openg2p" and target HTTPS **Index** **URL** as [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) and click on **Create**.
5. Select the namespace in which you would like to install PBMS, from the namespace filter on the top-right.
6. To display prerelease versions of OpenG2P apps, click on your user avatar in the upper right corner of the Rancher dashboard. Then click on **Include Prerelease Versions** under **Preferences** below the **Helm Charts**.
7. Navigate to **Apps->Charts** page on Rancher. You can find the **OpenG2P SPAR** is listed in the dashboard.\
   ![](<../../.gitbook/assets/image (74).png>)
8. Click on the Helm chart, select the version to be installed, and click **Install**.
9. On the next screen, choose a name for installation, like `spar`. Select the checkbox **Customise Helm** before the installation, and then click on **Next**.
10. Navigate to each app's configuration page, and configure the following:
    1. Configure a hostname for each app in the following way. `<appname>.<base-hostname>` , where base hostname is the wildcard hostname chosen during [Istio namespace setup](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/cluster-setup/istio#namespace-setup). Example: `spar.dev.openg2p.org`  etc. `<appname>` is arbitrary - default names have been provided.
    2. **Keycloak Base Url** is your organization-wide Keycloak URL. (Ex: keycloak.\<your domain>.org)
    3. OIDC Client details are asked. **Create Keycloak Client**, refer to [Keycloak Client Creation](../../deployment/deployment-guide/keycloak/keycloak-client-creation.md) guide.
    4. Click on **Next** to navigate to **Helm** **Options** page. Disable `wait` flag. Click on **Install**.
    5. Watch for every pods to enter a **Running** state. This may take several minutes.\
       ![](<../../.gitbook/assets/image (64).png>)

## Installation using CLI

* Install the following utilities on your machine:
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* Clone the [https://github.com/openg2p/openg2p-spar-deployment](https://github.com/OpenG2P/openg2p-spar-deployment/) repo. Switch to the branch of interest.  Navigate to `deployment` directory.
*   Run.&#x20;

    ```bash
    SPAR_HOSTNAME=spar.openg2p.sandbox.net \
      NS=<namespace> \
      ./install.sh
    ```

## Access links

After installation, SPAR is accessible over following URLs based on the `SPAR_HOSTNAME` given above:

* SPAR Self Service UI:  `https://spar.openg2p.sandbox.net`
* SPAR Self Service API: `https://spar.openg2p.sandbox.net/api/selfservice`
* SPAR Mapper: `https://spar.openg2p.sandbox.net/api/mapper`

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
