---
description: OpenG2P Deployment
---

# Deployment

OpenG2P offers production-grade deployment scripts, [Helm charts](helm-charts.md) and utilities based on reputed open-source components like Kubernetes, Rancher etc. This architecture is also referred to as **V4**\*. The deployment infra may be used for sandbox, pilot or full-scale rollout. All modules are available as Dockers and Kubernetes is used as the orchestration platform. The deployment architecture is depicted below.

{% hint style="info" %}
\* This deployment architecture is referred to as "V4" by the OpenG2P team due to the way it has evolved over the past few years.  The V4 deployment architecture is an extension of MOSIP's [V3 architecture](https://github.com/mosip/k8s-infra).  Unlike V3, where separate clusters are created for environments, in V4, all sandboxes and environments reside in the same cluster with finer access controls
{% endhint %}

If you would like to start off with OpenG2P and have limited hardware resources, you may deploy "[**OpenG2P in a box**](openg2p-in-a-box.md)" that installs all essential components required to run OpenG2P modules. However,  **we recommend installing V4 deployment infrastructure** in your organisation that offers several benefits:

* Ability to scale up by adding machines when multiple sandboxes are required, or load on the system is high.
* Single infrastructure to hold several sandboxes like dev, qa, staging and even production.
* High security and access control.
* High availability of services.
* Seamless transition to production rollout (same infrastructure may be used with few additions. Refer to [production guide](production.md)).&#x20;

## Deployment architecture (V4)

<figure><img src="../.gitbook/assets/deployment-architecture-v4.jpg" alt=""><figcaption><p>Deployment Architecture</p></figcaption></figure>

Essentially, for an organisation, you will need two clusters - one for [Rancher](base-infrastructure/rancher.md) (it requires its own dedicated Kubernetes cluster. [Learn more >>](https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade#high-availability-kubernetes-install-with-the-helm-cli)) and one for all OpenG2P modules and supporting components. All sandboxes and environments reside in the OpenG2P cluster under separate namespaces. The RBAC of Kubernetes is used to provide users access to namespaces. Further, the secure access to applications can be controlled by the following means:

1. Multiple Wireguard servers enabling separate [access channels](deployment-guide/private-access-channel.md).
2. Access control at the application level where login to dashboards, and portals is controlled via authentication and authorisation defined in Keycloak.

The Keycloak inside the Rancher cluster provides **organisation-wide authorization** and offers single sign-on to all resources.&#x20;

The above is a recommended architecture that also optimises resource usage.&#x20;

For deployment, set up the following in the sequence given below:

* [Base infrastructure](base-infrastructure/)
* OpenG2P specific modules _(instructions available in module-specific deployment pages)_

## **Concepts** <a href="#concepts" id="concepts"></a>

{% hint style="info" %}
**Concepts**

Before proceeding with deployment, read up on the following topics to better understand each infrastructure component required for a successful setup:

1. 🔒 [**Firewall Rules**](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster)
2. 📦 [**Kubernetes Cluster**](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/cluster-setup#cluster-installation)
3. 🔐 [**WireGuard Bastion**](https://docs.openg2p.org/deployment/base-infrastructure/wireguard-bastion#installation)
4. 📁 [**NFS Server**](https://docs.openg2p.org/deployment/base-infrastructure/nfs-server#installation)
5. 🔗 [**Kubernetes NFS CSI Driver**](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/cluster-setup#nfs-client-provisioner)
6. 🧩 [**Istio Service Mesh**](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/istio)
7. 🔐 [**SSL Certificates**](https://docs.openg2p.org/deployment/deployment-guide/ssl-certificates-using-letsencrypt)
8. 🧑‍💻 [**Rancher**](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/rancher)
9. 🧾 [**Keycloak**](https://docs.openg2p.org/deployment/1.0.0/guides/user-guides/create-payment-manager-types)
10. 📊 [**Prometheus Monitoring**](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/prometheus-and-grafana)
11. 📝 [**Logging**](https://docs.openg2p.org/pbms/functionality/monitoring-and-reporting/logging) **and** [**Fluentd**](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/fluentd-and-opensearch)
{% endhint %}
