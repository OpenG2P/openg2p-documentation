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

A Private Access Channel (PAC) is a tuple of Wireguard, Load Balancer, and Ingress gateway server.  A channel provides **access to resources** of the infrastructure and this can be controlled. The users assigned to the Wireguard server determine the group of users with access to these channels. All users with access to a Wireguard server have access to all channels to which the Wireguard server is connected. The [deployment architecture](../#deployment-architecture-v4) depicts a high-level view of the PACs.  A zoomed-in view is presented below.

{% embed url="https://miro.com/app/board/uXjVK2_5XEQ=/?share_link_id=115753732631" %}

Multiple Wireguard servers (bastions) can run on a single Virtual Machine (VM).  Similarly, multiple Nginx servers (vhosts) can run on a single Nginx instance.  Each network interface on Nginx has a unique IP. Each Nginx vhost forwards traffic to an Istio Ingress gateway server which further routes traffic to Kubernetes resources.  On the Istio Ingress gateway server,  gateways (or filters) are defined for each wildcard domain specifying the rule to forward traffic to the respective namespace on the cluster. See the example above.

In the above example, Users RG1 can access only RG1 domains.

