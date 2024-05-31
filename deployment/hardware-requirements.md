---
description: Various resources required for deployment
layout:
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Resource Requirements

The resource requirements pertain to the provisioning of resources for Kubernetes-based infrastructure required to house OpenG2P modules. See [deployment architecture.](./)

## Virtual machines (VMs)

The table below specifies typical requirements for V4 deployment architecture. These configurations are recommended both for internal organisation deployment as well pilot/production/rollouts.&#x20;

For high availability and greater resilience refer to [production guide](production.md).

<table><thead><tr><th width="150">Purpose</th><th width="239" align="center">Compute/Memory/Storage</th><th>Notes</th></tr></thead><tbody><tr><td><a href="base-infrastructure/wireguard-bastion/">Wireguard Bastion</a></td><td align="center">2vCPU/4 GB RAM/32 GB storage</td><td>Multiple Wireguard servers can run on a single node</td></tr><tr><td><a href="base-infrastructure/nfs-server.md">NFS Server</a></td><td align="center">2 vCPU/8 GB RAM/128 GB storage</td><td>Used for persistence both Rancher and OpenG2P clusters. <strong>The actual size of storage will depend on usage.</strong></td></tr><tr><td><a href="base-infrastructure/rancher.md">Rancher cluster</a></td><td align="center">4vCPU/16 GB RAM/128 GB storage</td><td>For high-availability<a href="https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade#high-availability-kubernetes-install-with-the-helm-cli"> </a>refer to <a href="production.md">production guide.</a></td></tr><tr><td><a href="base-infrastructure/openg2p-cluster/">OpenG2P cluster</a></td><td align="center">16 vCPU/64 GB RAM/256 GB storage</td><td><p><strong>Minimum requirement</strong>. The requirement may increase based on number of modules installed and need for higher resilience. Refer to the <a href="production.md">production guide.</a></p><p>You may provision these resources on more than one VMs with minimum configuration of each VM being 8 vCPU/32 GB RAM/128 GB storage. </p></td></tr><tr><td><a href="base-infrastructure/load-balancer/nginx.md">Nginx</a></td><td align="center">2 vCPU/8 GB RAM/64 GB</td><td>Multiple Nginx servers can run on a single node.</td></tr></tbody></table>

OS for all nodes:  **Ubuntu 22.04 Server**

## Networking&#x20;

* All the machines in the same network
* Public IP assigned to the Wireguard machine

## DNS&#x20;

The following domain names and mappings will be required.  The suggested domain name convention is as follows

\<module>.\<environment>.\<organisation>.\<tld>

Example:&#x20;

* spar.dev.openg2p.org
* socialregistry.uat.openg2p.org

### Domain mapping

| Requirement Description      | Domain Name (examples)                                                                      | Mapped to                                                                                                                                            |
| ---------------------------- | ------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| Domain mapping to sandbox    | <ul><li>dev.openg2p.net</li><li>uat.openg2p.net</li><li>staging.openg2p.org</li></ul>       | "A" Record mapped to Load Balancer IP (For sandbox, where LB is not used, this can be mapped directly tonodes of the K8s cluster, at least 3 nodes). |
| Wild card mapping to modules | <ul><li>*.dev.openg2p.net</li><li>*.uat.openg2p.net</li><li>*.staging.openg2p.org</li></ul> | "CNAME" Record mapped to the domain of the above "A" record. (This is a wildcard DNS mapping)                                                        |

The domain name mapping needs to be done on your domain service provider.  For example on AWS this is configured on Route 53.

## Certificates

One wildcard certificate is required at least, depending on the above domain names used. This can also be generated using Letsencrypt.  See guide [here](deployment-guide/ssl-certificates-using-letsencrypt.md).

