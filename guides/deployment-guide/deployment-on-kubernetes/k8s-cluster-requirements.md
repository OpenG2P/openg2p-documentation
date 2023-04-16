---
description: Work in progress
---

# K8s Cluster Requirements

## Hardware requirements

### For sandbox setups

| Purpose       | vCPUs |  RAM  | Storage (SSD) | Number of Virtual Machines\* | Preferred Operating System |
| ------------- | :---: | :---: | :-----------: | ---------------------------: | -------------------------- |
| Cluster nodes |   8   | 32 GB |     128 GB    |                            3 | Ubuntu Server 20.04        |
| Wireguard     |   4   | 16 GB |     64 GB     |                            1 | Ubuntu Server 20.04        |

### For staging setups

| Purpose       | vCPUs |  RAM  | Storage (SSD) | Number of Virtual Machines\* | Preferred Operating System |
| ------------- | :---: | :---: | :-----------: | ---------------------------: | -------------------------- |
| Cluster nodes |   8   | 32 GB |     128 GB    |                            3 | Ubuntu Server 20.04        |
| Wireguard     |   4   | 16 GB |     64 GB     |                            1 | Ubuntu Server 20.04        |
| Backup        |   4   | 16 GB |     512 GB    |                            1 | Ubuntu Server 20.04        |

### For production setups

TBD

## Networking requirements

* All the machines in the same network.
* Public IP assigned to the Wireguard machine.

## DNS requirements

The following domain names and mappings will be required. (The following is only a list sample hostnames).

| Domain                 | Mapped to                                                                   |
| ---------------------- | --------------------------------------------------------------------------- |
| openg2p.sandbox.net    | "A" Record mapped to at least 3 nodes of the K8s Cluster.                   |
| \*.openg2p.sandbox.net | "CNAME" Record mapped to the above domain. (This is a wildcard DNS mapping) |

## Certificate requirements

One wildcard certificate is required at least, depending on the above domain names used. This can also be generated using letsencrypt.
