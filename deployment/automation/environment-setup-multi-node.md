---
description: Setting up OpenG2P environments on an existing multi-node infrastructure
---

# Environment Setup for Multi-Node Configuration

This guide covers creating OpenG2P environments (namespace + services) on an **existing multi-node infrastructure** where Nginx, the Kubernetes cluster, and storage run on separate nodes.

{% hint style="info" %}
For single-node deployments where everything runs on a single VM, see [Single-Node Automation](single-node-automation.md).
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
│  • Let's Encrypt wildcard cert (certbot)                     │
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
│    • Keycloak secret                                         │
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

| Part | Where | What |
| --- | --- | --- |
| **Nginx setup** (Steps 1-3) | On the Nginx node (manual) | DNS, TLS certificate, Nginx server block |
| **Cluster setup** (Steps 4-5) | From your workstation (automated) | Namespace, Rancher project, Istio, Helm charts |

## Prerequisites

| Requirement | Details |
| --- | --- |
| **Infrastructure** | Nginx node, K8s cluster, Istio, Rancher, and Keycloak are all running |
| **Nginx node** | `certbot` installed, `nginx` running, `istio_ingress` upstream configured |
| **Workstation** | `kubectl` and `helm` installed, kubeconfig with admin access to the cluster |
| **DNS access** | Ability to create A records and TXT records at your DNS provider |

{% hint style="info" %}
The source code for the automation script lives in the [`openg2p-deployment`](https://github.com/OpenG2P/openg2p-deployment) repository under `automation/environment/`.
{% endhint %}

## Step-by-Step Guide

### Step 1: Create DNS records

At your DNS provider, create two A records pointing to the **Nginx node's public IP**:

| Type | Name | Value |
| --- | --- | --- |
| A | `qa.openg2p.org` | `<nginx_node_ip>` |
| A | `*.qa.openg2p.org` | `<nginx_node_ip>` |

{% hint style="warning" %}
Wait for DNS propagation before proceeding. Verify with:

```bash
dig qa.openg2p.org
# Should return the Nginx node IP
```
{% endhint %}

### Step 2: Obtain Let's Encrypt wildcard certificate

SSH into the **Nginx node** and run certbot with DNS-01 challenge:

```bash
sudo certbot certonly \
  --manual \
  --preferred-challenges dns \
  --agree-tos \
  --email admin@openg2p.org \
  -d "qa.openg2p.org" \
  -d "*.qa.openg2p.org"
```

Certbot will prompt you to create DNS TXT records:

```
Please deploy a DNS TXT record under the name:
  _acme-challenge.qa.openg2p.org
with the following value:
  <random_string>
```

**Do this:**

1. Go to your DNS provider
2. Create a TXT record: `_acme-challenge.qa.openg2p.org` → `<random_string>`
3. Wait for propagation: `dig TXT _acme-challenge.qa.openg2p.org`
4. Press Enter in the certbot prompt

{% hint style="info" %}
Certbot may ask for **two** TXT records (one for each domain). Create both before pressing Enter.
{% endhint %}

On success, certificates are saved at:

```
/etc/letsencrypt/live/qa.openg2p.org/fullchain.pem
/etc/letsencrypt/live/qa.openg2p.org/privkey.pem
```

{% tabs %}
{% tab title="Manual DNS (default)" %}
The manual method shown above works with any DNS provider. You create the TXT record by hand when prompted.
{% endtab %}

{% tab title="Cloudflare (automated)" %}
If you use Cloudflare, install the DNS plugin and automate the TXT record:

```bash
sudo apt install python3-certbot-dns-cloudflare

# Create credentials file
sudo tee /etc/letsencrypt/cloudflare.ini > /dev/null <<EOF
dns_cloudflare_api_token = YOUR_CLOUDFLARE_API_TOKEN
EOF
sudo chmod 600 /etc/letsencrypt/cloudflare.ini

# Obtain cert (fully automated)
sudo certbot certonly --dns-cloudflare \
  --dns-cloudflare-credentials /etc/letsencrypt/cloudflare.ini \
  --dns-cloudflare-propagation-seconds 30 \
  -d "qa.openg2p.org" -d "*.qa.openg2p.org"
```
{% endtab %}

{% tab title="Route53 (automated)" %}
If you use AWS Route53, install the DNS plugin:

```bash
sudo apt install python3-certbot-dns-route53

# Ensure AWS credentials are in the environment
export AWS_ACCESS_KEY_ID=...
export AWS_SECRET_ACCESS_KEY=...

# Obtain cert (fully automated)
sudo certbot certonly --dns-route53 \
  --dns-route53-propagation-seconds 30 \
  -d "qa.openg2p.org" -d "*.qa.openg2p.org"
```
{% endtab %}
{% endtabs %}

### Step 3: Create Nginx server block

Still on the **Nginx node**, create the server block:

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

    ssl_certificate     /etc/letsencrypt/live/qa.openg2p.org/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/qa.openg2p.org/privkey.pem;
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
keycloak_hostname: "keycloak.openg2p.org"

keycloak:
  client_manager_user: "client-manager@openg2p.org"
  client_manager_password: "your-password-here"

modules:
  commons: true
```

### Step 5: Run env-cluster.sh

From your **workstation** (with kubectl access to the cluster):

```bash
./env-cluster.sh --config env-config.yaml
```

The script performs 6 steps automatically:

| Step | What it does |
| --- | --- |
| 1 | Creates the K8s namespace |
| 2 | Creates a Rancher Project and associates the namespace |
| 3 | Creates the Istio Gateway for `*.qa.openg2p.org` |
| 4 | Creates the Keycloak `client-manager` K8s secret |
| 5 | Installs `openg2p-commons-base` (PostgreSQL, Kafka, MinIO, Redis, etc.) |
| 6 | Installs `openg2p-commons-services` (eSignet, Superset, ODK, etc.) |

{% hint style="info" %}
Takes approximately 15-20 minutes. The script is idempotent — it checks for existing resources before creating them.
{% endhint %}

## Configuration Reference

| Key | Description |
| --- | --- |
| `environment` | Environment name — used as namespace and Rancher project (e.g., `qa`) |
| `base_domain` | Full base domain for this environment (e.g., `qa.openg2p.org`) |
| `keycloak_hostname` | Keycloak hostname from infra setup (e.g., `keycloak.openg2p.org`) |
| `keycloak.client_manager_user` | Keycloak client-manager username |
| `keycloak.client_manager_password` | Keycloak client-manager password |
| `commons_base.chart_version` | Helm chart version for openg2p-commons-base |
| `commons_base.chart_path` | Local chart path (leave empty to use remote repo) |
| `commons_base.extra_helm_args` | Additional `--set` flags for the base chart |
| `commons_services.chart_version` | Helm chart version for openg2p-commons-services |
| `commons_services.chart_path` | Local chart path (leave empty to use remote repo) |
| `commons_services.extra_helm_args` | Additional `--set` flags for the services chart |
| `modules.commons` | Enable/disable commons installation (`true`/`false`) |

## CLI Options

```bash
./env-cluster.sh --config env-config.yaml [options]
```

| Option | Description |
| --- | --- |
| `--config <file>` | Path to environment config file (required) |
| `--step <N>` | Run only a specific step (1-6) |
| `--force` | Uninstall and reinstall Helm charts |
| `--help` | Show help message |

## Creating Multiple Environments

To create additional environments (e.g., `staging`) on the same cluster:

1. Create DNS records for `staging.openg2p.org` and `*.staging.openg2p.org` pointing to the Nginx IP
2. On the Nginx node: obtain a new certificate and create a server block (repeat Steps 2-3 with the new domain)
3. Create a new config file with `environment: staging` and `base_domain: staging.openg2p.org`
4. Run `env-cluster.sh` from your workstation with the new config

Each environment gets its own namespace, Rancher project, Istio gateway, and full set of services.

## File Structure

```
automation/environment/
├── env-cluster.sh            # Run from workstation (kubectl/helm)
├── env-config.example.yaml   # Example config — copy and edit
├── lib/
│   └── utils.sh              # Shared utilities (logging, config parser)
└── .gitignore                # Ignores env-config.yaml
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
