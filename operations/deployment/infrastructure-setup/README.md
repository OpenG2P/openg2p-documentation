---
description: Production (three-node) OpenG2P deployment — overview and sequence.
---

# Production — Three-Node

The production deployment runs OpenG2P across three Ubuntu 24.04 VMs — **Reverse Proxy**, **Compute** (Kubernetes), and **Storage** (host PostgreSQL + NFS) — with admin tools behind a Wireguard VPN and citizen-facing services on the public channel. For when to choose this over the sandbox, see [Deployment](../../../deployment/README.md).

Follow these in order:

1. **[Prerequisites & Procurement](../prerequisites-procurement.md)** — compute, DNS records, TLS certificate, server access, firewall. Start the long-lead items (compute + certificate) first.
2. **[Three-Node Infrastructure Automation](three-node-automation/)** — provision (optional) and install the cluster: RKE2, Istio, Rancher, Keycloak, monitoring, logging.
3. **[Environment Setup](../environment-setup-multi-node.md)** — install the OpenG2P modules into the production environment and open the public (citizen) channel.
4. **[Backups](../backups/)** — configure backups before go-live.
5. **[Production Best Practices](../production.md)** — hardening, HA, and operational recommendations.

The sandbox (single-node) path is documented separately under [Sandbox — Single-Node](single-node-automation.md).
