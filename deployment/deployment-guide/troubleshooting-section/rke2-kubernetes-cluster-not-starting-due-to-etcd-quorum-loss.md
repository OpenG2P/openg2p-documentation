# RKE2 Kubernetes Cluster not Starting due to ETCD Quorum Loss

This guide explains how to resolve RKE2 Server quorum related issues. When you have multiple RKE2 Server nodes (for HA of K8s cluster), and in case one of the server nodes doesn't start or fails because of issues with ETCD quorum, this guide can help.

RKE2 provides a feature to reset the cluster to a single-member cluster using the `--cluster-reset` flag. When this flag is passed to the RKE2 server, it resets the cluster while preserving the existing data directory. The etcd data directory is located at `/var/lib/rancher/rke2/server/db/etcd`. This flag can be used in the event of quorum loss in the cluster.

To use the reset flag, you must first stop the RKE2 service if it is enabled via systemd:

```bash
# Stop the RKE2 server service
systemctl stop rke2-server

# Perform a cluster reset
rke2 server --cluster-reset

```

A message in the logs states that RKE2 can be restarted without the flags. Start RKE2 again, and it should initialize as a single-member cluster.
