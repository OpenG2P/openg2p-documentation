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

# Access Channel

An access channel is a tuple of Wireguard, Load Balancer, and Ingress gateway.  The [deployment architecture](../../) depicts public, sys admin, and application user access channels. A channel provides a group of users access to certain resources of the infrastructure and this can be controlled. &#x20;

For example, only system administrators must be able to access the Rancher portal (or) Only a certain set of users must be able to access the sandbox inside the OpenG2P cluster (namespace).

The public channel is open to all on the Internet - this is typically used for end users (like beneficiaries) for example, accessing self-service portals.

## Creating and configuring a channel

TBD



