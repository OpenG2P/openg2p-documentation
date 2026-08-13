---
description: >-
  The end-to-end path for implementing a new registry on the OpenG2P Registry
  Platform and taking it from a laptop to production.
---

# Building a Registry

This section is the **implementer's path**. Follow it in order and you go from an
empty repository to a registry running in production.

It is deliberately split into three phases, because they happen at different
times, by different people, with different risks:

<table>
  <thead><tr><th width="230">Phase</th><th>What you do</th><th width="150">Ends when</th></tr></thead>
  <tbody>
    <tr>
      <td><a href="build-your-registry.md"><strong>1. Build your registry</strong></a></td>
      <td>Model your domain, write the extension, build images and a chart. Pure development — no cluster needed until the end.</td>
      <td>CI publishes your images and chart</td>
    </tr>
    <tr>
      <td><a href="run-in-a-sandbox.md"><strong>2. Run it in a sandbox</strong></a></td>
      <td>Install into a namespace with demo data, dashboards and maps, and prove it works.</td>
      <td>Sanity suite passes, staff portal opens</td>
    </tr>
    <tr>
      <td><a href="go-to-production.md"><strong>3. Go to production</strong></a></td>
      <td>Install empty, with the real country pack and every demo switch off.</td>
      <td>Real registrants are being enrolled</td>
    </tr>
  </tbody>
</table>

{% hint style="success" %}
**You are extending, not forking.** The platform publishes runnable images and a
Helm chart; your registry adds only its domain on top. You will not copy platform
code, templates or CI. If you find yourself doing that, stop — you are on the old
model.
{% endhint %}

## Before you start

| You need | Why |
|---|---|
| A **domain model** on paper — which registers, which fields, which relationships | Phase 1 step 1 turns this into code; guessing here is expensive to undo |
| A **GitLab project** under your group | CI, images and the chart are published from it |
| Access to an **OpenG2P environment** with commons-services | Needed only from Phase 2 |
| A **country pack** (or the intent to use the sample one) | Decides what geography and code lists your registry carries |

## Standards this follows

Every OpenG2P service is built to one set of conventions —
[**Creating a New Platform Service**](../../../../../platform/platform-services/creating-a-new-service.md)
— covering naming, IAM separation, Keycloak clients and roles, AWE, audit,
one Helm chart, versioning/CI, `questions.yaml`, the Rancher catalogue, sanity
tests, a clean uninstall script and docs-in-GitBook.

A registry is a **variant built by extension**, so most of that is already
satisfied by the platform images and chart you inherit. The split:

| Inherited — you get it by extending | Yours to uphold |
|---|---|
| Backend on `openg2p-fastapi-common`; staff / partner / beneficiary API separation | **Naming** — derive everything from one slug: repo, Python package, images, chart, DB, Keycloak clients ([§1](../../../../../platform/platform-services/creating-a-new-service.md)) |
| Keycloak clients and roles, partner keys and caching, audit integration | **Your roles → permissions catalog**, registered into IAM by the inherited `iam-register` job |
| Non-root images, restricted `securityContext`, CPU-only HPA, CronJobs | Nothing — these come with the base images and chart |
| One Helm chart, the central versioning/CI pipeline, generated `questions.yaml` | **Pin discipline** — `RP_VERSION` and the chart dependency move together (Phase 1 step 7) |
| The sanity harness and the extension-independent tests | **Your field-specific tests**, and keeping the e2e **off** in production (Phase 3) |
| Idempotent migrations and seeding | **Idempotent seed SQL** — your `meta_data/` re-runs on every upgrade |
| — | **A clean uninstall script** (copy `scripts/uninstall-registry.sh`) and **docs in GitBook**, not repo READMEs |

{% hint style="info" %}
The **nuance checklist** at the end of that page is worth reading before you ship
— several of its items (AWE opt-in, fail-closed partner-key fetch, `TEST_`-tagged
data, prod-safe-off e2e) are exactly the ones a new registry gets wrong.
{% endhint %}

## Reference material

The phases are **instructions**. When they need you to understand something
rather than do something, they link here — read these when you want the *why*:

* [**Anatomy of an extension**](anatomy-of-an-extension.md) — every folder in an
  extension package and what belongs in it. Keep this open during Phase 1.
* [**Contracts that fail silently**](contracts-that-fail-silently.md) — the names
  that must match across files nothing type-checks, and what breaks when they do
  not. Read it before writing metadata; it is where the time goes otherwise.
* [**Concepts**](concepts/README.md) — registry vs register, base models, register
  metadata, the extensions contract.
* [**Deployment and Extension**](../../deployment-and-extension/README.md) — how
  the platform is packaged and why extension works the way it does.
* [**Registry concepts**](../../concepts.md) — the vocabulary (register, section,
  tab, change request) used throughout.

## Worked examples

Complete registries built exactly this way. When a phase says "see how a real
registry does this", it means these:

| | Shape | |
|---|---|---|
| [**Farmer Registry**](../../../farmer-registry/README.md) | Two registers | Farmer + Household, with land, crop, livestock and cooperative sub-registers. [Source](https://gitlab.com/openg2p/registry/farmer-registry) |
| [**National Social Registry**](../../../national-social-registry/README.md) | Two registers | Individual + Household, with the socio-economic sub-registers used for targeting. [Source](https://gitlab.com/openg2p/registry/national-social-registry) |
| [**Disability Registry**](../../../disability-registry/README.md) | **One register** | A single `PersonWithDisability` register with eight sub-registers and no group register — the example to follow if your domain has one subject. Built to the SPDCI Disability Registry data objects. [Source](https://gitlab.com/openg2p/registry/disability-registry) |

{% hint style="info" %}
The two-register examples make a household register look mandatory. It is not —
a registry with a single register is a normal shape and needs no special
handling.
{% endhint %}
