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

# Persistent Storage

This document provides information on all the Persistent storages, i.e., PVs (Persistent Volume) and PVCs (Persistent Volume Claim), in OpenG2P deployments. It describes the type of storage, deletion behavior, and how to identify which PV belongs to which pod. It also defines and highlights the specific behavior of the StatefulSets and Deployments.

### **Types of persistent storage**

<table><thead><tr><th width="162">Storage type</th><th width="306">Definition</th><th>Deletion behavior</th></tr></thead><tbody><tr><td>StatefulSet attached storage</td><td><p>StatefulSets are used for applications that require stable network identities and persistent storage. The pods in a StatefulSet have unique identities and their storage is tied to their lifecycle. When a pod in a StatefulSet is deleted, the storage (PV) remains intact unless explicitly deleted. </p><p></p><p>Examples: Postgres, OpenSearch, and Minio.</p></td><td>By default, the storage attached to a StatefulSet is retained even after the pod is deleted. This is crucial for stateful applications where data persistence is critical.</td></tr><tr><td>Deployment attached storage</td><td><p>In stateless applications, deployments are used so that any pod can be replaced by another. The storage associated with a deployment is generally ephemeral unless PVs are explicitly attached. </p><p></p><p>Examples: Some auxiliary services might use Deployment-based storage, but it is less common for critical data. </p></td><td>If PVs are attached to a deployment, the storage may be deleted when the deployment is deleted, depending on the reclaim policy. Unlike StatefulSets, Deployments do not guarantee data persistence when pods are scaled down or deleted.</td></tr></tbody></table>

### Types of PVs

<table><thead><tr><th width="167">Types of PVs</th><th width="430">Purpose</th><th>Type</th></tr></thead><tbody><tr><td>Postgres</td><td>Stores database data for the application.</td><td>StatefulSet</td></tr><tr><td>OpenSearch</td><td>Stores indexing data, logs, and search-related data.</td><td>StatefulSet</td></tr><tr><td>Minio</td><td>Stores object data, files, and backups.</td><td>Deployment</td></tr><tr><td>SoftHSM</td><td><ul><li>Stores cryptographic key data used for secure key storage and management. </li><li>SoftHSM acts as a software-based Hardware Security Module (HSM) for the application.</li></ul></td><td>Deployment</td></tr><tr><td>Kafka</td><td><ul><li>Stores Kafka logs and messages, ensuring durability and persistence of data in the event of a pod restart or failure.</li><li>Kafka's stateful nature requires persistent storage to maintain message integrity.</li></ul></td><td>StatefulSet</td></tr><tr><td>Odoo</td><td>Stores database data, files, and other persistent configurations for the Odoo ERP system and ensures that data is retained across pod during restarting and upgrades.</td><td>Deployment</td></tr></tbody></table>

### **Persistent volume reclaim policies: retain vs. delete**

<table><thead><tr><th width="154">Reclaim policy</th><th>Behavior</th><th>Use case</th></tr></thead><tbody><tr><td>Retain</td><td>When a PVC is deleted, the associated PV is not automatically deleted. This is helpful if you want to reattach the PV to another PVC in the future or as a backup.</td><td>Critical data that you may want to preserve even after deleting the PVC or StatefulSet.</td></tr><tr><td>Delete</td><td>When a PVC is deleted, the associated PV is also automatically deleted. This is more suitable for temporary or non-critical data.</td><td>Ephemeral or temporary data where automatic cleanup is preferred.</td></tr></tbody></table>

### Checking which PV belongs to which pod&#x20;

In Rancher, follow the below steps to check which PV is associated with a particular pod.

1. Launch Rancher, then select the cluster where your deployment resides.
2. Select the namespace where your pods are deployed.
3. Navigate to **Workloads** > **Pods** to identify the pod. Each pod that uses persistent storage will have a PVC associated with it.
4. Click on the pod and look for the _**Volumes**_ section under the pod specification. Here, you will find the name of the PVC associated with the pod.
5. Navigate to **Storage** > **PersistentVolumeClaims**. Find the PVC name from the previous step. When you click on the PVC, the associated PV will appear.
6. Click on the PV to view additional information on its capacity, reclaim policy, and status.
