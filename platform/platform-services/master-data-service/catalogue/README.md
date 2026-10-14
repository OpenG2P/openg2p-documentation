---
description: >-
  The Master Data Service as a governed, versioned catalogue: datasets and
  geography with drafts, approvals, immutable published versions, lineage,
  releases, a change feed and an opt-in public catalogue
---

# MDS as Catalogue

**MDS as Catalogue** is how the [Master Data Service](../README.md) (MDS) works:
a **catalogue** of datasets and geography. Its reference data is
**governed** (changed only through an approved draft), **versioned** (every
published state is kept and can be read again) and **pinnable** (a consumer can
say exactly which version it used).

It is the same service, database and admin UI as before the catalogue. Nothing an
existing consumer does stopped working: the original tables and endpoints keep
their shapes and always show the **current published** data.

These pages use the admin UI's words: reference data comes in **datasets**, a
dataset holds **entries**, and each dataset has a **theme**. The API keeps its own names
(`list_code`, `value_code`, `domain`); see
[Names in the API](../api-reference.md#names-in-the-api).

## Why reference data needs versions

Reference data looks static, but it changes: a ministry adds seed varieties every
season, renames a crop, retires a unit of measure; a woreda is split in two, two
kebeles are merged, a zone is renamed. Before the catalogue, such a change was an
edit in place, visible to everyone the moment it was saved, with no record of what
the dataset looked like before.

That is not safe for the systems that build on the data:

* **A programme defines entitlements against a dataset.** A subsidy for "improved
  seed varieties of maize and wheat" names a set of entries. If the dataset
  changes under it, the programme's eligibility silently changes too.
* **A registry records codes.** A farmer recorded in woreda `ET041203` in 2026
  must still resolve after that woreda is split in 2027, and a report must be able
  to say where those farmers belong now.
* **Two services must agree.** A registry and a payment system that read "the crop
  dataset" at different moments may see different entries, with no way to tell.

So the rule is: **a consumer that defined something against a version must not be
switched to another version silently.** It reads the latest version when it wants
the latest, pins a version when it needs stability, and moves deliberately.

{% hint style="info" %}
**Why extend MDS rather than adopt something else.** Catalogues could have been
built on the registry platform (as registers) or on an existing open-source
product. The **GeoPrism Registry** was evaluated: it has strong temporal
geography, but its versioning and approvals cover only geographic lists, it runs
on Java and OrientDB, and it has no Helm chart or Keycloak integration. MDS is
therefore extended, borrowing GeoPrism's ideas of **working and published
versions** and **split/merge lineage**. An import adapter from GeoPrism or the
Common Geo Registry is a possible later add-on.
{% endhint %}

## What the catalogue added

| Area | Before | MDS as Catalogue |
|---|---|---|
| **Versions** | One current state, edited in place | Every dataset, and the geography, has numbered versions; old versions remain readable |
| **Drafts** | Edits were live immediately | Edits go into a **draft**; nobody reads a draft unless they ask for it |
| **Approval** | Any user with a write permission changed live data | A draft is **submitted** and **approved** before it is published, by a maker-checker permission (default, comparing stable user ids) or through AWE |
| **Immutability** | Rows could be updated or deleted | A **published version is immutable**, enforced by database triggers. Entries are never deleted; they are **retired** in a later version |
| **Effective dates** | None | A version has an `effective_from`, which may be in the future |
| **Reads** | Always the current data | `latest`, a **pinned** version number, **as of** a date, or a **release**; every response says which version it came from |
| **Typed fields** | Code and label only | A dataset may declare an **attribute schema** so an entry such as a seed variety carries crop, maturity days and so on, including references to other datasets |
| **Languages** | One label | `display` plus `display_i18n` labels per language on datasets, entries, levels and units |
| **Ownership and theme** | None | Each dataset, and the geography, has an **owner department** (`owner_org`, the Publisher), passed to AWE with approval requests; each dataset has a **theme** (`domain`) |
| **Change feed and audit** | None | Every lifecycle step is in an append-only **change log**, readable as a feed with a cursor; the log is also an outbox, so every event reaches the Audit Manager (at least once), and publications and versions taking effect are optionally pushed through WebSub. Every API call is audited as well |
| **Releases** | None | A **catalogue release** names a set of dataset versions and one geography version, for consumers that pin everything at once |
| **Geography** | Levels and units, edited in place | Versioned **as one dataset**, with **change events** (split, merge, rename, …) giving the lineage from old units to new, and a **crosswalk** API |
| **Boundaries** | Files in MinIO, overwritten on reseed | Files in MinIO under **immutable per-version keys** |
| **Open data** | None | Opt-in **public catalogue**: datasets and geography marked public (private by default) are readable anonymously at their published versions, with a licence, downloads and standard metadata. MDS itself stays an admin UI |

## What stays

* **The existing tables.** `g2p_attributes`, `g2p_attribute_values`,
  `g2p_geo_levels` and `g2p_geo_level_values` remain. They are now the
  **materialised current published state** (`ACTIVE` values and units only),
  refreshed in the same transaction as a publish and when a future-effective
  version comes into effect. Anything that reads them directly (the registry
  platform's rollback setting does) keeps working.
* **The original endpoints.** The read endpoints under `/geo` and `/attributes`
  keep their request and response shapes and return the current published data;
  `/attributes` reads add the version they show. The legacy write endpoints still
  work, but now write into the open **draft** instead of changing published data.
  See
  [Change control and approvals](change-control.md#what-the-legacy-write-endpoints-do-now).
* **Country packs** remain the way a country's data first arrives. The first load
  of a dataset or the geography becomes version 1; later loads create drafts. See
  [Country packs and migration](country-packs-and-migration.md).
* **One deployment serves one country**, as before.

## Pages in this section

| Page | What it covers |
|---|---|
| [Concepts](concepts.md) | Datasets and entries, versions and their lifecycle, effective dates, latest / pinned / as-of reads, retired entries, typed fields, labels, ownership and themes, visibility, releases, the change log |
| [Geography and boundary changes](geography.md) | Why geography is versioned as one dataset, change events with worked examples, future-effective changes, the crosswalk, boundaries in MinIO, what consumers do when geography changes |
| [Change control and approvals](change-control.md) | Drafts, submit, approval modes (maker-checker or AWE), permissions and roles, audit, what the original write endpoints do now |
| [API reference](../api-reference.md) | Every MDS endpoint, on one page |
| [Country packs and migration](country-packs-and-migration.md) | First and later pack loads, loader flags and chart values, boundaries, migration of existing data to version 1 |
| [For consumers](consumers.md) | How registries, PBMS and other services should read, cache, pin and follow changes |
| [Admin UI](ui.md) | The Master Data admin UI: the catalogue overview home page, datasets (with themes), versions, drafts, approvals, geography changes, releases and activity |
| [Public catalogue](public-catalogue.md) | Visibility and licence, the anonymous `/public` API, downloads, DCAT and SKOS, deployment settings |
| [Standards](../standards.md) | Every standard MDS uses, where, and how fully |

See also [Country Data Architecture](../../../country-data-architecture.md) for
country packs and P-codes.
