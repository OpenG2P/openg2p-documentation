---
description: Restore etcd in-place on the existing compute node from an RKE2 snapshot. Use when the control plane is broken but the compute node is reusable.
---

# Etcd in-place restore

This is a **cluster reset operation**. It rolls back the entire Kubernetes control plane to the moment of the chosen snapshot. Helm releases, runtime-issued certs, user-created CRs that landed after the snapshot are gone. Plan a maintenance window.

Use this when:
* The compute node's disk is intact and the OS boots, but
* Etcd is corrupted, OR
* The control plane is in a bad state you can't recover (failed upgrade, accidental `kubectl delete` of critical resources).

If the compute node is destroyed or unreachable, use [Full rebuild](full-rebuild.md) instead.

## Pre-flight

* Have the backup host reachable from your laptop.
* Have the `restic.pass` passphrase from your keystore (needed if you have to also restore the `cred/` and `tls/` dirs).
* Pick the target snapshot. List with `./openg2p-backup.sh list --component etcd`. The most recent valid snapshot is usually correct.
* Decide if you also need to restore RKE2 filesystem state. See "When also restore the FS state" below.

## Step 1 — Stage the snapshot on the compute node

```bash
./openg2p-backup.sh restore \
    --config backup-config.yaml \
    --component etcd \
    --target latest
```

This `scp`s the chosen snapshot to `/tmp/openg2p-etcd-restore/` on the compute node. It does **not** apply it. The orchestrator prints the next commands to run.

For a specific snapshot file:

```bash
./openg2p-backup.sh restore --component etcd --target etcd-snapshot-compute-1-1714000000.zip
```

## Step 2 — When also restore the FS state

Skip if: you're rolling back to a snapshot taken *after* the most recent change to `/var/lib/rancher/rke2/server/tls/` and `cred/`. The directories rarely change; usually only on initial install and on encryption-at-rest enable.

If the FS state on the compute node is intact and matches the era of the snapshot, **skip this step** and go to Step 3. The cluster CA in `tls/` is what signed all the certs etcd refers to.

If the FS state is broken (compute node had a partial wipe, or you're not sure it matches), restore from the configs repo:

```bash
./openg2p-backup.sh restore --component configs --target rke2-tls
./openg2p-backup.sh restore --component configs --target rke2-cred
./openg2p-backup.sh restore --component configs --target rke2-token
```

Each lands in `/tmp/openg2p-configs-restore/<tag>-<ts>/extracted/` on the **backup host**. Copy them onto the compute node:

```bash
ssh ubuntu@<backup-host> sudo tar -C /tmp/openg2p-configs-restore/rke2-tls-<ts>/extracted -czf - . | \
    ssh ubuntu@<compute-host> "sudo tar -C /var/lib/rancher/rke2/server/tls -xzf -"

# Same for cred/ and (if restored) the token files.
```

## Step 3 — Cluster reset and restore

On the **compute node** (under sudo):

```bash
# Stop RKE2.
sudo systemctl stop rke2-server

# Cluster reset with the snapshot path.
sudo rke2 server \
    --cluster-reset \
    --cluster-reset-restore-path=/tmp/openg2p-etcd-restore/<filename>

# When the reset completes (you'll see "etcd cluster has been reset" on stderr),
# Ctrl+C, then start the service normally.
sudo systemctl start rke2-server
```

`--cluster-reset` is a one-shot operation — it doesn't run the server, it just resets etcd and exits. After that, normal `systemctl start rke2-server` brings the cluster back.

## Step 4 — Verify

```bash
# Wait for the API to come back.
export KUBECONFIG=/etc/rancher/rke2/rke2.yaml
sudo kubectl get nodes
sudo kubectl get ns
sudo kubectl -n cattle-system get pods   # Rancher should be coming up

# From your laptop:
kubectl --kubeconfig ~/.kube/openg2p-prod get nodes
```

The cluster will look exactly as it did at the moment of the snapshot. Workloads pinned to NodePort/Ingress will reconnect; pods that depend on resources created post-snapshot won't find them.

## Step 5 — Reconcile

After the restore:
* **Postgres**: not touched (lives on storage, not compute). Still in whatever state it was when you started the restore.
* **NFS data**: not touched. Apps' on-disk state is from the present, but the cluster's view of them is from the snapshot. PVCs created post-snapshot won't exist; their data still on NFS will look like orphans. Reconcile by either (a) recreating the PVC and pointing it at the existing NFS UUID dir, or (b) accepting the data loss.
* **Resources created post-snapshot** (Helm releases of new apps, user-added secrets, custom CRs) are gone. Re-run helmfile if appropriate, or restore via [full-rebuild.md](full-rebuild.md)'s rancher-backup step targeted at specific namespaces.

## When this won't work

* Snapshot is corrupted — `etcd_verify` would have caught this. Pick an older snapshot.
* Snapshot was taken on a different RKE2 minor version than what's running now. Match versions before restoring.
* Compute node IP / hostname has changed since the snapshot. Etcd has node identity baked in. You'll need to fully rebuild instead.

## Upstream reference

* [RKE2 — Restoring a snapshot to existing nodes](https://docs.rke2.io/backup_restore#restoring-a-snapshot-to-existing-nodes)
* [RKE2 — Cluster reset](https://docs.rke2.io/backup_restore#cluster-reset)
