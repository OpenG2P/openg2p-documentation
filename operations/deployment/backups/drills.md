---
description: >-
  Weekly automated drill — verify + dry-run-restore + canary checks across every
  enabled backup group.
---

# Drills

Backups you don't test aren't backups. The orchestrator's `drill` subcommand runs a weekly verify + dry-run-restore for every enabled group and aggregates the results into a single status file. Cron schedules this for Sunday 05:00 by default — after the night's PG, NFS, and configs runs have completed.

## What each component's drill does

| Group       | Drill steps                                                                                                                                                                                                                                                                                            |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **pg**      | `pgbackrest verify` → restore latest full into `/var/lib/openg2p-backup-restore/drill-pg-<timestamp>` on storage → if `pg.canary_table` is set, start a temporary Postgres on port 55432 and run `SELECT count(*) FROM <canary_table>` → tear down                                                     |
| **etcd**    | Same as `verify`: auto-pull if the backup host copy is empty, then `etcdctl`/`etcdutl snapshot status` (with compute fallback via RKE2-bundled tools when the backup-host `etcd-client` is too old) |
| **rancher** | Resolves the rancher-backup NFS path (`openg2p-rancher-backup-store` static PV → `/srv/nfs/<cluster>/rancher-backup`), then SSHes to the storage node to confirm the latest `*.tar.gz` or `*.tar.gz.enc` is present, non-zero size, and passes `gzip -t` when not encrypted. (Encrypted tarballs cannot be listed with `tar -tzf`.) |
| **nfs**     | `restic check --read-data-subset=5%` on the NFS repo → `restic restore` of the canary file (`.pvc-mapping.yaml`) into a tempdir                                                                                                                                                                        |
| **configs** | `restic check --read-data-subset=5%` on the configs repo → `restic restore` of the smallest tagged snapshot (the `openg2p` tag) into a tempdir                                                                                                                                                         |
| **objectstore** | (When enabled) restic restore of the latest objectstore-tagged snapshot into a tempdir on the backup host, confirm non-empty, tear down |

`--read-data-subset=5%` re-reads 5% of the actual blob bytes (not just metadata), giving statistical confidence the bytes haven't bit-rotted on disk while keeping drill runtime modest.

## Running a drill manually

```bash
./openg2p-backup.sh drill --config backup-config.yaml
```

Output is human-readable; per-group verdicts go to the screen and aggregated into the status file.

## Status file

`/var/lib/openg2p-backup/.status.json` on the backup host. Schema:

```json
{
  "components": {
    "pg": {
      "last_run":          "2026-04-27T02:00:01Z",
      "last_run_result":   "ok",
      "last_run_details":  "type=full",
      "last_drill":        "2026-04-27T05:00:09Z",
      "last_drill_result": "ok",
      "last_drill_details": "verify+restore +canary"
    },
    "etcd":   { "last_run": "...", "last_drill": "...", ... },
    "rancher": { ... },
    "nfs":    { ... },
    "configs": { ... },
    "objectstore": { ... }
  }
}
```

`./openg2p-backup.sh status --config backup-config.yaml` reads this file via the backup host and tabulates it. When `alerting.email_enabled` is true, `daily-report` emails the same summary; Prometheus gauges under `$backup_repo_root/metrics/` mirror last-run outcomes for Alertmanager — see [Alerting](alerting.md).

## Reading the results

| Result     | Meaning                                                                                                                                                                                                           |
| ---------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `ok`       | Drill passed. Backups are restorable.                                                                                                                                                                             |
| `fail`     | At least one step in the drill failed. **Investigate before the next run.** Common causes: pgBackRest stanza dropped (e.g. PG was reinstalled), restic repo password file modified, etcd snapshot file truncated. |
| `disabled` | The group is disabled in `backup-config.yaml`. No drill runs.                                                                                                                                                     |
| `-`        | The drill has never run for this group (fresh install).                                                                                                                                                           |

A failed drill does NOT roll back the broken backup. The latest still-good backup is whatever passed `verify` previously. Restore drills do not modify production data — they restore into temp directories on the storage node and tear them down.

## Tuning drill cadence

Drills are cheap (5–15 minutes total) but they do read full snapshot contents. If you want to run them more often, edit `schedules.drill` in `backup-config.yaml`:

```yaml
schedules:
  drill: "0 5 * * *"   # every day at 05:00 instead of weekly
```

Re-run `install` to update the cron file. We recommend keeping at least the Sunday weekly cadence — it catches "haven't run drills in months" rust earlier than monthly.

## What drills do NOT cover

* **Network DR** — drills assume the backup host has SSH to compute and storage. They don't simulate a network partition.
* **Cross-version restore** — drills restore into the same tooling versions that produced the backup. Restoring a backup made on PG 16 into PG 17 needs a manual upgrade dance (see [Postgres PITR](restoration/postgres-pitr.md)).
* **Full cluster rebuild** — too disruptive to automate weekly. Schedule a manual rehearsal quarterly into a sandbox VPC. See [Full rebuild](restoration/full-rebuild.md).
* **Encryption key rotation** — drills don't test that you can decrypt with a _new_ key. Plan key rotation as a separate exercise.

## Common failure modes and what to check

<table><thead><tr><th width="340">Drill says</th><th>What to check first</th></tr></thead><tbody><tr><td><code>pg fail</code></td><td><code>pgbackrest --stanza=openg2p info</code> — is the stanza present? <code>archive_command</code> still set? PG running?</td></tr><tr><td><code>etcd fail</code></td><td>Is RKE2 running on compute? <code>ls -la /var/lib/rancher/rke2/server/db/snapshots/</code> on compute — is the latest snapshot recent? On backup host: <code>ls -la /var/lib/openg2p-backup/etcd/</code>. Run <code>./openg2p-backup.sh run --config backup-config.yaml --component etcd</code> to pull. Verify output shows compute fallback if distro <code>etcd-client</code> is incompatible.</td></tr><tr><td><code>rancher fail</code></td><td><code>kubectl get backup.resources.cattle.io -A</code> — did last backup succeed? <code>ls -la /srv/nfs/&lt;cluster&gt;/rancher-backup/</code> on storage — are <code>*.tar.gz.enc</code> files present? Re-run <code>./openg2p-backup.sh install --config backup-config.yaml --component rancher</code> if the static PV is missing.</td></tr><tr><td><code>nfs fail</code></td><td>Is the RO mount healthy? <code>mountpoint /mnt/openg2p-nfs-ro</code> (or <code>-dr</code> fallback). <code>restic snapshots --tag nfs</code> — do data snapshots exist (not only <code>pvc-manifest</code>)?</td></tr><tr><td><code>configs fail</code></td><td><code>restic snapshots --tag wireguard</code> (etc.) in the configs repo; SSH to RP/compute still works?</td></tr><tr><td><code>objectstore fail</code></td><td>Is <code>groups.objectstore: true</code>? rclone remote healthy? <code>restic snapshots</code> in the objectstore repo?</td></tr></tbody></table>

When a drill fails, run the corresponding `verify` subcommand by hand to get more detail:

```bash
./openg2p-backup.sh verify --config backup-config.yaml --component pg
```

## Quarterly: full DR rehearsal

Drills exercise the per-component restore paths. They do **not** rehearse the full "cluster is gone, build a new one and bring everything back" runbook. Schedule that quarterly. Procedure: provision a fresh sandbox VPC, run `openg2p-aws-provision.sh` then `openg2p-prod.sh`, then follow the [Full rebuild](restoration/full-rebuild.md) runbook to layer backups onto it. Time the end-to-end. Update the runbook if you find friction.
