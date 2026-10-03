---
description: >-
  Versioned geography in MDS as Catalogue: change events (split, merge, rename,
  recode, reparent, boundary change) with worked examples, future-effective
  changes, the crosswalk, per-version boundaries in MinIO, and what consumers do
  when the geography changes
---

# Geography and Boundary Changes

Administrative geography changes more often than it seems. Countries split
districts to bring services closer, merge small ones, rename them, move them from
one province to another and redraw their boundaries. Each such change touches data
that other systems hold: a registry records a person's woreda; a report counts
farmers per zone; a dashboard sums area per region; a map draws the shapes.

This page explains how MDS as Catalogue versions the geography, how each kind of
change is recorded, and what consumers should do when a new geography version is
published.

The examples use Ethiopian P-codes (region `ET04` → zone `ET0412` → woreda
`ET041203`). Kebele codes (one level below woreda) are illustrative: the `ETH`
country pack stops at woreda.

## Geography is versioned as one dataset

Code lists are versioned **one list at a time**. Geography is versioned **as a
whole**: its levels, all its units and their boundaries together form one
**geography version**.

The reason is that a geographic change ripples across levels. Splitting a woreda
creates new units at woreda level, changes the set of children of its zone, changes
the zone's boundary if the split moved a line, and may move kebeles to a new parent.
If each level were versioned separately, a consumer could read zones at one version
and woredas at another and get a hierarchy that never existed. One version number
for the whole geography means **every read sees a consistent hierarchy and a
matching set of boundaries.**

A geography version has the same lifecycle as a list version
(`DRAFT` → `SUBMITTED` → `PUBLISHED`, or `REJECTED` or `DISCARDED`; see
[Concepts](concepts.md#version)), the same never-reused version numbers, the same
`effective_from`, and the same latest / pinned / as-of reads. In addition it carries:

* its **levels** (`level_id`, `level_mnemonic`, parent level, `display`,
  `display_i18n`);
* its **units**: `unit_id` (the P-code), level, `name`, `name_i18n`, parent,
  `status` (`ACTIVE` or `RETIRED`), `valid_from` and `valid_to` (set on publish to
  the version's `effective_from` for units it creates or retires);
* its **change events**: what happened between its base version and this one;
* its **boundary objects**: the MinIO key of each level's GeoJSON
  (`boundary_objects`, keyed by level mnemonic);
* its `country` and `owner_org`.

## Units are never deleted

As with list values, a unit is **never deleted**. When a woreda ceases to exist, the
next geography version keeps it with status `RETIRED` and a `valid_to` date. So:

* a record holding the old P-code still resolves to a name, a level and a parent;
* the old unit's boundary is still in the old version's boundary files;
* the crosswalk can say what replaced it.

Reads leave retired units out unless `include_retired: true` is passed. Retiring a
unit that has active descendants fails unless `cascade: true` is passed. A unit
added in the current draft and never published is simply removed.

## Change events

Every geography draft records **why** units changed, as change events. These are
the **lineage**: the link from old units to new ones. Without them, a consumer would
see only that `ET041203` is gone and two new codes appeared, with no way to know
they are related.

| Change type | What happened | `from_units` | `to_units` | Effect on units in the new version |
|---|---|---|---|---|
| `CREATE` | New units that did not come from existing ones | (none) | the new units | New units `ACTIVE` |
| `RETIRE` | Units cease to exist and nothing replaces them | the units | (none) | Units `RETIRED` |
| `RENAME` | Same unit, same code, new name | one unit | the same unit | Name changed |
| `RECODE` | Same unit, new P-code, same level | the old code | the new code | Old code `RETIRED`, new code `ACTIVE` |
| `SPLIT` | One unit becomes two or more, at the same level | the old unit | the new units | Old unit `RETIRED` (or kept, if it continues as one of the parts); new units `ACTIVE` |
| `MERGE` | Two or more units become one, at the same level | the old units | the new (or surviving) unit | Old units `RETIRED` (except a surviving one); new unit `ACTIVE` |
| `REPARENT` | A unit moves to a different parent | one unit | the same unit | Parent changed |
| `BOUNDARY_CHANGE` | A boundary line moves; no unit is created or removed | the affected units | the same units | Units unchanged; boundary files change |

Each event also has an `effective_date` (by default the version's effective date)
and a `note` (for example the proclamation or decision that made the change).

**Edit the units first, then record the event.** `record_geo_change` checks the
event against the draft's base version and the draft: a `CREATE`'s units must be
active in the draft and new; a `RETIRE`'s must be active in the base and retired in
the draft; a `RENAME` or `REPARENT` names one unit whose name or parent actually
differs; a `RECODE`'s old code must be retired and its new code new; the parts of
a `SPLIT` or `MERGE` must be active in the draft and the old units retired (or be
the surviving unit). A unit can end in only one `RETIRE`, `SPLIT`, `MERGE` or
`RECODE` per version. The first geography version has no base and so no events. A
wrong event can be removed with `delete_geo_change`; all events are validated again
on submit.

**Unexplained changes are not blocked: the lineage is completed on submit.** For
every unit that was created, retired, renamed or moved in the draft without an
event naming it, MDS adds an automatic `CREATE`, `RETIRE`, `RENAME` or `REPARENT`
event, and for every unit whose geometry changed in an uploaded boundary file
without another event covering it, a `BOUNDARY_CHANGE`. Automatic events are
flagged `is_auto: true` and noted (`auto: unit created`,
`auto: parent ET0412 -> ET0415`, …). So the crosswalk can always follow a unit,
but an automatic `RETIRE` plus `CREATE` says nothing about a split or merge: record
those explicitly.

### Example 1: a woreda is split into two

Woreda `ET041203` (Adaa) in zone `ET0412` is split into two new woredas, Adaa North
and Adaa South, from 1 January 2027.

In a geography draft (based on the current version, say version 2):

1. Add units `ET041217` (Adaa North) and `ET041218` (Adaa South), parent `ET0412`.
2. Move each of the old woreda's kebeles to the new woreda it now belongs to (set
   its new parent). MDS adds a `REPARENT` event for each on submit, or record them
   yourself (one event per kebele).
3. Retire `ET041203` (it has no active children left).
4. Record the change event:

```json
{
  "change_type": "SPLIT",
  "from_units": ["ET041203"],
  "to_units": ["ET041217", "ET041218"],
  "effective_date": "2027-01-01",
  "note": "Regional proclamation 123/2026"
}
```

5. Upload the new woreda-level boundary file (and the kebele level's, if kebele
   shapes changed) with `upload_draft_boundary`.
6. Set the version's `effective_from` to `2027-01-01` and submit.

Once approved, geography version 3 is published but is **not latest until
1 January 2027**. Until then, `latest` still returns version 2 with `ET041203`
active.

{% hint style="info" %}
**When the old unit continues.** Sometimes a split carves a new woreda out of an
old one, and the old one keeps its name and code for the remaining area. Record it
as a `SPLIT` with `from_units: ["ET041203"]` and
`to_units: ["ET041203", "ET041217"]`. `ET041203` stays `ACTIVE`, with a new
boundary.
{% endhint %}

### Example 2: two kebeles are merged

Kebeles `ET04120305` and `ET04120306` are merged into one. The country decides the
merged kebele keeps the code `ET04120305`.

```json
{
  "change_type": "MERGE",
  "from_units": ["ET04120305", "ET04120306"],
  "to_units": ["ET04120305"],
  "effective_date": "2026-11-01"
}
```

`ET04120306` is retired; `ET04120305` stays active with a larger boundary. Had the
country given the merged kebele a new code, both old codes would be retired and the
new one created.

### Example 3: a zone is renamed

Zone `ET0412` is renamed. Its code does not change, so no record holding it is
affected.

```json
{
  "change_type": "RENAME",
  "from_units": ["ET0412"],
  "to_units": ["ET0412"],
  "note": "Renamed from 'Old Name' to 'New Name'"
}
```

Only the unit's `name` (and `name_i18n`) changes in the new version. Reading the
unit at an older version still returns the old name, which is what a historical
report should print.

### Example 4: a woreda is moved to another zone

Woreda `ET041205` moves from zone `ET0412` to zone `ET0415`.

Because P-codes nest (a child's code begins with its parent's), moving a unit
breaks the nesting unless the unit is given a new code. A country can do either:

* **Keep the code.** Change the woreda's parent to `ET0415` and record a
  `REPARENT` (or let MDS add it on submit). The woreda keeps `ET041205`. Records are
  unaffected, but the code no longer tells you the parent: consumers must read the
  parent from MDS rather than from the code's prefix.
* **Recode.** Add `ET041509` under `ET0415`, retire `ET041205` and record a
  `RECODE` from one to the other. Nesting holds, but records that hold the old code
  now point at a retired unit, and must be mapped through the crosswalk. (A
  `REPARENT` is not recorded here: the old unit no longer exists in the new
  version, and the new one has no previous parent.)

```json
{ "change_type": "REPARENT", "from_units": ["ET041205"], "to_units": ["ET041205"],
  "note": "Moved from zone ET0412 to ET0415" }
```

A `REPARENT` event names only the unit; the old and new parents are the unit's
parent in the base version and in the new one (an automatic event also puts them
in its note).

{% hint style="warning" %}
**Do not derive a parent from a P-code prefix.** After a `REPARENT` without a
`RECODE`, the prefix is wrong. Always take the parent from MDS at the version you
are reading.
{% endhint %}

In every case, a zone or region whose area changed also needs its boundary
updated; a pure boundary adjustment with no other change is a `BOUNDARY_CHANGE`.

## Future changes and effective dates

Administrative changes are usually decided before they take effect. MDS lets the
whole change be prepared, approved and published ahead of time:

* The geography version's **`effective_from`** says when it becomes `latest`.
  Before that date, `latest` returns the previous version; the new version can be
  read by number to prepare (for example, to train staff or pre-build a map).
* Each change event has its own **`effective_date`**, and each unit has
  `valid_from` and `valid_to`, so a consumer can see when a unit came into or went
  out of existence.
* An **`as_of`** read returns the version in effect on a given date, which is how a
  report for "farmers per woreda on 30 June 2026" gets the woredas as they were on
  that day.

The current-state tables (`g2p_geo_levels`, `g2p_geo_level_values`) switch to a
future-effective version when its `effective_from` passes: MDS checks on start, on
every publish and every `catalogue.effectiveRefreshSeconds` (300 s by default),
refreshes the tables and writes a `geo.version.effective` event to the change log.
That event is delivered like the others: to the Audit Manager and, with a WebSub
hub, on the `<prefix>.geo.effective` topic. So a consumer is told both when the
change is **published** (to prepare) and when it **takes effect** (to switch); see
[For consumers](consumers.md#following-changes).

## The crosswalk

The **crosswalk** answers: *"This record holds unit X from geography version A.
What is it in version B?"* It follows the change events between the two versions,
across every version in between, and returns the successor units.

```json
// request payload for get_geo_crosswalk
{ "unit_id": "ET041203", "from_version": 2, "to_version": 3 }
```

```json
// response payload
{
  "unit_id": "ET041203",
  "from_version": 2,
  "to_version": 3,
  "direction": "forward",
  "unchanged": false,
  "units": [
    { "unit_id": "ET041217", "level_id": "l3", "name": "Adaa North", "parent_unit_id": "ET0412", "status": "ACTIVE", "...": "..." },
    { "unit_id": "ET041218", "level_id": "l3", "name": "Adaa South", "parent_unit_id": "ET0412", "status": "ACTIVE", "...": "..." }
  ],
  "unmapped": [],
  "path": [
    { "version_no": 3, "change_id": 57, "change_type": "SPLIT",
      "from_units": ["ET041203"], "to_units": ["ET041217", "ET041218"] }
  ]
}
```

`units` are the successors as they are in `to_version`; `unmapped` lists units
that end without a successor (retired with nothing replacing them); `path` lists
the events followed; `unchanged` is true when the unit maps to itself with no event
on the way. `to_version` defaults to `latest`.

How to use the answer depends on the change:

| Change | Successors | What a consumer can do |
|---|---|---|
| `RENAME`, `REPARENT`, `BOUNDARY_CHANGE` | The same unit | Nothing to map; the code still holds |
| `RECODE`, `MERGE` | Exactly one | Map automatically |
| `SPLIT` | Several | **Cannot be mapped automatically.** The record's location (GPS, kebele, address) decides which part it falls in; otherwise it must be reviewed |
| `RETIRE` | None (in `unmapped`) | Flag for review |

The crosswalk works in both directions: from an old version to a newer one (to
report old records against current geography) and from a newer version back to an
older one (`direction: "backward"`, to compare with a historical baseline). Going
backward it returns predecessors, and `unmapped` lists units that were created
without a predecessor.

## Boundaries in MinIO, per version

Boundaries remain GeoJSON files in MinIO (bucket `openg2p-geo`), as described in
[Country Data Architecture](../../../country-data-architecture.md#map-shapes-are-stored-in-minio-not-in-the-database).
What changes is that they are stored **per geography version, under immutable
keys**:

```
geo/<country>/v<version>/<level mnemonic>.geojson
geo/ETH/v1/woreda.geojson
geo/ETH/v3/woreda.geojson
```

* A boundary file (a GeoJSON `FeatureCollection` for one level) is uploaded **to a
  draft**, under the draft's version key, with `upload_draft_boundary`. It can be
  replaced while the version is a draft. Features are matched to units by
  `properties.pcode` (or `unit_id`, `level_value_id`, or the feature `id`), so MDS
  can tell which units' geometry changed.
* Version numbers are never reused (a discarded draft keeps its number), so a
  key belongs to exactly one version and a published version's objects are never
  overwritten. A later change uploads new files under the next version's key. As a
  safeguard for older data, an upload is refused (`G2P-CAT-409`) if any other
  version, whatever its status, already records the key; the country-pack loader
  applies the same check.
* A level whose file did not change is **not copied**: the new version's
  `boundary_objects` points at the earlier version's object. In the example above,
  version 2 changed no woreda shapes, so its `woreda` entry is still
  `geo/ETH/v1/woreda.geojson`.
* `get_geo_boundary` returns a level's object key for a version, with a
  `presigned_url` and, when a public base URL is configured, a plain `url`; with
  `stream: true` it returns the GeoJSON itself.
* Uploading needs the boundary store configured (chart
  `masterDataAPI.catalogue.boundaryStore`). Objects uploaded to a draft that is
  then discarded stay in the bucket, recorded on the `DISCARDED` version; since its
  number is never used again, no later version writes to those keys.

So a map built for version 2 and a map built for version 3 can sit side by side, and
a historical map always has its own shapes.

## When a new geography version is published

Publishing a new geography version does **not** change any data a consumer
holds. What each kind of consumer should do:

| Consumer | What to do |
|---|---|
| **Registries** (records holding a unit code) | **Keep the recorded code.** It was true when recorded, and it still resolves (retired units are kept). Store the geography version with the record if you can (see [For consumers](consumers.md#store-the-version-with-the-record)). Do not rewrite records automatically |
| **Data entry** | New records use `latest`, so new woredas appear in dropdowns from the effective date and retired ones disappear. Screens showing an existing record read with `include_retired: true` |
| **Current reporting** | Map old codes to current units through the **crosswalk** at query or extract time. One-to-one changes map automatically; splits need the record's location or a review queue |
| **Aggregates and dashboards** | **Recompute** aggregates keyed by unit (counts per woreda, area per zone) against the new version, from the underlying records. An aggregate kept per unit code must not mix versions |
| **Historical reports** | Read the geography **as of** the report's date, or pinned to the version the report was produced with, so the report can be reproduced |
| **Maps** | Rebuild using the new version's boundary files; keep the old version's build for historical views |
| **Programmes and anything pinned** | **Re-pin deliberately.** A programme that targets woredas at version 2 stays on version 2 until someone reviews its targeting against version 3 and moves it |

Consumers learn of a new version from the
[change feed](consumers.md#following-changes), not by noticing that data changed.

{% hint style="warning" %}
**A split cannot be resolved by MDS alone.** MDS knows that `ET041203` became
`ET041217` and `ET041218`; it does not know which of your records fall in which
part. Plan for this before a split takes effect: a record with GPS coordinates can
be placed against the new boundaries; a record with only the old woreda needs a
review or an update by the field team.
{% endhint %}

## Reading geography

| Endpoint | Returns |
|---|---|
| `get_geo_versions` | The version history |
| `get_geo_levels` | The levels at a version |
| `get_geo_units` | Units at a version, by level and parent, optionally with retired ones |
| `get_geo_unit` | One unit at a version, with its ancestors |
| `get_geo_changes` | Change events between two versions |
| `get_geo_crosswalk` | Successors of a unit between two versions |
| `get_geo_boundary` | A level's boundary file at a version |

See [API reference](api-reference.md#geography) for requests and responses.
