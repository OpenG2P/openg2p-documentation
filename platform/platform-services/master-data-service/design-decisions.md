---
description: >-
  Why the Master Data Service (Catalogue) is designed the way it is: why
  reference data needs versions, why a service of its own, versioning per
  dataset, effective dates per version, no expiry date on entries,
  classification hierarchies, fixed codes, mappings to international
  standards, approvals and audit
---

# Design Decisions

This page explains why MDS is designed as it is. It starts with the reason for
versioning at all, then takes the main design choices one by one: versions per
dataset, effective dates, no expiry dates on entries, classification
hierarchies, fixed codes, mappings to international standards, and approvals and
audit. Each topic gives the **choice** (what MDS does) and **why**, and links to
what it means for a consumer on [For Consumers](consumers.md).

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
* **What a major/minor number tries to signal is already available:**
  * a consumer that must not move **pins** a version and stays put;
  * a consumer that wants the current, or a past, state reads the **latest**
    version or the version **as of** a date;
  * the **change feed** tells a consumer that a new version exists;
  * the **comparison of two versions** shows exactly what was added, changed,
    retired or brought back.
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
| New or changed typed fields | Usually no | Unless a consumer's rule reads that field |

For several datasets that must stay consistent with each other, a
[catalogue release](concepts.md#catalogue-release) pins a named set of versions.

**For consumers:** [Pin in configuration](consumers.md#pin-in-configuration).

## Effective dates per version

### Choice

Each published version has one **`effective_from`**. It may be in the future. It
can only move forward: never earlier than the latest published version's. Entries
have no effective dates of their own. See [Effective dates](concepts.md#effective-dates).

### Why

* **Changes come in sets.** New woredas, revised benefit amounts, a new season's
  seed varieties: these take effect together, on one date. One date per
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
correction then has to wait for the pending date, or take effect on it; see
[Admin Guide: schedule a change](admin-guide.md#schedule-a-change-for-a-future-date).

**For consumers:** [Latest, pinned or as of](consumers.md#latest-pinned-or-as-of).

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

**For consumers:** [Retired entries](consumers.md#retired-entries).

## Classification hierarchy

### Choice

* **Within a dataset, a single-parent hierarchy.** A hierarchical dataset gives
  each entry at most one parent (`parent_code`). MDS checks that the parent exists
  and is active, and that there are no cycles.
* **Across datasets, links through typed fields.** A field can hold a code of
  another dataset: a benefit type's frequency is a code of the Payment frequency
  dataset; a seed variety's crop is a code of the Crops dataset. See
  [Typed fields](concepts.md#typed-fields).
* **Cross-classification as a list of references.** An entry that belongs to
  several groups lists them in a field, such as `"groups": ["CEREAL", "FODDER"]`,
  each a code of a Crop groups dataset. It does not get several parents. See
  [Lists of references](api-reference.md#lists-of-references).

### Why

* **One tree gives exact roll-ups.** In a tree, each entry counts once at each
  level, so totals add up. With several parents, a crop that is both a cereal and
  a fodder crop would be counted under both, and the totals would not add up.
* **Other classifications are fields, with their own datasets.** "Crop group",
  "agro-ecological zone" or "benefit category" are classifications in their own
  right. As datasets they have their own codes, labels, versions and owners.
  Referring to them keeps each one maintained in one place.
* **References are checked.** Every referenced code, single or in a list, must be
  an active entry of the referenced dataset's version in effect.

**For consumers:** [Hierarchies and groupings in reports](consumers.md#hierarchies-and-groupings-in-reports).

## Codes fixed once published, labels per language

### Choice

* An entry's **code** cannot change once the entry has been published.
* Its **labels** (one per language), typed fields, parent and sort order can
  change in any later version.
* A **recode** is: retire the old entry, add a new one with the new code.

MDS enforces this on every write path, including the database and the
country-pack loader. See
[Codes are fixed once published](concepts.md#codes-are-fixed-once-published) and
[API errors](api-reference.md#errors).

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

**For consumers:** [Retired entries](consumers.md#retired-entries).

## Mapping to international standards

### Choice

* **Codes stay the country's own.** MDS does not replace a country's codes with
  an international scheme.
* **A mapping is a typed field of the entry.** When a country pack provides one,
  the dataset declares a field for it, and each entry carries the international
  code or URI. For example:

| International scheme | Example field | On which dataset |
|---|---|---|
| ISCED (UNESCO International Standard Classification of Education) | `isced_level` | Education levels |
| ISCO (ILO International Standard Classification of Occupations) | `isco_code` | Occupations |
| ICD-10 (WHO International Classification of Diseases) | `icd10_code` | Health conditions, disability causes |
| ISO 4217 currency codes | `iso4217_code` | Currencies, benefit types |
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
  FAO item, to several, or to none. A field can hold that, including a list, and
  can be left empty where there is no match.
* **Typed fields are already checked and versioned.** A mapping added or
  corrected goes through a draft and an approval like any other change, and the
  dataset's rules can check its format.

What is built and what is only a convention is on
[Standards](standards.md#mappings-to-international-schemes).

**For consumers:** [International codes](consumers.md#international-codes).

## Approval workflow and audit history

### Choice

Every change goes through a draft and is approved by a second person, either
inside MDS (maker-checker) or through the
[Approval Workflow Engine](../approval-workflow-engine/README.md). Every step is
recorded in an append-only change log and sent to the
[Audit Manager](../audit-manager/README.md). The modes, permissions and audit are
on [Change Control and Approvals](change-control.md).

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
