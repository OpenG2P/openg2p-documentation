---
description: >-
  Agri Stack is the digital public infrastructure (DPI) for agriculture:
  sovereign departmental registries, shared reference data, and the shared
  services that let partners use farmer data with the farmer's consent.
---

# Agri Stack

{% hint style="info" %}
**Source code:** [github.com/openg2p/agri-stack](https://github.com/openg2p/agri-stack) (the Composite), [github.com/OpenG2P/crop-sown-registry](https://github.com/OpenG2P/crop-sown-registry), [github.com/OpenG2P/farmer-registry](https://github.com/OpenG2P/farmer-registry) and [github.com/OpenG2P/registry-platform](https://github.com/OpenG2P/registry-platform).
{% endhint %}

## At a glance

<figure><img src="../.gitbook/assets/open-agri-stack-overview.svg" alt="Agri Stack. Above it, farmer services offered by banks, insurers, government programmes and agritechs, with the farmer's consent; for example credit, insurance, subsidies, market access, advisory and more. A use case for a farmer reaches Agri Stack through its API. Agri Stack has three layers: the Exchange for consented data sharing (national-ID login, Composite, consent, Partner Management); the registries, systems of record, each run by its own department and each issuing verifiable credentials (Farmer Registry, Crop Sown Registry, Livestock Registry, Land Registry); and the catalogues, a public common vocabulary (crop, seed, inputs, livestock, location, land)."><figcaption><p>Concept: Agri Stack makes farmer data available, with consent, to the farmer services offered in a country</p></figcaption></figure>

## What it is

Agri Stack is the digital public infrastructure (DPI) for agriculture. It has four parts:

* **Registries:** the functional registries (farmer, crop sown, livestock, DA), each run by its department.
* **Catalogues:** the reference data every registry uses (datasets such as crop types, units and seed varieties, geography).
* **Platform services:** Partner Management, Consent Manager and Audit Manager. Every install has its own.
* **[The Exchange](architecture/exchange.md)** (the data exchange layer): where service providers (banks, MFIs, agritechs: **partners**) onboard once and use one farmer consent across registries: the partner portal, the Exchange's own Consent Manager and Partner Management, eSignet, and the Composite (the Exchange's use-case service).

These pages describe how a partner gets farmer data held across the registries: who routes a request, who decides what may be shared, and who enforces it.

## Registries

Each department runs its own registry on the OpenG2P [registry platform](../products/registry/registry/README.md). Registries are sovereign: each checks the caller, asks its own Consent Manager what may be released, and releases only that. Registries share **data**, never code.

| Registry | Holds | Kind | Status |
| --- | --- | --- | --- |
| **Farmer Registry (FR)** | Farmers, land parcels, households, declared main crops, livestock (until a Livestock Registry exists) | Registers and child tables (entities) | Built ([Farmer Registry](../products/registry/farmer-registry/README.md)) |
| **Crop Sown Registry (CSR)** | What each farmer plans, prepares, sows, observes and harvests, plot by plot and season by season; clusters | An activity register (occurrences) plus a Cluster register | Built ([Crop Sown Registry](../products/registry/crop-sown-registry/README.md)) |
| **Livestock Registry** | Animals and livestock events (born, vaccinated, treated, sold) | An entity register and an activity register | Planned (design only, see [Livestock Registry](design/livestock-registry.md)) |
| **DA Registry** | Development agents | Register | Planned |

The kinds are the registry platform's: a **register** holds changeable records such as farmers, a **table** holds a register record's child rows such as land parcels, and an **[activity register](../products/registry/registry/features/activity-register.md)** holds append-only records of what happened, such as a crop sown or harvested, with figures worked out from them.

All registries are keyed to the same national identifier (Fayda in the reference setup).

## Catalogues, platform services and the Exchange

| Service | Role in Agri Stack |
| --- | --- |
| **Catalogues** | All reference data, defined once for the country; registries hold none of their own: datasets (the core datasets plus the agriculture theme of the country pack in use; ETH ships, its crops following the Ministry of Agriculture's crop variety list), geography, sample people. Served by the OpenG2P [Master Data Service](../platform/platform-services/master-data-service/README.md). Versions, approvals and a change feed: see [how MDS works](../platform/platform-services/master-data-service/README.md#key-features) and [open items](open-items/README.md#catalogues) |
| [Partner Management (PM)](../platform/platform-services/partner-management/README.md) | Trust root for every participant (partners, registries, the Composite): identities, public keys and access policies (what each partner may ask for), approved there. One per install |
| [Consent Manager (CM)](../consent-management/README.md) | The farmer's consent; `/validate` checks it against the partner's policy in PM and tells each registry what it may release. One per install; the Exchange's CM collects consents and issues a consent token per registry |
| **Composite** (in the Exchange) | One generic service that serves approved use cases (e.g. `loan-profile@1`) by querying several registries with one consent and returning one signed response |
| [Approval Workflow Engine (AWE)](../platform/platform-services/approval-workflow-engine/README.md) | Approval of registers' changes |
| [Audit Manager](../platform/platform-services/audit-manager/README.md) | Audit events from every hop, linked by the request ID. One per install |

## Agri Stack and OAN

Agri Stack stands on its own: any authorised partner uses it through its API. A country that also runs an agricultural services network such as the Open Agri Network (OAN), built on Beckn, can make Agri Stack one of that network's providers, so partners on the network reach it with the same order mechanism they use for everything else. That is a proposal, described in [Interoperability with OAN (Beckn)](design/oan-interoperability.md).

<figure><img src="../.gitbook/assets/open-agri-stack-oan-overview.svg" alt="OAN above Agri Stack. OAN holds use cases of value to the farmer, for example access to credit, access to market, grievance, access to payment, and more. A use case for a farmer reaches Agri Stack through Beckn or Agri Stack's own API. Agri Stack has the Exchange for consented data sharing, the departments' registries and the public catalogues."><figcaption><p>Concept: Agri Stack with OAN on top (proposal)</p></figcaption></figure>
