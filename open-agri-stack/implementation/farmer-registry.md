---
description: >-
  What changed in the Farmer Registry for Agri Stack: declared main crops
  instead of the Crops tab, sample lands numbered like the Crop Sown Registry,
  and the farmer ID in the DCI record.
---

# Farmer Registry Changes

The [Farmer Registry](../../products/registry/farmer-registry/README.md) ([OpenG2P/farmer-registry](https://github.com/OpenG2P/farmer-registry)) holds the entities the other registries refer to: farmers, their land, households and (for now) livestock. Its deployment, seeding and chart are documented in [Farmer Registry → Deployment](../../products/registry/farmer-registry/deployment/README.md). For Agri Stack it changed in three ways.

## Declared main crops replace the Crops tab

Decided in the [register model design](../design/register-model-design.md#decisions): the Farmer Registry keeps only the **crops the farmer mainly grows**, declared at registration. What was planned, sown and harvested each season is held only in the [Crop Sown Registry](../design/crop-sown-registry.md).

* **Main crops** is a multi-select on the farmer, from Master Data's `CROP_COMMODITY` list.
* The **Crops tab** (crop records per land) is removed; the crop register's metadata is retired on upgrade.
* Main crops are in the sample data, the DCI farmer record (key `main_crops`; data scope `farmer-registry.main_crops`), the reporting views and the dashboards.

Livestock stays as it is (the Livestock tab) until a Livestock Registry exists. Land stays in the Farmer Registry, as a child of the farmer; the Crop Sown Registry's plot IDs refer to it.

## The farmer ID in the DCI record

The DCI farmer record carries the farmer ID (`FARMER_ID`, e.g. `FR-0007`) alongside the Fayda `UIN` (the FAN), in `farmer_personal_details.member_identifier`. That is how a composite that receives a FAN finds the farmer ID the Crop Sown Registry is keyed on: the `loan-profile` use case reads it from the farmer record, so the Farmer Registry grant in the consent must include the data scope that carries it, `farmer-registry.farmer_identifiers`.

The farmer can be searched by Fayda FAN (`foundational_id`) or farmer ID (`functional_record_id`); the record comes with the farmer's linked records (land, household, livestock) and declared main crops either way.

## Sample lands numbered by convention

Sample data is shared with the Crop Sown Registry by convention, never by reading the other's database (see [register model design](../design/register-model-design.md#phase-1-built)):

* sample person `ETH-IND-0007` (Master Data's sample people) is farmer `FR-0007`;
* the loader numbers each sample person's lands `LAND-0007-1`, `LAND-0007-2`…, in their woreda.

The Crop Sown Registry's sample crop seasons use the same farmer and plot IDs. Sample data is off by default ("Load Sample Data", `registry.dbSeed.loadSampleData`; see [Data seeding](../../products/registry/farmer-registry/deployment/data-seeding.md)).

## Consent settings

The Farmer Registry's consent data controller is `farmer-registry` (`global.consentDataController`, defaulting to `global.registryVariant: farmer-registry`).

## Data scopes

A consent names the Farmer Registry's [data scopes](../../products/registry/registry/design/data-scopes.md), `farmer-registry.<name>`. The extension ships them in `farmer-extension/…/meta_data/data-scopes/data_scopes.json`; the registry publishes them at `POST /partner/data_scopes` (signed).

| Scope ID | Label | Fields |
| --- | --- | --- |
| `farmer-registry.farmer_identifiers` | Farmer ID and national ID | farmer ID (`functional_record_id`), Fayda FAN (`foundational_id`), registration and last-approval dates |
| `farmer-registry.personal_details` | Personal details | section `fr_farmer_personal_info` (name, sex, birth date or estimated age, marital status, education) and language spoken |
| `farmer-registry.contact` | Contact details | phone numbers, has a personal phone, emails |
| `farmer-registry.location` | Farmer's address and location | section `fr_farmer_location` |
| `farmer-registry.main_crops` | Main crops | declared main crops |
| `farmer-registry.socio_economic_and_health` | Socio-economic and health details | section `fr_farmer_socio_and_health` (sources of income, main crops, disability) |
| `farmer-registry.land` | Land parcels | section `fr_farmer_land` and the parcel ID, without location |
| `farmer-registry.land_location` | Land parcel locations | parcels' address, administrative area, GPS point and boundary |
| `farmer-registry.livestock` | Livestock | section `register_fr_farmer_livestocks` |
| `farmer-registry.farm_inputs` | Farm inputs | section `register_fr_farmer_farm_input` |
| `farmer-registry.memberships` | Cooperative and cluster memberships | section `fr_farmer_membership` |
| `farmer-registry.household` | Household details | sections `fr_household_information`, `hh_information` and the household ID |
| `farmer-registry.household_location` | Household address and location | section `fr_household_location` |
| `farmer-registry.household_members` | Household members | section `fr_household_members` |
| `farmer-registry.poverty_score` | Household poverty score | section `hh_score` (computed scores) |

* **Named scopes, no default section scopes** (`exclude_section_scopes: true`). Scope IDs are permanent, and section mnemonics are UI names (with an `fr_` / `hh_` prefix, and the Household register repeating the Farmer register's sections). Each scope references its section (`section:<mnemonic>`), so it follows the section's fields; a renamed section refuses the catalogue instead of silently retiring a scope.
* **Not shared:** the record header (status, approvers, image), documents, ID authentication, the farmer–household link (internal IDs), the intake-only farm-input and livestock sections, and the Household register's copies of the Farmer sections.
* **Finer than a section:** contact details, main crops and the farmer and parcel identifiers are scopes of their own, so a partner can get, say, main crops without the disability fields of the same section.
* The sample `loan-profile` use case grants `farmer_identifiers`, `personal_details`, `household_location`, `land`, `land_location` and `main_crops`.
