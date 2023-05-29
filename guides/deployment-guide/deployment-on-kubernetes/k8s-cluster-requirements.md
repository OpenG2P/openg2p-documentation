---
description: Work in progress
---

# K8s Cluster Requirements

## Hardware requirements

### For sandbox setups

<table><thead><tr><th width="136">Purpose</th><th align="center">vCPUs</th><th align="center">RAM</th><th align="center">Storage (SSD)</th><th align="right">Number of Virtual Machines*</th><th>Preferred Operating System</th></tr></thead><tbody><tr><td>Cluster nodes</td><td align="center">8</td><td align="center">32 GB</td><td align="center">128 GB</td><td align="right">3</td><td>Ubuntu Server 20.04</td></tr><tr><td>Wireguard</td><td align="center">4</td><td align="center">16 GB</td><td align="center">64 GB</td><td align="right">1</td><td>Ubuntu Server 20.04</td></tr></tbody></table>

### For staging setups

<table><thead><tr><th width="136">Purpose</th><th align="center">vCPUs</th><th align="center">RAM</th><th align="center">Storage (SSD)</th><th align="right">Number of Virtual Machines*</th><th>Preferred Operating System</th></tr></thead><tbody><tr><td>Cluster nodes</td><td align="center">8</td><td align="center">32 GB</td><td align="center">128 GB</td><td align="right">3</td><td>Ubuntu Server 20.04</td></tr><tr><td>Wireguard</td><td align="center">4</td><td align="center">16 GB</td><td align="center">64 GB</td><td align="right">1</td><td>Ubuntu Server 20.04</td></tr><tr><td>Backup</td><td align="center">4</td><td align="center">16 GB</td><td align="center">512 GB</td><td align="right">1</td><td>Ubuntu Server 20.04</td></tr></tbody></table>

### For production setups

TBD

## Networking requirements

* All the machines in the same network.
* Public IP assigned to the Wireguard machine.

## DNS requirements

The following domain names and mappings will be required. Examples:

| Example Domains                                                                                                                                               | Mapped to                                                                    |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- |
| <ul><li>openg2p.<em>&#x3C;your domain></em></li><li>uat.<em>&#x3C;your domain></em></li><li>pilot.openg2p.<em>&#x3C;your domain></em></li></ul>               | "A" Record mapped to at least 3 nodes of the K8s Cluster or load balancer IP |
| <p></p><ul><li>*. openg2p.<em>&#x3C;your domain></em></li><li>*.uat.<em>&#x3C;your domain></em></li><li>*.pilot.openg2p.<em>&#x3C;your domain></em></li></ul> | "CNAME" Record mapped to the above domain. (This is a wildcard DNS mapping)  |

## Certificate requirements

One wildcard certificate is required at least, depending on the above domain names used. This can also be generated using letsencrypt.
