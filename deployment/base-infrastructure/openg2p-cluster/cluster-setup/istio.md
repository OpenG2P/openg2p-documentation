---
description: Istio Setup
---

# Istio

Istio is a power traffic mesh management tool. It also provides an ingress gateway for the Kubernetes cluster.

## Installation

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

## Multiple ingress gateways

By default the installation scripts enable two Istio Ingress gateways -  **public** and **private**. The public gateway is disabled by default. You may enable the same while opening up services to the public by following the steps given [below](istio.md#enabling-public-gateway).  To create more private gateways, refer [here](istio.md#creating-private-gateways).

{% hint style="warning" %}
Having only one private gateway implies that all users can open URLs in all namespaces. Access control to services may be accomplished by authentication/authorization of the respective services via Keycloak
{% endhint %}

### Enabling public gateway

TBD.

### Creating private gateways

TBD.
