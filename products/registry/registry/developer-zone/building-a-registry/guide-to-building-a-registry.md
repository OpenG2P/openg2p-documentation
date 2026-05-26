---
description: Follow these chapters in order when building a new domain registry
---

# Step-by-Step Guide

{% stepper %}
{% step %}
### [Plan your domain](guide-to-building-a-registry/plan-your-domain.md)

Map registers (REGISTER, TABLE, CORE\_TABLE), choose PascalCase mnemonics, and decide mixins, functional IDs, dedup, and optional ingestion or scores before any code.
{% endstep %}

{% step %}
### [Scaffold the repository](guide-to-building-a-registry/scaffold-the-repository.md)

Create the domain repo with `{variant}-extension/`, `docker/`, `helm/openg2p-{variant}/`, and path-scoped GitHub workflows matching reference implementations.
{% endstep %}

{% step %}
### [Configure extensions package](guide-to-building-a-registry/configure-extensions-package.md)

Configure `pyproject.toml` for the `openg2p_registry_extensions` alias, wire `app.py` (core init, factory, migrations), and optional config, ID generator, enrichers, or scores.
{% endstep %}

{% step %}
### [Build models, schemas and services](guide-to-building-a-registry/configure-extensions-package.md)

Implement the classes set per mnemonic - live, history, and intake ORM; matching Pydantic schemas; domain services with validation and display hooks.
{% endstep %}

{% step %}
### [Generate metadata and sample data](guide-to-building-a-registry/generate-metadata-and-sample-data.md)

Author SQL under `meta_data/` for definitions, section UI JSON, tabs, intake forms, lookups, and optional ingestion rules; upload Jinja to MinIO; add sample data under `sample_data/register_data/` for development environments.
{% endstep %}

{% step %}
### [Build docker images](guide-to-building-a-registry/build-docker-images.md)

Build domain branded images via service spec files (domain extensions), bundling the extension with pinned platform packages (API, partner, Celery, UI, db-seed).
{% endstep %}

{% step %}
### [Construct helm charts](guide-to-building-a-registry/construct-helm-charts.md)

Wrap the base `openg2p-registry` chart with your image repositories, `idTypes`, optional Rancher `questions.yaml`, and sample-data toggle to create a deploy-able chart over base.
{% endstep %}

{% step %}
### [Post Install workflow](guide-to-building-a-registry/post-install-workflow.md)

Automate CI/CD builds and Helm publishing with path-scoped workflows so SQL, Python, and chart changes rebuild only what they affect. Smoke-test editable installs, Docker builds, db-seed, cluster install, change requests, Celery, and partner ingestion before production.
{% endstep %}
{% endstepper %}

{% hint style="info" %}
Working examples live in [Reference implementations](guide-to-building-a-registry/reference-implementations.md).
{% endhint %}
