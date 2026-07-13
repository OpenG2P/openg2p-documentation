---
description: Developer Installation for Openg2p Registry Staff Portal UI
---

# Staff Portal UI

### Setup

Follow these steps to set up Openg2p Registry Staff Portal UI:

* **Clone the Repository**: Clone the Openg2p Registry Staff Portal UI repository from the source:

```
git clone git@github.com:OpenG2P/openg2p-registry-staff-portal-ui.git
```

* **Install Dependencies**: Navigate into the cloned Openg2p Registry Staff Portal UI directory and install dependencies using npm:

```
npm install
```

* **Configuration**: Configure the OpenG2P Registry Staff Portal UI to connect to the APIs by setting the required environment variables.

```
IAM_URL="http://iam.dev.openg2p.my"
BACKEND_API_URL="https://staff-farmer-registry-gen2.dev.openg2p.org"
MASTERDATA_BACKEND_API_URL="https://gen2-master-data.dev.openg2p.org"

VERIFY_SERVICE_URL="https://registry-farmer.dev.openg2p.org/v1/verify"
VP_CLIENT_ID="did:web:registry-farmer.dev.openg2p.org:v1:verify"

PARTNER_IMPORT_EXPORT_ENABLE="true"

PAGE_SIZE=10

LOGIN_PROVIDER_ID="1"
APPLICATION_MNEMONIC="registry-staff-portal"
COOKIE_DOMAIN=".dev.openg2p.org"

DEFAULT_LOCALE="en"

# Content-Security-Policy — one env var per directive (space-separated sources).
CSP_SRC_DEFAULT=self
CSP_SRC_SCRIPT=self unsafe-inline
CSP_SRC_STYLE=self unsafe-inline
CSP_SRC_IMG="self blob: data: https://minio-api.dev.openg2p.org"
CSP_SRC_FONT=self
CSP_SRC_CONNECT=self
CSP_SRC_FRAME=self
CSP_SRC_OBJECT=none
CSP_SRC_BASE_URI=self
CSP_SRC_FORM_ACTION=self
CSP_SRC_FRAME_ANCESTORS=none
```

**Nginx Configuration**: Configure Nginx to act as a reverse proxy for Openg2p Registry Staff Portal UI

```
# Install Nginx if not already installed
sudo apt-get update
sudo apt-get install nginx -y

# Create a new configuration file for Openg2p Registry Staff Portal UI
sudo nano /etc/nginx/sites-available/staff-portal.conf
```

* Below is a sample Nginx configuration (`/etc/nginx/sites-available/staff-portal.conf`).

```
server {
    listen 80;
    server_name farmer-registry.openg2p.my;

    proxy_buffer_size 256k;
    proxy_buffers 8 512k;
    proxy_busy_buffers_size 512k;
    large_client_header_buffers 8 256k;

    location / {
        proxy_pass                      http://localhost:3000;
        proxy_http_version              1.1;
        proxy_set_header                Upgrade $http_upgrade;
        proxy_set_header                Connection "upgrade";
        proxy_set_header                Host $host;
        proxy_set_header                Referer $http_referer;
        proxy_set_header                X-Real-IP $remote_addr;
        proxy_set_header                X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header                X-Forwarded-Proto $scheme;
        proxy_pass_request_headers      on;
    }
}
```

* **Enable Configuration**: Enable the Nginx configuration by creating a symbolic link to `sites-enabled`

```
sudo ln -sf /etc/nginx/sites-available/staff-portal.conf /etc/nginx/sites-enabled/
```

* **Adding domain to Hosts**: Add the domain to the hosts for the system to recognize the domain.

```
sudo nano /etc/hosts
127.0.0.1 farmer-registry.openg2p.my
```

* **Restart Nginx**: Restart the Nginx service to apply the changes:

```
sudo service nginx restart
```

* **Start Openg2p IAM Service**: Ensure that Openg2p IAM Service is up and running. Refer to the Openg2p IAM Service documentation.
* **Run Openg2p Registry Staff Portal UI**: This command starts the development server. Open a web browser and navigate to the specified URL ([http://localhost:3000](http://localhost:3000/)) or a specific domain as per nginx server ([http://farmer-registry.openg2p.my](http://farmer-registry.openg2p.my/)) to access the UI interface.

```
npm run dev
```
