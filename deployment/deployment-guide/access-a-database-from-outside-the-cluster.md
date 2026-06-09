---
description: Post-deployment guide
---

# Access a Database from Outside the Cluster

This guide covers connecting to a database (or any in-cluster service — MinIO, Redis, Kafka, …) from outside the cluster using `kubectl` port-forwarding.

{% hint style="warning" %}
**PostgreSQL is different in production.** In the three-node production deployment, PostgreSQL is the **host install on the Storage node** — it is *not* an in-cluster `*-postgresql-0` pod, so `kubectl port-forward` to a PG pod won't work. To reach the host PostgreSQL from your laptop, use the **SSH tunnel** described in [Environment Setup → Accessing host PostgreSQL from your laptop](../../operations/deployment/environment-setup-multi-node.md#accessing-host-postgresql-from-your-laptop). The `kubectl port-forward` method below applies to **in-cluster services** (MinIO, Redis, Kafka, etc.) — and to PostgreSQL only on a sandbox / legacy in-cluster-PG install.
{% endhint %}

## Prerequisites

1. Installation and configuration.

The steps to install and configure kubectl to access the Kubernetes Cluster in your machine are given below.

*   Install kubectl.

    ```bash
    sudo snap install kubectl --classic
    ```
*   Check the kubectl version.

    ```bash
    kubectl version --client
    ```
*   Configure kubectl and create a .kube directory in your home folder.

    ```bash
     mkdir -p $HOME/.kube 
    ```
* Download the kube-config file from Rancher UI.
*   Place the kube-config file in the .kube folder.

    ```bash
    cp /path/to/your/kube-config $HOME/.kube/config
    ```
*   Set permissions for the kube-config file.

    ```bash
    chmod 400 $HOME/.kube/config
    ```
*   Export the KUBECONFIG environment variable.

    ```bash
    export KUBECONFIG="$HOME/.kube/config" 
    ```
*   Verify the configuration.

    ```bash
    kubectl config view
    ```

2. You must have access to the Kubernetes Cluster.
3. You must have the necessary permissions to perform port-forwarding to the database service in the Kubernetes Cluster.

## Procedure (in-cluster services)

Ensure the cluster kubeconfig is set on your machine, then port-forward the in-cluster service you want to reach.

*   List the relevant pods/services in the environment namespace:

    ```bash
    kubectl get pods,svc -n <namespace of env>
    # e.g. an in-cluster MinIO, Redis, or Kafka service
    ```
*   Port-forward the service (or pod) to a local port:

    ```bash
    kubectl -n <namespace> port-forward svc/<service> <local-port>:<service-port>
    # e.g. MinIO console:  kubectl -n prod port-forward svc/commons-minio 9001:9001
    ```
*   Connect with the appropriate client on `localhost:<local-port>` (e.g. a browser for MinIO, `redis-cli`, etc.).

For an **in-cluster PostgreSQL** (sandbox or a legacy in-cluster-PG install), the same pattern applies:

    ```bash
    kubectl -n <namespace> port-forward svc/<release>-postgresql 5432:5432
    psql -h localhost -p 5432 -U <dbuser> -d <database>
    ```

For the **host PostgreSQL** in three-node production, use the SSH tunnel instead — see the warning at the top of this page.

    <br>

Notes

* The `kubectl port-forward` must keep running in the foreground while you are accessing the database.
* Ensure that your local port (e.g., 5432) is not being used by another service on your local machine.&#x20;
