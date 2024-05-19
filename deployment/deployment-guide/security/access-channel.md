# Access Channel

An access channel is a tuple of Wireguard, Load Balancer, and Ingress gateway.  The [deployment architecture](../../) depicts public, sys admin, and application user access channels. A channel provides group of users access to certain resources of the infrastructure and this can be controlled.  For example, only system administrators should be able to access the Rancher portal.  Or a sandbox inside the OpenG2P cluster (namespace) must be accessed only by a certain set of users.

The public channel is open to all on the Internet - this is typically used for end users (like beneficiaries) accessing self-service portals, for example.

## Creating and configuring a channel

TBD



