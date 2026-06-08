---
description: >-
  Background on DNS and TLS in government OpenG2P deployments — cert formats
  customers actually receive, wildcards vs per-FQDN trade-offs, and the
  DNS-01 challenge for Let's Encrypt wildcards.
---

# DNS & TLS Certificates

Useful background for the cert team and the deployer. DNS and TLS are usually the longest-lead-time items in any government deployment; this page is the field guide.

For what's *required* (the production checklist) see [Prerequisites & Procurement](../prerequisites-procurement.md). For the architectural rationale (admin vs citizen channels, single wildcard cert) see [OpenG2P Deployment Architecture](../../../deployment/openg2p-deployment-model.md). This page only covers the realities customers tend to hit during cert procurement.

## The two layers

Every OpenG2P deployment has two categories of URL with different network exposure but the **same TLS certificate** (a single wildcard `*.<your-domain>` covers both):

| Layer | Audience | Examples | Network exposure |
| --- | --- | --- | --- |
| **Admin / operator** | Internal staff, ops team, system integrators | Rancher (local auth); per-environment app UIs (Keycloak, MinIO, Superset, …) | Reachable only over Wireguard VPN — never on the public internet |
| **Citizen-facing** | Public users (beneficiaries, applicants, agency staff) | Social registry portal, payments, eSignet, ODK Central | Public internet |

Both layers are served by the same wildcard cert; what differs is the IP the DNS A-records point at (private IP for admin hostnames, public IP for citizen hostnames) and the firewall posture in front of each. Splitting them is the whole point of the [private access channel](private-access-channel.md).

## Why customers struggle with DNS and certs

In a typical SaaS company, a domain + Let's Encrypt cert is a five-minute job. In a government department it can be weeks of process. Common situations:

* The department doesn't own a public domain yet — procurement is in progress.
* They own a domain but DNS is managed by a different team that takes weeks to add records.
* Certificates are from a sovereign or sectoral CA, but only as **per-FQDN** certificates — wildcards are forbidden by policy or by the CA.
* They've procured certificates but can't extract them from the system where they were originally installed (cPanel, IIS, another Nginx).
* Certificates arrive in formats they don't recognise (`.pfx`, separate `.crt` + `.ca-bundle` + `.key`, ZIP bundles from commercial CAs).
* For wildcards specifically: only **DNS-01** validation works, and the team operating their authoritative DNS doesn't know what an ACME TXT record is.

The OpenG2P automation is designed around these realities — not around an idealised DevOps environment.

## Hostname patterns

Three patterns dominate, in roughly decreasing order of convenience:

<table><thead><tr><th width="220">Pattern</th><th>Example</th><th>Cert needed</th></tr></thead><tbody><tr><td><strong>Per-environment subdomain</strong> (default)</td><td><code>*.prod.openg2p.org</code> covering <code>rancher.prod.openg2p.org</code>, <code>registry.prod.openg2p.org</code>, <code>payments.prod.openg2p.org</code>, …</td><td>One wildcard for the deployment</td></tr><tr><td><strong>Service-specific FQDNs under a department domain</strong></td><td><code>social-registry.moswa.gov.eth</code>, <code>payments.moswa.gov.eth</code>, <code>auth.moswa.gov.eth</code></td><td>One cert per FQDN (or a multi-SAN cert covering several)</td></tr><tr><td><strong>Mixed</strong></td><td>Some services on a department domain, others on a vendor-provided sub-tenant</td><td>Mix of the above</td></tr></tbody></table>

**Internal naming and external naming are decoupled.** Inside the cluster, services may be referenced by their per-environment hostname; the URL a citizen visits can be any hostname the customer chose. The reverse proxy and Istio Gateway translate via the `Host` header.

## Wildcard vs per-FQDN certs

OpenG2P's automation defaults to a **single wildcard** (`*.<your-domain>` + apex) — one cert for both admin and citizen hostnames. It's the lowest-overhead path and is what we recommend.

That said, some customers can't use wildcards. Reasons we see in the field:

<table><thead><tr><th width="180">Reason</th><th>What it looks like in practice</th></tr></thead><tbody><tr><td><strong>Security policy</strong></td><td>Some gov InfoSec teams ban wildcards — a single-key compromise exposes every subdomain. Per-FQDN limits blast radius.</td></tr><tr><td><strong>CA constraints</strong></td><td>Some sovereign CAs (DoD, national PKIs, ministry CAs) don't issue wildcards. One CN per cert, period.</td></tr><tr><td><strong>Procurement</strong></td><td>Certs go through tendering / approval per service. Each service has its own purchase order, owner, rotation date.</td></tr><tr><td><strong>Ownership boundaries</strong></td><td><code>social-registry.moswa.gov.eth</code> may be owned by the Ministry of Social Welfare; <code>payments.moswa.gov.eth</code> by Treasury. Different teams, different certs.</td></tr><tr><td><strong>SAN as middle ground</strong></td><td>Some CAs issue multi-SAN certs (one cert listing 5–10 specific hostnames). From the deployment's perspective, treat these the same as a wildcard.</td></tr></tbody></table>

If wildcards are off the table, the automation supports per-FQDN for the admin hostname by setting `tls_rancher_cert` explicitly instead of `tls_wildcard_cert`. Note that per-FQDN mode covers only `rancher`; the per-environment service hostnames (keycloak, minio, superset, …) are served via the wildcard, so those deployments need the wildcard cert. See `prod-config.example.yaml` for the schema.

## Cert formats customers actually receive

When a customer says "we have a certificate," it can mean any of these:

| Source | Format delivered | Customer pain |
| --- | --- | --- |
| Let's Encrypt (own certbot) | `/etc/letsencrypt/live/<domain>/{fullchain.pem, privkey.pem}` | None if they did it; can't always copy |
| Commercial CA (Sectigo, DigiCert, GoDaddy, GlobalSign) | Email/ZIP with `.crt` + `.ca-bundle` + separate `.key` | Concatenate fullchain, match key, install intermediates |
| Cloudflare Origin / Universal | Two PEM blobs in the dashboard | Copy/paste |
| Windows IIS / Azure | `.pfx` / `.p12` (binary, password-protected) | Convert with `openssl` |
| AWS ACM | Not exportable (cloud-only) | Customer realises too late |
| cPanel / Plesk hosted | PEM, downloadable | Usually fine |

The installer auto-detects PEM (fullchain + key, or separate cert + chain + key), PFX/P12 (with password), and ZIP bundles. ACM certificates can't be exported and won't work — flag this early so the customer doesn't go down that path.

{% hint style="warning" %}
**Don't use Let's Encrypt for production.** Most governments require certs from a commercial CA or their national / sovereign CA. The installer defaults to customer-provided certs; Let's Encrypt is a sandbox-only option.
{% endhint %}

## The DNS-01 challenge for wildcards (when Let's Encrypt is on the table)

If a customer wants to use Let's Encrypt for a wildcard cert, **DNS-01 is the only option**. Two flavours:

* **Automated** via the customer's DNS provider's API. Cloudflare is by far the easiest (one API token); Route 53, DigitalOcean, Linode, GoDaddy, Namecheap, and Google Cloud DNS all have certbot plugins.
* **Manual** — certbot prints a TXT record, the operator pastes it into the DNS provider's web UI, certbot continues. Slow but always works.

For organisations whose DNS is operated by a separate team without API access, automated mode isn't feasible — the manual flow is what they end up doing.

{% hint style="info" %}
**Practical advice for sandbox/PoC:** if your domain registrar supports it, move DNS hosting to Cloudflare (free tier). Getting a wildcard via certbot's `dns-cloudflare` plugin then takes about 5 minutes. Only the DNS hosting matters for this; the domain can stay registered elsewhere.
{% endhint %}

## Summary

* Plan for the cert pain to be the longest-lead-time item in any government deployment.
* Default to a **single wildcard** covering admin + citizen hostnames — that's what the automation expects, and it's the lightest path.
* Be ready for **per-FQDN** as a fallback when wildcards are restricted by policy or CA.
* Expect certs in **mixed formats** (PEM fullchain, separate PEM, PFX, ZIP); the installer handles all of them. ACM certificates can't be exported.
* Use Let's Encrypt only for sandbox/PoC. Production goes to a commercial or sovereign CA.
