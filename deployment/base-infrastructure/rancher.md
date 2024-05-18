---
description: Installation of Rancher and Keycloak on Kubernetes cluster
layout:
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Rancher Cluster

Rancher is used to manage multiple clusters. Being a critical component of cluster administration it is highly recommended that Rancher itself runs on a Kubernetes cluster with sufficient replication for high availability and avoiding a single point of failure. The guide here provides instructions to install both Rancher server and Keycloak which is required for system administration of clusters.&#x20;

{% hint style="info" %}
To conserve resources Rancher may be run on a single node cluster, however, there is risk with this approach. Ideally, at least 2 nodes must be used
{% endhint %}

To deploy Rancher carry out the following steps:

1. Make sure [NFS server](nfs-server.md) is already installed.
2. Install Kubernetes (K8s) cluster&#x20;
3. Install Rancher
4. Install Keycloak
5. Integrate Keycloak with Rancher

## K8s cluster installation

Follow steps 1-4 in the guide given [here](openg2p-cluster/cluster-setup/).

*   In step 3 of the K8s setup, delete these lines from the final RKE2 `config.yaml` file. This will allow RKE2 to install the Nginx Ingress Controller instead of Istio. (On this cluster Istio is not necessary as there are very few components to manage).

    ```
    node-label: "shouldInstallIstioIngress=true"
    disable:
      - rke2-ingress-nginx
    ```

{% hint style="info" %}
It is highly recommended to set up a 3-node cluster for high availability. However, for the non-production environments, you may create a single node cluster to conserve resources.
{% endhint %}

## Rancher installation

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

    * Configure/Create TLS secret accordingly.\
      Note: To create TLS certificates refer [here](https://docs.openg2p.org/v/latest/deployment/deployment-guide/ssl-certificates-using-letsencrypt)

    ```bash
    kubectl create secret tls tls-rancher-ingress -n cattle-system \
        --cert=path/to/cert/file \
        --key=path/to/key/file
    ```

## Keycloak installation

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

## Keycloak-Rancher integration

Integrate Rancher and Keycloak using [Rancher Auth - Keycloak (SAML)](https://docs.ranchermanager.rancher.io/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/authentication-config/configure-keycloak-saml) guide.
