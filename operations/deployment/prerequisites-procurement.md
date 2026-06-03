---
description: >-
  What must be in place before installing OpenG2P in production — DNS records,
  TLS certificate, server access, firewall — plus the steps to install once
  the certificate is issued.
---

# Prerequisites & Procurement

What must be in place before any OpenG2P installation runs. The [three-node infrastructure automation](infrastructure-setup/three-node-automation/) and the [environment setup](environment-setup-multi-node.md) both link here as the first prerequisite.

This page assumes a **single production environment** and a DevOps reader. Procurement requirements come first, then the install steps once the certificate arrives; conceptual background is in [Reference notes](#reference-notes).

{% hint style="warning" %}
**Start procurement first — before touching any server.** The two long-lead items are **compute** (capacity approval + VM provisioning) and **TLS certificates** (issuance from a commercial or sovereign CA typically takes **2–4 weeks**). Request both at the very start so neither lands on the critical path.
{% endhint %}

## On-prem or AWS?

Both are supported. The requirements are identical **except** for the four points below — each is flagged inline where it applies.

| Differs | On-prem | AWS (self-provisioned) |
| --- | --- | --- |
| Public address of the Reverse Proxy | Public IP on the NIC, or a NAT/DNAT address on your perimeter firewall | Elastic IP allocated to the RP instance |
| Where admin DNS records live | Internal / split-horizon DNS | Route 53 **private** hosted zone on the VPC |
| How firewall rules are applied | Perimeter firewall / router ACLs | Security Group inbound rules |
| DNS resolver for admin VPN clients | Your internal DNS server IP | VPC DNS resolver (`<vpc-base>.2`) |

{% hint style="info" %}
This page assumes the three VMs (Reverse Proxy, Compute, Storage) are **already provisioned**. On AWS you may use your own Terraform / console / CloudFormation — the bundled `openg2p-aws-provision.sh` is optional.
{% endhint %}

## Deployment-specific values

The requirements below refer to these values. Determine them for your deployment first.

| Value | Example | What it is |
| --- | --- | --- |
| `DOMAIN` | `prod.openg2p.gov.example` | The base domain. Every hostname is a subdomain of it |
| `RP_PRIVATE_IP` | `10.0.1.10` | The Reverse-Proxy VM's primary NIC IP. Admin hostnames resolve here (reachable only over the VPN) |
| `RP_PUBLIC_IP` | `198.51.100.5` | The RP's internet-reachable address; also the Wireguard endpoint. **On AWS:** the Elastic IP. **On-prem:** the public IP, or the NAT/DNAT address your firewall maps to the RP |
| `ADMIN_CIDR` | `203.0.113.5/32` | Public IP `/32` (or office range) allowed to SSH to the VMs — the deployer's workstation or jump host |
| `SSH_USER` | `ubuntu` | Linux user with passwordless sudo on the VMs |

## What to procure

### Compute (the three VMs)

Provision three Ubuntu Server 24.04 LTS machines on the same private subnet, with internet egress available during install (apt, RKE2, Helm charts). Each is **single-NIC** — channel separation is handled by the firewall + nginx, not by extra interfaces (see [Channel separation](infrastructure-setup/three-node-automation/README.md#channel-separation-keeping-admin-tools-off-the-public-internet)).

| Role | vCPU | RAM | Root disk | Notes |
| --- | --- | --- | --- | --- |
| Reverse Proxy | 2 | 4 GB | 64 GB SSD | TLS termination, Wireguard endpoint. Not expected to be heavily loaded. |
| Compute | 16 | 64 GB | 128 GB SSD | The Kubernetes node. Fits ~2 environments with all modules; expand for more. |
| Storage | 8 | 32 GB | 256 GB SSD | Host PostgreSQL + NFS. Expand CPU/RAM if PostgreSQL is heavily loaded. |
| Backup (optional) | 2 | 8 GB | 512 GB HDD/SSD | Only if you enable the backup node. SSD not required. |

These are minimums; larger is fine and smaller may fail preflight.

* **On-prem:** provision on your hypervisor (capacity approval + VM creation is itself a procurement lead-time item — request early).
* **On AWS:** equivalent instance types are roughly `t3a.medium` (RP), `m5a.4xlarge` (Compute), `t3a.2xlarge` (Storage), each with a gp3 root volume. You may provision with your own tooling, or use the bundled `openg2p-aws-provision.sh`.

### DNS records

Four A records. Admin hostnames point to the **private** IP (reachable only over the VPN); the apex and wildcard point to the **public** IP (citizen-facing).

| Hostname | Type | Points to | Channel |
| --- | --- | --- | --- |
| `rancher.<DOMAIN>` | A | `RP_PRIVATE_IP` | Admin (VPN-only) |
| `keycloak.<DOMAIN>` | A | `RP_PRIVATE_IP` | Admin (VPN-only) |
| `<DOMAIN>` (apex) | A | `RP_PUBLIC_IP` | Citizen |
| `*.<DOMAIN>` (wildcard) | A | `RP_PUBLIC_IP` | Citizen |

Explicit records (`rancher.`, `keycloak.`) take precedence over the wildcard, so the two IP targets coexist cleanly.

**Where to create them:**
* **Admin records** (→ private IP) must resolve for VPN-connected admins. **On-prem:** internal / split-horizon DNS. **On AWS:** a Route 53 **private** hosted zone attached to the VPC.
* **Citizen records** (→ public IP): public DNS — a Route 53 public zone on AWS, or your public authoritative DNS on-prem.

> Example, for `DOMAIN = prod.openg2p.gov.example`, `RP_PRIVATE_IP = 10.0.1.10`, `RP_PUBLIC_IP = 198.51.100.5`:
> `rancher.prod.openg2p.gov.example` → `10.0.1.10`, `keycloak.prod.openg2p.gov.example` → `10.0.1.10`, `prod.openg2p.gov.example` → `198.51.100.5`, `*.prod.openg2p.gov.example` → `198.51.100.5`.

### TLS certificate

**One wildcard certificate** for `*.<DOMAIN>`, with SANs covering both `*.<DOMAIN>` and the apex `<DOMAIN>`. This single cert serves the admin hostnames (`rancher`, `keycloak`) and every citizen-facing service, since all are subdomains of `<DOMAIN>` — see [Why a single wildcard certificate](#why-a-single-wildcard-certificate).

Accepted formats (the install scripts auto-detect):

| Format | Files |
| --- | --- |
| PEM fullchain + key (preferred) | `<DOMAIN>.fullchain.pem` + `<DOMAIN>.key` |
| Separate PEM | `<DOMAIN>.cert.pem` + `<DOMAIN>.chain.pem` + `<DOMAIN>.key` |
| PFX / P12 | `<DOMAIN>.pfx` (or `.p12`) + the password |
| ZIP bundle (Sectigo / DigiCert) | `<DOMAIN>.zip` |

The cert team delivers the issued **files** to the deployer (secure transfer — SFTP, encrypted mail, or a secrets vault). They need **no access to the OpenG2P servers** — the install automation places the files on the server. Installing them is covered in [After procurement](#after-procurement-installing-with-your-certificate).

{% hint style="warning" %}
**Don't use Let's Encrypt for production.** It's fine for a sandbox or PoC, but most governments require certs from a commercial CA (DigiCert, GlobalSign, Sectigo) or their national / sovereign CA. The installer defaults to customer-provided certs; Let's Encrypt is a sandbox-only option.
{% endhint %}

### Server access

SSH with **passwordless sudo** to all three VMs (Reverse-Proxy, Compute, Storage), as `SSH_USER`, from `ADMIN_CIDR`.

### Network ports (firewall)

Ingress rules at the network boundary. The per-host firewall (`ufw`) is configured automatically by the installer — your team only sets the boundary rules.

| Node | Port | Proto | Source | Purpose | Opened at |
| --- | --- | --- | --- | --- | --- |
| Reverse Proxy | 22 | TCP | `ADMIN_CIDR` | Admin SSH | infra setup |
| Reverse Proxy | 51820 | UDP | `0.0.0.0/0` | Wireguard VPN endpoint | infra setup |
| Reverse Proxy | all | any | private subnet | Intra-cluster traffic | infra setup |
| Reverse Proxy | 80, 443 | TCP | `0.0.0.0/0` | Citizen-facing HTTP/HTTPS | environment setup |
| Compute | 22 | TCP | `ADMIN_CIDR` | Admin SSH | infra setup |
| Compute | all | any | private subnet | Kubernetes / cluster | infra setup |
| Storage | 22 | TCP | `ADMIN_CIDR` | Admin SSH | infra setup |
| Storage | 2049 | TCP | private subnet | NFS (from compute) | infra setup |
| Storage | 5432 | TCP | private subnet | PostgreSQL (from compute) | infra setup |

* **Admin tools (Rancher, Keycloak) are never exposed publicly** — reached only over the Wireguard VPN. Public `80/443` serve citizen-facing services only.
* Public `80/443` are opened at the **environment-setup** stage, not during infra setup — see [environment setup](environment-setup-multi-node.md). You may open them upfront or defer; either is fine.
* Apply these as **Security Group** inbound rules (AWS) or **perimeter-firewall / router ACLs** (on-prem).

## After procurement: installing with your certificate

Once the cert team hands you the issued **files**, the deployer installs them — you never copy certs to the server by hand. On your workstation:

1. Put the received cert + key in a folder next to your config, e.g. `./certs/`.
2. Point `prod-config.yaml` at those **local** paths:
   ```yaml
   tls_wildcard_cert: "./certs/prod.openg2p.gov.example.fullchain.pem"
   tls_wildcard_key:  "./certs/prod.openg2p.gov.example.key"
   ```
3. Validate the certificate without running the full install:
   ```bash
   ./openg2p-prod.sh --validate-certs --config prod-config.yaml
   ```
   This checks each cert: parses as PEM, key matches cert, not expired, and the SAN covers the configured hostnames.
4. Run the install. The orchestrator uploads the files from your workstation and installs them on the Reverse-Proxy node.

Continue with the [three-node infrastructure automation](infrastructure-setup/three-node-automation/).

## Reference notes

Conceptual background. Skip if you just need the requirements.

### Admin vs citizen hostnames (private vs public)

Rancher and Keycloak are **operator tools**, not citizen-facing. The installer keeps them reachable only over the Wireguard VPN (bound to the private IP, with a firewall + nginx allowlist), which is why `rancher.<DOMAIN>` and `keycloak.<DOMAIN>` point to the **private** IP. Citizen-facing services are reached on the **public** IP, which is why the apex and wildcard point there. Full rationale: [Private Access Channel](../../deployment/deployment-guide/private-access-channel.md) and [Channel separation](infrastructure-setup/three-node-automation/README.md#channel-separation-keeping-admin-tools-off-the-public-internet).

### Why a single wildcard certificate

Every service is a subdomain of `<DOMAIN>` — `rancher.`, `keycloak.`, and citizen services like `registry.`, `esignet.`, `minio.`, `superset.`. One wildcard cert (`*.<DOMAIN>`, including the apex) covers them all, so procurement is **one cert** instead of one per service.

### How admin hostnames resolve from your laptop

After connecting to the VPN, your laptop resolves the admin hostnames to the RP's private IP. The `wg_peer_dns` setting in `prod-config.yaml` pushes a resolver to every Wireguard peer:

* **On-prem:** your internal DNS server's IP (inside the routed subnet, so the query crosses the tunnel).
* **On AWS:** the VPC DNS resolver at `<vpc-cidr-base>.2` (e.g. `10.0.0.2` for a `10.0.0.0/16` VPC), which resolves the Route 53 private hosted zone.

A one-time `/etc/hosts` entry on the laptop also works for either topology; the installer prints the exact line in its completion summary.

### Certificate formats in government procurement

For the cert formats commonly delivered by government / sovereign / commercial CAs and how the installer handles each, see [DNS & TLS Certificates](../../deployment/concepts/dns-and-certificates.md).

### Using a separate admin domain (advanced)

This page uses one domain for both admin and citizen hostnames — the common case. If your organisation requires admin tools on a wholly separate domain, procure a second wildcard cert for that domain and set the per-service `*_hostname` / `tls_*` keys in `prod-config.yaml`. See the [three-node automation](infrastructure-setup/three-node-automation/) page.

## Related pages

* [Three-node infrastructure automation](infrastructure-setup/three-node-automation/) — install the cluster once certs are in place
* [Environment setup](environment-setup-multi-node.md) — install OpenG2P modules into the production environment
* [DNS & TLS Certificates](../../deployment/concepts/dns-and-certificates.md) — cert formats in government procurement
* [Private Access Channel](../../deployment/deployment-guide/private-access-channel.md) — why admin tools sit behind the VPN
