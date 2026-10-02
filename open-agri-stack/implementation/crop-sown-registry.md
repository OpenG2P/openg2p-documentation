---
description: >-
  How the Crop Sown Registry is built: packaging, activity definitions, the
  Cluster entity register, reporting views, sample data, and the DCI records
  partners read.
---

# Crop Sown Registry (as built)

The design of the Crop Sown Registry (CSR) — the crop-season context, activity types, code lists, projection, indicators, season summary, clusters and channels — is in [Crop Sown Registry](../design/crop-sown-registry.md). This page covers how it is built and what partners read from it.

## Packaging

* **Repository:** [OpenG2P/crop-sown-registry](https://github.com/OpenG2P/crop-sown-registry). A thin extension of the registry platform, packaged like the Farmer Registry: its own images (staff API, partner API, Celery, db-seed), each built `FROM` the matching registry-platform image.
* **Chart:** `openg2p-crop-sown-registry` (Rancher: "OpenG2P Crop Sown Registry"), a values overlay over the `openg2p-registry` chart with no templates of its own. It sets the variant (`global.registryVariant: crop-sown-registry`, which is also its default consent data controller), the images, the seed switches and the ODK and sample-data settings. See [deploying Open Agri Stack](../guides/deployment.md#crop-sown-registry).
* **No ID generator:** CropSown is an activity register and a cluster's code is entered by staff, so no functional IDs are issued.
* **Code lists:** none are seeded or copied; every coded field is checked live against Master Data's agriculture domain.

**One file for the definitions.** The activity types, indicators and ODK mapping are **defined in one file**, `scripts/activity_definitions.py`. The seed SQL is generated from it (`scripts/build_seed_sql.py`). The script is a developer tool and never runs in a deployment. CI checks two things:

* the committed SQL matches the definitions;
* every list and code the definitions use exists in the Ethiopia pack.

## Phase 1 changes

Phase 1 of the [register model design](../design/register-model-design.md#phase-1-built), in the Crop Sown Registry:

* **Cluster entity register** with AWE approval and sample clusters (below);
* **typed participant roles:** farmer (primary), plot, development agent, cluster;
* **entities first:** temporary plot IDs (`TMP-…`) are no longer accepted; the cluster must exist (strict), farmer and plot are format-checked;
* **crop-change link** (`replaces_crop_season_id`) in the projection, the reporting view, DCI and the staff UI;
* **verification in DCI:** `verification_status` on activities; `sowing_verified`, `harvest_verified` and `pending_verification_count` on the crop season;
* **farmer ID linked to the Fayda FAN** for consent subject checks (`subject_id_fields`): a consent whose subject is the farmer's FAN passes the subject check when the search is by farmer ID;
* **final season summaries** on period lock (`is_final` in DCI), and searches across farmers for allow-listed partners;
* **sample crop seasons** from Master Data's sample people;
* a partner correction in the smoke test (`scripts/e2e_smoke.py`).

## Cluster register

Clusters are **entities** in their own register:

* **fields:** code (e.g. `CL-ET0406-001`), name, crop, woreda, agro-ecological zone, water source, area, smallholders, year established, coordinator;
* **changes:** created through an intake form and changed through change requests, both approved in AWE, like the Farmer Registry's registers. db-seed loads the Cluster approval policies into the shared AWE, and keycloak-init creates the approvers they name.

`CLUSTER_ENROLLED` carries only the cluster ID, and the cluster must exist. Cluster totals are derived from the plots' activities.

## Reporting views

In the registry's database, for Superset and Insights:

| View | One row per |
| --- | --- |
| `csr_rpt_crop_season` | crop season, with region, zone and woreda codes and names |
| `csr_rpt_crop_performance_region` | crop year, season, region, crop |
| `csr_rpt_crop_performance_zone` | crop year, season, zone, crop |
| `csr_rpt_crop_performance_woreda` | crop year, season, woreda, crop |

* The performance views count crop seasons, farmers and plots; sum planned, sown and harvested area and production; compute yield as production ÷ harvested area; and count infested and damaged crop seasons.
* They are plain views over the crop-season projection, which the platform keeps current, so they need no refresh.
* The Superset/Insights dashboards on them are not built ([open items](../open-items/README.md)).

## Sample data

Sample data is **off by default**. For a demo, turn on two Rancher questions:

* **Load Sample Data** (`registry.dbSeed.loadSampleData`) loads the sample clusters;
* **Load sample crop seasons** (`REGISTRY_CELERY_WORKERS_ACTIVITY_LOAD_SAMPLE_DATA`) loads the crop seasons, and is shown only when the first is on.

The crop seasons need the sample clusters, so the second question alone loads nothing. They also need Master Data's sample people (the country pack's samples).

* **Clusters:** db-seed loads two sample clusters.
* **Crop seasons:** the platform's sample task records them once, through the normal write path, after the activity types and clusters are loaded.
  * Farmers are the adults among Master Data's sample people, with the Farmer Registry's IDs: `ETH-IND-0007` → `FR-0007`.
  * Plots are `LAND-0007-1` (every farmer) and `LAND-0007-2` (every third), in the person's woreda.
  * The Farmer Registry numbers sample lands the same way, so a demo of both shows the same farmers and plots. Neither reads the other.
* **What they cover:**
  * Meher 2018 (complete, with an infestation for some);
  * Belg 2018 (complete for some farmers, with a drought);
  * Meher 2019 (growing, so harvests are due on the work list).

  Most sowings and harvests are verified; every fifth farmer's are pending. One sowing is corrected, and the farmers in a sample cluster's woreda are enrolled in it.

## DCI records

A DCI search with `reg_type = CropSown`, by farmer ID, returns one of three record types:

| `reg_record_type` | Returns | Used for |
| --- | --- | --- |
| `spdci-extensions-agri:CropActivity` | The farmer's current activities (plans, sowings, observations, harvests), each with its verification status | Evidence, audit |
| `spdci-extensions-agri:CropSeason` | Each crop season's current state: stage, planned and sown area, seed type, whether sowing and harvest were verified, activities awaiting verification, growth and infestation status, harvest, yield, location, and the season it replaced or was replaced by | **Decisions** such as a fertiliser subsidy or a loan |
| `spdci-extensions-agri:ActivityAggregate` | The farmer's season summaries across plots and crops | Decisions on the farmer as a whole |

All three share one set of consent scopes, the record's top-level keys:

* `activity` (activities only)
* `crop_season`
* `measures`
* `farmer_reference`
* `location`

A partner's policy therefore covers all three record types the same way.

**Querying.** Every search is synchronous (`/dci/registry/sync/search`).

* **By farmer ID** (`idtype-value`): every crop season or summary of the farmer.
* **Filtered** (`expression`): `subject_id` (the farmer ID) plus filters.
  * Activities can be filtered by any plain field: `activity_type`, `occurred_at`, `verification_status`, `crop`, `plot_id`…
  * Crop seasons can be filtered by any plain projection column, e.g. `crop_year`, `season`, `crop`, `stage`.
  * Summaries can be filtered by `aggregate_type`, `period_key`, `crop_year`, `season` and `is_final`.
* **Final summaries:** a farmer's season summary becomes final when a period lock (all activity types) covers the season's window and its activities are processed (`crop_season.is_final`). Plans are often made before the window, so lock from the planning start, or a late change to a plan makes the summary provisional again.
* **Across farmers:** a programme system the registry operator allow-lists can search summaries without a farmer ID, e.g. every final Belg 2018 summary for a subsidy run. See [aggregates across subjects](registry-platform.md#dci-search-of-activity-registers).
  * The operators are those of entity searches (`$eq`, `$in`, `$gte`…).

Results come newest first, so "the farmer's last 10 activities" needs no filter: `page_size: 10`. For example, "wheat sown by FR-0007 in Meher 2019" is the summary for `crop_year: 2019`, `season: SEASON_MEHER`, read at `measures.by_crop.CROP_WHEAT.area_sown_ha`. See the [composite worked example](../design/use-case-composite.md#worked-example-wheat-sown-by-a-farmer-this-season).

The `loan-profile` use case reads the crop seasons and the season summaries; its consent grant for this registry is `farmer_reference`, `crop_season`, `measures`, `location` ([composite configuration](../guides/composite-configuration.md#the-loan-profile-use-case)).
