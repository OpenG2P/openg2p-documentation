---
description: >-
  The instructions here pertain to the deployment of PBMS 3.0 and associated
  components on the Kubernetes cluster using OpenG2P PBMS Helm chart.  All the
  components are installed in the same namespace.
---

# PBMS 3.0

## Prerequisites

Before you deploy, make sure the following are in place:

* [ ] Kubernetes cluster is up and running
* [ ] Nginx server is configured (skip this for OpenG2P-in-a-box)
* [ ] Namespace is created (via Rancher under a Project)
* [ ] Project Owner access on the OpenG2P namespace
* [ ] Istio gateway is set up in the namespace

## Installation using Rancher UI

1. **Log in** to the **Rancher Admin Console** and select your **target cluster**.
2.  Navigate to **Apps → Repositories** and click **Create** to add a new repository:

    * **Name:** `openg2p`
    * **Target HTTPS Index URL:** `https://openg2p.github.io/openg2p-helm/rancher`
    * Click **Create**

    <figure><img src="../../.gitbook/assets/image.png" alt=""><figcaption></figcaption></figure>
3. On the top-right, select the **namespace** where you want to install PBMS.
4.  To view prerelease charts (if required), click your **user avatar → Preferences → Include Prerelease Versions**.

    <figure><img src="../../.gitbook/assets/image (81).png" alt=""><figcaption></figcaption></figure>
5.  Navigate to **Apps → Charts** and locate the chart:

    * **Name:** _OpenG2P PBMS (3.0.0)_
    * **Description:** Installs PBMS Odoo + Postgres, Background Tasks, and Minio

    <figure><img src="../../.gitbook/assets/image (80).png" alt=""><figcaption></figcaption></figure>
6. Click the chart, choose **version 3.0.0**, and click **Install**.
7. On the next screen:
   * **Installation Name:** `openg2p-pbms` (or any preferred name)
   * Enable **Customise Helmbox before installation** → click **Next**
8. In the **General Settings** section, configure the following:
   * **Hostname:** Set the PBMS URL (e.g., `pbms.dev.openg2p.org`)
   * **PostgreSQL Host:** Provide the hostname of the PostgreSQL instance (or use the internal one if enabled)
   * **Keycloak Base URL:** Enter your Keycloak URL (e.g., `https://keycloak.openg2p.sandbox.net`)
   * **Email Service Name:** Provide the email service name used in PBMS
   * **OIDC Client ID:** Provide the OIDC client ID for PBMS (Odoo)
   * **OIDC Client Secret:** Provide the OIDC client secret for PBMS (Odoo)
9. In the **Registry Settings** section:
   * **Registry DB:** Provide the PostgreSQL database name for Registry
   * **Registry DB User:** Enter the DB username
   * **Registry DB Secret:** Specify the Kubernetes secret name containing the DB password
   * **Registry DB Secret Key:** Enter the key name within the secret containing the user password
10. In the **Background Task Settings** section (only visible if enabled):
    * **Celery Beat Producer Frequency:** Set frequency in seconds (e.g., `60`)
    * **Celery Beat Producer Batch Size:** Set the number of tasks per batch
    * **Celery Beat Producer Number of Tasks to Process:** Set total tasks per run
    * **Celery Workers G2P Bridge Base URL:** Provide the Bridge API URL used by Celery Workers
    * **Celery Workers Batch Size:** Set worker batch size
11. Configure **Minio Settings** (if applicable):
    * **Hostname:** e.g., `minio-pbms.dev.openg2p.org`
    * Enable **Install Minio** and **Enable Minio Persistence**
12. Click **Next** → go to **Helm Options**.
    * **Disable the Wait flag**
13. Click **Install**.
14. Monitor pods in your namespace until they reach the **Running** state.

    <div align="left"><figure><img src="../../.gitbook/assets/image (5).png" alt=""><figcaption></figcaption></figure></div>

## Installation using CLI

1.  Clone the [OpenG2P PBMS Deployment Repository](pbms-helm-charts.md)

    ```
    git clone https://github.com/OpenG2P/openg2p-pbms-gen2-deployment.git
    cd openg2p-pbms-gen2-deployment/charts
    ```


2.  Update Helm Dependencies

    ```
    helm dependency update openg2p-pbms
    ```


3.  Review and update `values.yaml` as needed:

    * `global.hostname`: Public hostname for PBMS (e.g., `pbms.dev.openg2p.org`)
    * `global.keycloakBaseUrl`: Base URL for Keycloak authentication
    * `global.postgresqlHost`: PostgreSQL host (e.g., `openg2p-commons-postgresql`)
    * `global.registryDB*` and `global.pbmsDB*`: Registry and PBMS database credentials
    * `global.minioInstallationName`: Minio instance for file storage
    * `odoo.image.tag`: PBMS version or custom image tag
    * `openg2p-pbms-bg-task-celery-*`: Celery environment variables (frequency, batch size, etc.)
    * `istio.virtualservice.host`: Hostname when Istio is enabled

    {% hint style="info" %}
    You can override values inline using `--set` or pass a custom file with `-f`.
    {% endhint %}


4.  Install the Helm chart

    ```
    helm install <release-name> openg2p-pbms \
      -f ./values.yaml \
      -n <namespace>
    ```

    Replace `<release-name>` with a unique name (e.g., `pbms-dev`) and `<namespace>` with the target Kubernetes namespace.
5.  Verify deployment

    ```
    helm status <release-name> -n <namespace>
    kubectl get pods,svc -n <namespace>
    ```


6.  Upgrade the deployment when changing configuration

    ```
    helm upgrade <release-name> openg2p-pbms \
      -f ./values.yaml \
      -n <namespace>
    ```

    \
    You can view current values using:

    ```
    helm get values <release-name> -n <namespace>
    ```

{% hint style="info" %}
To uninstall PBMS from command line:

```
helm uninstall <release-name> -n <namespace>
```
{% endhint %}

## Post-Installation Configuration

1.  Get the Odoo service URL (usually from ingress or Istio VirtualService):

    ```
    kubectl get svc,ingress -n <namespace>
    ```


2. Log in to Odoo using admin credentials (configured in Keycloak or Odoo setup).
3. Activate the PBMS modules under **Apps**:
   * Ensure “OpenG2P PBMS Core”, “OpenG2P PBMS Background Tasks”, and other required extensions are installed.
   *   Update module list if they aren’t visible:

       ```
       kubectl exec -it <odoo-pod-name> -n <namespace> -- \
         odoo -d <database-name> -u all --stop-after-init
       ```


4. Verify background workers:
   *   Check Celery workers and beat scheduler pods:

       ```
       kubectl get pods -n <namespace> | grep celery
       ```
   * Confirm task queues are registered correctly.\

5. Validate Redis and Minio connectivity:
   * Ensure Redis pod is running and reachable by the Celery worker.
   * Verify Minio access credentials match the Helm values and Odoo configuration.
6. Confirm database migrations:
   *   Review logs of Odoo pod for any migration errors:

       ```
       kubectl logs <odoo-pod-name> -n <namespace>
       ```


7.  (Optional) Apply PBMS demo or seed data:

    ```
    kubectl exec -it <odoo-pod-name> -n <namespace> -- \
      odoo -d <database-name> -i g2p_pbms_demo
    ```
