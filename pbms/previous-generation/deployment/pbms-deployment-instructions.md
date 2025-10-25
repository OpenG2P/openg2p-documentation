---
description: PBMS Deployment Instructions
---

# Deployment Instructions

This document contains instructions for all the deployment of PBMS modules and their related components on the Kubernetes cluster using [Helm charts](https://docs.openg2p.org/pbms/deployment/helm-charts). All the components are installed in the same namespace. The methods used to achieve the deployment are:

* [Using Rancher UI](pbms-deployment-instructions.md#installation-using-rancher-ui)
* [Using command line](pbms-deployment-instructions.md#installation-using-the-command-line)

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
4.  Provide Name as `openg2p` and target HTTPS Index URL as [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) and click Create.\\

    <figure><img src="../../../.gitbook/assets/image (65).png" alt=""><figcaption></figcaption></figure>
5.  To display prerelease versions of OpenG2P apps, click on your user avatar in the upper right corner of the Rancher dashboard. Then click on `Include Prerelease Versions` under Preferences under Helm Charts.\\

    <figure><img src="../../../.gitbook/assets/image (66).png" alt=""><figcaption></figcaption></figure>
6. Select the namespace in which you would like to install PBMS, from the namespace filter on the top-right.
7.  Navigate to **Apps->Charts** page on Rancher. You should see `OpenG2P PBMS` Helm charts listed.\\

    <figure><img src="../../../.gitbook/assets/image (67).png" alt=""><figcaption></figcaption></figure>

    **Note:** You can ignore "**Part 2**" as it refers to an older version of the Helm chart.
8. Proceed to Install `OpenG2P PBMS` chart select the latest version to be installed, and click Install.
9. On the next screen, choose a name for installation, like `pbms`. Select the checkbox `Customise Helm options` before install, and click Next.
10. Navigate to each app's configuration page, and configure the following:
    1. Configure a hostname for each app in the following way. `<appname>.<base-hostname>` , where base hostname is the wildcard hostname chosen during [Istio namespace setup](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/cluster-setup/istio#namespace-setup). Example: `pbms.dev.openg2p.org` and `odk-pbms.dev.openg2p.org` , etc. `<appname>` is arbitrary - default names have been provided.
    2. **Keycloak Base Url** is your organization-wide Keycloak URL. (Ex: keycloak.\<your domain>.org)
    3. OIDC Client details are asked. **Create Keycloak Client**, refer to [Keycloak Client Creation](../../../deployment/deployment-guide/keycloak-client-creation.md) guide.
11. Click on Next to navigate to Helm Options page. Disable `wait` flag. Click on Install.
12. Watch for every pods to enter a **Running** state. This may take several minutes.

    <div align="left"><figure><img src="../../../.gitbook/assets/image (68).png" alt=""><figcaption></figcaption></figure></div>

## Installation using the command line

* Install the following utilities on your machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* To Be Done

## Post installation

### Keycloak

**Assigning roles to users**

Create[ Keycloak client roles](https://www.keycloak.org/docs/latest/server_admin/#con-client-roles_server_administration_guide) for the following components and assign them to users.

| Component                           | Role name      |
| ----------------------------------- | -------------- |
| OpenSearch Dashboards for logging   | `admin`        |
| OpenSearch Dashboards for Reporting | `admin`        |
| Apache Superset                     | `Admin`        |
| Minio Console                       | `consoleAdmin` |
| Kafka UI for Reporting              | `Admin`        |

**Assigning roles to clients**

* Create a realm role in Keycloak with the name "KEYMANAGER\_ADMIN" and assign it as a service account role to the PBMS Keycloak client in order for PBMS to be able to access Keymanager APIs.

#### Odoo <a href="#odoo" id="odoo"></a>

* Refer the [Odoo post-install guide](https://docs.openg2p.org/deployment/deployment-guide/odoo-post-install-configuration) to activate Odoo modules.
