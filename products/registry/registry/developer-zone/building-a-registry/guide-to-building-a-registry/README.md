---
description: Follow these chapters in order when building a new domain registry
---

# Step-by-Step Guide

{% stepper %}
{% step %}
### [Plan your domain](plan-your-domain.md)

Map registers (REGISTER, TABLE, CORE\_TABLE), choose PascalCase mnemonics, and decide mixins, functional IDs, dedup, and optional ingestion or scores before any code.
{% endstep %}

{% step %}
### [Scaffold the repository](scaffold-the-repository.md)

Create the domain repo with `{variant}-extension/`, `docker/`, `helm/openg2p-{variant}/`, and path-scoped GitHub workflows matching reference implementations.
{% endstep %}

{% step %}
### [Configure extensions package](configure-extensions-package.md)

Configure `pyproject.toml` for the `openg2p_registry_extensions` alias, wire `app.py` (core init, factory, migrations), and optional config, ID generator, enrichers, or scores.
{% endstep %}

{% step %}
### [Build models, schemas and services](configure-extensions-package.md)

Implement the classes set per mnemonic - live, history, and intake ORM; matching Pydantic schemas; domain services with validation and display hooks.
{% endstep %}

{% step %}
### [Generate metadata and sample data](generate-metadata-and-sample-data.md)

Author SQL under `meta_data/` for definitions, section UI JSON, tabs, intake forms, lookups, and optional ingestion rules; upload Jinja to MinIO; add sample data under `sample_data/register_data/` for development environments.
{% endstep %}

{% step %}
### [Build docker images](build-docker-images.md)

Build domain branded images via service spec files (domain extensions), bundling the extension with pinned platform packages (API, partner, Celery, UI, db-seed).
{% endstep %}

{% step %}
### [Construct helm charts](construct-helm-charts.md)

Wrap the base `openg2p-registry` chart with your image repositories, `idTypes`, optional Rancher `questions.yaml`, and sample-data toggle to create a deploy-able chart over base.
{% endstep %}

{% step %}
### [Post Install workflow](post-install-workflow.md)

Automate CI/CD builds and Helm publishing with path-scoped workflows so SQL, Python, and chart changes rebuild only what they affect. Smoke-test editable installs, Docker builds, db-seed, cluster install, change requests, Celery, and partner ingestion before production.
{% endstep %}
{% endstepper %}

{% hint style="info" %}
Working examples live in [Reference implementations](reference-implementations.md).
{% endhint %}
