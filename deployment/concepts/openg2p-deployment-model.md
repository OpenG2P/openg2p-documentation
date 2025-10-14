# OpenG2P Deployment Model

OpenG2P’s **deployment model** offers a **production-grade, Kubernetes-based infrastructure** designed to deliver secure, scalable, and reliable deployments of OpenG2P modules. Built on a robust Kubernetes orchestration framework, it supports multiple isolated environments—such as Development, QA, and Demo sandboxes—within a single organisational setup, enabling seamless management across the entire software lifecycle. &#x20;

The OpenG2P deployment model is inspired by [V4 deployment architecture](../scaling/v4-deployment-architecture.md) developed by OpenG2P team. Considering OpenG2P's use cases, resource availability with departments of countries, and ease of deployment,  we have adapted the V4 architure to be deployed in a "single box" - the entire installation in one sufficiently sized virtual machine or bare metal.

This deployment model ensures **secure access for internal development teams** and has been rigorously tested, earning an [**A+ rating in third-party penetration testing**](../../privacy-and-security/security-audits/security-audit-2025-march.md), underscoring its strong security posture. By leveraging the same deployment model for development as well as production, it facilitates an **easy and efficient transition from development to production environments**, significantly reducing complexity and risks.

For System Integrators, the OpenG2P deployment model represents a substantial time and resource saver by eliminating the need to build production-grade deployment setups from scratch. This turnkey solution accelerates implementation while maintaining enterprise-level security and operational excellence, making it the ideal foundation for organisations aiming to deploy OpenG2P at scale with confidence.

The deployment is offered as a set of instructions, scripts, [Helm charts](../../releases/helm-charts.md), utilities and guidelines.

The deployment is **cloud agnostic** - it does not use cloud specific components.&#x20;

<figure><img src="../../.gitbook/assets/openg2p-deployment-model.jpg" alt=""><figcaption></figcaption></figure>

## Key concepts

* Each environment like 'qa', 'dev', 'staging', 'production' is installed in a **separate Kubernetes namespace** on the same cluster.
* Access to each environment (namespace) can be controlled via [private access channels](../deployment-guide/private-access-channel.md).
* Firewall is outside the purview of this deployment.
* Git repo and Docker Registry are assumed externally hosted (public or private).  In case of production deployments, these should be hosted within private network. &#x20;
* As this deployment is based on Kubernetes, the system can be easily scaled up by adding more nodes (machines).&#x20;

## Role of various components

The deployment utilizes several open source third party components. The concept and role of these components is given below:

<table><thead><tr><th width="221">Component</th><th>Description</th></tr></thead><tbody><tr><td><mark style="color:$primary;">Wireguard</mark></td><td><p><a href="https://www.wireguard.com/">Wireguard</a> is a fast secure &#x26; open-source VPN, with P2P traffic encryption that can enable secure (non-public) access to the resources.  A combination of Wireguard, Nginx and Isto gateway is used to enable fine-grained access control to the environments.  See <a href="../deployment-guide/private-access-channel.md">Private Access Channels</a>.</p><p><sup><em>Note that the terms Wireguard, Wireguard Bastion and Wireguard Server are used interchangeably in this document.</em></sup></p></td></tr><tr><td>Nginx</td><td>Nginx as a reverse-proxy for incoming external (public) traffic. It serves as HTTPS termination and together with Wireguard and Istio Gateway it can be used to create <a href="../deployment-guide/private-access-channel.md">private access channels</a>.  Nginx isolates the internal network such that traffic does not directly fall on the Istio Gateway of the Kubernetes cluster.</td></tr><tr><td>Ingress Gateway</td><td></td></tr><tr><td>Rancher</td><td></td></tr><tr><td>Keycloak</td><td></td></tr><tr><td>Istio</td><td></td></tr><tr><td>NFS</td><td></td></tr><tr><td>Prometheus &#x26; Grafana</td><td></td></tr><tr><td>FluentD</td><td></td></tr><tr><td>OpenSearch</td><td></td></tr></tbody></table>

## Installation of an environment

An environment is an insolated setup for a specific purpose like development, testing, staging, production etc.  In OpenG2P's deployment model each environment is a namespace in Kubernetes.  The namespace contains set of common shared modules - `openg2p-commons` - and the modules (Registry, PBMS, SPAR, G2P Bridge) themselves along with any third-party dependency modules.  Access to each environment can be controlled using [private access channels](../deployment-guide/private-access-channel.md) and RBAC of Kubernetes.

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
