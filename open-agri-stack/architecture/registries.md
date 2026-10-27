---
description: >-
  The Farmer Registry and the Crop Sown Registry in Agri Stack: what each
  holds, how they are linked by the Farmer ID and the national ID, what the
  Composite reads, and the Composite as a partner of each.
---

# Registries in Agri Stack

Agri Stack reads two registries today, each its own install in its own department ([across departments](README.md#across-departments)). Both are built on the [registry platform](../../products/registry/registry/README.md); their registers, fields and data scopes are documented with each product. This page covers only their part in Agri Stack. How to install them: [Deployment](../deployment/README.md).

| Registry | Department (example) | Holds |
| --- | --- | --- |
| [Farmer Registry](../../products/registry/farmer-registry/README.md) | Agriculture | Farmers, their land, households, declared main crops and (for now) livestock |
| [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md) | Crops | Crop seasons: what each farmer plans, sows, observes and harvests, plot by plot and season by season |

## Farmer Registry

### What it holds

* **Crops:** only the farmer's declared main crops. Crop seasons are held only in the [Crop Sown Registry](#crop-sown-registry). A deployment could keep them instead in an activity register of the Farmer Registry (not built), but should then not also run the Crop Sown Registry for the same farmers: each fact has one authoritative registry, and two would count sown area twice.
* **Land:** a section of the farmer, for now; the Crop Sown Registry's plot IDs refer to it. If a land administration (cadastre) registry is set up, the parcel moves there and the Farmer Registry keeps a reference to it and how the farmer uses it.
* **Livestock:** stays as it is until a [Livestock Registry](../design/livestock-registry.md) exists.

### Farmer data the Composite reads

The `loan-profile` use case searches the `Farmer` register (`spdci-extensions-dci:Farmer`) by `foundational_id` (national ID) or `functional_record_id` (Farmer ID). The record comes with the farmer's land and household. Livestock, farm inputs, memberships, household members and the poverty score are not read.

| Data scope | Required or optional | Why |
| --- | --- | --- |
| `farmer-registry.farmer_identifiers` | Required | The Farmer ID the Crop Sown Registry is searched by |
| `farmer-registry.personal_details` | Required | Name, sex, age |
| `farmer-registry.land` | Required | Land parcels and total land |
| `farmer-registry.main_crops` | Required | Declared main crops |
| `farmer-registry.household_location` | Optional | The farmer's location |
| `farmer-registry.land_location` | Optional | Parcel locations |

Without an optional scope in the consent, those fields come back `null`. All scopes: [Farmer Registry → Data scopes](../../products/registry/farmer-registry/data-scopes.md); the use case: [Use-Case Configuration](../composite/use-case-configuration.md#the-loan-profile-use-case).

## Crop Sown Registry

An [activity register](../../products/registry/registry/features/activity-register.md), plus a Cluster register. It needs no other registry to run.

### How it relates to the Farmer Registry

The two share identifiers, not code or databases. They run in different departments, so the Crop Sown Registry never looks anything up in the Farmer Registry.

* **The farmer** is the Farmer Registry's Farmer ID (`FR-…`), with the national ID recorded alongside on each activity.
* **The plot** is a Farmer Registry land record ID (`LAND-…`).
* **Entities first:** farmers and plots are registered in the Farmer Registry before crop activities are recorded; the Crop Sown Registry checks their IDs by format only.
* **The district is entered** on the plan and the sowing, since the registry cannot read the plot's location.

More: [Crop Sown Registry → How it relates to the Farmer Registry](../../products/registry/crop-sown-registry/README.md#how-it-relates-to-the-farmer-registry).

### Crop data the Composite reads

The `loan-profile` use case searches the `CropSown` register by Farmer ID: read from the Farmer Registry's record, or the subject itself when the partner sends a `FARMER_ID`. Both sources are optional: if the Crop Sown Registry is down or denies, the loan profile still comes back, with that source marked.

| Source | `reg_record_type` | Query |
| --- | --- | --- |
| `season_summaries` | `spdci-extensions-agri:ActivityAggregate` | `subject_id`, `aggregate_type: FARMER_SEASON_SUMMARY`, and the partner's `crop_year` and `season` if given |
| `crop_seasons` | `spdci-extensions-agri:CropSeason` | `subject_id`, and the partner's `crop_year` and `season` if given |

Activities and the Cluster register are not read today.

| Data scope | Required or optional |
| --- | --- |
| `crop-sown-registry.farmer_reference` | Required |
| `crop-sown-registry.crop_season` | Required |
| `crop-sown-registry.measures` | Required |
| `crop-sown-registry.location` | Optional |

What each scope covers: [Crop Sown Registry → Data scopes](../../products/registry/crop-sown-registry/data-scopes.md).

**Final figures.** A season summary is final (`is_final`) once the season's period is locked in the register's **Settings**. A lender or subsidy programme that relies on a season's figures should read final summaries. Lock from the planning start, or a late change to a plan makes the summary provisional again.

### Searches across farmers

A programme system can read season summaries for many farmers at once (e.g. every final summary of a season, for a subsidy run) without a per-farmer consent, only if the registry operator lists it as a bulk aggregate partner ([bulk aggregate searches](../../products/registry/registry/design/activity-register.md#bulk-aggregate-searches)). The Composite does not use this, and no partner is listed by default.

## Farmer ID and national ID

Every Agri Stack registry is keyed to the same national identifier; the Farmer Registry holds the link to the Farmer ID.

| Identifier | Subject ID type | In the Farmer Registry | In the Crop Sown Registry |
| --- | --- | --- | --- |
| National ID | `FAYDA_FAN` | The farmer's foundational ID; `UIN` in the DCI record's `member_identifier` | Recorded on each activity (`fayda_fan`) |
| Farmer ID (e.g. `FR-0007`) | `FARMER_ID` | The farmer's functional ID; `FARMER_ID` in `member_identifier` | The register's subject |

* A partner can ask about a farmer by either. Given a national ID, the Composite reads the Farmer ID from the Farmer Registry and searches the Crop Sown Registry with it.
* **One consent covers both registries.** The Crop Sown Registry's configuration names `fayda_fan` among its subject ID fields, so a consent given for the national ID passes its subject check on a search by Farmer ID, as long as its own activities record that Farmer ID with that national ID ([sharing through partner search](../../products/registry/registry/design/activity-register.md#sharing-through-partner-search)).
* When a consent is collected in the Exchange's partner portal, CM staff check the Farmer ID in the request against the Farmer Registry before approving it ([consent collection](../../consent-management/design/consent-collection.md#identifiers-and-demographics)).

## The Composite as a partner

Each registry sees only the Composite, never the partner (e.g. a bank). The partner's ID travels in `header.meta.on_behalf_of`, which the registry logs. In each department:

| Where | What |
| --- | --- |
| Partner Management, key | `PARTNER_AGRI_COMPOSITE`, with the Composite's public key and `kid`. The registry checks the Composite's signature against it |
| Partner Management, scope policy | The Composite's policy for this registry's data controller (`farmer-registry` or `crop-sown-registry`): below |
| Consent Manager, role | **Exchange Role** `department`: it trusts consent tokens from the Exchange CM (`agri-stack-exchange-cm`) presented by the Composite (`agri-composite`), checked offline (a status check at the Exchange CM is optional, off by default) |

### Scope policy for the Composite

The department decides once what it releases through the Exchange: the Composite's scope policy for the registry, in the department's Partner Management, is the **ceiling**. The department's CM reads it from PM and cuts every consent token down to it (token scopes ∩ ceiling); without it, every search through the Composite is denied.

| Policy field | Value |
| --- | --- |
| Allowed data scopes | Every scope of this registry that the Composite's published use cases name, required and optional (for `loan-profile`, the scopes above) |
| Allowed purposes | The use cases' purposes: `credit-assessment` |
| Allowed subject ID types | `FAYDA_FAN`, `FARMER_ID` |
| Maximum validity | `P90D` |
| Fetch type | `oneshot` |

The [Exchange setup](../deployment/after-install.md#exchange-setup) proposes these values as a Partner Management policy request, which is approved in the department's PM, and only ever widens them. The department can narrow the policy with its own policy request in its PM; a scope it removes then comes back `null` (optional) or fails the source (required). How the department and Exchange CMs work together: [Exchange consent tokens](../../consent-management/design/exchange-consent-tokens.md); policies in general: [Data-Sharing Policies](data-sharing-policies.md).

## Sample data

The two registries' sample data describe the same people, the catalogue's sample people: person `ETH-IND-0007` is farmer `FR-0007` with lands `LAND-0007-1`, `LAND-0007-2`…, and the Crop Sown Registry's sample crop seasons are for those farmers and plots. A demo of `loan-profile` therefore returns crop seasons for the same farmer. The mock identity system at the Exchange holds the same people, so a sample farmer can log in with their national ID in the partner portal. Details: [Farmer Registry sample data](../../products/registry/farmer-registry/deployment/data-seeding.md#sample-data), [Crop Sown Registry sample data](../../products/registry/crop-sown-registry/deployment/rancher.md#sample-data).
