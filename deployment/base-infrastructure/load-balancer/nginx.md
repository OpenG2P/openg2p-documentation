---
description: Installation of Nginx load balancer
---

# Nginx

Nginx is used as both reverse proxy and load balancing for on-prem deployments.&#x20;

Install Nginx and related components as follows:

1. [Install Nginx](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/nginx)
2. [Create wildcard TLS certificates](../../deployment-guide/ssl-certificates-using-letsencrypt.md) (required to terminate HTTPS connects at Nginx)
3. Map the hostnames to Nginx IPs on your DNS service (Route53 on AWS)

