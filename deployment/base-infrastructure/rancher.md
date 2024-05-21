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

{% hint style="info" %}
It is highly recommended to set up a 3-node cluster for high availability. However, for the non-production environments, you may create a single node cluster to conserve resources.
{% endhint %}

Follow steps 1-5 in the guide given [here](openg2p-cluster/cluster-setup/).

## Rancher & Keycloak installation

*   Clone [https://github.com/OpenG2P/openg2p-deployment](https://github.com/OpenG2P/openg2p-deployment), and from [kubernetes/rancher](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/rancher) directory run the following: (Edit Hostnames according to need)&#x20;

    ```bash
    RANCHER_HOSTNAME=rancher.openg2p.org \
    KEYCLOAK_HOSTNAME=keycloak.openg2p.org \
        ./install.sh
    ```

## Keycloak-Rancher integration

Integrate Rancher and Keycloak using [Rancher Auth - Keycloak (SAML)](https://docs.ranchermanager.rancher.io/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/authentication-config/configure-keycloak-saml) guide.
