---
description: >-
  Who reads MDS and how, and how services should read datasets and geography:
  latest, pinned or as-of reads, caching, the change feed, pinning in
  configuration, storing the version used, retired entries, reports and
  geography changes
---

# For Consumers

This page is for teams building on MDS: registries, PBMS, reporting and any other
service that reads datasets or geography. Open-data portals and other websites
without a token use the [public catalogue](public-catalogue.md) instead. The
operations are in the [API Reference](api-reference.md).

## Who reads MDS, and how

| Consumer | What it takes | How |
|---|---|---|
| **Registries** (social, farmer, …) | Datasets and geography | At **runtime**, through the catalogue API: versioned, cached, following the change feed. The staff UI fills its dropdowns from the original `/attributes` and `/geo` reads, and a form's geography levels from the catalogue. The registry keeps no copy |
| **Registry seed scripts** | Datasets, geography, sample people | At **install**, through the same API |
| **Staff portal screens** | Geography units, level by level | At **runtime**, for cascading address dropdowns |
| **PBMS, Bridge, SPAR** | Geography lookups | At runtime |
| **Maps** | Boundary files per level and version | The boundary read, or the public download when the geography is public |
| **Open-data portals, other websites** | Public datasets and geography | The opt-in [public catalogue](public-catalogue.md), anonymous |

{% hint style="warning" %}
**Registries depend on MDS at runtime for data entry.** A registry's dropdowns
read datasets and geography from MDS. While MDS is unavailable they are empty, so
new records cannot be completed. Records already stored are unaffected: they hold
the codes.
{% endhint %}

How the registry platform itself reads MDS is in
[Country data & seeding](../../../products/registry/registry/deployment-and-extension/country-data-and-seeding.md#how-the-registry-reads-mds).

## Latest, pinned or as of

Every read says which version it wants (see
[Concepts](concepts.md#reading-latest-pinned-as-of-release)). Choose by what the data is
used for:

| Use | Read | Why |
|---|---|---|
| Data-entry dropdowns for new records | `latest` | New records should use the current entries |
| Displaying an existing record | `latest` with `include_retired: true` | The record's code must still show a label, even if retired |
| A programme's eligibility or entitlement rules | **Pinned** version (or a release) | The rules were defined against that version and must not change silently |
| A report for a past period | `as_of` the period's date, or pinned to the version used | Reproducible: run it again next year and get the same answer |
| A survey, programme cycle or national report that needs everything consistent | A **catalogue release** | All datasets and the geography at one agreed set of versions |

`latest` is the version in effect **now**, not the highest number: a higher,
future-dated version can already be published. Check `effective_from` and
`is_latest` in the response.

## Pin in configuration

A pin belongs in configuration, where it can be reviewed, not in code:

```yaml
catalogue:
  release: "2027.1"            # pin everything at once, or
  datasets:
    DISABILITY_TYPE: 7         # pin individual datasets
    CROP_COMMODITY: latest
  geography: 3
```

Moving a pin is a deliberate change: read the [diff](api-reference.md#datasets) (`get_list_diff`)
between the pinned and the new version, check what it does to your rules, then
change the configuration. Retired entries in the diff are the signal to review
(what counts as breaking is in
[Design Decisions](design-decisions.md#versioning-per-dataset-with-plain-version-numbers)).
A retirement and an addition together may be a recode: check the change note, as
records may need mapping.

## Store the version with the record

Where a record stores a code, also store **which version the code came from**, or
at least the geography version for unit codes. For example, an entitlement record
might hold `crop: MAIZE` with `catalogue_versions: { "CROP_COMMODITY": 4, "geo": 3 }`,
or a record might hold the release code it was created under.

That lets you later:

* resolve the code exactly as it was meant (`get_list_value` at that version);
* map a unit code to current geography with the
  [crosswalk](geography.md#the-crosswalk), which needs the from-version;
* explain an old decision.

If storing a version per record is not possible, the record's date and an `as_of`
read are the fallback.

## Cache by version

**A published version never changes.** So:

* a response for a **specific version number** can be cached **indefinitely**,
  keyed by dataset (or geography) and version number;
* a `latest` response should be cached only until the change feed says something
  new was published (or for a short time), then re-read. The `version` object in
  the response tells you which version you got, so the cache can be keyed by it;
* boundary files under a version key are immutable and can be cached the same way;
* cache labels by version: they may change in a later version. Codes do not.

The original `/attributes` and `/geo` reads are cached inside MDS, per API
worker, so after a publish other workers may serve the previous data for a short
time (the intervals are set on [Deployment](deployment.md#settings-at-install)).
The `/catalogue` reads are not cached.

## Following changes

Do not poll datasets to notice changes. Use the **change feed**:

1. Keep the last `event_id` you processed (start with `0`).
2. Call [`get_changes`](api-reference.md#change-feed-and-configuration) with it as the
   `cursor`, process the events in order, and store the new cursor.
3. On a `*.version.published` or `*.version.effective` event for a dataset or the
   geography you use: drop `latest` caches, and, if you pin, flag that a newer
   version exists for someone to review.

Events are ordered and the cursor is monotonic, so a consumer that was down simply
catches up from its last cursor.

MDS also publishes new and effective versions and published releases to the
deployment's WebSub hub, so a consumer can subscribe to be told immediately, and
use `get_changes` to fill any gaps. The topics are in the
[API Reference](api-reference.md#change-feed-and-configuration). Notifications are delivered
**at least once**: the same event may arrive twice, so de-duplicate on its
`event_id`.

A version with a **future `effective_from`** is announced twice: when it is
**published** (`*.version.published`; check `effective_from` before treating it as
current, and use the time to prepare), and when it **takes effect**
(`*.version.effective`, on the change feed and on the `*.effective` WebSub topic).

## Retired entries

* **Do not offer retired entries for new data.** Reads leave them out by default.
* **Do not reject records that hold a retired entry.** The entry was valid when
  recorded. Read with `include_retired: true` (or `get_list_value`) to show it.
* A registry's coded-value check should validate **new** values against `latest` and
  accept existing values that are retired.
* A stored code always resolves, in every later version (as `RETIRED` if it was
  retired).
* To know whether an entry was current on a date, read the dataset **as of** that
  date. For a geography unit, its `valid_from` and `valid_to` answer directly.

## Hierarchies and groupings in reports

* **Store the most specific code**: the crop or variety, the benefit type, not
  its group.
* **Roll up** by following `parent_code` up the tree for the main hierarchy. Use
  typed fields for other groupings, for example `attribute_filters:
  {"groups": ["FODDER"]}` to find every fodder crop.
* A report that groups by a list-of-references field must expect an entry in more
  than one group.

## International codes

* Store and exchange the country's codes.
* To report to an international body (ISCED, ICD-10, FAOSTAT, …), read the
  mapping field of each entry, at the version the report uses, and translate on
  output.
* Expect gaps: an entry may have no mapping, or several.

## Geography changes

When a new geography version is published, nothing a consumer holds changes:

| Consumer | What to do |
|---|---|
| **Registries** | **Keep the recorded code**; it still resolves. Store the geography version with the record if you can. Do not rewrite records automatically |
| **Data entry** | Use `latest`: new units appear and retired ones disappear from the effective date. Show existing records with retired units included |
| **Current reporting** | Map old codes to current units through the [crosswalk](geography.md#the-crosswalk). Splits need the record's location or a review |
| **Aggregates and dashboards** | **Recompute** per-unit figures against the new version; never mix versions |
| **Historical reports** | Read the geography as of the report date, or pinned to the version used |
| **Maps** | Rebuild with the new boundary files; keep the old build for historical views |
| **Programmes and anything pinned** | **Re-pin deliberately** anything that selects units (programmes, campaigns), after reviewing the eligibility rules |

A split cannot be resolved by MDS alone; see
[Geography: when a new geography version is published](geography.md#when-a-new-geography-version-is-published).

## Checklist for a new consumer

* [ ] Read through the `/catalogue` APIs, not MDS's database.
* [ ] Decide per use whether you need latest, a pin, as-of, or a release; put pins in
      configuration.
* [ ] Store the version (or release) used alongside records that hold codes.
* [ ] Cache by version number; follow the change feed with a stored cursor.
* [ ] Show retired entries on existing records; hide them in new-entry dropdowns.
* [ ] Have a plan for geography splits affecting your records.
