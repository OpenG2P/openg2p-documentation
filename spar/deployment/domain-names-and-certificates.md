---
description: Domain names and mapping for SPAR
---

# Domain Names and Certificates

## Domain names <a href="#domain-names" id="domain-names"></a>

The suggested convention is given below.

\<component>.\<environment>.\<your org domain>.\<tld>

Each SPAR API has its own hostname, set directly in the Helm values (or the
Rancher form). Defaults below use the `trial` environment segment.

| Component | Helm value | Example Domain (environment = `trial`) |
| --- | --- | --- |
| SPAR Mapper Partner API | `sparMapperAPI.sparHostname` | `spar.trial.openg2p.org` |
| Beneficiary Portal API | `benePortalAPI.benePortalHostname` | `beneficiary.trial.openg2p.org` |

All the above domains point to the Nginx IP for the server (virtual host) that
routes to the Istio Ingress gateway on the
[OpenG2P Cluster](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster).

## Certificates

SSL certs for all the above must be available, generally as a wild card certificate for the domain, example. `*.dev.openg2p.org`<br>
