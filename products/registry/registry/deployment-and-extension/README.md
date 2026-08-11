---
description: >-
  How the OpenG2P Registry is packaged, deployed and extended. The platform is
  now a complete, installable registry in its own right — with a reference
  registry, Helm chart, Docker images, seeding and tests all built in — that any
  domain (social, farmer, disability, …) extends rather than re-assembles.
---

# Deployment and Extension

{% hint style="info" %}
**New home: GitLab.** **`registry-platform`** is now developed at [gitlab.com/openg2p/registry/registry-platform](https://gitlab.com/openg2p/registry/registry-platform).

Any `github.com` links on this page refer to the **earlier GitHub repository**, which is now read-only. They are kept so that references to previous versions keep working.
{% endhint %}

This section explains **how the OpenG2P Registry is packaged, published, deployed and extended** under the current model. It is self-contained: read it to understand how the images and Helm chart are produced, how the platform runs out of the box, and how you turn it into a domain-specific registry.

## The model, and how it changed

{% hint style="warning" %}
**This is the reverse of the previous avatar.** Earlier, `registry-platform` was a *library repo*, and each domain registry (Farmer Registry, National Social Registry, …) **included** it and owned all the Dockerfiles, the full Helm chart, the build/publish CI and the seeding. That duplicated the chart and build logic across every registry and let them drift.

Now the direction is inverted: **`registry-platform` is a complete, runnable registry** that **publishes** the Docker images and the Helm chart. A domain registry is a thin **extension** that builds *on top of* those artifacts. It no longer re-assembles the platform.
{% endhint %}

The platform ships everything a registry needs, in-built and complete:

| In-built | What it means |
|---|---|
| **Reference registry** | A minimal but real registry (Individual + Household) that runs as-is — used for demos, CI and as the canonical example to copy. |
| **Helm chart** | One chart, `openg2p-registry`, that deploys any registry. No per-registry chart copy. |
| **Docker images** | The full set of runtime images, published and versioned together. |
| **Seeding** | A `db-seed` image + machinery; the reference registry's seed ships with it. |
| **Tests** | A sanity/e2e suite (`sanity-tests` image) that verifies a running registry end to end. |

A domain registry (social registry, farmer registry, disability registry, …) is created by **extending** this — supplying only its domain model, seed data, tests and a small deploy overlay. See [Extending into a new registry](extending-into-a-new-registry.md).

## Where the artifacts live

| Artifact | Location |
|---|---|
| Platform + reference registry source | [`OpenG2P/registry-platform`](https://github.com/OpenG2P/registry-platform) |
| Dockerfiles | `registry-platform/docker/*` (+ `ui/staff-ui/Dockerfile`) |
| Helm chart | `registry-platform/helm/openg2p-registry`, published to the OpenG2P Helm repository — [`openg2p.github.io/openg2p-helm`](https://openg2p.github.io/openg2p-helm) |
| Docker images | Docker Hub, the `openg2p/openg2p-registry-*` repositories |
| Reference extension (example) | `registry-platform/reference-extension` |
| Version catalogue / changelog | [`openg2p.github.io/openg2p-packaging/registry-platform/CHANGELOG`](https://openg2p.github.io/openg2p-packaging/registry-platform/CHANGELOG) |

## Versioning & CI

All Docker images and the Helm chart are built by a **single CI workflow** and carry **one version per commit** — images and chart never drift. The versioning scheme, derivation rules and lockstep tagging are documented once, org-wide, here:

{% hint style="info" %}
[**Helm & Docker versioning and CI**](https://docs.openg2p.org/operations/deployment/helm-docker-versioning-and-ci) — the authoritative reference (not repeated here).
{% endhint %}

## In this section

* [**Packaging & the reference registry**](packaging-and-reference-registry.md) — the images, the single chart, the reference registry, and how the domain model is selected at runtime.
* [**Extending into a new registry**](extending-into-a-new-registry.md) — how to build a social / farmer / disability registry on top: extension package, thin images, seeding, deploy overlay, and Rancher packaging.
* [**Country data & seeding**](country-data-and-seeding.md) — country packs, code lists, the seeding switches, and what an empty production install looks like.
* [**Testing & the sanity suite**](testing-and-sanity-suite.md) — the two-part test model (extension-independent vs field-specific) and how to extend the tests for your registry.

{% hint style="success" %}
**Looking for step-by-step instructions?** This section explains *how the model
works*. To actually build and deploy a registry, follow
[**Building a Registry**](../developer-zone/building-a-registry/README.md) — three
phases from an empty repository to production.
{% endhint %}
