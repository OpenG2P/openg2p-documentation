# Kubernetes Cluster Deployment Guide

This document provides essential guidelines for deploying a Kubernetes cluster, emphasizing the importance of having an odd number of master nodes for high availability. It explains fault tolerance, risks of even-numbered masters, and best practices for production environments. Additionally, it covers the feasibility of having a single master and worker node, highlighting its limitations for production use.

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

#### **Best Practices for Deploying Master Nodes**

* **Single Master (1 Node)** – Suitable for **non-production/testing** (no HA).
* **Three Masters (3 Nodes)** – Recommended for **small to medium HA clusters**.
* **Five Masters (5+ Nodes)** – Used for **large-scale enterprise deployments**.

#### **Is It OK to Have One Master and One Worker?**

Yes, but it is **not recommended for production**.

**✅ When is it OK?**

* **Development/Testing** – For local development or testing purposes.
* **Lightweight Workloads** – When applications are not critical and do not require high availability.

**🚨 Why is it NOT Recommended for Production?**

* **No High Availability (HA)** – If the master node fails, the cluster becomes completely unavailable.
* **Single Point of Failure** – The worker node relies on the master for scheduling, so if the master crashes, new workloads cannot be assigned.
* **No Redundancy** – etcd (which stores the cluster state) has no backup, increasing the risk of data loss.

**🔹 Recommended Minimum for Production**

* **1 Master, 2+ Workers** – Still not HA but better than a single worker.
* **3 Masters, 2+ Workers** – Ensures high availability and fault tolerance.
