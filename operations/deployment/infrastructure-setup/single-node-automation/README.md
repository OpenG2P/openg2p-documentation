---
description: Sandbox (single-node) deployment automation
---

# Sandbox — Single-Node

Brings up a complete OpenG2P sandbox on **one Ubuntu VM** — Kubernetes, Rancher, Istio, monitoring, logging, Wireguard, Nginx, DNS and real TLS certificates — from a laptop, over SSH.

<figure><img src="../../../../.gitbook/assets/Deployment Architecture - Single Node.jpg" alt=""><figcaption><p>Single-node architecture — all services on one VM</p></figcaption></figure>

{% hint style="success" %}
**Just want to run it?** Skip to [Part 2 — Guide](#part-2--guide). Part 1 explains how the pieces fit together and is worth reading once.
{% endhint %}

{% hint style="info" %}
Source: [`openg2p-deployment`](https://github.com/OpenG2P/openg2p-deployment) under `automation/sandbox/`.
{% endhint %}

---

# Part 1 — Concepts

## What the sandbox is

A sandbox is **one VM running everything**. It is intended for evaluation, development, QA, demos and small pilots — not for production, where compute, storage and the reverse proxy are separated across nodes.

The install has two distinct layers, and the distinction matters throughout:

| Layer | What it is | How often |
|---|---|---|
| **Infrastructure** | The machine and the cluster platform: RKE2, Istio, Rancher, monitoring, logging, Wireguard, NFS, Nginx, DNS records, TLS certificate | **Once** per VM |
| **Environment** | A namespace with its own sub-domain, certificate, Nginx routing, Rancher Project and Istio Gateway — ready for you to deploy applications into | **Many** per sandbox (`dev`, `qa`, `trial`…) |

Each layer has its own configuration file. Infrastructure is installed once; environments are added whenever you need one.

## Authentication — Rancher uses local accounts

There is **no Keycloak at the infrastructure level** and no SSO for Rancher. Rancher authenticates against its own local user database.

Create additional Rancher users directly in the UI: **☰ → Users & Authentication → Users**. See [User access & roles](#user-access--roles).

Keycloak *is* part of OpenG2P — but as an application deployed **inside an environment**, serving the OpenG2P services. It is unrelated to Rancher login.

## DNS and TLS — the model

This is the part most worth understanding, because it drives the prerequisites.

The sandbox uses **real, publicly-trusted certificates from Let's Encrypt**. Self-signed certificates are deliberately not supported: services inside the cluster call each other over HTTPS and fail when the issuing CA is not in the system trust store. Chasing those failures is far more painful than obtaining a real certificate.

Real certificates require a **real, registered domain name**. Reserved TLDs (`.test`, `.local`, `.internal`, `.localhost`) can never receive one — that is a CA/Browser Forum rule binding on every public CA, not a Let's Encrypt policy — so the installer rejects them.

**You do not need to expose the machine to the internet, and you do not need to touch your organisation's DNS.** Certificates are obtained using the ACME **DNS-01** challenge:

```
sandbox VM ──(1) write TXT _acme-challenge.<name>──▶ your DNS provider
sandbox VM ──(2) "please issue <name>"─────────────▶ Let's Encrypt
                              Let's Encrypt ──(3) DNS query──▶ your DNS provider
sandbox VM ◀──(4) signed certificate──────────────── Let's Encrypt
```

Let's Encrypt never connects **to** the sandbox — it only reads a DNS record. The VM makes two outbound HTTPS calls and nothing more. That is what makes this work on-premise and behind NAT.

The installer also publishes **A records** pointing at the VM, so hostnames resolve on laptops and inside pods with no local DNS server and no `/etc/hosts` entries.

{% hint style="info" %}
The A records normally point at a **private** address (e.g. `172.29.14.170`). Publishing a private IP in public DNS grants nobody access — the address is unroutable from the internet — but it does disclose your hostname and internal IP layout to anyone who queries the zone. Set `tls.publish_a_records: false` if that is unacceptable and manage those records yourself.
{% endhint %}

## Two options for DNS

**Which one applies to you depends on whether you already own a domain.**

<table><thead><tr><th width="180">Option</th><th>When to use it</th><th>What you need</th></tr></thead><tbody><tr><td><strong>A — Free domain</strong><br>(deSEC / dedyn.io)</td><td>You have no domain, or getting one involves procurement. Gets a sandbox running in minutes.</td><td>A free deSEC account (~2 minutes). No purchase, no approvals.</td></tr><tr><td><strong>B — Your own domain</strong></td><td>You already own a domain hosted on a provider with an API — Cloudflare, AWS Route 53, or a self-hosted acme-dns.</td><td>The domain, plus an API token scoped to that zone.</td></tr></tbody></table>

Both produce identical, publicly-trusted certificates. Option A is not "lesser" — it is the same Let's Encrypt certificate, just under a free domain name.

**You can move from A to B later.** Change `domain` and the `tls.*` provider settings, then re-run. New DNS records and a new certificate are issued for the new domain. Note that the hostnames change, so anything referencing the old names (bookmarks, client configs, deployed application settings) must be updated too — a clean rebuild is often simpler than a migration for a sandbox.

{% hint style="warning" %}
Bringing your **own certificate file** is not currently supported — certificates are always obtained via ACME. If you have an existing wildcard certificate you must use, that path is not yet automated.
{% endhint %}

## Access model — private by default

The sandbox is **not reachable from the public internet by default, even if the VM has a public IP.**

| Reachable over | Ports |
|---|---|
| Wireguard VPN, or from inside the VPC | `80`, `443` (Rancher and all environment services) |
| The public internet | `22` (SSH) and the Wireguard UDP port only |

Administrative and data-plane ports — the Kubernetes API, NodePorts, etcd, kubelet, NFS — are always restricted to the VPC and Wireguard, so `kubectl` and `helm` require the VPN.

Setting `public_access: true` opens `80/443` to `0.0.0.0/0`.

{% hint style="danger" %}
`public_access: true` exposes the Rancher **cluster-admin** UI and every environment service to anyone who can reach the public IP, protected only by local passwords. A valid TLS certificate encrypts the connection — it does **not** restrict who may connect. Only enable it deliberately, and prefer restricting source IPs at the firewall or cloud security group to the specific addresses that need access.
{% endhint %}

## How you reach it over the VPN

DNS resolution and packet routing are independent. Your laptop resolves `rancher.<domain>` through its normal resolver (public DNS returns the private IP); Wireguard then routes traffic to that address through the tunnel. No DNS configuration is needed on the client.

---

# Part 2 — Guide

## Prerequisites

| Requirement | Detail |
|---|---|
| **VM** | Ubuntu 24.04 LTS — 16 vCPU, 64 GB RAM, 128 GB SSD |
| **Access** | SSH from your laptop, passwordless `sudo` for the SSH user |
| **Internet** | Outbound only, from the VM (packages, Helm charts, ACME). **No inbound required.** |
| **Domain** | A real registered domain — see [Step 1](#step-1-set-up-dns) |
| **DNS API token** | For the provider hosting that domain |
| **Laptop** | `bash`, `ssh`, `rsync`, `curl`. Wireguard client for access afterwards. |

## Step 1: Set up DNS

### Option A — free domain with deSEC (dedyn.io)

Do this once, takes about two minutes.

1. **Create an account** at [https://desec.io/](https://desec.io/) — email address and a captcha. Confirm via the email link.
2. **Create a domain.** Go to [https://desec.io/domains](https://desec.io/domains) → **Add Domain** → enter a name under `dedyn.io`, for example `mydept.dedyn.io`. This registers the whole **zone** — you control every name beneath it (`rancher.mydept.dedyn.io`, `*.dev.mydept.dedyn.io`, …). You do **not** register subdomains separately.
3. **Create an API token** at [https://desec.io/tokens](https://desec.io/tokens) → **Create token**.
   * Give it a name, e.g. `openg2p-sandbox`.
   * **Leave it unrestricted** — do not attach token policies. The ACME client detects the zone by *listing* your domains, and a policy-restricted token can read a domain but fail to list it, which surfaces later as a confusing `invalid domain` error.
   * **Copy the token now** — deSEC shows it only once.
4. Put the domain and token into `sandbox-config.yaml` (Step 3).

{% hint style="info" %}
Nothing else is needed. The installer creates every DNS record itself — A records for the hostnames and the temporary `_acme-challenge` TXT records used to obtain certificates.
{% endhint %}

### Option B — your own domain

Use the domain you already own. Set `tls.dns_provider` to match where its DNS is hosted and supply a credential scoped to that zone:

| Provider | `dns_provider` | Credentials |
|---|---|---|
| Cloudflare | `cloudflare` | `tls.api_token` (API token with **DNS\:Edit** on the zone), `tls.cf_account_id` |
| AWS Route 53 | `route53` | `tls.aws_access_key_id` + `tls.aws_secret_access_key`, or leave both blank to use the EC2 instance role |
| Self-hosted acme-dns | `acmedns` | `tls.acmedns_*` fields |

{% hint style="info" %}
For `cloudflare` and `route53`, A-record publishing is not automated — the installer prints the exact records to create. Certificate issuance (DNS-01) is fully automated for all providers.
{% endhint %}

## Step 2: Provision the VM

Use any Ubuntu 24.04 machine you already have, or provision one on AWS — see [AWS Provisioning](aws-provisioning.md), which writes a `provision-output.yaml` that fills in `node_ip`, `ssh_*` and `wireguard.endpoint` automatically.

## Step 3: Configure

```bash
git clone https://github.com/OpenG2P/openg2p-deployment.git
cd openg2p-deployment/automation/sandbox

cp sandbox-config.example.yaml      sandbox-config.yaml
cp environment-config.example.yaml  environment-config.yaml
```

Minimum edits to `sandbox-config.yaml`:

```yaml
domain: "mydept.dedyn.io"          # your real domain

tls:
  email: "admin@yourorg.org"       # Let's Encrypt contact address
  dns_provider: "desec"
  api_token: "<your deSEC token>"
  staging: true                    # recommended for the first run — see below

# Only if you are NOT using AWS provisioning:
node_ip:  "172.29.14.170"          # the VM's private IP
ssh_host: "54.1.2.3"               # public IP reachable from your laptop
ssh_user: "ubuntu"
ssh_key:  "./aws/keys/sandbox.pem"
```

`environment-config.yaml` already contains `environment: "dev"` — no edit needed for a default install.

{% hint style="warning" %}
**Use `staging: true` for your first run.** It obtains certificates from the Let's Encrypt *staging* CA — untrusted by browsers, but with very generous rate limits. Production allows only **50 certificates per week** per registered domain and **5 failed validations per hostname per hour**, so a config problem discovered on production limits can lock you out for an hour. Once a run succeeds end-to-end, set `staging: false` and re-run with `--force`.
{% endhint %}

## Step 4: Check before you install

```bash
./openg2p-sandbox.sh --config sandbox-config.yaml --check
```

This validates the configuration and calls your DNS provider's API to confirm the token works **and** that the domain exists in that account. It makes **no SSH connection and changes nothing** — use it freely.

Exit code `0` means you are ready.

## Step 5: Install

```bash
./openg2p-sandbox.sh --config sandbox-config.yaml
```

The installer prints what it is about to do, verifies the DNS/TLS prerequisites again, and asks for confirmation before touching the VM (`--yes` skips the prompt). Expect **25–40 minutes**.

By default this installs the infrastructure **and** the `dev` environment (`install_environment: true`).

### What runs

| Stage | Phase | What happens |
|---|---|---|
| **Infra** | 1 | Tools, firewall (private by default), RKE2, Wireguard, NFS, **public A records**, **Let's Encrypt certificate**, Nginx |
| | 2 | Helmfile — Istio, Rancher, monitoring (Prometheus/Grafana), logging (Loki + OpenTelemetry) |
| | 3 | Rancher — admin password, cluster name, custom RBAC roles, OpenG2P chart repo, prerelease charts enabled |
| **Environment** | 1 | DNS records `*.dev.<domain>`, Let's Encrypt wildcard, Nginx server block, namespace, Rancher Project, Istio Gateway |

The run is **idempotent** — re-run it after a failure and completed steps are skipped.

## Step 6: Connect and log in

**1. Wireguard.** The installer pulls `artifacts/peer1.conf` to your laptop. Import it into the [Wireguard client](https://www.wireguard.com/install/) and activate the tunnel.

**2. Open Rancher.**

```
https://rancher.<your-domain>
```

Username `admin`; the password is printed in the completion summary and stored in the `cattle-system/rancher-secret` Kubernetes secret. The certificate is a real Let's Encrypt one, so there should be no browser warning — unless you used `staging: true`.

**3. Verify.**

```bash
nslookup rancher.<your-domain>      # → the VM's IP
kubectl get nodes                   # → one node, Ready (needs the kubeconfig below)
```

The installer also pulls `artifacts/rke2-remote.yaml`:

```bash
export KUBECONFIG=~/path/to/artifacts/rke2-remote.yaml
kubectl get nodes
```

{% hint style="info" %}
If `nslookup` returns nothing, your resolver is stripping private addresses from public DNS answers — "DNS rebinding protection", on by default in pfSense/OPNsense, Fritz!Box and OpenDNS. Confirm with `dig <name> @1.1.1.1`, and either add an exception or point that client at a public resolver.
{% endhint %}

## Configuration reference

### `sandbox-config.yaml`

#### Node and cluster

| Key | Default | Description |
|---|---|---|
| `node_ip` | — | The VM's **private** IP. Used for NFS, Nginx, Kubernetes and the published A records. Auto-filled by AWS provisioning. |
| `node_name` | `node1` | Kubernetes node name, visible in `kubectl get nodes`. |
| `cluster_name` | `openg2p` | Display name in the Rancher UI; also the NFS export path prefix. |

#### Domain and TLS

| Key | Default | Description |
|---|---|---|
| `domain` | — | **Required.** Your real registered domain, e.g. `mydept.dedyn.io`. Hostnames derive from it: `rancher.<domain>`, `<env>.<domain>`. Reserved TLDs are rejected. |
| `tls.email` | — | **Required.** Contact address registered with Let's Encrypt (expiry and problem notices). |
| `tls.dns_provider` | `desec` | Where `domain`'s DNS is hosted: `desec`, `cloudflare`, `route53`, `acmedns`. |
| `tls.api_token` | — | deSEC API token, or Cloudflare API token. Must be **unrestricted** for deSEC. |
| `tls.cf_account_id` | — | Cloudflare only. |
| `tls.aws_access_key_id` / `tls.aws_secret_access_key` | — | Route 53 only. Blank uses the EC2 instance role. |
| `tls.acmedns_*` | — | acme-dns only (`base_url`, `username`, `password`, `subdomain`). |
| `tls.publish_a_records` | `true` | Publish A records for the hostnames. Set `false` to manage DNS yourself. |
| `tls.dns_propagation_seconds` | `120` | Wait after writing the ACME challenge record before validation. Raise to `300` if validation fails with "No TXT record found". `0` uses the ACME client's adaptive check. |
| `tls.staging` | `false` | Use the Let's Encrypt staging CA — untrusted certificates, generous limits. **Set `true` for first runs.** |

#### Access

| Key | Default | Description |
|---|---|---|
| `public_access` | `false` | `false` = `80/443` reachable only via Wireguard/VPC. `true` = open to `0.0.0.0/0`. See the warning in [Access model](#access-model--private-by-default). |

#### Wireguard

| Key | Default | Description |
|---|---|---|
| `wireguard.endpoint` | `node_ip` | Public IP or hostname VPN clients dial. Set when the VM's public IP differs from `node_ip`. |
| `wireguard.subnet` | `10.15.0.0/16` | VPN subnet. |
| `wireguard.port` | `51820` | UDP listen port. |
| `wireguard.peers` | `254` | Number of peer configs pre-generated. |
| `wireguard.peer_dns` | — | Optional DNS server pushed to peers. Set to e.g. `1.1.1.1` if a client's own resolver strips private-IP answers. |

#### SSH (laptop orchestrator only)

| Key | Default | Description |
|---|---|---|
| `ssh_host` | — | Public IP/hostname reachable from your laptop. |
| `ssh_user` | `ubuntu` | SSH user with passwordless sudo. |
| `ssh_key` | — | Path to the private key, e.g. `./aws/keys/sandbox.pem`. |

#### Stages and platform

| Key | Default | Description |
|---|---|---|
| `install_environment` | `true` | Install the environment named in `environment-config.yaml` after infra. `false` stops after infra. |
| `rke2_version` | `v1.33.6+rke2r1` | RKE2 version. |
| `rke2_token` | auto | Cluster join token; generated if blank. |
| `rancher.version` | `2.12.3` | Rancher chart version. |
| `rancher.replicas` | `1` | Rancher replica count. |

#### Observability

| Key | Default | Description |
|---|---|---|
| `loki_retention_hours` | `168` | Log retention (7 days). |
| `loki_minio_root_user` | `loki` | Internal object store user for Loki. |
| `loki_minio_root_password` | auto | Generated if blank; saved under `/etc/openg2p/secrets`. |
| `loki_minio_size` | `50Gi` | PVC size for Loki's MinIO. |
| `alert_slack_webhook_url`, `alert_slack_channel` | — | Slack/Mattermost/Rocket.Chat alerting. |
| `alert_smtp_*` | — | Email alerting (`smarthost`, `from`, `username`, `password`, `to`). |
| `alert_telegram_bot_token`, `alert_telegram_chat_id` | — | Telegram alerting. |
| `ai_enabled` | `false` | Optional AI log-analysis layer. Observability works fully without it. |
| `ai_openrouter_api_key`, `ai_model` | — | Only when `ai_enabled: true`. |

### `environment-config.yaml`

| Key | Default | Description |
|---|---|---|
| `environment` | `dev` | Environment name. Becomes the Kubernetes namespace, the Rancher Project name and the sub-domain label. |
| `base_domain` | — | Leave blank to derive `<environment>.<domain>`. Set explicitly only to use a domain outside `domain` — in which case DNS records are **not** managed for you. |
| `sandbox_config` | `sandbox-config.yaml` | Path to the sandbox config, for inherited values (`node_ip`, `domain`, `tls.*`). |

### Command-line flags

| Flag | Description |
|---|---|
| `--config <file>` | Path to `sandbox-config.yaml` (required). |
| `--env-config <file>` | Path to `environment-config.yaml`. Auto-detected if blank. |
| `--provision-output <file>` | AWS overlay. Auto-detected if blank. |
| `--stage <all\|infra\|environment>` | What to run. Default `all`. |
| `--phase <n>` | Pass a phase through to the on-box script (infra `1`,`2`,`3`). |
| `--check` | Validate config and DNS/TLS prerequisites, then exit. No SSH, no changes. |
| `--probe` | SSH-probe the VM and exit. |
| `--force` | Ignore completion markers and re-run. |
| `--dry-run` | Print what would run; change nothing. |
| `--yes`, `-y` | Skip the interactive confirmation. |
| `--skip-environment` | Run infra only for this run. |
| `--reset-laptop` | Clear laptop-side state markers. |

## Adding another environment

Environments are tracked separately, so adding one leaves the others untouched:

```bash
# edit environment-config.yaml → environment: "qa"
./openg2p-sandbox.sh --config sandbox-config.yaml --stage environment
```

Each environment gets its own DNS records, its own wildcard certificate, its own Nginx server block, and its own namespace, Rancher Project and Istio Gateway.

{% hint style="info" %}
An environment is deliberately **empty of applications**. Deploy into the namespace afterwards via **Rancher → Apps** (the OpenG2P chart repository is pre-registered and prerelease versions are enabled for the admin user), with `helm` directly, or with `automation/environment/`.
{% endhint %}

## User access & roles

Rancher uses local authentication — every user that needs the UI is created in Rancher itself:

1. Log in as `admin`.
2. **☰ → Users & Authentication → Users → Create**.
3. Assign a global role (*Standard User*, or *Administrator* for a super-admin).

Rancher's built-in project roles all include full Secrets access, so the installer creates two extra roles that exclude secrets:

| Role | Source | Secrets | Permissions |
|---|---|---|---|
| Project Owner | built-in | full | full control of the project |
| Project Member | built-in | full | CRUD on workloads, services, configs, secrets |
| **Project Member (No Secrets)** | created by the installer | none | as Project Member, minus secrets |
| **Project Read-Only (No Secrets)** | created by the installer | none | view-only, no secrets |

To grant access to an environment: **Rancher → Project `<env>` → Members → Add Member**.

{% hint style="info" %}
New Rancher users must enable prerelease charts themselves to see the OpenG2P catalogue (**avatar → Preferences → Helm Charts → Include Prerelease Versions**). The installer sets this for `admin` only — Rancher has no cluster-wide default for it.
{% endhint %}

## Scale up

A sandbox is one VM, but the cluster can be expanded when you outgrow it.

**Adding a Kubernetes node.** Nginx, NFS and the Istio ingress gateway stay on the first node; a new node is a pure Kubernetes worker. It joins RKE2, runs pods, mounts NFS over the network, and traffic reaches it through the first node's Nginx → Istio → cluster networking. Nothing about DNS or certificates changes — hostnames still resolve to the first node.

Two things to keep in mind:

* The new node must be in the **same `/16` subnet** as the first — the firewall rules for the Kubernetes API, kubelet, VXLAN and NFS are derived from `node_ip`.
* NFS remains on the first node, so expanding compute does not make storage redundant. That is precisely what the [production topology](../) separates.

A dedicated add-node script is provided separately.

**Adding environments.** The same sandbox script creates as many environments as you need — see [Adding another environment](#adding-another-environment). This works identically before or after adding nodes.

## Uninstalling

```bash
# one environment (leaves the infrastructure intact)
./roles/environment/uninstall.sh --config environment-config.yaml

# everything on the VM (keeps the VM itself)
./openg2p-sandbox-uninstall.sh --config sandbox-config.yaml
```

{% hint style="warning" %}
Neither removes the DNS records from your provider. Delete them yourself (for example at [https://desec.io/domains](https://desec.io/domains)) if the sandbox is gone for good.
{% endhint %}

## Troubleshooting

**A step failed — re-run it.** The install is idempotent; completed steps are skipped.

**`--check` fails on the deSEC token.** The token must be **unrestricted**. A token limited by deSEC token policies can read a domain but not *list* domains, which the ACME client needs for zone detection.

**Certificate fails with `NXDOMAIN looking up TXT`.** A resolver cached the "does not exist" answer from before the record was created. It clears within the zone's negative TTL (typically 5 minutes); re-run after waiting.

**Certificate fails with `No TXT record found`.** The challenge record had not propagated to all of your provider's nameservers before validation. Raise `tls.dns_propagation_seconds` to `300` and re-run.

{% hint style="warning" %}
Let's Encrypt permits only **5 failed validations per hostname per hour**. If issuance fails repeatedly, stop and diagnose rather than retrying — and use `tls.staging: true` while investigating.
{% endhint %}

**Hostnames do not resolve on your laptop.** Your resolver is likely filtering private-IP answers. Test with `dig <name> @1.1.1.1`; add a rebinding exception or set `wireguard.peer_dns: "1.1.1.1"`.

**Browser warns about the certificate.** You are on `tls.staging: true`. Set it to `false` and re-run with `--force`.

**Cluster status:**

```bash
kubectl get nodes
kubectl get pods -A | grep -v Running
helm list -A
journalctl -u rke2-server -n 50
```

## File structure

```
automation/sandbox/
├── openg2p-sandbox.sh                 # laptop orchestrator
├── openg2p-sandbox-uninstall.sh
├── sandbox-config.example.yaml        # the sandbox (VM, domain, TLS, access)
├── environment-config.example.yaml    # one environment
├── helmfile-infra.yaml.gotmpl         # platform Helm releases
├── roles/
│   ├── infra/{run.sh, uninstall.sh}
│   └── environment/{run.sh, uninstall.sh}
├── lib/
│   ├── acme.sh        # Let's Encrypt + DNS provider integration
│   ├── phase1.sh      # host setup, firewall, RKE2, Wireguard, NFS, DNS+TLS, Nginx
│   ├── phase2.sh      # Istio, Rancher, monitoring, logging
│   ├── phase3.sh      # Rancher config, RBAC roles, chart repo
│   ├── env-phase1.sh  # environment: DNS, cert, Nginx, namespace, project, gateway
│   ├── utils.sh, ssh-utils.sh
├── charts/
└── aws/                               # optional AWS provisioning
```

## Related documentation

* [AWS Provisioning](aws-provisioning.md) — provision the VM on AWS
* [OpenG2P Deployment Architecture](../../../../deployment/openg2p-deployment-model.md#sandbox-single-node) — how sandbox compares to production
* [Production (three-node)](../) — the production topology
