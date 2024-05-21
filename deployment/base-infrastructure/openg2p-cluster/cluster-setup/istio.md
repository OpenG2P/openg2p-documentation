---
description: Istio Setup
---

# Istio

Istio is a power traffic mesh management tool. It also provides an ingress gateway for the Kubernetes cluster.

## Installation

### Operator Setup

* The following setup can be done from the client machine. This installs Istio Operator, Istio Service Mesh, Istio Ingressgateway components.
*   From [kubernetes/istio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio) directory, run;

    ```bash
    istioctl operator init
    kubectl apply -f istio-operator.yaml
    ```

### Namespace Setup

(Skip this section for Rancher cluster)

Once the above Operator setup is done, gateways need to be set up on each namespace. This assumes that the namespace (and relevant Rancher project) are created.

*   Edit and run this to define the variables:

    ```
    export NS=prod
    export WILDCARD_HOSTNAME='*.prod.openg2p.net'
    ```
*   Run this apply gateways

    ```bash
    envsubst < istio-gateway.yaml | kubectl apply -f -
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
