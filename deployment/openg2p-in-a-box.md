# OpenG2P In a Box

This document describes a deployment model wherein the infrastructure and components required by OpenG2P modules can be set up on a single node/VM/machine. This will help you to get started with OpenG2P and experience the functionality without having to meet all r[esource requirements](hardware-requirements.md) for a production-grade setup. Although the deployment has been made compact, the essence of the [deployment architecture ](./#deployment-architecture)is preserved so that upgrading the infra is easier when more hardware resources are available.

## Deployment architecture

{% embed url="https://miro.com/app/board/uXjVKEY_ZNk=/?share_link_id=892398727661" %}

{% hint style="danger" %}
Do NOT use this model for production/pilots.
{% endhint %}

## Installation

### Prerequisites

* Machine with the following configuration
  * 16 vCPU/64GB RAM/256 GB storage
  * OS: Ubuntu 22.04

### Base infrastructure setup

To set up the base infrastructure, login to the machine and install the following:

1. Set up [Firewall](base-infrastructure/openg2p-cluster/cluster-setup/firewall.md). Make sure to include [K8s Firewall](base-infrastructure/openg2p-cluster/cluster-setup/firewall.md#firewall-rules-for-kubernetes-node), [NFS Firewall](base-infrastructure/openg2p-cluster/cluster-setup/firewall.md#firewall-rules-for-nfs), [Wireguard Firewall](base-infrastructure/openg2p-cluster/cluster-setup/firewall.md#firewall-rules-for-wireguard), and [LB Firewall](base-infrastructure/openg2p-cluster/cluster-setup/firewall.md#firewall-rules-for-load-balancer), all in the same machine.
2. Install [Kubernetes Cluster (RKE2 Server)](base-infrastructure/openg2p-cluster/cluster-setup/#cluster-installation).
3. Install [Wireguard Bastion](base-infrastructure/wireguard-bastion/#installation), as given below. (This method doesn't require docker. Wireguard will run on Kubernetes):
   *   Run this command for each wireguard server/channel:

       ```bash
       WG_MODE=k8s ./wg.sh <name for this wireguard server> <client ips subnet mask> <port> <no of peers> <subnet mask of the cluster nodes & lbs>
       ```
   *   For example:

       ```bash
       WG_MODE=k8s ./wg.sh wireguard_app_users 10.15.0.0/16 51820 254 172.16.0.0/24
       WG_MODE=k8s ./wg.sh wireguard_sys_admins 10.16.0.0/16 51821 254 172.16.0.0/24
       ```
   *   Check logs of the servers and wait for all servers to finish startup. Example:

       ```bash
       kubectl -n wireguard-system logs -f wireguard-sys-admins
       ```
4. Install [NFS Server](base-infrastructure/nfs-server.md#installation).
5. Install [Kubernetes NFS CSI Driver](base-infrastructure/openg2p-cluster/cluster-setup/#nfs-client-provisioner).
6.  Istio: Setup; from [kubernetes/istio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio) directory, run the following:

    ```bash
    istioctl operator init
    kubectl apply -f istio-operator-no-external-lb.yaml
    kubectl apply -f istio-ef-spdy-upgrade.yaml
    ```
7. Set up TLS using the following:
   *   Create [SSL Certificate using Letsencrypt](deployment-guide/ssl-certificates-using-letsencrypt.md) for Rancher (Edit hostname below):

       ```bash
       certbot certonly --agree-tos --manual \
           --preferred-challenges=dns \
           -d rancher.your.org
       ```
   *   Create Rancher TLS Secret (Edit certificate paths below):

       ```bash
       kubectl -n istio-system create secret tls tls-rancher-ingress \
           --cert /etc/letsencrypt/live/rancher.your.org/fullchain.pem \
           --key /etc/letsencrypt/live/rancher.your.org/privkey.pem
       ```
   *   Create [SSL Certificate using Letsencrypt](deployment-guide/ssl-certificates-using-letsencrypt.md) for Keycloak (Edit hostname below):

       ```bash
       certbot certonly --agree-tos --manual \
           --preferred-challenges=dns \
           -d keycloak.your.org
       ```
   *   Create Keycloak TLS Secret, using (Edit certificate paths below):

       ```bash
       kubectl -n istio-system create secret tls tls-keycloak-ingress \
           --cert /etc/letsencrypt/live/keycloak.your.org/fullchain.pem \
           --key /etc/letsencrypt/live/keycloak.your.org/privkey.pem
       ```
8. Set up DNS for Rancher and Keycloak hostnames to point to the IP of the node.
9.  Rancher Install; from [kubernetes/rancher](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/rancher) directory, run the following (Edit hostname below):

    ```bash
    RANCHER_HOSTNAME=rancher.your.org \
    TLS=true \
    RANCHER_ISTIO_OPERATOR=false \
        ./install.sh
    ```

    * Login to Rancher using the above hostname and bootstrap the `admin` user according to the instructions. After successfully logging in to Rancher as admin, save the new admin user password in `local` cluster, in `cattle-system` namespace, under `rancher-secret`, with key `adminPassword`.
10. Keycloak Install; from [kubernetes/keycloak](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/keycloak) directory, run the following (Edit hostname below):

    ```bash
    KEYCLOAK_HOSTNAME=keycloak.your.org \
    TLS=true \
    KEYCLOAK_ISTIO_OPERATOR=false \
        ./install.sh
    ```
11. [Integrate Rancher & Keycloak](base-infrastructure/rancher.md#rancher-keycloak-integration).
12. Continue to use the same cluster (`local` cluster) for OpenG2P Modules also.
    * In Rancher, create a Project and Namespace, on which the OpenG2P modules will be installed. The rest of this guide will assume the Namespace to be `dev` .
    * In Rancher -> Namespaces menu, enable "Istio Auto Injection" for `dev` namespace.
13. Follow [Istio Namespace setup](base-infrastructure/openg2p-cluster/cluster-setup/istio.md#namespace-setup):
    1.  Edit and run this to define the variables:

        ```
        export NS=dev
        export WILDCARD_HOSTNAME='*.dev.your.org'
        ```
    2.  Run this apply gateways

        ```bash
        kubectl create ns $NS
        envsubst < istio-gateway-tls.yaml | kubectl apply -f -
        ```
    3.  Create [SSL Certificate using Letsencrypt](deployment-guide/ssl-certificates-using-letsencrypt.md) for the wildcard hostname used above. Example usage:

        ```bash
        certbot certonly --agree-tos --manual \
            --preferred-challenges=dns \
            -d dev.your.org \
            -d *.dev.your.org
        ```
    4.  Add the certificate to K8s.

        ```bash
        kubectl -n istio-system create secret tls tls-openg2p-$NS-ingress \
            --cert=<certificate path> \
            --key=<certificate key path>
        ```
14. Install [Prometheus and Monitoring](base-infrastructure/openg2p-cluster/prometheus-and-grafana.md) from Rancher
15. Install Logging and Fluentd. (TODO)

### OpenG2P modules' installation

[Install OpenG2P modules via Rancher](../spar/deployment.md#installation-using-rancher-ui). &#x20;
