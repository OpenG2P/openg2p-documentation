---
description: Helm Chart Deployment of OpenG2P G2P Bridge
---

# Deployment of G2P Bridge

### Prerequisites

Before deploying the Helm charts, ensure that the following prerequisites are met:

1. **Kubernetes Cluster**: A Kubernetes cluster is up and running. You can use any Kubernetes provider.
2. **Helm CLI**: Helm CLI installed. Version 3.x or higher is recommended. You can install Helm using the official Helm installation guide.
3. **Access to Docker Hub**: Ensure that Docker Hub can be accessed to pull the required container images.
4. **Configured Values**: Update the `values.yaml` file with any custom settings needed for your deployment, including image versions, credentials, hostnames, etc.

### Deployment Artefacts

An overview of all necessary artifacts to deploy the G2P Bridge application, stored in designated repositories to ensure controlled access and ease of deployment.

**1. Helm Chart for G2P Bridge**

* **Purpose**: Deploys the complete G2P Bridge suite on Kubernetes, including the API, Celery Beat (for scheduled tasks), and Celery Workers (for background processing).
* **Repository**: [G2P Bridge Deployment on GitHub](https://github.com/OpenG2P/openg2p-g2p-bridge-deployment)​
* **Access and Installation**:
  *   Add the GitHub Helm chart repository and install the `openg2p-g2p-bridge` chart, which includes all G2P Bridge components:\


      ```bash
      helm repo add openg2p https://github.com/OpenG2P/openg2p-g2p-bridge-deployment
      helm repo update
      helm install openg2p-g2p-bridge openg2p/openg2p-g2p-bridge --namespace your-namespace
      ```
  * **Environment Configuration**: Ensure the required environment variables are configured before installation. Refer to[ G2P Bridge Developer](https://docs.openg2p.org/g2p-bridge/development/developer-install/installing-openg2p-bridge-on-linux#docs-internal-guid-f8d8e15e-7fff-3872-8a9f-bfbb05735977) section to know more about environment configuration.

**2. Docker Images**

* **Purpose**: Provides containerized versions of each G2P Bridge component for consistent and repeatable deployments.
* **Repository**: Docker Hub
* **Available Images**:
  * **API**: [openg2p-g2p-bridge-api](https://hub.docker.com/r/openg2p/openg2p-g2p-bridge-api)​
  * **Celery Workers**: [openg2p-g2p-bridge-celery-workers](https://hub.docker.com/r/openg2p/openg2p-g2p-bridge-celery-workers)​
  * **Celery Beat Producers**: [openg2p-g2p-bridge-celery-beat-producers](https://hub.docker.com/r/openg2p/openg2p-g2p-bridge-celery-beat-producers)​
* **Usage**:
  *   Each image can be pulled directly from Docker Hub:

      ```bash
      docker pull openg2p/openg2p-g2p-bridge-api:<version>
      docker pull openg2p/openg2p-g2p-bridge-celery-workers:<version>
      docker pull openg2p/openg2p-g2p-bridge-celery-beat-producers:<version>
      ```


  * Replace `<version>` with the specific tag or `latest` for the latest stable release.

**2. Python Libraries**

* **Purpose**: Provides essential libraries and dependencies for G2P Bridge services. These are available on PyPI and should be installed where necessary.
* **Repository**: [PyPI (Python Package Index)](https://pypi.org/)​
* **Available Libraries**:
  * `openg2p-fastapi-common`: Common FastAPI components.
  * `openg2p-fastapi-auth`: Authentication modules.
  * `openg2p-g2pconnect-common-lib`: Core library for G2P Connect.
  * `openg2p-g2p-bridge-models`: Database models.
  * `openg2p-g2p-bridge-api`: API components.
  * `openg2p-g2p-bridge-bank-connectors`: Bank connectors for financial integration.
  * `openg2p-g2p-bridge-celery-beat-producers`: Schedulers for Celery tasks.
  * `openg2p-g2p-bridge-celery-workers`: Workers for background processing.
* **Installation**:
  *   Install each required package using `pip`

      ```
      pip install openg2p-fastapi-commonpip install openg2p-fastapi-authpip install openg2p-g2pconnect-common-libpip install openg2p-g2p-bridge-modelspip install openg2p-g2p-bridge-apipip install openg2p-g2p-bridge-bank-connectorspip install openg2p-g2p-bridge-celery-beat-producerspip install openg2p-g2p-bridge-celery-workers
      ```

**3. Post-Installation Configuration**

After deploying the G2P Bridge, the following database table must be configured to enable the benefit program features:

* **Table**: `benefit_program_configurations`
* **Purpose**: Stores configuration details for each benefit program, which are essential for the operation of the G2P Bridge.

### Deployment Steps

#### 1. Clone the GitHub Repository

```
# Clone the GitHub repository containing the Helm charts
$ git clone https://github.com/OpenG2P/openg2p-g2p-bridge-deployment.git
$ cd openg2p-g2p-bridge-deployment/charts
```

#### 2. Install Helm Dependencies

```
# Install the dependencies for the Helm chart
$ helm dependency update
```

#### 3. Install the Helm Chart

```
# Install the openg2p-g2p-bridge chart using Helm
$ helm install openg2p-g2p-bridge ./openg2p-g2p-bridge -f values.yaml -n <namespace>
```

* Replace `openg2p-g2p-bridge` with the desired release name.
* Replace `namespace` with your kubernetes namespace.
* Use the `-f` flag to provide custom configurations through a `values.yaml` file.

#### 4. Update Values File (Optional)

To customize the configuration, update the `values.yaml` file. Here's a sample of what you might want to configure:

* Set the hostname, Docker image tags, and various other configurations to match your environment.

#### 5. Check the Deployment

After running the install command, ensure that all pods and services are running correctly.

```
# Check the status of the Helm release
$ helm status openg2p-g2p-bridge

# View the Kubernetes pods and services
$ kubectl get pods,svc
```

#### 6. Updating the Helm Release

If changes are made to the `values.yaml` or any part of the Helm chart, use the following command to upgrade the release:

```
$ helm upgrade openg2p-g2p-bridge . -f ./values.yaml -n <namespace>
```

#### 7. Uninstalling the Chart

To remove the deployment, run the following:

```
$ helm uninstall openg2p-g2p-bridge -n <namespace>
```

This will delete all Kubernetes resources associated with the release.
