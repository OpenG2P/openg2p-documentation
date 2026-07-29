---
description: Restore one PersistentVolumeClaim's data from the NFS restic repo and rebind it to the target app.
---

# Single PVC restore

Use this when one application's data is corrupt or accidentally wiped, but the cluster and other apps are fine. Common cases: Keycloak themes overwritten, MinIO bucket data deleted, a CMS upload directory wiped.

## How the mapping works

Each PVC's data lives in a per-volume subdirectory under the NFS export (e.g. `/srv/nfs/openg2p/<namespace>-<pvc>-<pv-uuid>/` on the `nfs-csi` StorageClass, or a native NFS PV path). On its own restic just sees opaque directory names. The sidecar manifest at `/var/lib/openg2p-backup/nfs/.pvc-mapping.yaml` joins each directory against `kubectl get pv` (including CSI `volumeAttributes.subdir`) so restore knows which app a path belongs to. This file is regenerated every NFS run — always inspect the latest version.

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
2. `restic restore latest --tag nfs --include *<nfs-path>*` into `/tmp/openg2p-nfs-restore/<ns>-<pvc>-<timestamp>/` on the **backup host**. The `--tag nfs` filter is required: each nightly run also writes a separate `pvc-manifest` snapshot (only `.pvc-mapping.yaml`); without the tag, `latest` often selects that empty sidecar and you get a “successful” restore of 0 bytes.
3. Stops there. Fails if the staged directory is empty or the path is missing from the snapshot.

### After a full rebuild (DR)

Post-rebuild NFS cron may have already taken a new (empty) `--tag nfs` snapshot. Pin a **pre-disaster** snapshot:

```bash
./openg2p-backup.sh list --config backup-config.yaml --component nfs
# on backup host:
restic snapshots --tag nfs --compact
restic ls <snapshot-id> | grep commons-services-keymanager

./openg2p-backup.sh restore \
    --config backup-config.yaml \
    --component nfs \
    --target prod/commons-services-keymanager \
    --point-in-time <snapshot-id>
```

Also confirm the sidecar `nfs_path` is the **old** UUID (from the rancher-restored PV), not a new empty dir created by the fresh helmfile install.

## Step 4 — Push the data to the live NFS export

The NFS export is mounted **read-only** on the backup host. To replace the live data, copy from the backup host to the storage node.

### Plan A — replace the whole PVC's contents (most common)

```bash
# Pause the app so it's not writing during the swap.
kubectl --kubeconfig ~/.kube/openg2p-prod scale deploy keycloak -n keycloak --replicas=0

# Find the live NFS path on storage. The export root + UUID:
ssh ubuntu@<storage-host> ls -la /srv/nfs/openg2p/pvc-abc123-def456/

# Create the destination if it does not exist yet (tar -C fails otherwise).
ssh ubuntu@<storage-host> sudo mkdir -p /srv/nfs/openg2p/pvc-abc123-def456

# Backup the current state aside (don't delete!).
ssh ubuntu@<storage-host> sudo mv /srv/nfs/openg2p/pvc-abc123-def456 /srv/nfs/openg2p/pvc-abc123-def456.precrash
ssh ubuntu@<storage-host> sudo mkdir -p /srv/nfs/openg2p/pvc-abc123-def456

# Copy from backup host to storage. Use tar over SSH (ubuntu + sudo; not root@ scp).
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
2. Restore Kubernetes objects via a rancher-backup `Restore` CR — see [full-rebuild.md](full-rebuild.md). The orchestrator always restores cluster-wide (`--target cluster` does not filter by namespace). For a single namespace, apply a manual `Restore` CR with rancher-backup's restore filters.
3. The restored PVC will bind to a freshly-provisioned PV (because the old PV is also gone). The new PV's `nfs.path` won't match the original. Two options:
   * Move the restic-restored data into the new PV's NFS path.
   * Edit the restored PV manifest (before applying) to point at the original NFS path, so it binds to the existing data.

The second is faster but requires manual YAML edits. Operate carefully.

## Common gotchas

* **Permissions** — NFS exports often run with `root_squash`. Restored files may show up as `nobody:nogroup` (or `nobody:1001`). Match what the workload expects: Bitnami MinIO needs `chown -R 1001:1001` on the PVC dir or the pod fails with `Permission denied` on `.root_user`.
* **Bound UUID ≠ restored UUID after full rebuild** — helmfile creates new `nfs-csi` PVs; restic restores old UUID dirs. Put restored data under the **Bound** PV’s `subDir` (see `kubectl get pv … volumeAttributes.subDir`). Leaving data only under the old UUID leaves pods empty/failing.
* **CSI volume source is immutable** — you cannot `kubectl patch pv` to change `spec.csi.volumeAttributes.server` / `subDir`, and you cannot add `spec.nfs` onto a CSI PV. Recreate the PV or (preferred) copy data into the Bound path.
* **`mv` into a non-empty directory** — `mv chunks dest/chunks` fails with `Directory not empty`. `mv` has no `-r`. Replace the whole Bound directory, or `rm -rf dest/*` then `rsync -a src/ dest/`.
* **Destination must exist before `tar -C`** — create with `mkdir -p` on storage or extract fails with `Cannot open: No such file or directory`.
* **Same UUID on live NFS and in staging** — after rancher restore of native NFS PVs, staging nests data under `/tmp/openg2p-nfs-restore/<ns>-<pvc>-<ts>/<nfs-path>/`. Copy/move that **inner** directory, not the outer timestamped folder.
* **Trailing slashes in `tar -C`** — the path is the *destination* directory. Always verify with `du -sh` / `ls` after the copy.
* **Forgetting to scale the app down** — you can corrupt new files mid-restore. Always pause the consuming Deployment/StatefulSet first.
* **The restored data is older** — by definition. Anything written after the last NFS backup snapshot is gone. Check the restored snapshot timestamp in `.pvc-mapping.yaml` (`backed_up_at`).
* **Keycloak / Superset still CrashLoop after PG cutover** — on a storage rebuild they often still point at the **old** Postgres private IP in ConfigMaps/Secrets. Update those to the new storage IP, then restart — see [full-rebuild.md Step 9](full-rebuild.md#step-9-bounce-workloads--verify).
