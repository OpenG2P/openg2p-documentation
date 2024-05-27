---
description: Getting started with OpenG2P
---

# OpenG2P In a Box

This document describes a deployment model wherein the infrastructure and components required by OpenG2P modules can be set up on a single node/VM/machine. This will help you to get started with OpenG2P and experience the functionality without having to meet all r[esource requirements](hardware-requirements.md) for a production-grade setup. Although the deployment has been made compact, the essence of the [deployment architecture ](./#deployment-architecture)is preserved so that upgrading the infra to a production-grade infra is easier when more hardware resources are available.

{% hint style="danger" %}
Do NOT use this model for production/pilots.
{% endhint %}

## Prerequisites

* Machine with the following configuration:
  * TBD

## Installation

* Ssh into the machine.
* Set up [Firewall](base-infrastructure/openg2p-cluster/cluster-setup/firewall.md). Make sure to include [K8s Firewall](base-infrastructure/openg2p-cluster/cluster-setup/firewall.md#firewall-rules-for-kubernetes-node), [NFS Firewall](base-infrastructure/openg2p-cluster/cluster-setup/firewall.md#firewall-rules-for-nfs), [Wireguard Firewall](base-infrastructure/openg2p-cluster/cluster-setup/firewall.md#firewall-rules-for-wireguard), and [LB Firewall](base-infrastructure/openg2p-cluster/cluster-setup/firewall.md#firewall-rules-for-load-balancer), all in the same machine.
* Install [Wireguard Bastion](base-infrastructure/wireguard-bastion/#installation).
* Install [NFS Server](base-infrastructure/nfs-server.md#installation).
* Install [Kubernetes Cluster (RKE2 Server)](base-infrastructure/openg2p-cluster/cluster-setup/#cluster-installation).
  * Install [NFS CSI Driver](base-infrastructure/openg2p-cluster/cluster-setup/#nfs-client-provisioner).
*   Istio Setup; from [kubernetes/istio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio) directory, run the following:

    ```bash
    istioctl operator init
    kubectl apply -f istio-operator-no-external-lb.yaml
    ```
* Set up TLS using the following:
  *   Create [SSL Certificate using Letsencrypt](deployment-guide/ssl-certificates-using-letsencrypt.md) for Rancher (Edit hostname below):

      ```bash
      certbot certonly --agree-tos --manual \
          --preferred-challenges=dns \
          -d rancher.box.openg2p.org
      ```
  *   Create Rancher TLS Secret (Edit certificate paths below):

      ```bash
      kubectl -n istio-system create secret tls tls-rancher-ingress \
          --cert /etc/letsencrypt/live/rancher.box.openg2p.org/fullchain.pem \
          --key /etc/letsencrypt/live/rancher.box.openg2p.org/privkey.pem
      ```
  *   Create [SSL Certificate using Letsencrypt](deployment-guide/ssl-certificates-using-letsencrypt.md) for Keycloak (Edit hostname below):

      ```bash
      certbot certonly --agree-tos --manual \
          --preferred-challenges=dns \
          -d keycloak.box.openg2p.org
      ```
  *   Create Keycloak TLS Secret, using (Edit certificate paths below):

      ```bash
      kubectl -n istio-system create secret tls tls-keycloak-ingress \
          --cert /etc/letsencrypt/live/keycloak.box.openg2p.org/fullchain.pem \
          --key /etc/letsencrypt/live/keycloak.box.openg2p.org/privkey.pem
      ```
* Set up DNS for Rancher and Keycloak hostnames to point to the IP of the node.
*   Rancher Install; from [kubernetes/rancher](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/rancher) directory, run the following (Edit hostname below):

    ```bash
    RANCHER_HOSTNAME=rancher.box.openg2p.org \
    TLS=true \
    RANCHER_ISTIO_OPERATOR=false \
        ./install.sh
    ```

    * Login to Rancher using the above hostname and bootstrap the `admin` user according to the instructions. After successfully logging in to Rancher as admin, save the new admin user password in `local` cluster, in `cattle-system` namespace, under `rancher-secret`, with key `adminPassword`.
*   Keycloak Install; from [kubernetes/keycloak](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/keycloak) directory, run the following (Edit hostname below):

    ```bash
    KEYCLOAK_HOSTNAME=keycloak.box.openg2p.org \
    TLS=true \
    KEYCLOAK_ISTIO_OPERATOR=false \
        ./install.sh
    ```
* [Integrate Rancher & Keycloak](base-infrastructure/rancher.md#keycloak-rancher-integration).
* Continue to use the same cluster (`local` cluster) for OpenG2P Modules also. In Rancher, create a Project and Namespace, on which the OpenG2P modules will be installed (We will assume namespace name as `dev` for now.)
* Follow [Istio Namespace setup](base-infrastructure/openg2p-cluster/cluster-setup/istio.md#namespace-setup).
* Proceed to Install OpenG2P modules (TODO).
