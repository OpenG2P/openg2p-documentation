# Deployment on Kubernetes

## Introduction

The guide here provides instructions to deploy OpenG2P components on Kubernetes (K8s) cluster (Refer to [Deployment Architecture](../deployment-architecture.md)).  The following components are installed:

| Module/Component                                         | Comments                                                                                 |
| -------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| <p>Kubernetes cluster</p><p>Rancher</p><p>NFS server</p> | Required for all components as this is the common infrastructure used by all.            |
| PostgreSQL                                               | Required for all components. A single server instance may be used housing all databases. |
| Keycloak                                                 | Required for PBMS, Social Registry                                                       |
| MinIO                                                    | Required for PBMS and GCTB only                                                          |
| ODK Central                                              | Required for Registration Toolkit                                                        |
| Kafka                                                    | Required for Monitoring & Reporting                                                      |
| Logging & OpenSearch                                     | Required for Monitoring & Reporting                                                      |
| MOSIP Key Manager                                        | Required for PBMS, Social Registry                                                       |
| e-Signet                                                 | Required for SPAR and optionally for PBMS                                                |
| OpenG2P PBMS                                             | Helm chart that installs Odoo, SMTP server                                               |
| OpenG2P SPAR                                             | Helm chart that installs ID Mapper, Self Service Portal, SPAR Service                    |
| OpenG2P GCTB                                             | Helm chart                                                                               |
| Reporting                                                | Helm charts                                                                              |

## Prerequisites

* K8s infrastructure is set up as given [here](k8s-infrastructure-setup/).
* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.

## Installation

Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0) repository, and continue the installation of each of the following components from the [kubernetes](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes) directory.

Choose and install the components needed for your cluster from the following.

### Kubernetes Infra Setup

TODO

### PostgreSQL

* Navigate to [kubernetes/postgresql ](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/postgresql)directory.
*   Run:

    ```bash
    ./install.sh
    ```

### Keycloak

* Prerequisites:
  * [PostgreSQL](./#postgresql) \[REQUIRED].
* Navigate to [kubernetes/keycloak](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/keycloak) directory.
*   Run:

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```
* After installation is successful, Keycloak Admin console will be accessible at https://keycloak.openg2p.sandbox.net, depending on the hostname given above.

### MinIO

* Navigate to [kubernetes/minio](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/minio) directory.
*   Run:

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```
* After installation is successful, MinIO console will be accessible at https://minio.openg2p.sandbox.net, depending on the hostname given above.
* Post-installation:
  * Once OpenG2P PBMS is installed, do the following:
    * Navigate to OpenG2P Documents (From OpenG2P Menu) -> Document Store.
    * Configure URL and password for this backend service (Like `http://minio.minio:9000`). Password and account-id/username can be obtained from the secrets in minio namespace.

### ODK Central

* Prerequisites:
  * [PostgreSQL](./#postgresql) \[REQUIRED].
* Navigate to [kubernetes/odk-central](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/odk-central) directory.
*   Run the following to install ODK helm chart.

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```
* After installation is successful, ODK Central will be accessible at https://odk.openg2p.sandbox.net, depending on the hostname given above.
*   Note: The above helm chart uses the following docker images built from [https://github.com/getodk/central/tree/v2023.1.0](https://github.com/getodk/central/tree/v2023.1.0), since ODK Central doesn't provide pre-built docker images for these.

    ```
    openg2p/odk-central-backend:v2023.1.0
    openg2p/odk-central-frontend:v2023.1.0
    openg2p/odk-central-enketo:v2023.1.0
    ```
* Post-installation:
  *   Exec into the service pod, and create a user (and promote if required).

      ```bash
      kubectl exec -it <service-pod> -- odk-cmd -u <email> user-create
      kubectl exec -it <service-pod> -- odk-cmd -u <email> user-promote
      ```

### Kafka

* Navigate to [kubernetes/kafka](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/kafka) directory.
*   Run:

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```
* After installation is successful, Kafka UI can be accessed at https://kafka.openg2p.sandbox.net, depending on the hostname given above.

### Logging and OpenSearch

* Navigate to [kubernetes/logging](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/logging) directory.
*   Run:

    ```bash
    SANDBOX_HOSTNAME=openg2p.sandbox.net \
        ./install.sh
    ```
* After installation is successful, OpenSearch Dashboards will be accessible at https://opensearch.openg2p.sandbox.net, depending on the hostname given above.
* Post-installation: TODO

### Keymanager Deployment

TODO

### Mock e-Signet Deployment

TODO

### PBMS

TODO

### Social Payments Account Registry Deployment

TODO

### G2P Cash Transfer Bridge Deployment

TODO

### Reporting

* Prerequisites:
  * Kafka \[REQUIRED]
  * PostgreSQL \[REQUIRED]
  * OpenG2P \[REQUIRED]
  * Logging \[REQUIRED]. (At least Elasticsearch is required)
* Clone [https://github.com/OpenG2P/openg2p-reporting](https://github.com/OpenG2P/openg2p-reporting/tree/1.1.0).
* Navigate to [scripts](https://github.com/OpenG2P/openg2p-reporting/tree/1.1.0/scripts) directory inside the above reporting repo.
*   Run the following to install reporting

    ```sh
    ./install.sh
    ```
* Do the following to import the dashboards present in [dashboards](https://github.com/OpenG2P/openg2p-reporting/tree/1.1.0/dashboards) folder:
  * Navigate to Kibana Stack Management -> Kibana Section -> Saved Objects.
  * Import all files in [dashboards](https://github.com/OpenG2P/openg2p-reporting/tree/1.1.0/dashboards) folder.

### All

WIP. If you wish to install all the components, run this from the [kubernetes](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes) directory.:

```
SANDBOX_HOSTNAME=openg2p.sandbox.net \
    ./install-all.sh
```

This includes the following components : TODO
