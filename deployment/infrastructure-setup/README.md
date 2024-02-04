# Infrastructure Setup

| Infra                                  | Comments                                                                                                               |
| -------------------------------------- | ---------------------------------------------------------------------------------------------------------------------- |
| [Wireguard](wireguard-server-setup.md) | Only one per all the environments                                                                                      |
| [Rancher](rancher.md)                  | Only one per all the environments                                                                                      |
| [NFS Server](nfs-server.md)            | One for each environment like sandbox, pilot, staging, production                                                      |
| [OpenG2P K8s Cluster](k8s-cluster.md)  | One for each environment                                                                                               |
| [Loadbalancer](loadbalancer-setup.md)  | One for each environment. For non cloud-native Kubernetes clusters either create a VM with Nginx or create a cloud LB. |
