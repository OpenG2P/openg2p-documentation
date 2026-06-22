---
description: >-
  What must be in place before installing OpenG2P in production — compute,
  DNS records, TLS certificate, server access, firewall.
---

# Prerequisites & Procurement

This page assumes a **single production environment** and a DevOps reader. It lists the procurement requirements only — install steps live on the [Infrastructure Automation](infrastructure-setup/production-automation/) page. Conceptual background lives in [OpenG2P Deployment Architecture](../../deployment/openg2p-deployment-model.md) and [DNS & TLS Certificates](deployment-guide/dns-and-certificates.md).

{% hint style="info" %}
**Production deployment flow:**  **1. Procurement** (this page)  →  [2. Provisioning](infrastructure-setup/provisioning.md)  →  [3. Infrastructure](infrastructure-setup/production-automation/)  →  [4. Environment](environment-setup-multi-node.md)  →  [5. Modules](environment-setup-multi-node.md#next-install-your-openg2p-modules)
{% endhint %}

{% hint style="warning" %}
**Start procurement first — before touching any server.** The two long-lead items are **compute** (capacity approval + VM provisioning) and **TLS certificates** (issuance from a commercial or sovereign CA typically takes **2–4 weeks**). Request both at the very start so neither lands on the critical path.
{% endhint %}

{% hint style="info" %}
**Operator's workstation** — while procurement is in flight, the operator running the install (you) should ensure your laptop or jump host is set up. See [Operator's workstation](infrastructure-setup/provisioning.md#operators-workstation) for supported OSes (Linux / macOS / WSL2) and the required tooling per stage.
{% endhint %}

## On-prem or AWS?

Both are supported. The requirements are identical **except** for the four points below — each is flagged inline where it applies.

| Differs                             | On-prem                                                                | AWS (self-provisioned)                      |
| ----------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------- |
| Public address of the Reverse Proxy | Public IP on the NIC, or a NAT/DNAT address on your perimeter firewall | Elastic IP allocated to the RP instance     |
| Where admin DNS records live        | Internal / split-horizon DNS                                           | Route 53 **private** hosted zone on the VPC |
| How firewall rules are applied      | Perimeter firewall / router ACLs                                       | Security Group inbound rules                |
| DNS resolver for admin VPN clients  | Your internal DNS server IP                                            | VPC DNS resolver (`<vpc-base>.2`)           |

{% hint style="info" %}
This page assumes the four VMs (Reverse Proxy, Compute, Storage, Backup) are **already provisioned**. On AWS you may use your own Terraform / console / CloudFormation — the bundled `openg2p-aws-provision.sh` is optional.
{% endhint %}

## Deployment-specific values

The requirements below refer to these values. Determine them for your deployment first.

| Value           | Example                    | What it is                                                                                                                                                                     |
| --------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `DOMAIN`        | `prod.openg2p.gov.example` | The base domain. Every hostname is a subdomain of it                                                                                                                           |
| `RP_PRIVATE_IP` | `10.0.1.10`                | The Reverse-Proxy VM's primary NIC IP. Admin hostnames resolve here (reachable only over the VPN)                                                                              |
| `RP_PUBLIC_IP`  | `198.51.100.5`             | The RP's internet-reachable address; also the Wireguard endpoint. **On AWS:** the Elastic IP. **On-prem:** the public IP, or the NAT/DNAT address your firewall maps to the RP |
| `ADMIN_CIDR`    | `203.0.113.5/32`           | Public IP `/32` (or office range) allowed to SSH to the VMs — the deployer's workstation or jump host                                                                          |
| `SSH_USER`      | `ubuntu`                   | Linux user with passwordless sudo on the VMs                                                                                                                                   |

## What to procure

### Compute (the four VMs)

Provision four Ubuntu Server 24.04 LTS machines on the same private subnet, with internet egress available during install (apt, RKE2, Helm charts). Each is **single-NIC** — channel separation is handled by the firewall + nginx, not by extra interfaces (see [Channel separation](../../deployment/openg2p-deployment-model.md#channel-separation-public-vs-private-access)).

| Role          | vCPU | RAM   | Root disk      | Notes                                                                         |
| ------------- | ---- | ----- | -------------- | ----------------------------------------------------------------------------- |
| Reverse Proxy | 2    | 4 GB  | 64 GB SSD      | TLS termination, Wireguard endpoint. Not expected to be heavily loaded.       |
| Compute       | 16   | 64 GB | 128 GB SSD     | The Kubernetes node. Fits \~2 environments with all modules; expand for more. |
| Storage       | 8    | 32 GB | 256 GB SSD     | Host PostgreSQL + NFS. Expand CPU/RAM if PostgreSQL is heavily loaded.        |
| Backup        | 4    | 8 GB  | 64 GB root + ≥1 TB repo | Holds the backup repository (pgBackRest + restic) — required before go-live. The backup install **hard-fails below 4 vCPU / 8 GB**. The repo lives on a separate data volume (≥1 TB recommended; HDD acceptable — smaller = shorter retention). |

These are minimums; larger is fine and smaller may fail preflight.

* **On-prem:** provision on your hypervisor (capacity approval + VM creation is itself a procurement lead-time item — request early).
* **On AWS:** equivalent instance types are roughly `t3a.medium` (RP), `m5a.4xlarge` (Compute), `t3a.2xlarge` (Storage), and `t3a.xlarge` (Backup, with a separate ≥1 TB gp3 data volume for the repo), each with a gp3 root volume. You may provision with your own tooling, or use the bundled `openg2p-aws-provision.sh`.

### DNS records

Three A records. The admin hostname points to the **private** IP (reachable only over the VPN); the apex and wildcard point to the **public** IP (citizen-facing). The per-environment service hostnames (`keycloak.`, `minio.`, `superset.`, …) are covered by the wildcard and reached over the VPN once the environment stage runs.

| Hostname                | Type | Points to       | Channel          |
| ----------------------- | ---- | --------------- | ---------------- |
| `rancher.<DOMAIN>`      | A    | `RP_PRIVATE_IP` | Admin (VPN-only) |
| `<DOMAIN>` (apex)       | A    | `RP_PUBLIC_IP`  | Citizen          |
| `*.<DOMAIN>` (wildcard) | A    | `RP_PUBLIC_IP`  | Citizen          |

The explicit `rancher.` record takes precedence over the wildcard, so the two IP targets coexist cleanly.

**Where to create them:**

* **Admin records** (→ private IP) must resolve for VPN-connected admins. **On-prem:** internal / split-horizon DNS. **On AWS:** a Route 53 **private** hosted zone attached to the VPC.
* **Citizen records** (→ public IP): public DNS — a Route 53 public zone on AWS, or your public authoritative DNS on-prem.

> Example, for `DOMAIN = prod.openg2p.gov.example`, `RP_PRIVATE_IP = 10.0.1.10`, `RP_PUBLIC_IP = 198.51.100.5`: `rancher.prod.openg2p.gov.example` → `10.0.1.10`, `prod.openg2p.gov.example` → `198.51.100.5`, `*.prod.openg2p.gov.example` → `198.51.100.5`.

### TLS certificate

**One wildcard certificate** for `*.<DOMAIN>`, with SANs covering both `*.<DOMAIN>` and the apex `<DOMAIN>`. This single cert serves the admin hostname (`rancher`), every per-environment service (`keycloak`, `minio`, `superset`, …), and every citizen-facing service, since all are subdomains of `<DOMAIN>` — see [Why a single wildcard certificate](prerequisites-procurement.md#why-a-single-wildcard-certificate).

Accepted formats (the install scripts auto-detect):

| Format                          | Files                                                       |
| ------------------------------- | ----------------------------------------------------------- |
| PEM fullchain + key (preferred) | `<DOMAIN>.fullchain.pem` + `<DOMAIN>.key`                   |
| Separate PEM                    | `<DOMAIN>.cert.pem` + `<DOMAIN>.chain.pem` + `<DOMAIN>.key` |
| PFX / P12                       | `<DOMAIN>.pfx` (or `.p12`) + the password                   |
| ZIP bundle (Sectigo / DigiCert) | `<DOMAIN>.zip`                                              |

The cert team delivers the issued **files** to the deployer (secure transfer — SFTP, encrypted mail, or a secrets vault). They need **no access to the OpenG2P servers** — the install automation places the files on the server. The deployer then references them by path in `prod-config.yaml`; see [Infrastructure Automation → Step 1](infrastructure-setup/production-automation/#step-1-clone-and-configure).

{% hint style="warning" %}
**Don't use Let's Encrypt for production.** It's fine for a sandbox or PoC, but most governments require certs from a commercial CA (DigiCert, GlobalSign, Sectigo) or their national / sovereign CA. The installer defaults to customer-provided certs; Let's Encrypt is a sandbox-only option.
{% endhint %}

{% hint style="info" %}
**Advanced — separate admin domain.** This page assumes one domain for both admin and citizen hostnames (the common case). If your organisation requires admin tools on a wholly separate domain, procure a second wildcard cert and set the per-service `*_hostname` / `tls_*` keys in `prod-config.yaml`. See the [Infrastructure Automation](infrastructure-setup/production-automation/) page for the config-key details.
{% endhint %}

### Server access

SSH with **passwordless sudo** to all four VMs (Reverse-Proxy, Compute, Storage, Backup), as `SSH_USER`, from `ADMIN_CIDR`.

### Network ports (firewall)

Ingress rules at the network boundary. The per-host firewall (`ufw`) is configured automatically by the installer — your team only sets the boundary rules.

#### Reverse Proxy

| Port    | Proto | Source         | Purpose                                  | Opened at         |
| ------- | ----- | -------------- | ---------------------------------------- | ----------------- |
| 22      | TCP   | `ADMIN_CIDR`   | Admin SSH                                | infra setup       |
| 51820   | UDP   | `0.0.0.0/0`    | Wireguard VPN endpoint                   | infra setup       |
| all     | any   | private subnet | Intra-cluster traffic                    | infra setup       |
| 80, 443 | TCP   | `0.0.0.0/0`    | Citizen-facing HTTP/HTTPS                | environment setup |

#### Compute

| Port | Proto | Source         | Purpose                | Opened at   |
| ---- | ----- | -------------- | ---------------------- | ----------- |
| 22   | TCP   | `ADMIN_CIDR`   | Admin SSH              | infra setup |
| all  | any   | private subnet | Kubernetes / cluster   | infra setup |

#### Storage

| Port | Proto | Source         | Purpose                       | Opened at   |
| ---- | ----- | -------------- | ----------------------------- | ----------- |
| 22   | TCP   | `ADMIN_CIDR`   | Admin SSH                     | infra setup |
| 2049 | TCP   | private subnet | NFS (from compute)            | infra setup |
| 5432 | TCP   | private subnet | PostgreSQL (from compute)     | infra setup |

* **Admin tools (Rancher) and per-environment service UIs (Keycloak, MinIO, Superset, …) are never exposed publicly** — reached only over the Wireguard VPN. Public `80/443` serve citizen-facing services only.
* Public `80/443` are opened at the **environment-setup** stage, not during infra setup — see [environment setup](environment-setup-multi-node.md). You may open them upfront or defer; either is fine.
* Apply these as **Security Group** inbound rules (AWS) or **perimeter-firewall / router ACLs** (on-prem).

## Next: install

Once everything above is in place — DNS records created, certificate files in hand on the deployer's workstation, server access and firewall confirmed — continue with the [production infrastructure automation](infrastructure-setup/production-automation/). The install guide takes you through placing the cert files locally, configuring `prod-config.yaml`, validating, and running the install.


## Related pages

* [Production infrastructure automation](infrastructure-setup/production-automation/) — install the cluster once certs are in place
* [Environment setup](environment-setup-multi-node.md) — install OpenG2P modules into the production environment
* [DNS & TLS Certificates](deployment-guide/dns-and-certificates.md) — cert formats in government procurement
* [Private Access Channel](deployment-guide/private-access-channel.md) — why admin tools sit behind the VPN
