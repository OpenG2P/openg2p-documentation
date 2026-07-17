---
description: Day-to-day backup operations — install, run, verify, list, status, wal-health, daily-report, group toggling.
---

# Operations

The orchestrator is `automation/backups/openg2p-backup.sh`. Every subcommand takes `--config backup-config.yaml`. Most also accept `--component <name>` to target a single group (`all`, `pg`, `etcd`, `rancher`, `nfs`, `configs`, `objectstore`).

## Subcommands

```
./openg2p-backup.sh install       # one-time / idempotent bootstrap
./openg2p-backup.sh run           # execute backups now (also used by cron)
./openg2p-backup.sh verify        # cheap integrity checks, no restore
./openg2p-backup.sh drill         # weekly drill (verify + dry-run-restore)
./openg2p-backup.sh list          # what's in each repo
./openg2p-backup.sh restore       # see Restoration page
./openg2p-backup.sh status        # last-run + last-drill state
./openg2p-backup.sh wal-health    # independent PG WAL / archiver probe
./openg2p-backup.sh daily-report  # email .status.json summary (if SMTP enabled)
./openg2p-backup.sh help
```

`--component` accepts **one** value (or `all`). Do not pass multiple group names on one line.

## install

```bash
# Full bootstrap (all enabled groups + cron + PrometheusRule when monitoring.enabled)
./openg2p-backup.sh install --config backup-config.yaml

# Re-run a single group's install steps (e.g. after changing rancher storage)
./openg2p-backup.sh install --config backup-config.yaml --component rancher
```

`--component` is supported for `install` as well as `run` / `verify` / `list`. Per-group install skips the other groups — useful when re-provisioning rancher storage without triggering `etcd_install`'s `rke2-server` restart. Backup-host bootstrap and cron redeploy still run on every `install` invocation.

What it does, in order:

1. **SSH probes** for backup, plus production nodes touched by enabled groups.
2. **Backup-host preflight** — Ubuntu version, CPU (≥4, hard), RAM (≥8 GB, hard), root disk (≥64 GB, hard), repo data volume (≥1 TB, **warn-only**). Skip with `--skip-preflight` when re-running against a known-good host.
3. **Passphrase resolution** — reads each `*_passphrase_file` from the keystore. Generates if missing (with a banner reminder to move into the keystore).
4. **Backup-host bootstrap** — apt installs, repo dirs, lib files pushed to `/opt/openg2p-backup/`, SSH key generated for orchestrating compute/storage/RP, authorized on those nodes, wrapper scripts installed:
   * `/usr/local/bin/openg2p-backup-run`
   * `/usr/local/bin/openg2p-backup-drill`
   * `/usr/local/bin/openg2p-backup-status`
   * `/usr/local/bin/openg2p-backup-wal-health`
   * `/usr/local/bin/openg2p-backup-daily-report`
5. **Per-group install** — gated by `groups.<name>` toggle and `--component` (when not `all`):
   * `pg`: pgBackRest on backup + storage, archive_command on PG, stanza-create, first full backup
   * `etcd`: RKE2 snapshot schedule, rsync-pull SSH trust
   * `rancher`: rancher-backup operator (chart `107.1.5+up8.1.5` default), static NFS PV `openg2p-rancher-backup-store`, encryption Secret, ResourceSet + in-cluster Schedule CR
   * `nfs`: storage-node NFS export + `ufw` allow for backup host, read-only NFS mount on backup host (idempotent if already mounted), restic repo init
   * `configs`: restic repo for configs
   * `objectstore` (opt-in): rclone + restic for MinIO/S3 — skipped when `groups.objectstore: false` (default)
6. **SMTP install** (optional) — copies `alerting.smtp_env_file` to `/etc/openg2p-backup/smtp.env` when present.
7. **PrometheusRule** — when `monitoring.enabled` and `monitoring.apply_prometheusrule` are true, applies `manifests/prometheusrule-backup.yaml.template` into `cattle-monitoring-system` (warns and continues if CRD/namespace missing).
8. **Optional encryption-at-rest** — only if `--enable-secret-encryption` flag is passed. Restarts kube-apiserver.
9. **Cron deploy** — renders `cron.template` with active schedules, installs at `/etc/cron.d/openg2p-backup`.

`install` is **idempotent** — re-running it is safe. Pass `--force` where individual steps honour it. After pulling new orchestrator code, re-run `install` to refresh `/opt/openg2p-backup/lib` and the wrappers.

## run

```bash
# All enabled groups
./openg2p-backup.sh run --config backup-config.yaml --component all

# Just one
./openg2p-backup.sh run --config backup-config.yaml --component pg
```

Used by cron on the backup host (via `openg2p-backup-run <group>`). PG honors `PGBR_TYPE=full|diff` — the cron file passes `full` on Sundays and `diff` other days.

If a group is disabled in config, `run --component <that-group>` exits with a warning rather than failing.

Failures don't stop other groups — `run` attempts every enabled group and surfaces per-group results in the status file. Failed groups also trigger failure email when `alerting.email_enabled: true`. Each run updates Prometheus textfile metrics under `$backup_repo_root/metrics/` when `monitoring.enabled: true`.

**rancher is special.** The nightly rancher backup is driven by an in-cluster `Schedule` CR, not by the cron file on the backup host. `run --component rancher` from the laptop creates an *ad-hoc* `Backup` CR — useful before upgrades, but not the routine cadence.

## verify

```bash
./openg2p-backup.sh verify --config backup-config.yaml [--component X]
```

Cheap integrity checks. No data restored. When `--component all`, every enabled group is checked; a failure in one group does not stop the others (the orchestrator exits non-zero if any group failed).

| Group | Verify command |
|---|---|
| pg | `pgbackrest verify` |
| etcd | Finds the latest `etcd-snapshot-*` on the backup host (auto-pulls from compute once if empty). Runs `etcdctl`/`etcdutl snapshot status` locally; if the distro `etcd-client` cannot read RKE2's snapshot format, falls back to RKE2-bundled tools on compute and confirms the backup copy is present |
| rancher | Resolves the static NFS path (`/srv/nfs/<cluster>/rancher-backup` by default), SSHes to the storage node, confirms the latest `*.tar.gz` or `*.tar.gz.enc` is present and non-zero. Encrypted tarballs skip `gzip -t` (ciphertext, not plain gzip) |
| nfs | `restic check --read-data-subset=5%` on the NFS repo |
| configs | `restic check --read-data-subset=5%` on the configs repo |
| objectstore | `restic snapshots --latest 1` + `restic check --read-data-subset=1%` (when enabled) |

## drill

```bash
./openg2p-backup.sh drill --config backup-config.yaml
```

Weekly. Runs every group's `<group>_drill` function (verify + canary restore + tear down) and writes results to `/var/lib/openg2p-backup/.status.json` on the backup host. See [Drills](drills.md).

## list

```bash
./openg2p-backup.sh list --config backup-config.yaml [--component X]
```

Inventory per repo:

* **pg** → `pgbackrest info` (backup sets, dates, sizes)
* **etcd** → `ls -lh` of pulled snapshots
* **rancher** → `kubectl get backup.resources.cattle.io -A`
* **nfs / configs / objectstore** → `restic snapshots --compact`

For NFS, the sidecar `.pvc-mapping.yaml` is what tells you which PVC each UUID belongs to. Read it directly:

```bash
ssh ubuntu@<backup-host> sudo cat /var/lib/openg2p-backup/nfs/.pvc-mapping.yaml
```

## status

```bash
./openg2p-backup.sh status --config backup-config.yaml
```

Tabular per-group last-run and last-drill state, read from `/var/lib/openg2p-backup/.status.json`:

```
GROUP       STATE      LAST-RUN               RESULT     LAST-DRILL             RESULT
----------  ---------- ---------------------- ---------- ---------------------- --------
pg          enabled    2026-04-27T02:00:01Z   ok         2026-04-27T05:00:09Z   ok
etcd        enabled    2026-04-27T18:15:00Z   ok         2026-04-27T05:00:14Z   ok
rancher     enabled    2026-04-27T03:00:02Z   ok         2026-04-27T05:00:18Z   ok
nfs         enabled    2026-04-27T03:30:11Z   ok         2026-04-27T05:00:35Z   ok
configs     enabled    2026-04-27T03:30:14Z   ok         2026-04-27T05:00:42Z   ok
objectstore disabled   -                      -          -                      -
```

Disabled groups show `disabled` and dashes. The same JSON drives daily email summaries and complements Prometheus metrics — see [Alerting](alerting.md).

## wal-health

```bash
./openg2p-backup.sh wal-health --config backup-config.yaml
```

Independent of `pg` backup runs. SSHes to the storage node, measures `pg_wal` size and `pg_stat_archiver`, writes metrics, and (when email is enabled) notifies if `monitoring.wal.*` thresholds are exceeded. Cron runs this every 5 minutes via `openg2p-backup-wal-health`.

## daily-report

```bash
./openg2p-backup.sh daily-report --config backup-config.yaml
```

Emails operators a summary of `.status.json` when `alerting.email_enabled: true`.

After `install`, this runs **automatically** on the backup host via cron (`schedules.daily_report`, default `0 7 * * *` → `/usr/local/bin/openg2p-backup-daily-report`). The laptop command above is for smoke-testing only.

Failure mails are separate: they are sent automatically when a backup/drill run fails (no need to invoke `daily-report`). See [Alerting](alerting.md).

## Group toggles

Edit `backup-config.yaml`:

```yaml
groups:
  pg:          true
  etcd:        true
  rancher:     true
  nfs:         false   # ← disabled
  configs:     true
  objectstore: false   # opt-in MinIO/S3 (default false)
```

Re-run `install` to apply. The cron file is regenerated and the disabled group's lines are commented out (kept for reference). `objectstore` defaults to **off** when the key is absent so existing installs are not surprised.

## Forcing a re-run / resetting state

`install` uses state markers under `automation/backups/.state/` (laptop side) and `/var/lib/openg2p/deploy-state/` (remote side). `--force` ignores them where applicable:

```bash
./openg2p-backup.sh install --config backup-config.yaml --force
```

To reset only the laptop state, delete the `.state/` directory.

## Re-running aws-provision to add the backup node

The Backup node is required for production. If you brought the platform up before provisioning it (the recommended order is to have backups in place before go-live), add it as follows:

```bash
cd automation/production/aws/
# Edit aws-config.yaml: backup_node.enabled: true
./openg2p-aws-provision.sh --config aws-config.yaml
# This is idempotent — RP/compute/storage are unchanged.
# The new instance + EBS volume + SG are created.
# provision-output.yaml is updated with backup_* keys.
cd ../../backups/
cp backup-config.example.yaml backup-config.yaml
# Edit backup-config.yaml
./openg2p-backup.sh install --config backup-config.yaml
```

## Logs

| Location | Content |
|---|---|
| `automation/backups/logs/openg2p-backup-<timestamp>.log` | Laptop orchestrator invocation |
| `/var/log/openg2p-backup.log` on backup host | Cron group runs, drill, daily-report |
| `/var/log/openg2p-backup-wal.log` on backup host | WAL-health cron |
| `/var/lib/openg2p-backup/metrics/*.prom` on backup host | Prometheus textfile gauges |
| `/var/lib/openg2p-backup/.status.json` on backup host | Last-run / last-drill JSON |
