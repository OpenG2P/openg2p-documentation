---
description: Build fresh nodes, run the production install, then layer backups on top — the disaster recovery runbook.
---

# Full rebuild

The disaster scenario: nodes destroyed or unreachable, hardware lost, region-down event. Build fresh and bring everything back from backups.

## Pre-flight checklist

Before you start, gather:
* [ ] Original `aws-config.yaml` and `prod-config.yaml` (or equivalents for non-AWS)
* [ ] `backup-config.yaml` from before the disaster
* [ ] All keystore passphrases: `restic.pass`, `pgbackrest.pass`, `etcd-aescbc.key` (if encryption-at-rest was enabled); plus `objectstore-restic.pass` / `rclone.conf` if `groups.objectstore` was enabled
* [ ] Wireguard admin client `.conf` files (these aren't in backups by design)
* [ ] Any customer-supplied TLS cert + key files (if `tls.method: provided`)
* [ ] Working network access to the backup host's surviving repo

If the backup host itself is also destroyed, recovery isn't possible — backups are gone with it. Offsite / 3-2-1 replication is still an operator plan (see [Backups — what this does not do](../README.md#what-this-does-not-do)); protect the backup volume accordingly.

## Step 1 — Provision fresh nodes

```bash
cd automation/production/aws/
# Edit aws-config.yaml as needed (project, region, instance types).
# Set backup_node.enabled: true if you want backups again.
./openg2p-aws-provision.sh --config aws-config.yaml
```

This creates 3 (or 4) new instances with new IPs. The `provision-output.yaml` is regenerated with the new addresses.

If your backup host survived, **do not provision a new backup node** — keep using the existing one. Manually update `backup-config.yaml` to point at it (skip the `backup_node.enabled: true` flag in aws-config).

## Step 2 — Install the platform

```bash
cd ../
./openg2p-prod.sh --config prod-config.yaml --probe
./openg2p-prod.sh --config prod-config.yaml --preflight
./openg2p-prod.sh --config prod-config.yaml
```

This runs the full production automation. Result: a clean OpenG2P install with no customer data, default Rancher/Keycloak/etc.

Verify:
```bash
kubectl --kubeconfig ~/.kube/openg2p-prod get nodes
kubectl --kubeconfig ~/.kube/openg2p-prod get ns
```

## Step 3 — Make backup tooling available

If you provisioned a new backup node:
```bash
cd ../backups/
# Edit backup-config.yaml to reference the new prod-config.yaml.
# Make sure backup_private_ip points at the new backup node.
./openg2p-backup.sh install --config backup-config.yaml
```

If your backup host survived: re-run `install` so the backup host learns the new IPs/SSH keys of the freshly-provisioned production nodes:
```bash
./openg2p-backup.sh install --config backup-config.yaml --force
```

{% hint style="info" %}
**Kept the backup node with old repos?** The fresh platform install created a **new empty Postgres** whose system-id does not match the surviving pgBackRest stanza. `install` may log pgBackRest error `[028]` ("backup and archive info files exist but do not match the database") and then **skip the first full backup** on purpose — do **not** delete or re-init `/var/lib/openg2p-backup/pg`; you need those files for Step 4 restore. Tooling and SSH trust are still installed. After you restore + cutover PG, run `./openg2p-backup.sh run --component pg` to take a new full of the restored database.

**NFS mount I/O error on `/mnt/openg2p-nfs-ro`?** The backup host may still have a stale mount (and, on older installs, a systemd automount) to the **old** storage private IP. Re-run `install --force` with current scripts: they stop any leftover automount/mount units, force-unmount via `/proc/mounts`, rewrite `/etc/fstab` **without** `x-systemd.automount` (`ro,soft,timeo=30,retrans=2,noauto,_netdev`), remount, and fall back to `/mnt/openg2p-nfs-ro-dr` (marker: `/var/lib/openg2p-backup/.nfs-mount-point`) if the canonical path stays poisoned. Manual clear on the backup host if needed:

```bash
sudo systemctl stop mnt-openg2p\\x2dnfs\\x2dro.automount mnt-openg2p\\x2dnfs\\x2dro.mount 2>/dev/null || true
sudo umount -f -l /mnt/openg2p-nfs-ro /mnt/openg2p-nfs-ro-dr 2>/dev/null || true
sudo rm -f /var/lib/openg2p-backup/.nfs-mount-point
```
{% endhint %}

If `install` still hard-fails on an older script build before that skip existed, finish tooling without touching the PG repo:
```bash
# Temporarily disable pg for this install pass, then re-enable for restore/run.
# Or pull the latest lib/pgbackrest.sh and re-run install --force.
./openg2p-backup.sh install --config backup-config.yaml --force --component etcd
# …or set groups.pg: false once, install, set true again before restore.
```

## Step 4 — Restore PostgreSQL

The platform install just laid down a clean Postgres on the storage node. You need to replace it with the restored data.

```bash
./openg2p-backup.sh restore \
    --config backup-config.yaml \
    --component pg
    # No --point-in-time → script uses pgBackRest --type=immediate
```

This stages the restored Postgres data dir at `/var/lib/openg2p-backup-restore/pg-<ts>/` on the storage node. Follow the cutover steps in [Postgres PITR — Step 4](postgres-pitr.md#step-4-cutover-live-pg-replacement) to replace the live PG.

Verify:
```bash
ssh ubuntu@<storage> "sudo -u postgres psql -d postgres -c '\\l'"
```

## Step 5 — Restore Kubernetes resources

The fresh helmfile install recreated the platform's own resources. We now layer the user-state on top via a rancher-backup `Restore` CR.

{% hint style="warning" %}
**Kept the backup node but rebuilt storage/compute?** The **new** NFS export is empty. Pre-disaster rancher tarballs are **not** on the new storage node — they live in the **NFS restic repo on the backup host** (`/var/lib/openg2p-backup/restic/nfs`). Do **not** run `./openg2p-backup.sh restore --component rancher` first: it picks the newest `Backup` CR filename, which points at a **post-rebuild** tarball on the empty new NFS (or fails). For DR, always: **(1) fix NFS IPs → (2) copy tarball from backup host → (3) manual `Restore` CR**.
{% endhint %}

### 5a — Note the new storage NFS IP

After reprovision, the storage private IP changed. You need it for every NFS PV and for copying the tarball.

```bash
# From your laptop — new IP is in provision-output.yaml
grep storage_private_ip automation/production/provision-output.yaml

# Or from the cluster StorageClass (what install used for the static rancher-backup PV)
kubectl --kubeconfig ~/.kube/openg2p-prod get sc nfs-csi -o jsonpath='{.parameters.server}{"\n"}'
```

Write down:

| Item | Example |
|------|---------|
| **New** storage private IP | `172.29.7.49` |
| **Old** storage private IP (pre-disaster) | `172.29.0.104` (from your old notes / restored PV YAML) |
| Rancher tarball path on NFS | `/srv/nfs/openg2p/rancher-backup/` |

The pre-disaster rancher **backup tarball** and the **PV objects inside it** still reference the **old** NFS server IP. The new cluster's live PVs must use the **new** IP before and after restore.

### 5b — Point the rancher-backup store PV at the new NFS IP

`install` creates static PV `openg2p-rancher-backup-store` with the **current** storage IP.

Confirm it before you restore:
- If `server` already equals the **new** storage private IP, you can **skip the patch** in this step.
- Even if it’s correct, the restore tarball still contains old PV definitions; on full rebuilds the restore operator may hit immutable-field conflicts. That's why Step 5e uses `ignoreErrors: true`.

```bash
kubectl --kubeconfig ~/.kube/openg2p-prod get pv openg2p-rancher-backup-store \
  -o jsonpath='server={.spec.nfs.server} path={.spec.nfs.path}{"\n"}'
```

If `server` is wrong, patch it to the **new** storage IP (only safe when the PV is not bound to a running operator pod, or delete/recreate per your runbook):

```bash
NEW_STORAGE_IP=172.29.7.49   # your new private IP

kubectl --kubeconfig ~/.kube/openg2p-prod patch pv openg2p-rancher-backup-store --type=merge -p "
spec:
  nfs:
    server: ${NEW_STORAGE_IP}
    path: /srv/nfs/openg2p/rancher-backup
"
```

If patch fails with **immutable**, delete any stuck `Restore` CR, keep the PV with the new IP, and use `ignoreErrors: true` on the Restore (Step 5d) so restore does not try to replace this PV.

### 5c — Extract the pre-disaster tarball from the **backup host** (not new NFS)

On the **backup host** (`backup_private_ip` in config), the nightly NFS restic job captured the whole export, including `rancher-backup/*.tar.gz.enc` from the **old** cluster.

```bash
ssh ubuntu@<backup-host>

export RESTIC_REPOSITORY=/var/lib/openg2p-backup/restic/nfs
export RESTIC_PASSWORD_FILE=/etc/openg2p-backup/restic.pass

# List data snapshots (not pvc-manifest-only)
sudo -E restic snapshots --tag nfs --compact

# Find your pre-disaster rancher file (adjust date / name)
sudo -E restic ls <snapshot-id> --tag nfs | grep -i rancher-backup
# or:
sudo -E restic find openg2p-ondemand
sudo -E restic find openg2p-nightly

# Restore only the tarball(s) you need into a temp dir
SNAP=<pre-disaster-snapshot-id>
sudo -E restic restore "$SNAP" --tag nfs --target /tmp/rancher-old \
  --include '**/rancher-backup/*.tar.gz.enc'

sudo find /tmp/rancher-old -name '*.tar.gz.enc' -ls
# Note the exact basename, e.g. openg2p-ondemand-20260721….tar.gz.enc
```

This is the **only** source for the old rancher backup when the new storage NFS is empty.

### 5d — Copy the tarball onto the **new** storage NFS

The operator reads tarballs from `/srv/nfs/openg2p/rancher-backup/` on the **new** storage node (same path the static PV uses).

```bash
# From backup host — stream to new storage (ubuntu + sudo; do not scp as root)
TARBALL=/tmp/rancher-old/.../openg2p-ondemand-<exact>.tar.gz.enc
NEW_STORAGE=ubuntu@<new-storage-ip>

sudo tar -C "$(dirname "$TARBALL")" -czf - "$(basename "$TARBALL")" | \
  ssh -i <key> "$NEW_STORAGE" 'sudo tar -C /srv/nfs/openg2p/rancher-backup -xzf -'

ssh -i <key> "$NEW_STORAGE" 'sudo ls -lh /srv/nfs/openg2p/rancher-backup/'
```

### 5e — Apply `Restore` for that exact file (manual CR)

Use the **basename** you copied. Set `ignoreErrors: true` on full rebuild (duplicate Users, immutable PVs, etc.).

```bash
kubectl --kubeconfig ~/.kube/openg2p-prod apply -f - <<EOF
apiVersion: resources.cattle.io/v1
kind: Restore
metadata:
  name: openg2p-restore-from-ondemand
spec:
  backupFilename: openg2p-ondemand-<exact-basename>.tar.gz.enc
  encryptionConfigSecretName: openg2p-backup-encryption
  prune: false
  ignoreErrors: true
EOF
```

Do **not** rely on `./openg2p-backup.sh restore --component rancher` for DR — it does not select a pre-disaster file from restic and may pick a new-cluster nightly instead.

Watch progress:

```bash
kubectl --kubeconfig ~/.kube/openg2p-prod get restore.resources.cattle.io -A -w
kubectl --kubeconfig ~/.kube/openg2p-prod -n cattle-resources-system \
  logs -l app.kubernetes.io/name=rancher-backup --tail=100
```

The operator recreates Secrets, CRs, and PV/PVC objects from the tarball. Those PVs still carry the **old** NFS `server` IP inside the backup.

### 5f — Fix NFS server IP on restored PVs (old IP → new IP)

After restore, some **native NFS** PVs may still point at the dead storage IP. Patch those if `spec.nfs` is present:

```bash
OLD_IP=172.29.0.104    # pre-disaster storage private IP
NEW_IP=172.29.7.49     # new storage private IP from Step 5a

kubectl --kubeconfig ~/.kube/openg2p-prod get pv -o json \
  | jq -r --arg old "$OLD_IP" '.items[] | select(.spec.nfs.server==$old) | .metadata.name'

# Patch each (or script). Example for one PV:
kubectl --kubeconfig ~/.kube/openg2p-prod patch pv <pv-name> --type=merge -p "
spec:
  nfs:
    server: ${NEW_IP}
"
```

**`nfs-csi` PVs cannot be patched** this way (`spec.csi` / volume source is immutable). For CSI volumes, leave the Bound PV alone and put restored data under its `subDir` on the new NFS (Step 6). Delete unused **Released** PVs after cutover.

If a native NFS patch fails with **immutable**, delete the conflicting empty PV/PVC from the fresh install and re-apply restore with `ignoreErrors: true`, or recreate the PV. **Do not** change `openg2p-rancher-backup-store` back to the old IP — keep it on the new storage IP.

Confirm rancher-backup store still correct:

```bash
kubectl --kubeconfig ~/.kube/openg2p-prod get pv openg2p-rancher-backup-store \
  -o jsonpath='{.spec.nfs.server}{"\n"}'
# must print the NEW storage IP
```

### Common Step 5 failures

| Log / status | What to do |
|---|---|
| Restore used wrong / empty tarball | You skipped 5c–5d — tarball must come from **backup host restic**, not new NFS |
| `openg2p-rancher-backup-store` … `spec.nfs` is immutable (old vs new IP) | Keep PV on **new** IP (5b); use `ignoreErrors: true` (5e) |
| `users.management.cattle.io` / username already exists | Safe to ignore with `ignoreErrors: true` |
| App PVCs Pending / wrong NFS | Native NFS: patch `spec.nfs.server` (5f). CSI: put data under Bound `subDir` (Step 6); do not patch CSI attributes |

{% hint style="info" %}
The orchestrator-generated Restore CR sets `prune: false` only — no `ignoreErrors`, and no restic tarball pick. On DR, use the manual flow above.
{% endhint %}

## Step 6 — Restore NFS data

Now the cluster knows about every original PV and PVC, but their NFS-backed data dirs are empty (or newly created empty UUID dirs) on the new storage node.

For each PVC that needs data:

```bash
./openg2p-backup.sh restore \
    --config backup-config.yaml \
    --component nfs \
    --target <namespace>/<pvc>
# After DR, pin a pre-disaster snapshot if latest --tag nfs is empty:
#   --point-in-time <restic-snapshot-id>
```

Details (`--tag nfs` vs `pvc-manifest`, empty-restore failure, UUID matching) are in [single-pvc.md](single-pvc.md). Staging lands on the **backup host** under `/tmp/openg2p-nfs-restore/<ns>-<pvc>-<ts>/<nfs-path>/`.

### Where to put the data on the new NFS (`nfs-csi`)

After a full rebuild you usually have **two** UUID trees:

| Tree | Origin | What uses it |
|------|--------|--------------|
| **Bound** PV `subDir` (new UUID from helmfile) | Fresh install | Running pods |
| **Restored** dir (old UUID from restic / rancher tarball) | Pre-disaster backup | Nothing, until you copy into the Bound path |

Pods follow the **Bound** PV. Putting restored bytes only under the old UUID leaves the app on an empty new path.

```bash
# See the path each Bound PVC actually mounts
kubectl --kubeconfig ~/.kube/openg2p-prod get pv -o json | jq -r '
  .items[]
  | select(.status.phase=="Bound" and .spec.csi!=null)
  | "\(.spec.claimRef.namespace)/\(.spec.claimRef.name) -> \(.spec.csi.volumeAttributes.subDir)"
'
```

**Recommended:** scale the app down, then put restored contents into the Bound `subDir` name (replace the whole directory, or `rsync -a` after clearing the empty new tree). Do **not** use `mv chunks …/chunks/` into a non-empty destination — `mv` will not merge (`Directory not empty`), and `mv` has no `-r`.

```bash
# Example on storage — replace Bound path with restored tree
NEW=observability-loki-minio-pvc-<bound-uuid>
OLD=observability-loki-minio-pvc-<restored-uuid>   # or under old/

mv "$NEW" "${NEW}.precrash"
mv "$OLD" "$NEW"
chown -R 1001:1001 "$NEW"   # Bitnami MinIO; match the app otherwise
```

Copy from backup host with the tar pipe (`ubuntu` + `sudo`) from [single-pvc.md Step 4](single-pvc.md#step-4-push-the-data-to-the-live-nfs-export). **Create the destination directory first** (`sudo mkdir -p …`) or tar fails with `Cannot open: No such file or directory`.

{% hint style="warning" %}
**CSI PVs cannot be patched** to change `server` / `subDir` (`spec.persistentvolumesource` is immutable). Native `spec.nfs` patches also often fail. Prefer putting data under the Bound path. Delete leftover **Released** PVs after cutover if they are unused.
{% endhint %}

For lots of PVCs, script the mapping. Prefer a **pre-disaster** sidecar / restic snapshot if the live `.pvc-mapping.yaml` was regenerated against empty new dirs.

## Step 7 — Object store (opt-in)

Only if `groups.objectstore` was enabled before the disaster and the backup host (or its `objectstore-restic` repo) survived:

```bash
./openg2p-backup.sh restore --config backup-config.yaml --component objectstore
# Stages under /var/lib/openg2p-backup/restore/objectstore on the backup host.
```

Then sync the restored tree into the new MinIO/S3 (see [Restoration index — Object store](README.md#object-store-restore-opt-in)). PVC-backed bucket data under NFS is already covered by Step 6.

## Step 8 — Restore platform-level config (optional)

The fresh install regenerated:
* The local CA on the RP node (different cert!)
* Wireguard server keys (different pubkey!)
* RKE2 cluster CA

If you want to keep the **original** identities (so admin laptops' Wireguard configs and trusted CA cert still work), restore the configs group:

```bash
./openg2p-backup.sh restore --config backup-config.yaml --component configs --target wireguard
./openg2p-backup.sh restore --config backup-config.yaml --component configs --target openg2p   # local CA, dnsmasq
```

Each command stages on the **backup host** at `/tmp/openg2p-configs-restore/<tag>-<ts>/` and extracts the tarball to `extracted/` when present. Copy onto the RP node and restart:

```bash
# Example — Wireguard (adjust <ts> from the restore log)
ssh ubuntu@<backup-host> sudo tar -C /tmp/openg2p-configs-restore/wireguard-<ts>/extracted -czf - . | \
  ssh ubuntu@<rp-host> "sudo tar -C /etc/wireguard -xzf -"
ssh ubuntu@<rp-host> "sudo systemctl restart wg-quick@wg0"   # unit name may vary

# Local CA / dnsmasq tree
ssh ubuntu@<backup-host> sudo tar -C /tmp/openg2p-configs-restore/openg2p-<ts>/extracted -czf - . | \
  ssh ubuntu@<rp-host> "sudo tar -C /etc/openg2p -xzf -"
# restart dnsmasq / nginx as needed for your install
```

This is optional — most operators accept regenerating these and re-distributing Wireguard client configs to admin laptops.

## Step 9 — Bounce workloads + verify

### Update Postgres host for Keycloak and Superset (new storage IP)

The new storage node has a **new private IP**. Postgres now listens there, but rancher-restored (or previously rendered) app config may still embed the **old** storage IP.

**Keycloak** and **Superset** commonly keep failing until you point them at the new Postgres address:

1. Find the new storage private IP (`provision-output.yaml` / `storage_private_ip`, or the live Postgres host you cut over to).
2. Search ConfigMaps and Secrets for the old IP / old JDBC/DSN host.
3. Update Keycloak and Superset DB connection settings (ConfigMaps and Secrets — Superset often stores the SQLAlchemy URI in a Secret).
4. Restart those workloads and confirm they reach Postgres.

```bash
NEW_PG_IP=172.29.7.49   # your new storage private IP
OLD_PG_IP=172.29.0.104  # pre-disaster storage private IP

kubectl --kubeconfig ~/.kube/openg2p-prod get cm,secret -A -o yaml \
  | grep -nE "${OLD_PG_IP}|jdbc:postgresql|DATABASE_HOST|SQLALCHEMY" || true

# Edit the Keycloak / Superset ConfigMaps and Secrets that still reference OLD_PG_IP,
# then restart those deployments/statefulsets.
```

Until those values use the new IP, Keycloak and Superset will keep connecting to the dead address and stay CrashLooping / Not Ready.

### Restart and sanity-check

```bash
# Restart all pods to pick up restored Secrets/ConfigMaps (and the Postgres IP edits above).
kubectl --kubeconfig ~/.kube/openg2p-prod rollout restart deployment -A

# Give it a few minutes, then check.
kubectl --kubeconfig ~/.kube/openg2p-prod get pods -A | grep -v Running
```

Sanity tests:
* Log into Rancher with original SAML credentials
* Log into Keycloak with admin email (fails if still on old Postgres IP)
* Open Superset (same — confirm DB host is the new storage IP)
* Check at least one PVC-consuming app's data (e.g. MinIO buckets / Loki after NFS cutover)
* Confirm a known-recent-but-pre-disaster Postgres row exists

## Step 10 — Re-establish backup automation

```bash
./openg2p-backup.sh run --config backup-config.yaml --component all
./openg2p-backup.sh status --config backup-config.yaml
```

This produces the **first new backup of the rebuilt cluster**. From this point forward, restoring this cluster again uses these new backups (older ones still recoverable but tied to the old cluster identity).

## What you've lost

* Anything written to PG between the last backup and the disaster
* Anything written to NFS between the last NFS backup (nightly) and the disaster — up to 24h
* Cluster-internal Prometheus history (not in scope for this automation)
* In-flight requests at the moment of the disaster

## How long this takes

Empirically, on AWS with t3a.xlarge backup + the standard production sizing:
* AWS provisioning: ~5 min
* Production install: 18–25 min
* Backup install: ~5 min
* PG restore + cutover: 5–15 min depending on dataset size
* Rancher Restore CR: 5–10 min
* NFS restore (per PVC): 1–10 min depending on size
* End-to-end for a moderate-sized installation: **45–90 minutes**

Validate this number quarterly via the [Drills — Quarterly DR rehearsal](../drills.md#quarterly-full-dr-rehearsal) procedure. Real numbers from your environment beat estimated ones.
