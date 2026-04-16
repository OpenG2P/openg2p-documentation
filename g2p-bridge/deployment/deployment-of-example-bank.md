---
description: Deployment of OpenG2P Example Bank Simulator
---

# Deployment of Example Bank

### Prerequisites

Before you deploy, make sure the following are in place:

* ✅ **Kubernetes cluster** is up and running
* ✅ **Nginx server is configured** (skip this for OpenG2P-in-a-box)
* ✅ **Namespace is created** (via Rancher under a Project)
* ✅ **Project Owner access** on the OpenG2P namespace
* ✅ **Istio gateway** is set up in the namespace

## Installation using Rancher UI

1. Log in to the Rancher admin console and select your cluster.
2. Go to Apps -> Repositories and click Create to add a new repository.
3. Enter "openg2p" as the Name and `https://openg2p.github.io/openg2p-helm/rancher` as the target HTTPS Index URL, then click Create.
4. Select the desired namespace for installation from the filter on the top-right.
5. To see prerelease versions of OpenG2P apps, click your user avatar in the upper right corner of the Rancher dashboard and select Include Prerelease Versions under Preferences.
6. Navigate to the Apps -> Charts page. The OpenG2P-G2P-Bridge-Example-Bank will be listed on the dashboard.
7. Click on the Helm chart, choose the version you want to install, and click Install.\
   ![](<../../.gitbook/assets/image (73).png>)
8. On the next screen, provide a name for the installation (e.g., `example-bank`), check the Customise Helmbox before installation, and click Next.
9. Configure the following for each app:
   * Set a hostname for each app in the format `<appname>.<base-hostname>`, where `<base-hostname>` is the wildcard hostname chosen during the Istio namespace setup (e.g., `example-bank.dev.openg2p.org`). The `<appname>` is arbitrary, and default names are provided.
   * Select all the recommended services you wish to install. The Bridge installation includes API and Celery Background task services.
10. Click Next to proceed to the Helm Options page. Disable the wait flag and click Install.
11. Monitor the pods until they all enter a Running state, which may take several minutes.\
    ![](<../../.gitbook/assets/image (63).png>)

## **Installation using CLI**

#### 1. Clone the GitHub Repository

```
# Clone the GitHub repository containing the Helm charts
$ git clone https://github.com/OpenG2P/openg2p-g2p-bridge-example-bank-deployment
$ cd openg2p-g2p-bridge-example-bank-deployment/charts
```

#### 2. Install Helm Dependencies

```
# Install the dependencies for the Helm chart
$ helm dependency update
```

#### 3. Install the Helm Chart

```
# Install the openg2p-g2p-bridge-example-bank chart using Helm
$ helm install openg2p-g2p-example-bank ./openg2p-g2p-bridge-example-bank -f values.yaml -n <namespace>
```

* Replace `openg2p-g2p-example-bank` with the desired release name.
* Replace `namespace` with your kubernetes namespace.
* Use the `-f` flag to provide custom configurations through a `values.yaml` file.

#### 4. Update Values File (Optional)

To customize the configuration, update the `values.yaml` file. Here's a sample of what you might want to configure:

* Set the hostname, Docker image tags, and various other configurations to match your environment.

#### 5. Check the Deployment

After running the install command, ensure that all pods and services are running correctly.

```
# Check the status of the Helm release
$ helm status openg2p-g2p-example-bank

# View the Kubernetes pods and services
$ kubectl get pods,svc
```

#### 6. Updating the Helm Release

If changes are made to the `values.yaml` or any part of the Helm chart, use the following command to upgrade the release:

```
$ helm upgrade openg2p-g2p-example-bank . -f ./values.yaml -n <namespace>
```

#### 7. Uninstalling the Chart

To remove the deployment, run the following:

```
$ helm uninstall openg2p-g2p-example-bank -n <namespace>
```

This will delete all Kubernetes resources associated with the release.

## **Post-Installation Configuration**

After deploying the Example Bank, the following database table must be configured to enable the benefit program features:

* **Table**: `accounts`
* **Purpose**: Stores bank account details, which are essential for the operation of the G2P Bridge.
