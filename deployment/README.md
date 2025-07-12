---
description: OpenG2P Deployment
---

# Deployment

OpenG2P’s **V4 deployment architecture** offers a **production-grade, Kubernetes-based platform** designed to deliver secure, scalable, and reliable deployments of OpenG2P modules. Built on a robust Kubernetes orchestration framework, it supports multiple isolated environments—such as Development, QA, and Demo sandboxes—within a single organisational setup, enabling seamless management across the entire software lifecycle.

This infrastructure ensures **secure access for internal development teams** and has been rigorously tested, earning an [**A+ rating in third-party penetration testing**](../privacy-and-security/security-audits/security-audit-2025-march.md), underscoring its strong security posture. By leveraging the same V4 base for both development and production, it facilitates an **easy and efficient transition from development to production environments**, significantly reducing complexity and risks.

For System Integrators, the V4 Deployment Infra represents a substantial time and resource saver by eliminating the need to build production-grade deployment setups from scratch. This turnkey solution accelerates implementation while maintaining enterprise-level security and operational excellence, making it the ideal foundation for organisations aiming to deploy OpenG2P at scale with confidence.

The V4 deployment is offered as a set of instructions, scripts, [Helm charts](helm-charts.md), utilities and guidelines.

{% hint style="info" %}
\* This deployment architecture is referred to as "V4" by the OpenG2P team due to the way it has evolved over the past few years.  The V4 deployment architecture is an evolution of MOSIP's [V3 architecture](https://github.com/mosip/k8s-infra).  Unlike V3, where separate clusters are created for environments, in V4, all sandboxes and environments reside in the same cluster with finer access controls
{% endhint %}

## V4 deployment architecture&#x20;

<figure><img src="../.gitbook/assets/deployment-architecture-v4.jpg" alt=""><figcaption><p>Deployment Architecture</p></figcaption></figure>

The V4 architecture consists of two clusters - one for [Rancher](base-infrastructure/rancher.md) (it requires its own dedicated Kubernetes cluster. [Learn more >>](https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade#high-availability-kubernetes-install-with-the-helm-cli)) and one for all OpenG2P modules and supporting components. All sandboxes and environments reside in the OpenG2P cluster under separate namespaces. The RBAC of Kubernetes is used to provide users access to namespaces. Further, the secure access to applications can be controlled by the following means:

1. Multiple Wireguard servers enable separate [access channels](deployment-guide/private-access-channel.md).
2. Access control at the application level, where login to dashboards and portals is controlled via authentication and authorisation defined in Keycloak.

The Keycloak inside the Rancher cluster provides **organisation-wide authorisation** and offers single sign-on for all resources.&#x20;

## Deployment modes

Depending on the resource availability and purpose, we offer different modes (or configurations) of deployment as follows:

<table><thead><tr><th width="169">Deployment Mode</th><th>Resource requirement</th></tr></thead><tbody><tr><td><a href="openg2p-in-a-box.md">In-a-box</a></td><td>Single machine deployment. Good to start off with OpenG2P while still installing the entire V4 infrastructure packed in a box.  You may use such a deployment for learning how to deploy and for trying out OpenG2P. However, this is not recommended for production. </td></tr><tr><td>Development</td><td>This is typically a multi-node deployment for your organization, hosting multiple sandboxes such as Dev, QA, and Demo on the same infrastructure to optimize resource utilization. It provides high security and full access control for internal development and testing. Components like Postgres and MinIO are installed as Docker containers here, whereas in production they are usually deployed on separate machines. This deployment facilitates a smooth transition to production.</td></tr><tr><td>Production </td><td>Extension of the Development mode. It consists of multi-node deployment for fail-safe operation and high availability for your services. Certain features related to scalability, manageability, and access control have been strengthened to support production deployments. This infrastructure also allows you to host multiple environments, such as Production and Staging/UAT, within the same infrastructure.  Critical components like Postgres, Minio and installed on separate machines for better manageability, scale and access control.</td></tr></tbody></table>

If you would like to start off with OpenG2P and have limited hardware resources, you may deploy "[**OpenG2P in a box**](openg2p-in-a-box.md)" that installs all essential components required to run OpenG2P modules. However,  **we recommend installing V4 deployment infrastructure** in your organisation that offers several benefits:

* Ability to scale up by adding machines when multiple sandboxes are required, or load on the system is high.
* Single infrastructure to hold several sandboxes like dev, qa, staging and even production.
* High security and access control.
* High availability of services.
* Seamless transition to production rollout (same infrastructure may be used with few additions. Refer to [production guide](production.md)).&#x20;





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
