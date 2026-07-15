---
description: Per-component table of what is backed up, plus the rationale for what is lost vs. recreated when you re-run the production automation.
---

# What gets backed up

## The table

| Layer | Tool | Source → Repo | Schedule (default) | Retention (default) |
|---|---|---|---|---|
| PostgreSQL | pgBackRest | storage → backup (SSH) | full Sun 02:00, diff Mon-Sat 02:00, **WAL streaming continuous** | 4 full + 7 diff + 30 days WAL |
| etcd snapshots | RKE2 built-in + rsync | compute → backup | every 6h | 28 snapshots (~7 days) |
| Kubernetes resources | rancher-backup operator | static NFS PV → `/srv/nfs/<cluster>/rancher-backup` (`*.tar.gz.enc`) → restic via NFS | nightly 03:00 (in-cluster Schedule CR) | 14 days (operator) + restic retention downstream |
| NFS data | restic | NFS export RO mount → backup | nightly 03:30 | 7 daily + 4 weekly + 6 monthly |
| Wireguard config | restic over SSH-tar | RP `/etc/wireguard` → backup | nightly 03:30 | same as NFS |
| Nginx config | restic over SSH-tar | RP `/etc/nginx` → backup | nightly 03:30 | same as NFS |
| Local CA + dnsmasq | restic over SSH-tar | RP `/etc/openg2p` → backup | nightly 03:30 | same as NFS |
| RKE2 TLS material | restic over SSH-tar | compute `/var/lib/rancher/rke2/server/tls` | nightly 03:30 | same as NFS |
| RKE2 cred (incl. encryption-config) | restic over SSH-tar | compute `/var/lib/rancher/rke2/server/cred` | nightly 03:30 | same as NFS |
| RKE2 server token | restic over SSH-tar | compute `/var/lib/rancher/rke2/server/token` | nightly 03:30 | same as NFS |
| RKE2 config | restic over SSH-tar | compute `/etc/rancher/rke2` | nightly 03:30 | same as NFS |
| Object store (opt-in) | rclone RO mount + restic | MinIO/S3 → backup `objectstore-restic` | nightly 04:00 | 7 daily + 4 weekly (configurable) |
| WAL health (not a backup) | probe → metrics | storage `pg_wal` + `pg_stat_archiver` | every 5m | n/a — alerting only |

## What survives a fresh `openg2p-prod.sh` install

These are **not lost** when you re-run the production automation, because they're defined in code or recreated by Helm:

* All Helm-managed Deployments, Services, base ConfigMaps, ServiceAccounts, default RBAC
* Istio mesh configuration
* Monitoring + logging stack base configs
* CRD schemas themselves (re-installed by their charts)
* Operators (cert-manager, Rancher, etc.)

## What is lost — and therefore needs explicit backup

### Secrets, all namespaces

Secrets contain runtime-generated material that helmfile cannot recreate:

* TLS certificates issued by cert-manager
* Registry pull credentials
* Randomly generated DB passwords
* JWT signing keys
* ServiceAccount tokens that other services trust
* Rancher's bootstrap secret
* Keycloak admin password Secret
* **Helm release Secrets** (`sh.helm.release.v1.*`) — losing these means Helm thinks nothing is installed

Captured by: `rancher-backup` ResourceSet (resource type `secrets`, all namespaces except kube-system / kube-public / kube-node-lease).

### CRD instances created at runtime

* **Rancher**: `clusters.management.cattle.io`, `users.management.cattle.io`, RBAC bindings, GitOps repos, the Keycloak SAML auth provider config
* **cert-manager**: `Certificate`, `Issuer`, `ClusterIssuer` CRs (these regenerate Secrets, but only if `Issuer` config is intact)
* **Istio**: `VirtualService`, `Gateway`, `AuthorizationPolicy`, `PeerAuthentication`
* **Monitoring**: user-added `PrometheusRule`, `ServiceMonitor`
* **Keycloak operator**: realms, clients (when using the operator pattern)
* **Logging**: outputs and flows added beyond defaults

Captured by: `rancher-backup` ResourceSet (curated CR groups in `manifests/rancher-backup-resourceset.yaml`).

### PersistentVolume + PersistentVolumeClaim objects

Critical — these hold the binding between a UUID directory on NFS and the namespace/pod/app that owns it. Without these, restic's restored NFS folders are orphan UUIDs.

Captured by: `rancher-backup` ResourceSet (`persistentvolumes`, `persistentvolumeclaims`) **plus** the NFS sidecar manifest (`.pvc-mapping.yaml`) generated nightly. The sidecar adds a human-readable record of `nfs_path → (namespace, pvc, size, storage_class, app_label)` for every directory on the export, including CSI-provisioned subdirs from the `nfs-csi` StorageClass, so an operator can answer "what's in `cattle-resources-system-myapp-pvc-abc…`?" without booting a cluster.

### ConfigMaps that operators mutate

Some operators write status/state into a ConfigMap that the chart originally created empty. Hard to enumerate; safer to back up all CMs and let restore be selective.

Captured by: `rancher-backup` ResourceSet (`configmaps`).

### Application data inside PersistentVolumes

The actual bytes that apps write — Postgres on Keycloak's PVC (when Keycloak uses an embedded DB; OpenG2P uses the host PG, so this matters less for Keycloak), MinIO data if any environment installs MinIO, uploaded files, theme assets.

Captured by: `restic` on the NFS export. Excludes `**/logs/**` and `**/tmp/**` by default.

### Object store buckets (opt-in)

When an environment exposes MinIO/S3 over the S3 API (not only as NFS-backed PVCs) and `groups.objectstore: true`, bucket contents are snapshotted via rclone + restic onto the backup host. Leave the group disabled if you have no object store or already protect it elsewhere.

### Compute-node filesystem state — separate from etcd

A bare etcd snapshot is **not enough** to bring the cluster back, because:

| Path | Why it must be backed up |
|---|---|
| `/var/lib/rancher/rke2/server/tls/` | The cluster CA. Etcd contents reference certs signed by this CA; restoring etcd onto fresh RKE2 with a *new* CA produces a cluster where every kubelet, controller, and webhook is rejected. |
| `/var/lib/rancher/rke2/server/cred/encryption-config.json` | If etcd encryption-at-rest is enabled, this is the key. Without it, restored Secrets decrypt to garbage. |
| `/var/lib/rancher/rke2/server/token`, `node-token` | Cluster-join secrets for adding agents/additional servers. |
| `/etc/rancher/rke2/config.yaml`, `registries.yaml` | Install-time config. Recreatable from `prod-config.yaml` but worth capturing for fidelity. |

Captured by: `restic` over SSH-tar (configs group).

### RP-node config files

| Path | Why |
|---|---|
| `/etc/wireguard/` | `wg0.conf` plus peer pubkeys — the operator-distributed admin VPN config |
| `/etc/nginx/` | TLS terminator vhosts, includes — recreatable from prod-config but breaks if you've hand-edited |
| `/etc/openg2p/` | Local CA cert + key, dnsmasq config, openg2p state |

Captured by: `restic` over SSH-tar (configs group).

## Application data NOT in this scope

* **Pod-internal scratch state** — anything written to `emptyDir`, container filesystem, or a PVC explicitly excluded in `nfs.exclude` is gone on pod restart. By design.
* **System logs** — the platform pipes these to OpenSearch already. Backing them up here would duplicate.
* **Cluster Prometheus metrics** — the platform's monitoring stack stores these. Restoring metrics is out of scope; recreate from a fresh time window after restore.

## Two restore scenarios, two restore paths

The backup set above is dual-purpose:

**Scenario A — same cluster, control-plane crash or etcd corruption.**
You don't want to re-run helmfile; you want this exact cluster back. Restore path: reinstall the RKE2 binary, restore the `tls/` and `cred/` dirs, run `rke2 server --cluster-reset --cluster-reset-restore-path=<snapshot>`. See [Etcd in-place restore](restoration/etcd-in-place.md).

**Scenario B — full rebuild on fresh nodes.**
Run `openg2p-prod.sh install` to recreate the base platform, then layer the resource-level backup on top. See [Full rebuild](restoration/full-rebuild.md).

PG and NFS data restores are common to both scenarios.
