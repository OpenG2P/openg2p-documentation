---
description: >-
  This guide contains instructions on how to connect to a database outside the
  cluster
---

# Access a Database Outside the Cluster

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

## Procedure

Ensure that the cluster kubeconfig is set on your machine and follow the commands below to connect to the respective database.

*   Get the database services running in the cluster using the command below.

    ```bash
    kubectl get pods -n <namespace of env> | grep postgresql-0 
    ex : kubectl get pods -n dev | grep postgresql-0
    ```
*   Confirm the database you want to connect. Perform port-forwarding for the corresponding service using the `kubectl` command.

    ```bash
    kubectl port-forward pod/<pod-name> <local-port>:<pod-port>
    ex : kubectl port-forward -n dev pod/social-registry-postgresql-0 5432:5432
    ```
*   Connect to the database.

    ```bash
    psql -h localhost -p 5432 -U <dbuser> -d <database>
    ```

    \


Notes

* The `kubectl port-forward` must keep running in the foreground while you are accessing the database.
* Ensure that your local port (e.g., 5432) is not being used by another service on your local machine.&#x20;
