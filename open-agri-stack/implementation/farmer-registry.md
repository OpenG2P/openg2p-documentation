---
description: >-
  What changed in the Farmer Registry for Open Agri Stack: declared main crops
  instead of the Crops tab, sample lands numbered like the Crop Sown Registry,
  and the farmer ID in the DCI record.
---

# Farmer Registry Changes

The [Farmer Registry](../../products/registry/farmer-registry/README.md) ([OpenG2P/farmer-registry](https://github.com/OpenG2P/farmer-registry)) holds the entities the other registries refer to: farmers, their land, households and (for now) livestock. Its deployment, seeding and chart are documented in [Farmer Registry → Deployment](../../products/registry/farmer-registry/deployment/README.md). For Open Agri Stack it changed in three ways.

## Declared main crops replace the Crops tab

Decided in the [register model design](../design/register-model-design.md#decisions): the Farmer Registry keeps only the **crops the farmer mainly grows**, declared at registration. What was planned, sown and harvested each season is held only in the [Crop Sown Registry](../design/crop-sown-registry.md).

* **Main crops** is a multi-select on the farmer, from Master Data's `CROP_COMMODITY` list.
* The **Crops tab** (crop records per land) is removed; the crop register's metadata is retired on upgrade.
* Main crops are in the sample data, the DCI farmer record (top-level key `main_crops`), the reporting views and the dashboards.

Livestock stays as it is (the Livestock tab) until a Livestock Registry exists. Land stays in the Farmer Registry, as a child of the farmer; the Crop Sown Registry's plot IDs refer to it.

## The farmer ID in the DCI record

The DCI farmer record carries the farmer ID (`FARMER_ID`, e.g. `FR-0007`) alongside the Fayda `UIN` (the FAN), in `farmer_personal_details.member_identifier`. That is how a composite that receives a FAN finds the farmer ID the Crop Sown Registry is keyed on: the `loan-profile` use case reads it from the farmer record, so the Farmer Registry grant in the consent must include `farmer_personal_details`.

The farmer can be searched by Fayda FAN (`foundational_id`) or farmer ID (`functional_record_id`); the record comes with the farmer's linked records (land, household, livestock) and declared main crops either way.

## Sample lands numbered by convention

Sample data is shared with the Crop Sown Registry by convention, never by reading the other's database (see [register model design](../design/register-model-design.md#phase-1-built)):

* sample person `ETH-IND-0007` (Master Data's sample people) is farmer `FR-0007`;
* the loader numbers each sample person's lands `LAND-0007-1`, `LAND-0007-2`…, in their woreda.

The Crop Sown Registry's sample crop seasons use the same farmer and plot IDs. Sample data is off by default ("Load Sample Data", `registry.dbSeed.loadSampleData`; see [Data seeding](../../products/registry/farmer-registry/deployment/data-seeding.md)).

## Consent settings

The Farmer Registry's consent data controller is `farmer-registry` (`global.consentDataController`, defaulting to `global.registryVariant: farmer-registry`). Its consent scopes are the top-level keys of its DCI record; `loan-profile` asks for `farmer_personal_details`, `family_details`, `farm_details` and `main_crops`.
