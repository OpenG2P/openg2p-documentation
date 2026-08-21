---
description: Setting up OpenG2P environments on an existing multi-node infrastructure.
---

# Environment Setup

This guide covers creating OpenG2P environments (namespace + services) on an **existing multi-node infrastructure** where Nginx, the Kubernetes cluster, and storage run on separate nodes.&#x20;

{% hint style="info" %}
**Production deployment flow:**  [1. Procurement](prerequisites-procurement.md)  →  [2. Provisioning](infrastructure-setup/provisioning.md)  →  [3. Infrastructure](infrastructure-setup/production-automation/)  →  **4. Environment** (this page)  →  [5. Modules](#next-install-your-openg2p-modules)
{% endhint %}

**Where you are in the flow.** Stages 1–3 are done: VMs are provisioned, DNS+TLS are in place, and the platform (RKE2, Istio, Rancher with local auth, Wireguard, Nginx, NFS, host PostgreSQL) is installed and reachable. Production automation also **scaffolds** the environment (namespace, Istio Gateway, Helm repos, external-PG secret). This stage finishes by installing **Commons from the Rancher UI only**. After Commons, install the [product modules](#next-install-your-openg2p-modules) your rollout delivers (Registry, PBMS, SPAR, G2P Bridge).

{% hint style="info" %}
Note that for a  single-node setup the environment (including Commons) is installed as part of the [single node sandbox installation](infrastructure-setup/single-node-automation/).
{% endhint %}

{% hint style="danger" %}
**Before you start — procurement prerequisites**

DNS records, TLS certificates, and server access for this environment must already be in place before Commons install. If you have not yet procured these, start with the [**Prerequisites & Procurement**](prerequisites-procurement.md) page — it contains a single fillable checklist (admin + production hostnames + certs + server access + firewall ports) you can hand to your IT / network / cert team. TLS issuance from sovereign or commercial CAs typically takes 2–4 weeks, so do this **before** running any installer.
{% endhint %}

{% hint style="warning" %}
**Commons — Rancher UI only**

Install `openg2p-commons-base` and `openg2p-commons-services` from the **Rancher UI** (Apps → Charts), where the chart's `questions.yml` provides a guided form for production parameters (external PostgreSQL, hostnames, storage classes, replicas, and so on). Scripts under `automation/environment/` scaffold the namespace only — they do **not** install Commons. Production scaffolding (`openg2p-prod.sh`) already creates the namespace, Rancher Project, Istio Gateway, and `commons-postgresql` secret.
{% endhint %}

## How this stage runs — production vs standalone scaffolding

### Option A — Production automation scaffolding + Rancher UI Commons (recommended)

If you installed the platform with the production automation:

1. **Scaffolding** is Stage 4 of `openg2p-prod.sh` (runs at the end of a full install when `install_environment: true`). It creates the namespace, Rancher Project, Istio Gateway, Helm ClusterRepos (`openg2p` + `openg2p-gitlab`), and the external-PG secret. It uses an **SSH tunnel** to the Kubernetes API — **Wireguard is not required** for scaffolding.

```bash
./openg2p-prod.sh --config prod-config.yaml --stage environment
# or: ./openg2p-prod-env-install.sh --config prod-config.yaml
```

2. **Commons** — connect Wireguard, open Rancher, and install **openg2p-commons-base** then **openg2p-commons-services** in the environment namespace (use the `commons-postgresql` secret and host PostgreSQL on storage). Chart versions: [Commons changelog](https://openg2p.gitlab.io/versions/commons/CHANGELOG.html).

**Your only other manual actions:**

* **Step 1 — DNS records** (a procurement prerequisite; no script creates these).
* **Step 3 — citizen "go-public" exposure** on the Reverse Proxy (add the public Nginx server block + open public `80/443`), when you're ready to serve citizen traffic.

You do **not** need to write `env-config.yaml` for production scaffolding.

### Option B — Standalone scaffolding (`env-cluster.sh`) + Rancher UI Commons

If you're setting up an environment **separately** — on infrastructure not built by `openg2p-prod.sh` — use `automation/environment/env-cluster.sh` for **scaffolding only** (namespace, Rancher Project, Istio Gateway), then install Commons from the Rancher UI. Follow the step-by-step below for DNS / TLS / Nginx; skip any Commons Helm CLI steps.

### Which steps are manual?

| Step | Production flow (`openg2p-prod.sh` + Rancher) | Standalone flow |
| --- | --- | --- |
| **1 — DNS records** | Manual (prerequisite) | Manual |
| **2 — TLS cert on the RP** | **Automated** (done in Stage 3) — skip | Manual |
| **3 — Citizen exposure on the RP** | **Manual** (the go-public action) | Manual |
| Cluster scaffolding (namespace, project, gateway, repo, PG secret) | **Automated** (`openg2p-prod.sh` env stage) | `env-cluster.sh` (scaffolding only) or manual |
| Commons (`commons-base` + `commons-services`) | **Rancher UI only** | **Rancher UI only** |

## Architecture

In a multi-node setup, each environment gets its own domain, namespace, and full set of services. The Nginx node handles TLS termination and proxies traffic to the cluster's Istio ingress gateway.

```
                          ┌─────────────────────┐
                          │    DNS Provider      │
                          │  qa.openg2p.org  ──┐ │
                          │  *.qa.openg2p.org ─┘ │
                          └────────┬─────────────┘
                                   │ A records
                                   ▼
┌──────────────────────────────────────────────────────────────┐
│  Nginx Node                              (manual setup)      │
│                                                              │
│  • DNS A records → this node's IP                            │
│  • Customer-provided wildcard TLS cert (CA-issued)           │
│  • Nginx server block → proxy to Istio ingress               │
└──────────────────────┬───────────────────────────────────────┘
                       │ proxy_pass → http://istio_ingress
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  Kubernetes Cluster Node(s)                                  │
│                                                              │
│  Scaffolding + Rancher UI Commons:                           │
│    • Namespace                                               │
│    • Rancher Project                                         │
│    • Istio Gateway                                           │
│    • Helm (Rancher UI): openg2p-commons-base                 │
│    • Helm (Rancher UI): openg2p-commons-services             │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│  Storage Node (pre-existing)                                 │
│    • PostgreSQL                                              │
│    • MinIO                                                   │
└──────────────────────────────────────────────────────────────┘
```

The setup has two parts:

| Part                          | Where                             | What                                                   |
| ----------------------------- | --------------------------------- | ------------------------------------------------------ |
| **Nginx setup** (Steps 1-3)   | On the Nginx node (manual)        | DNS, TLS certificate, Nginx server block, open public firewall |
| **Cluster scaffolding**       | Workstation / production scripts  | Namespace, Rancher project, Istio gateway              |
| **Commons**                   | Rancher UI only                   | `openg2p-commons-base` then `openg2p-commons-services` |

## Prerequisites

| Requirement                 | Details                                                                                  |
| --------------------------- | ---------------------------------------------------------------------------------------- |
| **Infrastructure**          | Nginx node, K8s cluster, Istio, and Rancher are all running                              |
| **Procurement complete**    | DNS records, TLS cert, and Nginx access — see [Prerequisites & Procurement](prerequisites-procurement.md) |
| **DNS records**             | `<base_domain>` and `*.<base_domain>` A records pointing to the Nginx node               |
| **TLS cert on Nginx node**  | Wildcard cert at `/etc/openg2p/certs/<base_domain>/{fullchain.pem,privkey.pem}` (customer-provided) |
| **Nginx node**              | `nginx` running, `istio_ingress` upstream configured                                     |
| **Workstation**             | `kubectl` and `helm` installed, plus the base toolchain (bash 4+, ssh, openssl, git). See [Operator's workstation](infrastructure-setup/provisioning.md#operators-workstation) for the canonical list, supported OSes, and per-OS install commands. Kubeconfig with admin access to the cluster is also required. |

{% hint style="info" %}
Scaffolding scripts live in [`openg2p-deployment`](https://github.com/OpenG2P/openg2p-deployment) under `automation/environment/`. Commons is installed from the Rancher UI only.
{% endhint %}

## Step-by-Step Guide

### Step 1: Verify DNS records (procured up front)

_**Production:** manual — a procurement prerequisite (no script creates DNS records). **Standalone:** manual._

DNS records should have been procured as part of the [Prerequisites & Procurement](prerequisites-procurement.md) step. For this environment you need:

| Type | Name               | Value             |
| ---- | ------------------ | ----------------- |
| A    | `qa.openg2p.org`   | `<nginx_node_ip>` |
| A    | `*.qa.openg2p.org` | `<nginx_node_ip>` |

{% hint style="warning" %}
Verify DNS resolution before proceeding:

```bash
dig qa.openg2p.org
# Should return the Nginx node IP
```
{% endhint %}

### Step 2: Place the customer-provided TLS certificate

_**Production:** automated — the cert was installed on the Reverse Proxy in Stage 3 (Infrastructure); **skip this step**. **Standalone:** manual._

The wildcard certificate for `*.<base_domain>` (covering the apex too) is **procured from the customer's chosen CA** — commercial (DigiCert, GlobalSign, Sectigo) or national / sovereign — as listed in the [procurement checklist](prerequisites-procurement.md). Let's Encrypt is acceptable only for sandbox / PoC; see the note at the end of this step.

On the **Nginx node**, place the cert files at the standard path:

```bash
sudo mkdir -p /etc/openg2p/certs/qa.openg2p.org

# Upload your fullchain + private key
sudo cp /path/to/wildcard.fullchain.pem  /etc/openg2p/certs/qa.openg2p.org/fullchain.pem
sudo cp /path/to/wildcard.key            /etc/openg2p/certs/qa.openg2p.org/privkey.pem

# Set correct permissions
sudo chmod 644 /etc/openg2p/certs/qa.openg2p.org/fullchain.pem
sudo chmod 600 /etc/openg2p/certs/qa.openg2p.org/privkey.pem
```

Verify the cert covers the expected hostnames:

```bash
sudo openssl x509 -noout -ext subjectAltName \
  -in /etc/openg2p/certs/qa.openg2p.org/fullchain.pem
# Should include: DNS:*.qa.openg2p.org, DNS:qa.openg2p.org
```

<details>

<summary>Sandbox / PoC only — Let's Encrypt</summary>

If you're spinning up a quick sandbox and don't have a commercial cert, you can use Let's Encrypt with a DNS-01 challenge:

```bash
sudo certbot certonly \
  --manual --preferred-challenges dns --agree-tos \
  --email admin@openg2p.org \
  -d "qa.openg2p.org" -d "*.qa.openg2p.org"
```

Certbot prompts for TXT records you must add at your DNS provider. After issuance, copy the files to the standard path:

```bash
sudo mkdir -p /etc/openg2p/certs/qa.openg2p.org
sudo cp /etc/letsencrypt/live/qa.openg2p.org/fullchain.pem /etc/openg2p/certs/qa.openg2p.org/
sudo cp /etc/letsencrypt/live/qa.openg2p.org/privkey.pem   /etc/openg2p/certs/qa.openg2p.org/
```

Cloudflare DNS plugin (`python3-certbot-dns-cloudflare`) or Route53 plugin (`python3-certbot-dns-route53`) can automate the TXT record dance. **Do not use Let's Encrypt for production government deployments** — most procurement policies disallow it.

</details>

### Step 3: Expose the environment on the Reverse Proxy

_**Production & standalone:** manual — this is the citizen "go-public" action on the Reverse Proxy (the env stage is laptop-side and does not touch the RP). Do it when you're ready to serve citizen traffic._

This is the step that **opens the system to citizens**. It has two parts: an Nginx server block for the environment's hostnames, and opening the public channel at the firewall. Until now the Reverse Proxy served only the admin tools (Rancher, Keycloak) on the private channel — this step adds the public, citizen-facing channel alongside them.

{% hint style="info" %}
**Admin stays private — automatically.** The admin server blocks installed by the [infrastructure automation](infrastructure-setup/production-automation/) carry a source-IP allowlist (`allow <wg_subnet>; allow <private_subnet>; deny all;`). The citizen block you add below carries **no** allowlist. So even after you open public `80/443` here, a request to `rancher.<domain>` from the internet is still rejected by source IP, while citizen services are served normally. See [Channel separation](../../deployment/openg2p-deployment-model.md#channel-separation-public-vs-private-access) for the full three-layer model.
{% endhint %}

#### 3a. Nginx server block (citizen channel)

On the **Reverse-Proxy / Nginx node**, create the server block that references the cert from Step 2. Note the **listen address** and the **absence of an allowlist** — both deliberate:

{% tabs %}
{% tab title="AWS / behind NAT" %}
Bind to the RP's **private** IP. Public traffic to the Elastic IP (AWS) or your DNAT address (on-prem behind a firewall) arrives NAT'd to this private IP, so binding here serves it — and it coexists cleanly with the admin blocks already on `<rp_private_ip>:443` (different `server_name`, same socket — no conflict).

```nginx
listen <rp_private_ip>:80;
listen <rp_private_ip>:443 ssl;
```
{% endtab %}
{% tab title="On-prem (public IP on the NIC)" %}
If the RP holds its public IP **directly** on the NIC (no upstream NAT), bind the citizen block to that public IP. Admin blocks remain on the private IP, so there is no listen conflict.

```nginx
listen <rp_public_ip>:80;
listen <rp_public_ip>:443 ssl;
```
{% endtab %}
{% endtabs %}

```bash
# Use the listen address from the tab above in place of <listen_ip>.
sudo tee /etc/nginx/sites-available/openg2p-env-qa.conf > /dev/null <<'EOF'
# OpenG2P environment: qa  ·  Domain: *.qa.openg2p.org  ·  CITIZEN channel (public)

server {
    listen <listen_ip>:80;
    server_name *.qa.openg2p.org qa.openg2p.org;
    return 301 https://$host$request_uri;
}

server {
    listen <listen_ip>:443 ssl;
    server_name *.qa.openg2p.org qa.openg2p.org;

    # NO allow/deny here — citizen services must be reachable by the public.
    # (Admin blocks for rancher/keycloak keep their allowlist and stay private.)

    ssl_certificate     /etc/openg2p/certs/qa.openg2p.org/fullchain.pem;
    ssl_certificate_key /etc/openg2p/certs/qa.openg2p.org/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;

    location / {
        proxy_pass                      http://istio_ingress;
        proxy_http_version              1.1;
        proxy_buffering                 on;
        proxy_buffers                   8 16k;
        proxy_buffer_size               16k;
        proxy_busy_buffers_size         32k;
        proxy_set_header                Upgrade $http_upgrade;
        proxy_set_header                Connection "upgrade";
        proxy_set_header                Host $host;
        proxy_set_header                X-Real-IP $remote_addr;
        proxy_set_header                X-Forwarded-Host $host;
        proxy_set_header                X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header                X-Forwarded-Proto https;
        proxy_pass_request_headers      on;
    }
}
EOF
```

{% hint style="warning" %}
The `istio_ingress` upstream must already exist in your Nginx config (the infrastructure automation creates it, pointing at the cluster node's Istio ingress NodePort):

```nginx
upstream istio_ingress {
    server <cluster_node_ip>:30080;
}
```
{% endhint %}

Enable the site and reload Nginx:

```bash
sudo ln -sf /etc/nginx/sites-available/openg2p-env-qa.conf \
            /etc/nginx/sites-enabled/openg2p-env-qa.conf
sudo nginx -t && sudo systemctl reload nginx
```

#### 3b. Open the public channel (firewall)

The infrastructure setup deliberately left public `80/443` **closed** (only SSH + Wireguard were open). Open them now so citizens can reach the environment. The per-host firewall (`ufw`) already allows `80/443` from the private subnet; this step opens them at the **network boundary**.

{% tabs %}
{% tab title="AWS" %}
Add inbound rules to the Reverse-Proxy's Security Group (`<project>-reverse-proxy`):

```bash
SG=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=<project>-reverse-proxy" \
  --query 'SecurityGroups[0].GroupId' --output text)

aws ec2 authorize-security-group-ingress --group-id "$SG" \
  --ip-permissions \
    'IpProtocol=tcp,FromPort=80,ToPort=80,IpRanges=[{CidrIp=0.0.0.0/0,Description=citizen HTTP}]' \
    'IpProtocol=tcp,FromPort=443,ToPort=443,IpRanges=[{CidrIp=0.0.0.0/0,Description=citizen HTTPS}]'
```
{% endtab %}
{% tab title="On-prem" %}
At your perimeter firewall / router, allow inbound `80/tcp` and `443/tcp` from the internet to the Reverse Proxy. If the RP sits behind NAT, also DNAT those ports to the RP's private IP (the address the Nginx citizen block listens on).

No host-level change is needed — the automation already configured `ufw` to accept `80/443` from the private subnet, and the citizen block's source has no allowlist.
{% endtab %}
{% endtabs %}

{% hint style="info" %}
**Admin tools are unaffected.** Opening public `80/443` exposes only the citizen `server_name`s. A request to `rancher.<domain>` / `keycloak.<domain>` still hits the admin server blocks, whose source-IP allowlist returns `403` to any client outside the Wireguard + private subnets.
{% endhint %}

### Step 4: Scaffold the cluster environment (if needed)

_**Production:** skip — already done by `openg2p-prod.sh`. **Standalone:** run scaffolding only._

If the namespace / Rancher Project / Istio Gateway are not already present:

```bash
git clone https://github.com/OpenG2P/openg2p-deployment.git
cd openg2p-deployment/automation/environment
cp env-config.example.yaml env-config.yaml
# Edit environment + base_domain
./env-cluster.sh --config env-config.yaml
```

`env-cluster.sh` creates the namespace, Rancher Project, and Istio Gateway only. It does **not** install Commons.

### Step 5: Install Commons from the Rancher UI

_**Production and standalone:** required — Commons is installed from Rancher only._

1. Connect Wireguard (or otherwise reach Rancher) and open `https://rancher.<domain>`.
2. Select the environment namespace / project.
3. **Apps → Charts → openg2p-commons-base** — install with production values (external PostgreSQL via the `commons-postgresql` secret when using production scaffolding, hostnames, storage class, and so on).
4. Then install **openg2p-commons-services** in the same namespace.
5. Pick chart versions from the [Commons changelog](https://openg2p.gitlab.io/versions/commons/CHANGELOG.html).

{% hint style="info" %}
Do not use Helm CLI scripts under `automation/environment/` to install Commons. Those scripts are scaffolding-only.
{% endhint %}

## Configuration reference (scaffolding)

When using standalone `env-cluster.sh`, `env-config.yaml` needs:

| Key | Purpose |
| --- | --- |
| `environment` | Namespace and Rancher project name |
| `base_domain` | Domain for the Istio Gateway hosts |

Commons chart options are configured in the Rancher Apps UI (not in `env-config.yaml`).

## Next: install your OpenG2P modules

At this point you have a working environment with `commons-base` + `commons-services` installed — the shared infrastructure (PostgreSQL, Kafka, MinIO, Redis, Keycloak, etc.) plus baseline cross-cutting services (eSignet, Superset, ODK). What you **don't** yet have is the OpenG2P product modules a specific deployment actually delivers (registry, payments, beneficiary onboarding, etc.). Each product has its own Helm chart and deployment guide — install whichever modules your rollout requires:

* [**Farmer Registry**](../../products/registry/farmer-registry/deployment/README.md) — Social / Farmer / generic registry (Gen2). Helm Chart 4.x.
* [**PBMS**](../../pbms/deployment/) — Payment & Beneficiary Management System.
* [**SPAR**](../../spar/deployment/) — Single Payee Account Repository.
* [**G2P Bridge**](../../g2p-bridge/deployment/) — government-to-payer bridge (treasury / bank disbursement integration).

Each product page documents its Helm-chart version, deployment commands, Keycloak client setup, and domain-name requirements. Install only the modules required for your use case — none of them are mandatory infrastructure dependencies of the others.

## Creating Multiple Environments

To create additional environments (e.g., `staging`) on the same cluster:

1. Create DNS records for `staging.openg2p.org` and `*.staging.openg2p.org` pointing to the Nginx IP
2. On the Nginx node: obtain a new certificate (Step 2) and add a new server block (Step 3a) with the new domain. The firewall (Step 3b) is already open from the first environment — no need to repeat it.
3. Create a new config file with `environment: staging` and `base_domain: staging.openg2p.org` and run `env-cluster.sh` for scaffolding (or use production `--stage environment` with a different `environment.name`)
4. Install Commons for that environment from the **Rancher UI**

Each environment gets its own namespace, Rancher project, Istio gateway, and Commons install.

## Uninstallation

To tear down an environment's Helm releases (including Commons installed from Rancher), use `env-cluster-uninstall.sh` or production's `openg2p-prod-env-uninstall.sh`. Reinstall Commons afterward from the Rancher UI.

{% hint style="info" %}
The uninstall script takes only `--namespace <name>` — it does **not** read `env-config.yaml`. All cleanup is namespace-scoped, so it doesn't matter which apps or chart versions were originally installed. Every Helm release, Secret, PVC, and (in `--full` mode) the namespace itself is removed.
{% endhint %}

{% tabs %}
{% tab title="Default — Helm + data" %}
Uninstalls **all** Helm releases in the namespace and deletes all data (Secrets, PVCs, PVs). Preserves the namespace, Istio Gateway, and Rancher Project so you can reinstall Commons quickly from the Rancher UI.

```bash
./env-cluster-uninstall.sh --namespace qa
```

**Deletes:**

* ALL Helm releases in the namespace — `commons-services`, `commons`, and any other module charts (Registry, PBMS, SPAR, G2P Bridge, custom charts, etc.). The `commons` release is uninstalled last since other modules depend on its infrastructure.
* All Jobs (hook leftovers)
* All Secrets in the namespace
* All PVCs + associated PVs
* **Chart-owned ConfigMaps only** — those labelled `app.kubernetes.io/managed-by: Helm`, those carrying a `meta.helm.sh/release-name` annotation, or those named `<release>-*`

**Preserved ConfigMaps:** hand-created ConfigMaps (seed data, migration payloads, debug patches) are **kept** and listed in the output, so a shared namespace does not lose operator artifacts. Cluster- and mesh-owned ConfigMaps (`kube-root-ca.crt`, `istio-*`) are never touched.

**Preserves:**

* Namespace, Istio Gateway, Rancher Project
* Nginx config, certificates, DNS records
{% endtab %}

{% tab title="Full teardown" %}
Everything in the default mode, plus the Istio Gateway, Rancher Project, and the namespace itself. Leaves only infra-level resources.

```bash
./env-cluster-uninstall.sh --namespace qa --full
```

**Also deletes:**

* Istio Gateway(s) in the namespace
* Rancher Project association (and the project itself, if Rancher is on this cluster)
* The namespace itself

**Preserves:**

* Nginx config on the Nginx node
* Let's Encrypt certificates
* DNS records
* Cluster / Rancher / Istio installations
{% endtab %}

{% tab title="Dry-run" %}
See what would be deleted without actually deleting anything:

```bash
./env-cluster-uninstall.sh --namespace qa --full --dry-run
```
{% endtab %}
{% endtabs %}

{% hint style="warning" %}
The script previews everything that will be deleted and asks for confirmation before proceeding.

* Default mode requires typing `yes`
* `--full` mode requires typing the namespace name (prevents accidental wipes of the wrong environment)

Use `--yes` to skip confirmation for automation/CI.
{% endhint %}

### Uninstall CLI options

```bash
./env-cluster-uninstall.sh --namespace <name> [options]
```

| Option               | Description                                               |
| -------------------- | --------------------------------------------------------- |
| `--namespace <name>` | Target Kubernetes namespace to tear down (required)       |
| `--full`             | Also delete Istio Gateway, Rancher Project, and namespace |
| `--yes`              | Skip confirmation prompt (for automation)                 |
| `--dry-run`          | Show what would be deleted without actually deleting      |
| `--help`             | Show help message                                         |

{% hint style="info" %}
The uninstall script never touches the Nginx node, DNS records, certificates, or other namespaces on the cluster. Those are intentionally managed outside this automation.
{% endhint %}

{% hint style="warning" %}
**Why ConfigMaps are filtered rather than wiped**

Helm-labelled ConfigMaps that have lost their `meta.helm.sh/release-name` annotation are not removed by `helm uninstall` — it cannot associate them with any release. Left behind, they cause `invalid ownership metadata` failures the next time a chart tries to create a ConfigMap of the same name, so the uninstall script removes them explicitly.

It deliberately stops short of `kubectl delete configmap --all`: on a shared namespace that would silently destroy hand-applied seed data and migration payloads that no chart will ever recreate. Anything not chart-owned is listed in the output so you can remove it by hand if you want.
{% endhint %}

## Accessing host PostgreSQL from your laptop

Production PostgreSQL is the **host install on the storage node**, firewalled to the **compute node only** — so you reach it over **SSH**, not a direct connection (which fails even on Wireguard, because WG NATs your traffic to the reverse-proxy's IP). The full how-to — on-box `psql`, the SSH-tunnel routes, GUI clients, and where the credentials live — is the day-2 operational guide:

➡️ **[Access a Database from Outside the Cluster → Host PostgreSQL (production)](../../deployment/deployment-guide/access-a-database-from-outside-the-cluster.md#host-postgresql-production)**

Quick reference: the superuser password is on the storage node at `/etc/openg2p/secrets/postgres-superuser.env` and in the installer's final summary (`automation/production/setup-output/SETUP-SUMMARY.txt`).

## File Structure

```
automation/environment/
├── env-cluster.sh              # Scaffolding only (namespace / project / gateway)
├── env-cluster-uninstall.sh    # Tear down Helm releases in a namespace
├── env-refresh.sh              # Uninstall releases; reinstall Commons from Rancher UI
├── env-config.example.yaml     # Scaffolding config — copy and edit
├── lib/
│   └── utils.sh                # Shared utilities (logging, config parser)
└── .gitignore                  # Ignores env-config.yaml
```

## Troubleshooting

{% hint style="info" %}
`env-cluster.sh` is scaffolding-only and idempotent — re-run it on failure. Use `--step <spec>` (e.g. `--step 1-3`) for scaffolding steps only. Install or reinstall Commons from the Rancher UI.
{% endhint %}

### Certificate issues (on Nginx node)

```bash
# Check if cert exists
sudo ls -la /etc/letsencrypt/live/qa.openg2p.org/

# Test renewal
sudo certbot renew --dry-run

# Check TXT record propagation
dig TXT _acme-challenge.qa.openg2p.org
```

### Nginx issues (on Nginx node)

```bash
# Test config syntax
sudo nginx -t

# Check the server block
cat /etc/nginx/sites-enabled/openg2p-env-qa.conf

# Check if upstream exists
grep -r "istio_ingress" /etc/nginx/

# Check Nginx error log
sudo tail -50 /var/log/nginx/error.log
```

### Cluster issues (from workstation)

```bash
# Verify kubectl access
kubectl cluster-info
kubectl get nodes

# Check namespace and pods
kubectl get pods -n qa
kubectl get pods -n qa --field-selector=status.phase!=Running

# Check Helm releases
helm list -n qa

# Check Istio gateway
kubectl get gateway -n qa

# Check Rancher project
kubectl get projects.management.cattle.io -n local -o json | \
  jq '.items[] | {name: .metadata.name, display: .spec.displayName}'
```

### eSignet / mock-identity crashloop — `relation "key_alias" does not exist`

After installing commons-services, `esignet` and `mock-identity-system` may be in `CrashLoopBackOff` with this in their logs:

```
org.postgresql.util.PSQLException: ERROR: relation "key_alias" does not exist
```

**Cause.** eSignet and mock-identity each embed the keymanager library, which needs the keymanager schema (`key_alias`, `key_store`, …) **in their own database**. Each ships its schema-init as a `helm.sh/hook: post-install` Job, which deadlocks `helm --wait`: the pods can't become Ready until the schema exists, but the post-install hook that creates the schema only runs *after* the release is Ready. So the hook never runs and the release ends as `failed`. (Standalone keymanager is unaffected — its init runs as a regular resource.) This is a chart-level issue in `openg2p-commons-services`.

{% hint style="info" %}
After installing Commons from the **Rancher UI**, if eSignet / mock-identity crashloop with this error, apply the manual fix below.
{% endhint %}

Materialise the schema-init Jobs by hand (replace `qa` with your namespace):

```bash
# Materialise the post-install hook Jobs as regular Jobs (strips the hook annotations)
helm get hooks commons-services -n qa \
  | awk 'BEGIN{RS="\n---\n"} /kind: Job/ && /mosipid\/postgres-init/ {print "---"; print}' \
  | grep -vE '^[[:space:]]*"?helm\.sh/hook(-delete-policy|-weight)?"?:' \
  | kubectl apply -n qa -f -

# Wait for them to finish, then restart the crashlooping workloads
kubectl -n qa wait --for=condition=complete job \
  -l app.kubernetes.io/name=commons-services-esignet-postgres-init --timeout=5m
kubectl -n qa rollout restart deploy \
  commons-services-esignet commons-services-mock-identity-system
```

The init is idempotent (it skips tables that already exist), so re-running is safe.
