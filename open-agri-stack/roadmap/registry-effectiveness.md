---
description: Measuring whether the registries are accurate, used and trusted, not only how many records they hold.
---

# Registry Effectiveness

{% hint style="warning" %}
**Status: proposal, not built.** This page studies the Trust-Adjusted Registry Effectiveness Index proposed for India's AgriStack, compares India's registries with Agri Stack's, and says what Agri Stack would need to measure the same. The resulting work is listed in the [Roadmap](README.md#phase-2-farmers-partners-and-the-open-agri-network).
{% endhint %}

## The index

Rajeev Chawla's article [AgriStack: A Trust-Adjusted Registry Effectiveness Index (TAREI)](https://www.linkedin.com/pulse/agristack-trust-adjusted-registry-effectiveness-index-chawla-ias-xrpbc/) (November 2026) argues that a registry is not judged by how many Farmer IDs it has issued, plots it has mapped or crops it has surveyed, but by whether its records are accurate and current, used to deliver services, and trusted by farmers. It proposes one score per registry:

**TAREI = C × Q × U × T × 100**

| Factor | Meaning |
| --- | --- |
| **C**, coverage | Share of the eligible population or plots that are in the registry |
| **Q**, quality | Share of those records that are accurate, complete, correctly linked and updated within the prescribed time |
| **U**, usage | Share of the quality records used successfully in at least one chosen service during the period, directly or through an authorised intermediary |
| **T**, trust | Share of the farmers behind those used records who trust the registry, from an independent survey |

Each factor is between 0 and 1, with its own denominator. Multiplying them means high coverage cannot hide poor quality, little use or weak trust: the score is the share of eligible units that meet all four conditions.

### Applied to India's three registries

| Registry (unit) | Coverage | Quality | Usage |
| --- | --- | --- | --- |
| Farmer Registry (eligible farmers) | Farmers with a valid Farmer ID and the required links | Correct identity and land links; changes in ownership and other details reflected in time | Used for Kisan Credit Card loans, benefits, procurement, fertiliser or other services |
| Crop Sown Registry (plots chosen for the season's crop survey) | Those plots with a crop record for the season | Correct crop, area and plot link; survey on time; sowing date within tolerance | Used for crop insurance, crop advisory, input planning or other services |
| Map Registry (eligible cadastral plots) | Plots with digitised, georeferenced polygons | Correct survey and sub-survey link, topology, boundary updates, and spatial accuracy fit for the use | Used for soil sampling, satellite advisory, crop verification or other spatial services |

"Eligible" means everyone who should be in the Farmer Registry, or every plot that should be in the Map Registry; "cultivated" means the plots the state has chosen for that season's crop survey.

### Trust

Five statements per registry, asked in the farmer's language. A farmer counts as trusting the registry when they agree with at least four; "do not know" is recorded separately and is not agreement.

| Dimension | Statement (in substance) |
| --- | --- |
| Confidence in the data | What is recorded about me, my crop or my plot is correct |
| Transparency | I know what is recorded and why, and can see it or get a copy |
| Privacy and agency | My data is protected, and I can choose about sharing where consent is needed |
| Recourse | I know where to report an error, and it would be acted on in reasonable time |
| Willingness | I would use other services this registry enables |

### Illustration

The article's numbers are illustrative, not actual AgriStack figures:

| Registry | C | Q | U | T | TAREI |
| --- | --- | --- | --- | --- | --- |
| Farmer Registry | 90% | 90% | 60% | 80% | 38.9 |
| Crop Sown Registry | 85% | 80% | 50% | 75% | 25.5 |
| Map Registry | 95% | 70% | 40% | 70% | 18.6 |

The Map Registry has the highest coverage and the lowest score, because of quality, usage and trust.

### How it is to be run

* Publish the four factors separately, beside the score.
* Use authoritative denominators, independent field checks and service outcome logs; count neither API calls nor failed transactions as usage.
* For the Map Registry, set accuracy tiers by use: a point may do for soil sampling, while insurance on boundaries needs surveyed boundaries.
* Let farmers see their records (in a farmer app or assisted), ask for corrections and follow grievances; track the time to correct, overdue cases, rejection reasons and whether the farmer confirms the resolution.
* Pilot in a few districts each quarter; break results down by gender, location, holding size and farmer category (including cultivators who do not own land); survey people who are not registered too, to see who is left out; state sample sizes, thresholds and limitations.

Comments on the article add: **land rights integrity** as a fifth factor (a mapped parcel is not a secure title, and a registered farmer does not prove ownership or cultivation rights); **satellite checks** of the crop records against imagery every season, so field teams visit only the plots where they disagree; and **open aggregate data** at district level, as the USDA publishes its Cropland Data Layer.

## India's registries and Agri Stack's

India's AgriStack has three foundational registries: the **Farmer Registry**, the **Crop Sown Registry** (filled by the Digital Crop Survey) and the **Map Registry**, the geo-referenced village maps: every cadastral parcel as a surveyed polygon with a unique land parcel ID (ULPIN, "Bhu-Aadhaar"). The Farmer Registry links a farmer to parcels, and the Crop Sown Registry records what is sown on each parcel each season.

| India's AgriStack | Agri Stack (reference) |
| --- | --- |
| Farmer Registry | [Farmer Registry](../deployment/farmer-registry.md): farmers, and their land parcels with shapes (GeoJSON) |
| Crop Sown Registry | [Crop Sown Registry](../deployment/crop-sown-registry.md): crops sown per season, as activities |
| Map Registry | None: parcels and their shapes live in the Farmer Registry |
| — | [Livestock Registry](../registries/livestock-registry/README.md), [Agents Registry](../registries/agents-registry/README.md) |

Keeping parcels inside the Farmer Registry is simpler for a first deployment, but it ties a parcel to whoever registered it: a parcel owned by two farmers, or cultivated by a tenant, is recorded twice or not at all, and the land or survey department, which is the authority for boundaries, has no registry of its own. A separate Map Registry, kept by that department, gives every parcel one ID that the Farmer Registry (ownership, tenancy) and the Crop Sown Registry (crops) refer to. It is on the roadmap as **Map Registry**.

## How it applies to Agri Stack

Each part of the index and its counterpart in Agri Stack. Status: **exists**, **partial** or **missing**.

| In the index | In Agri Stack | Status |
| --- | --- | --- |
| **Registries** | | |
| Farmer Registry | [Farmer Registry](../deployment/farmer-registry.md) | Exists |
| Crop Sown Registry | [Crop Sown Registry](../deployment/crop-sown-registry.md) | Exists |
| Map Registry | None: parcels and their shapes are in the Farmer Registry | Missing (TODO 10) |
| **Coverage (C)** | | |
| Records counted by location and season | Each registry's reporting views and Superset dashboards | Exists |
| Eligible farmers, plots chosen for the crop survey (the denominators) | Nothing: they come from outside the registries | Missing (TODO 1) |
| **Quality (Q)** | | |
| Complete, accurate records | Required fields and code lists from the catalogue; staff changes go through change requests approved in AWE | Exists |
| Verified records | Verification on some activities (e.g. vaccinations in the Livestock Registry); no common model of who verified what, when, on what evidence | Partial (TODO 3) |
| Updated within prescribed timelines | Last-updated dates on records; no timeline per kind of record, so a stale record is not flagged | Missing (TODO 2) |
| Correctly linked | Each record holds the farmer's IDs; links between registries are not checked (a crop record's farmer or parcel need not exist) | Missing (TODO 4) |
| Spatial accuracy fit for the use | Parcel shapes in the Farmer Registry, with no accuracy recorded | Missing (TODO 10) |
| **Usage (U)** | | |
| A pre-defined service | A Composite use case (e.g. `loan-profile`, a lender's check, as the article's Kisan Credit Card loans) | Exists |
| An authorised intermediary | A partner in the Exchange's Partner Management with a policy for the use case | Exists |
| Service outcome logs, not API hits | The Composite's audit events (outcome per request, no farmer IDs by design) and the Exchange Consent Manager's access log (each use of a farmer's consent); not joined, so "this farmer's records were used successfully" cannot be counted | Partial (TODO 5) |
| Services outside the Exchange | A department using its own registry: no outcome log | Missing (country's choice) |
| **Trust (T)** | | |
| The survey itself | Outside the software: a field survey by the programme | Not software |
| Transparency: farmers see what is recorded | Staff see records; farmers have no portal or app for their records | Missing (TODO 8) |
| Privacy and agency | Consent through the Consent Manager, enforced at each registry with data scopes; partial consent and revoking one registry only are still to come | Partial |
| Recourse: report an error, see it acted on | Staff can correct records by change requests; no farmer-facing grievance channel, deadlines or tracking. For consents, the SMS and "I did not give this consent" are planned | Missing (TODO 9) |
| **Operating it** | | |
| Breakdowns by gender, location, holding size, farmer category | Gender and location are on the Farmer Registry; holding size can be derived from the parcels; farmer category (owner, tenant, cultivator) is country data | Partial (TODO 6) |
| Publishing the factors and the score | Superset dashboards per registry; nothing combines registries or shows the four factors | Missing (TODO 6) |
| From the comments: land rights integrity | Land parcels on the Farmer Registry; no history of transfers or tenancy | Missing (TODO 12) |
| From the comments: satellite checks of crops | None | Missing (TODO 11) |
| From the comments: open aggregate data | The public catalogue (planned) | Missing (TODO 13) |

The trust survey, the eligible populations and the choice of services that count as usage are the programme's decisions in each country, not software.

## TODO

| # | To do | Where | Depends on | Roadmap item |
| --- | --- | --- | --- | --- |
| 1 | Load the denominators per location and season: eligible farmers, and the plots chosen for the crop survey | Catalogue datasets (Master Data), read by the reporting views | — | Registry effectiveness figures |
| 2 | Set a timeline per kind of record or change (e.g. ownership change within 30 days) and flag records past it in the reporting views | Registry platform (reporting views, registry settings) | — | Registry effectiveness figures |
| 3 | One verification model for entity and activity records: who verified, when, with what evidence; reset on change | Registry platform | — | [Attestation on records](README.md#functional-in-order) |
| 4 | Check links across registries: a crop record's farmer exists in the Farmer Registry (and, later, its parcel in the Map Registry) | Crop Sown Registry, calling the Farmer Registry | Sharing on a mandate | [Sharing on a mandate](README.md#functional-in-order) |
| 5 | Count usage per farmer: join the Composite's successful answers with the consents used, by request ID, per use case and period | Composite, Exchange Consent Manager, Audit Manager | Request ID end to end | Registry effectiveness figures |
| 6 | Effectiveness dashboards: C, Q, U per registry and season, the survey's T loaded per district, the product; broken down by gender, location, holding size (derived from parcels) and farmer category | Superset at the Exchange or an analytics layer | 1, 2, 3, 5; dashboards and cross-registry figures | Registry effectiveness figures |
| 7 | Load the trust survey results (share trusting, per registry and district) so the dashboards can combine them | Dashboards (a simple upload or dataset) | 6 | Registry effectiveness figures |
| 8 | Farmers see their records and consents (portal or app, and assisted at an office) | Registries' beneficiary APIs, Consent Manager | — | Farmer access to their own records |
| 9 | Corrections and grievances raised by farmers, tracked with a timeline per kind: overdue cases, rejection reasons, farmer confirms resolution | Registries (change requests in AWE), the farmer channel | 8 | Corrections and grievances with service levels |
| 10 | Map Registry: parcels with a unique ID, surveyed polygon and accuracy tier, kept by the land or survey department; the Farmer Registry and Crop Sown Registry refer to parcels by ID | A new registry on the registry platform (as the Livestock Registry) | — | Map Registry |
| 11 | Crop records checked against the parcel (location within the polygon) and against a satellite crop map; disagreements listed for field checks | Crop Sown Registry | 10 | Crop records checked against the parcel and imagery |
| 12 | Ownership and tenancy as dated events with evidence, on parcels | Map Registry or Farmer Registry (activity register) | 10 (preferably) | [Land ownership as events](README.md#functional-in-order) |
| 13 | Publish the factors and other non-personal aggregates by district, crop and season | Public catalogue | 6; public catalogue on the internet | Open aggregate data |

The roadmap items are in [Phase 2](README.md#phase-2-farmers-partners-and-the-open-agri-network) unless linked to Phase 1.
