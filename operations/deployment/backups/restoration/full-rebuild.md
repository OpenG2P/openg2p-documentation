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
**After a storage rebuild the live NFS `rancher-backup/` dir only has post-DR tarballs** (often an empty/new-cluster nightly). The orchestrator's `restore --component rancher` picks the **newest Backup CR `status.filename`**, not “the best pre-disaster file on disk.” `--target cluster` means cluster-wide restore; it does **not** select which tarball.
{% endhint %}

### 5a — Put the pre-disaster tarball back on NFS

On the **backup host**, find the on-demand / nightly file inside NFS restic (captured under the export):

```bash
export RESTIC_REPOSITORY=/var/lib/openg2p-backup/restic/nfs
# unlock with restic.pass
restic snapshots --tag nfs --compact
restic find openg2p-ondemand   # or openg2p-nightly / a known date
restic restore <snapshot-id> --target /tmp/rancher-old \
  --include '**/rancher-backup/*.tar.gz.enc'
```

Copy the chosen `*.tar.gz.enc` onto the **new** storage export (same path the static PV uses):

```bash
# ubuntu SSH + sudo — do not scp as root (MOTD breaks scp) or as ubuntu into /srv/nfs directly
scp -i <key> /tmp/rancher-old/.../openg2p-ondemand-….tar.gz.enc ubuntu@<storage>:/tmp/
ssh -i <key> ubuntu@<storage> \
  'sudo cp /tmp/openg2p-ondemand-….tar.gz.enc /srv/nfs/openg2p/rancher-backup/'
```

### 5b — Apply Restore for that filename

If no newer Backup CR exists, the script may pick the file you just copied:

```bash
./openg2p-backup.sh restore \
    --config backup-config.yaml \
    --component rancher \
    --target cluster
```

If a newer nightly already exists (or you must pin a specific file), apply the Restore CR yourself:

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
  ignoreErrors: true   # recommended on full rebuild — see below
EOF
```

The operator handles:
* Recreating Secrets (incl. Helm release secrets — restoring these means `helm list` will show your prior releases again)
* Recreating CRs (Rancher state, cert-manager Issuers + Certificates, Istio configs, Keycloak realms if operator-managed, monitoring rules)
* Recreating PV + PVC objects with their original `claimRef` bindings (NFS paths = **pre-disaster UUIDs**)

Watch progress:
```bash
kubectl --kubeconfig ~/.kube/openg2p-prod get restore.resources.cattle.io -A -w
kubectl --kubeconfig ~/.kube/openg2p-prod -n cattle-resources-system \
  logs -l app.kubernetes.io/name=rancher-backup --tail=100
```

The Restore CR transitions through `Pending` → `Running` → `Done`. Common **full-rebuild** failures:

| Log / status | What to do |
|---|---|
| `PersistentVolume "openg2p-rancher-backup-store" … spec.persistentvolumesource is immutable` (old vs new storage IP) | Keep the **new** PV (`172.29.x` current). Do not let restore rewrite NFS `server`. Use `ignoreErrors: true`, or delete the stuck Restore and re-apply with that flag. Confirm afterward: `kubectl get pv openg2p-rancher-backup-store -o jsonpath='{.spec.nfs.server}{"\n"}'` |
| `users.management.cattle.io` / “username already exists” | Duplicate Rancher user vs fresh install — usually safe to ignore with `ignoreErrors: true`, or delete the conflicting User before re-running |
| Other “already exists” / immutable fields | Inspect the GVK in operator logs; fix or ignore per resource |

{% hint style="info" %}
The orchestrator-generated Restore CR sets `prune: false` only — it does **not** set `ignoreErrors`. On DR, prefer the manual CR above once the pre-disaster tarball is on NFS.
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

Details ( `--tag nfs` vs `pvc-manifest`, empty-restore failure, UUID matching ) are in [single-pvc.md](single-pvc.md). Staging lands on the **backup host** under `/tmp/openg2p-nfs-restore/<ns>-<pvc>-<ts>/<nfs-path>/`.

Copy **the inner UUID directory contents** onto storage at `/srv/nfs/openg2p/<same-uuid>/` — not the outer timestamped wrapper. Prefer the tar pipe (`ubuntu` + `sudo`) from [single-pvc.md Step 4](single-pvc.md#step-4-push-the-data-to-the-live-nfs-export). Match ownership to the app (e.g. Bitnami MinIO needs `chown -R 1001:1001`).

For lots of PVCs, script it. Prefer the sidecar from a **pre-disaster** NFS/pvc-manifest snapshot if the live `.pvc-mapping.yaml` was regenerated against empty new dirs.

**Important**: the *new* NFS UUIDs (those just created by the fresh helmfile install) won't match the *backup* UUIDs. The Restore CR in Step 5 recreated PVs that point at the *original* UUIDs — meaning the new PVs reference NFS paths that don't exist yet (or exist empty). Two options:

* **A — Move the data**. Restore from restic into the path the recreated PV expects. Cleanest. Same UUID in staging and under `/srv/nfs/openg2p/` is expected.
* **B — Edit the recreated PV**. Patch the PV's `spec.nfs.path` to match a new UUID, and either restic-restore into that path or symlink. More fragile.

Plan A is the default. Restore the data, then bounce the consuming workload.

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

```bash
# Restart all pods to pick up restored Secrets/ConfigMaps.
kubectl --kubeconfig ~/.kube/openg2p-prod rollout restart deployment -A

# Give it a few minutes, then check.
kubectl --kubeconfig ~/.kube/openg2p-prod get pods -A | grep -v Running
```

Sanity tests:
* Log into Rancher with original SAML credentials
* Log into Keycloak with admin email
* Check at least one PVC-consuming app's data (e.g. browse Keycloak admin themes, list MinIO buckets)
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
