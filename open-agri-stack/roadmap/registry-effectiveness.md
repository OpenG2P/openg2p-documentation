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

## What Agri Stack can measure

| Factor | What exists | What is missing |
| --- | --- | --- |
| Coverage | The registries' record counts by location, in their reporting views and Superset dashboards | The denominators come from outside: the eligible farmers (e.g. from the land records or a census) and the plots chosen for the crop survey. They would be loaded per location and season, e.g. as catalogue datasets |
| Quality | Completeness of fields; change requests and their approval (AWE); verification of some activities (e.g. vaccinations in the Livestock Registry); last-updated dates | One verification model with who verified what, when and with what evidence ([Attestation on records](README.md#functional-in-order)); timelines per kind of change, to tell a current record from a stale one; links checked across registries (a crop record's parcel exists; with a Map Registry, the crop's location lies within it) |
| Usage | The Exchange Consent Manager's access log: each use of a farmer's consent, by partner. The Composite's and registries' audit events record outcomes per request but, by design, no subject identifiers | Usage per record per period, from the consents used (or, under [sharing on a mandate](README.md#functional-in-order), from the mandate's audited uses); only successful answers counted. Services that do not go through the Exchange (a department using its own registry) would need their own outcome logs |
| Trust | Nothing in the software: it is a field survey | Supporting features that earn trust: farmers seeing their records and consents, asking for corrections, following grievances with deadlines, and the SMS and recourse already planned for consent |

The breakdowns (gender, location, holding size, farmer category) need those attributes on the records being counted; for figures that combine registries (e.g. crop records by the farmer's gender) this depends on the cross-registry figures planned under **Dashboards and cross-registry figures**.

Out of scope for the software: running the trust survey, setting the eligible populations, and choosing the services that count as usage. These are the programme's decisions, made by each country.

## Roadmap items

From this study, in [Phase 2](README.md#phase-2-farmers-partners-and-the-open-agri-network):

1. **Corrections and grievances with service levels**
2. **Registry effectiveness figures**
3. **Map Registry**
4. **Crop records checked against the parcel and imagery**
5. **Open aggregate data**
