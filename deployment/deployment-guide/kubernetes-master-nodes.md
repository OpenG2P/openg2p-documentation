# Kubernetes Cluster Deployment Guide

This document explains how Kubernetes control-plane (master) node count affects high availability — etcd quorum, fault tolerance, and the trade-offs of single vs. multi-master clusters.

{% hint style="info" %}
**How this maps to OpenG2P.** The two production configurations differ only in control-plane count:

* **Production — Minimum** (the default the automation provisions today) runs a **single RKE2 control-plane** on the Compute node. This is a supported production model for pilots and small-scale deployments where brief downtime during a node failure is acceptable — recovery relies on the backup automation (etcd snapshots, pgBackRest, etc.), not on live redundancy.
* **Production — High-Availability** scales the *same architecture* out to **3+ control-plane nodes** (odd count) so the cluster survives a node failure with no downtime. This is a manual/extension step today, not yet automated.

The rest of this page is the theory behind that choice — read it when deciding whether a deployment needs HA.
{% endhint %}

#### **Understanding Kubernetes Master Node Count: Odd vs. Even**

In a Kubernetes cluster, master nodes (control plane nodes) manage cluster state, schedule workloads, and ensure high availability.

#### **Why Should Master Nodes Be in an Odd Number?**

Kubernetes relies on **etcd**, a distributed key-value store, for cluster state management. **etcd requires a quorum (majority vote) for leader election and decision-making.**

* Having an **odd number of master nodes** prevents split-brain scenarios and ensures the cluster continues operating even if some nodes fail.
* For high availability, at least **three master nodes** are recommended.

**Fault Tolerance Formula:**

<table data-header-hidden><thead><tr><th width="370"></th><th></th></tr></thead><tbody><tr><td>Master Nodes</td><td>Failures Tolerated</td></tr><tr><td>3</td><td>1</td></tr><tr><td>5</td><td>2</td></tr></tbody></table>

#### **What Happens with an Even Number of Masters?**

* If the number of master nodes is **even** (e.g., 2 or 4), it increases the risk of a **split-brain situation**, where etcd cannot reach a majority, making the cluster **unstable or unavailable**.
* **Two masters are not recommended**, as losing one results in quorum loss, preventing decision-making.

#### **Minimum Requirements for a Kubernetes Cluster**

* A **high-availability (HA) cluster** should have at least **3 master nodes**.
* Each master node runs **etcd, the API server, scheduler, and controllers**.
* If using **3 master nodes**, at least **3 worker nodes** are recommended, though master nodes can schedule workloads in small setups.

#### **Control-plane counts and where they fit**

* **Single control-plane (1 node)** – No live HA. Used by **OpenG2P Production — Minimum** (and sandbox) where brief downtime during a node failure is acceptable; resilience comes from the **backup automation** (etcd snapshots, pgBackRest, rancher-backup, restic), not redundancy. Also the right choice for dev/test.
* **Three control-planes (3 nodes)** – **OpenG2P Production — High-Availability**. Survives one node failure with no downtime; recommended when near-zero-downtime is a requirement.
* **Five control-planes (5+ nodes)** – Large-scale deployments tolerating two simultaneous failures.

#### **Single control-plane: what to know**

A single control-plane is a legitimate production model for OpenG2P Production — Minimum, with one important caveat to plan around:

* **No live HA** – if the control-plane node fails, the cluster is unavailable until it's recovered.
* **Recovery, not redundancy** – etcd is snapshotted by the backup automation, so the cluster can be **restored** after a failure; this trades a recovery window for lower cost and complexity. Ensure backups (etcd snapshots especially) are configured **before go-live**.

**Choose HA (3+ control-planes) when** the deployment cannot tolerate any downtime — then run an odd number of control-plane nodes so etcd always has a quorum.
