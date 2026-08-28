---
description: >-
  Production deployment automation — one orchestrator script that drives a
  Reverse Proxy, Compute (Kubernetes), and Storage node from the admin's laptop,
  with optional AWS provisioning.
---

# Infrastructure Automation

The production automation provisions the OpenG2P platform across three role-specialised Ubuntu 24.04 VMs — Reverse Proxy, Compute, and Storage — from your laptop, with a single command. (The fourth node, **Backup**, is required for production and is set up by the separate [backup automation](../../backups/).) It is the production counterpart to [Single-Node Automation](../single-node-automation/): same logging, same idempotency, same general structure, but split across role-specialised machines.

<figure><img src="../../../../.gitbook/assets/Deployment Architecture - Three Node.jpg" alt=""><figcaption><p>The three platform VMs this automation provisions — Reverse Proxy, Compute (Kubernetes), and Storage (the Backup node is set up separately)</p></figcaption></figure>

{% hint style="info" %}
**Production deployment flow:** [1. Procurement](../../prerequisites-procurement.md) → [2. Provisioning](../provisioning.md) → **3. Infrastructure** (this page) → [4. Environment](../../environment-setup-multi-node.md) → [5. Modules](../../environment-setup-multi-node.md#next-install-your-openg2p-modules)
{% endhint %}

**Where you are in the flow.** You arrive at this stage with three Ubuntu VMs running and reachable (Stage 2 complete), DNS records and the TLS certificate ready, and SSH+sudo access from the deployer's workstation (Stage 1 complete). After this stage, the platform — Kubernetes, Rancher (local auth), the Wireguard endpoint, Nginx with TLS — is up, and **environment scaffolding** (namespace, Rancher Project, Istio Gateway, external-PG secret, Helm repos) is in place. **Commons** (`openg2p-commons-base` + `openg2p-commons-services`) is installed separately — from the **Rancher UI only**; see [Stage 4 — Environment](../../environment-setup-multi-node.md).

{% hint style="success" %}
**Just want to run it?** Jump straight to [How to use the script](./#how-to-use-the-script). The sections above it explain the architecture (also covered in [OpenG2P Deployment Architecture](../../../../deployment/openg2p-deployment-model.md)) and the prerequisites you must have in place first.
{% endhint %}

{% hint style="info" %}
The source code lives in the [`openg2p-deployment`](https://github.com/OpenG2P/openg2p-deployment) repository under `automation/production/`. The optional AWS provisioning lives at `automation/production/aws/`.
{% endhint %}

## How it works (in brief)

Three role-specialised VMs — **Reverse Proxy** (Nginx + Wireguard), **Compute** (RKE2 Kubernetes + Istio + Rancher + monitoring + logging), and **Storage** (NFS + host PostgreSQL). Admin tools (Rancher) are reached only over the Wireguard VPN (the **private channel**); citizen-facing services use the **public channel**. For the architecture detail, see [Deployment Architecture → Production — Minimum](../../../../deployment/openg2p-deployment-model.md#production-minimum) and [Channel separation](../../../../deployment/openg2p-deployment-model.md#channel-separation-public-vs-private-access).

**What gets installed and configured:**

* RKE2 single-control-plane Kubernetes, Istio, Rancher (cluster manager, **local authentication**), Prometheus + Grafana, OpenTelemetry + Grafana Loki (cluster-wide logging) — all on the Compute node via Helmfile.
* Rancher uses local auth — admins are created directly in Rancher (no SSO). The OpenG2P apps' Keycloak is installed separately, per environment.
* Wireguard VPN server + N peer configs on the RP; Nginx admin server blocks bound to the RP's private IP using **customer-supplied TLS certs** (validated locally before push); firewall keeps admin 443 off the public internet.
* NFS server + host PostgreSQL 16 on the Storage node.
* **One OpenG2P environment scaffolding** (default name `prod`) — namespace, Rancher Project, Istio Gateway, OpenG2P Helm repos registered in Rancher (`openg2p` + `openg2p-gitlab`), and the external-PostgreSQL secret. On by default; toggle with `install_environment`. **Commons charts are not installed here** — install them from the **Rancher UI only**. See [The environment stage](./#the-environment-stage).

**What it does NOT do (yet):** Commons Helm install (**Rancher UI only**), product modules (Registry, PBMS, SPAR, G2P Bridge — install those via their own Helm charts after Commons is up), citizen-facing public hostnames and certs (opening public 80/443 is a separate step), local Docker registry, local Git, air-gap operation, backup automation. See [Reference → Out of scope](./#out-of-scope).

**Two things to know before running:**

* **Idempotent & resumable** — each node records completed steps in `/var/lib/openg2p/deploy-state/*.done`; re-running skips done steps. `--force` re-runs everything.
* **Two config files** — you author `prod-config.yaml`; the AWS provisioner writes `provision-output.yaml` next to it (IPs, SSH paths), auto-loaded as an overlay whose keys win. For non-AWS, fill the `[AWS]`-tagged fields in `prod-config.yaml` yourself.

## Prerequisites

All prerequisites — compute, DNS, TLS certificate, server access, firewall — are listed on the [**Prerequisites & Procurement**](../../prerequisites-procurement.md) page. Everything in that checklist must be in place before you run the install. Two install-time specifics not in the procurement page:

* **Operator's workstation** must have the required tooling installed — bash 4+, ssh, rsync, openssl, git, and (for the post-install login) a Wireguard client. See [**Operator's workstation**](../provisioning.md#operators-workstation) on the Provisioning page for the canonical list, supported OSes (Linux / macOS / WSL2), and per-OS install commands.
* **Single-NIC RP** is the only supported topology — channel separation is enforced by the firewall + Nginx allowlist, not by physical interfaces. Existing two-NIC RPs should leave the secondary detached.

## Validate before you install

Verify everything's in order without touching the nodes:

```bash
./openg2p-prod.sh --validate-certs --config prod-config.yaml   # cert files on your laptop
./openg2p-prod.sh --preflight      --config prod-config.yaml   # nodes (resources, IPs, DNS)
```

Preflight is non-destructive. Run until everything reports green, then proceed to [How to use the script](./#how-to-use-the-script). Typical failures and where to fix them:

| Preflight error                                                       | Fix                                                                                                      |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `IP <rp_private_ip> NOT bound on this host`                           | The configured `rp_private_ip` isn't on any local NIC — fix the value or the NIC                         |
| `DNS: rancher.<domain> does not resolve`                              | Add the A-record (see [DNS records](../../prerequisites-procurement.md#dns-records))                     |
| `DNS: rancher.<domain> resolves to 1.2.3.4 but RP private is 5.6.7.8` | DNS points at the wrong IP — fix the A-record                                                            |
| `Cert ./certs/rancher.pem: does not cover hostname rancher.<domain>`  | Wrong cert for that hostname (see [TLS certificate](../../prerequisites-procurement.md#tls-certificate)) |
| `Cert ./certs/rancher.pem: key does not match cert`                   | Mismatched cert/key pair                                                                                 |
| `RAM: 3 GB (need ≥4)`                                                 | Resize the VM (see [Compute](../../prerequisites-procurement.md#compute-the-four-vms))                   |

## How to use the script

### Step 0 (optional) — provision the VMs on AWS

If you don't already have three Ubuntu VMs, the bundled AWS provisioning creates them for you. Follow [**AWS Provisioning**](aws-provisioning.md), then return here for Step 1.

If you have your own VMs (other clouds, on-prem, manual EC2), skip to step 1.

### Step 1 — clone and configure

On your laptop:

```bash
git clone https://github.com/OpenG2P/openg2p-deployment.git
cd openg2p-deployment/automation/production
cp prod-config.example.yaml prod-config.yaml
```

Drop the customer-provided TLS certificate files (received during [procurement](../../prerequisites-procurement.md#tls-certificate)) into a local folder next to your config — e.g. `./certs/wildcard.fullchain.pem` and `./certs/wildcard.key`. You'll reference them by path in `prod-config.yaml` below; the install uploads them to the Reverse-Proxy automatically. No need to copy certs to the server yourself.

Edit `prod-config.yaml`. The example config has every key tagged either `[USER]` (you fill in), `[CUSTOMER]` (provided by customer / govt — hostnames, certs), or `[AWS]` (auto-populated by AWS provisioning, or you fill in for non-AWS installs):

```yaml
# [USER] preferences
cluster_name: "openg2p"
postgres_version: "16"
wg_subnet: "10.15.0.0/16"
wg_port: "51820"

# [CUSTOMER] domain (the DNS A-record for rancher.<domain> must already exist,
# pointing at the RP's PRIVATE IP — see Prerequisites § 3. Rancher uses local
# auth; Grafana/Prometheus are reached via the Rancher UI, no dedicated DNS.)
public_domain: "openg2p.gov.eth"
# Override the hostname only if your customer uses a non-standard name:
# rancher_hostname:    "k8s-admin.dept.gov"

# [CUSTOMER] TLS certs (paths on YOUR laptop; uploaded to RP at install time)
# Either provide one wildcard cert covering *.<domain> (recommended — it also
# covers the per-environment service hostnames like keycloak/minio/superset):
tls_wildcard_cert: "./certs/wildcard.fullchain.pem"
tls_wildcard_key:  "./certs/wildcard.key"
# OR provide a per-FQDN cert for rancher (leave wildcard blank, fill these):
# tls_rancher_cert:    "./certs/rancher.fullchain.pem"
# tls_rancher_key:     "./certs/rancher.key"

# [AWS|MANUAL] node networking — auto-populated by AWS provisioning,
# or fill in manually for on-prem
rp_public_ip:       ""    # Wireguard endpoint (public/reachable address; on AWS = EIP)
rp_private_ip:      ""    # RP's primary NIC IP; admin Nginx binds here
compute_private_ip: ""
storage_private_ip: ""
private_subnet:     ""

# [USER, optional] Push a DNS resolver to every WG peer. Useful when admin
# hostnames are resolvable only via the customer's internal DNS (split-
# horizon DNS, AWS Route53 private zone, etc.). The resolver IP must live
# inside wg_subnet or private_subnet so queries traverse the tunnel.
#   On-prem example:  wg_peer_dns: "10.0.0.10"     (internal DNS server)
#   AWS example:      wg_peer_dns: "172.31.0.2"    (VPC DNS — <vpc-base>.2)
# Leave blank to skip the push (laptop uses its own resolver or /etc/hosts).
wg_peer_dns: ""
# ... and corresponding *_ssh_host, *_ssh_user, *_ssh_key, admin_cidr

# [USER] Environment stage — scaffolds one OpenG2P environment after infra.
# Commons is NOT installed here (install from the Rancher UI only).
install_environment: true           # master switch (false = stop after infra)
environment:
  name:            "prod"           # namespace + Rancher Project name
  base_domain:     ""               # blank → inherits 'public_domain'
```

{% hint style="info" %}
**Commons version.** When you install Commons from Rancher, pick the chart version from the [Commons changelog](https://openg2p.github.io/versions/commons/CHANGELOG.html).
{% endhint %}

### Step 2 — probe and preflight

Verify connectivity and resource adequacy before any installation work starts:

```bash
./openg2p-prod.sh --probe     --config prod-config.yaml   # SSH + sudo to all 3 nodes
./openg2p-prod.sh --preflight --config prod-config.yaml   # CPU/RAM/disk/internet/IP checks
```

The preflight runs in parallel on all three nodes, hard-fails on any node that doesn't meet the minimums, and warns (not fails) on rotational disks or pre-occupied ports.

### Step 3 — install

```bash
./openg2p-prod.sh --config prod-config.yaml
```

{% hint style="warning" %}
**Starting fresh (re-provisioned or reset machines)?** The orchestrator keeps laptop-side completion markers under `automation/production/.state/`. If you've torn down and re-provisioned the VMs (or wiped them) but kept the same `prod-config.yaml`, those markers are **stale** — the orchestrator will think every phase is already done and skip the whole install, leaving you with bare machines (it finishes in seconds and prints "SETUP COMPLETE").

Clear the stale state **before** the first install on fresh machines:

```bash
./openg2p-prod.sh --reset-laptop --config prod-config.yaml
./openg2p-prod.sh --config prod-config.yaml
```

From v1.x the orchestrator also **announces** any pre-existing markers at the start of a run (which phases will be skipped, with timestamps, plus the `--reset-laptop` hint), so an accidental skip is never silent. If you see that banner and the machines are fresh, run `--reset-laptop` and re-run.
{% endhint %}

Total runtime: 25–40 minutes for infrastructure, plus a few minutes for environment scaffolding (when `install_environment: true`). Environment scaffolding reaches the Kubernetes API through an **SSH tunnel to compute** — Wireguard is **not** required for that stage. Connect Wireguard afterward for Rancher UI and day-2 `kubectl`. For the exact phase sequence, see [Reference → Phase sequence](./#phase-sequence).

### Common command shapes

```bash
# Run only one role end-to-end
./openg2p-prod.sh --config prod-config.yaml --role storage
./openg2p-prod.sh --config prod-config.yaml --role compute
./openg2p-prod.sh --config prod-config.yaml --role rp

# Install (or re-run) just the environment scaffolding — SSH tunnel; Wireguard not required
./openg2p-prod.sh --config prod-config.yaml --stage environment
# or: ./openg2p-prod-env-install.sh --config prod-config.yaml

# Re-run a single phase on a single role
./openg2p-prod.sh --config prod-config.yaml --role compute --phase 2

# Force re-run completed steps
./openg2p-prod.sh --config prod-config.yaml --force

# Skip preflight (only for re-runs, when you've already validated the nodes)
./openg2p-prod.sh --config prod-config.yaml --skip-preflight

# Reset laptop-side orchestrator state (does not touch the nodes)
./openg2p-prod.sh --reset-laptop
```

### Step 4 — post-install on your laptop

When the orchestrator finishes it prints a **completion summary** with the Rancher local-admin password, the URL, and the exact commands for each step below — keep that summary handy. It is also saved to `automation/production/setup-output/SETUP-SUMMARY.txt`.

**Artifacts** are pulled automatically into `automation/production/artifacts/` (mode `0700` / files `0600`):

* `artifacts/peer1.conf` — Wireguard peer config
* `artifacts/rke2.yaml` — kubeconfig for day-2 use over Wireguard

Keep `artifacts/`, `provision-output.yaml`, `prod-config.yaml`, `aws/keys/*.pem`, and `certs/` secure — see the [production README](https://github.com/OpenG2P/openg2p-deployment/blob/main/automation/production/README.md) in the deployment repo.

The things to do, once, on your laptop:

#### 4.1 Connect Wireguard

Import the already-pulled peer file:

```bash
# Already at:
ls artifacts/peer1.conf
```

(If missing, pull manually:)

```bash
ssh -i <your-key> ubuntu@<rp-public-ip> \
    "sudo cat /etc/wireguard/peers/peer1/peer1.conf" > artifacts/peer1.conf
chmod 600 artifacts/peer1.conf
```

Install a Wireguard client and import this file:

| OS              | Where to get the client                                                           |
| --------------- | --------------------------------------------------------------------------------- |
| macOS           | [Wireguard from the App Store](https://apps.apple.com/app/wireguard/id1451685025) |
| Windows / Linux | [wireguard.com/install](https://www.wireguard.com/install/)                       |
| iOS / Android   | App Store / Play Store                                                            |

In the app: **Add Tunnel → Import from file/archive → choose `artifacts/peer1.conf` → Activate**.

Verify the tunnel is up:

```bash
ping 10.15.0.1   # the RP's WG-side IP — must respond
```

{% hint style="info" %}
The peer config uses **split tunnel** by default — only the Wireguard subnet (`10.15.0.0/16`) and the cluster's private subnet are routed through the VPN. Your normal internet stays direct.
{% endhint %}

#### 4.2 (Skipped — no local CA)

Since you're using **real certs from your customer's CA** (see [TLS certificate](../../prerequisites-procurement.md#tls-certificate)), there's no CA to install on your laptop. Browsers already trust the issuing CA. If you see a cert warning when first opening Rancher, that's a real issue — your cert chain probably isn't complete; re-run `--validate-certs` and the pre-flight will catch it.

#### 4.3 DNS resolution on your laptop

You need your laptop to resolve the admin hostname (`rancher.<domain>`) to the RP's **internal** IP. Three working patterns:

1.  **Customer's DNS reachable through Wireguard** (preferred) — if `wg_peer_dns` was set, the peer config already carries `DNS = …`.
2.  **`/etc/hosts` on your laptop** — manual but reliable. The orchestrator's completion summary prints the exact line:

    ```
    <RP-internal-IP>  rancher.openg2p.gov.eth
    ```
3. **Public DNS pointing at the private IP** — if the customer's authoritative DNS is public-facing and OK with publishing private-IP A-records.

{% hint style="warning" %}
On macOS, don't use `dig` to test — it bypasses the system resolver and will give NXDOMAIN even when everything works. Use `dscacheutil -q host -a name rancher.<domain>`, `ping`, or `curl`.
{% endhint %}

#### 4.4 Login to Rancher (local authentication)

Open `https://rancher.<your-domain>` in your browser (the hostname you put in `rancher_hostname` / derived from `public_domain`).

* **Username**: `admin`
*   **Password**: shown in the orchestrator's completion summary; or fetch it from the cluster:

    ```bash
    export KUBECONFIG=./artifacts/rke2.yaml   # Wireguard must be active
    kubectl -n cattle-system get secret rancher-secret \
      -o jsonpath='{.data.adminPassword}' | base64 -d && echo
    ```

You're now in the Rancher UI as the local `admin`.

{% hint style="info" %}
**Rancher uses local authentication — there is no external SSO.** Create additional admin users directly in Rancher: **☰ → Users & Authentication → Users → Create**, then assign cluster/project roles. Guard the `admin` password accordingly. (The OpenG2P apps' Keycloak is a separate, per-environment identity provider for the applications — it is not Rancher's login.)
{% endhint %}

#### 4.5 (Optional) kubectl from your laptop

```bash
export KUBECONFIG=./artifacts/rke2.yaml
kubectl get nodes
```

Requires Wireguard active — the kubeconfig points at the compute node's private IP.

### Step 5 — install Commons via Rancher UI

The orchestrator scaffolds the environment (namespace, project, gateway, PG secret, Helm repos) during the install when `install_environment: true`. **It does not install Commons.**

**Install Commons from the Rancher UI only** (Wireguard connected, logged into Rancher):

1. Apps → Charts → **openg2p-commons-base**
2. Then install **openg2p-commons-services** in the same namespace
3. Point PostgreSQL at the storage node's private IP using the `commons-postgresql` secret created by scaffolding
4. Pick the chart version from the [Commons changelog](https://openg2p.github.io/versions/commons/CHANGELOG.html)

If you skipped scaffolding (`install_environment: false`), run it first (SSH tunnel; Wireguard not required):

```bash
./openg2p-prod.sh --stage environment --config prod-config.yaml
```

## The environment stage

The infrastructure install ends by **scaffolding** one OpenG2P **environment** on the cluster (when `install_environment: true`). An environment is a namespace plus shared services that product modules later install into. Scaffolding runs **from your laptop** and reaches the API through an **SSH tunnel to compute** — Wireguard is not required for this step.

{% hint style="info" %}
This section documents how the environment stage is **wired into the production automation**. For Commons install (Rancher UI) and multi-environment setups, see [Environment Setup](../../environment-setup-multi-node.md).
{% endhint %}

**What production scaffolding does (phase 1 only):**

1. Opens an SSH tunnel to the Kubernetes API on compute and fetches kubeconfig
2. Registers Helm ClusterRepos: `openg2p` (GitHub Rancher index) and `openg2p-gitlab` (GitLab Helm registry)
3. Creates the namespace and Rancher Project, the Istio Gateway for `*.<base_domain>`, and the external-PostgreSQL secret (password auto-read from the Storage node)

**What it does _not_ do:** install `openg2p-commons-base` / `openg2p-commons-services`. That is done from the **Rancher UI only**.

**Key points:**

* **Same wildcard cert, same domain.** After Commons is installed, service URLs are `<service>.<base_domain>` (defaults to `public_domain`).
* **External PostgreSQL secret is prepared** for Commons — host PostgreSQL on the Storage node; the chart should use `postgresql.enabled=false` and the `commons-postgresql` secret.
* **Configurable** via `install_environment` and `environment.name` / `environment.base_domain` in `prod-config.yaml`.
* **Idempotent & re-runnable.** `./openg2p-prod.sh --stage environment` (or `./openg2p-prod-env-install.sh`).
* **Skippable.** Set `install_environment: false` to stop after infrastructure.

## How to verify the basic setup is up

After the orchestrator declares success, run these checks. Each is an explicit signal that one layer of the stack is healthy.

### From your laptop

#### 1. Wireguard tunnel

```bash
wg show wg0    # On macOS/Linux client
```

You should see the peer line populated with a recent handshake timestamp. On Wireguard's GUI clients (Windows, Mac, mobile) the connected/peer count is shown directly.

#### 2. Internal DNS

```bash
ping -c1 rancher.<your-domain>
```

The hostname should resolve to the RP's **internal** IP (e.g. `172.29.0.179`), not its public IP. If it resolves to the public IP, your customer's DNS has the wrong A-record.

{% hint style="info" %}
On macOS, `dig` bypasses the system resolver. Use `dscacheutil -q host -a name rancher.<your-domain>` if `dig` returns NXDOMAIN.
{% endhint %}

#### 3. Browser to Rancher

Open `https://rancher.<your-domain>`. You should see the Rancher login page (local auth — `admin` + password) and **no certificate warning** (your customer-supplied cert chains to a publicly-trusted CA).

#### 4. kubectl

```bash
export KUBECONFIG=./artifacts/rke2.yaml
kubectl get nodes
kubectl get pods -A | grep -v Running
```

The first command should show the compute node `Ready`. The second should be empty (or only show known transient pods like helm hooks).

### On the reverse-proxy node

```bash
sudo systemctl is-active wg-quick@wg0       # active
sudo systemctl is-active nginx              # active
sudo nginx -t                               # syntax OK
sudo ss -tlnp | grep -E ':80|:443'          # nginx bound to rp_private_ip
sudo ls /etc/openg2p/certs/public/          # one dir per admin hostname
```

### On the compute node

```bash
sudo systemctl is-active rke2-server                    # active
sudo KUBECONFIG=/etc/rancher/rke2/rke2.yaml kubectl get nodes
sudo KUBECONFIG=/etc/rancher/rke2/rke2.yaml kubectl get pods -A | grep -v Running   # empty
mountpoint /mnt/nfs/openg2p                             # is a mountpoint
```

### On the storage node

```bash
sudo systemctl is-active nfs-kernel-server              # active
sudo systemctl is-active postgresql                     # active
sudo exportfs -v                                        # shows the export to compute
sudo -u postgres psql -c "SELECT version();"            # PG 16 banner
sudo cat /etc/openg2p/secrets/postgres-superuser.env    # see PG superuser creds
```

The PostgreSQL superuser password is auto-generated by storage phase 1 and saved at `/etc/openg2p/secrets/postgres-superuser.env` on the storage node (root-owned, mode `0600`). The file contains `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER` (always `postgres`), and `POSTGRES_PASSWORD`. The orchestrator's completion summary also prints these values directly. The [environment stage](./#the-environment-stage) reads this password automatically (over SSH) into the `commons-postgresql` namespace secret — you don't copy it by hand when scaffolding.

## File structure

```
automation/production/
├── openg2p-prod.sh                    # Laptop orchestrator (install)
├── openg2p-prod-uninstall.sh          # Laptop orchestrator (wipe platform off the 3 VMs)
├── openg2p-prod-env-install.sh        # Environment scaffolding only
├── openg2p-prod-env-uninstall.sh      # Reset just the environment scaffolding
├── prod-config.example.yaml           # Single config file (flat YAML)
├── helmfile-infra.yaml.gotmpl         # Platform helmfile (Istio EnvoyFilter,
│                                       Rancher, monitoring, logging)
├── lib/
│   ├── ssh-utils.sh                   # ControlMaster SSH, rsync, K8s SSH tunnel
│   └── shared/
│       ├── utils.sh                   # logging, state, config loader
│       ├── preflight.sh               # Per-node resource + network checks
│       └── hostnames.sh               # Hostname helpers + config-key bridge
├── charts/
│   ├── raw/                           # Minimal chart for K8s manifests
│   └── istio-install/                 # Istio operator config
├── aws/                                # See AWS Provisioning page
├── artifacts/                          # peer1.conf, rke2.yaml (gitignored; mode 0700)
└── roles/
    ├── reverse-proxy/{run.sh,phase1.sh,uninstall.sh}
    ├── compute/{run.sh,phase1.sh,phase2.sh,uninstall.sh}
    ├── storage/{run.sh,phase1.sh,uninstall.sh}
    └── environment/{run.sh,phase1.sh,uninstall.sh}   # scaffolding via SSH tunnel
```

{% hint style="info" %}
Standalone scaffolding scripts live under `automation/environment/` (`env-cluster.sh`) for clusters not built by the production orchestrator. They do **not** install Commons. See [Environment Setup](../../environment-setup-multi-node.md).
{% endhint %}

## Troubleshooting

{% hint style="info" %}
**Script failed?** Re-run it. Completed steps are skipped via state markers. Error messages include diagnostic commands.
{% endhint %}

### Orchestrator (`openg2p-prod.sh`)

**`bash 4+ required` at startup** — only happens on macOS where `/bin/bash` is 3.2 by default. Install a newer one: `brew install bash`. The script's `#!/usr/bin/env bash` will then resolve to it.

**Script exits silently with no output (or only the boot line)** — there's a fatal error somewhere; the trap should print `[FATAL] ... at line N (command)`. If you see only the boot line and nothing else, check the log file path printed by the trap.

**Run finishes in seconds and prints "SETUP COMPLETE", but nothing is installed** — the laptop-side `.state/` markers are stale. This happens when you re-provisioned or reset the VMs but reused the same `prod-config.yaml`: the orchestrator sees every phase already marked done and skips them all. The run log shows `Skipping '<role> phase N' — already completed` for each phase, and the summary has empty hostnames / `<empty — secret may not exist>` passwords. Fix: clear the stale state and re-run.

```bash
./openg2p-prod.sh --reset-laptop --config prod-config.yaml
./openg2p-prod.sh --config prod-config.yaml
```

The orchestrator now prints a banner listing pre-existing markers (with timestamps) at the start of every run, so check that first — old timestamps against fresh machines confirm the state is stale.

**Preflight fails on a node** — the failure summary lists which node and which check (CPU, RAM, disk, internet, IP). Resize or reconfigure that VM and re-run. Common cases:

* RAM falls just below the threshold — Linux reports a slightly smaller MemTotal than the AWS-advertised RAM (kernel reservation). The check accepts 10% slack; if it still fails, your VM really is under-sized.
* Internet egress: from the failing node, run `curl -sSI --max-time 10 https://get.rke2.io` to reproduce.

### SSH and host-key prompts

**SSH probe fails / connection timed out** — the most common cause used to be the laptop's public IP no longer matching an auto-detected `admin_cidr` `/32` on the cloud security group. Blank `admin_cidr` now defaults to `0.0.0.0/0` so network changes do not lock you out. If you set a custom CIDR, confirm it still covers this laptop (`curl -s https://checkip.amazonaws.com`) or widen/`0.0.0.0/0` and re-run AWS provision (adds missing ingress; does not revoke old rules). Also check key path/perms and that instances are `running`.

**Compute helmfile sync hangs or errors** — SSH into the compute node:

```bash
sudo KUBECONFIG=/etc/rancher/rke2/rke2.yaml kubectl get pods -A | grep -v Running
sudo KUBECONFIG=/etc/rancher/rke2/rke2.yaml kubectl get events -A --sort-by=.lastTimestamp | tail -30
```

Then re-run only that phase: `./openg2p-prod.sh --config prod-config.yaml --role compute --phase 2`.

### Reverse-Proxy Nginx

**Nginx on the RP listens on 0.0.0.0:80 instead of `<rp-private>:443`** — happens when the apt nginx package's default config pre-bound port 80 and a `systemctl reload` didn't transition the listen sockets. Fix: `sudo systemctl restart nginx` on the RP. The current script uses unconditional `restart` (not `reload`) and verifies the bind, so this should not recur.

**`https://rancher.<domain>` doesn't load even with Wireguard up** — check, on the compute node, that `/etc/hosts` has the Rancher hostname pointing at the RP private IP (`grep rancher /etc/hosts`), and that nginx on the RP is listening on `<rp-private>:443` (`sudo ss -tlnp | grep 443`).

**Changed `public_domain` after a previous install (Rancher URL returns HTTP 000 / connection failed)** — compute `/etc/hosts` and RP Nginx blocks are only written once (state markers). Update DNS and certs for the new domain, then force-refresh:

```bash
./openg2p-prod.sh --config prod-config.yaml --role compute --phase 1 --force
./openg2p-prod.sh --config prod-config.yaml --role rp --phase 1 --force
./openg2p-prod.sh --config prod-config.yaml --role compute --phase 2 --force
```

Confirm the TLS cert covers `rancher.<new-domain>` (`./openg2p-prod.sh --validate-certs`).

### Login

**Rancher login is rejected** — Rancher uses **local authentication** (username `admin`, password from `cattle-system/rancher-secret`, printed in the orchestrator's completion summary). There is no Keycloak/SSO login for Rancher. Create further admin users in Rancher → **Users & Authentication → Users**.

**Wireguard connects but `*.openg2p.internal` doesn't resolve on macOS** — `dig` bypasses the macOS resolver and will give NXDOMAIN even when everything works. Use `dscacheutil -q host -a name rancher.openg2p.internal` instead. For reliable per-domain DNS:

```bash
sudo mkdir -p /etc/resolver
echo "nameserver 10.15.0.1" | sudo tee /etc/resolver/openg2p.internal
```

**Wireguard tunnel up, admin URL works, but I can't reach compute/storage by private IP** — `ping 10.15.0.1` answers, `https://rancher.<domain>` loads fine, but `ping <compute_private_ip>`, `ssh ubuntu@<storage_private_ip>`, or `kubectl --server=https://<compute_private_ip>:6443` time out. Cause: Ubuntu's ufw ships with `DEFAULT_FORWARD_POLICY="DROP"` and installs its own policy-enforcement chain in `FORWARD`. wg-quick's `PostUp` rules must be **inserted at the top** of `FORWARD` (`-I FORWARD 1 …`) so they match _before_ ufw's drop; **appending** them (`-A FORWARD …`) puts them after the drop where they never fire. INPUT traffic (laptop → Nginx on the RP's private IP) is unaffected, which is why admin URLs keep working; only forwarded traffic (`wg0 → private subnet`) is silently dropped.

The current automation generates the correct `-I` rules. If you have an older install with `-A` baked into `/etc/wireguard/wg0.conf`, hot-fix on the RP without re-running the install:

```bash
grep PostUp /etc/wireguard/wg0.conf                # see what's there
# If you see "-A FORWARD ... -j ACCEPT":
sudo sed -i 's/-A FORWARD/-I FORWARD 1/g' /etc/wireguard/wg0.conf
sudo systemctl restart wg-quick@wg0
sudo iptables -L FORWARD -n --line-numbers | head -5   # ACCEPT for wg0 should be on line 1
```

Then from the laptop: `ping <compute_private_ip>` should answer.

**Browser certificate warning even after trusting the CA** — on macOS the CA must be trusted at the **System** keychain (not Login keychain). Run the `security add-trusted-cert -k /Library/Keychains/System.keychain ...` form, then restart the browser.

**Compute helmfile sync hangs or errors** — SSH into the compute node:

```bash
sudo KUBECONFIG=/etc/rancher/rke2/rke2.yaml kubectl get pods -A | grep -v Running
sudo KUBECONFIG=/etc/rancher/rke2/rke2.yaml kubectl get events -A --sort-by=.lastTimestamp | tail -30
```

Then re-run only that phase: `./openg2p-prod.sh --config prod-config.yaml --role compute --phase 2`.

**Wireguard connects but `*.openg2p.internal` doesn't resolve on macOS** — `dig` bypasses the macOS resolver. Use `dscacheutil -q host -a name rancher.openg2p.internal` instead. For reliable per-domain DNS without going through the WG-pushed DNS:

```bash
sudo mkdir -p /etc/resolver
echo "nameserver 10.15.0.1" | sudo tee /etc/resolver/openg2p.internal
```

**Browser cert warning even after trusting CA** — the CA must be trusted at the **system** level (System keychain on macOS, not user). Restart the browser after trust changes.

**AWS-specific troubleshooting** (VPC not found, EIP `AddressLimitExceeded`, multiple environments on one account) → see [AWS Provisioning → Troubleshooting](aws-provisioning.md#troubleshooting).

## Recovery & uninstall

When an install fails, you usually do **not** need to re-provision the VMs. Try these in order:

| # | When                                                                                                                                                                          | Command                                                                                                    |
| - | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| 1 | **Transient failure** — network blip, slow apt mirror, Ctrl-C, dropped SSH. The install left a partial state but nothing semantically wrong.                                  | `./openg2p-prod.sh --config prod-config.yaml` (just re-run; completed steps are skipped via state markers) |
| 2 | **Need to re-run a completed phase** — you fixed a config value, or a previous step landed wrong but its marker got set.                                                      | `./openg2p-prod.sh --config prod-config.yaml --force`                                                      |
| 3 | **VMs were re-provisioned but you reused the same `prod-config.yaml`** — stale laptop markers will make the orchestrator skip everything.                                     | `./openg2p-prod.sh --reset-laptop --config prod-config.yaml` then re-run install.                          |
| 4 | **Install left the VMs in an unrecoverable state** — RKE2 cluster confused, helm releases half-applied, configs inconsistent. You want to start over without re-provisioning. | `./openg2p-prod-uninstall.sh --config prod-config.yaml` then re-run install.                               |

There are **two uninstall scopes**: reset just the **environment** (`openg2p-prod-env-uninstall.sh`), or wipe the **whole platform** off the VMs (`openg2p-prod-uninstall.sh`).

### `openg2p-prod-env-uninstall.sh` — reset just the environment scaffolding

Removes the environment namespace scaffolding (and optionally Commons workloads if present) but leaves the platform and the three VMs intact. Uses an SSH tunnel — Wireguard is not required.

```bash
./openg2p-prod-env-uninstall.sh --config prod-config.yaml            # confirm, then tear down
./openg2p-prod-env-uninstall.sh --config prod-config.yaml --dry-run  # preview only
```

* **Removes:** namespace resources managed by scaffolding (and Commons Helm releases / PVCs if present), and related databases on host PostgreSQL when applicable.
* **Preserves:** the 3 VMs, the platform, the NFS + PostgreSQL **servers**, and the PostgreSQL **superuser** credentials.
* **Flags:** `--full` (also delete the namespace, Istio Gateway, Rancher Project), `--keep-databases` (K8s only), `--yes`, `--dry-run`.

Re-create scaffolding with `./openg2p-prod.sh --stage environment --config prod-config.yaml`, then install Commons again from the Rancher UI.

### `openg2p-prod-uninstall.sh` — in-place uninstall

Wipes the OpenG2P installation off the three VMs while leaving the VMs themselves (and their provisioned IPs, SGs, EIP, etc.) intact.

```bash
# Full uninstall — all three nodes
./openg2p-prod-uninstall.sh --config prod-config.yaml

# Surgical — redo just one node (typical after RKE2 trouble on compute)
./openg2p-prod-uninstall.sh --config prod-config.yaml --role compute
```

You'll be asked to **type the `cluster_name`** to confirm before anything is touched.

**What gets removed (per node):**

* **Compute** — RKE2 (via `rke2-uninstall.sh`, which wipes the cluster, etcd, containerd, CNI, and **every helm release** including Istio / Rancher / monitoring / logging and any installed environment workloads); `kubectl`/`helm`/`istioctl`/`helmfile` binaries; NFS client mount; `/etc/hosts` managed block; sysctl tweaks; ufw rules; state markers.
* **Reverse Proxy** — Wireguard server + peer configs; Nginx admin server blocks; customer certs; ip\_forward sysctl; MASQUERADE residue; ufw rules; state markers.
* **Storage** — host PostgreSQL; NFS server + `/etc/exports`; ufw rules; state markers.
* **Laptop** — orchestrator `.state/` markers + pulled `artifacts/`.

**What's kept:**

* The VMs themselves and all AWS / on-prem infrastructure around them (use `aws/openg2p-aws-destroy.sh` to tear those down on AWS).
* Generic OS tools — `curl`, `jq`, `openssl`, `ssh`, `ufw`, `ca-certificates`.
* **Postgres data dir and NFS export contents** on the storage node (the actual data). Pass `--purge-data` to delete those too — there is no undo.

After uninstall the message "_To start fresh, run: ./openg2p-prod.sh …_" is printed. Re-run the install in the normal way.

{% hint style="warning" %}
The uninstall script is **destructive and idempotent** but it does NOT touch your `prod-config.yaml` or the certificate files on your laptop — those survive so a re-install just works.
{% endhint %}

{% hint style="info" %}
**Tearing down just the environment**, without wiping the whole cluster? Use `openg2p-prod-env-uninstall.sh` (or the teardown on the [Environment Setup](../../environment-setup-multi-node.md#uninstallation) page). A full compute uninstall removes the cluster _and_ everything in it. Either way, data in host PostgreSQL on the Storage node survives unless you pass `--purge-data`.
{% endhint %}

### Options reference

| Flag              | Purpose                                                                                                       |
| ----------------- | ------------------------------------------------------------------------------------------------------------- |
| `--config <file>` | Path to `prod-config.yaml` (required)                                                                         |
| `--role <name>`   | `all` (default) \| `rp` \| `compute` \| `storage` — wipe one node only                                        |
| `--purge-data`    | Also delete PostgreSQL data dir + NFS export contents on storage                                              |
| `--yes` / `-y`    | Skip the typed-name confirmation prompt                                                                       |
| `--skip-ssh`      | Laptop-side cleanup only (`.state/`, `artifacts/`) — useful for fixing stale markers without touching the VMs |
| `--help`          | Show help                                                                                                     |

## Reference

Background detail — not needed to run the install. Useful when something goes wrong or when you want to know what's running.

### Technology stack

| Component       | Version                                     | Notes                                                                                                                                  |
| --------------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| OS              | Ubuntu Server 24.04 LTS                     | All three nodes                                                                                                                        |
| Orchestrator    | bash + ssh + rsync                          | Runs on your laptop, no extra dependencies                                                                                             |
| Kubernetes      | RKE2 v1.33.6                                | Single control-plane on the compute node                                                                                               |
| Service mesh    | Istio 1.24.1                                | Installed via `istioctl`                                                                                                               |
| Helm            | v3.17.3                                     | + helm-diff plugin                                                                                                                     |
| Helmfile        | v1.1.0                                      | Drives the platform component installs                                                                                                 |
| Cluster manager | Rancher 2.12.3                              | In-cluster, with embedded Postgres                                                                                                     |
| Rancher auth    | Local authentication                        | Admin users created directly in Rancher; no external SSO. (The apps' Keycloak is per-environment, installed with Commons — not by production scaffolding.) |
| Monitoring      | Rancher monitoring 105.0.0                  | Prometheus + Grafana                                                                                                                   |
| Logging         | OpenTelemetry + Grafana Loki                | Cluster-wide log pipeline (OTel agent → gateway → Loki, backed by dedicated MinIO); replaces Fluentd/OpenSearch                        |
| Storage         | NFS-CSI driver v4.7.0                       | Default StorageClass `nfs-csi`, retain policy                                                                                          |
| VPN             | Wireguard (kernel + tools)                  | Native systemd service on the RP node                                                                                                  |
| DNS             | Customer-provided (no DNS server installed) | Hostnames resolved by customer's authoritative DNS or admin-laptop `/etc/hosts`                                                        |
| Database (host) | PostgreSQL 16                               | On the storage node, ready for environment automation                                                                                  |

### Phase sequence

The orchestrator runs phases in this order. Total runtime: 25–40 minutes.

| # | Where         | What                                                                                                                                                                                               |
| - | ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0 | Laptop        | SSH + sudo probe on all 3 nodes                                                                                                                                                                    |
| 0 | All 3 nodes   | Preflight: OS, CPU, RAM, disk, internet, IP-matches-config (in parallel)                                                                                                                           |
| 1 | Storage       | apt basics, ufw, NFS server export, host PostgreSQL install (no app DBs yet)                                                                                                                       |
| 2 | Compute       | apt basics, kubectl/helm/istioctl/helmfile, ufw, NFS client mount, RKE2 server, NFS CSI default StorageClass                                                                                       |
| 3 | Reverse Proxy | apt basics, ufw, Wireguard server + peer configs (with optional `wg_peer_dns` push), customer cert ingest + validate + install, Nginx server blocks bound to `rp_private_ip`                       |
| 4 | Compute       | helmfile sync — Istio, Rancher (local auth, NFS-backed embedded Postgres), monitoring, logging                                                                                                     |
| 5 | Laptop        | Environment scaffolding — Helm ClusterRepos (`openg2p`, `openg2p-gitlab`), namespace, Rancher Project, Istio Gateway, external-PG secret. Uses SSH tunnel to compute (**Wireguard not required**). Commons is **not** installed here. |

### Out of scope

The following are deferred to follow-up automation, not gaps:

* **Commons** — `openg2p-commons-base` + `openg2p-commons-services`. Production scaffolding prepares the namespace and secrets; install Commons from the **Rancher UI only**. See [Environment Setup](../../environment-setup-multi-node.md).
* **Product modules** — Registry, PBMS, SPAR, G2P Bridge, etc. Install on top of Commons via their own Helm charts. See the per-product deployment pages.
* **Citizen-facing public domains and the public channel** — this automation keeps admin tools on the private (VPN) channel. Opening public `80/443` for citizen-facing hostnames is a separate step. See [DNS & TLS Certificates](../../deployment-guide/dns-and-certificates.md).
* **Local Docker registry** — RKE2 pulls images from upstream. A pull-through cache mirror will come in a later phase.
* **Local Git repository** — deferred.
* **Air-gap / offline operation** — initial install requires internet. Self-contained operation is a later phase.
* **Backup node and backup automation** — the Backup node (the 4th node) is **required for production**, but it is set up by a **separate** tool, not this orchestrator. See [Backups](../../backups/).

### The orchestrator's `.state/` directory

The orchestrator keeps **laptop-side bookkeeping** under `automation/production/.state/orchestrator/*.done` to remember which whole-phase pushes have already been issued (e.g. "storage phase 1 was successfully driven from this laptop"). It is **not** the source of truth for what's installed — that lives on each node under `/var/lib/openg2p/deploy-state/`.

* **Safe to delete?** Yes, any time. Worst case is the orchestrator re-pushes role bundles and re-invokes role scripts; the remote state markers then skip already-done sub-steps, so nothing actually re-runs.
* **Should it be checked in?** No — already gitignored.
* **Quick reset:** `./openg2p-prod.sh --reset-laptop` removes the directory cleanly.

## Related documentation

* [OpenG2P Deployment Architecture](../../../../deployment/openg2p-deployment-model.md) — the deployment models (Sandbox, Production — Minimum, Production — High-Availability) and where this automation fits.
* [DNS & TLS Certificates](../../deployment-guide/dns-and-certificates.md) — wildcard vs per-FQDN trade-offs in gov procurement, and the cert formats customers actually have.
* [Prerequisites & Procurement](../../prerequisites-procurement.md) — compute, DNS, certs, access, firewall to arrange before install.
* [Single-Node Automation](../single-node-automation/) — the simpler counterpart, useful for sandboxes and reading source code patterns shared with production.
