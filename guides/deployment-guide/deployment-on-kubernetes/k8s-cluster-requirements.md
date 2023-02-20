---
description: Work in progress
---

# Requirements

The requirements to setup a Kubernetes Cluster, on which OpenG2P can be deployed, are given below.

## Hardware requirements

| Purpose       | vCPUs |  RAM  | Storage (SSD) | Number of VMs\* | Preferred Operating System |
| ------------- | :---: | :---: | :-----------: | --------------: | -------------------------- |
| Cluster nodes |   12  | 32 GB |     128 GB    |               3 | Ubuntu Server 22.04        |

\* Virtual Machines

## Networking configuration

WIP

## DNS requirements

The following domain names and mappings will be required. (The following is only a list sample hostnames).

| Domain                 | Mapped to                                                                   |
| ---------------------- | --------------------------------------------------------------------------- |
| openg2p.sandbox.net    | "A" Record mapped to atleast 3 nodes of the K8s Cluster.                    |
| \*.openg2p.sandbox.net | "CNAME" Record mapped to the above domain. (This is a wildcard DNS mapping) |

## Certificate requirements

One wildcard certificate is required atleast, depending on the above domain names used. This can also be generated using letsencrypt.
