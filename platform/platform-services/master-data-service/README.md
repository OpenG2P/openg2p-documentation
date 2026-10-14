---
description: >-
  The platform's catalogue service: versioned datasets and geography, with
  approval, releases, a change feed and an opt-in public catalogue
---

# Master Data Service

The **Master Data Service (MDS)** is the platform's **catalogue service**, also
called *Master Data Service (Catalogue)*. It keeps the reference data that more
than one service needs, so it is defined once and reused everywhere. Every change
goes through an approved draft, every published version is kept, and a consumer
can pin the version it used.

## What it contains

* **Datasets.** The country's own vocabularies and reference entities: gender,
  education level, water source, crop, seed variety, and so on. Each dataset has
  **entries** (a code and labels, optionally typed fields) and a **theme** (such
  as Core or Agriculture).
* **Geography.** The country's administrative hierarchy: levels, every unit with
  its **P-code**, change events (split, merge, rename, …) and boundary files per
  version.
* **Releases.** Named sets of pinned dataset and geography versions.
* **Sample people.** A few dozen made-up individuals and households from the
  country pack, for **testing and demos only**.

MDS holds **no partners**: partner organisations and their keys are in
[Partner Management](../partner-management/README.md).

Datasets, geography and sample people first arrive from a **country pack**. What
a pack is, and how a country is configured end to end, is in
[Country Data Architecture](../../country-data-architecture.md). How a pack loads
into the catalogue is in
[Country packs and migration](catalogue/country-packs-and-migration.md).

## How it works

| | |
|---|---|
| **Versions** | Datasets, and the geography, have numbered versions. A published version is immutable. Reads ask for the latest, a pinned number, a date (`as_of`) or a release |
| **Change control** | Edits go into a draft, which is submitted and approved (maker-checker, or through the Approval Workflow Engine) before it is published |
| **Change feed** | Every step is in an append-only change log, readable with a cursor, sent to the Audit Manager and, optionally, to WebSub |
| **Audit** | Every API call, and every catalogue change, is recorded in the Audit Manager |
| **Public catalogue** | Opt-in and off by default: datasets and geography marked public can be read anonymously, with downloads, DCAT and SKOS |

The details are in [MDS as Catalogue](catalogue/README.md). The standards MDS
uses are on [Standards](standards.md).

## What it serves, and to whom

| Consumer | What it takes | How |
|---|---|---|
| **Registries** (NSR, Farmer Registry, …) | Datasets and geography | At **runtime**, through the `/catalogue` API (versioned, cached, following the change feed). The staff UI fills its dropdowns from the `/attributes` and `/geo` endpoints, and a form's geography levels from `/catalogue/get_geo_levels`. The registry keeps no copy |
| **Registry seed scripts** | Datasets, geography, sample people | At **install**, through the API (`/catalogue`, and `/samples` for demo data) |
| **Staff portal screens** | Geography units, level by level | At **runtime**, via `/geo`; this fills cascading address dropdowns |
| **PBMS, Bridge, SPAR** | Geography lookups | At runtime, via `/geo` |
| **Maps** | Boundary GeoJSON per level and version | `get_geo_boundary`, or the public download when the geography is public |
| **Open-data portals, other websites** | Public datasets and geography | The opt-in [public catalogue](catalogue/public-catalogue.md) (`/public`, anonymous) |

{% hint style="warning" %}
**Registries depend on MDS at runtime for data entry.** A registry's dropdowns
read datasets and geography from MDS. While MDS is unavailable they are empty, so
new records cannot be completed. Records already stored are unaffected: they hold
the codes.
{% endhint %}

How consumers should read, cache and pin is in
[For consumers](catalogue/consumers.md). The endpoints are on
[API Reference](api-reference.md).

## One deployment serves one country

MDS is **single-tenant with respect to country**. A deployment is seeded with
exactly one country pack, declared in one place:

```yaml
geoSeed:
  countryPack: ETH      # chart default: XKM, the fictitious demo country
```

Everything MDS holds belongs to that pack. There is no country dimension on the
data; serving a second country means a second deployment. This keeps registry
images country-agnostic: the same registry build serves Ethiopia or Kamuntu
depending only on the pack the MDS beside it was seeded with.

## Admin UI

Datasets, geography, releases and approvals are managed in the Master Data admin
UI (`master-data-ui`): a catalogue overview home page, Datasets, Geography,
Releases and Activity. See [Admin UI](catalogue/ui.md).

## Source code

* **Repository:** [`github.com/OpenG2P/master-data-service`](https://github.com/OpenG2P/master-data-service)

One repository holds the FastAPI application (`master-data-api`), the admin UI
(`master-data-ui`), the Docker image builds, the Helm chart and the country-pack
loader (`docker/db-seed`). The OpenAPI spec is generated into
`docs/openapi/openapi-master-data.json`.

## Versions

Chart and image versions are listed on [Versions](versions.md). A
machine-readable changelog is also published by CI:
[Master Data Service changelog](https://openg2p.github.io/versions/master-data-service/CHANGELOG.html).

## Deployment

MDS is **not installed on its own**. It ships as part of the
**`commons-services`** Helm chart, alongside the other shared platform services.

* **Chart repository:** [`github.com/OpenG2P/commons`](https://github.com/OpenG2P/commons)

{% hint style="warning" %}
**Version bumps must be made in `commons-services`.** Publishing a new MDS chart
or image does not change any deployment by itself: the version pinned in
`commons-services` is what an install gets.
{% endhint %}

Settings that matter at install. In `commons-services` they sit under
`masterData.` (for example `masterData.geoSeed.countryPack`); its Rancher form
shows the first four in the **Country Pack** group.

| Setting | Rancher label | Notes |
|---|---|---|
| `geoSeed.countryPack` | Country Pack | `ETH` or `XKM` (the fictitious demo country). The MDS chart alone defaults to `XKM`; the `commons-services` form to `ETH` |
| `geoSeed.domains` | Dataset Themes | Themes (pack domains) to load besides the core datasets, as a list or comma-separated. Default `agriculture`; a theme the pack lacks is skipped with a warning |
| `geoSeed.load.codelists` | Load Datasets | On by default |
| `geoSeed.load.samples` | Load Sample People | On by default. Turn it off in production |
| `geoSeed.load.geo` | Load Geography (MDS chart form only) | On by default |
| `masterDataAPI.catalogue.approvalMode` | — | `permission` (default) or `awe`. See [Change control](catalogue/change-control.md#approval-modes) |
| `masterDataAPI.catalogue.public.*` | Public catalogue group (MDS chart form only) | Off by default. See [Public catalogue](catalogue/public-catalogue.md#deployment) |
| `iamRegister.runAsHook` | — | `true` (MDS chart default): the IAM registration Job runs as a Helm hook. `false`: a regular resource; `commons-services` sets `false`, because an umbrella chart chains or skips hooks |
