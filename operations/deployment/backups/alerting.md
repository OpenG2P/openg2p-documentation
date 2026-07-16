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
2. Fill `SMTP_*` and `MAIL_TO`. **Always quote `SMTP_FROM`** when it contains spaces or angle brackets — the file is `source`d by bash (`SMTP_FROM="OpenG2P Backup <ops@example.org>"`). Unquoted `<…>` causes a syntax error.
3. Set `email_enabled: true` and re-run `install` (copies to `/etc/openg2p-backup/smtp.env` on the backup host).

**Automatic vs manual**

| Event | When it fires |
|---|---|
| Daily `.status.json` summary | Cron on the backup host (`schedules.daily_report`, default `0 7 * * *`) — no laptop action needed |
| Backup / drill failure | Automatic on non-zero exit from `openg2p-backup-run` / `drill` (and laptop `run`) |
| Ad-hoc test | `./openg2p-backup.sh daily-report --config backup-config.yaml` |

`MAIL_SENT` in the log means the backup host handed the message to `SMTP_HOST`. It does **not** guarantee the recipient inbox received it — check the SMTP/relay logs if mail is missing.

### Recommended: authenticated smarthost (port 587)

On AWS and many clouds, **outbound TCP 25 is blocked**. The in-cluster `mail` chart (Exim) can accept mail from the backup host and then fail when delivering to Gmail/Google Workspace MX (`Network is unreachable` / `Connection timed out` on `:25`). Prefer a real smarthost:

```bash
SMTP_HOST=smtp.gmail.com          # or org SES/SendGrid/relay
SMTP_PORT=587
SMTP_STARTTLS=true
SMTP_USER=your-account@example.org
SMTP_PASS=your-app-or-smtp-password
SMTP_FROM="OpenG2P Backup <your-account@example.org>"
MAIL_TO=ops@example.org
```

### Email with in-cluster OpenG2P `mail`

The platform `mail` chart (`openg2p/smtp`) exposes SMTP as **ClusterIP port 25** and typically allows relay only from the pod CIDR (`RELAY_NETWORKS: :10.0.0.0/8`). That works for **Alertmanager inside the cluster** (`mail.<ns>.svc.cluster.local:25`), but the **backup host** (VPC `172.29.x`) cannot use ClusterIP DNS.

For backup emails via that pod (only if outbound :25 works in your environment):

1. Include the VPC in relay, e.g. `RELAY_NETWORKS: ':10.0.0.0/8:172.29.0.0/16'`.
2. Expose the Service (NodePort is simplest) and point `smtp.env` at the **compute private IP + NodePort**.
3. Use plain SMTP (`SMTP_STARTTLS=false`, empty `SMTP_USER` / `SMTP_PASS`).
4. If `MAIL_SENT` appears but no inbox mail, check `kubectl -n <mail-ns> logs deploy/mail` for MX/:25 timeouts — then switch to a **587 smarthost** (above).

```bash
SMTP_HOST=172.29.1.177          # compute private IP
SMTP_PORT=<mail-NodePort>
SMTP_STARTTLS=false
SMTP_USER=
SMTP_PASS=
SMTP_FROM="OpenG2P Backup <backup@YOUR_MAILNAME>"
MAIL_TO=you@your-org.com
```

## Slack (via Alertmanager)

Backup scripts do **not** post to Slack themselves. Slack is configured on **Rancher Monitoring Alertmanager**, which receives the backup PrometheusRules once metrics are scraped.

In `prod-config.yaml` (production automation):

```yaml
alert_slack_webhook_url: "https://hooks.slack.com/services/…"
alert_slack_channel: "#alerts"
```

Re-apply the monitoring/alerting values so Alertmanager picks up the receiver. Then firing rules such as `OpenG2PBackupMissed`, `OpenG2PBackupRunFailed`, and `OpenG2PWAL*` can notify Slack.

| Channel | Configured where | Covers |
|---|---|---|
| Email | `backup-config.yaml` → `alerting.*` + `smtp.env` | Daily summary + script failure mails |
| Slack | `prod-config.yaml` → `alert_slack_*` + Alertmanager | Prometheus-fired backup / WAL alerts |

You can enable both; they complement each other.

## Object store (MinIO/S3)

Opt-in group (`groups.objectstore: true`) using rclone read-only mount + restic. See [Configuration — Object store](configuration.md#object-store-minios3).

## How to test

| Check | Command / action | Pass look like |
|---|---|---|
| Metrics files | `run --component configs` then `cat /var/lib/openg2p-backup/metrics/*.prom` on backup host | `openg2p_backup_run_status`, `openg2p_backup_master_last_success_timestamp` present |
| WAL probe | `./openg2p-backup.sh wal-health --config …` | WAL size / archiver gauges written |
| PrometheusRule | `kubectl -n cattle-monitoring-system get prometheusrule \| grep openg2p-backup` | rule object exists |
| Prom scrape | Query `openg2p_backup_master_last_success_timestamp` in Prometheus | series returned (if empty, fix scrape/Pushgateway first) |
| Failed-run alert | Force one group to fail, wait ≥5m | `OpenG2PBackupRunFailed` in Alertmanager (and Slack if configured) |
| Daily email | `./openg2p-backup.sh daily-report --config …` | `MAIL_SENT` **and** message in inbox (if only `MAIL_SENT`, check relay logs / use port 587) |

Email works without scrape. Cluster / Slack alerts need **rule + scrape** both.

## Operator checklist after upgrade

1. Merge new keys from `backup-config.example.yaml` into your `backup-config.yaml`.
2. Re-run `install` (refreshes cron wrappers + libs under `/opt/openg2p-backup`, re-applies PrometheusRule).
3. Point node_exporter at `$backup_repo_root/metrics` (or set Pushgateway).
4. Confirm PrometheusRule: `kubectl -n cattle-monitoring-system get prometheusrule | grep openg2p-backup`.
5. Optionally enable email (prefer SMTP :587) and/or Slack via Alertmanager; optionally enable objectstore.
