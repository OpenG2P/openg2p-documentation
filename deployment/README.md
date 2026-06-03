---
description: OpenG2P Deployment — choosing and running a sandbox or production deployment.
---

# Deployment

OpenG2P supports two deployment shapes. Pick the one that matches your stage, then follow that section — the prerequisites and steps differ.

| | **Sandbox** (Single-Node) | **Production** |
| --- | --- | --- |
| **Use for** | Evaluation, dev/QA, demos, pilots-on-a-budget | Pilots and production rollouts |
| **Machines** | 1 VM | **Minimum:** 3 VMs (RP, Compute, Storage). **High-Availability:** more nodes of the same shape — HA control plane, redundant RPs, PG primary/replica |
| **TLS** | Let's Encrypt or self-signed (built in) | Customer CA cert (commercial / sovereign) |
| **DNS** | Optional / local | Customer DNS (admin + citizen records) |
| **Admin access** | Direct (optional Wireguard) | Wireguard VPN + private channel |
| **Procurement lead time** | None — just a machine | Compute + certificate (2–4 weeks) |

{% hint style="info" %}
**Rule of thumb.** To get started quickly with a sandbox or two (dev/QA), use **Single-Node**. For pilots and production, use the **Production** path — strongly recommended. The Production path has two configurations sharing the same architecture: **Minimum** (the 3-node setup the automation provisions today) and **High-Availability** (more nodes added for redundancy — supported architecture, not yet automated). If you do run a pilot on single-node, ensure backups are in place (data on Kubernetes-hosted PostgreSQL must be migrated to a standalone PostgreSQL server when you move to production — see the [migration guide](deployment-guide/transitioning-postgresql-from-docker-on-k8s-to-standalone-postgresql.md)).
{% endhint %}

* **Sandbox** → [Single-Node automation](../operations/deployment/infrastructure-setup/single-node-automation.md) (prerequisites are included on that page)
* **Production** → start with [Prerequisites & Procurement](../operations/deployment/prerequisites-procurement.md), then the [infrastructure automation](../operations/deployment/infrastructure-setup/three-node-automation/)

For the conceptual picture (deployment models, architecture, channel separation), see [OpenG2P Deployment Architecture](openg2p-deployment-model.md).
