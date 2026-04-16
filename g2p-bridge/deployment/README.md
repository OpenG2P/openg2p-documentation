# Deployment

This guide provides instructions for deploying all G2P Bridge components on a Kubernetes cluster using Helm charts. These charts will install the G2P Bridge components along with a dedicated PostgreSQL server, all within the same namespace. The deployment may be achieved by the following methods:

* [Using Rancher UI](./#using-rancher-ui)
* [Using command line](./#using-the-command-line)

## Prerequisites

Before you deploy, make sure the following are in place:

* ✅ **Kubernetes cluster** is up and running
* ✅ **Nginx server is configured** (skip this for OpenG2P-in-a-box)
* ✅ **Namespace is created** (via Rancher under a Project)
* ✅ **Project Owner access** on the OpenG2P namespace
* ✅ **Istio gateway** is set up in the namespace

## Installation u**sing Rancher UI**

1. Log in to the Rancher admin console and select your cluster.
2. Go to Apps -> Repositories and click Create to add a new repository.
3. Enter "openg2p" as the Name and `https://openg2p.github.io/openg2p-helm/rancher` as the target HTTPS Index URL, then click Create.
4. Select the desired namespace for installation from the filter on the top-right.
5. To see prerelease versions of OpenG2P apps, click your user avatar in the upper right corner of the Rancher dashboard and select Include Prerelease Versions under Preferences.
6. Navigate to the Apps -> Charts page. The OpenG2P G2P-Bridge will be listed on the dashboard.
7. Click on the Helm chart, choose the version you want to install, and click Install.\
   ![](<../../.gitbook/assets/image (75).png>)
8. On the next screen, provide a name for the installation (e.g., `g2p-bridge`), check the Customise Helmbox before installation, and click Next.
9. Configure the following for each app:
   * Set a hostname for each app in the format `<appname>.<base-hostname>`, where `<base-hostname>` is the wildcard hostname chosen during the Istio namespace setup (e.g., `g2p-bridge.dev.openg2p.org`). The `<appname>` is arbitrary, and default names are provided.
   * Select all the recommended services you wish to install. The Bridge installation includes API and Celery Background task services.
10. Click Next to proceed to the Helm Options page. Disable the wait flag and click Install.
11. Monitor the pods until they all enter a Running state, which may take several minutes.\
    ![](<../../.gitbook/assets/image (63).png>)

## Installation using CLI

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

### Post-Installation Configuration

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
