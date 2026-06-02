---
description: Setting up OpenG2P environments on an existing multi-node infrastructure.
---

# Environment Setup

This guide covers creating OpenG2P environments (namespace + services) on an **existing multi-node infrastructure** where Nginx, the Kubernetes cluster, and storage run on separate nodes.&#x20;

{% hint style="info" %}
Note that for a  single-node setup the environment is installed as part of the [single node sandbox installation](infrastructure-setup/single-node-automation.md).
{% endhint %}

{% hint style="danger" %}
**Before you start — procurement prerequisites**

DNS records, TLS certificates, and server access for this environment must already be in place before `env-cluster.sh` runs. If you have not yet planned and procured these, start with the [**Prerequisites & Procurement**](prerequisites-procurement.md) page — fill out the deployment plan once, generate a single checklist covering every environment, and hand it to your IT / network / cert team. TLS issuance from sovereign or commercial CAs typically takes 2-4 weeks; planning all environments up front avoids serial procurement cycles.
{% endhint %}

{% hint style="warning" %}
**In-cluster versus External Storage**

This script installs [**commons**](../../deployment/concepts/openg2p-commons-helm-chart.md) modules with **in-cluster** PostgreSQL, MinIO, Kafka, etc. This may be used to test the entire system before going for a production rollout.  For **production deployments** — where you typically need external PostgreSQL, custom hostnames, storage classes, replicas, image registry settings, and other overrides — disable module installation in the config (`modules.commons: false`) and install `openg2p-commons-base` and `openg2p-commons-services` via the **Rancher UI**, where the chart's `questions.yml` provides a guided form for all production parameters.

The script is still useful in production for the namespace, Rancher Project, and Istio Gateway scaffolding.
{% endhint %}

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
│  env-cluster.sh targets here (via kubectl from workstation): │
│    • Namespace                                               │
│    • Rancher Project                                         │
│    • Istio Gateway                                           │
│    • Helm: openg2p-commons-base                              │
│    • Helm: openg2p-commons-services                          │
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
| **Nginx setup** (Steps 1-3)   | On the Nginx node (manual)        | DNS, TLS certificate, Nginx server block               |
| **Cluster setup** (Steps 4-5) | From your workstation (automated) | Namespace, Rancher project, Istio gateway, Helm charts |

## Prerequisites

| Requirement                 | Details                                                                                  |
| --------------------------- | ---------------------------------------------------------------------------------------- |
| **Infrastructure**          | Nginx node, K8s cluster, Istio, and Rancher are all running                              |
| **Procurement complete**    | DNS records, TLS cert, and Nginx access — see [Prerequisites & Procurement](prerequisites-procurement.md) |
| **DNS records**             | `<base_domain>` and `*.<base_domain>` A records pointing to the Nginx node               |
| **TLS cert on Nginx node**  | Wildcard cert at `/etc/openg2p/certs/<base_domain>/{fullchain.pem,privkey.pem}` (customer-provided) |
| **Nginx node**              | `nginx` running, `istio_ingress` upstream configured                                     |
| **Workstation**             | `kubectl` and `helm` installed, kubeconfig with admin access to the cluster              |

{% hint style="info" %}
The source code for the automation script lives in the [`openg2p-deployment`](https://github.com/OpenG2P/openg2p-deployment) repository under `automation/environment/`.
{% endhint %}

## Step-by-Step Guide

### Step 1: Verify DNS records (procured up front)

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

### Step 3: Create Nginx server block

On the **Nginx node**, create the server block that references the cert you placed in Step 2:

```bash
sudo tee /etc/nginx/sites-available/openg2p-env-qa.conf > /dev/null <<'EOF'
# OpenG2P environment: qa
# Domain: *.qa.openg2p.org

server {
    listen 80;
    server_name *.qa.openg2p.org qa.openg2p.org;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name *.qa.openg2p.org qa.openg2p.org;

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
The `istio_ingress` upstream must already exist in your Nginx config (typically in `/etc/nginx/conf.d/upstream.conf` or similar). It should point to the cluster node's Istio ingress gateway port:

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

### Step 4: Configure env-cluster.sh

On your **workstation**, clone the repo and prepare the config:

```bash
git clone https://github.com/OpenG2P/openg2p-deployment.git
cd openg2p-deployment/automation/environment
cp env-config.example.yaml env-config.yaml
```

Edit `env-config.yaml` with your values:

```yaml
environment: "qa"
base_domain: "qa.openg2p.org"
admin_email: "admin@openg2p.org"

modules:
  commons: true
```

{% hint style="info" %}
`admin_email` is passed to the commons-base chart as `keycloak-init.realms.staff.users[0].email` — it becomes the default admin user in the per-env Keycloak `staff` realm. Leave it empty to accept the chart's default.
{% endhint %}

### Step 5: Run env-cluster.sh

From your **workstation** (with kubectl access to the cluster):

```bash
./env-cluster.sh --config env-config.yaml
```

The script performs 5 steps automatically:

| Step | What it does                                                                      |
| ---- | --------------------------------------------------------------------------------- |
| 1    | Creates the K8s namespace                                                         |
| 2    | Creates a Rancher Project and associates the namespace                            |
| 3    | Creates the Istio Gateway for `*.qa.openg2p.org`                                  |
| 4    | Installs `openg2p-commons-base` (PostgreSQL, Kafka, MinIO, Redis, Keycloak, etc.) |
| 5    | Installs `openg2p-commons-services` (eSignet, Superset, ODK, etc.)                |

{% hint style="info" %}
Takes approximately 15-20 minutes. The script is idempotent — it checks for existing resources before creating them.
{% endhint %}

## Configuration Reference

| Key                                | Description                                                                                                                                        |
| ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `environment`                      | Environment name — used as namespace and Rancher project (e.g., `qa`)                                                                              |
| `base_domain`                      | Full base domain for this environment (e.g., `qa.openg2p.org`)                                                                                     |
| `admin_email`                      | Email for the default Keycloak `staff`-realm admin user. Maps to `keycloak-init.realms.staff.users[0].email`. Leave empty to accept chart default. |
| `commons_base.chart_version`       | Helm chart version for openg2p-commons-base                                                                                                        |
| `commons_base.chart_path`          | Local chart path (leave empty to use remote repo)                                                                                                  |
| `commons_base.extra_helm_args`     | Additional `--set` flags for the base chart                                                                                                        |
| `commons_services.chart_version`   | Helm chart version for openg2p-commons-services                                                                                                    |
| `commons_services.chart_path`      | Local chart path (leave empty to use remote repo)                                                                                                  |
| `commons_services.extra_helm_args` | Additional `--set` flags for the services chart                                                                                                    |
| `modules.commons`                  | Enable/disable commons installation (`true`/`false`)                                                                                               |

## CLI Options

```bash
./env-cluster.sh --config env-config.yaml [options]
```

| Option            | Description                                |
| ----------------- | ------------------------------------------ |
| `--config <file>` | Path to environment config file (required) |
| `--step <N>`      | Run only a specific step (1-5)             |
| `--force`         | Uninstall and reinstall Helm charts        |
| `--help`          | Show help message                          |

## Creating Multiple Environments

To create additional environments (e.g., `staging`) on the same cluster:

1. Create DNS records for `staging.openg2p.org` and `*.staging.openg2p.org` pointing to the Nginx IP
2. On the Nginx node: obtain a new certificate and create a server block (repeat Steps 2-3 with the new domain)
3. Create a new config file with `environment: staging` and `base_domain: staging.openg2p.org`
4. Run `env-cluster.sh` from your workstation with the new config

Each environment gets its own namespace, Rancher project, Istio gateway, and full set of services.

## Uninstallation

To tear down an environment, use `env-cluster-uninstall.sh` (the reverse of `env-cluster.sh`). It has two modes.

{% hint style="info" %}
The uninstall script takes only `--namespace <name>` — it does **not** read `env-config.yaml`. All cleanup is namespace-scoped, so it doesn't matter which apps or chart versions were originally installed. Every Helm release, Secret, PVC, and (in `--full` mode) the namespace itself is removed.
{% endhint %}

{% tabs %}
{% tab title="Default — Helm + data" %}
Uninstalls **all** Helm releases in the namespace and deletes all data (Secrets, PVCs, PVs). Preserves the namespace, Istio Gateway, and Rancher Project so the environment can be reinstalled quickly.

```bash
./env-cluster-uninstall.sh --namespace qa
```

**Deletes:**

* ALL Helm releases in the namespace — `commons-services`, `commons`, and any other module charts (Registry, PBMS, SPAR, G2P Bridge, custom charts, etc.). The `commons` release is uninstalled last since other modules depend on its infrastructure.
* All Jobs (hook leftovers)
* All Secrets in the namespace
* All PVCs + associated PVs

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

## File Structure

```
automation/environment/
├── env-cluster.sh              # Install: run from workstation (kubectl/helm)
├── env-cluster-uninstall.sh    # Uninstall: reverse of env-cluster.sh
├── env-config.example.yaml     # Example config — copy and edit
├── lib/
│   └── utils.sh                # Shared utilities (logging, config parser)
└── .gitignore                  # Ignores env-config.yaml
```

## Troubleshooting

{% hint style="info" %}
`env-cluster.sh` is idempotent — re-run it on failure. Use `--step <N>` to run a specific step, or `--force` to tear down and reinstall Helm charts.
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
