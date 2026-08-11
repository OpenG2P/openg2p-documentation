---
description: >-
  What a domain registry owns and what it inherits from the platform, and the
  mechanism that lets one image serve several registries.
---

# Extending into a new registry

A domain registry — National Social Registry, Farmer Registry, a disability
registry — is **not a copy of the platform**. It is a small repository that adds
its domain on top of the platform's published images and Helm chart.

{% hint style="success" %}
**This page explains the model. To actually build a registry, follow
[Building a Registry](../developer-zone/building-a-registry/README.md)** — three
phases from an empty repository, through a sandbox, to production.
{% endhint %}

## What you own, what you inherit

| Your repository owns | Inherited from the platform |
|---|---|
| The **extension package** — domain models, schemas, services, factory | Core, APIs, celery and the UI — already in the images |
| **Seed content** — register/UI/AWE metadata SQL, DCI templates, sample data | The seeding machinery in `db-seed` |
| **Field-specific tests** — the assertions shaped by your fields | The test harness and the extension-independent tests in `sanity-tests` |
| **Thin Dockerfiles**, a **values overlay**, and templates for anything the platform has no concept of (analytics, dashboards, maps) | Every service template, IAM/Keycloak wiring and job in the `openg2p-registry` chart |
| A **~40-line CI stub** declaring what this repo has | All build, version, publish and changelog logic, centrally in `openg2p/packaging` |

Folder-by-folder detail:
[Anatomy of an extension](../developer-zone/building-a-registry/anatomy-of-an-extension.md).

## Why extension rather than a fork

Forking the platform means every registry carries its own copy of the templates,
the CI and the runtime — and they drift. Extension keeps a single source for
everything that is not domain-specific, so a platform fix reaches every registry
by moving one pinned version rather than by being reapplied N times.

The cost is one rule: your registry pins **one** platform version, used both for
the Docker base images (`RP_VERSION`) and the chart dependency, and the two move
together.

## How one image serves several registries

The platform's images already contain a **reference extension** so they are
runnable on their own. Your extension installs alongside it, under **its own
import name**, and an environment variable decides which one is active:

```dockerfile
ENV REGISTRY_EXTENSION_MODULE=openg2p_registry_<your>_extension
```

At startup the platform aliases that module into the name its factories import.
Nothing is uninstalled and nothing collides — which is why a domain image is a
`FROM` plus a `pip install`, not a rebuild.

{% hint style="warning" %}
Do **not** alias your package onto `openg2p_registry_extensions` in
`pyproject.toml`. That was the previous mechanism; it prevents your extension
from coexisting with the reference extension in one image.
{% endhint %}

The classes the platform resolves by register mnemonic are specified in the
[Extensions contract](../developer-zone/building-a-registry/concepts/registry-extensions/extensions-contract.md).

## Worked examples

Both are built exactly this way, and are the best reference while you work:

* [Farmer Registry](https://gitlab.com/openg2p/registry/farmer-registry) — Farmer
  and Household, with land, crop, livestock and cooperative sub-registers.
* [National Social Registry](https://gitlab.com/openg2p/registry/national-social-registry)
  — Individual and Household, with the socio-economic sub-registers used for
  targeting.
