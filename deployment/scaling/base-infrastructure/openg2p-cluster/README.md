---
description: Guide to create Kubernetes cluster for OpenG2P modules
---

# OpenG2P Cluster

As depicted in the [deployment architecture](../../../), all OpenG2P modules reside on a Kubernetes cluster.  The following installations are required:

1. [Kubernetes cluster](cluster-setup/)
2. [Prometheus & Grafana](prometheus-and-grafana.md)
3. [Fluentd & OpenSearch ](fluentd-and-opensearch/)
4. OpenG2P modules
   1. Install [SocialRegistry](https://docs.openg2p.org/social-registry/deployment) Module
   2. Install [PBMS](https://docs.openg2p.org/pbms/deployment) Module
   3. Install [SPAR](https://docs.openg2p.org/spar/deployment) Module
   4. Install [G2P Bridge](https://docs.openg2p.org/g2p-bridge/deployment#installation-using-rancher-ui) Module
   5. Install [OpenG2P Landing Page](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster/landing-page-for-openg2p)
