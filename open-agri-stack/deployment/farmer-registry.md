---
description: >-
  Installing the Farmer Registry for Agri Stack: its commons with the Consent
  Manager in the department role, then the Farmer Registry chart; what it
  shares, the Farmer ID and national ID link, the Composite as a partner.
---

# Farmer Registry

The [Farmer Registry](../../products/registry/farmer-registry/README.md) is the agriculture department's registry of farmers, their land, households and (for now) livestock. Its registers, fields, data scopes and generic install are documented there. This page says what to install and set for Agri Stack. On these pages it runs in the namespace `trial` ([topology](README.md#topology)).

## What to install

From **Apps → Charts** in Rancher, in the `trial` namespace, in this order:

| # | Chart (Rancher name) | Release |
| --- | --- | --- |
| 1 | **OpenG2P Commons Base** (`openg2p-commons-base`) | `commons` (fixed) |
| 2 | **OpenG2P Commons Services** (`openg2p-commons-services`) | `commons-services` (fixed) |
| 3 | **OpenG2P Farmer Registry** (`openg2p-farmer-registry`) | `fr` |

The Farmer Registry's install steps, hook Jobs and checks: [Farmer Registry → Deployment](../../products/registry/farmer-registry/deployment/README.md). Commons: [Commons Helm chart](../../deployment/openg2p-commons-helm-chart.md).

## Form fields to choose

The defaults work for a demo. Change only these.

| Chart | Field | Value | Why |
| --- | --- | --- | --- |
| Commons Services | Exchange Role (Consent Manager) | **department** | The CM trusts consent tokens from the Exchange CM (`agri-stack-exchange-cm`), presented by the Composite (`agri-composite`), with the public key at `https://consent-manager-partner.agrix.<parent domain>/…/.well-known/jwks.json` (e.g. `agrix.openg2p.org` for `trial.openg2p.org`) |
| Commons Services | Partner Portal? (Consent Manager) | **No** (the default) | Partners of this registry present a consent they collected and signed themselves; consents collected in person in a CM are used through the Exchange. With the portal off, Require National-ID Login is not shown |
| Farmer Registry | Release name | `fr` | The partner API is then `https://partner-fr.<domain>`, the URL the Composite is given |
| Farmer Registry | Load Sample Data (`registry.dbSeed.loadSampleData`) | **On**, for a demo only | Sample farmers from the catalogue's sample people, matching the Crop Sown Registry's samples ([sample data](#sample-data)) |

Keep the commons-services defaults otherwise: the registry needs AWE (its change requests; the db-seed Job waits for it), Master Data with the `agriculture` dataset theme (the farmer's main crops come from its `CROP_COMMODITY` list), Partner Management and the Consent Manager.

Right by default, and not to change: **Verify Partner Signature** and **Enforce Consent** on; the consent data controller `farmer-registry` (the registry variant); partner keys checked in Partner Management; the PM and CM URLs (`http://commons-services-pm-partner-api`, `http://commons-services-cm-partner-api`). Settings: [Helm chart](../../products/registry/farmer-registry/deployment/helm-chart.md).

## For production

| Field | Value | Why |
| --- | --- | --- |
| Base Domain (both commons charts, and the registry) | The department's own domain | Every hostname sits under it |
| Exchange Domain (Consent Manager) | The Exchange's domain, e.g. `agrix.example.org` | Only when it is not `agrix.<parent of this domain>` |
| Signing Key, Signing Key Secret, Signing Key ID (Consent Manager) | **existing**, the department's own `.p12` | The demo key is public |
| Load Sample Data, Load Sample Images | **Off** | Sample data is for demos ([data seeding](../../products/registry/farmer-registry/deployment/data-seeding.md)) |
| Load Sample People (Commons Services) | **Off** | As above |

Before going to production: [Farmer Registry → Deployment](../../products/registry/farmer-registry/deployment/README.md#before-going-to-production).

## What it does in Agri Stack

### What it holds

* **Crops:** only the farmer's declared main crops. Crop seasons (planned, sown, harvested) are held only in the [Crop Sown Registry](crop-sown-registry.md). A deployment could instead keep crop seasons in an activity register of the Farmer Registry (not built), but then it should not also run the Crop Sown Registry for the same farmers: each fact has one authoritative registry, and two would count sown area twice.
* **Land:** stays in the Farmer Registry for now, as a section of the farmer; the Crop Sown Registry's plot IDs refer to it. If a land administration (cadastre) registry is set up, the parcel moves there and the Farmer Registry keeps a reference to it and how the farmer uses it.
* **Livestock:** stays as it is until a [Livestock Registry](../design/livestock-registry.md) exists.

### What Agri Stack reads

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

A consent without an optional scope still works: those fields come back `null`. The full scope list: [Farmer Registry](../../products/registry/farmer-registry/README.md#data-scopes); the use case file: [Use-Case Configuration](../composite/use-case-configuration.md#the-loan-profile-use-case).

### Farmer ID and national ID

Every Agri Stack registry is keyed to the same national identifier. The Farmer Registry holds the link between the two:

* the farmer record's foundational ID is the **national ID** (Fayda FAN in the shipped Ethiopia example; subject ID type `FAYDA_FAN`);
* its functional ID is the **Farmer ID** (`FARMER_ID`, e.g. `FR-0007`);
* the DCI farmer record carries both in `farmer_personal_details.member_identifier`, as `UIN` and `FARMER_ID`.

A partner can ask about a farmer by either. When it sends a FAN, the Composite reads the Farmer ID from this record and uses it to search the [Crop Sown Registry](crop-sown-registry.md). When a consent is collected in the Exchange's partner portal, CM staff check the Farmer ID given in the request against this registry before approving it ([consent collection](../../consent-management/design/consent-collection.md#identifiers-and-demographics)).

### The Composite as a partner

The registry only sees the Composite, never the partner (a bank) directly. The bank's ID travels in `header.meta.on_behalf_of`, which the registry logs.

| Where (in `trial`) | What | Set by |
| --- | --- | --- |
| Partner Management | `PARTNER_AGRI_COMPOSITE`, with the Composite's public key and `kid`. The registry checks the Composite's signature against it | [Exchange setup](after-install.md#exchange-setup) |
| Consent Manager, role | **Exchange Role** `department`. Each consent token's status is checked at the Exchange CM | Commons Services form ([CM deployment](../../consent-management/deployment/README.md#exchange-optional)) |
| Consent Manager, binding | Audience `agri-composite`, controller `farmer-registry` | [Exchange setup](after-install.md#exchange-setup) |
| Consent Manager, standing policy | See below | [Exchange setup](after-install.md#exchange-setup) |

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

### Sample data

For a demo, **Load Sample Data** loads farmers from the catalogue's sample people, numbered so that they match the Crop Sown Registry's sample crop seasons: person `ETH-IND-0007` is farmer `FR-0007`, with lands `LAND-0007-1`, `LAND-0007-2`… ([data seeding](../../products/registry/farmer-registry/deployment/data-seeding.md#sample-data)). The mock identity system's identities at the Exchange are the same people, so a sample farmer can log in with their national ID in the partner portal.

## Check

```bash
helm -n trial list
kubectl -n trial get jobs
```

The releases `deployed` and the hook Jobs completed ([post-install check](../../products/registry/farmer-registry/deployment/README.md#post-install-check)). The partner API answers at `https://partner-fr.trial.openg2p.org`. The Exchange setup later checks that this CM trusts the Exchange's consent tokens and names the field if not.
