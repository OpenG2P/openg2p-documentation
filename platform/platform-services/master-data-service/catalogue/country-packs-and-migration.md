---
description: >-
  How country packs load into MDS as Catalogue (version 1 on first load, drafts
  on later loads), where boundaries go, and how an existing MDS is migrated
---

# Country Packs and Migration

A [country pack](../../../country-data-architecture.md) is still how a country's
data first reaches MDS. What changes is what a load does to data that is already
there: **a pack never overwrites published data.**

The pack loader (`docker/db-seed/load_geo_pack.py`) runs in the chart's geo-seed
Job after the API has created the catalogue schema: the Job waits until
`g2p_catalogue_state.schema_version` reaches the catalogue schema version it was
built for (`CATALOGUE_SCHEMA_VERSION`, currently **4**, set in the Job and kept
equal to the API's), and the loader itself refuses to run against an older
schema. It decides **per subject**: each list, and the geography, is handled on its
own.

## First load of a subject: version 1, published

A list that does not exist yet, or the geography when it has no version yet, is
loaded as **version 1** and **published directly**:

* each such code list in the pack becomes version 1 of that list, `PUBLISHED`;
* the pack's levels and units become **geography version 1**, `PUBLISHED`;
* the pack's boundary files are uploaded to MinIO under the version 1 keys,
  `geo/<country>/v1/<level>.geojson`;
* the current-state tables (`g2p_attributes`, `g2p_attribute_values`,
  `g2p_geo_levels`, `g2p_geo_level_values`) are filled as before, so registries
  work immediately.

Version 1 is effective from the moment of the load. This applies on a fresh install, and equally later to a list that appears for the
first time: a list added in a newer pack release, or a domain (such as
`agriculture`) enabled after the first install. There is no approval step: there is
nothing published to protect yet. This is the loader's `--publish-initial`
behaviour, on by default (chart `geoSeed.publishInitial: true`);
`--no-publish-initial` (`publishInitial: false`) leaves version 1 as a draft for
approval instead.

Labels in other languages (`display_i18n`, `name_i18n`), P-codes, each value's
`roles`, `attributes`, a list's `attribute_schema`, and its `description` and
`owner_org` (default `geoSeed.ownerOrg`) are kept as the pack gives them.
Each list's `domain` is set to `core` for the pack's `codelists/` and to the domain
name for `domains/<domain>/` (lists a domain's SQL fixtures add get that domain
too). A later load fills the domain of a list that has none (a list loaded before
the field existed) and never changes one already set; it is not versioned, so no
draft is created for it.

## Later loads: drafts, not overwrites

When a subject already has a published version, the loader compares the pack with
the **highest published version**:

* a list whose values or versioned metadata **differ** gets a **draft**: new values
  added, changed values updated, and values missing from the pack **retired**
  (never deleted);
* a list that is **unchanged** is left alone; no version is created, so re-running
  the loader is a no-op;
* if the geography differs (levels, units or boundary files), a **geography
  draft** is created: new units added, changed units updated, units missing from
  the pack **retired**, and changed boundary files uploaded under the draft's keys.
  Levels missing from the pack are kept, with a warning;
* a subject that already has an **open draft** (`DRAFT` or `SUBMITTED`) is
  skipped, as is a list that exists but was never published.

A list's `description` and `owner_org`, which are not versioned, are updated in
place when the pack changes them.

The drafts are left as **`DRAFT`, not submitted**. Someone reviews them (the diff
against the base version), submits them, and they are approved like any other
change (see [Change control and approvals](change-control.md)). Nothing a consumer
reads changes until then.

{% hint style="warning" %}
**A pack usually carries no change events.** A pack is a snapshot; it says which
units exist, not that `ET041203` was split into `ET041217` and `ET041218`. On submit
MDS completes the lineage with automatic `RETIRE` and `CREATE` events, which the
crosswalk can follow but which do not link old units to new ones. Before
submitting, record the real change events (split, merge, recode, …) so that the
crosswalk maps old codes. See [Geography and boundary changes](geography.md#change-events).

A pack may include an optional **`changes.json`**
(`[{"change_type", "from_units", "to_units", "note"}]`). The loader records those
of its events that apply to the draft's base (their from-units still active
there) as explicit events in the geography draft. Each event is first **validated
with the same rules as the API's `record_geo_change`** (the loader uses the API's
own rules module), against the base version and the draft as loaded. An invalid
event **fails the geography load** with a message naming the event, before any
boundary file is uploaded: nothing is written for the geography. Fix
`changes.json` (or the units) and load again.
{% endhint %}

For development and test environments, the loader's **`--publish`** flag (chart
`geoSeed.autoPublish: true`) publishes the drafts it creates straight away. For
the geography it first validates the `changes.json` events as above, then completes
the lineage exactly as the API does on submit (automatic `CREATE`, `RETIRE`,
`RENAME`, `REPARENT` and `BOUNDARY_CHANGE` events), then publishes. Do not use it in
production: it bypasses approval.

| Loader flag | Environment | Chart value | Default |
|---|---|---|---|
| `--publish-initial` / `--no-publish-initial` | `PACK_PUBLISH_INITIAL` | `geoSeed.publishInitial` | on |
| `--publish` | `PACK_AUTO_PUBLISH` | `geoSeed.autoPublish` | off |
| `--owner-org` | `PACK_OWNER_ORG` | `geoSeed.ownerOrg` | none |
| `--domains` | `PACK_DOMAINS` | `geoSeed.domains` | chart: `agriculture` (loader alone: none); a domain the pack lacks is skipped with a warning |
| `--actor` | `PACK_ACTOR` | — | `country-pack-loader` |

Every load step is written to the change log with the loader as the actor
(`country-pack-loader`, a system actor with no display name, so its versions have
`*_by_name` `null`). The loader no longer calls the Audit Manager or WebSub itself:
the change log is the outbox, and the API's relay delivers these events like its
own (to the Audit Manager, and the `*.version.published` ones to WebSub) within
`catalogue_outbox_relay_seconds` (see [Audit](change-control.md#audit)). Version
numbers come from the same database functions as the API's and are never reused.
The old `--purge` flag is deprecated: published geography is immutable, so it now
only re-materialises the current-state geography tables.

### This replaces the old upsert behaviour

Previously the loader **upserted** in place and never deleted, so a reloaded MDS kept
codes the pack had dropped (for example the old `CROP_SEASON` values
`SEASON_SUMMER`, `SEASON_MONSOON` and `SEASON_WINTER`) with no way to mark them as
no longer in use. Now such values are **retired** in a new version: they stay
resolvable for records that hold them, and disappear from data-entry dropdowns once
the version is published.

Code lists that come from the remaining SQL seed fixtures (lists a pack does not
define) are inserted only if missing, versioned as version 1, and the current-state
tables are then re-materialised so a fixture can never bring back a retired value.

## Boundaries

Boundaries are uploaded to MinIO under **per-version, immutable keys**: version 1
on first load, the draft's version on later loads. Only levels whose file changed
are uploaded; an unchanged level keeps pointing at the earlier version's object.
Because version numbers are never reused, a new version's keys are its own; as a
safeguard the loader (like the API) refuses to write a key that another version
already records. Without an
object store endpoint the hierarchy still loads; only the map layer is missing.

The loader and the API each have their object store settings; keep them in step:

| | Loader (geo-seed Job) | API |
|---|---|---|
| Endpoint | `geoSeed.objectStore.endpoint` | `masterDataAPI.catalogue.boundaryStore.endpoint` |
| Bucket | `geoSeed.objectStore.bucket` | `masterDataAPI.catalogue.boundaryStore.bucket` |
| Public base URL | `geoSeed.objectStore.publicBaseUrl` | `masterDataAPI.catalogue.boundaryStore.publicBaseUrl` |
| Credentials | `geoSeed.objectStore.existingSecret` with `accessKeyKey` / `secretKeyKey` | `masterDataAPI.catalogue.boundaryStore.existingSecret` with the same keys |

The defaults are `http://commons-minio:9000`, bucket `openg2p-geo`, and the
`commons-minio` Secret (`root-user`, `root-password`).

See [Boundaries in MinIO, per version](geography.md#boundaries-in-minio-per-version).

## Licence

When the pack's `manifest.json` names a licence (`license`, and optionally
`license_uri`), the loader sets the geography's licence from it, deriving the URI of
a well-known licence (for example CC BY-IGO, CC0-1.0) from its label, unless an
administrator has already set one. The loader never changes visibility: everything
it loads stays **private** until someone marks it public (see
[Public catalogue](public-catalogue.md)). The loader needs catalogue schema 5.

## Migrating an existing MDS

An MDS installed before the catalogue already has data in `g2p_attributes`,
`g2p_attribute_values`, `g2p_geo_levels` and `g2p_geo_level_values`. On start, the
API's database migration (and the loader, before it loads) converts it:

* every existing list without a version becomes **version 1, `PUBLISHED`**, with
  exactly the values it has today;
* the existing geography becomes **geography version 1, `PUBLISHED`**;
* both get **`effective_from` 1970-01-01**: the data was in force before the
  catalogue existed, so an `as_of` read for any past date resolves to it;
* `list.version.migrated` and `geo.version.migrated` events are written to the
  change log, with `migration` as the actor (and delivered to the Audit Manager by
  the relay);
* the existing tables are left as they are; they are now the current published
  state and match version 1.

The migration is **idempotent**: it runs on every start and skips any list, and
the geography, that already has a version. It records the catalogue schema version
it created (`schema_version` in `g2p_catalogue_state`, currently 4) last, which is
what the geo-seed Job waits for.

Upgrading a catalogue created by an earlier release adds what is new in place. For
schema version 3 that is the `*_by_name` columns (display names next to the user
ids in `created_by`, `updated_by`, `submitted_by`, `decided_by`, and on releases
`created_by`, `members_set_by`, `published_by`, and on change events
`created_by`). Existing rows get the name the change log records for that user id,
where it has one, else `null` (the UI then shows the id). This one-time fill is the
only change ever made to published rows: it runs inside the migration's
transaction with the immutability trigger switched off for that table and on again
before the transaction ends, and writes only the new name columns.

Migrated lists keep whatever `owner_org` they have (none, unless set); the
geography version 1 has no `country`, no `owner_org` and **no boundary objects**.
The next pack load with an object store configured therefore finds the boundaries
missing and creates a geography draft that adds them under the new version's keys,
to be approved like any other draft.

{% hint style="info" %}
**Nothing changes for consumers on migration.** The same data is returned by the
same endpoints and is in the same tables. Consumers can start using versions (and
pinning version 1) whenever they are ready.
{% endhint %}

After migration, direct edits to the old tables are no longer the way to change
data: use drafts, the admin UI, or a pack load. A direct SQL change to the
current-state tables is overwritten the next time that list (or the geography) is
published or comes into effect.
