---
description: Social Registry Deployment
---

# Deployment

The instructions here pertain to the deployment of all Social Registry and associated components on the Kubernetes cluster using[ Helm charts](../deployment/helm-charts.md).   All the components are installed in the same namespace. The deployment may be achieved by the following methods:

* Using Rancher UI&#x20;
* Using command line

## Prerequisites

Before you deploy, make sure the following are available:

* [Base infrastructure](../deployment/base-infrastructure/)
* Cluster Owner permission on your cluster
* Namespace in which you would be installing the module, along with [Istio namespace setup](../deployment/base-infrastructure/openg2p-cluster/cluster-setup/istio.md#namespace-setup).

## Installation using Rancher UI

1. Log in to Rancher admin console.
2. Select your cluster.
3. Under _Apps -> Repositories_ click on _Create_ to add a repository.
4. Provide _Name_ as "openg2p" and target HTTPS _Index URL_ as [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) and click _Create_.
5. Select the namespace in which you would like to install Social Registry, from the namespace filter on the top-right.
6. To display prerelease versions of OpenG2P apps, click on your user avatar in the upper right corner of the Rancher dashboard. Then click on "Include Prerelease Versions" under _Preferences_ under _Helm Charts_.
7. Navigate to _Apps->Charts_ page on Rancher. You should see "OpenG2P Social Registry" Helm charts listed.

<div align="left">

<figure><img src="../.gitbook/assets/social-registry-deployment-rancher-list.png" alt=""><figcaption></figcaption></figure>

</div>

7. Click on "Part 1" Helm chart, select the version to be installed, and click _Install_.
8. On the next screen, choose a name for installation, like `social-registry`. Select the checkbox _Customise Helm options before install_, and click _Next_.
9. Go through each app's configuration page, and configure accordingly:
   1. Choose to install all requirements (on the main _Questions_ page) unless not needed specifically.
   2. Configure a hostname for each app in the following way. `<appname>.<base-hostname>` , where base hostname is the wildcard hostname chosen during [Namespace Setup](../deployment/base-infrastructure/openg2p-cluster/cluster-setup/istio.md#namespace-setup).  Example: `socialregistry.dev.openg2p.org` and `odk.dev.openg2p.org` , etc. Refer to [DNS requirements](../deployment/hardware-requirements.md#dns-requirements) for mapping the hostname.
   3. _Keycloak Base Url_ is your organization-wide Keycloak URL, which is now done along with Rancher Installation. If not Installed along with Rancher, refer to Keycloak Installation.
   4. Create a Keycloak client in your main Keycloak, wherever OIDC Client details are asked. Refer to [Keycloak Client Creation](../deployment/deployment-guide/keycloak-client-creation.md) guide.
10. Click Next and you should be taken to the _Helm Options_ page. Make sure to disable `wait` flag on the _Helm Options_ page. Click on Install.
11. Navigate back to _Apps->Charts_ page on Rancher. And this time choose "Part 2" Helm chart. Select the same version as "Part 1", and click _Install_.
12. On the next screen, give the same installation name as on "Part 1" but with suffix `-p2` , like `social-registry-p2`. Select the checkbox _Customise Helm options before install_, and click _Next_.
13. Repeat the same as Step 9 & 10. Please note that the apps and configurations differ between "Part 1" and "Part 2".

## Installation using the command line

* Install the following utilities on your machine:
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* TBD

## Post Installation

* To access OpenSearch Dashboards, create a Keycloak client role under the OpenSearch Keycloak client, with the name `admin` and assign it to users.
* To access Superset, create a Keycloak client role under the Superset Keycloak client, with the name `Admin` and assign it to users.
* To access Minio Console, create a Keycloak client role under the Minio Keycloak client, with the name `consoleAdmin` and assign it to users.
* To access Kafka UI to monitor Reporting, create a Keycloak client role under the Reporting Kafka Keycloak client, with the name `Admin` and assign it to users.
* For Social Registry to be able to access Keymanager APIs, create a realm role in Keycloak with the name "KEYMANAGER\_ADMIN" and assign this as a service account role to the Social Registry Keycloak client.
* Proceed with Odoo post-install configuration, similar to [PBMS Odoo Post Install Configuration](../pbms/deployment/post-install-instructions.md).

## Access links

TBD

## Database

Postgresql is installed as part of the above procedure in the same namespace. The default database created is `socialregistrydb` .

## Sanity testing

TBD
