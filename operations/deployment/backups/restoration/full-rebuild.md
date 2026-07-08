---
description: Build fresh nodes, run the production install, then layer backups on top — the disaster recovery runbook.
---

# Full rebuild

The disaster scenario: nodes destroyed or unreachable, hardware lost, region-down event. Build fresh and bring everything back from backups.

## Pre-flight checklist

Before you start, gather:
* [ ] Original `aws-config.yaml` and `prod-config.yaml` (or equivalents for non-AWS)
* [ ] `backup-config.yaml` from before the disaster
* [ ] All three keystore passphrases: `restic.pass`, `pgbackrest.pass`, `etcd-aescbc.key` (if encryption-at-rest was enabled)
* [ ] Wireguard admin client `.conf` files (these aren't in backups by design)
* [ ] Any customer-supplied TLS cert + key files (if `tls.method: provided`)
* [ ] Working network access to the backup host's surviving repo

If the backup host itself is also destroyed, recovery isn't possible — backups are gone with it. This is why the [Architecture](../architecture.md) page calls out 3-2-1 as Phase 2 work.

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

## Step 4 — Restore PostgreSQL

The platform install just laid down a clean Postgres on the storage node. You need to replace it with the restored data.

```bash
./openg2p-backup.sh restore \
    --config backup-config.yaml \
    --component pg
    # No --point-in-time = restore latest
```

This stages the restored Postgres data dir at `/var/lib/openg2p-backup-restore/pg-<ts>/` on the storage node. Follow the cutover steps in [Postgres PITR — Step 4](postgres-pitr.md#step-4-cutover-live-pg-replacement) to replace the live PG.

Verify:
```bash
ssh ubuntu@<storage> "sudo -u postgres psql -d postgres -c '\\l'"
```

## Step 5 — Restore Kubernetes resources

The fresh helmfile install recreated the platform's own resources. We now layer the user-state on top via a rancher-backup `Restore` CR.

```bash
./openg2p-backup.sh restore \
    --config backup-config.yaml \
    --component rancher \
    --target cluster
```

This selects the most recent backup tarball on the operator's static NFS volume (`/srv/nfs/<cluster>/rancher-backup`, file pattern `*.tar.gz.enc`) and applies a `Restore` CR. The operator handles:
* Recreating Secrets (incl. Helm release secrets — restoring these means `helm list` will show your prior releases again)
* Recreating CRs (Rancher state, cert-manager Issuers + Certificates, Istio configs, Keycloak realms if operator-managed, monitoring rules)
* Recreating PV + PVC objects with their original `claimRef` bindings

Watch progress:
```bash
kubectl --kubeconfig ~/.kube/openg2p-prod get restore.resources.cattle.io -A -w
```

The Restore CR transitions through `Pending` → `Running` → `Done`. If it errors, the `kubectl describe restore.resources.cattle.io <name>` output points at the offending GVK. Most errors are caused by the cluster being in a state where the resource already exists with different fields — investigate per-resource.

## Step 6 — Restore NFS data

Now the cluster knows about every original PV and PVC, but their NFS-backed data dirs are empty (the new storage node has a fresh NFS export).

For each PVC that needs data:

```bash
./openg2p-backup.sh restore \
    --config backup-config.yaml \
    --component nfs \
    --target <namespace>/<pvc>
```

This restores the data into a staging dir on the **backup host**. Then copy it to the live NFS export on the new storage node — see [single-pvc.md](single-pvc.md#step-4-push-the-data-to-the-live-nfs-export).

For lots of PVCs, script it. The sidecar manifest at `/var/lib/openg2p-backup/nfs/.pvc-mapping.yaml` is your inventory.

**Important**: the *new* NFS UUIDs (those just created by the fresh helmfile install) won't match the *backup* UUIDs. The Restore CR in Step 5 recreated PVs that point at the *original* UUIDs — meaning the new PVs reference NFS paths that don't exist yet. Two options:

* **A — Move the data**. Restore from restic into the path the recreated PV expects. Cleanest.
* **B — Edit the recreated PV**. Patch the PV's `spec.nfs.path` to match a new UUID, and either restic-restore into that path or symlink. More fragile.

Plan A is the default. Restore the data, then bounce the consuming workload.

## Step 7 — Restore platform-level config (optional)

The fresh install regenerated:
* The local CA on the RP node (different cert!)
* Wireguard server keys (different pubkey!)
* RKE2 cluster CA

If you want to keep the **original** identities (so admin laptops' Wireguard configs and trusted CA cert still work), restore the configs group:

```bash
./openg2p-backup.sh restore --component configs --target wireguard
./openg2p-backup.sh restore --component configs --target openg2p   # local CA, dnsmasq
```

Then copy onto the RP node and restart the affected services. This is optional — most operators accept regenerating these and re-distributing to admin laptops.

## Step 8 — Bounce workloads + verify

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

## Step 9 — Re-establish backup automation

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
