---
description: Domain names and mapping for PBMS
---

# Domain names and Certificates

### Domain names <a href="#domain-names" id="domain-names"></a>

Suggested convention:

\<component>.\<environment>.\<your org domain>.\<tld>

| Component           | Example Domain                  |
| ------------------- | ------------------------------- |
| PBMS                | pbms.dev.openg2p.org            |
| Logging dashboard   | opensearch-pbms.dev.openg2p.org |
| Reporting dashboard | opensearch-pbms.dev.openg2p.org |
| Minio console       | minio-pbms.dev.openg2p.org      |
| ODK Central         | odk-pbms.dev.openg2p.org        |
| eSignet             | esignet-pbms.dev.openg2p.org    |
| Apache Superset     | superset-pbms.dev.openg2p.org   |
| Kafka dashboard     | kafka-pbms.dev.openg2p.org      |

All the above domains point to Nginx IP corresponding to server (virtual host) that routes to Istio Ingress gateway server on OpenG2P Cluster.

### Certificates <a href="#certificates" id="certificates"></a>

SSL certs for all the above must be available, generally as a wild card certificate for the domain, example. `*.dev.openg2p.org`
