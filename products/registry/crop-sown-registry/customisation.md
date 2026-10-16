---
description: >-
  What a country or programme changes in the Crop Sown Registry — crops,
  seasons, activities, rules, scopes — and where each change is made.
---

# Customisation

A country sets the registry's lists, calendar, seasons, units and administrative levels. Much of that is data and configuration, but some of it is code. This page says which is which. The examples use the configuration that ships with the registry.

## Where a change is made

Work down the table. Make each change at the first layer that can carry it.

| Layer | Change it in | Then | Examples |
| --- | --- | --- | --- |
| **1. Install settings** | Helm values (Rancher form or YAML) | Upgrade the release | Hostname, sample data, ODK pull, partners allowed to search across farmers |
| **2. Master Data** | The country pack, or the Master Data admin UI | Nothing: read live | A new crop, variety, fertiliser, pest or damage cause |
| **3. Activity definitions** | `scripts/activity_definitions.py`, then regenerate the seed SQL | Rebuild the db-seed image | A new field on an activity, a new activity type, due dates, verification, indicators, the ODK mapping |
| **4. Other seed metadata** | SQL under `meta_data/` and `awe_meta_data/` | Rebuild the db-seed image | Cluster screens, cluster approvers, reporting views, registry name and theme |
| **5. Register configuration** | `meta_data/activity-config/CropSown.json` and its templates | Rebuild all images | Plausibility warnings, search fields, list columns, DCI records for crop seasons and summaries |
| **6. Data scopes** | `meta_data/data-scopes/*.json` | Rebuild all images | A new or narrower scope |
| **7. Domain code** | Python in `crop-sown-extension` | Rebuild all images | What identifies a crop season, the crop season status, the season summary and its windows, stored columns |

Paths are in the [repository](https://github.com/OpenG2P/crop-sown-registry), under `crop-sown-extension/src/openg2p_registry_crop_sown_extension/` unless they start with `scripts/`.

## Lists in Master Data

The registry keeps **no lists**. Every coded field is checked against Master Data when an entry is made. The lists are the **agriculture domain** of the country pack in use. ETH ships ([`openg2p-data`, `packs/ETH/domains/agriculture`](https://github.com/OpenG2P/openg2p-data/tree/develop/packs/ETH/domains/agriculture)). Master Data loads it when commons-services is installed with **Dataset Themes** `agriculture`.

| Used for | Lists |
| --- | --- |
| The crop season | `CROP_COMMODITY` (each crop in a `CROP_CATEGORY`), `CROP_SEASON`, `SEED_VARIETY` (each variety names its crop) |
| Plan and land preparation | `CROPPING_SYSTEM`, `LAND_PREPARATION_METHOD`, `IRRIGATION_SOURCE`, `IRRIGATION_METHOD`, `SOIL_FERTILITY` |
| Sowing | `SEED_TYPE`, `SEED_SOURCE`, `SOWING_METHOD`, `FERTILIZER_TYPE`, `FARM_MACHINERY` |
| Field visits, pests and damage | `CROP_GROWTH_STAGE`, `CROP_CONDITION`, `INFESTATION_TYPE`, `INFESTATION_AGENT`, `INFESTATION_SEVERITY`, `PEST_CONTROL_ACTION`, `CROP_DAMAGE_CAUSE` |
| Clusters | `CROP_COMMODITY`, `AGRO_ECOLOGICAL_ZONE`, `WATER_SOURCE` |

* **Codes carry their list's prefix:** `CROP_TEFF`, `SEASON_MEHER`, `SEV_HIGH`.
* **Crops follow the Ministry of Agriculture's crop variety list:** one `CROP_COMMODITY` entry per MoA crop (e.g. `CROP_BREAD_WHEAT`, `CROP_DURUM_WHEAT`), with its category and scientific name as typed attributes, plus `CROP_MALT_BARLEY` and `CROP_OTHER`. The former `CROP_WHEAT` is retired.
* **Adding a code** (a new crop, a new pest) is a change to the pack or in Master Data's admin UI. No registry change.
* **A variety** not in `SEED_VARIETY` is accepted with a warning. Every other list is strict: an unknown code is rejected.
* **Without the agriculture domain,** every activity is rejected on its crop code.
* **To freeze the lists** for a season, pin the registry to a catalogue release (**Pinned Catalogue Release**, `global.catalogueRelease`).

{% hint style="warning" %}
Four codes are also used **in code**: the season codes `SEASON_MEHER`, `SEASON_BELG`, `SEASON_IRRIGATION` (season summary windows) and the severity codes `SEV_LOW`, `SEV_MEDIUM`, `SEV_HIGH` (worst severity, and the "crops with pests" indicator). Renaming them in the pack needs a code change. A new season code works, but its summary covers the whole crop year.
{% endhint %}

The CI build checks that every list and code the activity definitions name is in the country pack in use (ETH ships). A pack for another country must carry the same lists.

## Country-specific settings

| Setting | Where it is set | To change it |
| --- | --- | --- |
| Lists (crops, seasons, fertilisers…) | Master Data | The country pack |
| Administrative levels (region, zone, woreda in the shipped configuration) | Activity definitions (the location is a `woreda`), indicators, reporting views | Activity definitions, indicators and the reporting view SQL |
| Calendar (the Ethiopian calendar ships): crop year, planned sowing date | Activity definitions | Activity definitions; the season windows in code |
| Calendar for "when it happened" in the staff portal | The registry platform's staff portal, for every activity register | A platform change |
| Season windows (Meher, Belg, Irrigation ship) | `SEASON_WINDOWS` in the domain service | Code |
| Units (hectares, quintals and birr per quintal ship) | Field names and labels in the activity definitions, columns and views | Code and seed; field names are part of the DCI records and data scopes |
| National ID (Fayda FAN, 12–16 digits, in the reference setup) | Activity definitions, register configuration, data scopes | Activity definitions and configuration |
| Plausibility limits (1.5 × plan, 150 qt/ha ship) | `CropSown.json` | Register configuration |

A deployment in another country is therefore a fork of this repository, not only a new country pack.

## Activities and fields

Activity types are defined in one Python file, `scripts/activity_definitions.py`. For each type it sets:

* the fields, as a JSON Schema, and which are required;
* which list each coded field is checked against, and how strictly;
* whether the activity can repeat, which activity must come first, and whether that is a warning or a block;
* when it falls due (sowing 0–60 days after the plan, harvest 90–180 days after sowing);
* how far back it can be dated (plan 365 days, sowing 180, harvest 120, field visits 60);
* whether a supervisor must verify it (sowing and harvest);
* which date fields use the configured calendar.

The same file holds the indicators, the ODK mapping and the participant roles (farmer, plot, development agent, cluster).

To change any of these:

```bash
# edit scripts/activity_definitions.py, then
python3 scripts/build_seed_sql.py           # regenerate meta_data/activity-metadata/*.sql
python3 scripts/build_seed_sql.py --check   # what CI runs
```

Commit both. Only the generated SQL ships. The script never runs in a deployment. On upgrade, db-seed updates the existing activity types and indicators in place.

{% hint style="info" %}
A new field that only sits in an activity's details needs nothing more. A field that must be searchable, summed in indicators or shown in the crop season status is a **stored column**: that is a code change to `register_domain/models/crop_sown.py` and the domain service.
{% endhint %}

## Plausibility warnings and screens

`meta_data/activity-config/CropSown.json` holds the register's configuration:

| Key | Sets |
| --- | --- |
| `rules` | The four plausibility warnings, as JSON Logic with a message. Add, remove or change limits here |
| `search_fields` | Fields staff can search on: farmer ID, FAN, plot, crop, cluster |
| `ui_hints` | Summary fields, crop season list columns, fields carried from row to row in a batch, search placeholders |
| `final_on_period_lock` | Which summaries become final when a period is locked (`FARMER_SEASON_SUMMARY`) |
| `formats.dci` | The DCI record types and templates for crop seasons and season summaries |

The file is read from the extension package, so a change needs new images. The format is described in the [activity register design](../registry/design/activity-register.md).

## Clusters

* **Approvers.** `awe_meta_data/` loads two two-stage policies, one for new clusters and one for changes. Both name demo users, `alex.carter` then `nina.patel`. Replace them with your officials, or with role-based rules, before going live.
* **Cluster ID.** Ten digits after `CL-`, from the ID generator pool `cluster` (`registry.idgenerator.idGenerator.appConfig.idTypes.cluster.idLength`).
* **Screens.** The Cluster register's screens are seed SQL that db-seed inserts only once. A change to an installed registry needs an upgrade script, like the one in `meta_data/zz-upgrades/`.

## Data scopes

Scopes are defined in `meta_data/data-scopes/`: `10_crop_sown.json` for crop data, `20_cluster.json` for clusters. A scope is a named list of fields, independent of the DCI layout. See [Data scopes](../registry/design/data-scopes.md) for the format and the rules.

* **Never rename or reuse a scope name.** Consents and Consent Manager policies refer to it.
* **Narrowing** a scope is safe. **Widening** it does not reach consents given before.
* The consent data controller is the registry variant, `crop-sown-registry`. Changing it (`global.consentDataController`) changes every scope ID.

## Branding and languages

The registry name and logo are in `meta_data/registry-configurations/g2p_registry_configuration.sql`. It uses the factory OpenG2P theme. It ships one language, English.

## What not to change

* **The register IDs and mnemonics** (`CropSown`, `Cluster`). Metadata, data scopes, AWE bindings and partner requests refer to them.
* **The four fields that identify a crop season** (plot, crop year, season, crop). Changing them splits existing crop seasons.
* **Field names used in DCI records and scopes** once partners rely on them. Add new names instead.
