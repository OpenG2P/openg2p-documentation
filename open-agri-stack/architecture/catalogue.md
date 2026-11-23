---
description: >-
  The catalogue in Agri Stack: where it runs, the agricultural datasets it
  holds, who reads it, versions, who owns each dataset, and standards
---

# Catalogue

The **catalogue** is Agri Stack's common vocabulary: the codes every registry and service uses for crops, seed varieties, farm inputs, livestock, land and locations. A crop recorded as `CROP_TEFF` in the Crop Sown Registry means the same crop in the Farmer Registry, in a report and to a partner.

The catalogue is served by the platform's [Master Data Service](../../platform/platform-services/master-data-service/README.md) (MDS). How MDS works (datasets, versions, approvals, the public API) is documented there; this page says how Agri Stack uses it.

{% hint style="info" %}
**Three different "catalogues".** This page is about **reference data** (codes and their labels). A registry's [data scope catalogue](../../products/registry/registry/design/data-scopes.md) (the groups of fields a consent can grant) is the registry's own, not in MDS. Partner Management's [catalogue sources](../../platform/platform-services/partner-management/functional-specifications.md#catalogue-sources) (the use cases a policy can grant) come from the Composite.
{% endhint %}

## Where it runs

**Today, one catalogue per install.** The Exchange and each department each run their own MDS, in Commons Services, loaded from the **same country pack version**. The codes agree because the pack is the same, not because one catalogue is read by all ([Architecture](README.md)).

* A code added in one install's admin UI exists only there until the pack is updated and reloaded everywhere. Add shared codes **in the pack**.
* A department may add datasets only it uses.

**Later, one central catalogue** at the Exchange, read by the departments through its API (cached and pinned to a release) or mirrored, with each department's own datasets under its own publisher. See the [roadmap](../roadmap/README.md#phase-3-many-departments-other-stacks-conveniences).

## What it holds for agriculture

A country pack has core datasets and **themes**; the agriculture theme holds the farming datasets ([Country Packs](../../platform/platform-services/master-data-service/country-packs.md)). In the Ethiopia pack:

| Area | Datasets (examples) |
| --- | --- |
| **Crops and seasons** | `CROP_COMMODITY`, `CROP_CATEGORY`, `CROP_SEASON`, `CROP_GROWTH_STAGE`, `CROP_CONDITION`, `CROP_DAMAGE_CAUSE`, `CROP_END_USE`, `CROPPING_SYSTEM` |
| **Seeds and sowing** | `SEED_VARIETY`, `SEED_TYPE`, `SEED_SOURCE`, `SOWING_METHOD` |
| **Farm inputs** | `FERTILIZER_TYPE`, `FARM_MACHINERY`, `PEST_CONTROL_ACTION`, `IRRIGATION_METHOD`, `IRRIGATION_SOURCE` |
| **Pests and disease** | `INFESTATION_TYPE`, `INFESTATION_AGENT`, `INFESTATION_SEVERITY` |
| **Land** | `LAND_OWNERSHIP_TYPE`, `LAND_SIZE_UNIT`, `CURRENT_LAND_USE`, `SOIL_FERTILITY`, `AGRO_ECOLOGICAL_ZONE` |
| **Livestock** | `LIVESTOCK_TYPE`, `LIVESTOCK_BREED`, `LIVESTOCK_SYSTEM` |
| **Farmers** | `FARMING_TYPE`, `FARMER_CLUSTER_ROLE`, `SOURCE_OF_INCOME` |
| **Geography** | Regions, zones and woredas with their P-codes and boundaries |
| **Data sharing** | `CONSENT_PURPOSE`, `SUBJECT_ID_TYPE` (core datasets): the purposes and subject ID types a policy may name |

The full lists are in the pack. The planned [Livestock Registry](../roadmap/livestock-registry.md) will need a vaccine (and treatment) dataset, not in the pack yet. A new dataset is a pack change, not a code change.

## Who reads it

| Reader | What it reads | How |
| --- | --- | --- |
| **Farmer Registry** | Datasets for its fields; geography for addresses | Staff portal dropdowns and cascading address fields, at run time ([country data](../../products/registry/registry/deployment-and-extension/country-data-and-seeding.md#how-the-registry-reads-mds)) |
| **Crop Sown Registry** | Crops, seasons, pests, inputs, geography | Every activity's codes are checked against the catalogue (reference rules: strict or warn), and the activity records the catalogue versions it used ([customisation](../../products/registry/crop-sown-registry/customisation.md)) |
| **Partner Management** | `CONSENT_PURPOSE`, `SUBJECT_ID_TYPE` | The policy form's lists ([Master Data datasets](../../platform/platform-services/partner-management/functional-specifications.md#master-data-datasets)) |
| **Reporting** | The geography levels | Read at install, to generate the registries' [reporting views](../../platform/platform-services/reporting-and-analytics/reporting-views.md) |
| **Composite** | Nothing | It passes the registries' codes through unchanged |
| **Partners, OAN, agritechs** | The codes in the answers they get, and their labels | The [public catalogue](#public-catalogue), or the lists shared with them |

**Records hold codes, never labels.** A partner that gets `CROP_TEFF` in a loan profile looks up its label in the catalogue, at the version it needs.

## Versions

Each dataset has versions; a registry reads the latest unless pinned ([For Consumers](../../platform/platform-services/master-data-service/consumers.md)).

* **Pinning a season's lists:** a registry can read every list at one **catalogue release** with the Helm value `global.catalogueRelease` (empty: the latest). The Crop Sown Registry uses it to freeze its lists for a season.
* **Activities record their versions;** entity registers (the Farmer Registry) do not yet ([roadmap](../roadmap/README.md#phase-2-farmers-partners-and-the-open-agri-network)).
* **A code is never deleted.** A retired code stays valid on the records that hold it and is no longer offered for new ones.
* **Codes used in code:** a few codes are read by the Crop Sown Registry's code (season and severity codes); renaming them needs a code change ([customisation](../../products/registry/crop-sown-registry/customisation.md)).

## Who owns each dataset

Each dataset names its **publisher**: the department responsible for it (for example, agriculture for crops and inputs, the livestock department for livestock, the mapping agency for geography). Changes are approved before they are published ([Change Control](../../platform/platform-services/master-data-service/change-control.md)).

Today anyone with the catalogue permissions in an install can edit any dataset; edit rights per publisher are on the [roadmap](../roadmap/README.md#phase-2-farmers-partners-and-the-open-agri-network). Which codes a country uses is the system integrator's and the departments' work, not OpenG2P's.

## Public catalogue

Datasets marked public can be read anonymously, with downloads, DCAT and SKOS, so agritechs, OAN providers and open-data portals use the same codes ([Public Catalogue](../../platform/platform-services/master-data-service/public-catalogue.md)). Commons Services serves it on its own host, `catalogue.<base domain>`, on the internal gateway; publishing it on the internet, and which datasets go public, is each department's decision ([Production](../deployment/production.md#public-catalogue-master-data)).

## Standards

The codes are the **country's own** (`CROP_TEFF`, `SEASON_MEHER`); geography uses OCHA P-codes. International classifications (AGROVOC, FAO crop classifications, EPPO, …) are optional **mappings** on a dataset, not its codes. Beckn is not used for reference data ([design decision 7](../design-decisions.md#7-reference-data-in-mds-beckn-only-at-the-network-layer)). Details and open choices: [Standards](standards.md#catalogues-and-reference-data).
