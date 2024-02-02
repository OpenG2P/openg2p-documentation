# K8s Cluster Requirements

## Hardware requirements

### For Rancher&#x20;

Only one Rancher set up is required for managing multiple Kubernetes clusters.



### For sandbox&#x20;

<table><thead><tr><th width="136">Purpose</th><th width="137" align="center">vCPUs</th><th align="center">RAM</th><th align="center">Storage (SSD)</th><th width="80" align="right">VMs</th><th>OS</th></tr></thead><tbody><tr><td>Cluster nodes</td><td align="center">8</td><td align="center">32 GB</td><td align="center">128 GB</td><td align="right">3</td><td>Ubuntu Server 20.04</td></tr><tr><td>Wireguard</td><td align="center">4</td><td align="center">16 GB</td><td align="center">64 GB</td><td align="right">1</td><td>Ubuntu Server 20.04</td></tr></tbody></table>

### For pilot

<table><thead><tr><th width="136">Purpose</th><th align="center">vCPUs</th><th align="center">RAM</th><th align="center">Storage (SSD)</th><th align="right">Number of Virtual Machines*</th><th>Preferred Operating System</th></tr></thead><tbody><tr><td>Cluster nodes</td><td align="center">8</td><td align="center">32 GB</td><td align="center">128 GB</td><td align="right">3</td><td>Ubuntu Server 20.04</td></tr><tr><td>Wireguard</td><td align="center">4</td><td align="center">16 GB</td><td align="center">64 GB</td><td align="right">1</td><td>Ubuntu Server 20.04</td></tr><tr><td>NFS</td><td align="center">4</td><td align="center">16 GB</td><td align="center">1 TB GB*</td><td align="right">1</td><td>Ubuntu Server 20.04</td></tr></tbody></table>

\\\* As per estimate in <>

## Networking requirements

* All the machines in the same network.
* Public IP assigned to the Wireguard machine.

## DNS requirements

The following domain names and mappings will be required. Examples:

| Domain Name (examples)                                                                                                                               | Mapped to                                                                        |
| ---------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| <ul><li>openg2p.<em>&#x3C;your domain></em></li><li>uat.<em>&#x3C;your domain></em></li><li>pilot.openg2p.<em>&#x3C;your domain></em></li></ul>      | "A" Record mapped to Load Balancer IP **or** at least 3 nodes of the K8s Cluster |
| <ul><li><em>. openg2p.&#x3C;your domain></em></li><li>.uat.<em>&#x3C;your domain></em></li><li>*.pilot.openg2p.<em>&#x3C;your domain></em></li></ul> | "CNAME" Record mapped to the above domain. (This is a wildcard DNS mapping)      |

## Certificate requirements

One wildcard certificate is required at least, depending on the above domain names used. This can also be generated using letsencrypt.
