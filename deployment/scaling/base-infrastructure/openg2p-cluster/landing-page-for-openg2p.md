---
description: This document describes how to deploy landing page for OpenG2P
---

# Landing Page For OpenG2P

The instructions here pertain to the deployment of Landing Page for OpenG2P environments using Helm charts. All the components are installed in the same namespace. The deployment may be achieved by the following methods:

### Prerequisites <a href="#prerequisites" id="prerequisites"></a>

Before you deploy, make sure the following are in place:

* ✅ [Infrastruction setup](../../../deployment-instructions/infrastructure-setup.md) is completed&#x20;
* ✅ [Environment](../../../deployment-instructions/environment-installation.md) has been setup with common resources installed.
* ✅ Domain name `registry.<your environment>.<your domain name>` (e.g. `registry.qa.openg2p.org`) is available along with SSL certificate for the domain (_the wild certificate should have already been loaded during Infrastructure setup_)
* ✅ **Project Owner access** on the OpenG2P namespace

### Installation using Rancher UI <a href="#installation-using-rancher-ui" id="installation-using-rancher-ui"></a>

1. Log in to Rancher admin console.
2. Select your cluster.
3. Under Apps -> Repositories click on Create to add a repository.
4. Provide Name as "openg2p" and target HTTPS Index URL as [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) and click Create.
5. Select the namespace in which you would like to install Landing page, from the namespace filter on the top-right.
6. To display prerelease versions of OpenG2P apps, click on your user avatar in the upper right corner of the Rancher dashboard. Then click on "Include Prerelease Versions" under Preferences under Helm Charts.
7.  Navigate to Apps->Charts page on Rancher. You should see "Landing Page" Helm charts listed.

    <figure><img src="../../../../.gitbook/assets/image (23) (1).png" alt=""><figcaption></figcaption></figure>
8. Click on the Helm chart, provide the necessary URLs in the configuration, click Next, remove the wait flag, and then install it.
