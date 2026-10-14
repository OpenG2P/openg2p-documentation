---
description: >-
  What is configured in the Farmer Registry install for Agri Stack: the data it
  shares, the Farmer ID and national ID link, the Composite as a partner, and the
  department Consent Manager with its standing policy for the Composite.
---

# Farmer Registry

The [Farmer Registry](../../products/registry/farmer-registry/README.md) is the agriculture department's registry of farmers, their land, households and (for now) livestock. Its registers, fields, data scopes and installation are documented there. This page says what is set for Agri Stack.

In the three-namespace setup it runs in the department namespace `trial`, release `fr`, with its own commons (Partner Management, Consent Manager, Master Data: the catalogue). See [deploying on a cluster](../guides/deployment.md#farmer-registry).

## Registry settings

| Setting | Value for Agri Stack | Default? |
| --- | --- | --- |
| **Verify Partner Signature** (`global.partnerSignatureValidationEnabled`) | On | Yes |
| **Enforce Consent** (`global.consentEnforcementEnabled`) | On | Yes |
| Consent data controller (`global.consentDataController`) | `farmer-registry` | Yes (the registry variant) |
| **Load Sample Data** (`registry.dbSeed.loadSampleData`) | On for a demo only | Off |

Master Data in the same namespace needs the **agriculture** dataset theme (the default). The farmer's main crops are read from its `CROP_COMMODITY` list.

## What Agri Stack reads

The Composite's `loan-profile` use case searches the `Farmer` register, record type `spdci-extensions-dci:Farmer`, with an expression search on `foundational_id` (national ID) or `functional_record_id` (Farmer ID). The record comes with the farmer's land and household.

| Register | Read by Agri Stack |
| --- | --- |
| **Farmer** | Yes: identity, personal details, main crops |
| **Land** (section of Farmer) | Yes: parcels and, optionally, their location |
| **Household** | Its location only, optionally |
| Livestock, farm inputs, memberships, household members, poverty score | No |

**Data scopes** in the use case's grant for `farmer-registry`:

| Scope | Required or optional | Why |
| --- | --- | --- |
| `farmer-registry.farmer_identifiers` | Required | The Farmer ID the Crop Sown Registry is searched by is read from it |
| `farmer-registry.personal_details` | Required | Name, sex, age |
| `farmer-registry.land` | Required | Land parcels and total land |
| `farmer-registry.main_crops` | Required | Declared main crops |
| `farmer-registry.household_location` | Optional | The farmer's location |
| `farmer-registry.land_location` | Optional | Parcel locations |

A consent without an optional scope still works: those fields come back `null`. The full scope list is on the [Farmer Registry](../../products/registry/farmer-registry/README.md#data-scopes) page; the use case file is explained in [Composite configuration](../guides/composite-configuration.md#the-loan-profile-use-case).

## Farmer ID and national ID

Every Agri Stack registry is keyed to the same national identifier. The Farmer Registry holds the link between the two:

* the farmer record's foundational ID is the **national ID** (Fayda FAN in the reference setup; subject ID type `FAYDA_FAN`);
* its functional ID is the **Farmer ID** (`FARMER_ID`, e.g. `FR-0007`);
* the DCI farmer record carries both in `farmer_personal_details.member_identifier`, as `UIN` and `FARMER_ID`.

A partner can ask about a farmer by either. When it sends a FAN, the Composite reads the Farmer ID from this record and uses it to search the [Crop Sown Registry](crop-sown-registry.md). When a consent is collected in the Exchange's partner portal, Consent Manager staff check the Farmer ID given in the request against this registry before approving it ([consent collection](../../consent-management/design/consent-collection.md#identifiers-and-demographics)).

## The Composite as a partner

The registry only sees the Composite, never the partner (a bank) directly. The bank's ID travels in `header.meta.on_behalf_of`, which the registry logs.

| Where (in `trial`) | What | Set by |
| --- | --- | --- |
| Partner Management | `PARTNER_AGRI_COMPOSITE`, with the Composite's public key and `kid`. The registry checks the Composite's signature against it | [Exchange setup](../guides/exchange-setup.md) |
| Consent Manager, role | **Exchange Role** `department`: trusts consent tokens from issuer `agri-stack-exchange-cm`, presented by `agri-composite`, signed with the key published at `https://consent-manager-partner.agrix.<parent domain>/api/consent-manager-partner/.well-known/jwks.json`. Each token's status is checked at the Exchange CM | commons-services form ([CM deployment](../../consent-management/deployment/README.md#exchange-optional)) |
| Consent Manager, binding | Audience `agri-composite`, controller `farmer-registry` | [Exchange setup](../guides/exchange-setup.md) |
| Consent Manager, standing policy | See below | [Exchange setup](../guides/exchange-setup.md) |

### Standing policy for the Composite

The department decides once what it releases through the Exchange. Every consent token is then cut down to this policy (token scopes ∩ policy).

| Policy field | Value set by the Exchange setup |
| --- | --- |
| Allowed data scopes | Every `farmer-registry` scope the Composite's published use cases name, required and optional. For `loan-profile`: the six scopes above |
| Allowed purposes | The use cases' purposes: `credit-assessment` |
| Allowed subject ID types | `FAYDA_FAN`, `FARMER_ID` |
| Maximum validity | `P90D` |
| Fetch type | `oneshot` |

A rerun of the setup only widens this policy, never narrows it. The department can narrow it by hand in its CM; a scope it removes then comes back `null` (optional) or fails the source (required). How the department and Exchange CMs work together: [Exchange consent tokens](../../consent-management/design/exchange-receipts.md).

## Sample data

For a demo, **Load Sample Data** loads farmers from the catalogue's sample people, numbered so that they match the Crop Sown Registry's sample crop seasons: person `ETH-IND-0007` is farmer `FR-0007`, with lands `LAND-0007-1`, `LAND-0007-2`… ([data seeding](../../products/registry/farmer-registry/deployment/data-seeding.md#sample-data)). The mock identity system's identities are the same people, so a sample farmer can log in with their national ID in the partner portal.
