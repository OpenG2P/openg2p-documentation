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

## Reference material

The phases are **instructions**. When they need you to understand something
rather than do something, they link here — read these when you want the *why*:

* [**Anatomy of an extension**](anatomy-of-an-extension.md) — every folder in an
  extension package and what belongs in it. Keep this open during Phase 1.
* [**Concepts**](concepts/README.md) — registry vs register, base models, register
  metadata, the extensions contract.
* [**Deployment and Extension**](../../deployment-and-extension/README.md) — how
  the platform is packaged and why extension works the way it does.
* [**Registry concepts**](../../concepts.md) — the vocabulary (register, section,
  tab, change request) used throughout.

## Worked examples

Two complete registries are built exactly this way. When a phase says "see how a
real registry does this", it means these:

| | |
|---|---|
| [**Farmer Registry**](../../../farmer-registry/README.md) | Farmer + Household, with land, crop, livestock and cooperative sub-registers. [Source](https://gitlab.com/openg2p/registry/farmer-registry) |
| [**National Social Registry**](../../../national-social-registry/README.md) | Individual + Household, with the socio-economic sub-registers used for targeting. [Source](https://gitlab.com/openg2p/registry/national-social-registry) |
