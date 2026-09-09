---
description: Geography, code lists, partners and sample data — shared across the platform
---

# Master Data Service

The **Master Data Service** (MDS) is where OpenG2P keeps the reference data that
more than one service needs, so it is defined once and reused everywhere.

## What it contains

* **Geography** — the administrative hierarchy for the country this deployment
  serves, every administrative unit with its **P-code**, and a link to where each
  unit's map shape can be fetched.
* **Code lists** — the country's own vocabularies: genders, education levels,
  water sources, crops and so on, with their values.
* **Sample people** — a few dozen individuals and households belonging to the
  country, used for demos and smoke tests.
* **Partners** — the register of partner organisations (mnemonics, key-manager
  reference IDs, active status) used for inter-service trust and routing.

The first three come from a **country pack**. What a pack is, where packs live and
how a country is configured end to end is covered in
[Country Data Architecture](../../country-data-architecture.md) — this page does
not repeat it.

## What it serves, and to whom

| Consumer | What it takes | How |
|---|---|---|
| **Registries** (NSR, Farmer Registry, …) | Code lists, the geo hierarchy, sample people | At **install**, copied into the registry's own tables |
| **Staff portal screens** | Geo units, level by level | At **runtime**, via the Geo API — this is what fills cascading address dropdowns |
| **Bulk data generators** | The hierarchy and code lists | At install, so generated records point at real units |
| **PBMS, Bridge, SPAR** | Partner and geo lookups | At runtime, via the APIs |
| **Map and reporting surfaces** | Map shapes | From the country pack at build time — **not** from MDS at runtime |

{% hint style="info" %}
**Registries depend on MDS at install time, not on every write.** A registry copies
what it needs into its own tables during seeding and validates against that copy
afterwards. MDS being unavailable later does not stop a registration.
{% endhint %}

See the [API Reference](api-reference.md) for the endpoints themselves.

## One deployment serves one country

MDS is **single-tenant with respect to country**. A deployment is seeded with
exactly one country pack, declared in one place:

```yaml
geoSeed:
  countryPack: ETH      # the single place a deployment declares its country
```

Everything MDS holds — the hierarchy, the code lists, the sample people — belongs
to that pack. There is no country dimension on the data and no way to serve two
countries from one instance; serving a second country means a second deployment.

This is what keeps registry images country-agnostic: the same registry build
serves Ethiopia or Kamuntu depending only on which pack the MDS beside it was
seeded with.

## Source code

* **Repository:** [`github.com/OpenG2P/master-data-service`](https://github.com/OpenG2P/master-data-service)

One repository holds all of the service's parts together — the FastAPI
application, the admin UI, the Docker image builds, the Helm chart, and the
country-pack seeder.

## Versions

Chart and image versions are listed on [Versions](versions.md).

A machine-readable changelog is also published by CI:

* **[Master Data Service changelog](https://openg2p.github.io/versions/master-data-service/CHANGELOG.html)**

## Deployment

MDS is **not installed on its own**. It ships as part of the **`commons-services`**
Helm chart, alongside the other shared platform services.

* **Chart repository:** [`github.com/OpenG2P/commons`](https://github.com/OpenG2P/commons)

{% hint style="warning" %}
**Version bumps must be made in `commons-services`.** Publishing a new Master Data
chart or image does not change any deployment by itself — the version pinned in
the `commons-services` chart is what an install actually gets. A new MDS version
that is not picked up there is a version nobody runs.
{% endhint %}

Country-pack selection (`geoSeed.countryPack`, and which parts of the pack to
load) is therefore also configured through `commons-services`.
