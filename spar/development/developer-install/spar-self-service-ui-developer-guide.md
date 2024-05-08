---
description: Developer guide
---

# Spar Self Service UI developer Guide

### Introduction

Spar UI is a user interface designed to interact with Spar, a tool that serves as an ID mapper and displays linked account information. This documentation serves as a guide to understanding Spar UI, its features, and how to set it up to work with Spar services.

### Features

1. **ID Mapping**: Spar UI facilitates the mapping of IDs between different systems or accounts.
2. **Linked Account Information**: Users can view information about their linked accounts through the Spar UI interface.
3. **User-Friendly Interface**: The UI is designed to be intuitive and easy to navigate.

### Prerequisites

Before setting up Spar UI, ensure the following prerequisites are met:

1. **Spar Services**: Spar UI depends on the following Spar services:
   * **Spar-SelfService-API**: A FastAPI service responsible for self-service operations, running on port 8000.
   * **Spar-Mapper-API**: A FastAPI service responsible for ID mapping functionality, running on port 8007.
2. **Node.js and npm**: Spar UI is built using Next.js, which requires Node.js and npm to be installed on your system.
3. **Nginx**: Install and configure Nginx to act as a reverse proxy to avoid CORS issues when accessing Spar services.

### Setup

Follow these steps to set up Spar UI:

* **Clone the Repository**: Clone the Spar UI repository from the source:

```sh
git clone https://github.com/OpenG2P/openg2p-spar-self-service-ui.git
```

* **Install Dependencies**: Navigate into the cloned Spar UI directory and install dependencies using npm:

```sh
npm install
```

* **Configuration**: Configure Spar UI to connect with the Spar services. This typically involves setting environment variables&#x20;

<pre class="language-shellscript"><code class="lang-shellscript"><strong>NEXT_PUBLIC_BASE_PATH="/spar/self-service-ui"
</strong>NEXT_PUBLIC_BASE_API_PATH="/spar/self-service-api/"
</code></pre>

* **Nginx Configuration**: Configure Nginx to act as a reverse proxy for Spar services.&#x20;

```sh
# Install Nginx if not already installed
sudo apt-get update
sudo apt-get install nginx -y

# Create a new configuration file for Spar services
sudo nano /etc/nginx/sites-available/spar.conf

```

* &#x20;Below is a sample Nginx configuration (`/etc/nginx/sites-available/spar.conf`).&#x20;
* This configuration directs requests to `/spar/selfservice-api` to Spar-SelfService- running on port 8000,
* &#x20;Requests to `/spar/mapper-api` to Spar-Mapper running on port 8007, and all other requests to Spar UI running on port 3000 `/spar/self-service-ui`.

```
server {
    listen 80;
    server_name spar.openg2p.my;
    location = / {
        return 301 /spar/self-service-ui;
    }
        location /spar/self-service-ui {
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
    location /spar/self-service-api/ {
                proxy_pass                      http://localhost:8000/;
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
    location /spar/mapper-api/ {
                proxy_pass                      http://localhost:8007/;
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
ln -s /etc/nginx/sites-available/spar.conf /etc/nginx/sites-enabled/
```

* **Adding domain to Hosts**: Add the domain to the hosts for the system to recognize the domain.

```sh
sudo nano /etc/hosts
#127.0.0.1       spar.openg2p.my 
#add the above line
```

* **Restart Nginx**: Restart the Nginx service to apply the changes:

```sh
sudo service nginx restart
```

* **Start Spar Services**: Ensure that Spar-SelfService and Spar-Mapper services are up and running. Refer to the Mapper and Self service documentation.
* **Run Spar UI**: Start the Spar UI application: This command starts the development server for Spar UI. Open a web browser and navigate to the specified URL (usually http://localhost:3000) or a specific domain as per nginx server ,to access the Spar UI interface.

```sh
npm run dev
```

### Usage

Once Spar UI is set up and running, users can perform the following actions:

* **View Linked Account Information**: Access information about linked accounts.
* **Navigate the UI**: Explore different sections and features using the intuitive user interface.
* **Remove or Modify Account**: Seamless Modification and deletion of accounts linked for your ID.

### Troubleshooting

If you encounter any issues during setup or usage, refer to the following resources:

* **Spar Services Documentation**: Refer to the documentation for Spar-SelfService and Spar-Mapper for troubleshooting related to these services.
* **Community Support**: Seek help from the Spar community forums or discussion channels for assistance from other users and developers.

### Conclusion

Spar UI provides a convenient interface for interacting with Spar services, allowing users to manage ID mappings and access linked account information. By following this documentation, you can set up Spar UI and leverage its features effectively.

\
