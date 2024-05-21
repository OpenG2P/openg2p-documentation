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

# Load Balancer

Load balancing (LB) is essential to ensure high availability, scalability, and reliability of applications running within the cluster. It involves distributing incoming network traffic across multiple pods or nodes to optimise resource utilisation and prevent any single point of failure. LB also isolates the internal network from the external world avoiding users directly accessing the nodes of the Kubernetes cluster. For on-prem installations, Nginx may be used.
