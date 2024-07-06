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

    * Wait for `istiod` and `ingressgateway` pods to start.
*   Or, for Rancher cluster, run:

    ```bash
    kubectl apply -f istio-ef-spdy-upgrade.yaml
    ```

### Namespace Setup

(Skip this section for Rancher cluster)

Set up an Istio gateway on each namespace for a domain. This assumes that the namespace (and relevant Rancher project) are already created (you may use the Rancher console to create a namespace or via command line `kubectl`)

*   Edit and run this to define the variables:

    ```
    export NS=dev
    export WILDCARD_HOSTNAME='*.dev.your.org'
    ```
*   From [kubernetes/istio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio) directory,  run the following:

    ```bash
    envsubst < istio-gateway.yaml | kubectl apply -f -
    ```
