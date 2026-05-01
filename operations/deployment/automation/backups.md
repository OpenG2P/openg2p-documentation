---
description: >-
  Backup and restore automation for OpenG2P 3-node production installs —
  PostgreSQL via pgBackRest, etcd snapshots, rancher-backup for Kubernetes
  resources, restic for NFS data and configs. Pull-based f
---

# Backups

This page is the entry point for the OpenG2P backup automation that lives at `automation/backups/openg2p-backup.sh` in the deployment repo. It complements the [Three-Node Automation](three-node-automation.md): the 3-node script gets the platform up, the backup automation keeps it recoverable.

{% hint style="info" %}
The whole stack is opt-in. You can deploy the 3-node platform without backups, then add backups later by running aws-provision again with `backup_node.enabled: true` and running `openg2p-backup.sh install`.
{% endhint %}

## What this is, in one paragraph

A 4th "backup" node, on the same VPC, runs cron-driven backups of every part of an OpenG2P production install — PostgreSQL via pgBackRest with WAL streaming for \~1-minute RPO, etcd snapshots from RKE2's built-in mechanism, Kubernetes resources via the [rancher-backup operator](https://ranchermanager.docs.rancher.com/integrations-in-rancher/backup-restore-and-disaster-recovery), NFS data via [restic](https://restic.net/) with a sidecar manifest that maps NFS UUID directories back to their PVC/namespace/app, and the small but critical filesystem state (Wireguard config, Nginx config, RKE2 TLS material) via restic over SSH-tar. All repos are encrypted at rest. Drills run weekly. Restores are deliberate — staged into temp dirs, never overwriting live data without an operator's runbook step.

## Sub-pages

* [Architecture](backups/architecture.md) — the tools, why each is here, what's deliberately not used
* [What gets backed up](backups/what-gets-backed-up.md) — the per-component table and the rationale for what's lost vs. recreated on a fresh install
* [Prerequisites](backups/prerequisites.md) — backup-node sizing, network, secret custody (p12 keystore model)
* [Configuration](backups/configuration.md) — `backup-config.yaml` reference
* [Operations](backups/operations.md) — `install`, `run`, `verify`, `list`, `status`, group toggles
* [Drills](backups/drills.md) — weekly verify + dry-run-restore harness, interpreting `.status.json`
* [Restoration](backups/restoration.md) — index of restore scenarios
  * [Postgres PITR](backups/restoration/postgres-pitr.md)
  * [Single PVC](backups/restoration/single-pvc.md)
  * [Etcd in-place](backups/restoration/etcd-in-place.md)
  * [Full rebuild](backups/restoration/full-rebuild.md)
* [Alerting (Phase 2)](backups/alerting.md) — candidate mechanisms, deferred from v1

## TL;DR — get backups running

```bash
# 0. (One-time, only if you didn't enable backup_node before) Re-provision
#    AWS to add the 4th instance + EBS volume.
cd automation/production/aws/
# Set backup_node.enabled: true in aws-config.yaml
./openg2p-aws-provision.sh --config aws-config.yaml

# 1. Configure backups.
cd ../../backups/
cp backup-config.example.yaml backup-config.yaml
# Edit backup-config.yaml — passphrase paths in your p12 keystore,
# group toggles (default: all on), retention, schedules.

# 2. Bootstrap.
./openg2p-backup.sh install --config backup-config.yaml

# 3. Smoke-test.
./openg2p-backup.sh run --config backup-config.yaml --component all
./openg2p-backup.sh status --config backup-config.yaml

# 4. (Optional, separate maintenance window) Enable encryption-at-rest for
#    Kubernetes Secrets in etcd. Apiserver restarts (~30-60s).
./openg2p-backup.sh install --config backup-config.yaml --enable-secret-encryption
```

After install, cron on the backup host runs the daily/weekly schedule. Operators interact with the system via the orchestrator from their laptop for ad-hoc runs, status checks, and restores.

## Recovery objectives

| Component                                         | RPO           | RTO                                           |
| ------------------------------------------------- | ------------- | --------------------------------------------- |
| PostgreSQL (with WAL streaming)                   | ≈1 min        | minutes (PITR), 10s of minutes (full restore) |
| Kubernetes resources (Secrets, CRs, PV/PVCs)      | 24h (nightly) | 5–15 min (rancher-backup `Restore` CR)        |
| NFS data                                          | 24h           | minutes per PVC, hours for full export        |
| etcd snapshots                                    | 6h            | 5–10 min (cluster-reset restore)              |
| RP/compute filesystem state (WG, Nginx, RKE2 TLS) | 24h           | minutes per subsystem                         |

All of these are configurable via `backup-config.yaml` schedules. The defaults match a 6-month retention window and assume a 1 TB backup volume; smaller volumes work but shorten retention before pruning.

## What this does not do

* **Multi-site / offsite replication.** v1 keeps one copy on one volume on the backup node. The 3-2-1 rule says 3 copies on 2 media with 1 offsite — this is 1/1/0. Plan a second offsite target later via `restic copy` or pgBackRest's secondary repo support.
* **Mass alerting.** Status is exposed as `/var/lib/openg2p-backup/.status.json` on the backup host. A Phase 2 layer wires that into Prometheus/email/Slack (see [Alerting](backups/alerting.md)).
* **Full disaster-recovery rehearsal.** Weekly drills do per-component verify + dry-run-restore. Cluster-wide rehearsals into a sandbox VPC are a manual, separately-scheduled operator activity.
* **Restoring to a different cluster topology.** Restore assumes you're rebuilding into the same 3-node shape. Cross-version or cross-architecture restore is out of scope.

## Reference

* [pgBackRest user guide](https://pgbackrest.org/user-guide.html)
* [restic documentation](https://restic.readthedocs.io/)
* [RKE2 backup and restore](https://docs.rke2.io/backup_restore)
* [Rancher Backup Operator](https://ranchermanager.docs.rancher.com/integrations-in-rancher/backup-restore-and-disaster-recovery)
* [Kubernetes encryption at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
