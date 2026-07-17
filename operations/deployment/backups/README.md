---
description: >-
  Backup and restore automation for OpenG2P production - PostgreSQL via
  pgBackRest, etcd snapshots, rancher-backup for Kubernetes resources, restic
  for NFS data and configs. Pull-based and encrypted. Op
---

# Backups

This page is the entry point for the OpenG2P backup automation that lives at `automation/backups/openg2p-backup.sh` in the deployment repo. It complements the [Production Automation](../infrastructure-setup/production-automation/): the production script gets the platform up, the backup automation keeps it recoverable.

{% hint style="info" %}
**Ongoing operational concern** — not a one-time deployment stage. Configure backups **before go-live** and keep them running throughout the system's lifetime. For the staged Production rollout, see the [Production overview](../infrastructure-setup/).
{% endhint %}

{% hint style="info" %}
Backups are **required for production** and must be in place before go-live — the Backup node is the 4th node of the production topology. The platform install and the backup setup are **separate steps**: bring the cluster up first, then provision the Backup node (`backup_node.enabled: true`) and run `openg2p-backup.sh install`. (You _can_ stand the platform up first and add backups before go-live, but a production deployment is not complete without them.)
{% endhint %}

## What this is, in one paragraph

A 4th "backup" node, on the same VPC, runs cron-driven backups of every part of an OpenG2P production install — PostgreSQL via pgBackRest with WAL streaming for \~1-minute RPO, etcd snapshots from RKE2's built-in mechanism, Kubernetes resources via the [rancher-backup operator](https://ranchermanager.docs.rancher.com/integrations-in-rancher/backup-restore-and-disaster-recovery), NFS data via [restic](https://restic.net/) with a sidecar manifest that maps NFS UUID directories back to their PVC/namespace/app, filesystem state (Wireguard, Nginx, RKE2 TLS) via restic over SSH-tar, and (opt-in) MinIO/S3 object data via rclone read-only mount + restic. All repos are encrypted at rest. Install also wires Prometheus textfile metrics, an independent WAL-health probe, optional SMTP daily/failure mail, and a PrometheusRule into `cattle-monitoring-system`. Drills run weekly. Restores are deliberate — staged into temp dirs, never overwriting live data without an operator's runbook step.

## Sub-pages

* [Architecture](architecture.md) — the tools, why each is here, what's deliberately not used
* [What gets backed up](what-gets-backed-up.md) — the per-component table and the rationale for what's lost vs. recreated on a fresh install
* [Prerequisites](prerequisites.md) — backup-node sizing, network, secret custody (p12 keystore model)
* [Configuration](configuration.md) — `backup-config.yaml` reference
* [Operations](operations.md) — `install`, `run`, `verify`, `list`, `status`, `wal-health`, `daily-report`, group toggles
* [Drills](drills.md) — weekly verify + dry-run-restore harness, interpreting `.status.json`
* [Restoration](restoration/) — index of restore scenarios
  * [Postgres PITR](restoration/postgres-pitr.md)
  * [Single PVC](restoration/single-pvc.md)
  * [Etcd in-place](restoration/etcd-in-place.md)
  * [Full rebuild](restoration/full-rebuild.md)
* [Alerting](alerting.md) — Prometheus dead-man's switch, WAL probes, operator email

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
# group toggles (default: all on except objectstore), retention, schedules,
# monitoring/alerting if you want mail + Prometheus rules.

# 2. Bootstrap.
./openg2p-backup.sh install --config backup-config.yaml

# 3. Smoke-test.
./openg2p-backup.sh run --config backup-config.yaml --component all
./openg2p-backup.sh verify --config backup-config.yaml --component all
./openg2p-backup.sh status --config backup-config.yaml
./openg2p-backup.sh wal-health --config backup-config.yaml

# 4. (Optional, separate maintenance window) Enable encryption-at-rest for
#    Kubernetes Secrets in etcd. Apiserver restarts (~30-60s).
./openg2p-backup.sh install --config backup-config.yaml --enable-secret-encryption
```

After install, cron on the backup host runs the daily/weekly schedule plus WAL-health (every 5m) and daily-report (morning email when SMTP is enabled). Operators interact via the orchestrator from their laptop for ad-hoc runs, status checks, and restores. See [Alerting](alerting.md) to confirm PrometheusRule + metrics scrape.

## Recovery objectives

| Component                                         | RPO           | RTO                                           |
| ------------------------------------------------- | ------------- | --------------------------------------------- |
| PostgreSQL (with WAL streaming)                   | ≈1 min        | minutes (PITR), 10s of minutes (full restore) |
| Kubernetes resources (Secrets, CRs, PV/PVCs)      | 24h (nightly) | 5–15 min (rancher-backup `Restore` CR)        |
| NFS data                                          | 24h           | minutes per PVC, hours for full export        |
| etcd snapshots                                    | 6h            | 5–10 min (cluster-reset restore)              |
| RP/compute filesystem state (WG, Nginx, RKE2 TLS) | 24h           | minutes per subsystem                         |
| Object store (MinIO/S3, if `groups.objectstore`)  | 24h (nightly) | minutes (restic restore from backup host)     |

All of these are configurable via `backup-config.yaml` schedules. The defaults match a 6-month retention window and assume a 1 TB backup volume; smaller volumes work but shorten retention before pruning.

## What this does not do

* **Multi-site / offsite replication.** The default keeps one copy on one volume on the backup node. The 3-2-1 rule says 3 copies on 2 media with 1 offsite — plan a second offsite target later via `restic copy` or pgBackRest's secondary repo. Opt-in `objectstore` backs _up_ MinIO/S3 _onto_ the backup host; it is not itself an offsite copy.
* **Scraping the backup host for you.** `install` writes textfile metrics and applies a PrometheusRule into `cattle-monitoring-system`, but Prometheus only sees those metrics if node\_exporter (or Pushgateway) on the backup host is scraped. See [Alerting](alerting.md).
* **Full disaster-recovery rehearsal.** Weekly drills do per-component verify + dry-run-restore. Cluster-wide rehearsals into a sandbox VPC are a manual, separately-scheduled operator activity.
* **Restoring to a different cluster topology.** Restore assumes you're rebuilding into the same production shape. Cross-version or cross-architecture restore is out of scope.

## Reference

* [pgBackRest user guide](https://pgbackrest.org/user-guide.html)
* [restic documentation](https://restic.readthedocs.io/)
* [rclone documentation](https://rclone.org/docs/)
* [RKE2 backup and restore](https://docs.rke2.io/backup_restore)
* [Rancher Backup Operator](https://ranchermanager.docs.rancher.com/integrations-in-rancher/backup-restore-and-disaster-recovery)
* [Kubernetes encryption at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/)
