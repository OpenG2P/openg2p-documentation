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

## Install servers to Nginx

### Prerequisites

* [Create wildcard TLS certificates](../../deployment-guide/ssl-certificates-using-letsencrypt.md) (required to terminate HTTPS connects at Nginx and this certificate can be created only once for all the other servers you are going to configure later...)

### Installation

* Once nginx server is installed, it will create sites for HTTP redirection. To use streams for TCP connections instead of sites, you need to manually create the `streams-available` and `streams-enabled` directories inside the nginx directory.
* Navigate to `/etc/nginx/streams-available` directory and create a file called `<sandbox name>.conf` (Example: `prod-openg2p.conf`) by using kubernetes/nginx/streams.sample.conf file as a template.\
  **Notes:**

Creation of the `<sandbox name>.conf` section applies only to one server. Repeat this section for every server to be added.

* Use a new Listen IP Address for every server. It is recommended to add a new Network Interface in the same VM which is part of the same network.
* When configuring upstream servers, you need to configure the node port of the Istio IngressGateway. Therefore, it is important to understand the ports and determine which ports connect to which IngressGateway and for what purpose.

<!---->

*   Run this to enable the server that is just added.

    ```bash
    sudo ln -s /etc/nginx/streams-available/<sandbox name>.conf /etc/nginx/streams-enabled/
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

Map the hostnames to Nginx IPs on your DNS service, such as Route53 on AWS.
