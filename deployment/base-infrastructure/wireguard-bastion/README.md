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

The document talks about setting up a **Wireguard bastion host** to enable a private channel to the Kubernetes cluster.

TBD

Multiple Wireguard servers will be required (all on the same node/VM). Each server is used to give access to Load balancer(s) for a particular set of users. For the rest of the documentation, we will call this a "channel".

It is recommended to set up at least two channels, one for System Administrators, and one for OpenG2P Application Users (like Program Managers, Service Providers, etc). Further channels can be created based on the need.

## Prerequisites

* One virtual machine (VM) running on the same network as the rest of the nodes, and has access to them. For recommended configuration of the VM refer to [Hardware Requirements](../../hardware-requirements.md).
* Firewall rules: Allow only `22/tcp`, `51820-51830/udp` ports.
* Docker installed on the VM

## Installation

* Clone the [openg2p-deployment](https://github.com/OpenG2P/openg2p-deployment) repo and navigate to the [kubernetes/wireguard](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/wireguard) directory
*   Run this with root privileges:

    ```bash
    ./wg.sh <name for this wireguard server> <client ips subnet mask> <port> <no of peers> <subnet mask of the cluster nodes & lbs>
    ```
*   To create multiple wireguard servers, run the above script multiple times with appropriate parameters. For example:

    ```bash
    ./wg.sh wireguard_app_users 10.15.0.0/16 51820 254 172.16.0.0/24
    ./wg.sh wireguard_sys_admins 10.16.0.0/16 51821 254 172.16.0.0/24
    ```
*   Check logs of the servers and wait for all servers to finish startup. Example:

    ```bash
    docker logs -f wireguard_sys_admins
    ```

### Limit user access

* Limit each wireguard server to allow access to only the required Load Balancer/Nginx: (The following uses `wireguard_app_users` server example. Repeat this for all servers)
*   Comment out these lines in `/etc/wireguard_app_users/rules.sh` . (This allows everyone to access all IPs):

    ```bash
    iptables -A FORWARD -i wg0 -j ACCEPT
    iptables -A FORWARD -o wg0 -j ACCEPT
    ```
*   Add the following lines under the above lines in `/etc/wireguard_app_users/rules.sh` , repeat for all IPs of LB/Nginx:

    ```bash
    iptables -P FORWARD DROP

    iptables -A FORWARD -i wg0 -d <First Internal IP of LB/Nginx> -j ACCEPT
    iptables -A FORWARD -o wg0 -s <First Internal IP of LB/Nginx> -j ACCEPT

    iptables -A FORWARD -i wg0 -d <Second Internal IP of LB/Nginx> -j ACCEPT
    iptables -A FORWARD -o wg0 -s <Second Internal IP of LB/Nginx> -j ACCEPT
    ```
*   Restart the server

    ```bash
    docker restart wireguard_app_users
    ```
* Repeat the above for all the wireguard servers/channels.
* For System Admin channel, limit access to only Rancher LB/Nginx.\
  For Other Channels, limit access to the relevant LBs/Nginxs.

## Access to users

Refer to this [Wireguard Access to Users](wireguard-access-to-users.md)

## Wireguard client

To access systems behind Wireguard bastion, you need to install Wireguard client on your machine. Install the client as follows:

* [Install on Desktop](install-wireguard-client-on-machine.md)
* [Install on Android](install-wireguard-app-and-activate-tunnel.md)
