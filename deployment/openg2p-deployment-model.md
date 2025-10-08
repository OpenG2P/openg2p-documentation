# OpenG2P Deployment Model

OpenG2P’s **deployment model** offers a **production-grade, Kubernetes-based infrastructure** designed to deliver secure, scalable, and reliable deployments of OpenG2P modules. Built on a robust Kubernetes orchestration framework, it supports multiple isolated environments—such as Development, QA, and Demo sandboxes—within a single organisational setup, enabling seamless management across the entire software lifecycle. &#x20;

The OpenG2P deployment model is inspired by [V4 deployment architecture](scaling/v4-deployment-architecture.md) developed by OpenG2P team. Considering OpenG2P's use cases, resource availability with departments of countries, and ease of deployment,  we have adapted the V4 architure to be deployed in a "single box" - the entire installation in one sufficiently sized virtual machine or bare metal.

This deployment model ensures **secure access for internal development teams** and has been rigorously tested, earning an [**A+ rating in third-party penetration testing**](../privacy-and-security/security-audits/security-audit-2025-march.md), underscoring its strong security posture. By leveraging the same deployment model for development as well as production, it facilitates an **easy and efficient transition from development to production environments**, significantly reducing complexity and risks.

For System Integrators, the OpenG2P deployment model represents a substantial time and resource saver by eliminating the need to build production-grade deployment setups from scratch. This turnkey solution accelerates implementation while maintaining enterprise-level security and operational excellence, making it the ideal foundation for organisations aiming to deploy OpenG2P at scale with confidence.

The deployment is offered as a set of instructions, scripts, [Helm charts](../releases/helm-charts.md), utilities and guidelines.

The deployment is **cloud agnostic** - it does not use cloud specific components.&#x20;

<figure><img src="../.gitbook/assets/openg2p-deployment-model.jpg" alt=""><figcaption></figcaption></figure>

## Key concepts

* Each environment like 'qa', 'dev', 'staging', 'production' is installed in a **separate Kubernetes namespace** on the same cluster.
* Access to each environment (namespace) can be controlled via [private access channels](deployment-guide/private-access-channel.md).
* Firewall is outside the purview of this deployment.
* Git repo and Docker Registry are assumed externally hosted (public or private).  In case of production deployments, these should be hosted within private network. &#x20;
* As this deployment is based on Kubernetes, the system can be easily scaled up by adding more nodes (machines).&#x20;

## Role of various components

The deployment utilizes several open source third party components. The concept and role of these components is given below:

<table><thead><tr><th width="221">Component</th><th>Description</th></tr></thead><tbody><tr><td><mark style="color:$primary;">Wireguard</mark></td><td><p><a href="https://www.wireguard.com/">Wireguard</a> is a fast secure &#x26; open-source VPN, with P2P traffic encryption that can enable secure (non-public) access to the resources.  A combination of Wireguard, Nginx and Isto gateway is used to enable fine-grained access control to the environments.  See <a href="deployment-guide/private-access-channel.md">Private Access Channels</a>.</p><p><sup><em>Note that the terms Wireguard, Wireguard Bastion and Wireguard Server are used interchangeably in this document.</em></sup></p></td></tr><tr><td>Nginx</td><td>Nginx as a reverse-proxy for incoming external (public) traffic. It serves as HTTPS termination and together with Wireguard and Istio Gateway it can be used to create <a href="deployment-guide/private-access-channel.md">private access channels</a>.  Nginx isolates the internal network such that traffic does not directly fall on the Istio Gateway of the Kubernetes cluster.</td></tr><tr><td>Ingress Gateway</td><td></td></tr><tr><td>Rancher</td><td></td></tr><tr><td>Keycloak</td><td></td></tr><tr><td>Istio</td><td></td></tr><tr><td>NFS</td><td></td></tr><tr><td>Prometheus &#x26; Grafana</td><td></td></tr><tr><td>FluentD</td><td></td></tr><tr><td>OpenSearch</td><td></td></tr></tbody></table>

