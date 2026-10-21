---
description: >-
  The Farmer Registry's data scopes: their IDs, what each covers, how to read
  the live catalogue, and the rules for changing them.
---

# Data Scopes

A partner's consent and its access policy in Partner Management name the registry's [data scopes](../registry/design/data-scopes.md): named groups of fields that can be released.

## Scope IDs

A scope ID is `<data controller>.<scope>`. The data controller is the registry's **Consent Data Controller** (`global.consentDataController`), by default the registry variant: `farmer-registry`. So `land` is `farmer-registry.land`. This is the **Data controller** of a scope policy in Partner Management.

## The scopes

| Scope ID | Label | Covers |
| --- | --- | --- |
| `farmer-registry.farmer_identifiers` | Farmer ID and national ID | Farmer ID, Fayda FAN, registration and last-approval dates |
| `farmer-registry.personal_details` | Personal details | Section `fr_farmer_personal_info` (name, sex, birth date or estimated age, marital status, education) and language spoken |
| `farmer-registry.contact` | Contact details | Phone numbers, has a personal phone, emails |
| `farmer-registry.location` | Farmer's address and location | Section `fr_farmer_location` |
| `farmer-registry.main_crops` | Main crops | Declared main crops |
| `farmer-registry.socio_economic_and_health` | Socio-economic and health details | Section `fr_farmer_socio_and_health` |
| `farmer-registry.land` | Land parcels | Section `fr_farmer_land` and the parcel ID, without location |
| `farmer-registry.land_location` | Land parcel locations | Parcels' address, administrative area, GPS point and boundary |
| `farmer-registry.livestock` | Livestock | Section `register_fr_farmer_livestocks` |
| `farmer-registry.farm_inputs` | Farm inputs | Section `register_fr_farmer_farm_input` |
| `farmer-registry.memberships` | Cooperative and cluster memberships | Section `fr_farmer_membership` |
| `farmer-registry.household` | Household details | Sections `fr_household_information`, `hh_information` and the household ID |
| `farmer-registry.household_location` | Household address and location | Section `fr_household_location` |
| `farmer-registry.household_members` | Household members | Section `fr_household_members` |
| `farmer-registry.poverty_score` | Household poverty score | Section `hh_score` |

* **Named scopes only.** The default one-scope-per-section is off (`exclude_section_scopes: true`): scope IDs are permanent, while section mnemonics are UI names and the Household register repeats the Farmer register's sections. A scope names its section (`section:<mnemonic>`), so it follows the section's fields, and a renamed section makes the catalogue fail to load rather than silently retiring a scope.
* **Finer than a section:** contact details, main crops and the farmer and parcel identifiers are scopes of their own; a partner can get main crops without the disability fields of the same section.
* **Never shared:** the record header (status, approvers, image), documents, ID authentication, the farmer–household link (internal IDs), the intake-only farm-input and livestock sections, and the Household register's copies of the Farmer sections.

## The live catalogue

This table is what ships. An install's catalogue, with each scope's fields, is served by its partner API:

* `POST /partner/data_scopes`, signed by a partner onboarded in Partner Management;
* `GET /partner/data_scopes`, only when **Allow Unsigned Read of Data Scope Catalogue** is on.

## Where they are defined

`farmer-extension/src/openg2p_registry_farmer_extension/meta_data/data-scopes/data_scopes.json` in [farmer-registry](https://github.com/openg2p/farmer-registry). The format: [data scopes](../registry/design/data-scopes.md).

## Changing them

* **Never rename or reuse a scope.** Consents and access policies refer to it.
* **Narrowing** a scope is safe. **Widening** it does not reach consents given before.
* **Changing the data controller** changes every scope ID: every consent and policy naming the old IDs stops matching.
