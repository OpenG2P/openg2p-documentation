---
description: Deployment Base Infrastructure
---

# Base Infrastructure

The base infrastructure consists of the components listed below.  Individual module deployment instructions may be found in the documentation of respective modules.  The components need to be installed in the sequence given below.  An "environment" is a setup for a specific purpose like development, QA, staging, production etc.  Some of the components may be installed only once.&#x20;

<table><thead><tr><th>Base Infrastructure Components</th><th width="196" align="center">Number of Instances</th><th>Comments</th></tr></thead><tbody><tr><td><a href="wireguard-bastion/">Wireguard bastion</a></td><td align="center">1</td><td>Shared with all environments *</td></tr><tr><td><a href="rancher.md">Rancher</a></td><td align="center">1</td><td>For managing multiple environments *</td></tr><tr><td><a href="nfs-server.md">NFS server</a></td><td align="center">N</td><td>One for each environment like dev, QA, staging, production </td></tr><tr><td><a href="cluster-setup.md">Kuberenetes cluster</a></td><td align="center">N</td><td>One for each environment</td></tr><tr><td><a href="load-balancer.md">Load Balancer</a></td><td align="center">N</td><td>For non cloud-native Kubernetes clusters either create a VM with Nginx or create a cloud LB.</td></tr><tr><td>Prometheus &#x26; Gafana</td><td align="center">N</td><td>One for each environment</td></tr></tbody></table>

{% hint style="info" %}
\* While only one instance of Wireguard and Rancher is sufficient for all environments, for greater security and access control multiple instances may be installed and configured.
{% endhint %}
