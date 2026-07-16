---
description: Backup health monitoring — Prometheus dead-man's switch, WAL probes, and operator email.
---

# Alerting

The backup automation emits Prometheus metrics, runs an independent WAL probe outside the nightly `pg` job, can email operators who do not have SSH access, and applies a PrometheusRule into Rancher Monitoring (`cattle-monitoring-system`).

Status JSON at `/var/lib/openg2p-backup/.status.json` remains the source of truth for per-component last-run / last-drill results.

## What is alerted

| Event | Mechanism | Severity |
|---|---|---|
| Any backup component last run failed | `openg2p_backup_run_status == 0` + failure email | critical |
| No successful backup in >26h (dead-man) | `openg2p_backup_master_last_success_timestamp` | critical |
| Component hasn't run in >48h | `openg2p_backup_run_timestamp_seconds` | warning |
| Backup disk &lt;25GiB / &lt;10GiB | `openg2p_backup_disk_available_bytes` | warning / critical |
| WAL archive stalled / failing / growing | independent `wal-health` cron | critical / warning |
| Daily operator summary | SMTP `daily-report` cron | info |

## Prometheus rules (automated)

`install` applies `manifests/prometheusrule-backup.yaml.template` into `cattle-monitoring-system` when:

```yaml
monitoring:
  enabled: true
  namespace: "cattle-monitoring-system"
  apply_prometheusrule: true
```

If the PrometheusRule CRD or namespace is missing, install logs a warning and continues. Re-run `install` after Rancher Monitoring is up.

No manual `sed | kubectl apply` is required.

```bash
kubectl -n cattle-monitoring-system get prometheusrule | grep openg2p-backup
```

### Textfile metrics on the backup host

Each run (when `monitoring.enabled: true`) writes gauges under `$backup_repo_root/metrics/` (default `/var/lib/openg2p-backup/metrics/`). Configure node_exporter on the **backup host** with:

```
--collector.textfile.directory=/var/lib/openg2p-backup/metrics
```

and ensure Rancher Monitoring scrapes that node (or use Pushgateway — below). Without a scrape path, rules exist but never fire.

### Dead-man's switch

`openg2p_backup_master_last_success_timestamp` advances whenever any component reports `last_run_result=ok`. Alert `OpenG2PBackupMissed` fires if that gauge is older than 26 hours.

### Optional Pushgateway

If the backup host is not scraped by node_exporter, set `monitoring.pushgateway_url`. Metrics are POSTed after each emit. If your Pushgateway does not honor labels, adapt rule selectors to `exported_job` / `exported_instance`.

## Independent WAL health

`openg2p-backup-wal-health` runs every 5 minutes (outside `pg` backup runs). It SSHes to the storage node, measures `pg_wal` size and `pg_stat_archiver`, and writes:

* `openg2p_pg_wal_size_bytes`
* `openg2p_pg_archiver_failed_count`
* `openg2p_pg_archiver_last_archive_age_seconds`

Threshold emails use `monitoring.wal.*` in config; paging should use the PrometheusRules (`OpenG2PWAL*`).

```bash
./openg2p-backup.sh wal-health --config backup-config.yaml
```

## Email reports (operators without SSH)

```yaml
alerting:
  email_enabled: true
  smtp_env_file: "~/.openg2p/keystore/smtp.env"
```

1. Copy `automation/backups/roles/backup-host/smtp.env.example` → `~/.openg2p/keystore/smtp.env` (mode 0600).
2. Fill `SMTP_*` and `MAIL_TO`.
3. Set `email_enabled: true` and re-run `install` (copies to `/etc/openg2p-backup/smtp.env` on the backup host).

Failures from cron wrappers and laptop `run` send `[OpenG2P Backup] FAILED — …`. Daily cron at `schedules.daily_report` sends a `.status.json` summary.

```bash
./openg2p-backup.sh daily-report --config backup-config.yaml
```

### Email with in-cluster OpenG2P `mail`

The platform `mail` chart (`openg2p/smtp`) exposes SMTP as **ClusterIP port 25** and typically allows relay only from the pod CIDR (`RELAY_NETWORKS: :10.0.0.0/8`). That works for **Alertmanager inside the cluster** (`mail.<ns>.svc.cluster.local:25`), but the **backup host** (VPC `172.29.x`) cannot use ClusterIP DNS.

For backup emails:

1. Include the VPC in relay, e.g. `RELAY_NETWORKS: ':10.0.0.0/8:172.29.0.0/16'`.
2. Expose the Service (NodePort is simplest) and point `smtp.env` at the **compute private IP + NodePort**.
3. Use plain SMTP (`SMTP_STARTTLS=false`, empty `SMTP_USER` / `SMTP_PASS`).

```bash
SMTP_HOST=172.29.1.177          # compute private IP
SMTP_PORT=<mail-NodePort>
SMTP_STARTTLS=false
SMTP_USER=
SMTP_PASS=
SMTP_FROM=OpenG2P Backup <backup@YOUR_MAILNAME>
MAIL_TO=you@your-org.com
```

## Object store (MinIO/S3)

Opt-in group (`groups.objectstore: true`) using rclone read-only mount + restic. See [Configuration — Object store](configuration.md#object-store-minios3).

## How to test

| Check | Command / action | Pass look like |
|---|---|---|
| Metrics files | `run --component configs` then `cat /var/lib/openg2p-backup/metrics/*.prom` on backup host | `openg2p_backup_run_status`, `openg2p_backup_master_last_success_timestamp` present |
| WAL probe | `./openg2p-backup.sh wal-health --config …` | WAL size / archiver gauges written |
| PrometheusRule | `kubectl -n cattle-monitoring-system get prometheusrule \| grep openg2p-backup` | rule object exists |
| Prom scrape | Query `openg2p_backup_master_last_success_timestamp` in Prometheus | series returned (if empty, fix scrape/Pushgateway first) |
| Failed-run alert | Force one group to fail, wait ≥5m | `OpenG2PBackupRunFailed` in Alertmanager |
| Daily email | `./openg2p-backup.sh daily-report --config …` | inbox gets `[OpenG2P Backup] DAILY …` |

Email works without scrape. Cluster alerts need **rule + scrape** both.

## Operator checklist after upgrade

1. Merge new keys from `backup-config.example.yaml` into your `backup-config.yaml`.
2. Re-run `install` (refreshes cron wrappers + libs under `/opt/openg2p-backup`, re-applies PrometheusRule).
3. Point node_exporter at `$backup_repo_root/metrics` (or set Pushgateway).
4. Confirm PrometheusRule: `kubectl -n cattle-monitoring-system get prometheusrule | grep openg2p-backup`.
5. Optionally enable email + objectstore.
