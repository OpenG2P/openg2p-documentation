---
description: Complete information and guide on deployment of OpenG2P components
---

# OpenG2P Deployment Architecture

OpenG2P’s offers a **production-grade, Kubernetes-based deployment architecture** designed to deliver secure, scalable, and reliable deployments of OpenG2P modules. Built on a robust Kubernetes orchestration framework, it supports multiple isolated environments—such as Development, QA, Demo, Staging, Pilot and Production —within a single organisational setup, enabling seamless management across the entire software lifecycle. &#x20;

This deployment model ensures **secure access for internal development teams** and has been rigorously tested, earning an [**A+ rating in third-party penetration testing**](../../privacy-and-security/security-audits/security-audit-2025-march.md), underscoring its strong security posture. By leveraging the same deployment model for development as well as production, it facilitates an **easy and efficient transition from development to production environments**, significantly reducing complexity and risks.

For System implementors, the OpenG2P deployment package represents a substantial time and resource saver by eliminating the need to build production-grade deployment setups from scratch. This turnkey solution accelerates implementation while maintaining enterprise-level security and operational excellence, making it the ideal foundation for organisations aiming to deploy OpenG2P at scale with confidence.

The deployment is offered as a set of instructions, scripts, [Helm charts](../../releases/helm-charts.md), utilities and guidelines.

The deployment is **cloud agnostic** - it does not use cloud specific components - completely suitable for on-prem setups.

## Deployment architectures

Depening on availability of compute resources and scale of your deploment we recommend the following deployment architectures:

<table><thead><tr><th width="140.9140625">Architecture</th><th>Descripion</th><th>Purpose</th></tr></thead><tbody><tr><td>Single-node </td><td>All components including Kubernetes, Wireguard, Nginx, NFS run on the same machine.  Multiple environments run in separate Kubernetes namespaces</td><td>Well suited for quickly bring up OpenG2P for creating development sandboxes like dev, qa etc.  PostgreSQL runs at Dockers within each namespace.  </td></tr><tr><td>Two-node</td><td>The storage server is separated from the compute server (Kubernetes). PostgreSQL server runs on a separate "storage node" that contains large volumes of SSD storage with high througput disk I/O. The NFS also runs on this node. Thus, there is a separate of concerns between compute and data.</td><td>For pilots and even small scale production setups, specifically where I high uptime is not critical. If systems are predominantly used by administrators and some down time of services and portals is acceptable, then this architecture would be sufficient.</td></tr><tr><td>Multi-node</td><td>Multiple separate nodes for each of Wireguard, Nginx, Kubernetes nodes, NFS, PostgreSQL.</td><td>Full scale production deployment where fail safety is critical — certain services must continue to run without interruptions. Also, when the scale is high in terms of compute requirements. This typically will be the case with registration portals/beneficiary portals that have to be kept up and down time is not acceptable.</td></tr></tbody></table>

{% hint style="warning" %}
Over and above all these, there is minimally one more node required for backups and running local Git and Docker repositories. Refer to [Resource Requirements](../resource-requirements.md).
{% endhint %}

<figure><img src="../../.gitbook/assets/openg2p-deployment-model (1).jpg" alt=""><figcaption></figcaption></figure>

## Key concepts

* Each environment like 'qa', 'dev', 'staging', 'production' is installed in a **separate Kubernetes namespace** on the same cluster.
* Nginx, Wireguard, NFS and Postgres (production) are installed natively on the VM.  Rest of the components are inside the Kubernetes cluster.
* Access to each environment (namespace) can be controlled via [private access channels](../deployment-guide/private-access-channel.md).
* SSL termination (HTTPS) happens on the Nginx. The traffic further to Ingress gateway is HTTP.
* Firewall is outside the purview of this deployment.
* Git repo and Docker Registry are assumed externally hosted (public or private).  In case of production deployments, these should be hosted within private network. &#x20;
* As this deployment is based on Kubernetes, the system can be easily scaled up by adding more nodes (machines).&#x20;

## Role of various components

The deployment utilizes several open source third party components. The concept and role of these components is given below:

<table><thead><tr><th width="165">Component</th><th>Description</th></tr></thead><tbody><tr><td><mark style="color:$primary;">Wireguard</mark></td><td><p><a href="https://www.wireguard.com/">Wireguard</a> is a fast secure &#x26; open-source VPN, with P2P traffic encryption that can enable secure (non-public) access to the resources.  A combination of Wireguard, Nginx and Isto gateway is used to enable fine-grained access control to the environments.  See <a href="../deployment-guide/private-access-channel.md">Private Access Channels</a>.</p><p><sup><em>Note that the terms Wireguard, Wireguard Bastion and Wireguard Server are used interchangeably in this document.</em></sup></p></td></tr><tr><td>Nginx</td><td>Nginx as a reverse-proxy for incoming external (public) traffic. It serves as HTTPS termination and together with Wireguard and Istio Gateway it can be used to create <a href="../deployment-guide/private-access-channel.md">private access channels</a>.  Nginx isolates the internal network such that traffic does not directly fall on the Istio Gateway of the Kubernetes cluster.</td></tr><tr><td>Istio</td><td><a href="https://istio.io/">Istio</a> is a service mesh that provides a way to connect, secure, control, and observe microservices. It is a powerful mesh management tool. It also provides an ingress gateway for the Kubernetes cluster.  See note below.</td></tr><tr><td>Ingress Gateway</td><td>The <a href="https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/">Ingressgateway</a> component of Istio enables routing external traffic into Kubernetes services. Istio can be configured to do much more. Seen note below.</td></tr><tr><td>Rancher</td><td>Rancher provides advanced cluster management capabilities. It can also manage several clusters.</td></tr><tr><td>Keycloak</td><td>Keycloak provides <strong>organisation-wide authorisation</strong> and offers single sign-on for all resources.  </td></tr><tr><td>NFS</td><td>Network File System (NFS) provides persistence to the resources of the Kubernetes cluster.  Although on a single machine installation we can directly use the underlying SSD storage, we prefer to use NFS, keeping in mind scalability in case more nodes (machines) need to be added to the cluster. </td></tr><tr><td>Prometheus &#x26; Grafana</td><td>For system monitoring. <a href="../../monitoring-and-reporting/system-health.md">Learn more >></a> </td></tr><tr><td>FluentD</td><td>For collecting and shunting logs of services to OpenSearch. <a href="../scaling/base-infrastructure/openg2p-cluster/fluentd-and-opensearch/">Learn more >> </a></td></tr><tr><td>OpenSearch</td><td>For indexing and search of data. Primary used for logs and <a href="../../monitoring-and-reporting/reporting-framework/">reporting framework</a>.</td></tr><tr><td>PostgreSQL</td><td>Primary database of OpenG2P platform. For production deployment, PostgreSQL is installed on the VM directly (natively) while for sandboxes, PostgreSQL is installed on the Kubernetes cluster inside a namespace using PostgreSQL Docker.</td></tr></tbody></table>

{% hint style="info" %}
**Why Istio? What are the benefits of using Istio in OpenG2P setup?**&#x20;

* We can have advanced traffic management setups like load balancing, retries & failovers, and fault injection for testing resilience.
* We can use advanced deployment strategies like canary deployments and A/B testing, where Istio can route higher percentage of traffic to specific service versions.
* We can enable security features like mTLS encryption for service-to-service traffic. Istio can also provide an authentication & authorization layer for services.
* We can also define policies related to access control & rate limiting. One can define which services are allowed to access other services or limit the rate of requests accepted by a service.
* More importantly Istio provides comprehensive observability features. We can visualize & monitor service-to-service traffic real-time, with tools like [Kiali](https://istio.io/latest/docs/ops/integrations/kiali/), which would help identify performance bottlenecks and diagnose issues.
{% endhint %}

## Installation of an environment

An environment is an insolated setup for a specific purpose like development, testing, staging, production etc.  In OpenG2P's deployment model each environment is a namespace in Kubernetes.  The namespace contains set of common shared modules - [`openg2p-commons`](openg2p-commons-helm-chart.md) - and the modules (Registry, PBMS, SPAR, G2P Bridge) themselves along with any third-party dependency modules.  Access to each environment can be controlled using [private access channels](../deployment-guide/private-access-channel.md) and RBAC of Kubernetes.

In the previous deployments of modules each module was "self contained" - we would install all associated dependencies (like PostgreSQL, MinIO, OpenSearch, Kafka, Keymanager, etc. ) for a module as a single package, thus enabling a single click deployment for Registry, PBMS, G2P Bridge and SPAR and a clean separation of resources along with easier naming conventions, etc.  This is good to deploy a sandbox; however, in production, we seldom find more than one instance of the Postgres server or MinIO.  Even Kafka being resource-hungry, is preferred to have a single instance used by several services.  Therefore, having a set of **shared common resources**  within an **environment** would not only be closer to a production scenario but also save us resources on our deployment as resources would be shared across the modules.  The new deployment Helm charts offers a common resources layer - installed via "[openg2p-commons](openg2p-commons-helm-chart.md)" Helm Chart, and then each module, like Registry, PBMS etc, will continue to have their Helm packages with dependencies specific to the modules.

The new way of deployment offers a few challenges as databases of several sandboxes and instances of the module reside in the same PostgreSQL server. We must ensure that every database and its users are properly named to avoid any name clashes and allocated sufficient resources to the Postgres server. The tear down of modules also gets complicated as footprints or each module reside in the common components and they need to be removed manually or via scripts.

#### Self contained versus shared common resources

| Modules    | Helm Chart Versions - Self Contained | Helm Chart Versions - Shared Common Resources |
| ---------- | ------------------------------------ | --------------------------------------------- |
| Registry   | 2.x.x                                | 3.x.x                                         |
| PBMS       | 2.x.x                                | 3.x.x                                         |
| SPAR       | 1.x.x                                | 2.x.x                                         |
| G2P Bridge | 1.x.x                                | 2.x.x                                         |

#### Postgres

Postgres is installed using openg2p-commons. In previous deployment model the chart of Postgres would create database for the module along with an admin user of the database. Now the database and user has to be created by each module before installation. [`postgres-ini`](https://github.com/OpenG2P/postgres-init)  Helm Chart has been created for this purpose. This chart must be added to the dependency of the respective module Helm and sufficient time must be given for the module to wait until the database is created. There is[ `wait_for_psql.py` ](https://github.com/OpenG2P/openg2p-packaging/tree/main/packaging/docker-entrypoint.d) in Docker of modules like Registry and PBMS. The timeout there needs to be increased to ensure that enough time is given for the postgres-init to run and create the database

#### Database initialization

#### Work in progress

The work items related to environment depoyment may be tracked here:

{% @jira/embed url="https://openg2p.atlassian.net/browse/G2P-3290" %}

#### Modules

After the openg2p-commons is installed, all the modules - Registry,  PBMS, SPAR, G2P Bridge - are installed using their respective Helm charts.
