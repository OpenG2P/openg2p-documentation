---
description: Installation of Nginx load balancer
---

# Nginx

Nginx is used as both reverse proxy and load balancing for on-prem deployments.

## Installation

*   Run this to install nginx;

    ```bash
    sudo apt install nginx
    ```
*   Run this to delete default server;

    ```bash
    sudo rm /etc/nginx/sites-enabled/default
    ```
*   Restart nginx

    ```bash
    sudo systemctl restart nginx
    ```

This is only a one-time installation. Whenever you want to add new servers to this Nginx, follow [Install Servers to Nginx Section](nginx.md#install-servers-to-nginx).

## Install Servers to Nginx

This section applies only to one Server. Repeat this section for every server to be added.

### Pre-requisites

* [Create wildcard TLS certificates](../../deployment-guide/ssl-certificates-using-letsencrypt.md) (required to terminate HTTPS connects at Nginx)

### Installation

* Navigate to `/etc/nginx/sites-available` directory and create a file called `<sandbox name>.conf` (Example: `prod-openg2p.conf`) by using [kubernetes/nginx/server.sample.conf](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/nginx/server.sample.conf) file as a template.
  * Use a new Listen IP Address for every server. It is recommended to add a new Network Interface in the same VM which is part of the same network.
  * When configuring upstream servers, the node port of Istio Ingressgateway will need to be configured. So it is important to understand the ports and figure out which ports connect to which Ingressgateway and for what purpose.
*   Run this to enable the server that is just added.

    ```bash
    sudo ln -s /etc/nginx/sites-available/<sandbox name>.conf /etc/nginx/sites-enabled/
    ```
*   Test nginx conf for errors:

    ```bash
    sudo nginx -t
    ```
*   Restart nginx

    ```bash
    sudo systemctl restart nginx
    ```

### Post-installation

Map the hostnames to Nginx IPs on your DNS service (Map the hostnames to Nginx IPs on your DNS service (Route53 on AWS)
