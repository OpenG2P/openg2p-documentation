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

Rancher is used to manage multiple clusters. Being a critical component of cluster administration it is highly recommended that Rancher itself runs on a Kubernetes cluster. This cluster is called Rancher Cluster or Observation Cluster as it is used to observe other clusters.&#x20;

The guide here provides instructions to install both the Rancher server and Keycloak which is required for system administration of clusters.&#x20;

To deploy Rancher carry out the following steps:

1. Provision resources as given [here](../hardware-requirements.md).
2. Make sure [NFS server](nfs-server.md) is already installed.
3. Install Kubernetes (K8s) cluster&#x20;
4. Install Rancher
5. Install Keycloak
6. Integrate Keycloak with Rancher

## K8s cluster installation

Follow steps 1-5 in the guide given [here](openg2p-cluster/cluster-setup/).

{% hint style="info" %}
For high availability and resilience of this cluster, read the [production guide](../production.md).
{% endhint %}

## Nginx/Loadbalancer Setup

* If using AWS cloud; create two Loadbalancers as given in the [Loadbalancer/AWS](load-balancer/aws.md) section, one for Rancher and one for Keycloak.
* If using Nginx on-prem; install two Nginx servers as given in the [Loadbalancer/Nginx/Install Server](load-balancer/nginx.md#install-servers-to-nginx) section, one for Rancher and one for Keycloak (It is recommended to install Rancher and Keycloak Nginx servers on two different IPs/Listen address.)
* Make sure to limit wireguard access on the `sys_admins` channel only to Rancher and Keycloak LB/Nginx IPs. Use the [Limit user access](wireguard-bastion/#limit-user-access) guide.
* Make sure to limit wireguard access on the `app_users` channel only to Keycloak LB/Nginx IP. Use the [Limit user access](wireguard-bastion/#limit-user-access) guide.

## Rancher installation

*   Clone [https://github.com/OpenG2P/openg2p-deployment](https://github.com/OpenG2P/openg2p-deployment), and from [kubernetes/rancher](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/rancher) directory run the following: (Edit Hostnames according to need)&#x20;

    ```bash
    RANCHER_HOSTNAME=rancher.openg2p.org \
        ./install.sh
    ```
* Login to Rancher using the above hostname and bootstrap the admin user according to the instructions. After successfully logging in to Rancher as admin, save the new admin user password in `local` cluster, in `cattle-system` namespace, under `rancher-secret`, with key `adminPassword`.

## Keycloak Installation

*   Clone [https://github.com/OpenG2P/openg2p-deployment](https://github.com/OpenG2P/openg2p-deployment), and from [kubernetes/keycloak](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/keycloak) directory run the following: (Edit Hostnames according to need)&#x20;

    ```bash
    KEYCLOAK_HOSTNAME=keycloak.openg2p.org \
        ./install.sh
    ```

## Rancher-Keycloak integration

* Login to Rancher as `admin`, copy the Keycloak admin user password, from `keycloak-system` namespace, in `keycloak` secret, under `admin-password` key.
* Login to Keycloak Admin Console with the hostname used during installation, as `admin` user (and password from the above step).
* Configure email for `admin` user, under `Users` Menu in Keycloak.
* Under `master` realm -> `Realm Settings` -> `Login` Tab -> `Email Settings` , enable `Email as username`.
* Proceed with the rest of the steps given in the [Rancher Auth - Keycloak (SAML)](https://docs.ranchermanager.rancher.io/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/authentication-config/configure-keycloak-saml) guide:
  * Create a SAML client on Keycloak with the default config mentioned in the above guide.
  * In Keycloak client settings, disable `Client Signature Required` , under `Keys` tab.
  * Configure Auth Provider under Rancher with the default config mentioned in the above guide.
* Ignore any error that says `An error occurred logging in: An error occurred logging in. Please try again.`. The integration is successful as long as it shows `Login with Keycloak` button on the login page.
* Log out from Rancher and log in with Keycloak (as Keycloak admin). (Your Keycloak admin and Rancher admin are now the same user.)
* Create a user for yourself on Keycloak with a password in `Users` menu (You can assign `admin` role to your user.)
* In Rancher -> `local` cluster -> `Cluster` Menu -> `Cluster and Project Members` , add the following users with usernames as;
  * Email of `admin` user in Keycloak, permission as `Owner`.
  * Email of your newly created user in Keycloak, permission as `Owner`.
* After adding make sure both users are marked as `Keycloak User`s. (If you are not able to create Keycloak users on Rancher, log out from Rancher and log in with Keycloak, as admin.)
* In Rancher -> `Users & Authentication` Menu -> `Auth Provider` Menu -> Keycloak (SAML) -> under who can log in section, select `Allow members of clusters and projects, plus authorized users & groups` .
* Log out from Rancher and Keycloak as admin. Do not user `admin` user anymore, only log in to Rancher and Keycloak using your newly created user.
