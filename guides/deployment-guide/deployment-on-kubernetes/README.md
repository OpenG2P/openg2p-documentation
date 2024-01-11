# Deployment on Kubernetes

## Introduction

The guide here provides instructions to deploy OpenG2P components on Kubernetes (K8s) cluster (Refer to [Deployment Architecture](../../../platform/deployment/deployment-architecture.md)).  The following components are installed:

| Module/Component                                                | Comments                                                                                 |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| <p></p><p>Kubernetes cluster</p><p>Rancher</p><p>NFS server</p> | Required for all components as this is the common infrastructure used by all.            |
| PostgreSQL                                                      | Required for all components. A single server instance may be used housing all databases. |
| MinIO                                                           | Required for PBMS and GCTB only                                                          |
| Keycloak                                                        | Required for PBMS, Social Registry                                                       |
| MOSIP Key Manager                                               | Required for PBMS, Social Registry                                                       |
| ODK Central                                                     | Required for Registration Toolkit                                                        |
| e-Signet                                                        | Required for SPAR and optionally for PBMS                                                |
| Kafka                                                           | Required for Monitoring & Reporting                                                      |
| Elasticsearch                                                   | Required for Monitoring & Reporting                                                      |
| OpenG2P PBMS                                                    | Helm chart that installs Odoo, SMTP server                                               |
| OpenG2P SPAR                                                    | Helm chart that installs ID Mapper, Self Service Portal, SPAR Service                    |
| OpenG2P GCTB                                                    | Helm chart                                                                               |

## Prerequisites

* K8s infrastructure is set up as given [here](k8s-infrastructure-setup/).
* The following utilities/tools must be present on the user's machine.
  * `kubectl`, `istioctl`, `helm`, `jq`, `curl`, `wget`, `git`, `bash`, `envsubst`.

## Installation

Clone the [https://github.com/openg2p/openg2p-deployment](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0) repository, and continue the installation of each of the following components from the [kubernetes](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes) directory.

Choose and install the components needed for your cluster from the following. If you wish to install all the components below, run this from the [kubernetes](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes) directory (This doesn't include [Reporting](./#reporting)):

```
OPENG2P_HOSTNAME=openg2p.sandbox.net \
ODK_HOSTNAME=odk.openg2p.sandbox.net \
KEYCLOAK_HOSTNAME=keycloak.openg2p.sandbox.net \
KAFKA_UI_HOSTNAME=kafka.openg2p.sandbox.net \
KIBANA_HOSTNAME=kibana.openg2p.sandbox.net \
MINIO_HOSTNAME=minio.openg2p.sandbox.net \
    ./install-all.sh
```

### PostgreSQL

* Navigate to [kubernetes/postgresql ](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/postgresql)directory.
*   Run:

    ```bash
    ./install.sh
    ```

### PBMS

* Prerequisites:
  * PostgreSQL \[REQUIRED]
  * Minio \[Optional]
  * ODK \[Optional]
  * Packaged OpenG2P docker. [Packaging Instructions](../packaging-openg2p-docker.md). \[Optional]
* Navigate to [kubernetes/openg2p](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/openg2p) directory.
*   Run: (This installs the reference package dockers)

    <pre class="language-bash"><code class="lang-bash"><strong>OPENG2P_HOSTNAME=openg2p.sandbox.net \
    </strong>    ./install.sh
    </code></pre>

    *   If use already have a custom packaged docker image or tag use:

        ```bash
        OPENG2P_HOSTNAME=openg2p.sandbox.net \
        OPENG2P_ODOO_IMAGE_REPO=<docker image name> \
        OPENG2P_ODOO_IMAGE_TAG=<docker image tag> \
            ./install.sh
        ```
* Post installation: Refer to [Post Install Configuration](pbms-deployment/post-install-instructions.md)

### ODK

* Prerequisites:
  * PostgreSQL \[REQUIRED]
* Navigate to [kubernetes/odk-central](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/odk-central) directory.
*   Run the following to install ODK helm chart.

    ```bash
    ODK_HOSTNAME=odk.openg2p.sandbox.net \
        ./install.sh
    ```

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

### Minio

* Navigate to [kubernetes/minio](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/minio) directory.
*   Run:

    ```bash
    MINIO_HOSTNAME=minio.openg2p.sandbox.net \
        ./install.sh
    ```
* Post-installation:
  * Once OpenG2P is installed, do the following:
    * Navigate to OpenG2P Documents (From OpenG2P Menu) -> Document Store.
    * Configure URL and password for this backend service (Like `http://minio.minio:9000`). Password and account-id/username can be obtained from the secrets in minio namespace.

### Keycloak

* Navigate to [kubernetes/keycloak](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/keycloak) directory.
*   Run:

    ```bash
    OPENG2P_HOSTNAME=openg2p.sandbox.net
    KEYCLOAK_HOSTNAME=keycloak.openg2p.sandbox.net \
        ./install.sh
    ```

### Kafka

* Navigate to [kubernetes/kafka](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/kafka) directory.
*   Run:

    ```bash
    KAFKA_UI_HOSTNAME=kafka.openg2p.sandbox.net \
        ./install.sh
    ```

### Logging and Elasticsearch

* Navigate to [kubernetes/logging](https://github.com/OpenG2P/openg2p-deployment/tree/1.1.0/kubernetes/logging) directory.
*   Run:

    ```bash
    KIBANA_HOSTNAME=kibana.openg2p.sandbox.net \
        ./install.sh
    ```

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

### Social Payments Account Registry Deployment

TODO

### G2P Cash Transfer Bridge Deployment

TODO

### Keymanager Deployment

TODO

### Esignet Deployment

TODO
