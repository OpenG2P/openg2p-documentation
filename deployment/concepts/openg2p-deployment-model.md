---
description: Complete information and guide on deployment of OpenG2P components
---

# OpenG2P Deployment Architecture

OpenG2P’s offers a **production-grade, Kubernetes-based deployment architecture** designed to deliver secure, scalable, and reliable deployments of OpenG2P modules. Built on a robust Kubernetes orchestration framework, it supports multiple isolated environments—such as Development, QA, Demo, Staging, Pilot and Production —within a single organisational setup, enabling seamless management across the entire software lifecycle.

This deployment architecture ensures **secure access for internal development teams** and has been rigorously tested, earning an [**A+ rating in third-party penetration testing**](../../privacy-and-security/security-audits/security-audit-2025-march.md), underscoring its strong security posture. By leveraging the same deployment model for development as well as production, it facilitates an **easy and efficient transition from development to production environments**, significantly reducing complexity and risks.

The deployment is offered as a **package** of instructions, scripts, [Helm charts](../../releases/helm-charts.md), utilities and guidelines. enabling system implementors to rapidly deploy OpenG2P securely thereby saving time and resources substantially and by eliminating the need to build production-grade deployment setups from scratch.

The deployment is **cloud agnostic** - it does not use cloud specific components - completely suitable for on-prem setups.

## Deployment architectures

Depening on availability of compute resources and scale of your deploment we recommend the following deployment architectures:

<table><thead><tr><th width="140.9140625">Architecture</th><th>Descripion</th><th>Purpose</th></tr></thead><tbody><tr><td><strong>Single-node</strong></td><td>All components including Kubernetes, Wireguard, Nginx, NFS run on the same machine. Multiple environments run in separate Kubernetes namespaces. PostgreSQL runs at Docker within each namespace.</td><td><p><strong>Sandbox</strong></p><p>Well suited for getting started with OpenG2P for creating development sandboxes like dev, qa etc. This setup can also be used for small scale pilots.</p></td></tr><tr><td><strong>Three-node</strong></td><td>The storage server is separated from the compute server (Kubernetes). PostgreSQL server runs on a separate "storage node" that contains large volumes of SSD storage with high througput disk I/O. The NFS also runs on this node. Thus, there is a separate of concerns between compute and data.</td><td><p><strong>Pilots | Small scale production</strong></p><p>For pilots and small scale production setups, specifically where I high uptime is not critical. If systems are predominantly used by administrators and some down time of services and portals is acceptable, then this architecture would be sufficient.</p></td></tr><tr><td><strong>Full-scale</strong></td><td>Multiple separate nodes for each of Wireguard, Nginx, Kubernetes nodes, NFS, PostgreSQL.</td><td><p><strong>Large scale production</strong></p><p>Full scale production deployment for following senarious:</p><ul><li>Multiple applications need to be supported on the cluster and clear separation of concerns is important.</li><li>Fail safety is critical — certain services must continue to run without interruptions. This typically will be the case with registration portals/beneficiary portals that have to be kept up and down time is not acceptable.</li><li>Scale is high in terms of compute requirements.</li><li>Fine grain access control for various resources of the system.</li><li>"Circuit breakers" for traffic control and attacks.</li></ul></td></tr></tbody></table>

{% hint style="warning" %}
Over and above all these, there is minimally one more node required for backups and running local Git and Docker repositories. Refer to [Prerequisites & Procurement → Compute](../../operations/deployment/prerequisites-procurement.md#compute-the-three-vms).
{% endhint %}

### Single-node

<figure><img src="../../.gitbook/assets/single-node-deployment.jpg" alt=""><figcaption></figcaption></figure>

* Single virtual machine running all services
* One Kubernetes cluster hosting both Rancher and OpenG2P services
* Nginx, Wireguard, NFS server running outside the Kubernetes cluster but on the same node
* Multiple environments like dev, qa, demo etc. as Kubernetes namespaces
* Access to each environment (namespace) can be controlled via [private access channels](../deployment-guide/private-access-channel.md). (The node needs multiple network interfaces to support the same).
* SSL termination (HTTPS) happens on the Nginx. The traffic further to Ingress gateway is HTTP.
* Firewall is outside the purview of this deployment.
* Git repo and Docker Registry are assumed externally hosted (public or private). For on-prem hosting you will need more resources to host the same as in [Three-node](openg2p-deployment-model.md#three-node) setup.
* As this deployment is based on Kubernetes, the system can be easily scaled up by adding more nodes (machines) as in [Full-scale](openg2p-deployment-model.md#full-scale) setup.

### Three-node

<figure><img src="../../.gitbook/assets/three-node-deployment (1).jpg" alt=""><figcaption></figcaption></figure>

* Separation of concerns - storage and reverse proxy on separate nodes
* PostgreSQL server runs on the Storage Node.
* Only one environment like Pilot or Prod is expected to run on the cluster. _Sharing same PosgreSQL server for multiple envirornments is not recommended. If you would like to do the same, make sure names of all databases are different for different environments._
* NFS server runs on the storage node
* Storage node is expected to have larger SSD disks and not very high compute capability, while Compute node must have high compute power and RAM. See [Prerequisites & Procurement → Compute](../../operations/deployment/prerequisites-procurement.md#compute-the-three-vms).
* Storage Node can be managed - in terms of access, scale up and backups indendently.
* Local Git repo and Docker Repositories may be hosted on Storage Node.
* Access to each environment (namespace) can be controlled via [private access channels](../deployment-guide/private-access-channel.md). (The node needs multiple network interfaces to support the same).
* SSL termination (HTTPS) happens on the Nginx. The traffic further to Ingress gateway is HTTP.
* Firewall is outside the purview of this deployment.

### Full-scale

<figure><img src="../../.gitbook/assets/deployment-architecture-v4.jpg" alt=""><figcaption></figcaption></figure>

* For multiple applications, large scale rollout where availability, real-time response is critical
* The Rancher cluster is separated from OpenG2P cluster as Rancher can manage multiple clusters.
* Organization wide Keycloak runs on Rancher cluster
* NFS server is hosted on a separate "Storage node".
* PostgreSQL (although not shown in the diagram) is also hosted on separate servers for production deployments. The same may be run on the above Storage node. Thus PostgreSQL and NFS may run on the same node if load can be handled.
* Multiple environments can run within OpenG2P cluster (as in single-node and three-node architectures
* Miniumum number of OpenG2P cluster nodes recommended is 3 nodes — this is for fail safety of Kubrenetes "master" node.
* More nodes may be added to the cluster as per scaling requirements
* Wireguard and Load Balancer (Nginx) run on separate nodes for better separation of concens and management.
* While OpenG2P departmental apps typically don't need such robust infrastructure, it's essential if you want fast-response, beneficiary-facing websites with zero downtime.

## Role of various components

The deployment utilizes several open source third party components. The concept and role of these components is given below:

<table><thead><tr><th width="165">Component</th><th>Description</th></tr></thead><tbody><tr><td><mark style="color:$primary;">Wireguard</mark></td><td><p><a href="https://www.wireguard.com/">Wireguard</a> is a fast secure &#x26; open-source VPN, with P2P traffic encryption that can enable secure (non-public) access to the resources. A combination of Wireguard, Nginx and Isto gateway is used to enable fine-grained access control to the environments. See <a href="../deployment-guide/private-access-channel.md">Private Access Channels</a>.</p><div data-gb-custom-block data-tag="hint" data-style="info" class="hint hint-info"><p>If you have your own VPN setup, Wireguard is not required. However, it is expected that the implementers take care of setting up secure access; OpenG2P only provides guidance for Wireguard.</p></div><blockquote><p><sup><em>The terms Wireguard, Wireguard Bastion and Wireguard Server are used interchangeably in this document.</em></sup></p></blockquote></td></tr><tr><td>Nginx</td><td>Nginx as a reverse-proxy for incoming external (public) traffic. It serves as HTTPS termination and together with Wireguard and Istio Gateway it can be used to create <a href="../deployment-guide/private-access-channel.md">private access channels</a>. Nginx isolates the internal network such that traffic does not directly fall on the Istio Gateway of the Kubernetes cluster. Nginx node needs to have public IP for public facing portals.</td></tr><tr><td>Istio</td><td><a href="https://istio.io/">Istio</a> is a service mesh that provides a way to connect, secure, control, and observe microservices. It is a powerful mesh management tool. It also provides an ingress gateway for the Kubernetes cluster. See note below.</td></tr><tr><td>Ingress Gateway</td><td>The <a href="https://istio.io/latest/docs/tasks/traffic-management/ingress/ingress-control/">Ingressgateway</a> component of Istio enables routing external traffic into Kubernetes services. Istio can be configured to do much more. Seen note below.</td></tr><tr><td>Rancher</td><td>Rancher provides advanced cluster management capabilities. It can also manage several clusters.</td></tr><tr><td>Keycloak</td><td>Keycloak provides <strong>organisation-wide authorisation</strong> and offers single sign-on for all resources.</td></tr><tr><td>NFS</td><td>Network File System (NFS) provides persistence to the resources of the Kubernetes cluster. Although on a single machine installation we can directly use the underlying SSD storage, we prefer to use NFS, keeping in mind scalability in case more nodes (machines) need to be added to the cluster.</td></tr><tr><td>Prometheus &#x26; Grafana</td><td>For system monitoring. <a href="../../monitoring-and-reporting/system-health.md">Learn more >></a></td></tr><tr><td>FluentD</td><td>For collecting and shunting logs of services to OpenSearch. <a href="../../operations/deployment/_archive/scaling/base-infrastructure/openg2p-cluster/fluentd-and-opensearch/">Learn more >></a></td></tr><tr><td>OpenSearch</td><td>For indexing and search of data. Primary used for logs and <a href="../../monitoring-and-reporting/reporting-framework/">reporting framework</a>.</td></tr><tr><td>PostgreSQL</td><td>Primary database of OpenG2P platform. For production deployment, PostgreSQL is installed on the VM directly (natively) while for sandboxes, PostgreSQL is installed on the Kubernetes cluster inside a namespace using PostgreSQL Docker.</td></tr></tbody></table>

{% hint style="info" %}
**Why Istio? What are the benefits of using Istio in OpenG2P setup?**

* We can have advanced traffic management setups like load balancing, retries & failovers, and fault injection for testing resilience.
* We can use advanced deployment strategies like canary deployments and A/B testing, where Istio can route higher percentage of traffic to specific service versions.
* We can enable security features like mTLS encryption for service-to-service traffic. Istio can also provide an authentication & authorization layer for services.
* We can also define policies related to access control & rate limiting. One can define which services are allowed to access other services or limit the rate of requests accepted by a service.
* More importantly Istio provides comprehensive observability features. We can visualize & monitor service-to-service traffic real-time, with tools like [Kiali](https://istio.io/latest/docs/ops/integrations/kiali/), which would help identify performance bottlenecks and diagnose issues.
{% endhint %}

## Base infrastructure

In all the architectures above there is a base infrastructure (comprising of Kubernetes, Nginx, Wireguard, NFS etc) over which specific environments are installed. Refer to the base infrastructure installation instructions [here](../../operations/deployment/_archive/deployment-instructions/infrastructure-setup.md).

## Environments

An environment is an insolated setup for a specific purpose like development, testing, staging, production etc. In OpenG2P's deployment model each environment resides in a _namespace_ in Kubernetes. The namespace contains set of common shared modules - [`openg2p-commons`](openg2p-commons-helm-chart.md) - and the modules (Registry, PBMS, SPAR, G2P Bridge) themselves along with any third-party dependency modules. Access to each environment can be controlled using [private access channels](../deployment-guide/private-access-channel.md) and RBAC of Kubernetes. Generally, all modules share the common resources like Postgres, MinIO, Kafka etc. These resources are installed as part of the [`openg2p-commons`](openg2p-commons-helm-chart.md) . Only one instance of PostgreSQL server is run per environment which means all modules use the same PostgreSQL server (Dockerized or external - depending on the choice of installation). An environment needs the following:

1. A short name of the environment (without hyphens, to keep it simple) like 'qa'. This name is used for domain name and namespace
2. Wildcard domain name like '\*.qa.openg2p.org' 'cause several services will run within this domain.
3. Installation of opengp2-commons
4. Installation of any (or all modules): Registry, PBMS, SPAR, G2P Bridge, Beneficiary Portal.

While the installation can be easily achieved by provided Helm Charts, tear down of the environment involves few manual steps. Refer to tear down section in the deployment documentation for each module.
