---
description: >-
  The Crop Sown Registry's data scopes: their IDs, what each covers, how to
  read the live catalogue, and the rules for changing them.
---

# Data Scopes

A partner's consent and its access policy in Partner Management name the registry's [data scopes](../registry/design/data-scopes.md): named groups of fields that can be released.

## Scope IDs

A scope ID is `<data controller>.<scope>`. The data controller is the registry's **Consent Data Controller** (`global.consentDataController`), by default the registry variant: `crop-sown-registry`. So `crop_season` is `crop-sown-registry.crop_season`. This is the **Data controller** of a scope policy in Partner Management.

## The scopes

| Scope ID | Label | Covers |
| --- | --- | --- |
| `crop-sown-registry.crop_season` | Crop season | Which crop on which plot in which season: plot, crop year, season, crop, variety, cluster; a crop season's stage and status; a summary's period and whether it is final |
| `crop-sown-registry.measures` | Crop measures | Areas, quantities, yields, dates, seed type, crop condition, pest and damage counts, verification flags, each activity's details, a summary's figures |
| `crop-sown-registry.farmer_reference` | Farmer reference | Farmer ID and national ID. More sensitive |
| `crop-sown-registry.location` | Location | The administrative areas, and an activity's GPS point. More sensitive |
| `crop-sown-registry.activity` | Activity details | An activity's ID, type, dates, channel and verification status |
| `crop-sown-registry.cluster_profile` | Cluster profile | Cluster ID, programme code, name, crop, year established |
| `crop-sown-registry.csr_cluster_details` | Cluster details (with coordinator contact) | The cluster's details section, including the coordinator's name and phone |
| `crop-sown-registry.csr_cluster_location_resources` | Cluster location and resources | The cluster's district, GPS point, area, smallholders, agro-ecological zone and water source |

* **One scope, three record types.** Each scope covers the matching fields of activities, crop seasons and season summaries; records are cut down to the consented fields before they are rendered.
* **Cluster scopes are not searchable yet.** They are in the catalogue, but the registry ships no DCI template for the Cluster register: a DCI search on `Cluster` fails, and partners see clusters only as the Cluster ID on activities and crop seasons.

## The live catalogue

This table is what ships. An install's catalogue, with each scope's fields, is served by its partner API:

* `POST /partner/data_scopes`, signed by a partner onboarded in Partner Management;
* `GET /partner/data_scopes`, unsigned, while **Allow Unsigned Read of Data Scope Catalogue** is on (the default).

## Where they are defined

`crop-sown-extension/src/openg2p_registry_crop_sown_extension/meta_data/data-scopes/` in [crop-sown-registry](https://github.com/openg2p/crop-sown-registry): `10_crop_sown.json` (crop data) and `20_cluster.json` (clusters). The format: [data scopes](../registry/design/data-scopes.md).

## Changing them

* **Never rename or reuse a scope.** Consents and access policies refer to it.
* **Narrowing** a scope is safe. **Widening** it does not reach consents given before.
* **Changing the data controller** changes every scope ID: every consent and policy naming the old IDs stops matching.
