---
description: 'Production Deployment Guide: WORK IN PROGRESS'
---

# Production

The guide here provides some useful hints for production deployment. However, this guide is not intended to be a comprehensive production deployment handbook. Production deployments vary and implementers of OpenG2P (like System Integrators) have a choice of production configurations, orchestration platforms and components. We also encourage our partners to update this guide based on their learning in the field.

## Postgresql&#x20;

* Number of instances
* Cloud native
* Production configuration

## High availability

### Pod replication

* Replication of pods for high-availability.

### Node replication

* Provisioning of VMs across different underlying hardware and subnets for resilience.  does
* Minimum 3 nodes for Rancher and OpenG2P cluster (3 control planes).

## Backups

### ETCD&#x20;

Backup of `etcd` of all clusters for recovery in case of complete failure.

### NFS&#x20;

## Security

* Creation of [access channels](deployment-guide/security/access-channel.md).

## CEPH Storage

If the Kubernetes clusters are used for other critical applications with large data that is critical, CEPH storage may be considered. CEPH is a highly scalable and distributed data storage which provides high performance, reliability and scalability.  The storage system is installed on a separate cluster and Kubernetes communicates the same via CSI drivers that are available. CEPH automatically replicates data across multiple nodes, ensuring data redundancy and protection against node failures. However,  CEPH is very complex to set up and manage as compared to say NFS.  It has a steep learning curve. Further, it requires high resources (CPU, memory, network).
