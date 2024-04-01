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

OpenG2P offers production-grade deployment scripts and utilities based on reputed open-source components like Kubernetes, Rancher etc. The deployment infra may be used for sandbox, pilot or full scale rollout. All components are available as Dockers and Kubernetes is used as the orchestration platform. The deployment architecture is depicted below

{% embed url="https://miro.com/app/board/uXjVN5LsWDw=/?share_link_id=356935336772" %}

All modules reside in the OpenG2P Cluster shown above.  Rancher (housed in Rancher cluster) is used to manage multiple Kubernetes clusters. &#x20;

## Deployment stack

The figure below depicts how all components are stacked

{% embed url="https://miro.com/app/board/uXjVKaaGd40=/?share_link_id=118505524008" %}
