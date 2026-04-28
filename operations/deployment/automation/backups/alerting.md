---
description: Phase 2 work — alerting on backup health. Candidate mechanisms for on-prem, air-gapped deployments.
---

# Alerting (Phase 2)

The v1 backup automation **does not implement alerting**. It writes per-component status to `/var/lib/openg2p-backup/.status.json` on the backup host and to `/var/log/openg2p-backup.log`. Operators today must inspect those files (`./openg2p-backup.sh status`) or run `./openg2p-backup.sh drill` and read the output.

This page documents candidate mechanisms for adding alerting in Phase 2. Pick one that fits your operational model.

## What needs to be alerted

| Event | Severity | When |
|---|---|---|
| `run_result` flipped to `fail` | warning | Within an hour of the failure |
| Two consecutive `run` failures for the same component | critical | Backups are silently broken |
| `drill_result` flipped to `fail` | warning | Within a day of the failed drill |
| Drill hasn't run for >10 days | warning | Cron broke or someone disabled the schedule |
| Backup repo disk usage > 85% | warning | Retention pruning isn't keeping up |
| pgBackRest WAL archive lag > 15 min | warning | RPO degraded — archive_command failing |

The first four read directly from `.status.json`. The disk and WAL-lag alerts need their own probes.

## Candidate mechanisms

### 1. Prometheus textfile collector (recommended default)

The cluster already runs Prometheus + Grafana. Add `node_exporter` to the backup host with `--collector.textfile.directory=/var/lib/openg2p-backup/metrics/`. Each backup run writes a `.prom` file:

```
# HELP openg2p_backup_run_status Last run status (1=ok, 0=fail).
# TYPE openg2p_backup_run_status gauge
openg2p_backup_run_status{component="pg"} 1
openg2p_backup_run_status{component="etcd"} 1
openg2p_backup_run_status{component="rancher"} 1
openg2p_backup_run_status{component="nfs"} 1
openg2p_backup_run_status{component="configs"} 0
openg2p_backup_run_timestamp_seconds{component="pg"} 1714183201
```

PrometheusRule alerts:

```yaml
groups:
- name: openg2p-backups
  rules:
  - alert: BackupRunFailed
    expr: openg2p_backup_run_status == 0
    for: 5m
    labels: { severity: warning }
    annotations:
      summary: "{{ $labels.component }} backup last run failed"
  - alert: BackupRunStale
    expr: time() - openg2p_backup_run_timestamp_seconds > 86400 * 2
    labels: { severity: warning }
    annotations:
      summary: "{{ $labels.component }} backup hasn't succeeded in 48h"
```

Why this is the recommended default: piggybacks on existing infra, reuses operators' familiarity with PromQL/Grafana, no external services, works air-gapped.

### 2. Healthchecks.io (self-hosted)

Each cron job pings a UUID URL on success. Missed pings trigger email/webhook. Self-hostable on the backup host or any internal Linux box.

Setup is a single `pip install hc-app` and a sqlite DB. Add to each cron line:
```cron
__PG_FULL_CRON__ root /usr/local/bin/openg2p-backup-run pg && curl -fsS https://healthchecks.local/ping/<uuid>
```

Pros: catches both "job failed" and "job didn't run". Liveness covered for free.

Cons: another web service to maintain. Sends pings outbound from the backup host — fine if the healthchecks instance is on the same VPC.

### 3. msmtp + cron MAILTO

The simplest possible alerting:

```cron
MAILTO=ops@example.gov
__NFS_CRON__ root /usr/local/bin/openg2p-backup-run nfs
```

Cron emails on non-zero exit. Configure msmtp on the backup host to relay through the customer's mail server (often on the same internal network).

Pros: zero new infrastructure if mail relay exists.
Cons: noisy — a transient failure spams every operator. Easy to ignore once the inbox fills.

### 4. Slack / Teams / webhook

If the customer permits outbound HTTPS from the backup host (or via the RP node's egress), wrap each cron job:

```bash
#!/bin/bash
/usr/local/bin/openg2p-backup-run "$1" || \
    curl -X POST -H 'Content-type: application/json' \
        --data "{\"text\":\":x: Backup $1 failed on $(hostname)\"}" \
        "$SLACK_WEBHOOK"
```

Pros: instant, where ops people already are.
Cons: depends on outbound internet — typically **not** allowed in air-gapped government deployments.

### 5. Rancher Alerting v2

Re-uses the cluster's existing notifier configuration. Works only after the cluster is healthy — so it's only useful for warnings about backups themselves, not for "the cluster is gone, alert me" scenarios.

[Rancher Alerting docs](https://ranchermanager.docs.rancher.com/how-to-guides/advanced-user-guides/enable-experimental-features/alerting-drivers).

## When to revisit

Phase 2 should land when the platform has been in production for at least a quarter and operators have a clearer picture of which alerts they actually want. Avoid building alerting before you know the failure modes — alert fatigue is a worse outcome than no alerts.

For now, the recommended interim practice is:
* `./openg2p-backup.sh status` every Monday morning (5 minutes of operator time per week)
* Eyeball `/var/log/openg2p-backup.log` after any production deploy
* Manually run `./openg2p-backup.sh drill` after major platform upgrades

If a customer mandates alerting from day one, start with Prometheus textfile collector (option 1) — the rules above can be in your initial install.
