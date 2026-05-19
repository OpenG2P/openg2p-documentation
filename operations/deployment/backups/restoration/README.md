---
description: >-
  Index of restoration scenarios — pick one based on what failed and what you're
  trying to bring back.
---

# Restoration

There are four common restore scenarios. Pick one:

| Scenario          | When to use                                                                                                                                               | Page                                             |
| ----------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------ |
| **Postgres PITR** | A bad migration, accidental DROP TABLE, or DELETE without WHERE. You want to roll back the database to a specific moment.                                 | [postgres-pitr.md](postgres-pitr.md)             |
| **Single PVC**    | One application's data is corrupt or accidentally wiped, but the cluster and other apps are fine. Common case: Keycloak realm exports, MinIO bucket data. | [restoration/single-pvc.md](single-pvc.md)       |
| **Etcd in-place** | The cluster's control plane is broken (etcd corrupted, master crashed without redundancy) but the compute node and its disk are reusable.                 | [restoration/etcd-in-place.md](etcd-in-place.md) |
| **Full rebuild**  | Disaster — node(s) destroyed, hardware lost. Build fresh and layer backups onto it.                                                                       | [restoration/full-rebuild.md](full-rebuild.md)   |

## General principles

**Restore is always staged first.** The orchestrator never overwrites live data. Every restore lands in a `/var/lib/openg2p-backup-restore/` (storage / backup host) or `/tmp/openg2p-*-restore/` directory and the operator follows a runbook step to make the cutover.

**Use `--dry-run` first.** Every restore subcommand supports `--dry-run`, which prints what would happen without doing it.

**Keep the keystore handy.** Every restore needs the same passphrases used at backup time. Losing the passphrase = losing the backup.

**Don't run two restores in parallel.** Especially across components — the relationships between PG, NFS data, and PV/PVC bindings matter. Restore PG → restore NFS → reconcile PV/PVCs → restart pods.

## Choosing a restore order

For a partial loss (one app):

1. Restore that app's PVC ([single-pvc.md](single-pvc.md))
2. Restart the app's pods

For a full rebuild:

1. Provision fresh nodes + run `openg2p-prod.sh install` to get the platform back
2. Restore Postgres ([postgres-pitr.md](postgres-pitr.md), with `--type=immediate`)
3. Restore Kubernetes resources via rancher-backup `Restore` CR ([full-rebuild.md](full-rebuild.md))
4. Restore NFS data + reconcile PVC mappings via the sidecar manifest
5. Restart workloads, verify

For control-plane recovery without rebuilding:

1. [etcd-in-place.md](etcd-in-place.md) — restore the snapshot, restart RKE2 with `--cluster-reset`

## Things that are not restored automatically

* **Wireguard peer device-side configs** — you have wg0.conf and pubkeys, but the _clients'_ `.conf` files (with admin private keys) live on admin laptops. Re-distribute them as part of the platform recovery.
* **Customer-supplied TLS certs** — if you used `tls.method: provided` in prod-config, those originals come from the customer. Backups capture the installed copies under `/etc/openg2p/certs/`, but the operator should also keep originals separately.
* **Off-cluster integrations** — anything outside Kubernetes (DNS records, external Postgres replicas, customer-side firewalls) needs separate restore planning.
