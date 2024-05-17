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

The resource requirements pertain to the provisioning of resources for Kubernetes-based infrastructure required to house OpenG2P modules.&#x20;

## Virtual machines (VMs)

### For sandbox&#x20;

<table><thead><tr><th width="150">Purpose</th><th width="212" align="center">Configuration</th><th width="79" align="center">VMs</th><th>Notes</th></tr></thead><tbody><tr><td><a href="base-infrastructure/rancher.md">Rancher cluster</a></td><td align="center">4vCPU/16 GB RAM/128 GB storage</td><td align="center">1</td><td>For high-availability<a href="https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade#high-availability-kubernetes-install-with-the-helm-cli"> 3 nodes are recommended</a></td></tr><tr><td><a href="base-infrastructure/openg2p-cluster/">OpenG2P cluster</a></td><td align="center">8 vCPU/32 GB RAM/128 GB storage</td><td align="center"><p></p><p>2</p></td><td>Start with 2 nodes and if required add another one</td></tr><tr><td><a href="base-infrastructure/wireguard-bastion/">Wireguard Bastion</a></td><td align="center">2vCPU/4 GB RAM/32 GB storage</td><td align="center">1</td><td></td></tr><tr><td><a href="base-infrastructure/nfs-server.md">NFS Server</a></td><td align="center">2 vCPU/8 GB RAM/128 GB storage</td><td align="center">1</td><td>Used for persistence both Rancher and OpenG2P clusters. The actual size of storage will depend on usage.</td></tr></tbody></table>

OS for all nodes:  **Ubuntu 22.04 Server**

{% hint style="info" %}
To save costs, on AWS recommended EC2 instance type for cluster nodes is **t3a.\***&#x20;
{% endhint %}

### For pilot and limited rollout

<table><thead><tr><th width="139">Purpose</th><th width="262">Configuration</th><th width="79" align="center">VMs</th><th width="373">Notes</th></tr></thead><tbody><tr><td><a href="base-infrastructure/openg2p-cluster/cluster-setup/">Kubernetes </a>cluster</td><td>8 vCPU/32 GB RAM/128 GB storage</td><td align="center">3</td><td>Required for control-plane, master, etcd, work loads of Kubernetes cluster</td></tr><tr><td><a href="base-infrastructure/wireguard-bastion/">Wireguard Bastion</a></td><td>2 vCPU/4 GB RAM/32 GB storage</td><td align="center">1</td><td>One VM for Wireguard is sufficient for all the environments/setups in your network. This is used to facilitate VPN access to the pilot environments</td></tr><tr><td><a href="base-infrastructure/rancher.md">Rancher cluster</a></td><td>2 vCPU/8 GB RAM/128 GB storage</td><td align="center">3</td><td>For high-availability<a href="https://ranchermanager.docs.rancher.com/getting-started/installation-and-upgrade#high-availability-kubernetes-install-with-the-helm-cli"> 3 nodes are recommended</a>. This cluster also holds organisation wide Keycloak.</td></tr><tr><td>Nginx load balancer</td><td>4 vCPU/16 GB RAM/64 GB storage</td><td align="center">1</td><td>This VM is not required if using a Cloud Provider - the LB of Cloud Provider is recommended in that case</td></tr><tr><td><a href="base-infrastructure/nfs-server.md">NFS Server</a></td><td>4 vCPU/16 GB RAM/500 GB storage</td><td align="center">1</td><td>Used for persistence both Rancher and OpenG2P clusters. The actual size of storage will depend on usage.</td></tr></tbody></table>

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

