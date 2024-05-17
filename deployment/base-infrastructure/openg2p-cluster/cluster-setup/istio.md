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

For access control to specific namespaces or pods in the cluster multiple ingress gateways may be required.  See [deployment architecture](../../../). The rules in the gateway allow traffic from load balancers to be filtered at the gateway.  A combination of rules on the gateway and "reception" rules on Istio virtual services of individual pods are employed to achieve this. &#x20;

Typically, for every load balancer, there will be one ingress gateway  in a one-to-one relationship.

### Ingress gateway configuration

TBD

### Virtual service configuration

TBD
