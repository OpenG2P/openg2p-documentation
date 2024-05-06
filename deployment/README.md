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
A single cluster may suffice for an organisation. Different environments like dev, qa, staging may be installed on the same cluster under different namespaces.  If required, a separate cluster may be installed for production.
{% endhint %}

## Deployment stack

The figure below depicts how all components are stacked

{% embed url="https://miro.com/app/board/uXjVKaaGd40=/?share_link_id=118505524008" %}
Deployment Stack
{% endembed %}

For deployment, set up the following in the sequence given below:

* [Base infrastructure](base-infrastructure/)
* [Common components](common-components/)
* OpenG2P specific modules _(instructions available in module-specific deployment pages)_
