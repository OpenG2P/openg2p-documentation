---
description: 'Production Deployment Guide: WORK IN PROGRESS'
---

# Production

The guide here provides some useful hints for production deployment. However, this guide is not intended to be a comprehensive production deployment handbook. Production deployments vary and implementers of OpenG2P (like System Integrators) have a choice of production configurations, orchestration platforms and components. We also encourage our partners to update this guide based on their learning in the field.

## Postgresql&#x20;

* Number of instances
* Cloud native if available
* Production configuration
* Master / Slave configuration

## High availability of services

### Pod replication

* Replication of pods for high-availability.

### Node replication

* Provisioning of VMs across different underlying hardware and subnets for resilience.  does
* Minimum 3 nodes for Rancher and OpenG2P cluster (3 control planes).

## Backup and Restore

### ETCD&#x20;

Backup the etcd data of all clusters to ensure recovery in case of a complete failure. Here is how to create and restore backups of the etcd data in an RKE2 cluster.\
**Note:** /var/lib/rancher/rke2 is the default data directory for rke2. In RKE2, snapshots are stored on each etcd node. If you have multiple etcd or etcd + control-plane nodes, you will have multiple copies of local etcd snapshots.

You can take a snapshot manually while RKE2 is running with the `etcd-snapshot` subcommand. For example: `rke2 etcd-snapshot save --name pre-upgrade-snapshot`.

### Restoring a snapshot to existing nodes

When RKE2 is restored from backup, the old data directory will be moved to /var/lib/rancher/rke2/server/db/etcd-old-%date%/. RKE2 will then attempt to restore the snapshot by creating a new data directory and start etcd with a new RKE2 cluster with one etcd member.

1. You must stop RKE2 service on all server nodes if it is enabled via systemd. Use the following command to do so:\
   `systemctl stop rke2-server`
2. Next, you will initiate the restore from snapshot on the first server node with the following commands:\
   `rke2 server \`\
   &#x20;   `--cluster-reset \`\
   &#x20;   `--cluster-reset-restore-path=<PATH-TO-SNAPSHOT>`
3. Once the restore process is complete, start the rke2-server service on the first server node as follows:\
   `systemctl start rke2-server`
4. Remove the rke2 db directory on the other server nodes as follows:\
   `rm -rf /var/lib/rancher/rke2/server/db`
5. Start the rke2-server service on other server nodes with the following command:\
   `systemctl start rke2-server`

### Restoring a snapshot to new nodes

**Note:** For all versions of rke2 v.1.20.9 and prior, you will need to back up and restore certificates first due to a known issue in which bootstrap data might not save on restore (Steps 1 - 3 below assume this scenario). See [note](https://docs.rke2.io/backup\_restore#other-notes-on-restoring-a-snapshot) below for an additional version-specific restore caveat on restore.

1. Back up the following: `/var/lib/rancher/rke2/server/cred`, `/var/lib/rancher/rke2/server/tls`, `/var/lib/rancher/rke2/server/token`, `/etc/rancher`
2. Restore the certs in Step 1 above to the first new server node.
3. Install rke2 v1.20.8+rke2r1 on the first new server node as in the following example:\
   `curl -sfL https://get.rke2.io | INSTALL_RKE2_VERSION="v1.20.8+rke2r1" sh -`
4. Stop RKE2 service on all server nodes if it is enabled and initiate the restore from snapshot on the first server node with the following commands:\
   `systemctl stop rke2-server`\
   `rke2 server \`\
   &#x20;   `--cluster-reset \`\
   &#x20;   `--cluster-reset-restore-path=<PATH-TO-SNAPSHOT>`
5. Once the restore process is complete, start the rke2-server service on the first server node as follows:\
   `systemctl start rke2-server`
6. You can continue to add new server and worker nodes to cluster.

### NFS&#x20;

### Cluster access key

Downloading of user's cluster access key to be able to operate OpenG2P cluster directly using `kubectl` in case Rancher is not accessible. Sys Admins may download this key using Rancher console and keep them safely and protected with them.

## Security

* Creation of [private access channels](deployment-guide/private-access-channel.md).

## Nginx

You may need to set Nginx load balancers in HA mode by having a Nginx cluster (available with Nginx Plus, but it comes with commercial terms).  HA for Nginx is critical if user-facing portal traffic lands on the same.  For back-office administration tasks, HA may not be critical.

## OpenSearch

* Enable data nodes in OpenSearch so that backups can be taken of the data node.
* The data node maybe enabled while installing OpenSearch. _(TBD)._

## CEPH Storage

If the Kubernetes clusters are used for other critical applications with large data that is critical, CEPH storage may be considered. CEPH is a highly scalable and distributed data storage which provides high performance, reliability and scalability.  The storage system is installed on a separate cluster and Kubernetes communicates the same via CSI drivers that are available. CEPH automatically replicates data across multiple nodes, ensuring data redundancy and protection against node failures. However,  CEPH is very complex to set up and manage as compared to say NFS.  It has a steep learning curve. Further, it requires high resources (CPU, memory, network).
