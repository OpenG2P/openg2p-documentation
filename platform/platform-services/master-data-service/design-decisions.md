---
description: >-
  Why the Master Data Service (Catalogue) is designed the way it is: why
  reference data needs versions, why a service of its own, versioning per
  dataset, effective dates per version, no expiry date on entries,
  classification hierarchies, fixed codes, mappings to international
  standards, approvals and audit, storage
---

# Design Decisions

This page explains why MDS is designed as it is. It starts with the reason for
versioning at all, then takes common catalogue requirements (version every change,
effective and expiry dates, classification hierarchies, mapping to international
standards, approvals and audit) one by one. Each topic has three parts:

* **Choice**: what MDS does.
* **Why**: the reasoning.
* **What this means for consumers**: what a registry, report or other service does
  with it.

The details are in [Concepts](concepts.md), [Geography and Boundary Changes](geography.md),
[Change Control and Approvals](change-control.md) and [Standards](standards.md).

## Why versions

Reference data looks static, but it changes. A ministry adds a disability type,
renames a benefit category, adds seed varieties every season, retires a unit of
measure. A district is split in two, two villages are merged, a province is
renamed. Systems that build on the data need to know which version they used:

* **A programme defines entitlements against a dataset.** A cash transfer for
  "households with a member with a severe disability" names a set of entries. If
  the dataset changes under it, the programme's eligibility changes too.
* **A registry records codes.** A person recorded in district `ET041203` in 2026
  must still resolve after that district is split in 2027, and a report must be
  able to say where those people belong now.
* **Two services must agree.** A registry and a payment system that read the same
  dataset at different moments may see different entries.

So the rule is: **a consumer that defined something against a version is never
switched to another version silently.** It reads the latest version when it wants
the latest, pins a version when it needs stability, and moves deliberately.

## Why a service of its own

Catalogues could have been built on the registry platform (as registers) or on an
existing open-source product. The **GeoPrism Registry** was evaluated: it has
strong temporal geography, but its versioning and approvals cover only geographic
lists, it runs on Java and OrientDB, and it has no Helm chart or Keycloak
integration. MDS borrows its ideas of **working and published versions** and
**split/merge lineage**. An import adapter from GeoPrism or the Common Geo
Registry is a possible later add-on.

## Versioning per dataset, with plain version numbers

### Choice

A **dataset** has versions, not each entry. Every change, to one entry or to
fifty, goes into a draft. When the draft is approved it becomes the next version
of the whole dataset. Versions are plain numbers: 1, 2, 3. There is no major or
minor part. See [Versions](concepts.md#versions).

### Why

* **A dataset is used as a whole.** A dropdown shows all of `CROP_COMMODITY`. A
  validation rule checks a code against the whole dataset. A programme rule names
  a set of entries. A consumer needs to say "I used version 4", and get back
  exactly what it saw.
* **Per-entry versions would leave the consumer to assemble the state.** It would
  have to work out which version of each entry was current at a moment. A dataset
  version answers that once, for everyone.
* **The tools that a major/minor number tries to signal already exist:**
  * **pinning** (`version: 4`): a consumer that must not move stays put;
  * **latest** and **as-of** reads: a consumer that wants the current, or a past,
    state asks for it;
  * the **change feed** (`get_changes`): a consumer learns that a new version
    exists;
  * the **version diff** (`get_list_diff`): a consumer sees exactly what was
    added, changed, retired or brought back.
* **A major/minor number is a judgement that someone must make on every change.**
  The diff is a fact. A consumer that cares reads the diff, whatever the number.

What counts as **breaking** for reference data is narrow:

| Change | Breaking? | Why |
|---|---|---|
| An entry is **retired** | Yes, for new data | The code is no longer valid for new records. Old records keep it |
| An entry is **recoded** | Yes | In MDS this is retire + add: see [Codes](#codes-fixed-once-published-labels-per-language) |
| An entry's **meaning** changes (same code, different thing) | Yes | Records that hold the code now mean something else. Avoid it: retire and add a new code |
| A new entry | No | Additive |
| A new or corrected label, or a label in another language | No | Codes are unchanged |
| New or changed typed attributes | Usually no | Unless a consumer's rule reads that attribute |

For several datasets that must stay consistent with each other, a
[catalogue release](concepts.md#catalogue-release) pins a named set of versions.

An automatic **"breaking change" flag** on a version is a possible addition: it
could be set on publish when the diff retires an entry. It is **not built**. A
change of meaning cannot be detected automatically; the maker must say so in the
change note.

### What this means for consumers

* Pin a version (or a release) where a change must be reviewed first. Read
  `latest` where the current entries are wanted.
* Follow the change feed. When a dataset you pin has a new version, read the diff
  and decide when to move.
* Treat **retired** entries in the diff as the signal to review.
* Store the version you used with the record where it matters
  (see [For Consumers](consumers.md#store-the-version-with-the-record)).

## Effective dates per version

### Choice

Each published version has one **`effective_from`**. It may be in the future. It
can only move forward: never earlier than the latest published version's. Entries
have no effective dates of their own. See [Effective dates](concepts.md#effective-dates).

### Why

* **Changes come in sets.** New woredas, a new season's varieties, a revised
  fertiliser subsidy list: these take effect together, on one date. One date per
  version says that once.
* **Staging works naturally.** A version for 2027-01-01 can be prepared, approved
  and published in October 2026. Until that date `latest` returns the previous
  version, and the new one can be read by number to prepare. MDS announces it when
  it is published and again when it takes effect.
* **Dates per entry would allow states that were never approved.** With separate
  dates on each entry, the set of entries in effect on a day could be one that no
  one reviewed as a whole.

The limitation: **effective dates only move forward.** While a future-dated
version is pending, a new version cannot take effect before it. An urgent
correction then has to wait for the pending date, or take effect on it.

The practice to follow:

* Publish a future-dated version **close to its date**, not months ahead, unless
  the dataset rarely changes.
* Make urgent corrections **before** staging a future-dated version.
* If an urgent correction is needed while one is pending, publish it with the
  **same effective date** as the pending version. It then takes effect together
  with it.

### What this means for consumers

* `latest` is the version in effect **now**, not the highest number. A higher,
  future-dated version can exist; check `effective_from` and `is_latest`.
* Use the time between "published" and "effective" to prepare: train staff,
  update forms, pre-load caches.

## No expiry date on entries

### Choice

Dataset entries have **no effective-to (expiry) date**. To end an entry on a
date, publish a version, effective on that date, that **retires** it. See
[Retired entries](concepts.md#retired-entries).

Geography **units** do carry `valid_from` and `valid_to`. MDS sets them on
publish from the version's `effective_from`.

### Why

* **A future-dated version that retires the entry does the same job.** The entry
  is current until that date and retired from it.
* **One mechanism, not two.** With both expiry dates and retirement, the two
  could disagree. Retirement goes through a draft and an approval; an expiry date
  on an entry would be a second way to change what is current.
* **Retired entries stay resolvable.** A record that holds a retired code still
  shows its label, in every later version.
* **Geography is different because records keep pointing at old units.** A
  person recorded in woreda `ET041203` in 2026 still holds that code after the
  woreda is split in 2027. `valid_from` and `valid_to` say when each unit existed,
  and the [crosswalk](geography.md#the-crosswalk) says what replaced it.

### What this means for consumers

* To know whether an entry was current on a date, read the dataset **as of** that
  date.
* For geography, a unit's `valid_from` and `valid_to` answer the same question
  directly, and the crosswalk maps old units to new ones.

## Where effective dates matter

Effective dates are not decoration. Three uses depend on them:

| Use | How |
|---|---|
| **Validating an event against the catalogue as it was then** | To check a crop-sown record dated 2026-06-30, read `CROP_COMMODITY` `as_of` that date, not today's version. A crop retired since then is still valid for that date |
| **Reports over past periods** | "Farmers per woreda on 30 June 2026" reads the geography `as_of` that day, so the woredas are the ones that existed then. Running the report again next year gives the same answer |
| **Staging changes** | A version published now, effective later, is visible by number before its date and becomes `latest` on the date |

See [Reading: latest, pinned, as of, release](concepts.md#reading-latest-pinned-as-of-release)
and [Future changes and effective dates](geography.md#future-changes-and-effective-dates).

## Classification hierarchy

### Choice

* **Within a dataset, a single-parent hierarchy.** A hierarchical dataset gives
  each entry at most one parent (`parent_code`). MDS checks that the parent exists
  and is active, and that there are no cycles.
* **Across datasets, links through typed attributes.** A field with `x-list-ref`
  holds a code of another dataset: a seed variety's `crop` is a code of
  `CROP_COMMODITY`. See [Typed attributes](concepts.md#typed-attributes).
* **Cross-classification as a list of references.** An entry that belongs to
  several groups lists them in an array attribute, such as
  `"groups": ["CEREAL", "FODDER"]`, each a code of `CROP_GROUP`. It does not get
  several parents. See [Lists of references](concepts.md#lists-of-references).

### Why

* **One tree gives exact roll-ups.** In a tree, each entry counts once at each
  level, so totals add up. With several parents, a crop that is both a cereal and
  a fodder crop would be counted under both, and the totals would not add up.
* **Other classifications are attributes, with their own datasets.** "Crop group",
  "agro-ecological zone" or "commodity class" are classifications in their own
  right. As datasets they have their own codes, labels, versions and owners.
  Linking to them by `x-list-ref` keeps each one maintained in one place.
* **References are checked.** Every referenced code, single or in a list, must be
  an active entry of the referenced dataset's version in effect.

### What this means for consumers

* **Store the most specific code.** A registry stores the crop (or the variety),
  not the group.
* **Roll up in reports.** Follow `parent_code` up the tree for the main
  hierarchy. Use the attributes for other groupings, for example
  `attribute_filters: {"groups": ["FODDER"]}` to find every fodder crop.
* A report that groups by a list-of-references attribute must expect an entry in
  more than one group.

## Codes fixed once published, labels per language

### Choice

* An entry's **code** cannot change once the entry has been published.
* Its **labels** (`display`, and `display_i18n` per language), attributes, parent
  and sort order can change in any later version.
* A **recode** is: retire the old entry, add a new one with the new code.

MDS enforces this on every write path: the API, the original `/attributes`
endpoints, submit, publish (in the database) and the country-pack loader. A change
to a published code is refused with `G2P-CAT-CODE-IMMUTABLE`. See
[Codes are fixed once published](concepts.md#codes-are-fixed-once-published).

### Why

* **Registries store codes.** A changed code would leave records holding a code
  that no longer exists, or quietly change what they mean.
* **Labels are for people.** Correcting a spelling or adding an Amharic or Afaan
  Oromo label changes nothing that is stored.
* **Retire + add keeps history honest.** The old code stays resolvable, the diff
  shows a retirement and an addition, and a consumer can see that something
  breaking happened.
* **Geography already works this way.** A unit ID (P-code) is the unit's key. A
  new P-code is a new unit, linked to the old one by a `RECODE` change event that
  the crosswalk follows.

### What this means for consumers

* A stored code always resolves, in every later version (as `RETIRED` if it was
  retired).
* Cache labels by version: they may change. Codes do not.
* When a diff shows a retirement and an addition together, check the change note:
  it may be a recode, and records may need mapping.

## Mapping to international standards

### Choice

* **Codes stay the country's own.** MDS does not replace a country's codes with
  an international scheme.
* **A mapping is an attribute of the entry.** When a country pack provides one, a
  dataset's attribute schema declares a field for it, and each entry carries the
  international code or URI. For example:

| International scheme | Example attribute | On which dataset |
|---|---|---|
| FAO World Programme for the Census of Agriculture 2020, Indicative Crop Classification | `fao_wca_icc` | Crops |
| FAOSTAT item codes | `faostat_item_code` | Crops, livestock products |
| AGROVOC concept URIs | `agrovoc_uri` | Crops, pests, practices |
| FAO DAD-IS breeds | `dadis_breed_id` | Livestock breeds |
| UCUM unit codes | `ucum_code` | Units of measure |
| Harmonized System (HS) codes | `hs_code` | Traded commodities, inputs |

* **Geography already uses an international scheme as its codes.** Unit IDs are
  OCHA COD-AB **P-codes**, so they match other datasets that use the same P-codes.

### Why

* **Registries, laws and forms use the country's codes.** Replacing them would
  break existing records and systems.
* **International schemes do not map one-to-one.** A national crop may map to one
  FAO item, to several, or to none. An attribute can hold that, including an
  array, and can be left empty where there is no match.
* **Attributes are already validated and versioned.** A mapping added or corrected
  goes through a draft and an approval like any other change, and its JSON Schema
  can check the format with a `pattern`.

### What is built and what is a convention

| | Status |
|---|---|
| Typed attributes per entry, validated by JSON Schema, versioned with the dataset | **Built** |
| Finding entries by an attribute value (`attribute_filters`) | **Built** |
| COD-AB P-codes as geography unit IDs | **Built** (from the shipped country pack) |
| Attribute names for international mappings (the table above) | **Convention**: a suggestion, not enforced |
| International mappings in the shipped Ethiopia pack | **Not provided**: the pack carries none today |
| International schemes loaded as datasets of their own, referenced with `x-list-ref` | **Option**: possible with what is built; no pack does it |
| Publishing mappings as `skos:exactMatch` in the [public catalogue's](public-catalogue.md) SKOS | **Not built** (see [Standards](standards.md#datasets-and-entries)) |

### What this means for consumers

* Store and exchange the country's codes.
* To report to an international body, read the mapping attribute of each entry
  (at the version the report uses) and translate on output.
* Expect gaps: an entry may have no mapping, or several.

## Approval workflow and audit history

### Choice

* **Every change goes through a draft.** Edits are made in a draft, submitted, and
  approved before they are published. A published version never changes; the
  database refuses it. See [Change Control and Approvals](change-control.md).
* **Two approval modes**, set per deployment:
  * `permission`: maker-checker inside MDS. An approver holds the publish
    permission and must not be the person who created, last edited or submitted
    the draft.
  * `awe`: the draft goes to the
    [Approval Workflow Engine](../approval-workflow-engine/README.md), whose policy
    decides the stages and approvers. The owner department travels with the
    request.
* **Role-based permissions.** Separate permissions to create, edit, retire and
  publish, for datasets and for geography. The `MASTER_DATA_APPROVER` role can
  approve but not edit. See [Permissions](change-control.md#permissions).
* **Audit history at three levels:**
  * each **version** records who created, edited, submitted and decided it, when,
    and the change and decision notes;
  * an append-only **change log** records every step, and also feeds the change
    feed;
  * the [Audit Manager](../audit-manager/README.md) receives every change-log
    event and every API call. See [Audit](change-control.md#audit).

### Why

* **Reference data changes what other systems accept.** A wrong entry reaches
  every registry that reads it. A second person's approval catches mistakes before
  they spread.
* **Approval rules differ between countries and departments.** Simple deployments
  use maker-checker; others need several stages, which AWE provides without
  changing MDS.
* **Audit must be complete and must not change afterwards.** The change log is
  written in the same transaction as the change, and the database refuses to
  update or delete its rows. Delivery to the Audit
  Manager is retried until it succeeds.

### What this means for consumers

* Nothing a consumer reads changes until a version is approved and takes effect.
* Who changed what, when and why is available from the version history, the change
  feed and the Audit Manager.

## Storage

MDS keeps the original `g2p_attributes` and `g2p_geo_*` tables, extended, and adds
versioned tables beside them. The schema is in the
[repository](https://github.com/OpenG2P/master-data-service)
(`models/g2p_catalogue.py`, `catalogue_sql.py`).

| Tables | Hold |
|---|---|
| `g2p_attributes` (extended) | Datasets and their administrative fields |
| `g2p_list_versions`, `g2p_list_version_values` | Dataset versions and their entries |
| `g2p_geo_versions`, `g2p_geo_version_levels`, `g2p_geo_version_units`, `g2p_geo_changes` | Geography versions, levels, units and change events |
| `g2p_catalogue_releases`, `g2p_catalogue_release_members` | Releases and their members |
| `g2p_catalogue_change_log` | The append-only change log, also the delivery outbox |
| `g2p_catalogue_awe_events`, `g2p_catalogue_state` | AWE callbacks received; catalogue settings and schema version |
| `g2p_attribute_values`, `g2p_geo_levels`, `g2p_geo_level_values` | The current published state (active entries and units only), refreshed from the versions |
