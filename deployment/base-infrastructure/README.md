---
description: Deployment Base Infrastructure
---

# Base Infrastructure

The base infrastructure consists of the components listed below.  Individual module deployment instructions may be found in the documentation of respective modules.  The components need to be installed in the sequence given below.  An "environment" is a setup for a specific purpose like development, QA, staging, production etc.  Some of the components may be installed only once.&#x20;

<table><thead><tr><th>Base Infrastructure Components</th><th width="196" align="center">Minimum number of Instances</th><th>Notes</th></tr></thead><tbody><tr><td><a href="wireguard-bastion/">Wireguard bastion</a></td><td align="center">1</td><td>More may be required based on separate channels for users.</td></tr><tr><td><a href="nfs-server.md">NFS server</a></td><td align="center">1</td><td>Organisation wide NFS server. </td></tr><tr><td><a href="rancher.md">Rancher cluster </a></td><td align="center">1</td><td><strong>K8s cluster</strong> with Rancher and Keycloak for managing multiple environments. </td></tr><tr><td><a href="openg2p-cluster/">OpenG2P cluster</a></td><td align="center">1</td><td><strong>K8s cluster</strong> for OpenG2P modules</td></tr><tr><td><a href="load-balancer/">Load Balancer</a></td><td align="center">2</td><td>One for public and one for private access. However, more LBs may be created for separate <a href="../deployment-guide/security/access-channel.md">access channels</a>.</td></tr></tbody></table>
