---
description: >-
  Backup-node sizing, network, and secret custody requirements before running
  openg2p-backup.sh install.
---

# Prerequisites

## Backup node — hardware

| | Backup node | Note |
|---|---|---|
| **vCPU minimum** | 4 | Hard fail at install. pgBackRest parallelism + restic dedup/encrypt run side-by-side. |
| **RAM minimum** | 8 GB | Hard fail at install. |
| **Root disk minimum** | 64 GB | Hard fail at install. OS, tooling, logs. |
| **Backup data disk** | ≥ 1 TB recommended | **Warn-only.** Smaller disk = shorter retention before pruning kicks in. The script proceeds and tells you how many days of retention to expect. Mounted at `/var/lib/openg2p-backup`. |
| **Disk type** | SSD recommended for repo | HDD acceptable for an archive tier later. |
| **Network** | Private subnet; SSH-reachable from the admin laptop | The bundled AWS provisioning gives it a public IP (SG-locked to the admin CIDR), like Compute/Storage, so the deployer can SSH in to install. On-prem, reach it over the private subnet / VPN instead. SSH inbound also from compute, storage, RP. |
| **OS** | Ubuntu 24.04 LTS | Same as the rest of the platform. |

The script enforces vCPU/RAM/root-disk as hard-fails. The data volume size is **warn-and-continue** — the operator can knowingly run with a smaller volume, accepting reduced retention.

If you provisioned via `openg2p-aws-provision.sh` with `backup_node.enabled: true`, the AWS instance type defaults to `t3a.xlarge` (4 vCPU, 16 GB RAM) with a 1 TB gp3 data volume formatted ext4 and mounted at `/var/lib/openg2p-backup` by cloud-init. See [aws-config.example.yaml](https://github.com/OpenG2P/openg2p-deployment/blob/main/automation/production/aws/aws-config.example.yaml) for tuning.

## Network

Inbound to backup node:

* **TCP 22 (SSH)** from admin laptop CIDR (the orchestrator)
* **TCP 22 (SSH)** from RP, compute, storage SGs (only RP's storage's archive\_command actually uses this — over the same port)

Outbound from backup node:

* **TCP 22 (SSH)** to RP, compute, storage (orchestrating per-component backups)
* **NFS** (TCP 2049 + portmapper) to storage node — backup mounts the NFS export read-only

The storage node's NFS export must permit the backup node's private IP. By default the production install exports to the whole private subnet, which already covers the backup node. If your install has restricted exports, add the backup node's IP to `/etc/exports` on the storage node before running `install`.

## Secret custody

The backup automation needs three passphrases. They are loaded from files on the operator's laptop at install time and shipped to the backup host as mode-0600 files under `/etc/openg2p-backup/`. They are **never** committed to the repository.

| File (laptop)     | Used for                                  | Loss impact                                               |
| ----------------- | ----------------------------------------- | --------------------------------------------------------- |
| `restic.pass`     | restic NFS + configs repos                | NFS data + RP/compute config backups unrecoverable        |
| `pgbackrest.pass` | pgBackRest repo cipher                    | All Postgres backups unrecoverable                        |
| `etcd-aescbc.key` | etcd encryption-at-rest (only if enabled) | Etcd-stored Secrets unrecoverable from restored snapshots |

OpenG2P's convention is to keep these in a per-project [PKCS#12 keystore](https://en.wikipedia.org/wiki/PKCS_12) that the operator maintains separately from the repo. The keystore itself is password-protected. Custody = operator's responsibility; the automation reads file paths and never modifies them.

If a configured passphrase file does not exist when `install` runs, the orchestrator generates a random 32-byte passphrase and writes it to that path with mode 0600. **The operator is then prompted to move it into the keystore.** This is the only safe way to bootstrap on a new install — but it means a hostile process with read access to the laptop while install is running could intercept the passphrase. For maximum control, generate the passphrases yourself and place them at the configured paths before running `install`.

## Production-side prerequisites

The production platform install (`openg2p-prod.sh`) must be **complete** before backups can install. Specifically:

* RKE2 must be running on compute (etcd snapshot config is a `systemctl restart rke2-server` on a working RKE2)
* Postgres must be running on storage (pgBackRest stanza-create needs a live PG)
* NFS export must be active on storage and reachable on the cluster
* Helm + the rancher-charts repo must be available on compute (operator install uses them)

Run `./openg2p-prod.sh --probe --config prod-config.yaml` first to confirm cluster health.

## Backup-config-side prerequisites

The backup orchestrator reads the live cluster's `prod-config.yaml`. Set `prod_config: <path>` in `backup-config.yaml`. Relative paths resolve against the `automation/backups/` directory; the default `../production/prod-config.yaml` matches the standard repo layout.

## Tools required on the operator's laptop

The orchestrator runs on the laptop and needs:

* `bash` 4+ (macOS: `brew install bash`)
* `ssh` + `rsync`
* `aws-cli` v2 (only for the optional AWS provisioning step)

The backup host gets `pgbackrest`, `restic`, `nfs-common`, `jq`, `curl`, `etcd-client` apt-installed automatically by `roles/backup-host/install.sh`.

## What does not need to be done

* No customer DNS changes (the backup node gets a public IP for SSH, but no public DNS hostname)
* No TLS certificate procurement (backup node's only inbound port is SSH)
* No Wireguard peer config for the backup node — the deployer reaches it by SSH (its public IP on the AWS path, SG-restricted to the admin CIDR; or over the private subnet / VPN on-prem)
