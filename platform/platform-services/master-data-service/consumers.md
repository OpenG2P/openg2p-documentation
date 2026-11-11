---
description: >-
  For teams whose services read MDS: who reads it today, and for each topic what
  to know and what to do (which version to read, pinning, storing the version,
  caching, learning about new versions, retired entries, reports and geography
  changes), with a checklist
---

# For Consumers

This page is for teams whose services read MDS: registries, Partner Management,
reporting and any other service that reads datasets or geography. Each topic says
first **what to know** (how MDS behaves) and then **what to do** (what your
service should do). The ideas are explained in [Concepts](concepts.md); the
operations are in the [API Reference](api-reference.md). Open-data portals and
other websites without a token use the [public catalogue](public-catalogue.md)
instead.

## Who reads MDS, and how

| Consumer | What it reads | When and how |
|---|---|---|
| **Registries** (farmer, social, …) | Datasets and geography | At **runtime**, through the [catalogue API](api-reference.md#staff-api), with its own service account. The registry's staff portal fills its dropdowns (datasets) and its cascading address fields (geography, level by level) from MDS. The registry keeps no copy |
| **Registry seed scripts** | Datasets, geography, sample people | At **install**, through the same API |
| **Partner Management** | The datasets `CONSENT_PURPOSE` and `SUBJECT_ID_TYPE` (purposes and subject ID types a partner's access policy may name) | At **runtime**, with its own service account, cached. A dataset the pack lacks, or MDS down, leaves the policy form free text. See [Master Data datasets](../partner-management/functional-specifications.md#master-data-datasets) |
| **Maps** | Boundary files per level and version | The boundary read, or the public download when the geography is public |
| **Open-data portals, other websites** | Public datasets and geography | The opt-in [public catalogue](public-catalogue.md), anonymous |

Other services (PBMS, G2P Bridge, SPAR) do not read MDS today.

{% hint style="warning" %}
**Registries depend on MDS at runtime for data entry.** A registry's dropdowns
read datasets and geography from MDS. While MDS is unavailable they are empty, so
new records cannot be completed. Records already stored are unaffected: they hold
the entry codes and P-codes.
{% endhint %}

How the registry platform itself reads MDS is in
[Country data & seeding](../../../products/registry/registry/deployment-and-extension/country-data-and-seeding.md#how-the-registry-reads-mds).

## Choosing which version to read

**What to know.** Every read names the version it wants: latest (the default), a
version number, as of a date, or a [catalogue release](concepts.md#catalogue-release)
(see [Which version a read returns](concepts.md#which-version-a-read-returns)).
Every answer says which version it came from. `latest` is the version in effect
**now**, not the highest number: a higher, future-dated version can already be
published (see `effective_from` and `is_latest` in the response).

**What to do.** Choose by what the data is used for:

| Use | Read | Why |
|---|---|---|
| Data-entry dropdowns for new records | `latest` | New records should use the current entries |
| Displaying an existing record | `latest` with `include_retired: true` | The record's entry code must still show a label, even if retired |
| A programme's eligibility or entitlement rules | A **version number**, or a **catalogue release** | The rules were defined against that version and must not change silently |
| A report for a past period | `as_of` the period's date, or the version number used | Reproducible: run it again next year and get the same answer |
| A survey, programme cycle or national report that needs everything consistent | A **catalogue release** | All datasets and the geography at one agreed set of versions |

The parameters are in [Choosing a version](api-reference.md#choosing-a-version).

## Pinning a version in your service's settings

**What to know.** To *pin* is to make your service read a fixed version (a
version number or a catalogue release) instead of `latest`. The pin is a setting
of **your service**, not of MDS: MDS keeps every published version, and each
consumer decides which one it reads. Moving a pin later, to a newer version, is a
change to your service.

The registry, for example, can pin every MDS read to one catalogue release with
the Helm value `global.catalogueRelease` (empty: `latest`). A dataset the release
does not name is then read at its latest version.

**What to do.**

1. Keep the pin in your service's configuration (Helm values or environment), not
   in code, so it is visible and reviewed. A service with its own settings might
   use:

   ```yaml
   catalogue:
     release: "2027.1"            # pin everything at once, or
     datasets:
       DISABILITY_TYPE: 7         # pin individual datasets by version number
       CROP_COMMODITY: latest
     geography: 3
   ```

2. Before moving a pin to a newer version, compare the two versions with
   [`get_list_diff`](api-reference.md#datasets): entries added, changed and
   retired. Check what the changes do to your rules, then change the setting.
3. Treat **retired entries** in the comparison as the signal to review (what
   counts as breaking is in
   [Design Decisions](design-decisions.md#versioning-per-dataset-with-plain-version-numbers)).
   A retirement and an addition together may be a recode: check the change note,
   as records may need mapping.

## Store the version with the record

**What to know.** An entry code always resolves, in every later version, but its
label and fields can change from version to version, and a P-code can be split or
merged in a later geography.

**What to do.** Where a record stores an entry code or a P-code, also store
**which version it came from**, or at least the geography version for P-codes. For
example, an entitlement record might hold `crop: MAIZE` with
`catalogue_versions: { "CROP_COMMODITY": 4, "geo": 3 }`, or the release code it was
created under. That lets you later:

* resolve the entry code exactly as it was meant (`get_list_value` at that version);
* map a P-code to current geography with the
  [crosswalk](geography.md#the-crosswalk), which needs the from-version;
* explain an old decision.

If storing a version per record is not possible, the record's date and an `as_of`
read are the fallback.

## Caching

**What to know.**

* **A published version never changes**, nor do boundary files under a version.
* A `latest` read changes when a new version is published or takes effect.
* Labels may change in a later version; entry codes and P-codes do not.
* Inside MDS, some of the original `/attributes` and `/geo` reads are cached per
  API worker (which ones: [Original endpoints](api-reference.md#original-endpoints)),
  so after a publish other workers may serve the previous data for a short time
  (the intervals are on [Deployment](deployment.md#settings-at-install)). The
  `/catalogue` reads are not cached.

**What to do.**

* Cache a read of a **version number** without expiry, keyed by dataset (or
  geography) and version number. Cache labels by version.
* Cache a `latest` read until the [change feed](#learning-about-new-versions-the-change-feed)
  says something was published or took effect (or for a short time), then read it
  again. Key the cache by the `version` object in the response.
* Cache boundary files by version the same way.

## Learning about new versions: the change feed

**What to know.** MDS records every step of every version in its change log, and
serves it as a **change feed** (`get_changes`): events in order, each with an
increasing `event_id`. It also pushes new and effective versions and published
releases to the deployment's WebSub hub, if one is set. WebSub delivers **at least
once**: the same event may arrive twice. A version with a **future
`effective_from`** is announced twice: when it is **published**
(`*.version.published`) and when it **takes effect** (`*.version.effective`).

**What to do.**

1. Do not poll datasets to notice changes. Keep the last `event_id` you processed
   (start with `0`).
2. Call [`get_changes`](api-reference.md#change-feed-and-configuration) with it as
   the `cursor`, process the events in order, and store the new cursor. A service
   that was down catches up from its last cursor.
3. On a `*.version.published` or `*.version.effective` event for a dataset or the
   geography you use: drop `latest` caches and, if you pin, flag that a newer
   version exists for someone to review. On `*.version.published`, check
   `effective_from` before treating the version as current.
4. To be told at once, also subscribe to the WebSub topics (in the
   [API Reference](api-reference.md#change-feed-and-configuration)); de-duplicate
   on `event_id`, and use `get_changes` to fill any gaps.

## Retired entries

**What to know.** A retired entry stays in its dataset, marked retired, in every
later version (see [Retired entries](concepts.md#retired-entries)). Reads leave it
out unless asked; a stored entry code or P-code always resolves (as `RETIRED` if it
was retired). A geography unit carries `valid_from` and `valid_to`.

**What to do.**

* **Do not offer retired entries for new data.**
* **Do not reject records that hold a retired entry.** The entry was valid when
  recorded. Read with `include_retired: true` (or `get_list_value`) to show it.
* Validate **new** values against `latest`, and accept existing values that are
  retired.
* To know whether an entry was current on a date, read the dataset **as of** that
  date. For a geography unit, its `valid_from` and `valid_to` answer directly.

## Hierarchies and groupings in reports

**What to know.** A dataset may have one main hierarchy (`parent_code`), and
[typed fields](concepts.md#typed-fields) can hold other groupings, including lists
of references, so an entry can be in more than one group.

**What to do.**

* **Store the most specific entry code**: the crop or variety, the benefit type,
  not its group.
* **Roll up** by following `parent_code` up the tree. Use typed fields for other
  groupings, for example `attribute_filters: {"groups": ["FODDER"]}` to find every
  fodder crop.
* A report that groups by a list-of-references field must expect an entry in more
  than one group.

## Reporting to international bodies

**What to know.** Records hold the country's own entry codes and P-codes. A
dataset can carry a mapping field to an international classification (ISCED,
ICD-10, FAOSTAT, …), which may be empty or have several values.

**What to do.**

* Store and exchange the country's own entry codes and P-codes.
* To report, read each entry's mapping field at the version the report uses, and
  translate on output. Expect gaps.

## Geography changes

**What to know.** When a new geography version is published, nothing a consumer
holds changes: recorded P-codes still resolve. Splits, merges and renames are
recorded as change events, and the [crosswalk](geography.md#the-crosswalk) maps old
units to new. A split cannot be resolved by MDS alone; see
[Geography: when a new geography version is published](geography.md#when-a-new-geography-version-is-published).

**What to do.**

| Consumer | What to do |
|---|---|
| **Registries** | **Keep the recorded P-code**. Store the geography version with the record if you can. Do not rewrite records automatically |
| **Data entry** | Use `latest`: new units appear and retired ones disappear from the effective date. Show existing records with retired units included |
| **Current reporting** | Map old P-codes to current units through the crosswalk. Splits need the record's location or a review |
| **Aggregates and dashboards** | **Recompute** per-unit figures against the new version; never mix versions |
| **Historical reports** | Read the geography as of the report date, or at the version number used |
| **Maps** | Rebuild with the new boundary files; keep the old build for historical views |
| **Programmes and anything pinned** | **Move the pin deliberately** for anything that selects units (programmes, campaigns), after reviewing the eligibility rules |

## Checklist for a new consumer

* [ ] Get a service account (a Keycloak client in the `staff` realm) and read
      through the [Staff API](api-reference.md#staff-api) (`/catalogue`), never
      MDS's database. See [Authentication and permissions](api-reference.md#authentication-and-permissions).
* [ ] Decide per use whether you read latest, a version number, as of a date, or a
      catalogue release ([Choosing which version to read](#choosing-which-version-to-read));
      keep pins in your service's settings ([Pinning](#pinning-a-version-in-your-services-settings)).
* [ ] Store the version (or release) used with records that hold entry codes or
      P-codes ([Store the version with the record](#store-the-version-with-the-record)).
* [ ] Cache by version number ([Caching](#caching)); follow the change feed with
      a stored cursor ([`get_changes`](api-reference.md#change-feed-and-configuration)).
* [ ] Show retired entries on existing records; hide them in new-entry dropdowns
      ([Retired entries](#retired-entries)).
* [ ] Have a plan for geography splits affecting your records
      ([Geography changes](#geography-changes), [the crosswalk](geography.md#the-crosswalk)).
* [ ] For anonymous or public use, use the [Public API](api-reference.md#public-api)
      instead.
