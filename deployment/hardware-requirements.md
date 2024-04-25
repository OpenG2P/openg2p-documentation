---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Hardware Requirements

The hardware requirements pertain to the Kubernetes-based infrastructure required to house OpenG2P modules. The number of VMs and configuration are subjected to scaled-down if only specific modules are being installed.

## For sandbox&#x20;

<table><thead><tr><th width="150">Purpose</th><th width="212" align="center">Configuration</th><th width="79" align="center">VMs</th><th>Notes</th></tr></thead><tbody><tr><td><a href="base-infrastructure/rancher.md">Rancher cluster</a></td><td align="center">4vCPU/16 GB RAM/64 GB storage</td><td align="center">1</td><td>For HA at least 2 nodes are recommended</td></tr><tr><td><a href="base-infrastructure/cluster-setup.md">Kubernetes cluster</a></td><td align="center">8 vCPU/32 GB RAM/128 GB storage</td><td align="center"><p></p><p>2</p></td><td>Start with 2 nodes and if required add another one</td></tr><tr><td><a href="base-infrastructure/wireguard-bastion/">Wireguard Bastion</a></td><td align="center">4vCPU/16 GB RAM/64 GB storage</td><td align="center">1</td><td></td></tr></tbody></table>

OS for all nodes:  **Ubuntu 20.04 Server**

{% hint style="info" %}
To save costs, on AWS recommended EC2 instance type for cluster nodes is **t3a.2xlarge.**&#x20;
{% endhint %}

## For pilot and limited rollout

<table><thead><tr><th width="139">Purpose</th><th width="262">Configuration</th><th width="79" align="center">VMs</th><th width="373">Notes</th></tr></thead><tbody><tr><td><a href="base-infrastructure/cluster-setup.md">Kubernetes nodes</a></td><td>8 vCPU/32 GB RAM/128 GB storage</td><td align="center">3</td><td>Required for master, etc, work loads of Kubernetes cluster</td></tr><tr><td><a href="base-infrastructure/wireguard-bastion/">Wireguard Bastion</a></td><td>4 vCPU/8 GB RAM/64 GB storage</td><td align="center">1</td><td>One VM for Wireguard is sufficient for all the environments/setups in your network. This is used to facilitate VPN access to the pilot environments</td></tr><tr><td><a href="base-infrastructure/rancher.md">Rancher cluster</a></td><td>4 vCPU/16 GB RAM/128 GB storage</td><td align="center">1</td><td>For HA at least 2 nodes are recommended</td></tr><tr><td>Nginx load balancer</td><td>4 vCPU/16 GB RAM/64 GB storage</td><td align="center">1</td><td>This VM is not required if using a Cloud Provider - the LB of Cloud Provider is recommended in that case</td></tr><tr><td><a href="base-infrastructure/nfs-server.md">NFS Server</a></td><td>4 vCPU/16 GB RAM/500 GB storage</td><td align="center">1</td><td>Used for persistence of all components in the K8s cluster. The actual size of storage required will vary from setup to setup. </td></tr></tbody></table>

OS for all nodes:  **Ubuntu 20.04 Server**

## Networking requirements

* All the machines in the same network
* Public IP assigned to the Wireguard machine

## DNS requirements

The following domain names and mappings will be required. Examples:

| Requirement Description                                                        | Domain Name (examples)                                                                                                                                       | Mapped to                                                                                                                                                      |
| ------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Top level domain that points to the sandbox.                                   | <p></p><ul><li>openg2p.<em>&#x3C;your domain></em></li><li>uat.<em>&#x3C;your domain></em></li><li>pilot.openg2p.<em>&#x3C;your domain></em></li></ul>       | "A" Record mapped to Load Balancer IP (For sandox, where loadbalancer is not present, this can be mapped directly nodes of the K8s Cluster, at least 3 nodes). |
| Wildcard subdomain for accessing individual components within OpenG2P sandbox. | <p></p><ul><li>*.openg2p.<em>&#x3C;your domain></em></li><li>*.uat.<em>&#x3C;your domain></em></li><li>*.pilot.openg2p.<em>&#x3C;your domain></em></li></ul> | "CNAME" Record mapped to the domain of the above "A" record. (This is a wildcard DNS mapping)                                                                  |

## Certificate requirements

One wildcard certificate is required at least, depending on the above domain names used. This can also be generated using Letsencrypt.  See guide [here](deployment-guide/ssl-certificates-using-letsencrypt.md).

