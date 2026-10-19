---
description: >-
  The ideas behind MDS in plain language: datasets, entries and typed fields,
  the geography, versions and effective dates, fixed codes and retired entries,
  reading latest, pinned, as of a date or by release, the change feed,
  visibility and licence
---

# Concepts

This page explains the ideas behind MDS. The fields, statuses and rules a
developer needs are in [API Reference: Data model](api-reference.md#data-model).

## What MDS holds

MDS holds two kinds of reference data: **datasets** and the **geography**.

| | A dataset | The geography |
|---|---|---|
| **How many** | Many: gender, disability type, benefit type, units of measure, crops… | One per country |
| **Shape** | A list of entries, optionally a hierarchy | A hierarchy of levels (e.g. region → zone → woreda) |
| **Codes** | Chosen by the country | P-codes |
| **Extra content** | Optional typed fields | Boundaries (map shapes) per level |
| **How it changes** | Entries added, changed, retired (or brought back) | Units added, retired, split, merged, renamed or moved, recorded as change events |
| **Versioned** | Each dataset on its own | All levels together as one version |

They are treated differently because they behave differently. A dataset is a
self-contained list that one department maintains. The geography is one connected
structure: splitting a woreda moves its kebeles and redraws the map, so its levels
must change together.

## Datasets and entries

A dataset is a list; each item in it is an **entry**, for example *Female* in the
Gender dataset.

Each entry has a **code** and a **label**. The code is what systems store (a
registry records `F`, not *Female*); the label is what people see, with a label
per language where needed (*Maize*, *በቆሎ*, *Boqqolloo*). Datasets and geography
units have labels per language in the same way.

Each dataset has a **theme** (core, agriculture, …) that groups it in the admin
UI and the public catalogue, and a **publisher**: the department responsible for
it.

A dataset may be **hierarchical**: each entry may have one parent entry in the
same dataset, as crop categories contain crops.

### Typed fields

Some datasets need more than a code and a label. A benefit type has an amount and
a payment frequency; a seed variety has a crop, maturity days and a release year.
Their entries carry **typed fields**. Each dataset can declare the rules its
fields must follow (which fields exist, which are required, their types and
ranges), and MDS checks every entry against them. Changing the rules is itself a
change, made in a draft like any other.

A field may **refer to another dataset**: a benefit type's frequency is an entry
of the Payment frequency dataset; a seed variety's crop is an entry of the Crops
dataset. A field may also hold **a list of references**, which is how an entry
belongs to several groups at once (maize is both a cereal and a fodder crop)
while keeping a single parent.

A reference must name an active entry of the other dataset's **published**
version in effect, never one only in its draft. So when two datasets change
together (a new crop and its varieties, a new frequency and the benefit types
that use it), **publish the referenced dataset first**, with the same or an
earlier effective date.

How fields are declared and checked is in
[API Reference: Typed fields schema](api-reference.md#typed-fields-schema).

## The geography

The geography is its own kind of reference data: the country's administrative
levels, every unit with its P-code, and each level's boundaries. Splits, merges
and renames are recorded as change events, and a crosswalk maps old units to new.
See [Geography and Boundary Changes](geography.md).

## Versions

Every dataset, and the geography, has numbered **versions**: 1, 2, 3, …

A change is made in a **draft**, a copy of the latest published version. The
draft is submitted, and another person approves it (or rejects it). When it is
approved it is **published** as the next version. A published version **never
changes**: every later change, however small, is a new version. A dataset has at
most one draft at a time. How drafts are approved is on
[Change Control and Approvals](change-control.md).

### Effective dates

Each published version has an **effective date**: the moment it takes effect. By
default that is when it is published, but it may be in the future. New woredas
that come into force on 1 January 2027 can be approved in October 2026: the
version is published and can be read by number, but it becomes the latest only on
1 January. Effective dates only move forward: a version cannot take effect before
the version published before it.

Effective dates let a consumer check a record against the data **of its date**
(a record dated 30 June 2026 is checked against the entries in effect that day),
run a report for a past period that gives the same answer next year, and prepare
for a change before it takes effect.

### Codes are fixed once published

Records hold codes, so once an entry has been published its **code never
changes**. Its labels, typed fields, parent and order can change in any later
version. To **recode**, retire the old entry and add a new one with the new code;
the old code still resolves. Geography follows the same rule: a new P-code is a
new unit, linked to the old one by a recode event.

### Retired entries

An entry that should no longer be used is **retired** in the next version, not
deleted. It stays in that version and every later one, so a record holding its
code still shows a label ("Season: Summer (retired)"), and a consumer reading an
older version sees it as it was. Lists for new data entry leave retired entries
out; a screen showing an existing record includes them. Geography units are
retired the same way. What a consumer should do with them is on
[For Consumers](consumers.md#retired-entries).

## Reading: latest, pinned, as of, release

Every read says which version it wants:

* **Latest** (the default): the newest published version that has taken effect.
* **Pinned**: one version by number, whatever has been published since.
* **As of a date**: the version that was in effect at that moment, for example to
  check a record dated 30 June 2026 against the data of that day.
* **Release**: the version a named [catalogue release](#catalogue-release) pins.

Every answer says which version it came from. Which read to use is covered in
[For Consumers](consumers.md#latest-pinned-or-as-of).

### Catalogue release

Most consumers pin one or two datasets. Some need **everything** to be
consistent: a programme cycle, a survey, a national report. A **catalogue
release** is a named set of published versions of datasets, plus at most one
version of the geography:

| Release `2027.1` | |
|---|---|
| Benefit types | version 4 |
| Disability types | version 7 |
| Units of measure | version 2 |
| Geography | version 3 |

A release is put together as a draft and, once published, never changes. Reading
by release gives each dataset at the version the release names.

## Change log and change feed

Every step (a draft created, entries changed, submitted, approved, published, a
version taking effect) is recorded in an append-only **change log**. It is the
audit trail, and it is also the **change feed**: a consumer asks for everything
after the last event it saw, and so learns what was published or took effect.
MDS can also push new and effective versions to subscribers. How to follow it is
on [For Consumers](consumers.md#following-changes); how events are delivered is on
[Change Control: audit](change-control.md#audit).

## Visibility and licence

Each dataset, and the geography, is **private** (the default) or **public**, and
may carry a **data licence**. Public data can be read anonymously by other
websites. See [Public Catalogue](public-catalogue.md).
