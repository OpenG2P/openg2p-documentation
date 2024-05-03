---
description: Deployment of Wireguard Bastion host
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

# Wireguard Bastion

[Wireguard](https://www.wireguard.com/) is the recommended VPN to get private channel access to your OpenG2P clusters and resources. Wireguard is a fast secure & open-source VPN, with P2P traffic encryption.

The document talks about setting up a **Wireguard bastion host** (Wireguard server) to enable a private channel to the Kubernetes cluster.

## Prerequisites

* One Virtual machine running on the same network as the rest of the nodes, and has access to them. For recommended configuration of the VM refer to [Hardware Requirements](../../hardware-requirements.md).
* Docker installed on the VM

## Installation

* Clone the [openg2p-deployment](https://github.com/OpenG2P/openg2p-deployment) repo and navigate to the [kubernetes/wireguard](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/wireguard) directory
*   Run this with root privileges:

    ```bash
    ./wg.sh <name for this wireguard instance> <client ips subnet mask> <port> <no of peers> <subnet mask of the cluster nodes & lbs>
    ```
*   For example:

    ```bash
    ./wg.sh wireguard 10.15.0.0/16 51820 200 172.16.0.0/24
    ```
* Make sure to edit the firewall rules of this VM to enable incoming traffic on the above UDP port (Default 51820) and disable incoming traffic on all other ports (excluding SSH)

## Access to users

Refer to this [Wireguard Access to Users](wireguard-access-to-users.md)

## Wireguard client

To access systems behind Wireguard bastion, you need to install Wireguard client on your machine. Install the client as follows:

* [Install on Desktop](install-wireguard-client-on-machine.md)
* [Install on Android](install-wireguard-app-and-activate-tunnel.md)
