---
description: This document describes how to deploy landing page for OpenG2P
---

# Landing Page For OpenG2P

The instructions here pertain to the deployment of Landing Page for OpenG2P environments using Helm charts. All the components are installed in the same namespace. The deployment may be achieved by the following methods:

### Prerequisites <a href="#prerequisites" id="prerequisites"></a>

Before you deploy, make sure the following are available:

* [Base infrastructure](https://docs.openg2p.org/deployment/base-infrastructure) along with domain name and certificates for Rancher and Keycloak
* [Domain names and certificates](https://docs.openg2p.org/social-registry/deployment/domain-names-and-certificates) specific to Landing Page.
* Nginx server configuration
  * A conf file is created under `sites-enabled` on Nginx containing the above SSL certs. See [sample conf file](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/nginx/server.sample.conf).
* Namespace is created (On Rancher a namespace is created under a Project).
* [Project Owner](https://ranchermanager.docs.rancher.com/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/manage-role-based-access-control-rbac/cluster-and-project-roles#project-roles) permission on the namespace of OpenG2P cluster.
* Gateways are setup for the domain as given here [Istio namespace setup](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/cluster-setup/istio#namespace-setup).

### Installation using Rancher UI <a href="#installation-using-rancher-ui" id="installation-using-rancher-ui"></a>

1. Log in to Rancher admin console.
2. Select your cluster.
3. Under _Apps -> Repositories_ click on _Create_ to add a repository.
4. Provide _Name_ as "openg2p" and target HTTPS _Index URL_ as [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) and click _Create_.
5. Select the namespace in which you would like to install Landing page, from the namespace filter on the top-right.
6. To display prerelease versions of OpenG2P apps, click on your user avatar in the upper right corner of the Rancher dashboard. Then click on "Include Prerelease Versions" under _Preferences_ under _Helm Charts_.
7.  Navigate to _Apps->Charts_ page on Rancher. You should see "Landing Page" Helm charts listed.

    <figure><img src="../../../.gitbook/assets/image (23) (1).png" alt=""><figcaption></figcaption></figure>
8. Click on the Helm chart, provide the necessary URLs in the configuration, click Next, remove the wait flag, and then install it.
