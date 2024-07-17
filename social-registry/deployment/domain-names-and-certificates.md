---
description: Domain names and mapping for Social Registry
---

# Domain names and Certificates

## Domain names

Suggested convention:

\<component>.\<environment>.\<your org domain>.\<tld>



<table><thead><tr><th width="282">Component</th><th width="417">Example Domain</th></tr></thead><tbody><tr><td>Social Registry</td><td>socialregistry.dev.openg2p.org</td></tr><tr><td>Keymanager</td><td>keymanager-sr.dev.openg2p.org</td></tr><tr><td>Logging dashboard</td><td>opensearch-logging-sr.dev.openg2p.org</td></tr><tr><td>Reporting dashboard</td><td>opensearch-reporting-sr.dev.openg2p.org</td></tr><tr><td>Minio console</td><td>minio-sr.dev.openg2p.org</td></tr><tr><td>ODK Central</td><td>odk-sr.dev.openg2p.org</td></tr><tr><td>eSignet</td><td>esignet-sr.dev.openg2p.org</td></tr><tr><td>Apache Superset</td><td>superset-sr.dev.openg2p.org</td></tr><tr><td>Kafka dashboard</td><td>kafka-reporting-sr.dev.openg2p.org</td></tr></tbody></table>

All the above domains point to Nginx IP corresponding to server (virtual host) that routes to Istio Ingress gateway server on [OpenG2P Cluste](../../deployment/base-infrastructure/openg2p-cluster/)r.&#x20;

## Certificates

SSL certs for all the above must be available, generally as a wild card certificate for the domain, example. `*.dev.openg2p.org`
