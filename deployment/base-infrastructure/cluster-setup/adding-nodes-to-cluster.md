---
description: Guide to add nodes to an existing Kubernetes cluster
---

# Adding Notes to Cluster

To add more nodes to the Kubernetes cluster:

* From [kubernetes/rke2](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/rke2) directory, take either the `rke2-server.conf.subsequent.template` or `rke2-agent.conf.template` based on whether the new node is control plane node or Worker node. Copy this file to `/etc/rancher/rke2/config.yaml` in the new node.
* Configure the the config.yaml with relevant values
*   Run this to download rke2.

    ```
    curl -sfL https://get.rke2.io | sh -
    ```
*   Run this to start rke2 node:

    ```
    systemctl enable rke2-server
    systemctl start rke2-server
    ```
