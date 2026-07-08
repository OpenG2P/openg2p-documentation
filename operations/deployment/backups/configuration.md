---
description: Reference for backup-config.yaml — every key, default, and what changing it does.
---

# Configuration

The orchestrator reads two YAML files: `backup-config.yaml` (your preferences) and the cluster's `prod-config.yaml` (referenced by the `prod_config:` key, gives SSH details for the 3 production nodes). The example file at `automation/backups/backup-config.example.yaml` is the source of truth for the schema.

## Top-level keys

### `prod_config`

Path to the production `prod-config.yaml`. Relative paths resolve against the `automation/backups/` directory. Default: `../production/prod-config.yaml`.

### `backup_*` (host details)

`backup_private_ip`, `backup_ssh_host`, `backup_ssh_user`, `backup_ssh_key`. If `backup_ssh_host` is blank, falls back to `backup_private_ip`. When `aws-provision` runs with `backup_node.enabled: true`, these are written into `provision-output.yaml` automatically.

### `backup_repo_root`

Where every repo lives on the backup host. Default `/var/lib/openg2p-backup` — matches the cloud-init mount point of the dedicated EBS data volume. Change this only if you want repos somewhere else (e.g. a custom block storage path on a non-AWS install).

## Encryption — passphrase files

```yaml
restic_passphrase_file:     "~/.openg2p/keystore/restic.pass"
pgbackrest_passphrase_file: "~/.openg2p/keystore/pgbackrest.pass"
etcd_at_rest_key_file:      "~/.openg2p/keystore/etcd-aescbc.key"
```

`~` is expanded to the operator's home. If a file is empty/missing at install time, the orchestrator generates a random passphrase and writes it back. **You must then move that file into your p12 keystore** — the automation prints a reminder.

## Group toggles

```yaml
groups:
  pg:       true
  etcd:     true
  rancher:  true
  nfs:      true
  configs:  true
```

Each group is independently switchable. Disabling a group:
* Skips its install steps
* Comments out its cron entries on the backup host
* Causes `run`/`verify`/`drill` to skip it
* Reports it as `disabled` in `status` output

You can disable a group later by editing `backup-config.yaml` and re-running `install` — the orchestrator regenerates the cron file.

## Retention

```yaml
retention:
  pg_full_count:      4        # keep 4 fulls (~4 weeks rolling)
  pg_diff_count:      7        # keep 7 differentials
  pg_wal_days:        30       # WAL archive retention (PITR window)
  etcd_snapshot_count: 28      # ~7 days at 6-hourly
  rancher_backup_count: 14     # 14 nightly tarballs
  keep_daily:   7              # restic
  keep_weekly:  4              # restic
  keep_monthly: 6              # restic
```

Defaults give roughly 6 months of granular history. Government data-retention policies may require more — increase `keep_monthly` (and ensure the data volume can hold it). The drill (`drill` subcommand) does not touch retention.

## Schedules

```yaml
schedules:
  pg_full:    "0 2 * * 0"
  pg_diff:    "0 2 * * 1-6"
  etcd_pull:  "15 */6 * * *"
  rancher:    "0 3 * * *"        # consumed by the in-cluster Schedule CR
  nfs:        "30 3 * * *"
  configs:    "30 3 * * *"
  drill:      "0 5 * * 0"
```

Standard cron syntax. The orchestrator renders these into `/etc/cron.d/openg2p-backup` on the backup host at install time. Edit the cron file directly to test changes; commit them back to `backup-config.yaml` so the next `install` re-applies them.

The defaults stagger: PG at 02:00, etcd every 6h offset by 15 minutes, rancher and NFS at 03:00–03:30 (rancher writes a tarball that NFS then captures, so order matters), drill on Sunday at 05:00 after Saturday's runs.

**About `schedules.rancher`**: nightly rancher backups are driven by the in-cluster `Schedule` CR (`manifests/rancher-backup-schedule.yaml`), not by a cron entry on the backup host. The `schedules.rancher` value is informational only today — it documents the intended cadence. (Wiring it into the Schedule CR's `.spec.schedule` is a Phase 2 nicety.) Ad-hoc rancher backups can still be triggered from the laptop with `./openg2p-backup.sh run --component rancher`.

## PostgreSQL

```yaml
pg:
  stanza_name: "openg2p"
  parallel_jobs: 4
  archive_timeout_seconds: 60   # bounds the RPO
  canary_table: ""
```

`canary_table`: optional. If set, the weekly drill runs `SELECT count(*) FROM <canary_table>` against the temporarily-restored Postgres to confirm the backup is application-readable, not just byte-readable. Pick a table that is always present and has predictable content (e.g. a `users` table with a known minimum row count).

`archive_timeout_seconds`: how long Postgres waits before forcing a WAL switch. Lower = better RPO but more WAL files. 60s is a good default; under 30s starts wasting space.

## NFS data

```yaml
nfs:
  export_root: "/srv/nfs/openg2p"   # what's mounted on the backup host
  paths: ["."]                      # subdirs to back up; "." = whole export
  exclude:
    - "**/logs/**"
    - "**/tmp/**"
    - "**/.snapshots/**"
```

Use `paths` as an explicit allowlist when you don't want the entire export. The orchestrator's bash YAML parser doesn't natively handle nested arrays — if you need multiple paths, use `nfs.path1`, `nfs.path2` flat keys (the parser handles those):

```yaml
nfs:
  export_root: "/srv/nfs/openg2p"
  path1: "./prod"
  path2: "./shared"
  exclude1: "**/logs/**"
  exclude2: "**/tmp/**"
```

System logs are excluded by default because OpenSearch already retains them.

## ResourceSet

The live `ResourceSet` CR applied at install is `automation/backups/manifests/rancher-backup-resourceset.yaml` in the deployment repo. **Edit that manifest** to change what is captured. At install time, the orchestrator validates each `apiVersion` entry against the live cluster (`kubectl api-resources`) and warns about any unknown API group — it does not fail install if optional operators (cert-manager, Istio, Keycloak, etc.) are not yet deployed.

The operator v8.x CRD uses strict decoding:

* There is **no** top-level `namespaceRegexp` or boolean `controllerReferences` field.
* Namespace scoping is per `resourceSelector` entry (`namespaces` / `namespaceRegexp`, Go RE2 only — no negative lookahead).
* The shipped manifest captures all namespaces for DR completeness; system-namespace objects are small and mostly helmfile-recreatable.

The `resource_set:` block in `backup-config.example.yaml` documents the **intended** policy for operators customizing the manifest — it is not rendered into the CR at install time.

Example selectors (see the manifest for the full list):

```yaml
resourceSelectors:
  - apiVersion: "v1"
    kindsRegexp: "^(secrets|configmaps|namespaces|serviceaccounts|persistentvolumes|persistentvolumeclaims)$"
  - apiVersion: "management.cattle.io/v3"
    kindsRegexp: "."
  - apiVersion: "cert-manager.io/v1"
    kindsRegexp: "."
```

Add custom CRD groups in the manifest if your environment installs additional operators (e.g. `eventing.knative.dev`).

## rancher-backup operator storage

```yaml
rancher:
  pvc_storage_class: "nfs-csi"   # StorageClass used to read NFS server/share
  pvc_size: "50Gi"               # capacity of the static backup PV/PVC
```

The backup-restore-operator writes encrypted tarballs to a PVC mounted at `/var/lib/backups` inside the operator pod. **Do not** set `storageLocation` on `Backup` / `Restore` CRs — the operator only supports explicit `storageLocation` for S3; PVC storage is configured at the Helm chart level.

**Static NFS PV (stable location).** The chart's default dynamic persistence names the PVC `<release>-<helm-revision>`, so every `helm upgrade` provisions a fresh empty volume and strands prior backups. Install therefore:

1. Reads the NFS `server` + `share` from the cluster's `pvc_storage_class` StorageClass.
2. Creates `/srv/nfs/<cluster>/rancher-backup` on the storage node (mode `0777` so the operator pod can write).
3. Applies a static NFS `PersistentVolume` named `openg2p-rancher-backup-store`.
4. Installs the chart with `persistence.enabled=true`, `persistence.storageClass=-` (no dynamic provisioning), and `persistence.volumeName=openg2p-rancher-backup-store`.

Tarballs land at **`/srv/nfs/<cluster>/rancher-backup/`** on the NFS export (captured downstream by the nfs restic job). With `encryptionConfigSecretName` set, files are named `*.tar.gz.enc`.

To re-provision rancher storage after a chart/config change without re-running the full install (which restarts RKE2 for etcd):

```bash
./openg2p-backup.sh install --config backup-config.yaml --component rancher
```

## Etcd encryption-at-rest

```yaml
etcd_encryption:
  enabled: false
```

Default: disabled. To turn it on, run `./openg2p-backup.sh install --enable-secret-encryption` during a maintenance window. This is a separate, deliberate action because it restarts the apiserver. The flag overrides this config key only for that run; flipping the key to `true` does **not** automatically enable encryption — you must pass the CLI flag.

## Tool versions

```yaml
versions:
  pgbackrest: ""                  # blank = use distro package
  restic: "0.17.3"
  # Helm CHART version from charts.rancher.io — scheme <chartVersion>+up<appVersion>.
  # This is the CHART version, NOT the operator app version (there is no plain "7.0.0").
  # 107.1.5+up8.1.5 → Rancher 2.12.x, Kubernetes 1.31–1.33.
  rancher_backup_chart: "107.1.5+up8.1.5"
```

Pinned to known-good versions. Bump after testing in a non-production environment. Choose a `rancher_backup_chart` whose `rancher-version` / `kube-version` annotations match your cluster:

```bash
helm search repo rancher-charts/rancher-backup --versions
```
