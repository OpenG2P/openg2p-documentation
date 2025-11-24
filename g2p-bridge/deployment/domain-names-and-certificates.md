---
description: Domain names and mapping for G2P Bridge
---

# Domain Names and Certificates

## Domain names <a href="#domain-names" id="domain-names"></a>

The suggested convention is given below.

\<component>.\<environment>.\<your org domain>.\<tld>

| Component  | Example Domain             |
| ---------- | -------------------------- |
| G2P Bridge | g2p-bridge.dev.openg2p.org |

All the above domains point to Nginx IP corresponding to server (virtual host) that routes to Istio Ingress gateway server on [OpenG2P Cluster](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster).

## Certificates

SSL certs for all the above must be available, generally as a wild card certificate for the domain, example. `*.dev.openg2p.org`<br>
