---
description: Guide to add nodes to an existing Kubernetes cluster
---

# Adding Nodes to Cluster

Below are the steps to add more nodes to the Kubernetes cluster.

* From [kubernetes/rke2](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/rke2) directory, use the `rke2-server.conf.subsequent.template` or `rke2-agent.conf.template` based on whether the new node is control plane node or worker node. Copy this file to `/etc/rancher/rke2/config.yaml` in the new node.
* Configure the config.yaml with relevant values.
*   Run the following to set the RKE2 version. Make sure this version is the same across all the nodes. (Refer to [RKE2 Releases](https://github.com/rancher/rke2/releases). Use `rke2 --version` on an existing node to get the version.)

    ```
    export INSTALL_RKE2_VERSION="v1.30.0+rke2r1"
    ```
*   Run the below command to download RKE2.

    ```
    curl -sfL https://get.rke2.io | sh -
    ```
*   Run the below commands to start RKE2 node.

    ```
    systemctl enable rke2-server
    systemctl start rke2-server
    ```
