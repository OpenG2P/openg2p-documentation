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

# Private Access Channel

A Private Access Channel (PAC) is a tuple of Wireguard, Load Balancer, and Ingress gateway.  A channel provides **access to resources** of the infrastructure and this can be controlled. The users assigned to the Wireguard server determine the group of users with access to these channels. All users with access to a Wireguard server have access to all channels to which the Wireguard server is connected. The [deployment architecture](../#deployment-architecture-v4) depicts a high-level view of the PACs.  A zoomed-in view is presented below.

{% embed url="https://miro.com/app/board/uXjVK2_5XEQ=/?share_link_id=115753732631" %}

Multiple Wireguard servers (bastions) can run on a single Virtual Machine (VM).  Similarly, multiple Nginx servers (vhosts) can run on a single Nginx instance.  Each network interface on Nginx has a unique IP. Each Nginx vhost forwards traffic to an Istio Ingress gateway server which further routes traffic to Kubernetes resources. Multiple gateways can run on a single Istio Ingress gateway server.

In the above configuration, User Group 1 has access to both Ingress gateway servers while User Group 2 can only access resources associated with Ingress gateway server 2.

