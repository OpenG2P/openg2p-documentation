---
description: >-
  Everything a customer must procure before installing OpenG2P in production —
  DNS records, TLS certificates, server access. Fill in your values and hand
  the checklist to your IT / network / cert team.
---

# Prerequisites & Procurement

This page is the **single source of truth** for what a customer must procure before any OpenG2P installation runs. The [three-node infrastructure automation](infrastructure-setup/three-node-automation/) and the [environment setup](environment-setup-multi-node.md) both link here as the first prerequisite.

{% hint style="warning" %}
**Start procurement early.** TLS certificate issuance — especially from sovereign or commercial CAs — typically takes **2–4 weeks**. If a missing certificate is discovered mid-install, that becomes a 2–4 week delay. Fill in the worksheet below and hand the resulting checklist to your IT / network / cert team **before** any servers are touched, so procurement runs in parallel with VM provisioning.
{% endhint %}

## How to use this page

1. **Read the overview** below so you know what's being procured and why.
2. **Fill in the worksheet** in [Step 1](#step-1-fill-in-your-values) with your real values.
3. **Copy the checklist** in [Step 2](#step-2-the-procurement-checklist), substitute your worksheet values into the angle-bracket placeholders, print / save as PDF, and email it to your IT / network / cert team.
4. **A worked example** at the bottom shows what the filled-in checklist looks like.

## What needs to be procured

| Category | What | How many |
| --- | --- | --- |
| **DNS A records** | Admin hostnames (`rancher`, `keycloak`) | 2, pointing to the RP's **private** IP |
| **DNS A records** | Production hostnames (apex + wildcard for citizen services) | 2, pointing to the RP's **public** IP |
| **TLS certificates** | Wildcard cert covering admin hostnames | 1 |
| **TLS certificates** | Wildcard cert covering production hostnames | 1 |
| **Server access** | SSH (+ sudo) to the three VMs | 1 admin workstation CIDR |

A single wildcard cert per domain covers every subdomain — there's no need to procure a separate cert per service. See [Why wildcards](#why-wildcards).

## Step 1 — Fill in your values

Copy this worksheet into a working document (a `.txt` file, a wiki page, anywhere) and fill in the right-hand column. You'll substitute these values into the checklist in Step 2.

| Field | Your value | What it is |
| --- | --- | --- |
| `ORG_NAME` | _e.g. "Country X Ministry of Social Welfare"_ | Used on the cert subject line and in the procurement-request header |
| `ADMIN_DOMAIN` | _e.g. `openg2p.gov.example`_ | Parent domain for admin hostnames. `rancher.<ADMIN_DOMAIN>` and `keycloak.<ADMIN_DOMAIN>` are derived from it |
| `PROD_DOMAIN` | _e.g. `prod.openg2p.gov.example`_ | Base domain for production citizen-facing services. Usually a subdomain of the admin domain |
| `RP_PRIVATE_IP` | _e.g. `10.0.1.10`_ | The Reverse-Proxy VM's primary NIC IP. Admin hostnames resolve here; reachable only via VPN or the private network |
| `RP_PUBLIC_IP` | _e.g. `198.51.100.5`_ | The Reverse-Proxy VM's public IP (Elastic IP on AWS, public IP / NAT'd address on-prem). Production hostnames resolve here; also the Wireguard endpoint |
| `ADMIN_CIDR` | _e.g. `203.0.113.5/32`_ | Public IP (`/32`) or office CIDR allowed to SSH to the Reverse-Proxy. The deployer's laptop or jump host |
| `SSH_USER` | _default: `ubuntu`_ | Linux user with sudo on the VMs (Ubuntu 24.04 cloud images default to `ubuntu`) |

{% hint style="info" %}
**`ADMIN_DOMAIN` vs `PROD_DOMAIN`** — they're often related but distinct:
* `ADMIN_DOMAIN` = `openg2p.gov.example` → admin URLs become `rancher.openg2p.gov.example`, `keycloak.openg2p.gov.example`
* `PROD_DOMAIN` = `prod.openg2p.gov.example` → production services live under it (`registry.prod.openg2p.gov.example`, `signet.prod.openg2p.gov.example`, etc.)

`PROD_DOMAIN` is most often a subdomain of `ADMIN_DOMAIN`, but they don't have to be related — pick whatever your organisation already uses.
{% endhint %}

## Step 2 — The procurement checklist

Copy the block below into an email / document, replace every `<placeholder>` with the value from your worksheet, and send to your IT / network / cert team.

```
══════════════════════════════════════════════════════════════════════════════
  PROCUREMENT REQUEST — OpenG2P Production Deployment
  Organisation: <ORG_NAME>
══════════════════════════════════════════════════════════════════════════════


─── 1. DNS A RECORDS ─────────────────────────────────────────────────────────

  Admin hostnames — private channel (reachable only via VPN).
  Point these records at the Reverse-Proxy's PRIVATE IP <RP_PRIVATE_IP>:

      A    rancher.<ADMIN_DOMAIN>      →  <RP_PRIVATE_IP>
      A    keycloak.<ADMIN_DOMAIN>     →  <RP_PRIVATE_IP>

  Production hostnames — public channel (citizen-facing).
  Point these records at the Reverse-Proxy's PUBLIC IP <RP_PUBLIC_IP>:

      A    <PROD_DOMAIN>               →  <RP_PUBLIC_IP>
      A    *.<PROD_DOMAIN>             →  <RP_PUBLIC_IP>


─── 2. TLS CERTIFICATES ──────────────────────────────────────────────────────

  Issue ONE wildcard certificate for each of the two domains.
  Each wildcard MUST also cover the apex (the bare domain).

      • *.<ADMIN_DOMAIN>      SANs must include:   <ADMIN_DOMAIN>
                                                   rancher.<ADMIN_DOMAIN>
                                                   keycloak.<ADMIN_DOMAIN>

      • *.<PROD_DOMAIN>       SANs must include:   <PROD_DOMAIN>
                                                   *.<PROD_DOMAIN>

  Accepted formats (the install scripts auto-detect):

      • PEM fullchain + key                 (*.fullchain.pem + *.key)   — preferred
      • Separate PEM (cert + chain + key)   (*.cert.pem + *.chain.pem + *.key)
      • PFX / P12 (password-protected)      (*.pfx / *.p12; supply the password)
      • ZIP bundle (Sectigo / DigiCert)     (*.zip)


─── 3. CERT PLACEMENT ON THE REVERSE-PROXY ───────────────────────────────────

  Once issued, upload the certs to the Reverse-Proxy node at:

      /etc/openg2p/certs/<ADMIN_DOMAIN>/fullchain.pem      (mode 644)
      /etc/openg2p/certs/<ADMIN_DOMAIN>/privkey.pem        (mode 600)

      /etc/openg2p/certs/<PROD_DOMAIN>/fullchain.pem       (mode 644)
      /etc/openg2p/certs/<PROD_DOMAIN>/privkey.pem         (mode 600)


─── 4. SERVER ACCESS ─────────────────────────────────────────────────────────

  SSH (with sudo) to all three VMs (Reverse-Proxy, Compute, Storage) from:

      <ADMIN_CIDR>     (the deployer's workstation / jump host public IP /32)

  Use the OS user: <SSH_USER>


─── 5. NETWORK PORTS / FIREWALL ──────────────────────────────────────────────

  Reverse-Proxy node — INGRESS rules required:

      Port        Proto   Source            Purpose
      22          TCP     <ADMIN_CIDR>      Admin SSH
      51820       UDP     0.0.0.0/0         Wireguard VPN endpoint
      80          TCP     0.0.0.0/0         HTTP → HTTPS redirect (citizen services)
      443         TCP     0.0.0.0/0         Citizen-facing HTTPS (env services)
      all         any     private subnet    Intra-cluster traffic

  Compute node — INGRESS rules required:

      22          TCP     <ADMIN_CIDR>      Admin SSH
      all         any     private subnet    Kubernetes / cluster traffic

  Storage node — INGRESS rules required:

      22          TCP     <ADMIN_CIDR>      Admin SSH
      2049        TCP     private subnet    NFS (from compute node)
      5432        TCP     private subnet    PostgreSQL (from compute node)


══════════════════════════════════════════════════════════════════════════════
  END OF REQUEST
══════════════════════════════════════════════════════════════════════════════
```

## Worked example

Below is the same checklist with realistic values filled in, so you can see what the final artifact looks like.

<details>

<summary>Show worked example</summary>

```
══════════════════════════════════════════════════════════════════════════════
  PROCUREMENT REQUEST — OpenG2P Production Deployment
  Organisation: Country X Ministry of Social Welfare
══════════════════════════════════════════════════════════════════════════════


─── 1. DNS A RECORDS ─────────────────────────────────────────────────────────

  Admin hostnames — private channel (reachable only via VPN).
  Point these records at the Reverse-Proxy's PRIVATE IP 10.0.1.10:

      A    rancher.openg2p.gov.example       →  10.0.1.10
      A    keycloak.openg2p.gov.example      →  10.0.1.10

  Production hostnames — public channel (citizen-facing).
  Point these records at the Reverse-Proxy's PUBLIC IP 198.51.100.5:

      A    prod.openg2p.gov.example          →  198.51.100.5
      A    *.prod.openg2p.gov.example        →  198.51.100.5


─── 2. TLS CERTIFICATES ──────────────────────────────────────────────────────

  Issue ONE wildcard certificate for each of the two domains.
  Each wildcard MUST also cover the apex (the bare domain).

      • *.openg2p.gov.example     SANs must include:   openg2p.gov.example
                                                       rancher.openg2p.gov.example
                                                       keycloak.openg2p.gov.example

      • *.prod.openg2p.gov.example  SANs must include: prod.openg2p.gov.example
                                                       *.prod.openg2p.gov.example

  Accepted formats: PEM fullchain + key (preferred), Separate PEM, PFX/P12, ZIP.


─── 3. CERT PLACEMENT ON THE REVERSE-PROXY ───────────────────────────────────

      /etc/openg2p/certs/openg2p.gov.example/fullchain.pem      (mode 644)
      /etc/openg2p/certs/openg2p.gov.example/privkey.pem        (mode 600)

      /etc/openg2p/certs/prod.openg2p.gov.example/fullchain.pem (mode 644)
      /etc/openg2p/certs/prod.openg2p.gov.example/privkey.pem   (mode 600)


─── 4. SERVER ACCESS ─────────────────────────────────────────────────────────

  SSH from:  203.0.113.5/32   as user 'ubuntu'.


─── 5. NETWORK PORTS / FIREWALL ──────────────────────────────────────────────

  (as listed in the template — same for every deployment)
```

</details>

## Reference notes for the cert team

### Why wildcards

Every microservice in a production environment (registry, e-Signet, ODK, MinIO, Superset, etc.) gets its own subdomain — e.g. `registry.prod.openg2p.gov.example`, `signet.prod.openg2p.gov.example`. A single wildcard cert (`*.prod.openg2p.gov.example`) covers all of them; this keeps procurement to **one cert per domain** instead of one per service.

The wildcard must also be valid for the **apex** (the bare domain) so the same cert serves `prod.openg2p.gov.example` directly. Most CAs include the apex automatically when issuing a wildcard, but always confirm with your CA.

### Cert formats in detail

For more on common cert formats from government / sovereign / commercial CA procurement, see [DNS & TLS Certificates](../../deployment/concepts/dns-and-certificates.md).

{% hint style="warning" %}
**Don't use Let's Encrypt for production.** It's fine for a sandbox or PoC, but most governments require certs from a commercial CA (DigiCert, GlobalSign, Sectigo) or their national / sovereign CA. The install scripts default to customer-provided certs; Let's Encrypt is supported only as a sandbox option.
{% endhint %}

### After the certs arrive

1. The IT / cert team uploads each cert + key pair to the predictable paths under `/etc/openg2p/certs/...` on the Reverse-Proxy node.
2. The deployer points `prod-config.yaml`'s `tls_wildcard_cert` / `tls_wildcard_key` at the admin-domain cert (the install scripts use this for Nginx admin server blocks).
3. The production-domain cert is consumed later by the [environment setup](environment-setup-multi-node.md) when citizen-facing services are deployed.

You can validate certs at any time without running the full install:

```bash
./openg2p-prod.sh --validate-certs --config prod-config.yaml
```

This checks each cert: parses as PEM, key matches cert, not expired, and the SAN actually covers the configured hostnames.

## Related pages

* [Three-node infrastructure automation](infrastructure-setup/three-node-automation/) — install the cluster after certs are in place
* [Environment setup](environment-setup-multi-node.md) — install OpenG2P modules into the production environment
* [DNS & TLS Certificates](../../deployment/concepts/dns-and-certificates.md) — cert formats commonly seen in government procurement
