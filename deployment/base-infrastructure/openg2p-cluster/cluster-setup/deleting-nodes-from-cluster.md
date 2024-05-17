---
description: Guide to delete nodes from existing Kubernetes cluster
---

# Deleting Nodes from Cluster

To delete  nodes from Kubernetes cluster:

* Before you delete the node, make sure the **PodDisruptionBudget** is set to "**0**" on deleting node.  Click [here](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) for more information.&#x20;
*   To drain the node from the cluster, run the command below.&#x20;

    ```
    kubectl drain <nodename> --ignore-daemonsets --delete-emptydir-data
    ```
*   Once done draining the node, run the command below to delete it from the cluster.

    ```
    kubectl delete node <nodename>
    ```
* After deleting the node, check your Kubernetes cluster to ensure the node has been deleted.
