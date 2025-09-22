---
description: Developer Installation for Openg2p Beneficiary Portal UI
---

# Openg2p Beneficiary Portal UI

### Setup

Follow these steps to set up Openg2p Beneficiary Portal UI:

* **Clone the Repository**: Clone the Openg2p Beneficiary Portal UI repository from the source:

```sh
git clone https://github.com/OpenG2P/openg2p-beneficiary-portal-ui.git
```

* **Install Dependencies**: Navigate into the cloned Openg2p Beneficiary Portal UI directory and install dependencies using npm:

```sh
npm install
```

* **Configuration**: Configure Openg2p Beneficiary Portal UI to connect with the Openg2p Portal Server. This typically involves setting environment variables&#x20;

```shellscript
NEXT_PUBLIC_BASE_PATH="/selfservice"
NEXT_PUBLIC_BASE_API_PATH="/v1/selfservice"
NEXT_PUBLIC_LANGUAGES_SUPPORTED="en fr tl"
```

* **Nginx Configuration**: Configure Nginx to act as a reverse proxy for Openg2p Portal Server.&#x20;

```sh
# Install Nginx if not already installed
sudo apt-get update
sudo apt-get install nginx -y

# Create a new configuration file for Openg2p Portal server
sudo nano /etc/nginx/sites-available/selfservice.conf
```

* &#x20;Below is a sample Nginx configuration (`/etc/nginx/sites-available/selfservice.conf`).&#x20;
* This configuration directs requests to `/v1/selfservice` to Openg2p-Portar-Server running on port 8001,

```
server {
    listen 80;
    server_name selfservice17.openg2p.my;
    location = / {
        return 301 /selfservice;
    }
    location /selfservice {
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
    location /v1/selfservice/ {
        proxy_pass                      http://localhost:8001/;
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

```sh
ln -s /etc/nginx/sites-available/selfservice.conf /etc/nginx/sites-enabled/
```

* **Adding domain to Hosts**: Add the domain to the hosts for the system to recognize the domain.

```sh
sudo nano /etc/hosts
#127.0.0.1       selfservice17.openg2p.my
#add the above line
```

* **Restart Nginx**: Restart the Nginx service to apply the changes:

```sh
sudo service nginx restart
```

* **Start Openg2p Portal Server**: Ensure that Beneficiary Portal Server is up and running. Refer to the Openg2p Portal Server documentation.
* **Run Openg2p Beneficiary Portal UI**: This command starts the development server. Open a web browser and navigate to the specified URL ([http://localhost:3000](http://localhost:3000/)) or a specific domain as per nginx server ([http://selfservice17.openg2p.my/selfservice](http://selfservice17.openg2p.my/selfservice)) to access the UI interface.

```sh
npm run dev
```
