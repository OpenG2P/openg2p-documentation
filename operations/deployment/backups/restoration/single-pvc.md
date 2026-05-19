---
description: Restore one PersistentVolumeClaim's data from the NFS restic repo and rebind it to the target app.
---

# Single PVC restore

Use this when one application's data is corrupt or accidentally wiped, but the cluster and other apps are fine. Common cases: Keycloak themes overwritten, MinIO bucket data deleted, a CMS upload directory wiped.

## How the mapping works

Each PVC's data lives in a UUID-named directory under the NFS export (e.g. `/srv/nfs/openg2p/pvc-abc123-def456/...`). On its own restic just sees opaque UUIDs. The sidecar manifest at `/var/lib/openg2p-backup/nfs/.pvc-mapping.yaml` joins each UUID against `kubectl get pv` so restore knows which app a UUID belongs to. This file is regenerated every NFS run — always inspect the latest version.

## Step 1 — Find the PVC

```bash
ssh ubuntu@<backup-host> sudo cat /var/lib/openg2p-backup/nfs/.pvc-mapping.yaml | jq '.[] | select(.pvc_namespace == "keycloak")'
```

You'll see entries like:

```yaml
- nfs_path: pvc-abc123-def456
  pv_name: pvc-abc123-def456
  pvc_namespace: keycloak
  pvc_name: keycloak-data
  pvc_size: 20Gi
  storage_class: nfs-csi
  app_label: app=keycloak
  backed_up_at: 2026-04-27T03:30:11Z
```

## Step 2 — Dry-run

```bash
./openg2p-backup.sh restore \
    --config backup-config.yaml \
    --component nfs \
    --target keycloak/keycloak-data \
    --dry-run
```

Confirms the manifest entry and prints the staging path it would use.

## Step 3 — Stage the restore

```bash
./openg2p-backup.sh restore \
    --config backup-config.yaml \
    --component nfs \
    --target keycloak/keycloak-data
```

This:
1. Reads the sidecar manifest, finds the NFS path for that PVC.
2. `restic restore latest --include /<nfs-path>` into `/tmp/openg2p-nfs-restore/<ns>-<pvc>-<timestamp>/` on the **backup host**.
3. Stops there.

## Step 4 — Push the data to the live NFS export

The NFS export is mounted **read-only** on the backup host. To replace the live data, copy from the backup host to the storage node.

### Plan A — replace the whole PVC's contents (most common)

```bash
# Pause the app so it's not writing during the swap.
kubectl --kubeconfig ~/.kube/openg2p-prod scale deploy keycloak -n keycloak --replicas=0

# Find the live NFS path on storage. The export root + UUID:
ssh ubuntu@<storage-host> ls -la /srv/nfs/openg2p/pvc-abc123-def456/

# Backup the current state aside (don't delete!).
ssh ubuntu@<storage-host> sudo mv /srv/nfs/openg2p/pvc-abc123-def456 /srv/nfs/openg2p/pvc-abc123-def456.precrash

# Copy from backup host to storage. Use rsync to preserve perms.
ssh ubuntu@<backup-host> "sudo tar -C /tmp/openg2p-nfs-restore/keycloak-keycloak-data-<ts>/<nfs-path> -czf - ." | \
    ssh ubuntu@<storage-host> "sudo tar -C /srv/nfs/openg2p/pvc-abc123-def456 -xzf -"

ssh ubuntu@<storage-host> sudo chown -R nobody:nogroup /srv/nfs/openg2p/pvc-abc123-def456
# (chown depends on your NFS export's no_root_squash settings — match what the
# original directory had.)

# Bring the app back.
kubectl --kubeconfig ~/.kube/openg2p-prod scale deploy keycloak -n keycloak --replicas=1
```

After verifying the app is healthy, remove the `.precrash` aside.

### Plan B — selective file restore

For when you just need a few files back:

```bash
# Inspect what restic restored.
ssh ubuntu@<backup-host> sudo find /tmp/openg2p-nfs-restore/keycloak-keycloak-data-<ts> -type f

# Copy just the file you need.
ssh ubuntu@<backup-host> "sudo cat /tmp/openg2p-nfs-restore/.../themes/openg2p/login.ftl" | \
    ssh ubuntu@<storage-host> "sudo tee /srv/nfs/openg2p/pvc-abc123-def456/themes/openg2p/login.ftl"
```

## Step 5 — Verify

```bash
kubectl --kubeconfig ~/.kube/openg2p-prod -n keycloak logs deploy/keycloak --tail=50
# Browse the Keycloak admin to confirm restored content is present.
```

## Restoring a deleted PVC (PV/PVC objects gone)

If the PVC itself was deleted (not just the data):

1. Check `.pvc-mapping.yaml` for the PV/PVC names + size + storage class.
2. Restore Kubernetes objects via the rancher-backup `Restore` CR — see [full-rebuild.md](full-rebuild.md). You can target a single namespace with rancher-backup's restore filters.
3. The restored PVC will bind to a freshly-provisioned PV (because the old PV is also gone). The new PV's `nfs.path` won't match the original. Two options:
   * Move the restic-restored data into the new PV's NFS path.
   * Edit the restored PV manifest (before applying) to point at the original NFS path, so it binds to the existing data.

The second is faster but requires manual YAML edits. Operate carefully.

## Common gotchas

* **Permissions** — NFS exports often run with `root_squash`. The restored files may end up as `nobody:nogroup`. Check what the live directory had before the swap and match it.
* **Trailing slashes in `tar -C`** — the path is the *destination* directory. If the live PVC dir has files at the root and a trailing slash mismatches, you can end up with files inside a subdirectory. Always test with `find ... -ls | head` after the copy.
* **Forgetting to scale the app down** — you can corrupt new files mid-restore. Always pause the consuming Deployment/StatefulSet first.
* **The restored data is older** — by definition. Anything written after the last NFS backup snapshot is gone. Check the restored snapshot timestamp in `.pvc-mapping.yaml` (`backed_up_at`).
