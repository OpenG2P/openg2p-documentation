---
description: Day-to-day backup operations — install, run, verify, list, status, group toggling.
---

# Operations

The orchestrator is `automation/backups/openg2p-backup.sh`. Every subcommand takes `--config backup-config.yaml`. Most also accept `--component <name>` to target a single group.

## Subcommands

```
./openg2p-backup.sh install     # one-time bootstrap
./openg2p-backup.sh run         # execute backups now (also used by cron)
./openg2p-backup.sh verify      # cheap integrity checks, no restore
./openg2p-backup.sh drill       # weekly drill (verify + dry-run-restore)
./openg2p-backup.sh list        # what's in each repo
./openg2p-backup.sh restore     # see Restoration page
./openg2p-backup.sh status      # last-run + last-drill state
./openg2p-backup.sh help
```

## install

```bash
# Full bootstrap (all enabled groups + cron)
./openg2p-backup.sh install --config backup-config.yaml

# Re-run a single group's install steps (e.g. after changing rancher storage)
./openg2p-backup.sh install --config backup-config.yaml --component rancher
```

`--component` is supported for `install` as well as `run` / `verify` / `list`. Per-group install skips the other groups — useful when re-provisioning rancher storage without triggering `etcd_install`'s `rke2-server` restart. Steps 1–4 (SSH probes, backup-host bootstrap, cron) still run on every `install` invocation.

What it does, in order:

1. **SSH probes** for backup, plus production nodes touched by enabled groups.
2. **Backup-host preflight** — Ubuntu version, CPU (≥4, hard), RAM (≥8 GB, hard), root disk (≥64 GB, hard), repo data volume (≥1 TB, **warn-only**).
3. **Passphrase resolution** — reads each `*_passphrase_file` from the keystore. Generates if missing (with a banner reminder to move into the keystore).
4. **Backup-host bootstrap** — apt installs, repo dirs, lib files pushed to `/opt/openg2p-backup/`, SSH key generated for orchestrating compute/storage/RP, authorized on those nodes, wrapper scripts (`/usr/local/bin/openg2p-backup-{run,drill,status}`) installed.
5. **Per-group install** — gated by `groups.<name>` toggle and `--component` (when not `all`):
   * `pg`: pgBackRest on backup + storage, archive_command on PG, stanza-create, first full backup
   * `etcd`: RKE2 snapshot schedule, rsync-pull SSH trust
   * `rancher`: rancher-backup operator (chart `107.1.5+up8.1.5` default), static NFS PV `openg2p-rancher-backup-store`, encryption Secret, ResourceSet + in-cluster Schedule CR
   * `nfs`: storage-node NFS export + `ufw` allow for backup host, read-only NFS mount on backup host, restic repo init
   * `configs`: restic repo for configs
6. **Optional encryption-at-rest** — only if `--enable-secret-encryption` flag is passed. Restarts kube-apiserver.
7. **Cron deploy** — renders `cron.template` with active schedules, installs at `/etc/cron.d/openg2p-backup`.

`install` is **idempotent** — re-running it is safe and skips completed steps via state markers. Pass `--force` to re-run all steps.

```bash
# Example: turn on backup automation, but skip the first full PG backup
# (run later when load is low)
./openg2p-backup.sh install --config backup-config.yaml
# ...the install will pause and run an initial pgbackrest full. To skip:
# disable pg in backup-config.yaml, install, then re-enable and re-install.
```

## run

```bash
# All enabled groups
./openg2p-backup.sh run --config backup-config.yaml

# Just one
./openg2p-backup.sh run --config backup-config.yaml --component pg
```

Used by cron on the backup host (via the wrapper `openg2p-backup-run <group>`). PG honors `PGBR_TYPE=full|diff` — the cron file passes `full` on Sundays and `diff` other days.

If a group is disabled in config, `run --component <that-group>` exits with a warning rather than failing.

Failures don't stop other groups — `run` attempts every enabled group and surfaces per-group results in the status file.

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

Run after a restore drill or a suspected hardware issue. Cheap enough to run nightly if you want extra paranoia.

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
* **nfs / configs** → `restic snapshots --compact`

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
GROUP      STATE      LAST-RUN               RESULT     LAST-DRILL             RESULT
---------- ---------- ---------------------- ---------- ---------------------- --------
pg         enabled    2026-04-27T02:00:01Z   ok         2026-04-27T05:00:09Z   ok
etcd       enabled    2026-04-27T18:15:00Z   ok         2026-04-27T05:00:14Z   ok
rancher    enabled    2026-04-27T03:00:02Z   ok         2026-04-27T05:00:18Z   ok
nfs        enabled    2026-04-27T03:30:11Z   ok         2026-04-27T05:00:35Z   ok
configs    enabled    2026-04-27T03:30:14Z   ok         2026-04-27T05:00:42Z   ok
```

Disabled groups show `disabled` and dashes. The Phase 2 alerting layer reads the same JSON file directly — see [Alerting](alerting.md).

## Group toggles

Edit `backup-config.yaml`:

```yaml
groups:
  pg:       true
  etcd:     true
  rancher:  true
  nfs:      false   # ← disabled
  configs:  true
```

Re-run `install` to apply. The cron file is regenerated and the disabled group's lines are commented out (kept for reference).

## Forcing a re-run / resetting state

`install` uses state markers under `automation/backups/.state/` (laptop side) and `/var/lib/openg2p/deploy-state/` (remote side). `--force` ignores them:

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

Laptop-side log: `automation/backups/logs/openg2p-backup-<timestamp>.log` (one per orchestrator invocation).
Backup-host cron log: `/var/log/openg2p-backup.log` on the backup host.
