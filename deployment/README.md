---
description: OpenG2P Deployment
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Deployment

OpenG2P offers production-grade deployment scripts, [Helm charts](helm-charts.md) and utilities based on reputed open-source components like Kubernetes, Rancher etc. The deployment infra may be used for sandbox, pilot or full-scale rollout. All modules are available as Dockers and Kubernetes is used as the orchestration platform. The deployment architecture is depicted below

{% embed url="https://miro.com/app/board/uXjVN5LsWDw=/?share_link_id=356935336772" %}
Deployment Architecture
{% endembed %}

The modules reside in the OpenG2P Cluster shown above.  Rancher (housed in the Rancher cluster) is used to manage multiple Kubernetes clusters.

{% hint style="info" %}
You may need environments for development, staging, production, QA etc. Each environment will have its own Kubernetes cluster.  Rancher can be used to manage all these environments.
{% endhint %}

## Deployment stack

The figure below depicts how all components are stacked

{% embed url="https://miro.com/app/board/uXjVKaaGd40=/?share_link_id=118505524008" %}
Deployment Stack
{% endembed %}
