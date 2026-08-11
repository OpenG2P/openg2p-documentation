---
description: >-
  This guide is variant-agnostic. The repositories below are concrete
  implementations of the same extension pattern. Use them as working templates;
  copy structure and conventions.
---

# Reference Implementations

{% hint style="info" %}
**New home: GitLab.** These repositories are now developed on GitLab:
> * [`national-social-registry`](https://gitlab.com/openg2p/registry/national-social-registry)
> * [`farmer-registry`](https://gitlab.com/openg2p/registry/farmer-registry)
>

Any `github.com` links on this page refer to the **earlier GitHub repository**, which is now read-only. They are kept so that references to previous versions keep working.
{% endhint %}

### Platform Modules

Not to be forked for new domain implementations

| Repository                                                                                                | Monorepo path                   | Role                                |
| --------------------------------------------------------------------------------------------------------- | ------------------------------- | ----------------------------------- |
| [openg2p-registry-gen2-core](https://github.com/OpenG2P/openg2p-registry-gen2-core)                       | `openg2p-registry-gen2-core/`   | Core ORM, services, metadata engine |
| [openg2p-registry-gen2-apis](https://github.com/OpenG2P/openg2p-registry-gen2-apis)                       | `openg2p-registry-gen2-apis/`   | Staff portal API, partner API       |
| [openg2p-registry-gen2-celery](https://github.com/OpenG2P/openg2p-registry-gen2-celery)                   | `openg2p-registry-gen2-celery/` | Celery workers and beat producers   |
| [openg2p-registry-gen2-staff-portal-ui](https://github.com/OpenG2P/openg2p-registry-gen2-staff-portal-ui) | cloned at UI image build        | Staff portal frontend               |
| [openg2p-helm](https://github.com/OpenG2P/openg2p-helm)                                                   | -                               | Base `openg2p-registry` chart       |

***

### Domain Extension Examples

| Repository                                                                      | Monorepo path               | Domain          |
| ------------------------------------------------------------------------------- | --------------------------- | --------------- |
| [farmer-registry](https://github.com/OpenG2P/farmer-registry)                   | `farmer-registry/`          | Farmer Registry |
| [national-social-registry](https://github.com/OpenG2P/national-social-registry) | `national-social-registry/` | Social Registry |

Both follow identical layout: `{variant}-extension/`, `docker/`, `helm/openg2p-{variant}/`, path-scoped CI.

| Area              | Look at                                                         |
| ----------------- | --------------------------------------------------------------- |
| Repository layout | Root folder structure                                           |
| Import alias      | `{variant}-extension/pyproject.toml`                            |
| App bootstrap     | `{variant}-extension/src/.../app.py`                            |
| Domain factory    | `register_domain/factory/g2p_register_domain_factory.py`        |
| Model pattern     | Any `register_domain/models/*.py`                               |
| Domain service    | Any `register_domain/services/g2p_register_domain_service_*.py` |
| Metadata SQL      | `meta_data/register-metadata/g2p_register_definitions.sql`      |
| Service spec      | `docker/staff-portal-api/develop.txt`                           |
| Docker build      | `docker/scripts/build.sh`, `parse_service.py`                   |
| Helm wrapper      | `helm/openg2p-{variant}/values.yaml`                            |
| CI workflows      | `.github/workflows/docker-build-*.yml`, `helm-publish.yml`      |

While building your own domain registry replace domain models, metadata content, image names, and ID-generator keys with your own.

***

### Published product documentation

| Registry                 | Docs                                                                                            |
| ------------------------ | ----------------------------------------------------------------------------------------------- |
| Farmer Registry          | [Farmer Registry](https://docs.openg2p.org/products/registry/farmer-registry)                   |
| National Social Registry | [National Social Registry](https://docs.openg2p.org/products/registry/national-social-registry) |

{% hint style="warning" %}
These pages describe domain models and deployment specifics for each product not the generic build process covered here.
{% endhint %}
