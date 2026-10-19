---
description: >-
  How MDS represents geography and administrative boundaries: P-codes, one
  version for the whole geography, units that are never deleted, change events
  (split, merge, rename, recode, reparent, boundary change) with worked examples,
  the crosswalk and boundaries per version
---

# Geography and Boundary Changes

Geography is its own kind of reference data in MDS. It holds the country's
administrative hierarchy: its **levels** (for example country → region → zone → woreda), every
**unit** with its code (the P-code), and each level's **boundaries**.

Administrative geography changes more often than it seems. Districts are split,
merged, renamed, moved to another province, and their lines are redrawn. Each
change touches data other systems hold: a registry records a person's district, a
report counts people per district, a map draws the shapes. MDS records every
change so that old codes still resolve and can be mapped to new ones.

The examples use Ethiopian P-codes (region `ET04` → zone `ET0412` → woreda
`ET041203`). Kebele codes (one level below woreda) are illustrative.

## How geography is represented

| | What it is |
|---|---|
| **One version for the whole geography** | Levels, units and boundaries are versioned together, so a read never mixes zones of one version with woredas of another |
| **Units** | Each unit has its P-code, level, name (and names per language), parent (one unit of the level above), status (active or retired) and the dates it was valid from and to |
| **Change events** | Why units changed between two versions: the link from old units to new ones |
| **Boundaries** | One GeoJSON file per level and version, in the object store |

### P-codes

A **P-code** (place code) is a published identifier for an administrative area,
such as `ET0101` for one zone. OCHA publishes them in its
[Common Operational Datasets](https://cod.unocha.org/) so that every organisation
uses the same code for the same area.

* **P-codes usually nest.** A child's code starts with its parent's: `ET` →
  `ET01` → `ET0101` → `ET010101`. MDS does not enforce this (see
  [Example 4](#example-4-a-woreda-moves-to-another-zone)).
* **The P-code is the identifier.** A unit's id is its P-code; no second internal
  id is minted.

So the code a registry stores on a record, the key of the map shape and the
column a report groups by are the same value. Nothing needs translating.

### Versions and retired units

A geography version has the same lifecycle, effective date and latest / pinned /
as-of reads as any dataset version; see [Concepts](concepts.md#versions).

**Units are never deleted.** When a woreda ceases to exist, the next version keeps
it as **retired**, with the date it ended. A record holding the old code still
resolves, the old shape is still in the old version's boundary files, and the
crosswalk says what replaced it. Reads leave retired units out unless asked to
include them.

## Change events

| Change | What happened | Effect in the new version |
|---|---|---|
| `CREATE` | New units, not from existing ones | New units active |
| `RETIRE` | Units cease to exist; nothing replaces them | Units retired |
| `RENAME` | Same unit and code, new name | Name changed |
| `RECODE` | Same unit, new P-code | Old code retired, new code active |
| `SPLIT` | One unit becomes two or more | Old unit retired (or kept as one of the parts); new units active |
| `MERGE` | Two or more units become one | Old units retired (except a surviving one); new unit active |
| `REPARENT` | A unit moves to a different parent | Parent changed |
| `BOUNDARY_CHANGE` | A line moves; no unit is created or removed | Boundary files change |

Each event has an effective date and a note (for example, the decision that made
the change).

**Edit the units first, then record the event.** MDS checks that the event matches
the edits (for example, that the parts of a split exist and the old unit is
retired).

**Unexplained changes are not blocked.** On submit, MDS adds automatic events
(`CREATE`, `RETIRE`, `RENAME`, `REPARENT`, `BOUNDARY_CHANGE`) for any change left
without one, so the crosswalk can always follow a unit. An automatic retire plus
create does **not** say that a unit was split or merged: record those yourself.

### Example 1: a woreda is split

Woreda `ET041203` (Adaa) is split into Adaa North (`ET041217`) and Adaa South
(`ET041218`) from 1 January 2027. In a geography draft:

1. Add the two new woredas under zone `ET0412`.
2. Move each kebele of the old woreda to its new parent.
3. Retire `ET041203`.
4. Record a `SPLIT` from `ET041203` to `ET041217` and `ET041218`.
5. Upload the new woreda boundary file.
6. Set the effective date to 1 January 2027 and submit.

Once approved, the new version is published but does not become `latest` until
1 January 2027. If the old woreda continues for the remaining area, list it among
the parts of the split; it stays active with a new boundary.

### Example 2: two kebeles are merged

Kebeles `ET04120305` and `ET04120306` are merged and keep the code `ET04120305`.
Record a `MERGE` from both to `ET04120305`. `ET04120306` is retired; `ET04120305`
stays active with a larger boundary. With a new code instead, both old codes are
retired and the new one created.

### Example 3: a zone is renamed

Zone `ET0412` gets a new name; its code stays. Record a `RENAME`. No record is
affected, and a read at an older version still returns the old name, which is
what a historical report should print.

### Example 4: a woreda moves to another zone

Woreda `ET041205` moves from zone `ET0412` to `ET0415`. A country can:

* **keep the code**: change the parent and record a `REPARENT`. Records are
  unaffected, but the code prefix no longer names the parent; or
* **recode**: add `ET041509` under `ET0415`, retire `ET041205` and record a
  `RECODE`. Nesting holds, but records with the old code must be mapped through
  the crosswalk.

{% hint style="warning" %}
**Do not derive a parent from a P-code prefix.** After a reparent without a
recode, the prefix is wrong. Always read the parent from MDS at the version you
use.
{% endhint %}

## Future changes and effective dates

A geography change is usually approved ahead of its **effective date**, like any
[future-dated version](concepts.md#effective-dates): it can be read by number to
prepare, and an **as-of** read gives the woredas in effect on a given day.

## The crosswalk

The **crosswalk** answers: *"A record holds unit X from version A. What is it in
version B?"* It follows the change events between the two versions and returns the
successor units, the units with no successor, and the events it followed. It also
works backwards, from a newer version to an older one.

For Example 1, the crosswalk of `ET041203` from version 2 to version 3 returns
`ET041217` and `ET041218`.

| Change | Successors | What a consumer can do |
|---|---|---|
| `RENAME`, `REPARENT`, `BOUNDARY_CHANGE` | The same unit | Nothing to map |
| `RECODE`, `MERGE` | Exactly one | Map automatically |
| `SPLIT` | Several | **Cannot be mapped automatically.** The record's location decides; otherwise review it |
| `RETIRE` | None | Flag for review |

## Boundaries per version

Boundaries are GeoJSON files in the platform's object store (see
[Deployment](deployment.md#object-store-for-boundaries)). They are **simplified per
level** when the pack is built, coarser at country level and finer further down,
so a browser can load a whole level. They are stored **per geography version,
under keys that never change**:

```
geo/<country>/v<version>/<level>.geojson      e.g. geo/ETH/v3/woreda.geojson
```

* A boundary file is uploaded to a **draft**, and can be replaced until the draft
  is published. Features are matched to units by P-code, so MDS can tell whose
  shape changed.
* A published version's files are never overwritten. A level whose file did not
  change points at the earlier version's file; nothing is copied.
* So a map for version 2 and a map for version 3 can sit side by side.

## Making a change

Geography changes follow the same draft → submit → approve flow as any dataset;
see [Change Control and Approvals](change-control.md). In the
admin UI, units, change events and boundary files are edited on the Geography
page; the [Admin Guide](admin-guide.md#change-geography-split-merge-rename)
has the steps. A country pack can also bring geography changes; see
[Country Packs](country-packs.md#later-loads-drafts-not-overwrites).

## When a new geography version is published

Publishing does **not** change any data a consumer holds: recorded codes still
resolve. What each kind of consumer should do is on
[For Consumers](consumers.md#geography-changes).

{% hint style="warning" %}
**MDS alone cannot resolve a split.** It knows that `ET041203` became two woredas;
it does not know which of your records fall in which part. Plan before the split
takes effect: records with GPS can be placed against the new boundaries; others
need a review.
{% endhint %}

The geography reads (versions, levels, units, changes, crosswalk, boundaries) are
in the [API Reference](api-reference.md#geography).
