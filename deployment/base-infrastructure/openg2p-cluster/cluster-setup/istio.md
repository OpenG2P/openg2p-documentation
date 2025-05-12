---
description: Istio Setup
---

# Istio

[Istio](https://istio.io/) is a service mesh that provides a way to connect, secure, control, and observe microservices. It is a powerful mesh management tool.  It also provides an ingress gateway for the Kubernetes cluster. \
Currently, we use the [Ingressgateway](https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/) component of Istio which enables routing external traffic into Kubernetes services. Istio can be configured to do much more. See note below.

{% hint style="info" %}
**Why Istio? What are the benefits of using Istio in OpenG2P setup?**&#x20;

* We can have advanced traffic management setups like load balancing, retries & failovers, and fault injection for testing resilience.
* We can use advanced deployment strategies like canary deployments and A/B testing, where Istio can route higher percentage of traffic to specific service versions.
* We can enable security features like mTLS encryption for service-to-service traffic. Istio can also provide an authentication & authorization layer for services.
* We can also define policies related to access control & rate limiting. One can define which services are allowed to access other services or limit the rate of requests accepted by a service.
* More importantly Istio provides comprehensive observability features. We can visualize & monitor service-to-service traffic real-time, with tools like [Kiali](https://istio.io/latest/docs/ops/integrations/kiali/), which would help identify performance bottlenecks and diagnose issues.


{% endhint %}

## Installation

### Operator Setup

* The following setup can be done from the client machine. This installs Istio Operator, Istio Service Mesh, Istio Ingressgateway components.
*   From [kubernetes/istio](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio) directory, run;

    ```bash
    istioctl install -f istio-operator.yaml
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
