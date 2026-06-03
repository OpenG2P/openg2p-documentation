---
description: >-
  Everything to arrange before installing OpenG2P in production — DNS records,
  TLS certificate, server access, firewall. Fill in your values and hand the
  checklist to your network / cert / IT team.
---

# Prerequisites & Procurement

The **single source of truth** for what must be in place before any OpenG2P installation runs. The [three-node infrastructure automation](infrastructure-setup/three-node-automation/) and the [environment setup](environment-setup-multi-node.md) both link here as the first prerequisite.

This page assumes a **single production environment** and a DevOps reader. The step-by-step checklist is kept deliberately lean; background and "why" live in [Reference notes](#reference-notes) at the end and in linked concept pages.

{% hint style="warning" %}
**Start procurement first — before touching any server.** TLS issuance from a commercial or sovereign CA typically takes **2–4 weeks**. Fill in the worksheet, hand the checklist to your network / cert team, and let procurement run in parallel with VM provisioning.
{% endhint %}

## Before you start: on-prem or AWS?

Both are supported, and the steps below are identical **except** for the four points in this table. Each is flagged inline where it applies with **On AWS** / **On-prem** labels.

| Differs | On-prem | AWS (self-provisioned) | Where |
| --- | --- | --- | --- |
| Public address of the Reverse Proxy | Public IP on the NIC, or a NAT/DNAT address on your perimeter firewall | Elastic IP allocated to the RP instance | [Step 1](#step-1-fill-in-your-values) |
| Where admin DNS records live | Internal / split-horizon DNS | Route 53 **private** hosted zone on the VPC | [Step 2 §1](#step-2-hand-this-checklist-to-your-network-cert-team) |
| How firewall rules are applied | Perimeter firewall / router ACLs | Security Group inbound rules | [Step 2 §5](#step-2-hand-this-checklist-to-your-network-cert-team) |
| DNS resolver pushed to admin VPN clients | Your internal DNS server IP | VPC DNS resolver (`<vpc-base>.2`) | [Reference notes](#resolving-admin-hostnames-from-your-laptop) |

{% hint style="info" %}
This guide assumes you have **already provisioned** the three VMs (Reverse Proxy, Compute, Storage). On AWS you may use your own Terraform / console / CloudFormation — the bundled `openg2p-aws-provision.sh` is optional and not required by this guide.
{% endhint %}

## What to procure

| Item | Detail | Quantity |
| --- | --- | --- |
| **DNS A records** | Admin hostnames → RP **private** IP; apex + wildcard → RP **public** IP | 4 |
| **TLS certificate** | One **wildcard** cert for `*.<your-domain>` (must also cover the apex) | 1 |
| **Server access** | SSH with passwordless sudo to all three VMs | 1 admin CIDR |
| **Firewall openings** | Ingress rules at the network boundary (host firewall is automated) | per [§5](#step-2-hand-this-checklist-to-your-network-cert-team) |

A single wildcard cert covers every hostname — admin and citizen-facing alike. See [Why a single wildcard certificate](#why-a-single-wildcard-certificate).

## Step 1 — Fill in your values

Copy this worksheet into your working notes and fill the right-hand column. You'll substitute these into the checklist in Step 2.

| Field | Your value | What it is |
| --- | --- | --- |
| `ORG_NAME` | _e.g. "Country X Ministry of Social Welfare"_ | Goes on the certificate subject and the procurement-request header |
| `DOMAIN` | _e.g. `prod.openg2p.gov.example`_ | The base domain for this deployment. Every hostname is a subdomain of it |
| `RP_PRIVATE_IP` | _e.g. `10.0.1.10`_ | The Reverse-Proxy VM's primary NIC IP. Admin hostnames resolve here (reachable only over the VPN) |
| `RP_PUBLIC_IP` | _e.g. `198.51.100.5`_ | The RP's internet-reachable address. Citizen hostnames resolve here; also the Wireguard endpoint. **On AWS:** the Elastic IP. **On-prem:** the public IP, or the NAT/DNAT address your firewall maps to the RP |
| `ADMIN_CIDR` | _e.g. `203.0.113.5/32`_ | Public IP `/32` (or office range) allowed to SSH to the VMs — the deployer's workstation or jump host |
| `SSH_USER` | _default: `ubuntu`_ | Linux user with passwordless sudo on the VMs |

## Step 2 — Hand this checklist to your network / cert team

Replace every `<placeholder>` with your worksheet value, then send the block below to whoever manages your DNS, certificates, and firewall. It is self-contained and topology-neutral; the **On AWS** / **On-prem** notes around each section tell *you* (the deployer) how to interpret it for your environment.

> **§1 DNS — where to create the records.** Admin records point to a **private** IP, so they must resolve for VPN-connected admins. **On-prem:** create them in your internal / split-horizon DNS. **On AWS:** create them in a Route 53 **private** hosted zone attached to the VPC. The apex + wildcard point to the **public** IP and go in your public DNS (Route 53 public zone on AWS, or your public authoritative DNS on-prem). Explicit records (`rancher.`, `keycloak.`) take precedence over the wildcard, so the two IP targets coexist cleanly.

> **§5 Firewall — how to apply it.** **On AWS:** add these as Security Group inbound rules on the relevant instances. **On-prem:** apply them at your perimeter firewall / router ACLs. The ports are identical. The per-host firewall (`ufw`) is configured automatically by the installer — your team does **not** set that up.

```
══════════════════════════════════════════════════════════════════════════════
  PROCUREMENT REQUEST — OpenG2P Production Deployment
  Organisation: <ORG_NAME>
══════════════════════════════════════════════════════════════════════════════


─── 1. DNS A RECORDS ─────────────────────────────────────────────────────────

  Admin hostnames — must resolve to the PRIVATE IP (reachable only over VPN):

      A    rancher.<DOMAIN>      →  <RP_PRIVATE_IP>
      A    keycloak.<DOMAIN>     →  <RP_PRIVATE_IP>

  Citizen-facing — resolve to the PUBLIC IP:

      A    <DOMAIN>              →  <RP_PUBLIC_IP>     (apex)
      A    *.<DOMAIN>            →  <RP_PUBLIC_IP>     (wildcard)


─── 2. TLS CERTIFICATE ───────────────────────────────────────────────────────

  ONE wildcard certificate for the domain. It MUST cover the apex too:

      • *.<DOMAIN>      SANs must include:   <DOMAIN>
                                             *.<DOMAIN>

  This single cert serves the admin hostnames (rancher, keycloak) AND every
  citizen-facing service, all of which are subdomains of <DOMAIN>.

  Do NOT use Let's Encrypt for production — use a commercial or sovereign CA.


─── 3. CERTIFICATE DELIVERY ──────────────────────────────────────────────────

  Deliver the issued certificate + private key FILES to the deployer running
  the install (secure transfer: SFTP, encrypted mail, or a secrets vault).
  No access to the OpenG2P servers is required for this step — the install
  automation places the files on the server itself.

  Deliver one of these file sets (any format the CA returns is fine):

      • <DOMAIN>.fullchain.pem  +  <DOMAIN>.key                    (PEM — preferred)
      • <DOMAIN>.cert.pem + <DOMAIN>.chain.pem + <DOMAIN>.key       (separate PEM)
      • <DOMAIN>.pfx  (or .p12)  +  the password                   (PFX / P12)
      • <DOMAIN>.zip                                                (CA bundle)


─── 4. SERVER ACCESS ─────────────────────────────────────────────────────────

  SSH with passwordless sudo to all three VMs (Reverse-Proxy, Compute,
  Storage), as user <SSH_USER>, from:

      <ADMIN_CIDR>


─── 5. NETWORK PORTS (ingress at the network boundary) ───────────────────────

  Reverse-Proxy:
      22     TCP   <ADMIN_CIDR>     Admin SSH                         (infra setup)
      51820  UDP   0.0.0.0/0        Wireguard VPN endpoint            (infra setup)
      all    any   private subnet   Intra-cluster traffic             (infra setup)
      80     TCP   0.0.0.0/0        HTTP → HTTPS redirect             (environment setup)
      443    TCP   0.0.0.0/0        Citizen-facing HTTPS              (environment setup)

  Compute:
      22     TCP   <ADMIN_CIDR>     Admin SSH
      all    any   private subnet   Kubernetes / cluster traffic

  Storage:
      22     TCP   <ADMIN_CIDR>     Admin SSH
      2049   TCP   private subnet   NFS (from compute)
      5432   TCP   private subnet   PostgreSQL (from compute)

  Notes:
  • Admin tools (Rancher, Keycloak) are NEVER exposed publicly — reached only
    over the Wireguard VPN. Public 80/443 serve citizen-facing services only.
  • Public 80/443 are opened at the ENVIRONMENT-SETUP stage, not during infra
    setup. You can open them upfront or defer until then — either is fine.
  • Implement these as Security Group rules (AWS) or perimeter-firewall /
    router ACLs (on-prem). Per-host firewall (ufw) is configured automatically.


══════════════════════════════════════════════════════════════════════════════
  END OF REQUEST
══════════════════════════════════════════════════════════════════════════════
```

## Worked example

<details>

<summary>Show the checklist with realistic values filled in</summary>

Worksheet: `ORG_NAME` = Country X Ministry of Social Welfare · `DOMAIN` = `prod.openg2p.gov.example` · `RP_PRIVATE_IP` = `10.0.1.10` · `RP_PUBLIC_IP` = `198.51.100.5` · `ADMIN_CIDR` = `203.0.113.5/32` · `SSH_USER` = `ubuntu`

```
─── 1. DNS A RECORDS ─────────────────────────────────────────────────────────

      A    rancher.prod.openg2p.gov.example     →  10.0.1.10
      A    keycloak.prod.openg2p.gov.example    →  10.0.1.10
      A    prod.openg2p.gov.example             →  198.51.100.5
      A    *.prod.openg2p.gov.example           →  198.51.100.5

─── 2. TLS CERTIFICATE ───────────────────────────────────────────────────────

      • *.prod.openg2p.gov.example   SANs:  prod.openg2p.gov.example
                                            *.prod.openg2p.gov.example

─── 3. CERTIFICATE DELIVERY ──────────────────────────────────────────────────

      prod.openg2p.gov.example.fullchain.pem  +  prod.openg2p.gov.example.key
      (handed to the deployer by secure transfer)

─── 4. SERVER ACCESS ─────────────────────────────────────────────────────────

      SSH from 203.0.113.5/32 as 'ubuntu', passwordless sudo, all three VMs.

─── 5. NETWORK PORTS ─────────────────────────────────────────────────────────

      (as in the template — same ports for every deployment)
```

The single wildcard `*.prod.openg2p.gov.example` covers `rancher.`, `keycloak.`, and every citizen service such as `registry.prod.openg2p.gov.example` or `esignet.prod.openg2p.gov.example`.

</details>

## Reference notes

Background for the steps above. Skip if you only need the checklist.

### Admin vs citizen hostnames (private vs public)

Rancher and Keycloak are **operator tools**, not citizen-facing. The installer binds them to the RP's **private** IP and the firewall keeps admin `443` off the internet, so they are reachable only over the Wireguard VPN. Citizen-facing services bind to the **public** IP. That is why `rancher.<DOMAIN>` and `keycloak.<DOMAIN>` point to the private IP while the apex and wildcard point to the public IP. Full rationale: [Private Access Channel](../../deployment/deployment-guide/private-access-channel.md).

### Why a single wildcard certificate

Every service is a subdomain of `<DOMAIN>` — `rancher.`, `keycloak.`, and citizen services like `registry.`, `esignet.`, `minio.`, `superset.`. One wildcard cert (`*.<DOMAIN>`, including the apex) covers them all, so procurement is **one cert** instead of one per service. The same cert is served on both the private (admin) and public (citizen) listeners of the RP.

### Resolving admin hostnames from your laptop

After connecting to the VPN, your laptop must resolve the admin hostnames to the RP's private IP. The cleanest way is to push a resolver to every Wireguard peer via the `wg_peer_dns` setting in `prod-config.yaml`:

* **On-prem:** set it to your internal DNS server's IP (must sit inside the routed subnet so the query crosses the tunnel).
* **On AWS:** set it to the VPC DNS resolver at `<vpc-cidr-base>.2` (e.g. `10.0.0.2` for a `10.0.0.0/16` VPC), which resolves the Route 53 private hosted zone.

A one-time `/etc/hosts` entry on the laptop works for either topology; the installer prints the exact line in its completion summary.

### Certificate formats

The install scripts auto-detect the common formats from government / commercial CA procurement: PEM fullchain+key (preferred), separate PEM (cert+chain+key), PFX/P12 (with password), and ZIP bundles. For the formats seen in government procurement, see [DNS & TLS Certificates](../../deployment/concepts/dns-and-certificates.md).

{% hint style="warning" %}
**Don't use Let's Encrypt for production.** It's fine for a sandbox or PoC, but most governments require certs from a commercial CA (DigiCert, GlobalSign, Sectigo) or their national / sovereign CA. The installer defaults to customer-provided certs; Let's Encrypt is a sandbox-only option.
{% endhint %}

### After the certificates arrive — the deployer's workflow

The cert team hands you the **files**; you do not give them server access. On your workstation:

1. Put the received cert + key in a folder next to your config, e.g. `./certs/`.
2. Point `prod-config.yaml` at those **local** paths:
   ```yaml
   tls_wildcard_cert: "./certs/prod.openg2p.gov.example.fullchain.pem"
   tls_wildcard_key:  "./certs/prod.openg2p.gov.example.key"
   ```
3. Validate without running the full install:
   ```bash
   ./openg2p-prod.sh --validate-certs --config prod-config.yaml
   ```
   This checks each cert: parses as PEM, key matches cert, not expired, and the SAN covers the configured hostnames.
4. Run the install. The orchestrator uploads the files from your laptop and installs them on the Reverse-Proxy node automatically — you never copy certs to the server by hand.

{% hint style="info" %}
**Separate admin domain (advanced).** This guide uses one domain for both admin and citizen hostnames — the common case. If your organisation requires admin tools on a wholly separate domain, procure a second wildcard cert for that domain and set the per-service `*_hostname` / `tls_*` keys in `prod-config.yaml`. See the three-node automation page.
{% endhint %}

## Related pages

* [Three-node infrastructure automation](infrastructure-setup/three-node-automation/) — install the cluster once certs are in place
* [Environment setup](environment-setup-multi-node.md) — install OpenG2P modules into the production environment
* [DNS & TLS Certificates](../../deployment/concepts/dns-and-certificates.md) — cert formats in government procurement
* [Private Access Channel](../../deployment/deployment-guide/private-access-channel.md) — why admin tools sit behind the VPN
