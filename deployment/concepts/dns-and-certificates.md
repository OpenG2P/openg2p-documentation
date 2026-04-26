---
description: How DNS and TLS certificates work in an OpenG2P deployment, the trade-offs, and the patterns we recommend for different customer realities.
---

# DNS & TLS Certificates

DNS and TLS are two of the most painful parts of any production deployment, and OpenG2P customers — especially government departments — face a more constrained environment than the typical SaaS company. This page lays out the concepts, the real-world constraints we see in the field, and the patterns the OpenG2P automation builds around.

{% hint style="info" %}
This page is **conceptual**. For how the automation actually implements these patterns, see [Three-Node Automation](../../operations/deployment/automation/three-node-automation.md) and [Single-Node Automation](../automation/single-node-automation.md).
{% endhint %}

## The two layers

Every OpenG2P deployment has two distinct categories of URL, and they have very different DNS / TLS needs.

<table>
  <thead>
    <tr><th>Layer</th><th>Audience</th><th>Examples</th><th>Network exposure</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Admin / operator</strong></td>
      <td>Internal staff, ops team, system integrators</td>
      <td>Rancher, Keycloak (admin SSO), Grafana, OpenSearch dashboards, Prometheus</td>
      <td>Reachable only over Wireguard VPN — never on the public internet</td>
    </tr>
    <tr>
      <td><strong>Citizen-facing</strong></td>
      <td>Public users (beneficiaries, applicants, agency staff)</td>
      <td>Social registry portal, payments dashboard, eSignet, ODK Central, beneficiary self-service</td>
      <td>Public internet</td>
    </tr>
  </tbody>
</table>

The two layers have radically different DNS and TLS requirements. Conflating them is one of the main reasons deployment is harder than it needs to be.

## Why customers struggle with DNS and certs

In a typical SaaS company, getting a domain name and a Let's Encrypt cert is a five-minute job. In a government department, it can be weeks of process. Common situations we see:

* The department doesn't own a public domain at all yet. Procurement is in progress.
* They own a domain but DNS is managed by a different team that takes weeks to add records.
* They have certificates from a sovereign or sectoral CA, but only as **per-FQDN** certificates — wildcards are forbidden by their security policy or their CA.
* They've procured certificates but don't know how to extract them from the system where they were originally installed (cPanel, IIS, another Nginx).
* They have certificates in formats they don't recognize (`.pfx`, separate `.crt` + `.ca-bundle` + `.key`, ZIP bundles from commercial CAs).
* For wildcards specifically: only **DNS-01** validation works, and the team operating their authoritative DNS doesn't know what an ACME TXT record is.

The OpenG2P automation is designed around these realities, not around an idealized DevOps environment.

## Admin tools — internal DNS and self-signed certs

For Rancher, Keycloak admin, monitoring dashboards, and similar **operator tools**, we use a self-contained scheme that requires zero external dependencies:

* **Internal domain** — a single TLD reserved for private use, default `openg2p.internal`. ICANN reserved `.internal` in 2024 specifically for this purpose, so it's guaranteed never to clash with public DNS.
* **Local DNS server** (`dnsmasq`) on the reverse-proxy node, listening on the Wireguard interface. Resolves `*.openg2p.internal` to the reverse-proxy's private IP. Only Wireguard peers can reach it.
* **Local Certificate Authority** generated on the reverse-proxy node. A 10-year CA root, used to issue a wildcard `*.openg2p.internal` leaf certificate (2-year validity, renewable in place).
* **CA certificate distributed once to admin laptops**. After installing it in the OS trust store, browsers accept the self-signed certs without warnings.

{% hint style="success" %}
**The customer needs nothing for the admin layer.** No domain registration, no DNS records, no commercial certificates. Connect to Wireguard, install the CA, you're done.
{% endhint %}

This pattern works because admin tools are by definition internal. Exposing Rancher publicly is rarely needed and almost always a security mistake. Most government deployments specifically require admin access to be VPN-only.

## Citizen-facing services — customer-supplied certs

For services that real users hit over the public internet — the social registry portal, payments dashboards, eSignet — the customer has to provide the domain names and certificates. This is the layer where reality bites.

### Hostname patterns

Three patterns dominate, in roughly decreasing order of convenience:

<table>
  <thead>
    <tr><th width="220">Pattern</th><th>Example</th><th>Cert needed</th></tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Per-environment subdomain</strong></td>
      <td><code>*.prod.openg2p.org</code> covering <code>registry.prod.openg2p.org</code>, <code>payments.prod.openg2p.org</code>, …</td>
      <td>One wildcard per environment</td>
    </tr>
    <tr>
      <td><strong>Service-specific FQDNs under a department domain</strong></td>
      <td><code>social-registry.moswa.gov.eth</code>, <code>payments.moswa.gov.eth</code>, <code>auth.moswa.gov.eth</code></td>
      <td>One cert per FQDN (or one SAN cert covering several)</td>
    </tr>
    <tr>
      <td><strong>Mixed</strong></td>
      <td>Some services on a department domain, others on a vendor-provided sub-tenant</td>
      <td>Mix of the above</td>
    </tr>
  </tbody>
</table>

**Internal naming and external naming are decoupled.** Inside the cluster, services may be referenced as `registry.prod.openg2p.org` (OpenG2P convention), but the URL a citizen visits can be any hostname the customer chose — `social-registry.moswa.gov.eth`. The reverse proxy and Istio Gateway translate between the two via the `Host` header.

### Wildcard vs per-FQDN certs

Wildcards seem like the natural choice (one cert, many services), but they're the **exception** in government environments, not the norm.

<table>
  <thead><tr><th width="180">Reason</th><th>What it looks like in practice</th></tr></thead>
  <tbody>
    <tr><td><strong>Security policy</strong></td><td>Many gov InfoSec teams ban wildcards — single key compromise exposes every subdomain. Per-FQDN limits blast radius.</td></tr>
    <tr><td><strong>CA constraints</strong></td><td>Some sovereign CAs (DoD, national PKIs, ministry CAs) don't issue wildcards. One CN per cert, period.</td></tr>
    <tr><td><strong>Procurement</strong></td><td>Certs go through tendering / approval per service. Each service has its own purchase order, owner, rotation date.</td></tr>
    <tr><td><strong>Ownership boundaries</strong></td><td><code>social-registry.moswa.gov.eth</code> may be owned by the Ministry of Social Welfare; <code>payments.moswa.gov.eth</code> by Treasury. Different teams, different certs.</td></tr>
    <tr><td><strong>SAN as middle ground</strong></td><td>Some CAs issue multi-SAN certs (one cert listing 5–10 specific hostnames). Treat these the same as wildcards from the deployment's perspective.</td></tr>
  </tbody>
</table>

{% hint style="warning" %}
**Don't bet on wildcards.** Architect for per-FQDN as the primary case, treat wildcards and SAN certs as a happy bonus when offered.
{% endhint %}

### Cert formats customers actually receive

When customers say "we have a certificate," it can mean any of the following:

| Source | Format delivered | Customer pain |
|---|---|---|
| Let's Encrypt (own certbot) | `/etc/letsencrypt/live/<domain>/{fullchain.pem, privkey.pem}` | None if they did it; can't always copy |
| Commercial CA (Sectigo, DigiCert, GoDaddy, GlobalSign) | Email/ZIP with `.crt` + `.ca-bundle` + separate `.key` | Concatenate fullchain, match key, install intermediates |
| Cloudflare Origin / Universal | Two PEM blobs in the dashboard | Copy/paste |
| Windows IIS / Azure | `.pfx` / `.p12` (binary, password-protected) | Convert with `openssl` |
| AWS ACM | Not exportable (cloud-only) | Customer realises too late |
| cPanel / Plesk hosted | PEM, downloadable | Usually fine |

Plus the wildcard challenge: only **DNS-01** validation works for wildcards. Someone needs to put a TXT record at the DNS authority — which is often the part where customers get stuck.

### The DNS-01 challenge for wildcards (when applicable)

If a customer wants to use Let's Encrypt for a wildcard cert, **DNS-01 is the only option**. Two flavours:

* **Automated** via the customer's DNS provider's API. Cloudflare is by far the easiest (one API token); Route 53, DigitalOcean, Linode, GoDaddy, Namecheap, and Google Cloud DNS all have certbot plugins.
* **Manual** — certbot prints a TXT record, the operator pastes it into the DNS provider's web UI, certbot continues. Slow but always works.

For organisations whose DNS is operated by a separate team that doesn't support API access, automated mode often isn't feasible — the manual flow is what they end up doing.

{% hint style="info" %}
**Practical advice we give customers:** if your domain registrar supports it, move DNS hosting to Cloudflare (free tier). After that, getting a wildcard via certbot's `dns-cloudflare` plugin takes about 5 minutes. Even when the domain stays registered elsewhere, only the DNS hosting matters for this.
{% endhint %}

## How the automation handles all this

| Layer | Approach |
|---|---|
| **Admin tools** (Rancher, Keycloak, monitoring) | Always internal. Local CA + self-signed wildcard for `*.openg2p.internal`, served via Wireguard. No customer DNS or certs needed. |
| **Citizen-facing services** (registry, payments, eSignet, …) | Customer supplies hostnames and certs per service. The environment automation accepts certs in any of the formats above and normalises them; configures Nginx and Istio with per-FQDN server blocks. |
| **Cert renewal** | For Let's Encrypt: certbot's systemd timer + Nginx reload hook (automatic). For user-provided certs: manual rotation via a one-line helper, and a Prometheus expiry monitor with Grafana alerts. |

This split lets a customer install the **infrastructure** with zero domain or cert procurement, then add citizen-facing services later as their compliance/legal teams complete cert procurement — without re-installing or migrating anything.

## Summary

* Two layers — admin (internal, VPN-only, self-signed) and citizen-facing (public, customer-supplied).
* For admin tools, customers need **nothing**.
* For citizen-facing services, expect **per-FQDN certs in mixed formats**. Wildcards are the exception.
* Plan for the cert pain to be the longest lead-time item in any government deployment, and design the automation to work with whatever the customer ends up with — not what we'd prefer they had.
