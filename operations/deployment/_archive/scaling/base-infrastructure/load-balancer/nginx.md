---
description: Installation of Nginx load balancer
---

# Nginx

Nginx is used as both reverse proxy and load balancing for on-prem deployments.

## Installation

*   Follow the procedure to install nginx.\
    Install the prerequisite:

    ```bash
    sudo apt install curl gnupg2 ca-certificates lsb-release ubuntu-keyring
    ```

    Import an official nginx signing key so apt could verify the packages authenticity. Fetch the key:

    ```bash
    curl https://nginx.org/keys/nginx_signing.key | gpg --dearmor \
        | sudo tee /usr/share/keyrings/nginx-archive-keyring.gpg >/dev/null
    ```

    Verify that the downloaded file contains the proper key:

    ```bash
    gpg --dry-run --quiet --no-keyring --import --import-options import-show /usr/share/keyrings/nginx-archive-keyring.gpg
    ```

    To set up the apt repository for stable nginx packages, run the following command:

    ```bash
    echo "deb [signed-by=/usr/share/keyrings/nginx-archive-keyring.gpg] \
    http://nginx.org/packages/ubuntu `lsb_release -cs` nginx" \
        | sudo tee /etc/apt/sources.list.d/nginx.list
    ```

    Set up repository pinning to prefer our packages over distribution-provided ones:

    ```bash
    echo -e "Package: *\nPin: origin nginx.org\nPin: release o=nginx\nPin-Priority: 900\n" \
        | sudo tee /etc/apt/preferences.d/99nginx
    ```

    To install nginx, run the following commands:

    ```bash
    sudo apt update
    sudo apt install nginx
    ```

    **Note:** Refer to know more about nginx installation [here](https://nginx.org/en/linux_packages.html#Ubuntu).
*   Run this to delete default server.

    ```bash
    sudo rm /etc/nginx/sites-enabled/default
    ```
*   Set client\_max\_body\_size to 50m on /etc/nginx/nginx.conf.

    ```nginx
    client_max_body_size 50m;
    ```
*   Find the list of headers to add in `/etc/nginx/nginx.conf` to enhance the security of environments.\
    Add the following headers under **Basic Settings** on nginx.conf.

    ```bash
    server_tokens off;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    limit_req_zone $binary_remote_addr zone=explore:10m rate=100r/s;
    add_header X-Content-Type-Options "nosniff" always;
    ```

    Add the following headers under **SSL settings** on nginx.conf.

    ```bash
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 1h;
    ssl_stapling on;
    ```
*   Restart nginx.

    ```bash
    sudo systemctl restart nginx
    ```

This is only a one-time installation. Whenever you want to add new servers for each environments on this Nginx, follow the [Install Servers to Nginx Section](nginx.md#install-servers-to-nginx).

## Install servers to Nginx

### Prerequisites

* [Create wildcard TLS certificates](../../../../../../deployment/deployment-guide/ssl-certificates-using-letsencrypt.md) (This certificate can be created each time for all the other servers you can configure later).

### Installation

{% hint style="info" %}
On AWS EC2, the number of network interfaces that can be created is limited depending on the node type. For example on `t3a.small` node, the maximum number of network interfaces is 2. Refer to [EC2 Network Specifications](https://docs.aws.amazon.com/ec2/latest/instancetypes/gp.html#gp_network) for more info.
{% endhint %}

* Once nginx server is installed, it will create `sites-enabled` and `sites-available` directories inside /etc/nginx directory.
* Navigate to `/etc/nginx/sites-available` directory and create a file called `<sandbox name>.conf` (Example: `prod-openg2p.conf`) by using [kubernetes/nginx/sites.sample.conf ](https://github.com/OpenG2P/openg2p-deployment/blob/main/kubernetes/nginx/server.sample.conf)file as a template.
* Set `session_id` ,`rate limiting` directive's under location block in each server conf file if needed.

```bash
{
        location / {
            limit_req           zone=<sandbox_name>;
            proxy_cookie_flags  session_id samesite=lax secure;
            ...
}
```

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

If you want to keep your environment private and access it only through WireGuard VPN, then map **only the private IP address of your nginx node** to your domains instead of the public IP.

{% hint style="info" %}
To make your environment publicly accessible, ensure that a public DNS is configured. Then, map the nginx node’s public IP address to the appropriate domain names for both public and private DNS entries.
{% endhint %}
