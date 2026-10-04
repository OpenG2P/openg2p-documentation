---
description: >-
  The Crop Sown Registry (CSR): a registry with an activity register of crop
  seasons — context, activity types, code lists, projection, indicators, the
  farmer's season summary, clusters and channels.
---

# Crop Sown Registry

The Crop Sown Registry (CSR) records what each farmer plans, prepares, sows, observes and harvests, plot by plot and season by season. It is a registry instance whose data is an **activity register** (see [activity register](activity-register.md)), plus a [Cluster register](#cluster-register) for clusters. Crop seasons have no functional IDs and no change requests.

It is a thin extension of the registry platform, packaged like the Farmer Registry: [github.com/OpenG2P/crop-sown-registry](https://github.com/OpenG2P/crop-sown-registry). How it is built, its sample data and its DCI records are in [Crop Sown Registry (as built)](../implementation/crop-sown-registry.md).

The Crop Sown Registry is **independent**. It shares data with the Farmer Registry (farmer and plot IDs), not code. If the Farmer Registry itself is to keep crop seasons against its Land records, that is a register in the Farmer Registry's own extension; see [where an activity register lives](activity-register.md#where-an-activity-register-lives).

## Crop season: the activity context

**One context is one crop on one plot in one season:**

```
<plot_id>|<crop_year>|<season>|<crop>        e.g.  LND-7781|2019|SEASON_MEHER|CROP_TEFF
```

* **Intercropping** is two contexts on the same plot.
* **The subject** is the farmer (Farmer Registry ID). The Fayda FAN is carried alongside.
* **The plot** is a Farmer Registry land record. The plot, farmer and DA are held by other registries, so they are checked for **format only** and never block an entry.
* **Entities first** ([register model design](register-model-design.md#participants-and-entities-first)): the farmer and plot are registered in the Farmer Registry before crop activities are recorded. Temporary plot IDs (`TMP-…`) are no longer accepted; a plot found in the field is registered first.
* **Participants:** every activity records its participants in typed roles: farmer (primary), plot and development agent (Farmer Registry and other systems), and cluster (the Cluster register here). Activities can be searched by participant.
* **A changed crop** is a new crop season that names the one it replaces (`replaces_crop_season_id`). The old season is closed, and each points to the other.
* **The location** is the plot's **woreda**, chosen from the catalogues' geography (MDS). It is required when a crop season is planned or sown; later activities take it from their crop season. Every activity stores it with its zone, region and country as named levels, so every figure can be rolled up by level. The registry can't read the plot's location from the Farmer Registry, which may be on another instance, so the woreda is entered.

## Activity types

| Type | Records | Rules |
| --- | --- | --- |
| `PLANNED` | Variety, planned area, cropping system, planned sowing date (Ethiopian calendar), planned seed and fertilisers, expected yield | Once per crop season |
| `LAND_PREPARED` | Method (oxen / tractor / manual / zero tillage), area, irrigation source and method, soil fertility | Once; expected after `PLANNED` (warning) |
| `SOWN` | Area sown, variety, seed type and source, seed kg, sowing method, fertilisers (type + kg), compost/manure, machinery, geo-tagged photo | Once; expected after `PLANNED` (warning); due 0–60 days after planning; **verified by a supervisor** |
| `CLUSTER_ENROLLED` | Cluster ID only; the cluster must exist in the Cluster register | Once |
| `GROWTH_OBSERVED` | Growth stage, crop condition, area under crop, estimated yield | Repeatable; **requires `SOWN`** |
| `INFESTATION_REPORTED` | Pest / disease / weed, agent (e.g. fall armyworm, wheat rust, striga), severity, area, % damage, action, pesticide | Repeatable; **requires `SOWN`** |
| `DAMAGE_REPORTED` | Cause (drought, flood, hail, frost, wind, wildlife), area, % loss | Repeatable; **requires `SOWN`** |
| `HARVESTED` | Area harvested, quantity (quintals), yield (computed), post-harvest loss, stored / sold / consumed / kept as seed, sale price | Once; **requires `SOWN`**; due 90–180 days after sowing; **verified by a supervisor** |

**Where the fields come from:** the crop-sown sample registry, extended from:

* FAO's World Programme for the Census of Agriculture 2020 (crop module and crop-loss causes);
* Ethiopia's CSA Agricultural Sample Survey (Meher/Belg seasons, UREA/DAP/NPS fertilisers, quintals).

**Plausibility warnings** (never blocking):

* sown area more than 1.5 × the planned area;
* observed or harvested area larger than the sown area;
* yield above 150 qt/ha;
* stored + sold + consumed + seed quantities adding up to more than the harvest.

## Code lists

**All code lists live in the catalogues (MDS).** The Crop Sown Registry keeps none of its own. The registry platform checks every coded field against Master Data at the time of writing, the same way the Farmer Registry's dropdowns and validation read their lists.

The lists are the **agriculture domain of the Ethiopia country pack** (`openg2p-data`, `packs/ETH/domains/agriculture`). Master Data loads that domain when installed with `geoSeed.domains: [agriculture]` (see [deployment](../guides/deployment.md)).

| Used for | Lists |
| --- | --- |
| The crop season | `CROP_COMMODITY`, `CROP_SEASON` (Meher, Belg, Irrigation), `SEED_VARIETY` |
| Planning and land preparation | `CROPPING_SYSTEM`, `LAND_PREPARATION_METHOD`, `IRRIGATION_SOURCE`, `IRRIGATION_METHOD`, `SOIL_FERTILITY` |
| Sowing | `SEED_TYPE`, `SEED_SOURCE`, `SOWING_METHOD`, `FERTILIZER_TYPE`, `FARM_MACHINERY` |
| Clusters | `AGRO_ECOLOGICAL_ZONE`, `WATER_SOURCE` |
| Observation, infestation and damage | `CROP_GROWTH_STAGE`, `CROP_CONDITION`, `INFESTATION_TYPE`, `INFESTATION_AGENT`, `INFESTATION_SEVERITY`, `PEST_CONTROL_ACTION`, `CROP_DAMAGE_CAUSE` |

* **Codes carry their list's prefix,** such as `CROP_TEFF`, `SEASON_MEHER` and `SEV_HIGH`.
* **Adding or changing a code** is a change to the country pack, not to the registry.
* **Without the agriculture domain in Master Data,** every activity is rejected on its crop code.

## Crop season status (projection)

One row per crop season:

* furthest **stage** reached (planned → land prepared → sown → growing → harvested);
* planned area and date, expected yield;
* area sown, sowing date, seed type, whether sowing was verified;
* whether the harvest was verified;
* the crop season it replaced, or was replaced by;
* latest growth stage and condition;
* infestations (count, worst severity), damage reports (count, worst % loss);
* area harvested, quantity, yield, harvest date;
* activities awaiting verification.

## Indicators

* area sown by crop;
* quantity harvested by crop;
* average yield by crop;
* crops by stage;
* farmers reporting;
* crops with infestations.

Each is grouped by crop year and season.

**Indicators by geographic level:**

* area sown by region, by zone and by woreda (with crop);
* quantity harvested by region;
* average yield by region;
* farmers reporting by woreda.

They sit alongside the indicators by crop year, season and crop. The reporting views for Superset and Insights are listed in [Crop Sown Registry (as built)](../implementation/crop-sown-registry.md#reporting-views).

## Farmer's season summary

For each farmer, crop year and season, the Crop Sown Registry keeps a summary across all their plots and crops. It is an aggregate, `FARMER_SEASON_SUMMARY`, with period key `<crop year>|<season>`. It holds:

* crop seasons and plots;
* planned, sown and harvested area;
* quantity harvested and yield;
* infestations and damage reports;
* a breakdown by crop.

The period is the season's window in the Ethiopian crop year, following the CSA Agricultural Sample Survey:

| Season | Window | Why |
| --- | --- | --- |
| Meher | Meskerem – Yekatit (Sep – Feb) | Meher crops are harvested September to February |
| Belg | Megabit – Pagume (Mar – Aug) | Belg crops are harvested March to August |
| Irrigation | Hidar – Ginbot (Nov – May) | The dry season |

The summary's location is the geographic levels all of the farmer's plots share, e.g. one woreda, or only a zone when the plots span woredas. Programmes read it through DCI with record type `spdci-extensions-agri:ActivityAggregate`, keyed by farmer ID.

The summary is recomputed from the crop-season projections after every change, including corrections and voids, and each value is kept in its history. It becomes **final** when the season is locked (see [final figures](../implementation/registry-platform.md#final-figures)).

## Cluster register

Clusters are **entities** in their own register in this registry, not activity data:

* **fields:** Cluster ID, programme cluster code (optional, e.g. `CL-ET0406-001`), name, crop, woreda, agro-ecological zone, water source, area, smallholders, year established, coordinator;
* **identity:** the Cluster ID is the record's functional ID, **generated** by the ID generator when the registration is approved (pool `cluster`, prefix `CL-`, e.g. `CL-4729318560`); staff never type it. The programme's own code is kept, if known, in the searchable **Programme Cluster Code** field. Activities refer to a cluster by its Cluster ID;
* **changes:** created through an intake form and changed through change requests, both approved in AWE, like the Farmer Registry's registers.

A plot joins a cluster with a `CLUSTER_ENROLLED` activity. Cluster totals are derived from the plots' activities.

## Channels

* **Staff portal:** single entry or batch.
* **Partner systems:** e.g. a cooperative, via the signed partner API. A partner can correct (supersede or void) only what it submitted.
* **ODK Central:** a `crop_sowing` form whose submissions are pulled every few minutes. The ODK instance ID is the idempotency key; photos are stored as documents; failed submissions are kept for review.

## Sharing with partners (DCI)

Partners read three record types by farmer ID: the farmer's **activities** (`spdci-extensions-agri:CropActivity`), each **crop season's current state** (`spdci-extensions-agri:CropSeason`, what a subsidy or loan decision reads) and the farmer's **season summaries** (`spdci-extensions-agri:ActivityAggregate`). The record types, consent scopes, filters and examples are in [Crop Sown Registry (as built)](../implementation/crop-sown-registry.md#dci-records).
