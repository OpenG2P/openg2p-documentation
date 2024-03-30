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

# Infrastructure

Following components need to be installed in the sequence given below to set up the infrastructure that houses OpenG2P modules.

| Infra                                   | Comments                                                                                                               |
| --------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| [Wireguard](wireguard-bastion/)         | Only one per all the environments                                                                                      |
| [Rancher](rancher.md)                   | Only one per all the environments                                                                                      |
| [NFS Server](nfs-server.md)             | One for each environment like sandbox, pilot, staging, production                                                      |
| [OpenG2P K8s Cluster](cluster-setup.md) | One for each environment                                                                                               |
| [Loadbalancer](loadbalancer.md)         | One for each environment. For non cloud-native Kubernetes clusters either create a VM with Nginx or create a cloud LB. |
