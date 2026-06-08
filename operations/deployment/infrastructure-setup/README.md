---
description: Production OpenG2P deployment — overview, sequence, and operational follow-on.
---

# Production

The production deployment runs OpenG2P across role-specialised VMs — **Reverse Proxy**, **Compute** (Kubernetes), and **Storage** (host PostgreSQL + NFS) — with admin tools behind a Wireguard VPN and citizen-facing services on the public channel.

<figure><img src="../../../.gitbook/assets/three-node-deployment (1).jpg" alt=""><figcaption></figcaption></figure>

It comes in two configurations, sharing the **same architecture** — the difference is the number of nodes:

* **Production — Minimum** (three nodes; one RP, one Compute, one Storage) — pilots and small-scale production where some downtime is acceptable. This is what the automation provisions today.
* **Production — High-Availability** (more nodes; HA Kubernetes control plane, redundant RPs behind a load balancer, PostgreSQL primary/replica) — large-scale or near-zero-downtime deployments. A supported scaling-up of the same architecture; manual/extension work today, not yet automated.

See [OpenG2P Deployment Architecture](../../../deployment/openg2p-deployment-model.md) for the full conceptual picture, and [Deployment](../../../deployment/) for choosing between sandbox and production.

## The five stages

A production rollout happens in five stages. Stage 1 (Procurement) can — and should — start in parallel with Stage 2 (Provisioning), since the cert and DNS items in Stage 1 typically take **2–4 weeks** to deliver. Stages 3, 4, and 5 are strictly serial.

```mermaid
flowchart LR
    S1["1. Procurement<br/>compute specs · DNS · TLS cert<br/>server access · firewall plan<br/><i>2-4 weeks lead time</i>"]
    S2["2. Provisioning<br/>bring up the 3 VMs<br/>on-prem or AWS"]
    S3["3. Infrastructure<br/>RKE2, Istio, Rancher,<br/>Keycloak, WG, Nginx, NFS,<br/>host PostgreSQL"]
    S4["4. Environment<br/>namespace, Istio Gateway,<br/>commons-base + commons-services"]
    S5["5. Modules<br/>per-product Helm charts<br/>(Registry, PBMS, SPAR, …)"]

    S1 -. "in parallel" .-> S2
    S2 --> S3 --> S4 --> S5
```

| Stage                 | Page                                                                                                                                                                                                            | What you produce                                                                                                                                                                                                                                  |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Procurement**    | [Prerequisites & Procurement](../prerequisites-procurement.md)                                                                                                                                                  | A confirmed shopping list — compute specs, DNS records to create, the TLS certificate, server-access plan, firewall rules. Requests have gone to your network / cert / IT team.                                                                   |
| **2. Provisioning**   | [Provisioning](provisioning.md) (with [AWS Provisioning](three-node-automation/aws-provisioning.md) sub-page for the AWS path)                                                                                  | Three Ubuntu 24.04 VMs running, on one private subnet, SSH-reachable from the deployer's workstation.                                                                                                                                             |
| **3. Infrastructure** | [Infrastructure Automation](three-node-automation/)                                                                                                                                                             | The cluster platform: RKE2, Istio, Rancher, Keycloak (admin SSO), monitoring, logging, Wireguard, Nginx with customer-provided TLS, NFS server + host PostgreSQL. Admin tools reachable over the VPN.                                             |
| **4. Environment**    | Run by the **same** [Infrastructure Automation](three-node-automation/#the-environment-stage) (`openg2p-prod.sh`); [Environment Setup](../environment-setup-multi-node.md) is the deep reference / standalone path | A working environment namespace with the Rancher Project, Istio Gateway, and `openg2p-commons-base` + `openg2p-commons-services` (PostgreSQL, Kafka, MinIO, Redis, Keycloak realm, Superset, eSignet, ODK, etc.) installed. Public 80/443 opened. |
| **5. Modules**        | Per-product deployment pages — [Registry](../../../products/registry/registry/deployment/), [PBMS](../../../pbms/deployment/), [SPAR](../../../spar/deployment/), [G2P Bridge](../../../g2p-bridge/deployment/) | Your chosen OpenG2P product modules installed into the environment via their own Helm charts.                                                                                                                                                     |

{% hint style="info" %}
**Stages 3 and 4 are one command.** The environment install (Stage 4) is built into the infrastructure automation — it runs as the `environment` stage at the tail of `openg2p-prod.sh`, not as a separate tool you invoke from another folder. It's listed as its own stage for clarity, and can be re-run on its own (`./openg2p-prod.sh --stage environment …`). The [Environment Setup](../environment-setup-multi-node.md) page documents the underlying `env-cluster.sh` and standalone / multi-environment use.
{% endhint %}

## Ongoing operational concerns

These are not deployment stages — they are continuous responsibilities that begin **before go-live** and continue throughout the system's lifetime.

* [**Backups**](../backups/) — configure pgBackRest, etcd snapshots, rancher-backup, and restic for NFS/configs. Set up the backup node, schedule the drills. Must be in place before go-live.
* [**Production Best Practices**](../production.md) — hardening, HA recommendations, air-gap considerations, RBAC, image-pull policy, Nginx tuning. Apply incrementally; consult per deployment context.

## Sandbox is different

For evaluation, demos, dev/QA, or small pilots, use the [Sandbox — Single-Node](single-node-automation.md) path instead. Sandbox collapses all five stages into a single VM and a pair of scripts — no separate procurement, provisioning, infrastructure, environment, or modules phases. The staged flow described above applies only to Production.
