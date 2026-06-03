---
description: OpenG2P Deployment — choosing and running a sandbox or production deployment.
---

# Deployment

OpenG2P supports two deployment shapes. Pick the one that matches your stage, then follow that section — the prerequisites and steps differ.

| | **Sandbox** (Single-Node) | **Production** (Three-Node) |
| --- | --- | --- |
| **Use for** | Evaluation, dev/QA, demos, pilots-on-a-budget | Pilots and production rollouts |
| **Machines** | 1 VM | 3 VMs (Reverse Proxy, Compute, Storage) |
| **TLS** | Let's Encrypt or self-signed (built in) | Customer CA cert (commercial / sovereign) |
| **DNS** | Optional / local | Customer DNS (admin + citizen records) |
| **Admin access** | Direct (optional Wireguard) | Wireguard VPN + private channel |
| **Procurement lead time** | None — just a machine | Compute + certificate (2–4 weeks) |

{% hint style="info" %}
**Rule of thumb.** To get started quickly with a sandbox or two (dev/QA), use **Single-Node**. For pilots and production, use **Three-Node** — it's strongly recommended. If you do run a pilot on single-node, ensure backups are in place (data on Kubernetes-hosted PostgreSQL must be migrated to a standalone PostgreSQL server when you move to production — see the [migration guide](deployment-guide/transitioning-postgresql-from-docker-on-k8s-to-standalone-postgresql.md)).
{% endhint %}

* **Sandbox** → [Single-Node automation](../operations/deployment/infrastructure-setup/single-node-automation.md) (prerequisites are included on that page)
* **Production** → start with [Prerequisites & Procurement](../operations/deployment/prerequisites-procurement.md), then the [three-node infrastructure automation](../operations/deployment/infrastructure-setup/three-node-automation/)

Shared background for both lives under [Concepts](concepts/README.md).
