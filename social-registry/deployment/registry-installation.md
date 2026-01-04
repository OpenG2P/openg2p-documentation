# Registry Installation

The instructions here pertain to the deployment of Registry and associated components on the Kubernetes cluster using [Registry Helm chart](registry-helm-chart-3.x.x.md).  All the components are installed in the same namespace.&#x20;

## Prerequisites

Before you deploy, make sure the following are in place:

* ✅ [Infrastruction setup](../../deployment/deployment-instructions/infrastructure-setup.md) is completed&#x20;
* ✅ [Environment](../../deployment/deployment-instructions/environment-installation.md) has been setup with common resources installed.
* ✅ Domain name `registry.<your environment>.<your domain name>` (e.g. `registry.qa.openg2p.org`) is available along with SSL certificate for the domain (_the wild certificate should have already been loaded during Infrastructure setup_)
* ✅ **Project Owner access** on the OpenG2P namespace

## Installation using Rancher UI

1. Log in to Rancher admin console.
2. Select your cluster.
3. Under **Apps -> Repositories** click on Create to add a repository.
4.  Provide Name as `openg2p` and target HTTPS Index URL as [https://openg2p.github.io/openg2p-helm/rancher](https://openg2p.github.io/openg2p-helm/rancher) and click Create.<br>

    <figure><img src="../../.gitbook/assets/image (2).png" alt=""><figcaption></figcaption></figure>
5.  To display prerelease versions of OpenG2P apps, click on your user avatar in the upper right corner of the Rancher dashboard. Then click on `Include Prerelease Versions` under Preferences under Helm Charts.<br>

    <figure><img src="../../.gitbook/assets/image (3).png" alt=""><figcaption></figcaption></figure>
6. Select the namespace in which you would like to install Registry, from the namespace filter on the top-right.
7.  Navigate to **Apps->Charts** page on Rancher. You should see `OpenG2P  Registry` Helm charts listed.

    <div align="center"><figure><img src="../../.gitbook/assets/image (83).png" alt=""><figcaption></figcaption></figure></div>
8. Proceed to Install `OpenG2P  Registry` chart select the latest version to be installed, and click Install.
9. On the next screen, choose a name for installation, like `registry`. Select the checkbox `Customise Helm options` before install, and click Next.
10. Go through each app's configuration page, and configure the following:
    1. Configure a hostname for each app in the following way. `<appname>.<base-hostname>` , where base host name is the wildcard hostname chosen during [Istio namespace setup](../../deployment/scaling/base-infrastructure/openg2p-cluster/cluster-setup/istio.md#namespace-setup).  Example: `socialregistry.dev.openg2p.org`, etc. `<appname>` is arbitrary - default names have been provided.
    2. For production deployments, if the PostgreSQL server is running as a pod inside Kubernetes, set the PostgreSQL hostname to `host.docker.internal` (PostgreSQL pod name), as this acts as a proxy for localhost. If PostgreSQL is running on a separate server, specify the server’s domain name or IP address instead.
    3. **Keycloak Base Url** is your organization-wide Keycloak URL. (Ex: keycloak.\<your domain>.org)
    4. OIDC Client details are asked. **Create Keycloak Client**, refer to [Keycloak Client Creation](../../deployment/deployment-guide/keycloak-client-creation.md) guide.
    5.  To change the docker image from the default image, click on `Edit YAML` table and update the following section in Helm. \
        **Note:** This step is required only if you have separate docker image to be deployed or else you can go with default one and skip this step.

        ```bash
        image:
            pullPolicy: Always
            repository: openg2p/openg2p-social-registry-odoo-package
            tag: 17.0-develop-social-registry
        ```
11. To pull docker from a private repository on Docker Hub, follow guide [here](../../deployment/deployment-guide/pulling-docker-from-private-repository-on-docker-hub.md). \
    **Note:** This step is required only if you have separate private docker image to be deployed or else you can go with default one skip this step.
12. Click Next to reach Helm Options page. Disable `wait` flag. Click on Install.
13. Wait for all the pods to get into **Running state**. This may take several minutes.

    <div align="left"><figure><img src="../../.gitbook/assets/image (5).png" alt=""><figcaption></figcaption></figure></div>

## Post Installation

### Odoo

* Activate the `base_registry` module after logging into Odoo (TBD).

## Accessing the registry

On the browser connect to URL

https://\<registry domain name>/web/login?db=registry\_db

Examples:

* [https://registry.devops.openg2p.org/web/login?db=registry\_db](https://admin-pbms.devops.openg2p.org/web/login?db=pbms_db)&#x20;
* [https://admin-registry.devops.openg2p.org/web/login?db=registry\_db](https://admin-pbms.devops.openg2p.org/web/login?db=pbms_db)

<mark style="color:orange;">**TBD:  The database in the above URL should not be required. This issue is to be fixed. See issue below:**</mark>

{% @jira/embed url="https://openg2p.atlassian.net/browse/G2P-3299" %}

## Tear down

To completely cleanup Registry installation, note the following:  Helm uninstall will **not** delete the database and secrets created. Secret for user does not get deleted (and rightly so). If you re-run the Helm while database still exists, it just brings up Odoo without any issues - it does not re-initalize the database.

To tear down completely:

1. Helm uninstall via command line or Rancher (Apps -> Installed Apps --> Delete)
2. Delete `registry` secret in the namespace
3. Drop `registry_db` and user from Postgres&#x20;
   1. Login into Postgres as admin (via port fowarding or directly from Rancher). Use the `postgres-password` key in `commons-postgresql` secret to get the password
   2. `drop database registry_db;`&#x20;
   3. `drop role registry_db_user;`&#x20;
4. Drop `mosip-kernel` database:
   1. `drop database mosip-kernel`&#x20;
