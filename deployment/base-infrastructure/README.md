---
description: Deployment Base Infrastructure
---

# Base Infrastructure

The base infrastructure consists of the components listed below.  Individual module deployment instructions may be found in the documentation of respective modules.  The components need to be installed in the sequence given below.  An "environment" is a setup for a specific purpose like development, QA, staging, production etc.  Some of the components may be installed only once.&#x20;

<table><thead><tr><th>Base Infrastructure Components</th><th width="196" align="center">Minimum number of Instances</th><th>Comments</th></tr></thead><tbody><tr><td><a href="wireguard-bastion/">Wireguard bastion</a></td><td align="center">1</td><td>More may be required based on separate channels for users.</td></tr><tr><td><a href="rancher.md">Rancher &#x26; Keycloak</a></td><td align="center">1</td><td>For managing multiple environments. One Keycloak for SSO across organisation </td></tr><tr><td><a href="nfs-server.md">NFS server</a></td><td align="center">1</td><td>Organisation wide NFS server. </td></tr><tr><td><a href="cluster-setup/">Kuberenetes cluster</a></td><td align="center">2</td><td>For Rancher and OpenG2P modules</td></tr><tr><td><a href="load-balancer/">Load Balancer</a></td><td align="center">N</td><td>For non cloud-native Kubernetes clusters either create a VM with Nginx or create a cloud Load Balancer.</td></tr><tr><td><a href="prometheus-and-grafana.md">Prometheus &#x26; Gafana</a></td><td align="center">1</td><td>One for OpenG2P cluster</td></tr></tbody></table>
