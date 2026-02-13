# Environment Installation

The instructions here pertain to the deployment of [common components](../concepts/openg2p-commons-helm-chart.md) for an environment on the Kubernetes cluster.  All the components are installed in the same namespace.

## Prerequisites

Before you deploy, make sure the following are in place:

* ✅ [Infrastruction setup](infrastructure-setup.md) is completed&#x20;
* ✅ Domain name `esignet.<your environment>.<your domain name>` (e.g. `esignet.qa.openg2p.org`) is available along with SSL certificate for the domain (_the wild certificate should have already been loaded during Infrastructure setup_)
* ✅ **Project Owner access** on the OpenG2P namespace

## Installation using Rancher UI

1. Log in to Rancher admin console.
2. Select your cluster.
3. Under **Apps -> Repositories** click on Create to add a repository.
4.  Provide Name as `openg2p` and target HTTPS Index URL as [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) and click Create.

    <figure><img src="../../.gitbook/assets/image.png" alt=""><figcaption></figcaption></figure>
5.  To display prerelease versions of OpenG2P apps, click on your user avatar in the upper right corner of the Rancher dashboard. Then click on `Include Prerelease Versions` under Preferences under Helm Charts.

    <figure><img src="../../.gitbook/assets/image (1).png" alt=""><figcaption></figcaption></figure>
6. Select the namespace from the namespace filter on the top-right.
7.  Navigate to **Apps->Charts** page on Rancher. You should see **OpenG2P commons** Helm charts listed.

    <figure><img src="../../.gitbook/assets/image (2).png" alt=""><figcaption></figcaption></figure>
8. Proceed to Install **OpenG2P Commons** chart select the latest version to be installed, and click Install.
9. On the next screen, provie installation name as **`commons`** . Select the checkbox Customise Helm options before install, and click Next.\
   **Note:** Make sure the installation name should be **commons** only.
10. Go through each app's configuration page, and configure the following:
    1. Configure a hostname for each app in the following way. \
       `<appname>.<base-hostname>` , where base hostname is the wildcard hostname chosen during [Istio namespace](https://docs.openg2p.org/deployment/scaling/base-infrastructure/openg2p-cluster/cluster-setup/istio#namespace-setup) setup. Example: `esignet.dev.openg2p.org` and `odk.dev.openg2p.org` , etc. is arbitrary - default names have been provided.
    2. **Keycloak Base Url** is your organization-wide Keycloak URL. (Ex: keycloak..org)
    3. OIDC Client details are asked. **Create Keycloak Client**, refer to [Keycloak Client Creation ](https://docs.openg2p.org/deployment/deployment-guide/keycloak/keycloak-client-creation)guide.
11. Click Next to reach Helm Options page. Disable **`wait`** flag. Click on Install.
12. Wait for all the pods to get into **Running state**. This may take several minutes.\
    ![](<../../.gitbook/assets/image (3).png>)

## Installation using the command line

* Install the following utilities on your machine:
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.
* To Be Done

## Post Installation

### Keycloak

#### Assigning roles to users

Create[ Keycloak client roles](https://www.keycloak.org/docs/latest/server_admin/#con-client-roles_server_administration_guide) for the following components and assign them to users:

<table><thead><tr><th width="336">Component</th><th>Role name</th></tr></thead><tbody><tr><td>OpenSearch Dashboards for logging</td><td><code>admin</code></td></tr><tr><td>OpenSearch Dashboards for <a href="../../monitoring-and-reporting/reporting-framework/">Reporting</a> </td><td><code>admin</code></td></tr><tr><td>Kafka UI for <a href="../../monitoring-and-reporting/reporting-framework/">Reporting</a></td><td><code>Admin</code></td></tr><tr><td>Apache Superset</td><td><code>Admin</code></td></tr><tr><td>Minio Console</td><td><code>consoleAdmin</code></td></tr></tbody></table>

#### Assigning roles to clients

* For Social Registry to be able to access Keymanager APIs, create a realm role in Keycloak with the name "KEYMANAGER\_ADMIN" and assign this as a service account role to the Social Registry Keycloak client.

{% hint style="info" %}
By default, the Superset username and password are **admin / admin**. To change this, run the following command inside the superset pod.\
`superset fab reset-password --username admin --password <NEW_PASSWORD>`
{% endhint %}

## Modules

Install the modules and other utility apps individually using their respective instructions:

1. [Registry](../../social-registry/deployment/registry-installation.md)
2. [PBMS](https://docs.openg2p.org/pbms/deployment)&#x20;
3. [SPAR](https://docs.openg2p.org/spar/deployment)&#x20;
4. [G2P Bridge](https://docs.openg2p.org/g2p-bridge/deployment#installation-using-rancher-ui)&#x20;
5. Beneficiary Portal

