---
description: Weekly automated drill — verify + dry-run-restore + canary checks across every enabled backup group.
---

# Drills

Backups you don't test aren't backups. The orchestrator's `drill` subcommand runs a weekly verify + dry-run-restore for every enabled group and aggregates the results into a single status file. Cron schedules this for Sunday 05:00 by default — after the night's PG, NFS, and configs runs have completed.

## What each component's drill does

| Group | Drill steps |
|---|---|
| **pg** | `pgbackrest verify` → restore latest full into `/var/lib/openg2p-backup-restore/drill-pg-<timestamp>` on storage → if `pg.canary_table` is set, start a temporary Postgres on port 55432 and run `SELECT count(*) FROM <canary_table>` → tear down |
| **etcd** | `etcdutl --write-out=table snapshot status <latest>` — verifies snapshot file isn't truncated/corrupt |
| **rancher** | Spawns a busybox pod mounting the backup PVC, `tar -tzf` the latest tarball to confirm it lists expected GVKs |
| **nfs** | `restic check --read-data-subset=5%` on the NFS repo → `restic restore` of the canary file (`.pvc-mapping.yaml`) into a tempdir |
| **configs** | `restic check --read-data-subset=5%` on the configs repo → `restic restore` of the smallest tagged snapshot (the `openg2p` tag) into a tempdir |

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
    "configs": { ... }
  }
}
```

`./openg2p-backup.sh status --config backup-config.yaml` reads this file via the backup host and tabulates it.

## Reading the results

| Result | Meaning |
|---|---|
| `ok` | Drill passed. Backups are restorable. |
| `fail` | At least one step in the drill failed. **Investigate before the next run.** Common causes: pgBackRest stanza dropped (e.g. PG was reinstalled), restic repo password file modified, etcd snapshot file truncated. |
| `disabled` | The group is disabled in `backup-config.yaml`. No drill runs. |
| `-` | The drill has never run for this group (fresh install). |

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
* **Encryption key rotation** — drills don't test that you can decrypt with a *new* key. Plan key rotation as a separate exercise.

## Common failure modes and what to check

| Drill says | What to check first |
|---|---|
| `pg fail` | `pgbackrest --stanza=openg2p info` — is the stanza present? `archive_command` still set? PG running? |
| `etcd fail` | Is RKE2 actually running on compute? `ls -la /var/lib/rancher/rke2/server/db/snapshots/` on compute — is the latest snapshot recent? |
| `rancher fail` | `kubectl get backup.resources.cattle.io -A` — did last backup succeed? Is the PVC bound? |
| `nfs fail` | `mount | grep openg2p-nfs-ro` on backup host — is the read-only mount alive? Storage NFS export still permits backup-host's IP? |
| `configs fail` | `restic -r /var/lib/openg2p-backup/restic/configs snapshots` on backup host — does it list any snapshots at all? Streaming SSH from RP/compute may have failed. |

When a drill fails, run the corresponding `verify` subcommand by hand to get more detail:

```bash
./openg2p-backup.sh verify --config backup-config.yaml --component pg
```

## Quarterly: full DR rehearsal

Drills exercise the per-component restore paths. They do **not** rehearse the full "cluster is gone, build a new one and bring everything back" runbook. Schedule that quarterly. Procedure: provision a fresh sandbox VPC, run `openg2p-aws-provision.sh` then `openg2p-prod.sh`, then follow the [Full rebuild](restoration/full-rebuild.md) runbook to layer backups onto it. Time the end-to-end. Update the runbook if you find friction.
