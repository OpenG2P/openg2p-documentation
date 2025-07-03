# Deployment

G2P Bridge Deployment

The instructions here pertain to the deployment of all G2P Bridge components on the Kubernetes cluster using [Helm charts](helm-charts.md).  The charts install G2P Bridge components along with the Postgresql server specific to G2P Bridge. All the components are installed in the same namespace. The deployment may be achieved by the following methods:

* [Using Rancher UI ](./#installation-using-rancher-ui)
* [Using command line](./#installation-using-the-command-line)

## Prerequisites

Before you deploy G2P Bridge, make sure the following are available:

* [Base infrastructure](https://docs.openg2p.org/deployment/base-infrastructure) along with domain name and certificates for Rancher and Keycloak
* [Domain names and certificates](domain-names-and-certificates.md) specific to Social Registry.
* Nginx server configuration
  * A conf file is created under `sites-enabled` on Nginx containing the above SSL certs. See [sample conf file](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/nginx/server.sample.conf).
* Namespace is created (On Rancher a namespace is created under a Project).
* [Project Owner](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac/cluster-and-project-roles#project-roles) permission on the namespace of OpenG2P cluster.
* Gateways are setup for the domain as given here [Istio namespace setup](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/cluster-setup/istio#namespace-setup).

## Installation using Rancher UI

1. Log in to Rancher admin console.
2. Select your cluster.
3. Under _**Apps -> Repositories**_ click the _**Create**_ to add a repository.
4. Provide _**Name**_ as "openg2p" and target HTTPS _**Index URL**_ as [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) and click on _**Create**_.
5. Select the namespace in which you would like to install PBMS, from the namespace filter on the top-right.
6. To display prerelease versions of OpenG2P apps, click on your user avatar in the upper right corner of the Rancher dashboard. Then click on _**Include Prerelease Versions**_ under _**Preferences**_ below the _**Helm Charts**_.
7. Navigate to **Apps->Charts** page on Rancher. You can find the _**OpenG2P SPAR**_ is listed in the dashboard.

<div align="left"><figure><img src="../../.gitbook/assets/Screenshot 2025-06-30 at 1.21.29 PM.png" alt="" width="295"><figcaption></figcaption></figure></div>

6. Click on the Helm chart, select the version to be installed, and click _**Install**_.
7. On the next screen, choose a name for installation, like `g2p-bridge`. Select the checkbox _**Customise Helm**_ before the installation, and then click on _**Next**_.
8. Navigate to each app's configuration page, and configure the following:
   1. Configure a hostname for each app in the following way. `<appname>.<base-hostname>` , where base hostname is the wildcard hostname chosen during [Istio namespace setup](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/cluster-setup/istio#namespace-setup). Example: `g2p-bridge.dev.openg2p.org`  etc. `<appname>` is arbitrary - default names have been provided.
   2. Select all the recommended services you want to install. Bridge installation comes with API and Celery Background task services.&#x20;
   3. Click on _**Next**_ to navigate to _**Helm Options**_ page. Disable `wait` flag. Click on _**Install**_.
   4. Watch for every pods to enter a _**Running**_ state. This may take several minutes.

## Access links

After installation, G2P-BRIDGE is accessible over following URLs based on the url given above:

* G2P-Bridge API: _https://g2p-bridge.openg2p.sandbox.net/_&#x61;pi/

## Database

Postgresql is installed as part of the above procedure in the same namespace. The default database created is `openg2p_g2p_bridge_db`.

## Sanity testing

TBD
