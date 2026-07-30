---
description: >-
  Index of restoration scenarios — pick one based on what failed and what you're
  trying to bring back.
---

# Restoration

There are four common restore scenarios (plus an opt-in object-store path). Pick one:

| Scenario          | When to use                                                                                                                                               | Page                                             |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| **Postgres PITR** | A bad migration, accidental DROP TABLE, or DELETE without WHERE. You want to roll back the database to a specific moment.                                 | [postgres-pitr.md](postgres-pitr.md)             |
| **Single PVC**    | One application's data is corrupt or accidentally wiped, but the cluster and other apps are fine. Common case: Keycloak realm exports, PVC-backed MinIO. | [single-pvc.md](single-pvc.md)                   |
| **Etcd in-place** | The cluster's control plane is broken (etcd corrupted, master crashed without redundancy) but the compute node and its disk are reusable.                 | [etcd-in-place.md](etcd-in-place.md)             |
| **Full rebuild**  | Disaster — node(s) destroyed, hardware lost. Build fresh and layer backups onto it.                                                                       | [full-rebuild.md](full-rebuild.md)               |
| **Object store**  | MinIO/S3 content was backed up with `groups.objectstore: true` (rclone + restic). Restore the bucket tree onto the backup host, then copy into MinIO.   | [Object store restore](#object-store-restore-opt-in) |

{% hint style="info" %}
PVC-backed object data under the NFS export is restored via [single-pvc.md](single-pvc.md) / NFS restic. The **objectstore** group is only for S3-API bucket contents snapshotted onto the backup host.
{% endhint %}

## General principles

**Where restore lands depends on the component:**
* **nfs / rancher / configs (RP tags)** — orchestrator places data on the live target (new storage NFS or RP).
* **etcd** — snapshot is copied onto compute; cluster-reset remains a manual maintenance step.
* **pg** — staged on storage; cutover follows the postgres runbook.
* **objectstore** — staged on the **backup host** only (no push into MinIO).

**Use `--dry-run` first.** Every restore subcommand supports `--dry-run`, which prints what would happen without doing it.

**Keep the keystore handy.** Every restore needs the same passphrases used at backup time. Losing the passphrase = losing the backup. If objectstore was enabled, also keep `rclone.conf` / `objectstore-restic.pass` (or `/etc/openg2p-backup/restic-objectstore.env` on the backup host).

**Don't run two restores in parallel.** Especially across components — the relationships between PG, NFS data, and PV/PVC bindings matter. Restore PG → restore NFS → reconcile PV/PVCs → restart pods.

**One `--component` per invoke.** `restore` requires a single group (`pg`, `etcd`, `rancher`, `nfs`, `configs`, or `objectstore`). There is no `restore --component all`.

## Choosing a restore order

For a partial loss (one app):

1. Restore that app's PVC ([single-pvc.md](single-pvc.md))
2. Restart the app's pods

For a full rebuild:

1. Provision fresh nodes + run `openg2p-prod.sh install` to get the platform back
2. Restore Postgres ([postgres-pitr.md](postgres-pitr.md) — omit `--point-in-time` for latest; the script uses pgBackRest `--type=immediate`)
3. Restore Kubernetes resources ([full-rebuild.md](full-rebuild.md) Step 5 — `restore --component rancher --point-in-time <cutoff>` pulls tarball from backup-host restic onto new NFS)
4. Restore NFS PVC data ([single-pvc.md](single-pvc.md); `restore --component nfs` pushes onto each **Bound** PV `subDir`; pin `--point-in-time <snapshot-id>` if needed)
5. If `groups.objectstore` was enabled, restore object-store snapshots onto the **backup host** ([below](#object-store-restore-opt-in)), then sync into MinIO yourself
6. Optionally restore RP configs (`wireguard` / `nginx` / `openg2p`) — they push onto the RP node
7. Restart workloads, verify
   * After a storage rebuild, update **Keycloak** and **Superset** ConfigMaps/Secrets to the **new** Postgres private IP ([full-rebuild.md Step 9](full-rebuild.md#step-9-bounce-workloads--verify)).

For control-plane recovery without rebuilding:

1. [etcd-in-place.md](etcd-in-place.md) — restore the snapshot, restart RKE2 with `--cluster-reset`

## Object store restore (opt-in)

Only when MinIO/S3 was backed up with `groups.objectstore: true`. Stages a restic restore onto the **backup host** (does not push into live MinIO for you):

```bash
# List snapshots
./openg2p-backup.sh list --config backup-config.yaml --component objectstore

# Restore latest (or pass a snapshot ID as --target)
./openg2p-backup.sh restore --config backup-config.yaml --component objectstore
# Default destination: /var/lib/openg2p-backup/restore/objectstore
```

Then copy/sync the restored tree into the live bucket (MinIO console, `mc mirror`, or `rclone sync`) during a maintenance window. Treat this like NFS restore: verify content before cutting over.

## Things that are not restored automatically

* **Wireguard peer device-side configs** — you have wg0.conf and pubkeys, but the _clients'_ `.conf` files (with admin private keys) live on admin laptops. Re-distribute them as part of the platform recovery.
* **Customer-supplied TLS certs** — if you used `tls.method: provided` in prod-config, those originals come from the customer. Backups capture the installed copies under `/etc/openg2p/certs/`, but the operator should also keep originals separately.
* **Off-cluster integrations** — anything outside Kubernetes (DNS records, external Postgres replicas, customer-side firewalls) needs separate restore planning.
* **Prometheus history / Alertmanager silence state** — monitoring stack metrics are out of scope; backup *alerting rules* may return via rancher-backup ResourceSet, but time-series data does not.
* **In-cluster SMTP delivery** — restoring the `mail` chart does not fix outbound port-25 blocks; see [Alerting](../alerting.md).
