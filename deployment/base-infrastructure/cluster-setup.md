---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Kubernetes Cluster

OpenG2P modules and components are recommended to be run on Kubernetes (K8s), because of ease-of-use, management, and security features that K8s provides.

This document provides instructions to set up a K8s Cluster on which OpenG2P Modules and other components can be installed.

## Prerequisites

* [Hardware Requirements](../hardware-requirements.md)
* The following tools are installed on all the nodes and the client machine.
  * `wget` , `curl` , `kubectl` , `istioctl` , `helm` , `jq`

## Firewall Requirements

* Set up firewall rules on each node according to the following table. The exact method to set up the firewall rules will vary from cloud to cloud and on-prem. (For example on AWS, EC2 security groups can be used. For on-prem cluster, ufw can be used and so on)

<table><thead><tr><th width="126">Protocol</th><th width="144">Port</th><th width="272">Should be accessible by only</th><th>Description</th></tr></thead><tbody><tr><td>TCP</td><td>22</td><td></td><td>SSH</td></tr><tr><td>TCP</td><td>80</td><td></td><td>Postgres ports</td></tr><tr><td>TCP</td><td>443</td><td></td><td>Postgres ports</td></tr><tr><td>TCP</td><td>5432</td><td></td><td>Postgres port</td></tr><tr><td>TCP</td><td>9345</td><td>RKE2 agent nodes</td><td>Kubernetes API</td></tr><tr><td>TCP</td><td>6443</td><td>RKE2 agent nodes</td><td>Kubernetes API</td></tr><tr><td>UDP</td><td>8472</td><td>RKE2 server and agent nodes</td><td>Required only for Flannel VXLAN</td></tr><tr><td>TCP</td><td>10250</td><td>RKE2 server and agent nodes</td><td>kubelet</td></tr><tr><td>TCP</td><td>2379</td><td>RKE2 server nodes</td><td>etcd client port</td></tr><tr><td>TCP</td><td>2380</td><td>RKE2 server nodes</td><td>etcd peer port</td></tr><tr><td>TCP</td><td>9796</td><td>Cluster nodes over internal network. </td><td>Prometheus metrics</td></tr><tr><td>TCP</td><td>30000:32767</td><td>RKE2 server and agent nodes</td><td>NodePort port range</td></tr></tbody></table>

* For example, this is how you can use `ufw` to set up the firewall on each cluster node.
  * SSH into each node, and change to superuser
  *   Run the following command for each rule in the above table

      ```
      ufw allow from <from-ip-range-allowed> to any port <port/range> proto <tcp/udp>
      ```
  *   Example:

      ```
      ufw allow from any to any port 22 proto tcp
      ufw allow from 10.3.4.0/24 to any port 9345 proto tcp
      ```
  *   Enable ufw:

      ```
      ufw enable
      ufw default deny incoming
      ```
* Additional Reference: [RKE2 Networking Requirements](https://docs.rke2.io/install/requirements#networking)

## Installation on AWS cloud

If you are using AWS only to get EC2 nodes, and you want to set up the K8s cluster manually, move to the [On-premises Setup](cluster-setup.md#installation-on-premises-on-prem).

## Installation on-premises (on-prem)

### k8s cluster

The following section uses [RKE2](https://docs.rke2.io) to set up the K8s cluster.

* Decide the number of K8s control-plane nodes (server nodes) and worker nodes (agent nodes).
  * Choose an odd number of control-plane nodes. For example, for a 3-node k8s cluster, choose 1 control-plane node and 2 worker nodes. For a 7-node k8s cluster, choose 3 control-plane nodes and 4 worker nodes.
* The following setup has to be done on each node on the cluster.
  * SSH into the node
  *   Create the rke2 config directory

      ```
      mkdir -p /etc/rancher/rke2
      ```
  * Create a `config.yaml` file in the above directory, using one of the following config file templates:
    * For the first control-plane node, use [rke2-server.conf.primary.template](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/rke2/rke2-server.conf.primary.template)
    * For subsequent control-plane nodes, use [rke2-server.conf.subsequent.template](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/rke2/rke2-server.conf.primary.template)
    * For worker nodes, use [rke2-agent.conf.template](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/rke2/rke2-agent.conf.template)
  * Edit the above `config.yaml` file with the appropriate names, IPs, and tokens
  *   Run this to download rke2.

      ```
      curl -sfL https://get.rke2.io | sh -
      ```
  * Run this to start rke2:
    *   On the control-plane node, run:

        ```
        systemctl enable rke2-server
        systemctl start rke2-server
        ```
    *   On the worker node, run:

        ```
        systemctl enable rke2-agent
        systemctl start rke2-agent
        ```
* To export KUBECONFIG, run (only on control-plane nodes):
  * ```
    echo -e 'export PATH="$PATH:/var/lib/rancher/rke2/bin"\nexport KUBECONFIG="/etc/rancher/rke2/rke2.yaml"' >> ~/.bashrc
    source ~/.bashrc
    ```
  * ```
    kubectl get nodes
    ```
* Additional Reference: [RKE2 High Availability Installation](https://docs.rke2.io/install/ha)

### Cluster import into Rancher

This section assumes a Rancher server has already been set up and operational. [Rancher Server Setup](rancher.md) in case not already done.

* Navigate to Cluster Management section in Rancher
* Click on `Import Existing` cluster. And follow the steps to import the new OpenG2P cluster
* After importing, download kubeconfig for the new cluster from rancher (top right on the main page), to access the cluster through kubectl from user's machine (client), without SSH

### NFS provisioner&#x20;

This section assumes an NFS server has already been set up and operational, which meets the requirements, as given in [NFS Server](nfs-server.md). The NFS server is used to provide persistent storage volumes to K8s cluster.

### Longhorn&#x20;

This installation only applies if Longhorn is used as storage. This may be skipped if you are using NFS.

[Longhorn Install as a Rancher App](https://longhorn.io/docs/1.3.2/deploy/install/install-with-rancher/)

### Istio&#x20;

* The following setup can be done from the client machine. This installs Istio Operator, Istio Service Mesh, Istio Ingressgateway components.
*   From [kubernetes/istio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio) directory, configure the istio-operator.yaml, and run;

    ```
    istioctl operator init
    kubectl apply -f istio-operator.yaml
    ```

    *   If an external Loadbalancer is being used, then use the `istio-operator-external-lb.yaml` file.

        ```
        kubectl apply -f istio-operator-external-lb.yaml
        ```
    * Configure the operator.yaml with any further configuration
*   Gather Wildcard TLS certificate and key and run;\
    Note: To create TLS certificates refer [here](https://docs.openg2p.org/v/latest/deployment/deployment-guide/ssl-certificates-using-letsencrypt)

    ```
    kubectl create secret tls tls-openg2p-ingress -n istio-system \
        --cert=<CERTIFICATE PATH> \
        --key=<KEY PATH>
    ```
*   Create istio gateway for all hosts using this command:

    ```
    kubectl apply -f istio-gateway.yaml
    ```

    *   If using external loadbalancer/external TLS termination, use the `istio-gateway-no-tls.yaml` file

        ```
        kubectl apply -f istio-gateway-no-tls.yaml
        ```

### Adding new nodes

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
