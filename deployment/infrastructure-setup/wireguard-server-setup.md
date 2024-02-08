# Wireguard Server Setup

## Introduction

Wireguard is the recommended VPN to get private channel access to your OpenG2P clusters and resources. Wireguard is a fast secure & open-source VPN, with P2P traffic encryption.

The document talks about setting up a Wireguard bastion host (Wireguard server) to enable a private channel to the Kubernetes cluster.

## Prerequisites

* One Virtual machine running on the same network as the rest of the nodes, and has access to them. For recommended configuration of the VM refer to [Cluster Requirements](../../guides/deployment-guide/deployment-on-kubernetes/k8s-infrastructure-setup/k8s-cluster-requirements.md).
* Docker installed on the VM.

## Installation

* Clone the [openg2p-deployment](https://github.com/OpenG2P/openg2p-deployment) repo and navigate to the [kubernetes/wireguard](https://github.com/OpenG2P/openg2p-deployment/tree/main/kubernetes/wireguard) directory.
*   Run this with root privileges:

    ```bash
    ./wg.sh <name for this wireguard instance> <client ips subnet mask> <port> <no of peers> <subnet mask of the cluster nodes & lbs>
    ```
*   For Example:

    ```bash
    ./wg.sh wireguard 10.15.0.0/16 51820 200 172.16.0.0/24
    ```
* Make sure to edit the firewall rules of this VM to enable incoming traffic on the above UDP port (Default 51820) and disable incoming traffic on all other ports (excluding SSH).
