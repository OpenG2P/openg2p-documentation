---
description: >-
  Single source of truth for everything a customer must procure to bring
  up an OpenG2P deployment — DNS records, TLS certificates, server access.
---

# Prerequisites & Procurement

This page is the **single source of truth** for what a customer must procure before any OpenG2P installation runs. Both the [three-node infrastructure automation](infrastructure-setup/three-node-automation/) and the [multi-node environment setup](environment-setup-multi-node.md) link here as the first prerequisite.

{% hint style="warning" %}
**Plan all environments up front.** TLS certificate issuance — especially from sovereign or commercial CAs — typically takes **2-4 weeks**. If you discover a missing certificate mid-deployment, that becomes a 2-4 week delay. List every environment you intend to bring up (dev, qa, prod, etc.) in the deployment plan, generate the full checklist once, and start procurement before any servers are touched.
{% endhint %}

## The two-step procurement workflow

1. **Fill out a Deployment Plan** — one YAML file listing infra hostnames + every planned environment.
2. **Generate the checklist** — one printable document the customer hands to their network/cert/IT team.

Procurement then runs in parallel with VM provisioning. By the time infrastructure is ready, certs and DNS are in place too, and the install runs end-to-end without delay.

### Where this lives

```
automation/procurement/
├── deployment-plan.example.yaml      # Template — copy and edit
└── generate-procurement-checklist.sh # Reads the plan, prints the checklist
```

## Step 1 — Fill out the Deployment Plan

Copy the example:

```bash
cd automation/procurement
cp deployment-plan.example.yaml deployment-plan.yaml
```

Edit `deployment-plan.yaml` with your real values. The plan covers four areas:

<table><thead><tr><th width="180">Section</th><th>What you fill in</th></tr></thead><tbody><tr><td><strong>Infrastructure</strong></td><td><code>nginx_node_ip</code>, <code>rancher_hostname</code>, optionally <code>keycloak_hostname</code></td></tr><tr><td><strong>Environments</strong></td><td>Comma-separated list of environment names (e.g. <code>dev,qa,prod</code>) and a <code>base_domain</code> per environment</td></tr><tr><td><strong>Cert placement</strong></td><td>Standard path on the Nginx node where certs will be placed (default <code>/etc/openg2p/certs</code>)</td></tr><tr><td><strong>Access</strong></td><td>SSH user, admin CIDR — informational; included in the printed checklist</td></tr></tbody></table>

A minimal plan looks like this:

```yaml
organization: "Country X Ministry of Social Welfare"

nginx_node_ip: "10.0.1.10"
rancher_hostname: "rancher.openg2p.gov.example"

environments: "dev,qa,prod"

env_dev_base_domain:  "dev.openg2p.gov.example"
env_qa_base_domain:   "qa.openg2p.gov.example"
env_prod_base_domain: "prod.openg2p.gov.example"

cert_base_path: "/etc/openg2p/certs"
ssh_user: "ubuntu"
admin_workstation_cidr: "203.0.113.5/32"
```

## Step 2 — Generate the procurement checklist

```bash
./generate-procurement-checklist.sh --plan deployment-plan.yaml
```

To save the checklist to a file (e.g. to email to the customer):

```bash
./generate-procurement-checklist.sh --plan deployment-plan.yaml --out checklist.txt
```

The generator prints a six-section document covering everything the customer must arrange:

<details>

<summary>Sample output</summary>

```
══════════════════════════════════════════════════════════════════════════════
  PROCUREMENT CHECKLIST — OpenG2P Deployment
  Country X Ministry of Social Welfare
══════════════════════════════════════════════════════════════════════════════

─── 1. DNS A RECORDS ─────────────────────────────────────────────────

  All hostnames below must resolve to the Nginx node's public IP:
      10.0.1.10

  Admin hostnames (required):
      A   rancher.openg2p.gov.example                   → 10.0.1.10

  Environment hostnames (one base + one wildcard per environment):
      A   dev.openg2p.gov.example                       → 10.0.1.10
      A   *.dev.openg2p.gov.example                     → 10.0.1.10
      A   qa.openg2p.gov.example                        → 10.0.1.10
      A   *.qa.openg2p.gov.example                      → 10.0.1.10
      A   prod.openg2p.gov.example                      → 10.0.1.10
      A   *.prod.openg2p.gov.example                    → 10.0.1.10

─── 2. TLS CERTIFICATES TO OBTAIN ────────────────────────────────────

  Admin certificates:
      • rancher.openg2p.gov.example                   (single-host cert)

  Environment certificates (one wildcard per environment):
      • *.dev.openg2p.gov.example                     (wildcard cert, must include apex)
      • *.qa.openg2p.gov.example                      (wildcard cert, must include apex)
      • *.prod.openg2p.gov.example                    (wildcard cert, must include apex)

─── 3. CERT PLACEMENT ON NGINX NODE ──────────────────────────────────
─── 4. SERVER ACCESS REQUIRED ────────────────────────────────────────
─── 5. NETWORK PORTS / FIREWALL ──────────────────────────────────────
─── 6. ADDING MORE ENVIRONMENTS LATER ────────────────────────────────
```

</details>

Send this output to the customer's network/cert/IT team. Each section is self-contained and actionable.

## What gets procured

### DNS A records

| Record | Points to | Purpose |
| --- | --- | --- |
| `rancher.<your-domain>` | Nginx internal IP (or public, depending on access model) | Admin UI for Rancher |
| `<env>.<your-domain>` | Nginx public IP | Apex for the environment |
| `*.<env>.<your-domain>` | Nginx public IP | Wildcard for all services in the env (e.g. `minio.<env>.<your-domain>`, `superset.<env>.<your-domain>`) |

One base + one wildcard A record **per environment** is enough — no per-service records are needed thanks to the wildcard.

### TLS certificates

| Type | Required for | Format |
| --- | --- | --- |
| Single-host | Admin hostnames (Rancher, optional shared Keycloak) | PEM fullchain + key |
| Wildcard | Each environment — `*.<env-base-domain>` (must also cover the apex) | PEM fullchain + key |

{% hint style="info" %}
**Why wildcard for environments?** Every microservice in an environment (MinIO, Superset, eSignet, ODK, etc.) gets its own subdomain — `minio.qa.openg2p.org`, `superset.qa.openg2p.org`, and so on. A single wildcard cert covers all of them. This keeps procurement to one cert per environment instead of ten.
{% endhint %}

#### Accepted formats

The install scripts auto-detect cert formats. Common ones from government / commercial CA procurement:

* **PEM fullchain + key** — `*.fullchain.pem` + `*.key`
* **Separate PEM** — `*.cert.pem` + `*.chain.pem` + `*.key`
* **PFX / P12** (password-protected) — `*.pfx` / `*.p12` (specify the password in the install config)
* **ZIP bundle** (Sectigo / DigiCert style) — `*.zip`

For more on cert formats in government deployments, see [DNS & TLS Certificates](../../deployment/concepts/dns-and-certificates.md).

{% hint style="warning" %}
**Don't use Let's Encrypt for production.** It's fine for a sandbox or PoC, but most governments require certs from a commercial CA (DigiCert, GlobalSign, Sectigo) or their national / sovereign CA. The install scripts default to customer-provided certs; Let's Encrypt is supported only as a sandbox option.
{% endhint %}

### Cert placement on the Nginx node

Each cert must be placed on the Reverse-Proxy (Nginx) node at a predictable path so the install scripts can find it:

```
/etc/openg2p/certs/<domain>/fullchain.pem    (mode 644)
/etc/openg2p/certs/<domain>/privkey.pem      (mode 600)
```

For example, for the plan shown above:

```
/etc/openg2p/certs/rancher.openg2p.gov.example/
/etc/openg2p/certs/dev.openg2p.gov.example/
/etc/openg2p/certs/qa.openg2p.gov.example/
/etc/openg2p/certs/prod.openg2p.gov.example/
```

The customer's IT team uploads certs to these paths once they're issued.

### Server access

* SSH access (root or sudo) to the Reverse-Proxy / Nginx node
* SSH access to the Kubernetes control-plane node(s) — only if the operator's workstation isn't the same machine
* `kubectl` admin access to the cluster (kubeconfig file with cluster-admin rights, retrievable from the cluster node after RKE2 install)

### Network ports

| Node | Port | Direction |
| --- | --- | --- |
| Nginx | `443/TCP` | Public — citizen + admin HTTPS (admin via VPN) |
| Nginx | `80/TCP` | Public — HTTP→HTTPS redirect |
| Nginx | `22/TCP` | Admin CIDR — SSH |
| Nginx | `51820/UDP` | Public — Wireguard (if used) |
| Cluster | `6443/TCP` | Operator workstation — kubectl |
| Storage | `5432/TCP` | Private subnet only — PostgreSQL |
| Storage | `2049/TCP` | Private subnet only — NFS |

## Adding more environments later

If a new environment is needed months after initial deployment:

1. Append the new env name to the `environments:` list in your `deployment-plan.yaml` and add the matching `env_<name>_base_domain` entry.
2. Re-run `./generate-procurement-checklist.sh` — the output will include the same overall checklist, but only the new env's DNS records and cert are still to be procured.
3. Procure DNS + cert for the new env.
4. Run `./env-cluster.sh --config <env-config.yaml>` to bring the new environment online.

No infrastructure rebuild is needed — each environment is independent inside the same cluster.

## Related pages

* [Three-node infrastructure automation](infrastructure-setup/three-node-automation/) — install the cluster after certs are in place
* [Environment setup (multi-node)](environment-setup-multi-node.md) — install OpenG2P modules per environment
* [Single-node automation](infrastructure-setup/single-node-automation.md) — sandbox setup (Let's Encrypt acceptable)
* [DNS & TLS Certificates](../../deployment/concepts/dns-and-certificates.md) — cert formats commonly seen in gov procurement
