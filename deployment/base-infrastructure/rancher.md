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

# Rancher

Rancher is used to manage multiple clusters. Being a critical component of cluster administration it is highly recommended that Rancher itself runs on a Kubernetes cluster with sufficient replication for high availability and avoiding a single point of failure.

{% hint style="info" %}
For simplicity of deployment and to conserve compute resources Rancher may be installed on a node with just the Docker. However, Kubernetes based deployment is preferred for above reasons
{% endhint %}

## Installation using Kubernetes

### Prerequisites

One Virtual machine running on the same network as the rest of the nodes, and has access to them. For recommended configuration of the VM refer to [Hardware Requirements](../k8s-cluster-requirements.md)

### Kubernetes cluster setup

* SSH into the node
*   Create the rke2 config directory:

    ```
    mkdir -p /etc/rancher/rke2
    ```
* Create a `config.yaml` file in the above directory, using this config file template; [rke2-server.conf.primary.template](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/rke2/rke2-server.conf.primary.template)
*   Edit the above config.yaml file with the appropriate names and IPs. IMPORTANT: Remove the section for disabling ingress-nginx in this config file.

    ```
    curl -sfL https://get.rke2.io | sh -
    ```
*   Start rke2 using this

    ```
    systemctl enable rke2-server
    ```
* Download and install `kubectl` and `helm`. And execute this:&#x20;
  * ```
    echo -e 'export PATH="$PATH:/var/lib/rancher/rke2/bin"\nexport KUBECONFIG="/etc/rancher/rke2/rke2.yaml"' >> ~/.bashrc
    source ~/.bashrc
    ```
  * ```
    kubectl get nodes
    ```

{% hint style="info" %}
It is recommended to set up a double-node cluster for high availability. However, for the non-production environments, you may create a single node cluster to conserve resources
{% endhint %}

### Rancher installation

*   To install Rancher use this (hostname to be edited in the below command):

    ```bash
    helm repo add rancher-latest https://releases.rancher.com/server-charts/latest
    helm repo update
    helm install rancher rancher-latest/rancher \
      --namespace cattle-system \
      --create-namespace \
      --set hostname=rancher.openg2p.org \
      --set ingress.tls.source=tls-rancher-ingress
    ```

    * Configure/Create TLS secret accordingly.

    ```bash
    kubectl create secret tls tls-rancher-ingress -n cattle-system \
        --cert=path/to/cert/file \
        --key=path/to/key/file
    ```

### Longhorn Setup

* Install[ Longhorn as a Rancher App](https://longhorn.io/docs/1.3.2/deploy/install/install-with-rancher/)

### Keycloak setup

* From [kubernetes/rancher](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/rancher) folder, run the following to install Keycloak (hostname to be edited in the below command)
* ```bash
  helm repo add bitnami https://charts.bitnami.com/bitnami
  helm repo update
  helm install keycloak bitnami/keycloak \
    -n keycloak \
    --create-namespace \
    --version "7.1.18" \
    --set ingress.hostname=keycloak.openg2p.org \
    --set ingress.extraTls[0].hosts[0]=keycloak.openg2p.org \
    -f keycloak-values.yaml
  ```

### Integrate Rancher and Keycloak

Integrate Rancher and Keycloak using [Rancher Auth - Keycloak (SAML)](https://docs.ranchermanager.rancher.io/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/authentication-config/configure-keycloak-saml) guide.

## Installation using Docker

Refer to [Installing Rancher using Docker](https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade/other-installation-methods/rancher-on-a-single-node-with-docker) guide.
