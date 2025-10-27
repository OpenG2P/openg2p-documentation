---
description: Domain names and certificates for PBMS
---

# Domain names & certificates

## Domain names <a href="#domain-names" id="domain-names"></a>

The suggested convention is given below.

`<component>.<environment>.<your org domain>.<tld>`

<table><thead><tr><th width="241">Component</th><th>Example Domain</th></tr></thead><tbody><tr><td>PBMS</td><td><code>pbms.dev.openg2p.org</code></td></tr><tr><td>PBMS Background Tasks</td><td><code>pbms-bg-task.dev.openg2p.org</code></td></tr></tbody></table>

All the above domains point to Nginx IP corresponding to server (virtual host) that routes to Istio Ingress gateway server on [OpenG2P Cluster](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster).

## Certificates

SSL certs for all the above must be available, generally as a wild card certificate for the domain, example. `*.dev.openg2p.org`\
