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

OpenG2P offers production-grade deployment scripts, [Helm charts](helm-charts.md) and utilities based on reputed open-source components like Kubernetes, Rancher etc. The deployment infra may be used for sandbox, pilot or full-scale rollout. All modules are available as Dockers and Kubernetes is used as the orchestration platform. The deployment architecture is depicted below.

{% embed url="https://miro.com/app/board/uXjVN5LsWDw=/?share_link_id=356935336772" %}
Deployment Architecture
{% endembed %}

Essentially, for an organisation, you will need two clusters - one for [Rancher](base-infrastructure/rancher.md) (it requires its own dedicated Kubernetes cluster. [Learn more >>](https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade#high-availability-kubernetes-install-with-the-helm-cli)) and one for all OpenG2P modules and supporting components. All sandboxes and environments reside in the OpenG2P cluster under separate namespaces. The RBAC of Kubernetes is used to provide users access to namespaces. Further, the secure access to applications can be controlled by the following means:

1. Multiple Wireguard servers enabling separate [access channels](deployment-guide/security/access-channel.md).
2. Access control at the application level where login to dashboards, and portals is controlled via authentication and authorisation defined in Keycloak.

The Keycloak inside Rancher cluster provides access control to system administrators to access Rancher and cluster.&#x20;

The above is a recommended architecture that also optimises resource usage. However, for pilots or production, you may create a dedicated cluster and a separate instance of Rancher, Keycloak etc. These choices are left to the implementers.

For deployment, set up the following in the sequence given below:

* [Base infrastructure](base-infrastructure/)
* OpenG2P specific modules _(instructions available in module-specific deployment pages)_

{% hint style="info" %}
This deployment architecture is referred to as "V4" by the OpenG2P team due to the way it has evolved over the last few years.  The V4 is a modification of MOSIP's V3 deployment architecture essentially housing multiple environments within the same organisation-wide cluster.
{% endhint %}
