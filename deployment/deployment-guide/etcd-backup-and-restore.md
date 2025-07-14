---
description: Guide to backup Kubernetes Master ETCD
---

# ETCD Backup and Restore

Backup of the etcd data of all clusters to ensures recovery in case of a complete failure. Here is how to create and restore backups of the etcd data in an RKE2 cluster.\
**Note:** /var/lib/rancher/rke2 is the default data directory for rke2. In RKE2, snapshots are stored on each etcd node. If you have multiple etcd or etcd + control-plane nodes, you will have multiple copies of local etcd snapshots.

You can take a snapshot manually while RKE2 is running with the `etcd-snapshot` subcommand. For example: `rke2 etcd-snapshot save --name pre-upgrade-snapshot`.

### Restoring a snapshot to existing nodes

When RKE2 is restored from backup, the old data directory will be moved to /var/lib/rancher/rke2/server/db/etcd-old-%date%/. RKE2 will then attempt to restore the snapshot by creating a new data directory and start etcd with a new RKE2 cluster with one etcd member.

1. You must stop RKE2 service on all server nodes if it is enabled via `systemd`. Use the following command to do so:\
   `systemctl stop rke2-server`
2. Initiate the restore from the snapshot on the first server node with the following commands:\
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

**Note:** For all versions of rke2 v.1.20.9 and prior, you will need to back up and restore certificates first due to a known issue in which bootstrap data might not save on restore (Steps 1 - 3 below assume this scenario). See [note](https://docs.rke2.io/backup_restore#other-notes-on-restoring-a-snapshot) below for an additional version-specific restore caveat on restore.

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
