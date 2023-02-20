---
description: Work in progress
---

# Rancher Server Setup

### Cluster setup

* It is recommended to setup a single node cluster, to install rancher.
* Setup a new rke2 cluster, single server node. Use the [Cluster Setup](broken-reference) guide.&#x20;
  * Do not remove the stock ingress controller in server config.
  * No need to install istio.

### Rancher install

*   To install rancher use this (hostname to be edited in the below command):

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

* Use this to install longhorn. [Longhorn Install as a Rancher App](https://longhorn.io/docs/1.3.2/deploy/install/install-with-rancher/)

### Keycloak setup

* From [infra](https://github.com/OpenG2P/openg2p-packaging/tree/develop/infra) directory, run the following to install Keycloak (hostname to be edited in the below command).
* ```bash
  helm repo add bitnami https://charts.bitnami.com/bitnami
  helm repo update
  helm install keycloak bitnami/keycloak \
    -n keycloak \
    --create-namespace \
    --version "7.1.18" \
    --set ingress.hostname=keycloak.openg2p.org \
    --set ingress.extraTls[0].hosts[0]=keycloak.openg2p.org \
    -f rancher-keycloak-values.yaml
  ```
* ### Integrate Rancher and Keycloak
  * Integrate Rancher and Keycloak using this, [Rancher Auth - Keycloak (SAML)](https://docs.ranchermanager.rancher.io/how-to-guides/new-user-guides/authentication-permissions-and-global-configuration/authentication-config/configure-keycloak-saml)
