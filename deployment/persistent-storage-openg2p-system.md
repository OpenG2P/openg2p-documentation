---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Persistent Storage - OpenG2P System

This document provides information on all the Persistent storages, i.e., PVs (Persistent Volume) and PVCs (Persistent Volume Claim), in OpenG2P deployments. It describes the type of storage, deletion behavior, and how to identify which PV belongs to which pod. It also defines and highlights the specific behavior of the stateful sets and deployments.

## **Overview of Persistent storage in OpenG2P system**

<table><thead><tr><th width="167">Types of PVs</th><th width="430">Purpose</th><th>Type</th></tr></thead><tbody><tr><td>Postgres</td><td>Stores database data for the application.</td><td>StatefulSet</td></tr><tr><td>OpenSearch</td><td>Stores indexing data, logs, and search-related data.</td><td>StatefulSet</td></tr><tr><td>Minio</td><td>Stores object data, files, and backups.</td><td>Deployment</td></tr><tr><td>SoftHSM</td><td><ul><li>Stores cryptographic key data used for secure key storage and management. </li><li>SoftHSM acts as a software-based Hardware Security Module (HSM) for the application.</li></ul></td><td>Deployment</td></tr><tr><td>Kafka</td><td><ul><li>Stores Kafka logs and messages, ensuring durability and persistence of data in the event of a pod restart or failure.</li><li>Kafka's stateful nature requires persistent storage to maintain message integrity.</li></ul></td><td>StatefulSet</td></tr><tr><td>Odoo</td><td>Stores database data, files, and other persistent configurations for the Odoo ERP system and ensures that data is retained across pod during restarting and upgrades.</td><td>Deployment</td></tr></tbody></table>

### **Types of persistent storage**

<table><thead><tr><th width="141"></th><th width="318">Statefulset attached storage</th><th>Deployment attached storage</th></tr></thead><tbody><tr><td>Definition</td><td>Statefulsets are used for applications that require stable network identities and persistent storage. The pods in a StatefulSet have unique identities and their storage is tied to their lifecycle. When a pod in a StatefulSet is deleted, the storage (PV) remains intact unless explicitly deleted.</td><td>In stateless applications, deployments are used so that any pod can be replaced by another. The storage associated with a deployment is generally ephemeral unless PVs are explicitly attached.</td></tr><tr><td>Deletion behavior</td><td>By default, the storage attached to a StatefulSet is retained even after the pod is deleted. This is crucial for stateful applications where data persistence is critical.</td><td>If PVs are attached to a deployment, the storage may be deleted when the deployment is deleted, depending on the reclaim policy. Unlike StatefulSets, Deployments do not guarantee data persistence when pods are scaled down or deleted.</td></tr><tr><td>Examples</td><td>Postgres, OpenSearch, and Minio.</td><td>Some auxiliary services might use Deployment-based storage, but it is less common for critical data.</td></tr></tbody></table>

### **Persistent Volume Reclaim Policies: Retain vs. Delete**

<table><thead><tr><th width="154"></th><th>Retain</th><th>Delete</th></tr></thead><tbody><tr><td>Behavior</td><td>When a PVC is deleted, the associated PV is not automatically deleted. This is helpful if you want to reattach the PV to another PVC in the future or as a backup.</td><td>When a PVC is deleted, the associated PV is also automatically deleted. This is more suitable for temporary or non-critical data.</td></tr><tr><td>Use Case</td><td>Critical data that you may want to preserve even after deleting the PVC or StatefulSet.</td><td>Ephemeral or temporary data where automatic cleanup is preferred.</td></tr></tbody></table>

### **Procedure**

#### How to check which PV belongs to which Pod&#x20;

In Rancher, follow the below steps to check which PV is associated with a particular pod.

1. Launch Rancher, then select the cluster where your deployment resides.
2. Select the namespace where your pods are deployed.
3. Navigate to **Workloads** > **Pods** to identify the pod. Each pod that uses persistent storage will have a PVC associated with it.
4. Click on the pod and look for the _**Volumes**_ section under the pod specification. Here, you will find the name of the PVC associated with the pod.
5. Navigate to **Storage** > **PersistentVolumeClaims**. Find the PVC name from the previous step. When you click on the PVC, the associated PV will appear.
6. Click on the PV to view additional information on its capacity, reclaim policy, and status.
