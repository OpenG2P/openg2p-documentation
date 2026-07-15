---
description: Tool choices for the backup automation, and what is deliberately not used.
---

# Architecture

The backup stack is a hybrid of well-established tools, glued together by a thin orchestrator script. We delegate everything that touches actual data bytes — WAL replay, deduplication, compression, encryption, PITR — to tools that have been beaten on by thousands of ops teams. The custom code is limited to: config parsing, SSH orchestration, cron rendering, and the drill harness.

## Topology

```
        ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
        │ Reverse Proxy│    │   Compute    │    │   Storage    │    │    Backup    │
        │  (RP node)   │    │   (RKE2)     │    │ (NFS + PG)   │    │   (4th node) │
        ├──────────────┤    ├──────────────┤    ├──────────────┤    ├──────────────┤
        │ wireguard    │    │ etcd snap    │    │ postgres     │    │ pgBackRest   │
        │ nginx        │    │ rancher-     │    │ NFS export   │    │   repo host  │
        │ local CA     │    │  backup CR   │    │ pgbackrest   │    │ restic repos │
        │              │    │ rke2 TLS     │    │  (client)    │    │ etcd archive │
        │              │    │  state       │    │              │    │ cron         │
        └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
               │                   │                    │                    │
               │  tar over SSH     │ rsync pull         │ pgbackrest         │
               └───────────────────┴────────────────────┴────────────────────┘
                                      pull-based, encrypted
```

Pull-based — the backup node SSHes outward to the production nodes, never the other way around. A compromised production node can't reach back and erase its own backups.

Remote commands run under `sudo bash -lc` with `TERM=dumb` so login-shell profile hooks (`clear_console`, etc.) do not pollute captured stdout over non-interactive SSH.

## Tools and why each is here

### pgBackRest — PostgreSQL

**Why this and not `pg_dump`:** dumps are point-in-time only; recovery loses every transaction since the dump. We need WAL streaming for ~1-minute RPO. pgBackRest does WAL archiving, parallel full/diff, native compression, AES-256 repo encryption, and restore with PITR (`--type=time --target=...`).

**Why this and not Barman:** both work. pgBackRest's config is simpler for our shape (one stanza, one repo host, no separate `barman` user vs. `postgres` SSH key dance), and parallel WAL push is built in.

[User guide](https://pgbackrest.org/user-guide.html) · [Command reference](https://pgbackrest.org/command.html)

### RKE2 built-in `etcd-snapshot` — etcd

**Why built-in and not external:** RKE2 already has the snapshot mechanism, schedule, and cluster-reset-from-snapshot path. Adding etcdctl-based jobs would duplicate that and risk drift. We just configure the schedule (`etcd-snapshot-schedule-cron`) and rsync-pull the resulting files.

[Backup and restore](https://docs.rke2.io/backup_restore)

### rancher-backup operator — Kubernetes resources

**Why this and not Velero:** Velero needs an always-on S3-compatible store for its primary workflow. Volume snapshots are not our main gap — we handle PVC bytes via restic on the NFS export. Opt-in MinIO/S3 *content* backup (when an environment runs object storage) is a separate `objectstore` group using rclone + restic onto the backup host. rancher-backup does what we need for Kubernetes API objects: a curated `ResourceSet` of GVKs, encrypted tarball output, schedules. Despite the "rancher-" name, it backs up arbitrary GVKs — we use it for Secrets, ConfigMaps, PV/PVCs, and curated CRD groups (cert-manager, monitoring, Istio, Keycloak, Logging) in addition to Rancher's own state.

**Storage model:** The operator writes to a PVC mounted at `/var/lib/backups` inside its pod. We provision a **static NFS PV** (`openg2p-rancher-backup-store`) bound to `/srv/nfs/<cluster>/rancher-backup` on the storage export — not dynamic per-helm-revision PVCs (which rotate empty on every `helm upgrade`). `Backup` / `Restore` CRs omit `storageLocation` (the operator only supports explicit S3 there). Tarballs are AES-encrypted (`*.tar.gz.enc`) via an `encryptionConfigSecretName` Secret applied at install.

[Backup-restore-operator](https://github.com/rancher/backup-restore-operator) · [Rancher docs](https://ranchermanager.docs.rancher.com/integrations-in-rancher/backup-restore-and-disaster-recovery)

### restic — NFS data and config files

**Why this and not borg/duplicity:** single Go binary (air-gap friendly), encrypted-by-default, content-addressed dedup, supports backup from stdin (we use this for SSH-tar streams of remote config dirs). restic's local-filesystem repo backend works fine without S3.

The NFS export is mounted **read-only** on the backup host — a compromised backup process cannot accidentally write into the live NFS volume.

[Documentation](https://restic.readthedocs.io/)

### rclone + restic — object store (opt-in)

When `groups.objectstore: true`, the backup host mounts a MinIO/S3 remote **read-only** with rclone and takes an encrypted restic snapshot into `$backup_repo_root/objectstore-restic`. This backs *up* object-store contents onto the backup volume; it is not Velero and not an offsite replica by itself.

[rclone](https://rclone.org/docs/) · [restic](https://restic.readthedocs.io/)

### Sidecar PVC manifest — UUID → app mapping

NFS data is stored under directories named after the PV's CSI `subdir` or native NFS path (e.g. `cattle-resources-system-<pvc>-<pv-uuid>` under `/srv/nfs/<cluster>/` on the `nfs-csi` StorageClass). On its own, restic just sees opaque dirs. Each backup run writes a sidecar YAML manifest (`<repo>/nfs/.pvc-mapping.yaml`) joining `kubectl get pv -o json` against the live NFS file listing. The jq filter matches both native NFS PVs (`spec.nfs.path`) and CSI PVs (`spec.csi.volumeAttributes.subdir` / reconstructed `<namespace>-<pvc>-<pv>` names), so restore knows which directory belongs to which `(namespace, pvc, app)` triple.

## Tools we considered and rejected

| Tool | Why not |
|---|---|
| Velero | Primary workflow needs S3; heavier than rancher-backup + NFS restic for our topology |
| Barman | Functionally equivalent to pgBackRest; less ergonomic for our SSH-pull setup |
| etcdctl scheduled snapshots | Duplicates RKE2's built-in mechanism |
| Hand-rolled `kubectl get -o yaml` | Doesn't strip managed fields cleanly, no restore tooling |
| K10 / commercial backup | Out of scope for OpenG2P open-source baseline |

## Where custom code is

`automation/backups/` in the deployment repo:

* `openg2p-backup.sh` — orchestrator (subcommand dispatch, install, restore, wal-health, daily-report)
* `lib/utils.sh` — sources the production lib's logger, cfg parser, ssh helpers; adds group toggles, status JSON, passphrase resolution, backup-host preflight
* `lib/{pgbackrest,etcd,rancher,nfs,configs,objectstore,restic,drills}.sh` — per-group lifecycle (install / run / verify / list / restore / drill)
* `lib/{metrics,notify,wal_health}.sh` — Prometheus textfile / optional Pushgateway, SMTP notify, independent WAL probe
* `manifests/prometheusrule-backup.yaml.template` — applied into `cattle-monitoring-system` at install
* `roles/storage/configure-pg.sh` — runs on storage node to configure pgBackRest client + WAL archiving
* `roles/backup-host/install.sh` + `cron.template` — bootstrap on the 4th node (includes wal-health + daily-report + objectstore cron lines)

Everything that touches data bytes is still delegated to pgBackRest / restic / rclone / rancher-backup / RKE2.

## Where keys live

The operator's [p12 keystore](prerequisites.md#secret-custody) holds:

1. `restic.pass` — passphrase for both NFS and configs restic repos (one passphrase, two repos)
2. `pgbackrest.pass` — pgBackRest repo cipher passphrase
3. `etcd-aescbc.key` — etcd encryption-at-rest key (only if encryption is enabled)
4. (Optional) `smtp.env` — SMTP settings for operator email ([Alerting](alerting.md))
5. (Optional) `rclone.conf` + `objectstore-restic.pass` — when `groups.objectstore` is enabled

These are pushed to the backup host at install time as mode-0600 files under `/etc/openg2p-backup/` (except rclone/objectstore only when that group is enabled). The orchestrator never commits them to the repo. Losing restic/pgBackRest passphrases renders the corresponding backups unrecoverable — same custody model as TLS keys for the platform.
