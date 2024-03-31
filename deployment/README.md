---
description: OpenG2P Deployment
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

# Deployment

OpenG2P offers production-grade deployment scripts and utilities based on reputed open-source components like Kubernetes, Rancher etc. The deployment infra may be used for sandbox, pilot or full scale rollout. All components are available as Dockers and Kubernetes is used as the orchestration platform. The deployment architecture is depicted below

{% embed url="https://miro.com/app/board/uXjVN5LsWDw=/?share_link_id=356935336772" %}

Rancher is used to manage multiple Kubernetes clusters. Rancher may be installed on a separate node with Docker or a Kubernetes cluster (preferable) with redundancy as it is a critical gateway to manage the clusters. &#x20;

The base infrastructure consists of the components listed below.  Individual module deployment instructions may be found in the documentation of respective modules.

The following components need to be installed in the sequence given below to set up the base infrastructure that houses OpenG2P modules.

| Infra Components                                            | Comments                                                                                                               |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| [Wireguard bastion](base-infrastructure/wireguard-bastion/) | Only one per all the environments                                                                                      |
| [Rancher](base-infrastructure/rancher.md)                   | Only one per all the environments                                                                                      |
| [NFS Server](base-infrastructure/nfs-server.md)             | One for each environment like sandbox, pilot, staging, production                                                      |
| [Kuberenetes cluster](base-infrastructure/cluster-setup.md) | One for each environment                                                                                               |
| [Loadbalancer](base-infrastructure/loadbalancer.md)         | One for each environment. For non cloud-native Kubernetes clusters either create a VM with Nginx or create a cloud LB. |
