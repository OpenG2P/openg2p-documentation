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

Load balancing in Kubernetes (K8s) is essential to ensure high availability, scalability, and reliability of applications running within the cluster. It involves distributing incoming network traffic across multiple pods or nodes to optimise resource utilisation and prevent any single point of failure. Load balancer may be installed cloud native (like network load balancer of AWS) or on on-prem using Istio or Nginx.

* [AWS cloud native load balancer](aws.md)
* [Istio load balancer](istio.md)
* [Nginx as load balancer](nginx.md)

