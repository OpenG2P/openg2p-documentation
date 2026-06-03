---
description: Production OpenG2P deployment — overview and sequence.
---

# Production

The production deployment runs OpenG2P across role-specialised VMs — **Reverse Proxy**, **Compute** (Kubernetes), and **Storage** (host PostgreSQL + NFS) — with admin tools behind a Wireguard VPN and citizen-facing services on the public channel.

It comes in two configurations, sharing the **same architecture** — the difference is the number of nodes:

* **Production — Minimum** (three nodes; one RP, one Compute, one Storage) — pilots and small-scale production where some downtime is acceptable. This is what the automation provisions today.
* **Production — High-Availability** (more nodes; HA Kubernetes control plane, redundant RPs behind a load balancer, PostgreSQL primary/replica) — large-scale or near-zero-downtime deployments. A supported scaling-up of the same architecture; manual/extension work today, not yet automated.

See [OpenG2P Deployment Architecture](../../../deployment/openg2p-deployment-model.md) for the full conceptual picture, and [Deployment](../../../deployment/README.md) for choosing between sandbox and production.

## Production setup sequence

Follow these in order (applies to both Minimum and High-Availability — HA just adds more nodes of the same shape):

1. **[Prerequisites & Procurement](../prerequisites-procurement.md)** — compute, DNS records, TLS certificate, server access, firewall. Start the long-lead items (compute + certificate) first.
2. **[Infrastructure Automation](three-node-automation/)** — provision (optional) and install the cluster: RKE2, Istio, Rancher, Keycloak, monitoring, logging.
3. **[Environment Setup](../environment-setup-multi-node.md)** — install the OpenG2P modules into the production environment and open the public (citizen) channel.
4. **[Backups](../backups/)** — configure backups before go-live.
5. **[Production Best Practices](../production.md)** — hardening, HA, and operational recommendations.

The sandbox (single-node) path is documented separately under [Sandbox — Single-Node](single-node-automation.md).
