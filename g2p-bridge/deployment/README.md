# Deployment

This guide provides instructions for deploying all G2P Bridge components on a Kubernetes cluster using Helm charts. These charts will install the G2P Bridge components along with a dedicated PostgreSQL server, all within the same namespace. The deployment may be achieved by the following methods:

* [Using Rancher UI](./#using-rancher-ui)
* [Using command line](./#using-the-command-line)

***

## Prerequisites

Before you begin the G2P Bridge deployment, ensure the following prerequisites are met:

* Base Infrastructure: A running Kubernetes cluster is required. You can use any Kubernetes provider.
* Helm CLI: The Helm CLI (version 3.x or higher) must be installed. You can find installation instructions in the official Helm guide.
* Domain and Certificates: You need a domain name and certificates for Rancher and Keycloak, as well as domain names and certificates specific to the Social Registry.
* Nginx Configuration: An Nginx server must be configured with a `.conf` file in the `sites-enabled`directory containing the SSL certificates.
* Kubernetes Namespace: A namespace must be created. In Rancher, this is done within a Project.
* Permissions: You will need "Project Owner" permissions on the namespace within the OpenG2P cluster.
* Gateways: Istio gateways must be set up for the domain as per the Istio namespace setup instructions.
* Docker Hub Access: Ensure that you can access Docker Hub to pull the necessary container images.
* Configured Values: The `values.yaml` file should be updated with any custom settings required for your deployment, such as image versions, credentials, and hostnames.

***

## Deployment Artefacts

Here is an overview of the necessary artifacts for deploying the G2P Bridge application. These are stored in designated repositories for controlled access and straightforward deployment.

### **1. Helm Chart for G2P Bridge**

* Purpose: Deploys the entire G2P Bridge suite on Kubernetes, which includes the API, Celery Beat (for scheduled tasks), and Celery Workers (for background processing).
* Repository: [G2P Bridge Deployment on GitHub](https://github.com/OpenG2P/openg2p-g2p-bridge-deployment)
*   Access and Installation: To add the GitHub Helm chart repository and install the `openg2p-g2p-bridge`chart, which contains all G2P Bridge components, run the following commands:

    ```bash
    helm repo add openg2p https://github.com/OpenG2P/openg2p-g2p-bridge-deployment
    helm repo update
    helm install openg2p-g2p-bridge openg2p/openg2p-g2p-bridge --namespace your-namespace
    ```
* Environment Configuration: Make sure that the required environment variables are configured before installation. Refer to the G2P Bridge Developer section for more information on environment configuration.

### **2. Docker Images**

* Purpose: Provide containerized versions of each G2P Bridge component for consistent and repeatable deployments.
* Repository: [Docker Hub](https://hub.docker.com/)
* Available Images:
  * `openg2p-g2p-bridge-api`
  * `openg2p-g2p-bridge-celery-workers`
  * `openg2p-g2p-bridge-celery-beat-producers`
*   Usage: You can pull each image directly from Docker Hub using the following commands. Replace `<version>` with the specific tag or use `latest` for the most recent stable release.

    ```bash
    docker pull openg2p/openg2p-g2p-bridge-api:<version>
    docker pull openg2p/openg2p-g2p-bridge-celery-workers:<version>
    docker pull openg2p/openg2p-g2p-bridge-celery-beat-producers:<version>
    ```

### **3. Python Libraries**

* Purpose: Provide essential libraries and dependencies for G2P Bridge services. These are available on PyPI and should be installed where necessary.
* Repository: [PyPI (Python Package Index)](https://pypi.org/)
* Available Libraries:
  * `openg2p-fastapi-common`
  * `openg2p-fastapi-auth`
  * `openg2p-g2pconnect-common-lib`
  * `openg2p-g2p-bridge-models`
  * `openg2p-g2p-bridge-api`
  * `openg2p-g2p-bridge-bank-connectors`
  * `openg2p-g2p-bridge-celery-beat-producers`
  * `openg2p-g2p-bridge-celery-workers`
*   Installation: Install each required package using `pip`:

    ```bash
    pip install openg2p-fastapi-common openg2p-fastapi-auth openg2p-g2pconnect-common-lib openg2p-g2p-bridge-models openg2p-g2p-bridge-api openg2p-g2p-bridge-bank-connectors openg2p-g2p-bridge-celery-beat-producers openg2p-g2p-bridge-celery-workers
    ```

***

## Installation

### **Using Rancher UI**

1. Log in to the Rancher admin console and select your cluster.
2. Go to Apps -> Repositories and click Create to add a new repository.
3. Enter "openg2p" as the Name and `https://openg2p.github.io/openg2p-helm/rancher` as the target HTTPS Index URL, then click Create.
4. Select the desired namespace for installation from the filter on the top-right.
5. To see prerelease versions of OpenG2P apps, click your user avatar in the upper right corner of the Rancher dashboard and select Include Prerelease Versions under Preferences.
6. Navigate to the Apps -> Charts page. The OpenG2P SPAR will be listed on the dashboard.
7. Click on the Helm chart, choose the version you want to install, and click Install.

<div align="left"><figure><img src="../../.gitbook/assets/Screenshot 2025-06-30 at 1.21.29 PM.png" alt="" width="295"><figcaption></figcaption></figure></div>

8. On the next screen, provide a name for the installation (e.g., `g2p-bridge`), check the Customise Helmbox before installation, and click Next.
9. Configure the following for each app:
   * Set a hostname for each app in the format `<appname>.<base-hostname>`, where `<base-hostname>` is the wildcard hostname chosen during the Istio namespace setup (e.g., `g2p-bridge.dev.openg2p.org`). The `<appname>` is arbitrary, and default names are provided.
   * Select all the recommended services you wish to install. The Bridge installation includes API and Celery Background task services.
10. Click Next to proceed to the Helm Options page. Disable the wait flag and click Install.
11. Monitor the pods until they all enter a Running state, which may take several minutes.

### **Using the Command Line**

1.  Clone the GitHub Repository:

    ```bash
    git clone https://github.com/OpenG2P/openg2p-g2p-bridge-deployment.git
    cd openg2p-g2p-bridge-deployment/charts
    ```
2.  Install Helm Dependencies:

    ```bash
    helm dependency update
    ```
3.  Install the Helm Chart:

    ```bash
    helm install openg2p-g2p-bridge ./openg2p-g2p-bridge -f values.yaml -n <namespace>
    ```

    * Replace `openg2p-g2p-bridge` with your desired release name.
    * Replace `<namespace>` with your Kubernetes namespace.
    * Use the `-f` flag to provide custom configurations through a `values.yaml` file.
4. Update Values File (Optional): To customize your configuration, you can update the `values.yaml` file. This is where you can set the hostname, Docker image tags, and other configurations to match your environment.
5.  Check the Deployment: After running the install command, verify that all pods and services are running correctly.

    ```bash
    helm status openg2p-g2p-bridge
    kubectl get pods,svc
    ```
6.  Updating the Helm Release: If you make changes to the `values.yaml` file or any part of the Helm chart, use the following command to upgrade the release:

    ```bash
    # This command will delete all Kubernetes resources associated with the release.
    helm upgrade openg2p-g2p-bridge ./openg2p-g2p-bridge -f values.yaml -n <namespace>
    ```

***

## Post-Installation Configuration

After deploying the G2P Bridge, you must configure the following database table to enable the benefit program features:

* Table: `benefit_program_configurations`
* Purpose: This table stores configuration details for each benefit program, which are essential for the operation of the G2P Bridge.

### **Access Links**

Once the installation is complete, G2P-Bridge will be accessible at the following URL, based on the URL you provided during setup:

* G2P-Bridge API: `https://g2p-bridge.openg2p.sandbox.net/api/g2p-bridge`

### **Database**

PostgreSQL is installed as part of this procedure in the same namespace. The default database created is `openg2p_g2p_bridge_db`.

## **Sanity Testing**

TBD
