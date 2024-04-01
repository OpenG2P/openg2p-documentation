---
description: Deployment Base Infrastructure
---

# Base Infrastructure

The base infrastructure consists of the components listed below.  Individual module deployment instructions may be found in the documentation of respective modules. The components need to be installed in the sequence given below.&#x20;

| Base Infrastructure Components          | Comments                                                                                                               |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| [Wireguard bastion](wireguard-bastion/) | Only one per all the environments                                                                                      |
| [Rancher](rancher.md)                   | Only one per all the environments                                                                                      |
| [NFS Server](nfs-server.md)             | One for each environment like sandbox, pilot, staging, production                                                      |
| [Kuberenetes cluster](cluster-setup.md) | One for each environment                                                                                               |
| [Loadbalancer](loadbalancer.md)         | One for each environment. For non cloud-native Kubernetes clusters either create a VM with Nginx or create a cloud LB. |

