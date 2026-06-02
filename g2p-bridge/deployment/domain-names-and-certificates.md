---
description: Domain names and mapping for G2P Bridge
---

# Domain Names and Certificates

## Domain names <a href="#domain-names" id="domain-names"></a>

The suggested convention is given below.

\<component>.\<environment>.\<your org domain>.\<tld>

The chart **derives every hostname from `global.namespace`** by default, so you
usually only set the namespace segment (e.g. `trial`). Each hostname can still be
overridden individually.

| Component | Helm value | Example Domain (namespace = `trial`) |
| --- | --- | --- |
| G2P Bridge Partner API | `global.g2pBridgeHostname` | `g2p-bridge.trial.openg2p.org` |
| Beneficiary Portal API | `global.benePortalHostname` | `g2p-bridge-bene-portal.trial.openg2p.org` |
| Example Bank API (bundled) | `global.exampleBankHostname` | `example-bank.trial.openg2p.org` |

All the above domains point to the Nginx IP for the server (virtual host) that routes to the Istio Ingress gateway on the [OpenG2P Cluster](https://docs.openg2p.org/deployment/base-infrastructure/openg2p-cluster).

## Certificates

SSL certs for all the above must be available, generally as a wild card certificate for the domain, example. `*.dev.openg2p.org`<br>
