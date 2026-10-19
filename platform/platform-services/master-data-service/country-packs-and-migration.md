---
description: >-
  How a country pack loads into MDS (version 1 on first load, drafts on later
  loads), the loader settings, licences, and how an MDS installed before
  versioning is migrated
---

# Country Packs and Migration

A **country pack** is a folder of a country's data: its geography, its datasets
and a few sample people. What a pack contains, where packs live and how to build
one are on [Country Data Architecture](../../country-data-architecture.md). This
page is about what happens when a pack is loaded into MDS.

The rule is: **a pack never overwrites published data.**

The loader runs as a Job in the MDS chart, after the API has prepared the
database. It handles each dataset, and the geography, on its own.

## First load: version 1, published

A dataset that does not exist yet, or the geography when it has no version yet,
is loaded as **version 1** and **published at once**. There is nothing published
to protect yet, so no approval is needed. Registries can use the data immediately.

This applies on a fresh install, and later to any dataset that appears for the
first time (a dataset added in a newer pack, or a theme turned on after install).
Labels in every language, codes, typed fields, schemas, descriptions and the
publisher are kept as the pack gives them. Each dataset gets its theme from the
pack folder it came from (Core, or the theme's name, such as Agriculture).

## Later loads: drafts, not overwrites

When a dataset or the geography already has a published version, the loader
compares the pack with it:

| Pack compared with the published version | What the loader does |
|---|---|
| Unchanged | Nothing. Re-running the loader is safe |
| Different | Creates a **draft**: new entries or units added, changed ones updated, missing ones **retired** (never deleted). For geography, changed boundary files are uploaded to the draft |
| An open draft already exists | Skips it |

The drafts are left as **drafts, not submitted**. Someone reviews the difference,
submits it and has it approved like any other change (see
[Change Control and Approvals](change-control.md)). Nothing consumers read
changes until then. The steps are in the
[Admin Guide](admin-guide.md#load-a-newer-country-pack-version).

Things to know:

* **Codes are fixed once published.** A pack that gives a published entry a new
  code stops that dataset's load with a clear error. To recode in a pack, give the
  new code a new entry id and drop the old entry; the loader retires the old one
  and adds the new one. See
  [Codes are fixed once published](concepts.md#codes-are-fixed-once-published).
* **References between datasets.** An entry that refers to a code that exists
  only in another dataset's draft cannot be approved until that draft is
  published. Approve the referenced dataset first (for example, crops before seed
  varieties).
* **A pack is a snapshot.** It says which units exist, not that one was split
  into two. On submit MDS adds automatic change events, but they do not link old
  units to new ones. Record the real events (split, merge, recode, …) in the draft
  before submitting, or ship them in the pack's optional **`changes.json`**; the
  loader checks them with the same rules as the API and stops the geography load
  if one is invalid. See [Geography: change events](geography.md#change-events).

Earlier loaders updated data in place and never removed anything, so entries a
pack had dropped stayed in use. Now they are **retired** in a new version: they
still resolve for old records and disappear from data-entry dropdowns.

## Loader settings

| Chart value (`geoSeed.`) | Default | What it does |
|---|---|---|
| `countryPack` | `XKM` (MDS chart), `ETH` (`commons-services`) | Which pack to load |
| `load.geo`, `load.codelists`, `load.samples` | all on | Which parts to load |
| `domains` | `agriculture` | Themes to load besides the core datasets. A theme the pack lacks is skipped with a warning |
| `publishInitial` | on | Publish a first load as version 1. Off: leave it as a draft for approval |
| `autoPublish` | off | Publish the drafts of later loads at once, without approval. **Development and test only** |
| `ownerOrg` | none | Publisher recorded on what the loader creates |

The loader has a matching command-line flag and environment variable for each
(see the chart's `values.yaml`). Every load step is written to the change log with
the loader (`country-pack-loader`) as the actor, and delivered to the Audit
Manager and WebSub like any other change.

Boundary files go to the object store; see
[Geography: boundaries per version](geography.md#boundaries-per-version) and
[Deployment](deployment.md#object-store-for-boundaries).

## Licence

When the pack's manifest names a licence, the loader sets the geography's licence
from it, unless an administrator has already set one. The loader never makes
anything public: everything it loads stays **private** until someone marks it
public (see [Public Catalogue](public-catalogue.md)).

## Migrating an existing MDS

An MDS installed before versioning already has datasets and geography. On start,
MDS converts them:

* every existing dataset becomes **version 1, published**, with exactly the
  entries it had;
* the existing geography becomes **geography version 1, published**;
* both are **effective from 1970-01-01**, so a read as of any past date finds them;
* a migration event is written to the change log for each.

The migration runs on every start and skips anything that already has a version.
Later schema upgrades add new fields in place (theme, visibility, licence, display
names of who made each change).

The migrated geography has **no boundary files**. The next pack load with an
object store configured adds them in a geography draft, to be approved like any
other.

{% hint style="info" %}
**Nothing changes for consumers on migration.** The same endpoints return the same
data. Consumers can start pinning versions when they are ready.
{% endhint %}

After migration, change data through drafts, the Admin UI or a pack load, not by
editing the database. A direct database change is overwritten the next time that
dataset or the geography is published.
