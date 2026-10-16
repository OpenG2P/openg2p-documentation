---
description: >-
  The platform's catalogue: versioned datasets, reference entities and
  geography, with drafts, approvals, releases, a change feed and an opt-in
  public catalogue
---

# Master Data Service

The **Master Data Service (MDS)** is the platform's **catalogue**, also called
*Master Data Service (Catalogue)*. It keeps the reference data that more than one
service needs, so it is defined once and reused everywhere. Its data is:

* **governed:** every change goes through a draft that is approved before it is
  published;
* **versioned:** every published version is kept and can be read again;
* **pinnable:** a consumer can say exactly which version it used.

## Why reference data needs versions

Reference data looks static, but it changes. A ministry adds a disability type,
renames a benefit category, adds seed varieties every season, retires a unit of
measure. A district is split in two, two villages are merged, a province is
renamed. Systems that build on the data need to know which version they used:

* **A programme defines entitlements against a dataset.** A cash transfer for
  "households with a member with a severe disability", or a subsidy for "improved
  seed varieties of maize", names a set of entries. If the dataset changes under
  it, the programme's eligibility changes too.
* **A registry records codes.** A person recorded in district `ET041203` in 2026
  must still resolve after that district is split in 2027, and a report must be
  able to say where those people belong now.
* **Two services must agree.** A registry and a payment system that read the same
  dataset at different moments may see different entries.

The examples on these pages use the shipped country pack (Ethiopia's P-codes, where
a district is a *woreda*) and datasets from several sectors.

So the rule is: **a consumer that defined something against a version is never
switched to another version silently.** It reads the latest version when it wants
the latest, pins a version when it needs stability, and moves deliberately.

## What it contains

* **Datasets.** The country's own vocabularies and reference entities: gender,
  education level, water source, crop, seed variety, and so on. A dataset holds
  **entries** (a code and labels, optionally typed fields) and has a **theme**
  (such as Core, or a sector such as Agriculture).
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
[Country Data Architecture](../../country-data-architecture.md). How a pack
loads, and how an older MDS is migrated, is in
[Country Packs and Migration](country-packs-and-migration.md).

The admin UI says datasets, entries and themes. The API keeps its own names
(`list_code`, `value_code`, `domain`); see
[Names in the API](api-reference.md#names-in-the-api).

## How it works

| | |
|---|---|
| **Versions** | Each dataset, and the geography, has numbered versions. A published version is immutable; entries and units are retired in a later version, never deleted. See [Concepts](concepts.md#version) |
| **Reads** | `latest`, a pinned version number, a date (`as_of`) or a release. Every response says which version it came from. See [Concepts](concepts.md#reading-latest-pinned-as-of-release) |
| **Effective dates** | A version has an `effective_from`, which may be in the future |
| **Typed fields and labels** | A dataset may declare a schema for its entries' fields, including references to other datasets. Labels can be given per language |
| **Change control** | Edits go into a draft. The draft is submitted and approved (maker-checker, or through the Approval Workflow Engine) before it is published. See [Change Control and Approvals](change-control.md) |
| **Geography changes** | The geography is versioned as one dataset. Change events (split, merge, rename, …) link old units to new, and a crosswalk maps codes across versions. See [Geography and Boundary Changes](geography.md) |
| **Change feed** | Every step is in an append-only change log, readable with a cursor, sent to the Audit Manager and, optionally, to WebSub |
| **Audit** | Every API call, and every catalogue change, is recorded in the Audit Manager |
| **Public catalogue** | Opt-in and off by default: datasets and geography marked public can be read anonymously, with downloads, DCAT and SKOS. See [Public Catalogue](public-catalogue.md) |

The original `/attributes` and `/geo` endpoints keep their shapes and show the
current published data; their writes go into the open draft. See
[What the legacy write endpoints do now](change-control.md#what-the-legacy-write-endpoints-do-now).
The standards MDS uses are on [Standards](standards.md).

{% hint style="info" %}
**Why MDS rather than another product.** Catalogues could have been built on the
registry platform (as registers) or on an existing open-source product. The
**GeoPrism Registry** was evaluated: it has strong temporal geography, but its
versioning and approvals cover only geographic lists, it runs on Java and
OrientDB, and it has no Helm chart or Keycloak integration. MDS borrows its ideas
of **working and published versions** and **split/merge lineage**. An import
adapter from GeoPrism or the Common Geo Registry is a possible later add-on.
{% endhint %}

## What it serves, and to whom

| Consumer | What it takes | How |
|---|---|---|
| **Registries** (NSR, Farmer Registry, …) | Datasets and geography | At **runtime**, through the `/catalogue` API (versioned, cached, following the change feed). The staff UI fills its dropdowns from the `/attributes` and `/geo` endpoints, and a form's geography levels from `/catalogue/get_geo_levels`. The registry keeps no copy |
| **Registry seed scripts** | Datasets, geography, sample people | At **install**, through the API (`/catalogue`, and `/samples` for demo data) |
| **Staff portal screens** | Geography units, level by level | At **runtime**, via `/geo`; this fills cascading address dropdowns |
| **PBMS, Bridge, SPAR** | Geography lookups | At runtime, via `/geo` |
| **Maps** | Boundary GeoJSON per level and version | `get_geo_boundary`, or the public download when the geography is public |
| **Open-data portals, other websites** | Public datasets and geography | The opt-in [public catalogue](public-catalogue.md) (`/public`, anonymous) |

{% hint style="warning" %}
**Registries depend on MDS at runtime for data entry.** A registry's dropdowns
read datasets and geography from MDS. While MDS is unavailable they are empty, so
new records cannot be completed. Records already stored are unaffected: they hold
the codes.
{% endhint %}

How consumers should read, cache and pin is in [For Consumers](consumers.md).
The endpoints are on [API Reference](api-reference.md).

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

## Source code

* **Repository:** [`github.com/OpenG2P/master-data-service`](https://github.com/OpenG2P/master-data-service)

One repository holds the FastAPI application (`master-data-api`), the admin UI
(`master-data-ui`), the Docker image builds, the Helm chart and the country-pack
loader (`docker/db-seed`). The OpenAPI spec is generated into
`docs/openapi/openapi-master-data.json`. Chart and image versions are on
[Versions](versions.md).

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
| `masterDataAPI.catalogue.approvalMode` | — | `permission` (default) or `awe`. See [Approval modes](change-control.md#approval-modes) |
| `masterDataAPI.catalogue.public.*` | Public catalogue group (MDS chart form only) | Off by default. See [Public Catalogue](public-catalogue.md#deployment) |
| `iamRegister.runAsHook` | — | `true` (MDS chart default): the IAM registration Job runs as a Helm hook. `false`: a regular resource; `commons-services` sets `false`, because an umbrella chart chains or skips hooks |

The loader's other flags are in
[Country Packs and Migration](country-packs-and-migration.md).

## Pages

| Page | What it covers |
|---|---|
| [Concepts](concepts.md) | Datasets and entries, versions and their lifecycle, effective dates, latest / pinned / as-of reads, retired entries, codes fixed once published, typed fields and lists of references, labels, owner and theme, visibility, releases, the change log, storage |
| [Design Decisions](design-decisions.md) | Why MDS is designed as it is: versioning per dataset, effective dates per version, no expiry date on entries, classification hierarchy, fixed codes, mapping to international standards, approvals and audit |
| [Geography and Boundary Changes](geography.md) | Why geography is versioned as one dataset, change events with worked examples, future-effective changes, the crosswalk, boundaries in MinIO, what consumers do when geography changes |
| [Change Control and Approvals](change-control.md) | Drafts, submit, approval modes (maker-checker or AWE), permissions and roles, audit, what the original write endpoints do now |
| [Country Packs and Migration](country-packs-and-migration.md) | First and later pack loads, loader flags, boundaries, licences, migration of existing data to version 1 |
| [For Consumers](consumers.md) | How registries, PBMS and other services read, cache, pin and follow changes |
| [Admin UI](ui.md) | The Master Data admin UI (`master-data-ui`): catalogue overview, datasets, versions, drafts, approvals, geography, releases and activity |
| [Public Catalogue](public-catalogue.md) | Visibility and licence, the anonymous `/public` API, downloads, DCAT and SKOS, deployment settings |
| [API Reference](api-reference.md) | Every MDS endpoint, on one page |
| [Standards](standards.md) | Every standard MDS uses, where, and how fully |
| [Versions](versions.md) | Chart and image versions, and the changelog |
