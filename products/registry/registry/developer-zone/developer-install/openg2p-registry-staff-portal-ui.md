---
description: >-
  Run the OpenG2P Registry Staff UI locally against remote Staff Portal API,
  IAM, Masterdata, and AWE services that are already deployed.
---

# Staff Portal UI

Run Staff UI locally with remote APIs.

### Prerequisites

* Node.js and npm
* Nginx
* [mkcert](https://github.com/FiloSottile/mkcert) (local TLS certificates)
* The following remote services must already be **running and deployed** (this guide only runs Staff UI locally):
  * Staff Portal API
  * IAM
  * Masterdata API
  * AWE

Configure `.env.local` so Staff UI points at those deployed environments (`BACKEND_API_URL`, `IAM_URL`, `MASTERDATA_BACKEND_API_URL`, and related settings).

### Setup

#### 1. Add hostname

```bash
sudo nano /etc/hosts
```

Add:

```text
127.0.0.1 localstaff-ui.dev.openg2p.org
```

#### 2. Create TLS certificate for the hostname

```bash
mkcert -install

sudo mkdir -p /etc/nginx/ssl

sudo mkcert -cert-file /etc/nginx/ssl/localstaff-ui.dev.openg2p.org.pem \
  -key-file /etc/nginx/ssl/localstaff-ui.dev.openg2p.org-key.pem \
  localstaff-ui.dev.openg2p.org
```

#### 3. Create Nginx configuration for Staff UI

```bash
sudo nano /etc/nginx/sites-available/staff-portal.conf
```

Paste:

```nginx
server {
    listen 80;
    server_name localstaff-ui.dev.openg2p.org;

    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name localstaff-ui.dev.openg2p.org;

    ssl_certificate     /etc/nginx/ssl/localstaff-ui.dev.openg2p.org.pem;
    ssl_certificate_key /etc/nginx/ssl/localstaff-ui.dev.openg2p.org-key.pem;

    proxy_buffer_size 256k;
    proxy_buffers 8 512k;
    proxy_busy_buffers_size 512k;
    large_client_header_buffers 8 256k;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;

        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header Referer $http_referer;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_pass_request_headers on;
    }
}
```

Create the symlink and reload Nginx:

```bash
sudo ln -sf /etc/nginx/sites-available/staff-portal.conf /etc/nginx/sites-enabled/staff-portal.conf

sudo nginx -t

sudo systemctl reload nginx
```

#### 4. Clone the repository

```bash
git clone https://github.com/OpenG2P/registry-platform.git

cd registry-platform/ui/staff-ui
```

#### 5. Use local ui-widgets (optional)

If you are developing against a local widget library build:

```bash
cd ../ui-widgets

npm install

npm run build

cd ../staff-ui

npm install @openg2p/registry-widgets@file:../ui-widgets/
```

#### 6. Create `.env.local` in the staff-ui directory

```bash
BACKEND_API_URL="https://staff-farmer-registry.dev.openg2p.org"
MASTERDATA_BACKEND_API_URL="https://master-data.dev.openg2p.org/"
DEFAULT_LOCALE="en"
IAM_URL="https://staff-iam.dev.openg2p.org"
LOGIN_PROVIDER_ID="1"
APPLICATION_MNEMONIC="farmer-registry-staff-portal"
COOKIE_DOMAIN=".dev.openg2p.org"
CSP_SRC_IMG="self blob: data: https://minio-api.dev.openg2p.org"
```

Adjust URLs and `APPLICATION_MNEMONIC` for the registry environment you are targeting. See `ui/staff-ui/.env.example` for the full set of optional variables.

#### 7. Build and start Staff UI

```bash
npm install

npm run build

npm start
```

#### 8. Open Staff UI

Open [https://localstaff-ui.dev.openg2p.org](https://localstaff-ui.dev.openg2p.org).

### Note

To use a different local hostname, repeat the `/etc/hosts` update, TLS certificate generation, Nginx `server_name` / certificate paths, and matching `.env.local` values (especially `COOKIE_DOMAIN` if the parent domain changes).
