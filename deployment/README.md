# Deployment

OpenG2P offers production-grade deployment scripts and utilities and is based on reputed open-source components like Kubernetes, Rancher etc. The deployment infra may be used for sandbox, pilot or rollout. All components are available as Dockers and Kubernetes is used as the orchestration platform. The deployment architecture is depicted below



{% embed url="https://miro.com/app/board/uXjVN5LsWDw=/?share_link_id=356935336772" %}

Rancher is used to manage multiple OpenG2P clusters. Rancher itself is installed on a Kubernetes cluster with redundancy as it is a critical gateway to manage the clusters.  The clusters may be directly managed by the command line utility `kubectl` as well.
