---
layout:
  width: default
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
  metadata:
    visible: true
  tags:
    visible: true
---

# Tech Architecture

<div data-full-width="false"><figure><img src="../../../../.gitbook/assets/Tech Arch - Registry.jpg" alt=""><figcaption><p>Registry - Tech Architecture</p></figcaption></figure></div>

## Technology Stack

The following technologies and tools are used by OpenG2P Registry.

| Technology      | Purpose                                          | Version | License                                                           |
| --------------- | ------------------------------------------------ | ------- | ----------------------------------------------------------------- |
| Ubuntu Server   | Operating System                                 | 22.04   | Free                                                              |
| Python          | Development                                      | 3.11    | [PSF License](https://docs.python.org/3/license.html#psf-license) |
| FastAPI         | REST API                                         |         | MIT                                                               |
| Celery          | Asynchronous task processing                     |         | BSD                                                               |
| Redis           | Celery broker / result backend / caching         |         | BSD / RSALv2                                                      |
| Postgres        | Database                                         |         | Postgres License BSD 2-clause "Simplified License"                |
| Keycloak        | Identity & OIDC clients                          |         | Apache 2.0                                                        |
| Next.js         | Staff Portal UI                                  | 16      | MIT                                                               |
| React           | Staff Portal UI library                          | 19      | MIT                                                               |
| MinIO           | Object storage (documents, attachments, templates) |         | AGPL 2.0                                                          |
| Apache Superset | Reporting                                        |         | Apache 2.0                                                        |
| GitLab          | Source code management                           |         | Commercial (OpenG2P uses Free plan)                               |
| Docker          | Deployment                                       |         | Apache 2.0                                                        |
| Helm            | Packaging / deployment                           |         | Apache 2.0                                                        |
| Rancher         | Deployment                                       |         | Apache 2.0                                                        |
| Kubernetes      | Deployment                                       |         | Apache 2.0                                                        |
| Istio           | Ingress / service mesh                           |         | Apache 2.0                                                        |
| Prometheus      | Monitoring                                       |         | Apache 2.0                                                        |
| Grafana         | Monitoring                                       |         | AGPL 3.0                                                          |
| Nginx           | Web proxy                                        |         | BSD                                                               |
