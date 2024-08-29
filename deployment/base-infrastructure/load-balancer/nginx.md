---
description: Installation of Nginx load balancer
---

# Nginx

Nginx is used as both reverse proxy and load balancing for on-prem deployments.

## Installation

*   Run this to install nginx.

    ```bash
    sudo apt install nginx
    ```
*   Run this to delete default server.

    ```bash
    sudo rm /etc/nginx/sites-enabled/default
    ```
*   Set `client_max_body_size` to `50m` :

    ```bash
    client_max_body_size 50m;
    ```
*   Restart nginx.

    ```bash
    sudo systemctl restart nginx
    ```

This is only a one-time installation. Whenever you want to add new servers to this Nginx, follow the [Install Servers to Nginx Section](nginx.md#install-servers-to-nginx).

## Install servers to Nginx

### Prerequisites

* [Create wildcard TLS certificates](../../deployment-guide/ssl-certificates-using-letsencrypt.md) (This certificate can be created each time for all the other servers you can configure later).

### Installation

* Once nginx server is installed, it will create `sites-enabled` and `sites-available` directories inside /etc/nginx directory.
* Navigate to `/etc/nginx/sites-available` directory and create a file called `<sandbox name>.conf` (Example: `prod-openg2p.conf`) by using [kubernetes/nginx/sites.sample.conf ](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/nginx/server.sample.conf)file as a template.

{% hint style="info" %}
Creation of the `<sandbox name>.conf` file applies only to one server in the nginx node. Repeat this section for every server to be added.
{% endhint %}

* Use a new Listen IP Address for every server. It is recommended to add a new network interface in the same VM which is part of the same network.
* When configuring upstream servers, you need to configure the node port of the Istio IngressGateway. Therefore, it is important to understand the ports and determine which ports connect to which IngressGateway and for what purpose.
*   Run this to enable the server that is added now.

    ```bash
    sudo ln -s /etc/nginx/sites-available/<sandbox name>.conf /etc/nginx/sites-enabled/
    ```
*   Test nginx conf for errors.

    ```bash
    sudo nginx -t
    ```
*   Restart nginx.

    ```bash
    sudo systemctl restart nginx
    ```

### Post-installation

Map the hostnames to Nginx IPs on your DNS service, such as Route53 on AWS.
