---
description: >-
  Agri Stack is the digital public infrastructure (DPI) for agriculture:
  sovereign departmental registries, shared reference data, and the shared
  services that let partners use farmer data with the farmer's consent.
---

# Agri Stack

<figure><img src="../.gitbook/assets/open-agri-stack-logo.jpg" alt="Agri Stack — DPI for Agriculture" width="160"><figcaption></figcaption></figure>

{% hint style="info" %}
**Source code:** [github.com/openg2p/agri-stack](https://github.com/openg2p/agri-stack) (the Composite), [github.com/OpenG2P/crop-sown-registry](https://github.com/OpenG2P/crop-sown-registry), [github.com/OpenG2P/farmer-registry](https://github.com/OpenG2P/farmer-registry) and [github.com/OpenG2P/registry-platform](https://github.com/OpenG2P/registry-platform).
{% endhint %}

## What it is

Agri Stack is the digital public infrastructure (DPI) for agriculture. It has four parts:

* **Registries:** the functional registries (farmer, crop sown, livestock, DA), each run by its department.
* **Catalogues:** the reference data every registry uses (datasets such as crop types, units and seed varieties, geography).
* **Platform services:** Partner Management, Consent Manager and Audit Manager. Every install has its own.
* **The Exchange** (the data exchange layer): where service providers (banks, MFIs, agritechs: **partners**) onboard once and use one farmer consent across registries: the partner portal, the Exchange's own Consent Manager and Partner Management, eSignet, and the Composite (the Exchange's use-case service).

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
| **Catalogues** | All reference data, defined once for the country; registries hold none of their own: datasets (the core datasets plus the agriculture theme of the country pack in use; ETH ships, its crops following the Ministry of Agriculture's crop variety list; see [catalogue content](open-items/catalogue-content.md)), geography, sample people. Served by the OpenG2P [Master Data Service](../platform/platform-services/master-data-service/README.md). Versions, approvals and a change feed: see [how MDS works](../platform/platform-services/master-data-service/README.md#key-features) and [open items](open-items/README.md#catalogues) |
| [Partner Management (PM)](../platform/platform-services/partner-management/README.md) | Trust root for every participant (partners, registries, the Composite): identities and public keys. One per install |
| [Consent Manager (CM)](../consent-management/README.md) | The farmer's consent and, today, the data-share policies; `/validate` tells each registry what it may release. One per install; the Exchange's CM collects consents and issues a consent token per registry |
| **Composite** (in the Exchange) | One generic service that serves approved use cases (e.g. `loan-profile@1`) by querying several registries with one consent and returning one signed response |
| [Approval Workflow Engine (AWE)](../platform/platform-services/approval-workflow-engine/README.md) | Approval of registers' changes; approval of policies is optional and off by default |
| [Audit Manager](../platform/platform-services/audit-manager/README.md) | Audit events from every hop, linked by the request ID. One per install |

## Map of this section

What is built today, and what is still design: [TODOs & Open Items](open-items/README.md#what-is-built).

| Part | Pages |
| --- | --- |
| **[Architecture and concepts](architecture/README.md)** | Components and who talks to whom; [consent](architecture/consent.md); [data-sharing policies](architecture/data-sharing-policies.md); [request flow](architecture/request-flow.md); [terms](architecture/terms.md); [standards](architecture/standards.md) |
| **[Design](design/README.md)** | [Registry data sync](design/registry-data-sync.md); [Livestock Registry](design/livestock-registry.md) |
| **[Composite](composite/README.md)** | The partners' entry point: design; [Composite API](composite/api.md); [use-case configuration](composite/use-case-configuration.md); [adding a data source](composite/adding-a-data-source.md); [Composite console](composite/console.md); [running the Composite locally](composite/running-locally.md) |
| **[Deployment](deployment/README.md)** | Topology, install order and the names that must match; installing the [Exchange](deployment/exchange.md), the [Farmer Registry](deployment/farmer-registry.md), the [Crop Sown Registry](deployment/crop-sown-registry.md) and the [Composite](deployment/composite.md); [after install](deployment/after-install.md); [testing](deployment/testing.md); [upgrades and uninstall](deployment/upgrades-and-uninstall.md); [separate clusters](deployment/separate-clusters.md) |
| **[Partner guide](partner-guide.md)** | For banks, MFIs and agritechs: joining Agri Stack and calling a use case end to end |
| **[TODOs and open items](open-items/README.md)** | Decisions and checks still pending; [service guide notes](open-items/service-guide-notes.md) |
