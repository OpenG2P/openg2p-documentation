---
description: >-
  The OpenG2P Registry — a platform for building functional registries, and the
  domain registries that extend it.
---

# Registry

**OpenG2P Registry** is an open-source platform for building **functional registries** — not mere databases — of individuals, non-human entities, and groups, designed to fit naturally into a country's digital public infrastructure. A single deployment hosts one or more **Registers** (Individual, Household, Farmer, …), each governed by change-management workflows, version history, consent-aware data sharing and a metadata-driven UI.

The **platform is itself installable** and ships a runnable reference registry. A domain registry — social, farmer, disability, … — is a thin **extension** on top of it, not a fork. So the platform and every registry built on it share one codebase, one Helm chart and one set of images.

{% hint style="info" %}
**New home: GitLab.** These repositories are now developed on GitLab:

* [`registry-platform`](https://github.com/OpenG2P/registry-platform)
* [`national-social-registry`](https://github.com/OpenG2P/national-social-registry)
* [`farmer-registry`](https://github.com/OpenG2P/farmer-registry)
{% endhint %}

## In this section

| | |
|---|---|
| [**OpenG2P Registry (Platform)**](registry/README.md) | The platform itself — concepts, features, design, the developer zone, and how it is [packaged and extended](registry/deployment-and-extension/README.md). Start here to understand how registries are built. |
| [**Farmer Registry**](farmer-registry/README.md) | A registry tuned for agricultural use — Farmer and Household registers plus farm, land, crop, livestock and cooperative data. |
| [**National Social Registry**](national-social-registry/README.md) | A registry for social protection — Individual and Household registers with the socio-economic data used to target and enrol programmes. |

Both the Farmer Registry and the National Social Registry are **extensions of the platform**: each adds only its domain model, seed data, tests and a thin values overlay. See [Deployment and Extension](registry/deployment-and-extension/README.md) for how that works, and [Use Case Implementation](registry/use-case-implementation.md) to build your own.
