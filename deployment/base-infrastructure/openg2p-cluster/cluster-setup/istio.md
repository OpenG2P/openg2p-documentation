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

> _Skip this section for Rancher cluster_

Set up an Istio gateway on each namespace for a domain. This assumes that the namespace (and relevant Rancher project) are already created (use the Rancher console to create a namespace or via command line `kubectl):`

*   One command line define these variables (example):

    ```
    export NS=dev
    export HOSTNAME='dev.your.org'
    export WILDCARD_HOSTNAME='*.dev.your.org'
    ```
*   Git clone https://github.com/openg2p/openg2p-deployment repo.  In [kubernetes/istio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio) directory,  run the following:

    ```bash
    envsubst < istio-gateway.yaml | kubectl apply -f -
    ```
