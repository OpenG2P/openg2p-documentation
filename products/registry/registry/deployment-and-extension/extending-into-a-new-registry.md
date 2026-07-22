---
description: >-
  How to turn the platform into a domain registry — social, farmer, disability,
  … — by adding only an extension, seed, tests and a deploy overlay on top of the
  published images and chart.
---

# Extending into a new registry

A domain registry (National Social Registry, Farmer Registry, a Disability Registry, …) is **not** a copy of the platform. It is a small repository that adds its domain on top of the published images and chart. `OpenG2P/farmer-registry` is a complete worked example.

## What an extension repo contains

| It owns | It does **not** own |
|---|---|
| The **extension package** (domain models, schemas, services, factory) | Core, APIs, celery, UI — inherited from the images |
| **Seed data** (register/UI/AWE metadata SQL, templates) | The seeding machinery — inherited from `db-seed` |
| **Domain-specific tests** | The test harness + generic tests — inherited from `sanity-tests` |
| Thin **Dockerfiles** and a **values overlay** (and optionally a Rancher wrapper) | The Helm chart templates — inherited from `openg2p-registry` |

A typical extension repo:

```
<your>-registry/
├── <your>-extension/          # the domain model package (+ meta_data / awe_meta_data / templates seed)
├── docker/                    # thin Dockerfiles (FROM the platform images) + db-seed data
├── deployment/values.yaml     # Helm values overlay
└── test/sanity/               # your field-specific tests
```

## 1. The extension package

Implement the domain classes the platform resolves by **register mnemonic** — `G2PRegister{Mnemonic}`, `G2PRegisterSchema{Mnemonic}`, `G2PRegisterDomainService{Mnemonic}`, and their history/intake variants. This class contract is **unchanged** from before and documented in full here:

{% hint style="info" %}
[**Extensions contract**](../developer-zone/building-a-registry/concepts/registry-extensions/extensions-contract.md) — the required classes, methods and hooks.
{% endhint %}

The one packaging change: install the package under **its own** import name (no `wheel.sources` alias onto `openg2p_registry_extensions`), and select it at runtime via `REGISTRY_EXTENSION_MODULE` (below).

## 2. Thin Docker images

Each image is a few lines — `FROM` the matching platform image, add your extension, point the env var at it:

```dockerfile
ARG RP_VERSION=1.2.0
FROM openg2p/openg2p-registry-staff-api:${RP_VERSION}

# Select your domain model (it coexists with the reference extension already in
# the image; the env var picks yours — no uninstall).
ENV REGISTRY_EXTENSION_MODULE=openg2p_registry_<your>_extension

COPY <your>-extension/ /app/<your>-extension/
RUN pip install --no-cache-dir /app/<your>-extension
```

Repeat for `partner-api` and `celery` (same shape). ENV defaults and the `migrate` + serve CMD are inherited from the platform image.

**db-seed** ships the *reference* seed, so a domain db-seed clears it and adds its own:

```dockerfile
FROM openg2p/openg2p-registry-db-seed:${RP_VERSION}
RUN rm -rf /seed/meta_data/* /seed/awe_meta_data/* /seed/templates/* /seed/seed-data/*
COPY <ext>/src/<pkg>/meta_data/     /seed/meta_data/
COPY <ext>/src/<pkg>/awe_meta_data/ /seed/awe_meta_data/
COPY <ext>/src/<pkg>/templates/     /seed/templates/
```

`staff-ui` and `bene-api` are usually consumed **as-is** from the platform images (no domain code), so most registries don't rebuild them.

## 3. Deploy overlay

Deployment reuses the **published `openg2p-registry` chart** — you supply only a values overlay pointing at your images and identity:

```yaml
global:
  registryVariant: <your>-registry
<component>.image:
  repository: openg2p/openg2p-<your>-registry-<component>
  tag: <version>
```

```bash
helm repo add openg2p https://openg2p.github.io/openg2p-helm
helm install <your>-registry openg2p/openg2p-registry -f deployment/values.yaml
```

## 4. Installing via Rancher

Two options, **neither** of which copies the chart templates:

* **Values-only** — install the `openg2p-registry` app from the catalogue and paste your `values.yaml`. Simplest; no per-registry catalogue tile.
* **Thin wrapper chart** — a ~4-file chart (`Chart.yaml` declaring `openg2p-registry` as a **dependency**, `values.yaml` with your overrides nested under the subchart key, `questions.yaml`, `app-readme.md`) — **no templates**. Gives a branded "<Your> Registry" catalogue tile while the templates still live once in the platform subchart.

The wrapper is *not* the old duplicated chart (which copied ~50 template files); it is a manifest of a handful of files.

## Summary

Building a social, farmer, disability or any other registry means: **one extension package + seed + tests + a handful of thin `FROM`-image Dockerfiles + a values overlay** (and optionally a wrapper chart). Everything else — core, APIs, UI, seeding machinery, the Helm templates, the versioning/CI — is inherited from the platform.
