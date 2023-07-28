---
description: Work in progress
---

# K8s Cluster Setup

## Introduction

The following guide uses [RKE2](https://docs.rke2.io) to set up the Kubernetes (K8s) cluster.

## Prerequisites

* The requirements for setting up the cluster are met as given [here](k8s-cluster-requirements.md).
* The following tools are installed on all the nodes and the client machine.
  * `ufw` , `wget` , `curl` , `kubectl` , `istioctl` , `helm` , `jq`

## Firewall setup

*   Set up firewall rules on each node. The following uses `ufw` to setup firewall.

    * SSH into each node, and change to superuser.
    * Run the following command for each rule in the following table

    ```
    ufw allow from <from-ip-range-allowed> to any port <port/range> proto <tcp/udp>
    ```

    * Example

    ```
    ufw allow from any to any port 22 proto tcp
    ufw allow from 10.3.4.0/24 to any port 9345 proto tcp
    ```

    * Enable ufw.

    ```bash
    ufw enable
    ufw default deny incoming
    ```

    * Additional Reference: [RKE2 Networking Requirements](https://docs.rke2.io/install/requirements#networking)

<table><thead><tr><th width="126">Protocol</th><th width="144">Port</th><th width="272">Should be accessible by only</th><th>Description</th></tr></thead><tbody><tr><td>TCP</td><td>22</td><td></td><td>SSH</td></tr><tr><td>TCP</td><td>80</td><td></td><td>Postgres ports</td></tr><tr><td>TCP</td><td>443</td><td></td><td>Postgres ports</td></tr><tr><td>TCP</td><td>5432:5434</td><td></td><td>Postgres ports</td></tr><tr><td>TCP</td><td>9345</td><td>RKE2 agent nodes</td><td>Kubernetes API</td></tr><tr><td>TCP</td><td>6443</td><td>RKE2 agent nodes</td><td>Kubernetes API</td></tr><tr><td>UDP</td><td>8472</td><td>RKE2 server and agent nodes</td><td>Required only for Flannel VXLAN</td></tr><tr><td>TCP</td><td>10250</td><td>RKE2 server and agent nodes</td><td>kubelet</td></tr><tr><td>TCP</td><td>2379</td><td>RKE2 server nodes</td><td>etcd client port</td></tr><tr><td>TCP</td><td>2380</td><td>RKE2 server nodes</td><td>etcd peer port</td></tr><tr><td>TCP</td><td>30000:32767</td><td>RKE2 server and agent nodes</td><td>NodePort port range</td></tr></tbody></table>

## K8s setup

* The following setup has to be done for each cluster node.
* Choose odd number of server nodes. Example if there are 3 nodes, choose 1 server node and two agent nodes. If there are 7 nodes, choose 3 server nodes and 4 agent nodes.
* Clone the [https://github.com/OpenG2P/openg2p-deployment](https://github.com/OpenG2P/openg2p-deployment) and go to [infra](https://github.com/OpenG2P/openg2p-deployment/tree/main/infra) directory.
* For the first server node:
  * Configure `rke2-server.conf.primary.template`,
  * SSH into the node. Place the file to this path: `/etc/rancher/rke2/config.yaml`. Create the directory if not present already. `mkdir -p /etc/rancher/rke2` .
  *   Run this to download rke2.

      ```
      curl -sfL https://get.rke2.io | sh -
      ```
  *   Run this to start rke2 server:

      ```
      systemctl enable rke2-server
      systemctl start rke2-server
      ```
* For subsequent server and agent nodes:
  * Configure `rke2-server.conf.subsequent.template` or `rke2-agent.conf.template`, with relevant ips for each node.
  * SSH into each node place the relevant file to this path: `/etc/rancher/rke2/config.yaml`, based on whether its a worker node, or control-plane node. (If worker use agent file. If control-plane use server file).
  *   Run this to get download rke2.

      ```
      curl -sfL https://get.rke2.io | sh -
      ```
  *   To start rke2, use this

      ```
      systemctl enable rke2-server
      systemctl start rke2-server
      ```

      or, based on server or agent.

      ```
      systemctl enable rke2-agent
      systemctl start rke2-agent
      ```
* Execute these commands on a server node.
  * ```
    echo -e 'export PATH="$PATH:/var/lib/rancher/rke2/bin"\nexport KUBECONFIG="/etc/rancher/rke2/rke2.yaml"' >> ~/.bashrc
    source ~/.bashrc
    ```
  * ```
    kubectl get nodes
    ```
* Additional Reference: [RKE2 High Availabilty Installation](https://docs.rke2.io/install/ha)

## Cluster import into Rancher.

* This section assumes a Rancher server has already been setup and operational. [Rancher Server Setup](rancher-server-setup.md) in case not already done.
* Navigate to Cluster Management section in Rancher.
* Click on `Import Existing` cluster. And follow the steps to import the newly created cluster.
* After Rancher import, do not use the the kubeconfig from server anymore. Use it only via downloading kubeconfig from rancher.

## Longhorn setup

* Use this to install longhorn. [Longhorn Install as a Rancher App](https://longhorn.io/docs/1.3.2/deploy/install/install-with-rancher/)

## Istio setup

* The following setup can be done from the client machine. This install Istio Operator, Istio Service Mesh, Istio Ingressgateway components.
*   From [infra](https://github.com/OpenG2P/openg2p-deployment/tree/main/infra) directory, configure the istio-operator.yaml, and run;

    ```
    istioctl operator init
    kubectl apply -f istio-operator.yaml
    ```

    *   If an external Loadbalancer is being used, then use the `istio-operator-external-lb.yaml` file.

        ```
        kubectl apply -f istio-operator-external-lb.yaml
        ```
    * Configure the operator.yaml with any further configuration.
*   Gather Wildcard TLS certificate and key and run;

    ```
    kubectl create secret tls tls-openg2p-ingress -n istio-system \
        --cert=<CERTIFICATE PATH> \
        --key=<KEY PATH>
    ```
*   Create istio gateway for all hosts using this command:

    ```
    kubectl apply -f istio-gateway.yaml
    ```

    *   If using external loadbalancer/external TLS termination, use the `istio-gateway-no-tls.yaml` file.

        ```
        kubectl apply -f istio-gateway-no-tls.yaml
        ```

## Adding new nodes

* From [infra](https://github.com/OpenG2P/openg2p-deployment/tree/main/infra) directory, take either the `rke2-server.conf.subsequent.template` or `rke2-agent.conf.template` based on whether the new node is control plane node or Worker node. Copy this file to `/etc/rancher/rke2/config.yaml` in the new node.
* Configure the the config.yaml with relevant values.
*   Run this to download rke2.

    ```
    curl -sfL https://get.rke2.io | sh -
    ```
*   Run this to start rke2 node:

    ```
    systemctl enable rke2-server
    systemctl start rke2-server
    ```
