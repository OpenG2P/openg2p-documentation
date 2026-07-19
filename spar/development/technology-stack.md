# Technology Stack

The following technologies and tools are used by SPAR.

| Technology | Purpose | Version | License |
| --- | --- | --- | --- |
| Ubuntu Server | Operating System (cluster nodes) | 22.04 | Free |
| Python | Development language | 3.11 | [PSF License](https://docs.python.org/3/license.html#psf-license) |
| openg2p-fastapi-common | OpenG2P application framework (base for all SPAR services) | | MPL 2.0 |
| FastAPI | REST API framework | | MIT |
| Pydantic | Data validation & schemas | | MIT |
| SQLAlchemy | ORM (async) | | MIT |
| Gunicorn | Application server | ~22.0 | MIT |
| Uvicorn | ASGI worker | | BSD |
| PostgreSQL | Database (shared `commons-postgresql`) | | PostgreSQL License |
| Keycloak | Authentication — OIDC / OAuth2 | | Apache 2.0 |
| Docker | Containerization | | Apache 2.0 |
| Helm | Packaging & deployment | | Apache 2.0 |
| Kubernetes | Orchestration | | Apache 2.0 |
| Istio | Service mesh / ingress | | Apache 2.0 |
| Rancher | Cluster management & catalog UI | | Apache 2.0 |
| Nginx | Web proxy / ingress | | BSD |
| Prometheus | Monitoring | | Apache 2.0 |
| Grafana | Monitoring dashboards | | AGPL 3.0 |
| GitHub | Source code management | | Commercial (OpenG2P uses Free plan) |
