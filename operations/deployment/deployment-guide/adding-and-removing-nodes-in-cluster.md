---
description: Guide to Adding and Removing Nodes from an Existing Kubernetes Cluster
---

# Adding and Removing Nodes in Cluster

{% hint style="info" %}
**Updated automation guide:** For the current OpenG2P production add-node workflow (bundled scripts, step-by-step), see **[Add Node](add-node/README.md)**. Optional AWS EC2 provisioning is documented separately at **[AWS Add-Node Provisioning (optional)](add-node/aws-provisioning.md)**.
{% endhint %}

## Adding Nodes to Cluster

Below are the steps to add new nodes to an existing Kubernetes cluster.

* From [kubernetes/rke2](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/rke2) directory, use the `rke2-server.conf.subsequent.template` or `rke2-agent.conf.template` based on whether the new node is control plane node or worker node. Copy this file to `/etc/rancher/rke2/config.yaml` in the new node.
* Configure the config.yaml with relevant values.
*   Run the following to set the RKE2 version. Make sure this version is the same across all the nodes. (Refer to [RKE2 Releases](https://github.com/rancher/rke2/releases). Use `rke2 --version` on an existing node to get the version.)

    <a class="button secondary">Copy</a>

    ```
    export INSTALL_RKE2_VERSION="v1.28.9+rke2r1"
    ```
*   Run the below command to download RKE2.

    <a class="button secondary">Copy</a>

    ```
    curl -sfL https://get.rke2.io | sh -
    ```
*   Run the below commands to start RKE2 node.

    <a class="button secondary">Copy</a>

    ```
    systemctl enable rke2-server
    systemctl start rke2-server
    ```

## Deleting Nodes from Cluster

Follow the steps below to remove a node from the Kubernetes cluster.

* Before you delete the node, make sure the **PodDisruptionBudget** is set to "**0**" on deleting node. Click [here](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) for more information.
*   To drain the node from the cluster, run the command below.

    <a class="button secondary">Copy</a>

    ```
    kubectl drain <nodename> --ignore-daemonsets --delete-emptydir-data
    ```
*   Once done draining the node, run the command below to delete it from the cluster.

    <a class="button secondary">Copy</a>

    ```
    kubectl delete node <nodename>
    ```
* After deleting the node, check your Kubernetes cluster to ensure the node has been deleted.
* Make sure the node IP is removed from the LoadBalancer/NGINX to avoid intermittent issues in the environment.



[<br>](https://docs.openg2p.org/1.3/deployment/base-infrastructure/openg2p-cluster/cluster-setup/adding-nodes-to-cluster)
