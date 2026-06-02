---
description: >-
  Three-node production deployment automation — one orchestrator script that
  drives a Reverse Proxy, Compute (Kubernetes), and Storage node from the
  admin's laptop, with optional AWS provisioning.
---

# Production - Three-Node

The three-node automation provisions a complete production OpenG2P infrastructure across three Ubuntu 24.04 VMs from your laptop, with a single command. It is the production counterpart to [Single-Node Automation](../single-node-automation.md): same logging, same idempotency, same general structure, but split across three role-specialised machines.

{% hint style="info" %}
The source code lives in the [`openg2p-deployment`](https://github.com/OpenG2P/openg2p-deployment) repository under `automation/production/`. The optional AWS provisioning lives at `automation/production/aws/`.
{% endhint %}

## Key concepts

The three-node deployment model itself — what each node does, why the split exists, and where it fits between single-node and full-scale — is described in [OpenG2P Deployment Architecture](../../../../deployment/concepts/openg2p-deployment-model.md#three-node). This page is about the **automation** that brings it up.

### The three roles

<table><thead><tr><th width="180">Role</th><th>What runs on it</th><th>Public-facing?</th></tr></thead><tbody><tr><td><strong>Reverse Proxy</strong></td><td>Nginx (TLS terminator, two-channel: public + private), Wireguard server</td><td>Yes — public IP, Wireguard endpoint</td></tr><tr><td><strong>Compute</strong></td><td>RKE2 single-control-plane Kubernetes, Istio, Rancher, Keycloak (admin SSO), Prometheus + Grafana, Fluentd + OpenSearch, NFS client</td><td>No — only reachable via the reverse proxy or Wireguard</td></tr><tr><td><strong>Storage</strong></td><td>NFS server (cluster persistent storage), host-installed PostgreSQL (ready for environment automation)</td><td>No — private subnet only</td></tr></tbody></table>

### Why admin tools live behind Wireguard

Rancher and Keycloak are **operator tools**, not citizen-facing services. The automation makes them reachable only from the reverse-proxy node's private interface (vNIC-internal), served on hostnames the customer provides — `rancher.<your-domain>` and `keycloak.<your-domain>`. The customer also provides real certs for those hostnames (commercial CA, sovereign CA, etc. — see [Prerequisites § 4](./#id-4.-customer-supplied-tls-certificates)). Admin laptops connect via Wireguard, terminated on the RP's public interface; once the tunnel is up, traffic to the admin hostnames routes via the internal interface.

Grafana and Prometheus ship as part of the install but are **not** exposed on their own hostnames — they're reached from inside the Rancher UI (**Cluster Explorer → Monitoring**), so no dedicated DNS records or certs are needed for them.

This is deliberate. Government customers almost universally require admin tools to be VPN-only, have security policies that flag publicly exposed admin panels, and procure certs from their own CAs (rarely Let's Encrypt).

{% hint style="info" %}
For the full discussion of cert formats commonly seen in gov procurement (PEM split bundles, PFX, sovereign CAs) and why per-FQDN dominates over wildcards, see [DNS & TLS Certificates](../../../../deployment/concepts/dns-and-certificates.md).
{% endhint %}

### Channel separation: public vs private on the RP

The RP has two network interfaces (see [Prerequisites § 2](./#id-2.-two-network-interfaces-on-the-reverse-proxy-vm)):

* **vNIC-public** — public IP. Wireguard server binds here. Future env-automation will bind public citizen-facing Nginx server blocks here too.
* **vNIC-internal** — internal IP. Admin Nginx server blocks bind here (rancher, keycloak). The compute and storage nodes also live on this network.

Nginx server blocks for each hostname are bound to a specific IP, so the two channels can't bleed into each other. Public traffic can never reach an admin hostname; only Wireguard peers (whose tunnel exits on the internal interface) can.

The [Private Access Channel](../../../../deployment/deployment-guide/private-access-channel.md) concept page covers the underlying pattern; this automation implements the single-channel admin/private channel out of the box, and the public channel becomes meaningful once env automation lands.

### Idempotent and resumable

Each node tracks completed steps in `/var/lib/openg2p/deploy-state/*.done`. Re-running the orchestrator (or any role's phase) skips completed steps and resumes from where it left off. Use `--force` to ignore markers and rerun everything.

### Two-file configuration

| File                    | Author                                                                      | Contains                                                                                                                                 | Loaded                           |
| ----------------------- | --------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------- |
| `prod-config.yaml`      | You author it                                                               | preferences: `cluster_name`, `public_domain`, hostnames per service, cert paths, versions, `keycloak_admin_email`, `postgres_*`, `nfs_*` | First                            |
| `provision-output.yaml` | Auto-generated by AWS provisioning (or filled by hand for non-AWS installs) | provisioning state: IPs, SSH paths, `private_subnet`, `admin_cidr`, `wg_endpoint`                                                        | Second — overrides matching keys |

The orchestrator auto-loads `provision-output.yaml` next to `prod-config.yaml`. Re-running AWS provisioning regenerates `provision-output.yaml` cleanly without touching your hand-edited preferences.

## Technology

| Component       | Version                                     | Notes                                                                           |
| --------------- | ------------------------------------------- | ------------------------------------------------------------------------------- |
| OS              | Ubuntu Server 24.04 LTS                     | All three nodes                                                                 |
| Orchestrator    | bash + ssh + rsync                          | Runs on your laptop, no extra dependencies                                      |
| Kubernetes      | RKE2 v1.33.6                                | Single control-plane on the compute node                                        |
| Service mesh    | Istio 1.24.1                                | Installed via `istioctl`                                                        |
| Helm            | v3.17.3                                     | + helm-diff plugin                                                              |
| Helmfile        | v1.1.0                                      | Drives the platform component installs                                          |
| Cluster manager | Rancher 2.12.3                              | In-cluster, with embedded Postgres                                              |
| Auth            | Keycloak (in-cluster)                       | SSO for Rancher only — embedded Postgres on NFS-backed PVC                      |
| Monitoring      | Rancher monitoring 105.0.0                  | Prometheus + Grafana                                                            |
| Logging         | Rancher logging 102.0.0                     | Fluentd + OpenSearch                                                            |
| Storage         | NFS-CSI driver v4.7.0                       | Default StorageClass `nfs-csi`, retain policy                                   |
| VPN             | Wireguard (kernel + tools)                  | Native systemd service on the RP node                                           |
| DNS             | Customer-provided (no DNS server installed) | Hostnames resolved by customer's authoritative DNS or admin-laptop `/etc/hosts` |
| Database (host) | PostgreSQL 16                               | On the storage node, ready for environment automation                           |

## Prerequisites

{% hint style="warning" %}
**Plan all environments up front.** The DNS records and TLS certs listed below cover only the admin tools (Rancher, optional Keycloak). Each environment you intend to bring up (dev, qa, prod, …) needs its own DNS records + wildcard cert too — and TLS issuance from sovereign or commercial CAs typically takes **2-4 weeks**.

Run the [unified procurement workflow](../../prerequisites-procurement.md) at the start of the deployment: fill out one `deployment-plan.yaml` covering infra + every planned environment, generate a single checklist, and hand it to your IT / network / cert team. This avoids serial procurement cycles mid-deployment.
{% endhint %}

This section is **self-contained** — everything you need to have ready before running the automation. The orchestrator's `--preflight` mode mechanically verifies every item below and refuses to start if any is missing, with a clear error message and a link back to this section.

### 1. Three Ubuntu 24.04 VMs

|                       | Reverse Proxy                                    | Compute                 | Storage                  |
| --------------------- | ------------------------------------------------ | ----------------------- | ------------------------ |
| **OS**                | Ubuntu Server 24.04 LTS                          | Ubuntu Server 24.04 LTS | Ubuntu Server 24.04 LTS  |
| **vCPU minimum**      | 2                                                | 16                      | 8                        |
| **RAM minimum**       | 4 GB                                             | 64 GB                   | 32 GB                    |
| **Root disk minimum** | 64 GB                                            | 128 GB                  | 256 GB                   |
| **Disk type**         | SSD recommended                                  | SSD recommended         | SSD strongly recommended |
| **Network**           | All three on the same private subnet             |                         |                          |
| **Internet egress**   | Required during install (apt, RKE2, Helm charts) |                         |                          |

See [Resource Requirements](../../../../deployment/resource-requirements.md) for the full table per deployment model.

### 2. Two network interfaces on the Reverse Proxy VM

The RP node terminates **two** network channels:

* **Public channel** — Wireguard endpoint + (in env-automation later) citizen-facing services. Reachable from the internet.
* **Private channel** — Nginx server blocks for the admin tools. Reachable only via Wireguard or the internal network.

For the two channels to be enforced cleanly, the RP needs **two separate IPs** — one per channel — and they must be on **different network interfaces**. SNI / Host-header differentiation on a single IP is NOT enough: anyone able to reach the public IP on 443 could set the Host header and bypass the channel separation.

The standard pattern is:

| Interface       | Network                 | Used for                                                           |
| --------------- | ----------------------- | ------------------------------------------------------------------ |
| `vNIC-public`   | DMZ / public-facing     | Wireguard UDP, public Nginx server blocks                          |
| `vNIC-internal` | internal mgmt / cluster | Admin Nginx server blocks (rancher, keycloak)                       |

Adding the second vNIC is a sysadmin task done **before** running the automation. It's trivial on every common hypervisor:

| Hypervisor                     | How to add the second vNIC                                                    |
| ------------------------------ | ----------------------------------------------------------------------------- |
| VMware vSphere / ESXi          | Point-and-click in vCenter; hot-add supported                                 |
| KVM / libvirt (`virt-manager`) | XML edit or one click; hot-add supported                                      |
| Proxmox VE                     | Web UI; seconds                                                               |
| Microsoft Hyper-V              | Hyper-V Manager → Add Hardware → Network Adapter                              |
| Nutanix AHV                    | Prism Element / Central                                                       |
| OpenStack                      | Multiple ports per instance — built into the API                              |
| oVirt / RHV                    | Per-VM NIC management                                                         |
| Bare metal                     | Use a second physical NIC, or a VLAN-tagged sub-interface on the existing one |

If you genuinely cannot add a second vNIC (rare on modern hypervisors), see [Fallback: two Nginx VMs](three-node-automation-fallback-second-rp.md).

### 3. Customer-supplied DNS records

The automation does NOT install any DNS server. Your authoritative DNS must resolve the following hostnames:

| Hostname                   | DNS A-record →                               | Channel | Purpose                                          |
| -------------------------- | -------------------------------------------- | ------- | ------------------------------------------------ |
| `rancher.<your-domain>`    | RP's **internal** IP (the vNIC-internal one) | private | Rancher cluster manager UI                       |
| `keycloak.<your-domain>`   | RP's **internal** IP                         | private | Keycloak admin SSO (Rancher's identity provider) |

`<your-domain>` is whatever your organisation uses (e.g. `openg2p.gov.eth`). The two hostnames don't have to share the exact prefix shown — you can use `rancher-admin.gov.eth`, `sso.gov.eth`, etc. — but the automation defaults expect the `<service>.<domain>` shape; override per-service in `prod-config.yaml` if you need different names.

{% hint style="info" %}
**Why only two?** Grafana and Prometheus run in-cluster as part of `rancher-monitoring`, but they're reached from inside the Rancher UI (**Cluster Explorer → Monitoring → Grafana / Prometheus**) — so they don't need their own DNS records or TLS certs. Any `grafana_hostname` / `prometheus_hostname` / `tls_grafana_*` / `tls_prometheus_*` keys in `prod-config.yaml` are ignored by the automation.
{% endhint %}

Admin laptops must be able to resolve these hostnames. Three working patterns:

1. **Split-horizon DNS** (recommended) — your internal DNS resolves these to the RP's internal IP; public DNS doesn't expose them. Admin laptops reach the internal DNS via Wireguard.
2. **Public DNS pointing at the private IP** — anyone can resolve the name, but the IP is private; only Wireguard peers can reach it. Acceptable for many gov setups.
3. **`/etc/hosts` on the admin laptop** — fully manual. The orchestrator prints the exact lines in the completion summary; you append them once per laptop.

### 4. Customer-supplied TLS certificates

The automation does NOT generate certs. You provide one cert+key per admin hostname (or one wildcard covering all four). Government CAs typically deliver certificates in one of these formats — all are supported:

| Format                  | Files you provide                                       | Notes                                                                                |
| ----------------------- | ------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| **PEM fullchain + key** | `<host>.fullchain.pem`, `<host>.key`                    | Native Nginx format. Most CAs can produce this on request.                           |
| **Separate PEM**        | `<host>.cert.pem`, `<host>.chain.pem`, `<host>.key.pem` | Auto-concatenated into a fullchain by the script. Common from commercial CAs.        |
| **PFX / P12**           | `<host>.pfx` (with password)                            | Windows IIS / Microsoft AD CS export. Converted with `openssl pkcs12` by the script. |
| **ZIP bundle**          | `<host>.zip` (Sectigo/DigiCert layout)                  | Auto-detected and extracted.                                                         |

The customer drops the cert files in a directory on **your laptop** (not the RP). Reference them by path in `prod-config.yaml`. The script:

1. **Validates locally** on your laptop before any push:
   * Cert covers the declared hostname (SAN/CN match, including wildcards)
   * Key matches cert (modulus / pubkey hash)
   * Chain is complete
   * Expires more than 30 days out (warn at 14, fail at 7)
   * Issued by a trusted CA (warn-only — sovereign / internal CAs are accepted)
2. **Normalizes** to PEM fullchain + key.
3. **Uploads** to `/etc/openg2p/certs/public/<hostname>/` on the RP (`fullchain.pem` 0644, `privkey.pem` 0600, root:root).
4. **Atomic-swap** into Nginx, with rollback if `nginx -t` fails on the new config.

See [DNS & TLS Certificates](../../../../deployment/concepts/dns-and-certificates.md) for the deeper discussion on cert formats, per-FQDN vs wildcards in gov environments, and the validation pipeline.

You can also pre-validate certs without running an install:

```bash
./openg2p-prod.sh --validate-certs --config prod-config.yaml
```

Iterate until every cert reports green before you commit to the install.

### 5. Customer-supplied SSH access

* Key-based SSH from the admin's laptop to each of the three VMs.
* The SSH user on each VM has **passwordless sudo** (`NOPASSWD:ALL` in `/etc/sudoers.d/<user>`) or you SSH as root directly.

### 6. On the admin's laptop

* **`bash` 4 or later** (`bash --version`). macOS ships `/bin/bash` 3.2 by default — install a newer one with `brew install bash` and make sure it's first in `PATH`. Linux distros ship 4+ by default.
* `ssh`, `rsync` (preinstalled on macOS and Linux).
* `openssl` (preinstalled on macOS and Linux) — used by the local cert validator.
* A Wireguard client (only needed AFTER install, to reach the admin tools).
* The cert files from your customer / CA, in any of the supported formats above.

### 7. What this automation does NOT need

Explicitly so:

* **No git server, no Docker registry, no backup node.** Deferred to follow-up automation.
* **No public DNS for the admin hostnames** (point them at private IPs; access is via Wireguard).
* **No Let's Encrypt or any other ACME client.** Government deployments universally use procured certs from sovereign or commercial CAs.
* **No local CA / self-signed certs.** Earlier versions of the automation used a self-signed CA for admin tools; this is no longer supported. Real certs only.

### Preflight verification

The orchestrator's `--preflight` mode (and the implicit preflight at the start of an end-to-end run) mechanically validates everything in this section:

```bash
./openg2p-prod.sh --preflight --config prod-config.yaml
```

For each item that fails, the error message tells you exactly what's wrong and links back here. Example failures and what to fix:

| Preflight error                                                        | Fix                                                                                          |
| ---------------------------------------------------------------------- | -------------------------------------------------------------------------------------------- |
| `RP node has only 1 network interface`                                 | Add a second vNIC (see [section 2](./#id-2.-two-network-interfaces-on-the-reverse-proxy-vm)) |
| `DNS: rancher.<domain> does not resolve`                               | Add the A-record (see [section 3](./#id-3.-customer-supplied-dns-records))                   |
| `DNS: rancher.<domain> resolves to 1.2.3.4 but RP internal is 5.6.7.8` | DNS points at the wrong IP — fix the A-record                                                |
| `Cert ./certs/rancher.pem: does not cover hostname rancher.<domain>`   | Wrong cert for that hostname (see [section 4](./#id-4.-customer-supplied-tls-certificates))  |
| `Cert ./certs/rancher.pem: key does not match cert`                    | Mismatched cert/key pair                                                                     |
| `RAM: 3 GB (need ≥4)`                                                  | Resize the VM (see [section 1](./#id-1.-three-ubuntu-24.04-vms))                             |

Preflight is non-destructive — it makes no changes. Run it until everything's green, then run the full install.

## How to use the script

### Step 0 (optional) — provision the VMs on AWS

If you don't already have three Ubuntu VMs, the bundled AWS provisioning creates them for you. See [AWS provisioning](./#aws-provisioning) below.

If you have your own VMs (other clouds, on-prem, manual EC2), skip to step 1.

### Step 1 — clone and configure

On your laptop:

```bash
git clone https://github.com/OpenG2P/openg2p-deployment.git
cd openg2p-deployment/automation/production
cp prod-config.example.yaml prod-config.yaml
```

Edit `prod-config.yaml`. The example config has every key tagged either `[USER]` (you fill in), `[CUSTOMER]` (provided by customer / govt — hostnames, certs), or `[AWS]` (auto-populated by AWS provisioning, or you fill in for non-AWS installs):

```yaml
# [USER] preferences
cluster_name: "openg2p"
keycloak_admin_email: "admin@yourcorp.gov.eth"
postgres_version: "16"
wg_subnet: "10.15.0.0/16"
wg_port: "51820"

# [CUSTOMER] domain (DNS A-records for rancher.<domain> and keycloak.<domain>
# must already exist, both pointing at the RP's INTERNAL IP — see
# Prerequisites § 3. Grafana/Prometheus are reached via the Rancher UI, no
# dedicated DNS needed.)
public_domain: "openg2p.gov.eth"
# Override individual hostnames only if your customer uses non-standard names:
# rancher_hostname:    "k8s-admin.dept.gov"
# keycloak_hostname:   "sso.dept.gov"

# [CUSTOMER] TLS certs (paths on YOUR laptop; uploaded to RP at install time)
# Either provide one wildcard cert covering both hostnames:
tls_wildcard_cert: "./certs/wildcard.fullchain.pem"
tls_wildcard_key:  "./certs/wildcard.key"
# OR provide per-FQDN certs (leave wildcard blank, fill these):
# tls_rancher_cert:    "./certs/rancher.fullchain.pem"
# tls_rancher_key:     "./certs/rancher.key"
# tls_keycloak_cert:   "./certs/keycloak.fullchain.pem"
# tls_keycloak_key:    "./certs/keycloak.key"

# [AWS|MANUAL] node networking — auto-populated by AWS provisioning,
# or fill in manually for on-prem
rp_public_ip:       ""    # vNIC-public address, also the Wireguard endpoint
rp_internal_ip:     ""    # vNIC-internal address, Nginx binds admin server blocks here
compute_private_ip: ""
storage_private_ip: ""
private_subnet:     ""
# ... and corresponding *_ssh_host, *_ssh_user, *_ssh_key, admin_cidr
```

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

Total runtime: 25–40 minutes. The orchestrator runs phases in this order:

| # | Where         | What                                                                                                                                                         |
| - | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 0 | Laptop        | SSH + sudo probe on all 3 nodes                                                                                                                              |
| 0 | All 3 nodes   | Preflight: OS, CPU, RAM, disk, internet, IP-matches-config (in parallel)                                                                                     |
| 1 | Storage       | apt basics, ufw, NFS server export, host PostgreSQL install (no app DBs yet)                                                                                 |
| 2 | Compute       | apt basics, kubectl/helm/istioctl/helmfile, ufw, NFS client mount, RKE2 server, NFS CSI default StorageClass                                                 |
| 3 | Reverse Proxy | apt basics, ufw, second-NIC bring-up, Wireguard server + peer configs, customer cert ingest + validate + install, Nginx server blocks bound to vNIC-internal |
| 4 | Compute       | helmfile sync — Istio, Rancher, Keycloak (with NFS-backed embedded Postgres), monitoring, logging                                                            |
| 5 | Compute       | Rancher-Keycloak SAML integration                                                                                                                            |

### Common command shapes

```bash
# Run only one role end-to-end
./openg2p-prod.sh --config prod-config.yaml --role storage
./openg2p-prod.sh --config prod-config.yaml --role compute
./openg2p-prod.sh --config prod-config.yaml --role rp

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

When the orchestrator finishes it prints a **completion summary** with both passwords (Rancher local admin + Keycloak admin), the URLs, and the exact commands for each step below — keep that summary handy while you go through this section the first time.

The four things to do, once, on your laptop:

#### 4.1 Pull the Wireguard peer config and connect

The peer file on the RP node is owned by `root`, so we read it via `sudo cat` over SSH and write it locally:

```bash
ssh -i <your-key> ubuntu@<rp-public-ip> \
    "sudo cat /etc/wireguard/peers/peer1/peer1.conf" > peer1.conf
```

Install a Wireguard client and import this file:

| OS              | Where to get the client                                                           |
| --------------- | --------------------------------------------------------------------------------- |
| macOS           | [Wireguard from the App Store](https://apps.apple.com/app/wireguard/id1451685025) |
| Windows / Linux | [wireguard.com/install](https://www.wireguard.com/install/)                       |
| iOS / Android   | App Store / Play Store                                                            |

In the app: **Add Tunnel → Import from file/archive → choose `peer1.conf` → Activate**.

Verify the tunnel is up:

```bash
ping 10.15.0.1   # the RP's WG-side IP — must respond
```

{% hint style="info" %}
The peer config uses **split tunnel** by default — only the Wireguard subnet (`10.15.0.0/16`) and the cluster's private subnet are routed through the VPN. Your normal internet stays direct.
{% endhint %}

#### 4.2 (Skipped — no local CA)

Since you're using **real certs from your customer's CA** (see [Prerequisites § 4](./#id-4.-customer-supplied-tls-certificates)), there's no CA to install on your laptop. Browsers already trust the issuing CA. If you see a cert warning when first opening Rancher, that's a real issue — your cert chain probably isn't complete; re-run `--validate-certs` and the pre-flight will catch it.

#### 4.3 DNS resolution on your laptop

You need your laptop to resolve the admin hostnames (`rancher.<domain>` and `keycloak.<domain>`) to the RP's **internal** IP. Three working patterns:

1.  **Customer's DNS reachable through Wireguard** (preferred) — the WG peer config can include the customer's internal DNS resolver. Edit `peer1.conf` after pulling it (or have the customer add it):

    ```
    [Interface]
    ...
    DNS = <customer-internal-dns-IP>
    ```
2.  **`/etc/hosts` on your laptop** — manual but reliable. The orchestrator's completion summary prints the exact lines. Append once per laptop:

    ```
    <RP-internal-IP>  rancher.openg2p.gov.eth keycloak.openg2p.gov.eth
    ```
3. **Public DNS pointing at the private IP** — if the customer's authoritative DNS is public-facing and OK with publishing private-IP A-records, the hostnames resolve from anywhere (but only WG-connected laptops can actually reach the IP).

{% hint style="warning" %}
On macOS, don't use `dig` to test — it bypasses the system resolver and will give NXDOMAIN even when everything works. Use `dscacheutil -q host -a name rancher.<domain>`, `ping`, or `curl`.
{% endhint %}

#### 4.4 Login to Rancher — the recommended flow

There are two distinct logins. The first time you connect, do them in this order:

**Step A — Login with the LOCAL Rancher admin first**

Open `https://rancher.<your-domain>` in your browser (the hostname you put in `rancher_hostname`). On the Rancher login page, click **"Use a local user"** (the small link below the big "Login with Keycloak" button).

* **Username**: `admin`
*   **Password**: shown in the orchestrator's completion summary; or fetch it from the cluster:

    ```bash
    export KUBECONFIG=~/.kube/openg2p-prod   # see "kubectl access" below
    kubectl -n cattle-system get secret rancher-secret \
      -o jsonpath='{.data.adminPassword}' | base64 -d && echo
    ```

You're now in Rancher as the local admin. Use this session to take a quick look around.

**Step B — Find the Keycloak admin password (optional, for confirmation)**

While logged in to Rancher, browse to: **`local` cluster → Storage → Secrets → keycloak-system → keycloak**. Reveal the `admin-password` value. This is the same password the orchestrator's summary printed; the Rancher UI just gives you a click-to-reveal way to find it without using kubectl.

**Step C — Logout, then login again with Keycloak SSO**

In Rancher, click your avatar (top-right) → **Log Out**. You're back at the login screen.

Now click the big **"Login with Keycloak"** button. Your browser is redirected to `https://keycloak.<your-domain>/...` — the URL change confirms you're on the Keycloak login form, not Rancher's.

* **Username**: the email you set in `keycloak_admin_email`.
* **Password**: the Keycloak admin password (from the orchestrator summary, or step B above).

Keycloak authenticates you, signs a SAML assertion, and redirects you back to Rancher. You should land on the Rancher home page as the Keycloak-authenticated admin. **SAML SSO is now verified working.**

{% hint style="success" %}
From now on, day-to-day admins should use "Login with Keycloak". Manage user accounts in Keycloak, assign Rancher roles via Rancher's **Members** UI. The local `admin` is a fallback for when Keycloak is unavailable — guard the password accordingly.
{% endhint %}

#### 4.5 (Optional) kubectl from your laptop

If you want to run `kubectl` directly against the cluster (instead of going through the Rancher UI):

```bash
mkdir -p ~/.kube
ssh -i <your-key> ubuntu@<compute-private-ip> \
    "sudo cat /etc/rancher/rke2/rke2-remote.yaml" > ~/.kube/openg2p-prod
chmod 600 ~/.kube/openg2p-prod
export KUBECONFIG=~/.kube/openg2p-prod
kubectl get nodes
```

Requires Wireguard active — the K8s API listens on the compute node's private IP, only reachable through the VPN.

## What this automation DOES

* Provisions a working production OpenG2P infrastructure on three Ubuntu 24.04 VMs.
* Hard-enforces resource and network requirements via preflight — no surprise failures 18 minutes into an install.
* Configures Wireguard + Nginx on the RP node with **customer-supplied DNS and TLS certs** (the customer's CA — sovereign, commercial, internal PKI), validates the certs locally before push, and serves the admin tools on a dedicated private network interface (vNIC-internal).
* Installs Rancher, Keycloak (admin SSO), monitoring (Prometheus + Grafana), and logging (Fluentd + OpenSearch) via Helmfile.
* Wires Rancher-Keycloak SAML integration so admins log in once via Keycloak.
* Configures the storage node with NFS export and host PostgreSQL (PG16), ready for environment automation to create per-environment databases on per-environment ports. The auto-generated superuser password is saved at `/etc/openg2p/secrets/postgres-superuser.env` on the storage node (and printed in the orchestrator's completion summary).
* Is fully **idempotent and resumable** — re-running picks up where the last run left off.

## What this automation DOES NOT do (yet)

These are deferred to follow-up automation, not gaps:

* **Environment automation** — creating `prod`, `staging`, etc. namespaces with their own Postgres, Keycloak, eSignet, Superset, etc. The host PostgreSQL on the storage node sits idle until that lands.
* **Citizen-facing public domains and certs** — admin tools (the four hostnames in this automation) are private channel only. Public citizen-facing hostnames (`registry.<env>.<domain>`, `payments.<env>.<domain>`, etc.) come with environment automation, on the same RP's public NIC. See [DNS & TLS Certificates](../../../../deployment/concepts/dns-and-certificates.md).
* **Local Docker registry** — RKE2 pulls images from upstream. A pull-through cache mirror will come in a later phase.
* **Local Git repository** — deferred.
* **Air-gap / offline operation** — initial install requires internet. Self-contained operation is a later phase.
* **Backup node and backup automation** — out of scope for v1.
* **Domain migration script** — single-node has one (`openg2p-migrate-domain.sh`); will be ported when environment automation lands.

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

Open `https://rancher.<your-domain>`. You should see the Rancher login page with a **Login with Keycloak** button — and **no certificate warning** (your customer-supplied cert chains to a publicly-trusted CA).

#### 4. kubectl

```bash
export KUBECONFIG=~/.kube/openg2p-prod
kubectl get nodes
kubectl get pods -A | grep -v Running
```

The first command should show the compute node `Ready`. The second should be empty (or only show known transient pods like helm hooks).

### On the reverse-proxy node

```bash
sudo systemctl is-active wg-quick@wg0       # active
sudo systemctl is-active nginx              # active
sudo nginx -t                               # syntax OK
sudo ss -tlnp | grep -E ':80|:443'          # nginx bound to vNIC-internal IP
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

The PostgreSQL superuser password is auto-generated by storage phase 1 and saved at `/etc/openg2p/secrets/postgres-superuser.env` on the storage node (root-owned, mode `0600`). The file contains `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER` (always `postgres`), and `POSTGRES_PASSWORD`. The orchestrator's completion summary also prints these values directly. **No application uses this database yet** — it sits idle until environment automation creates per-environment databases on per-environment ports.

## File structure

```
automation/production/
├── openg2p-prod.sh                    # Laptop orchestrator
├── prod-config.example.yaml           # Single config file (flat YAML)
├── helmfile-infra.yaml.gotmpl         # Platform helmfile (Istio EnvoyFilter,
│                                       Rancher, Keycloak, monitoring, logging)
├── lib/
│   ├── ssh-utils.sh                   # ControlMaster SSH, rsync push/pull
│   └── shared/
│       ├── utils.sh                   # logging, state, config loader
│       ├── preflight.sh               # Per-node resource + network checks
│       ├── hostnames.sh               # Hostname helpers + config-key bridge
│       └── phase3.sh                  # Vendored Rancher-Keycloak SAML
├── charts/
│   ├── raw/                           # Minimal chart for K8s manifests
│   └── istio-install/                 # Istio operator config
├── aws/                                # See AWS provisioning section below
└── roles/
    ├── reverse-proxy/{run.sh,phase1.sh}
    ├── compute/{run.sh,phase1.sh,phase2.sh}
    └── storage/{run.sh,phase1.sh}
```

## AWS provisioning

The bundled AWS provisioning is a separate, optional step that creates the three EC2 instances and the supporting AWS resources, then writes `provision-output.yaml` for the orchestrator to consume. Lives at `automation/production/aws/`.

### Prerequisites

|                     |                                                                                                                                                       |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **AWS CLI**         | v2 installed on your laptop. `aws --version` should print `aws-cli/2.x`.                                                                              |
| **AWS credentials** | Configured via `aws configure`, environment variables, or an `AWS_PROFILE`. The script honours `AWS_REGION`, `AWS_PROFILE`, and `AWS_DEFAULT_REGION`. |
| **`jq`**            | Not required (we deliberately avoid the dependency).                                                                                                  |
| **Permissions**     | The IAM user/role needs the EC2 permissions listed below.                                                                                             |
| **EIP quota**       | At least **one Elastic IP free** in the target region. AWS's default per-region quota is 5 EIPs. An EIP is **required** (not optional) — see [About the Elastic IP](#about-the-elastic-ip) for why. If you're at quota, free one first (see [troubleshooting](#aws-provision-eip-addresslimitexceeded)) before running the provisioner. |

### IAM permissions

The provisioning script needs a moderately broad set of EC2 permissions. The minimal set:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ec2:DescribeVpcs",
      "ec2:DescribeSubnets",
      "ec2:DescribeImages",
      "ec2:DescribeInstances",
      "ec2:DescribeInstanceStatus",
      "ec2:DescribeKeyPairs",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeAddresses",
      "ec2:DescribeNetworkInterfaces",
      "ec2:CreateKeyPair",
      "ec2:DeleteKeyPair",
      "ec2:CreateSecurityGroup",
      "ec2:DeleteSecurityGroup",
      "ec2:AuthorizeSecurityGroupIngress",
      "ec2:RevokeSecurityGroupIngress",
      "ec2:AllocateAddress",
      "ec2:ReleaseAddress",
      "ec2:AssociateAddress",
      "ec2:DisassociateAddress",
      "ec2:RunInstances",
      "ec2:TerminateInstances",
      "ec2:ModifyInstanceAttribute",
      "ec2:CreateTags",
      "sts:GetCallerIdentity",
      "tag:GetResources"
    ],
    "Resource": "*"
  }]
}
```

If you have full EC2 admin (`AmazonEC2FullAccess` managed policy + `sts:GetCallerIdentity` + `tag:GetResources`), that works too.

### What gets created

All resources are tagged with `Project=<project>` so the destroy script can find and remove them later.

| Resource           | Default name                          | Configurable          | Notes                                                                                                                                              |
| ------------------ | ------------------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Key pair           | `openg2p-prod-key`                    | `key_name`            | Created if missing; .pem saved to `aws/keys/` mode 0400                                                                                            |
| SG: RP (public)    | `openg2p-prod-reverse-proxy-public`   | `rp_sg_public_name`   | Attached to RP's public ENI (Wireguard endpoint + public services from env automation). Reused if exists; rules added if missing.                  |
| SG: RP (internal)  | `openg2p-prod-reverse-proxy-internal` | `rp_sg_internal_name` | Attached to RP's internal ENI (admin services only, intra-VPC). Reused if exists; rules added if missing.                                          |
| SG: Compute        | `openg2p-prod-k8s-node`               | `compute_sg_name`     | Same                                                                                                                                               |
| SG: Storage        | `openg2p-prod-storage`                | `storage_sg_name`     | Same                                                                                                                                               |
| **Elastic IP**     | tagged `Role=reverse-proxy-eip`       | —                     | **Mandatory** — one EIP allocated and associated with the RP's public ENI. Script **hard-fails** on `AddressLimitExceeded`. See below for why.    |
| Instance: RP       | `openg2p-prod-reverse-proxy`          | `rp_name`             | `t3a.medium`, 64 GB gp3, **two ENIs** (public + internal)                                                                                          |
| Instance: Compute  | `openg2p-prod-k8s-node-1`             | `compute_name`        | `m5a.4xlarge`, 128 GB gp3                                                                                                                          |
| Instance: Storage  | `openg2p-prod-storage`                | `storage_name`        | `t3a.2xlarge`, 256 GB gp3                                                                                                                          |

### Default sizing

Matches the OpenG2P resource minimums.

| Role          | Instance type | vCPU | RAM   | Root disk (gp3) |
| ------------- | ------------- | ---- | ----- | --------------- |
| Reverse Proxy | `t3a.medium`  | 2    | 4 GB  | 64 GB           |
| Compute / K8s | `m5a.4xlarge` | 16   | 64 GB | 128 GB          |
| Storage       | `t3a.2xlarge` | 8    | 32 GB | 256 GB          |

All sizes are configurable in `aws-config.yaml` via `*_instance_type`, `*_disk_gb`, `*_disk_iops`, `*_disk_throughput`. Larger is fine; smaller may fail the orchestrator's preflight.

### About the Elastic IP

Only the reverse-proxy node gets an Elastic IP. Compute and storage use AWS's auto-assigned dynamic public IPs (which is fine — those public IPs are only used for SSH from your laptop).

**The EIP is mandatory — not optional.** There are two reasons:

1. **AWS multi-ENI launch forbids auto-assigned public IPs.** The RP is launched with **two network interfaces** (public + internal) to enforce channel separation between the Wireguard endpoint and the admin Nginx (see [Channel separation](#channel-separation-public-vs-private-on-the-rp)). AWS's `RunInstances` API rejects `AssociatePublicIpAddress=true` whenever more than one ENI is specified at launch. So the RP comes up with **no public IP at all** unless we explicitly allocate and associate an EIP after launch. Without the EIP, the RP would be unreachable from the internet — no Wireguard, no admin access.

2. **Wireguard endpoint stability across stop/start.** The WG `Endpoint` line in every peer config is the RP's public IP. An EIP survives instance stop/start; a dynamic IP would not. Even if AWS allowed auto-assigned IPs on multi-ENI launches (it doesn't), we'd still want an EIP for this reason.

**Behaviour when the EIP quota is exhausted:** if your AWS account is at the default 5-EIP per-region limit, `AllocateAddress` returns `AddressLimitExceeded` and the provisioner **hard-fails** at step 2 ("Allocating Elastic IP for RP"). No instances have been launched yet, so there's nothing to clean up — just free an EIP (or request a quota increase) and re-run.

**To check your current EIP usage and free unused ones:**

```bash
# How many EIPs are allocated in this region (compared to the quota of 5):
aws ec2 describe-addresses --query 'length(Addresses)'

# List EIPs that are allocated but not associated with any instance (these are safe to release):
aws ec2 describe-addresses --query 'Addresses[?AssociationId==null].[AllocationId,PublicIp]' --output table

# Release one:
aws ec2 release-address --allocation-id <alloc-id>
```

**During teardown**, `openg2p-aws-destroy.sh` automatically releases every EIP tagged `Project=<project>` (step 2 of the destroy flow), so the EIP returns to your pool for reuse on the next provision. No manual cleanup needed.

### Workflow

```bash
cd automation/production/aws
cp aws-config.example.yaml aws-config.yaml
# Edit aws-config.yaml — minimum: project, region.
# Leave vpc_id, subnet_id, key_mode blank to be prompted interactively.

./openg2p-aws-provision.sh --config aws-config.yaml
# ~5–8 minutes. Creates resources, waits for status checks AND SSH on
# all 3 instances before declaring done. Writes ../provision-output.yaml.

cd ..
cp prod-config.example.yaml prod-config.yaml
# Edit prod-config.yaml — only USER PREFERENCES (no IPs needed).

./openg2p-prod.sh --probe     --config prod-config.yaml
./openg2p-prod.sh --preflight --config prod-config.yaml
./openg2p-prod.sh             --config prod-config.yaml
```

### Interactive selection (default)

When `vpc_id`, `subnet_id`, or `key_mode` are blank in `aws-config.yaml`, the script queries AWS and presents a numbered menu — no need to leave the terminal to look anything up. Example:

```
[INFO] No vpc_id in config — querying available VPCs...
[INFO] Multiple VPCs available in region ap-south-1:
  [1] vpc-0a1b2c3d4e5f67890  10.0.0.0/16 (default)
  [2] vpc-0123456789abcdef0  10.10.0.0/16 — staging
  [3] vpc-abcdef0123456789a  10.20.0.0/16 — prod
  Select [1-3] or paste VPC ID:
```

Your selection is written back to `aws-config.yaml`, so the next run is fully non-interactive. The same applies to subnet selection and key-pair selection (existing AWS key pairs are listed alongside a "Create new" option).

For CI / automation, pass `--non-interactive` and pre-fill all required values. The script will fail loudly (with a list of options) on anything ambiguous.

### Reusing existing security groups

If your infra team has already created security groups, point the `*_sg_name` fields in `aws-config.yaml` at their names. The script:

1. **Reuses** the existing SG (no new SG created).
2. **Verifies** the required ingress rules — adds any that are missing, leaves the rest alone.
3. **Never removes** rules.

Per-rule status is logged so you can see what was added vs already present:

```
+ TCP/22  from 203.0.113.5/32: added
· ICMP    from 203.0.113.5/32: already present
· UDP/51820 (Wireguard) from 0.0.0.0/0: already present
```

### `provision-output.yaml` — what the orchestrator consumes

After AWS provisioning succeeds, the orchestrator's `prod-config.yaml` does not need any IPs or SSH paths. Those live in a sibling file `provision-output.yaml`:

```yaml
# AUTO-GENERATED by aws/openg2p-aws-provision.sh — overwritten on every run.
rp_public_ip:    "13.x.x.x"
rp_private_ip:   "10.0.1.50"
rp_ssh_host:     "13.x.x.x"
rp_ssh_user:     "ubuntu"
rp_ssh_key:      "./aws/keys/openg2p-prod-key.pem"
compute_private_ip:  "10.0.1.51"
compute_ssh_host:    "<dynamic-public>"
# ... etc
private_subnet:  "10.0.0.0/16"
admin_cidr:      "203.0.113.5/32"
wg_endpoint:     "13.x.x.x"
```

The orchestrator auto-detects this file next to `prod-config.yaml` and loads it as an overlay — its keys win on conflict. Re-running AWS provisioning regenerates it cleanly (single `.prev` archive, no timestamped backup churn). Your hand-edited `prod-config.yaml` is never touched.

### Tearing down

```bash
cd automation/production/aws
./openg2p-aws-destroy.sh --config aws-config.yaml
```

Confirms by asking you to type the project name back, then deletes everything tagged `Project=<project>`:

| # | Resource                                                          | How it gets deleted                                                                                                                                                              |
| - | ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | EC2 instances                                                     | `terminate-instances` + wait for `terminated`                                                                                                                                    |
| 1 | Root EBS volumes                                                  | Auto-deleted with the instance (created with `DeleteOnTermination: true`)                                                                                                        |
| 1 | Primary ENI                                                       | Auto-deleted with the instance                                                                                                                                                   |
| 2 | Elastic IPs                                                       | `release-address`                                                                                                                                                                |
| 3 | Security groups                                                   | `delete-security-group`                                                                                                                                                          |
| 4 | Key pair                                                          | **Only deleted if WE created it** (tagged `Project=<project>` `ManagedBy=openg2p-aws-provision`). Pre-existing keys imported by the user are kept. Force-keep with `--keep-key`. |
| 5 | **Stray EBS volumes** in `available` / `creating` / `error` state | Explicit `delete-volume` — catches volumes detached from instances or extras attached after provisioning                                                                         |
| 5 | **Stray snapshots** owned by you, tagged with the project         | Explicit `delete-snapshot`                                                                                                                                                       |
| 5 | **Stray ENIs** in `available` state, tagged                       | Explicit `delete-network-interface`                                                                                                                                              |
| 6 | `../provision-output.yaml`                                        | Removed (stale after teardown)                                                                                                                                                   |
| 7 | Final sweep                                                       | Lists anything **still** tagged `Project=<project>` so leaks are visible                                                                                                         |

A clean teardown ends with `Nothing left tagged Project=<project>`.

{% hint style="warning" %}
The destroy script only touches resources tagged `Project=<project>`. If you've created VPC peering, NAT gateways, EFS file systems, or anything else that you tagged with the same project, those will appear in the final sweep — review the list before assuming "all clean."
{% endhint %}

{% hint style="info" %}
**Before re-provisioning into the same config directory:** the teardown removes `provision-output.yaml`, but it does **not** clear the orchestrator's laptop-side state under `automation/production/.state/`. If you provision new VMs and re-run the install with the same `prod-config.yaml`, those stale markers will make the orchestrator skip every phase. Run `./openg2p-prod.sh --reset-laptop --config prod-config.yaml` after teardown (or before the next install) to start clean.
{% endhint %}

### Costs (rough, us-east-1, on-demand)

| Item                                      | $/hour         | $/month (730 h)                  |
| ----------------------------------------- | -------------- | -------------------------------- |
| `t3a.medium` (RP)                         | $0.0376        | \~$27                            |
| `m5a.4xlarge` (Compute)                   | $0.688         | \~$502                           |
| `t3a.2xlarge` (Storage)                   | $0.301         | \~$220                           |
| EIP (attached)                            | free           | $0                               |
| EIP (released-but-unattached)             | $0.005         | \~$3.65                          |
| EBS gp3 storage (64 + 128 + 256 = 448 GB) | $0.08/GB-month | \~$36                            |
| **Total**                                 |                | **\~$785/month** if running 24/7 |

Stop instances when not using them to drop EC2 charges to near-zero (you still pay for EBS). The EIP stays attached to the (stopped) RP, so the Wireguard endpoint survives stop/start when present.

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

**SSH probe fails with a host-key prompt** — should not happen anymore (the orchestrator uses `StrictHostKeyChecking=no` for ephemeral cloud VMs), but if it does, the SSH error is surfaced verbatim in the `log_error` block. The most common real cause is the laptop's public IP not being in `admin_cidr` on the cloud security group — check what the script set, vs `curl -s https://checkip.amazonaws.com`.

**Compute helmfile sync hangs or errors** — SSH into the compute node:

```bash
sudo KUBECONFIG=/etc/rancher/rke2/rke2.yaml kubectl get pods -A | grep -v Running
sudo KUBECONFIG=/etc/rancher/rke2/rke2.yaml kubectl get events -A --sort-by=.lastTimestamp | tail -30
```

Then re-run only that phase: `./openg2p-prod.sh --config prod-config.yaml --role compute --phase 2`.

### Phase 3 (Rancher / Keycloak SAML)

**Phase 3 reports `Cannot reach Rancher at https://rancher.<internal>`** — the compute node can't resolve or connect to the Rancher hostname. Two checks (run on the compute node):

```bash
grep rancher /etc/hosts                      # entry must point at RP private IP
curl -kv https://rancher.openg2p.internal/ping 2>&1 | head -30
```

If `/etc/hosts` is missing the entry, re-run `--role compute --phase 3` — the script self-heals the `/etc/hosts` block via `ensure_admin_hostnames_in_etc_hosts`. If `curl` returns "Connection refused", nginx on the RP isn't listening on 443 — see the next item.

**Nginx on the RP listens on 0.0.0.0:80 instead of `<rp-private>:443`** — happens when the apt nginx package's default config pre-bound port 80 and a `systemctl reload` didn't transition the listen sockets. Fix: `sudo systemctl restart nginx` on the RP. The current script uses unconditional `restart` (not `reload`) and verifies the bind, so this should not recur.

### Login

**Rancher's "Login with Keycloak" rejects the credentials** — the most common mistake is using the wrong password for the wrong username/page:

* On Keycloak's page (URL `keycloak.openg2p.internal/...`), use the **email** from `keycloak_admin_email` and the password from `keycloak-system/keycloak`.
* On Rancher's local-user page (URL `rancher.openg2p.internal`), use `admin` and the password from `cattle-system/rancher-secret`.

Both passwords are printed live in the orchestrator's completion summary.

**Wireguard connects but `*.openg2p.internal` doesn't resolve on macOS** — `dig` bypasses the macOS resolver and will give NXDOMAIN even when everything works. Use `dscacheutil -q host -a name rancher.openg2p.internal` instead. For reliable per-domain DNS:

```bash
sudo mkdir -p /etc/resolver
echo "nameserver 10.15.0.1" | sudo tee /etc/resolver/openg2p.internal
```

**Wireguard tunnel up, admin URLs work, but I can't reach compute/storage by private IP** — `ping 10.15.0.1` answers, `https://rancher.<domain>` and `https://keycloak.<domain>` load fine, but `ping <compute_private_ip>`, `ssh ubuntu@<storage_private_ip>`, or `kubectl --server=https://<compute_private_ip>:6443` time out. Cause: Ubuntu's ufw ships with `DEFAULT_FORWARD_POLICY="DROP"` and installs its own policy-enforcement chain in `FORWARD`. wg-quick's `PostUp` rules must be **inserted at the top** of `FORWARD` (`-I FORWARD 1 …`) so they match *before* ufw's drop; **appending** them (`-A FORWARD …`) puts them after the drop where they never fire. INPUT traffic (laptop → Nginx on the RP's internal IP) is unaffected, which is why admin URLs keep working; only forwarded traffic (`wg0 → private subnet`) is silently dropped.

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

**AWS provision: "VPC not found"** — some accounts have no default VPC. Either create one (`aws ec2 create-default-vpc`), set `vpc_id` and `subnet_id` explicitly in `aws-config.yaml`, or run with the default `vpc_id: ""` and pick interactively.

**AWS provision: EIP `AddressLimitExceeded`** — the script **hard-fails** at step 2 (no instances launched yet). The RP uses a multi-ENI launch, which AWS doesn't allow with auto-assigned public IPs, so an EIP is mandatory. Free an unused EIP and re-run, or request a quota increase:

```bash
# List EIPs that are allocated but unassociated (safe to release):
aws ec2 describe-addresses --query 'Addresses[?AssociationId==null].[AllocationId,PublicIp]' --output table
aws ec2 release-address --allocation-id <alloc-id>

# Or request a quota increase (default is 5 EIPs/region):
aws service-quotas request-service-quota-increase \
    --service-code ec2 --quota-code L-0263D0A3 --desired-value 10
```

See [About the Elastic IP](#about-the-elastic-ip) for the full explanation of why EIP is mandatory.

**Multiple environments on the same AWS account** — use a different `project:` value in each `aws-config.yaml` (e.g., `openg2p-prod`, `openg2p-staging`). Resources are isolated by tag; the destroy script only touches the configured project.

## Manual uninstall (non-AWS deployments)

For AWS-provisioned setups, `aws/openg2p-aws-destroy.sh` removes everything (see [Tearing down](./#tearing-down) above). For other clouds / on-prem, dedicated uninstall scripts are not included in v1 — clean up manually per node:

```bash
# Compute (Kubernetes node)
sudo /usr/local/bin/rke2-uninstall.sh
sudo rm -rf /etc/openg2p /var/lib/openg2p /mnt/nfs

# Storage
sudo apt purge -y postgresql 'postgresql-contrib*' nfs-kernel-server
sudo rm -rf /etc/openg2p /var/lib/openg2p /srv/nfs

# Reverse Proxy
sudo apt purge -y wireguard-tools dnsmasq nginx
sudo rm -rf /etc/openg2p /etc/wireguard /var/lib/openg2p
sudo rm -f /etc/dnsmasq.d/openg2p.conf /etc/nginx/sites-enabled/openg2p-infra.conf
```

After that, drop your laptop-side `provision-output.yaml` (if you used the AWS path) and the orchestrator's `.state/` directory. Full uninstall automation will land when the environment automation work begins.

## The orchestrator's `.state/` directory

The orchestrator keeps **laptop-side bookkeeping** under `automation/production/.state/orchestrator/*.done` to remember which whole-phase pushes have already been issued (e.g. "storage phase 1 was successfully driven from this laptop"). It is **not** the source of truth for what's installed — that lives on each node under `/var/lib/openg2p/deploy-state/`.

* **Safe to delete?** Yes, any time. Worst case is the orchestrator re-pushes role bundles and re-invokes role scripts; the remote state markers then skip already-done sub-steps, so nothing actually re-runs.
* **Should it be checked in?** No — already gitignored.
* **Quick reset:** `./openg2p-prod.sh --reset-laptop` removes the directory cleanly.

## Related documentation

* [OpenG2P Deployment Architecture](../../../../deployment/concepts/openg2p-deployment-model.md) — the deployment models (single-node / three-node / full-scale) and where this automation fits.
* [DNS & TLS Certificates](../../../../deployment/concepts/dns-and-certificates.md) — why admin tools are internal, why citizen-facing certs are typically per-FQDN, and the cert formats customers actually have.
* [Resource Requirements](../../../../deployment/resource-requirements.md) — minimums per node, by deployment model.
* [Single-Node Automation](../single-node-automation.md) — the simpler counterpart, useful for sandboxes and reading source code patterns shared with three-node.
