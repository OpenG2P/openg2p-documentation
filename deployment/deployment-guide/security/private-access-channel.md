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

A Private Access Channel (PAC) is a tuple of Wireguard, Load Balancer, and Ingress gateway.  A channel provides **access to resources** of the infrastructure and this can be controlled. The group of users who have access to these channels is determined by the users assigned to Wireguard server. All users who have access to a Wireguard server have access to all channels that the Wireguard server is connected to.   For example, in the diagram below Application Users have access to both OpenG2P Cluster and Keycloak.



{% embed url="https://miro.com/app/board/uXjVN5LsWDw=" %}

The public channel, however,  is open to all on the Internet - this is typically used for end users (like beneficiaries) for example, accessing self-service portals.

## Creating and configuring a channel

TBD



