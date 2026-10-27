---
description: >-
  Agri Stack components, the layers they belong to, and who talks to whom
  when a partner asks for farmer data.
---

# Architecture & Concepts

## Components and who talks to whom

<figure><img src="../../.gitbook/assets/open-agri-stack-components.svg" alt="Agri Stack in layers: the partner on top; the Exchange, its own install behind its own ingress (partner portal, Composite, eSignet, Consent Manager, Partner Management, catalogue, Audit Manager); below it the departments, each running its registry install behind its own ingress with its own Consent Manager, Partner Management, catalogue and Audit Manager (Department A: Farmer Registry; Department B: Crop Sown Registry). Paths: A, a partner uses one registry directly; B1 to B6, distributed registries through the Composite; C, one registry as a partner of another"><figcaption><p>Components of Agri Stack, across departments</p></figcaption></figure>

| Colour | Part |
| --- | --- |
| Blue | Registries (systems of record) |
| Ochre | Catalogues (reference data) |
| Teal | Platform services (Partner Management, Consent Manager, Audit Manager), and the Exchange's partner portal and eSignet |
| Green | The Composite (the Exchange's use-case service) |

**Departments and installs.** Each department runs its own Kubernetes cluster, behind its own ingress (Nginx, Istio): the public entry point for everything in that cluster. An **install** is one namespace in a cluster with its own commons: Partner Management, Consent Manager, Audit Manager and catalogue. Each registry is its own install. The **Exchange** (the data exchange layer: partner portal, Consent Manager, Partner Management, eSignet, the Composite) is one more install, above the departments ([The Exchange](exchange.md)). It can run in its own cluster or share one with a department; either way it is a separate install, with its own Partner Management, Consent Manager and Audit Manager.

**A — a partner uses one registry directly (no Composite).** The partner is onboarded in that registry's Partner Management, with a scope policy for that registry, and calls the registry's partner API (DCI): searching a farmer by ID with no consent (the registry's Consent Manager finds the one it holds), or, if its policy allows, with a consent it signed itself. The registry checks the signature at its own Partner Management and the consent at its own Consent Manager, and releases only the effective scopes. Every registry shares data this way, Composite or not.

**B — distributed registries, through the Composite** (the OAN layer). The partner onboards once, in the Exchange, and uses one consent for several registries. The Composite runs only approved use cases (each a configuration file, such as `loan-profile`); there is no general query engine across registries.

1. **Consent request.** The partner asks for the farmer's consent at the Exchange's Consent Manager, for example from the partner portal.
2. **Consent.** The farmer gives it through one of several mechanisms ([consent](consent.md#how-a-farmer-gives-consent)), always proving who they are with the national ID (eSignet). Once it is active, the partner can use it.
3. **Query.** The partner's system sends a signed query to the Composite with the consent's ID, or with none (the Exchange's Consent Manager finds it), or, if its policy allows, a consent the partner signed.
4. **Consent tokens.** The Composite asks the Exchange's Consent Manager for one signed consent token per registry, with only the scopes the use case needs.
5. **Search.** The Composite searches each registry with its consent token, through that department's ingress.
6. **Check.** Each registry checks its consent token at its **own** Consent Manager, which trusts the Exchange's consent tokens: it checks them offline with the Exchange CM's public keys and never calls the Exchange, and applies the department's ceiling for the Composite (a scope policy in its Partner Management).

**C — registry to registry (not in use today).** A registry that needs another's data is simply one of its partners: onboarded in its Partner Management with a scope policy there, no Composite involved. The reference design is crop activity from the Crop Sown Registry kept in the Farmer Registry, through the registries' outgestion and ingestion and a small relay (not built): [registry data sync](../design/registry-data-sync.md), including [how it would be set up](../design/registry-data-sync.md#how-it-would-be-set-up). Sharing of this kind usually rests on a mandate rather than each farmer's consent; the Consent Manager's rule for that (a standing permission for a purpose) is an [open item](../open-items/README.md).

* The ingress (dashed grey: OpenG2P deployment infrastructure, not an Agri Stack service) routes requests but never reads data. The Composite runs only approved use cases and keeps nothing after it responds.
* Beckn appears only at the OAN network layer, for discovering service providers and consumers. It isn't used to exchange registry data today; a proposal makes the Composite a provider on that network: [Interoperability with OAN (Beckn)](../design/oan-interoperability.md).

## Components and source code

Every component in the diagram, what it does, and where its source code is. All are open source under the Mozilla Public License 2.0, except eSignet (MOSIP, under its own open-source licence).

| Layer | Component | What it does | Source code |
| --- | --- | --- | --- |
| Registries | [Farmer Registry](../../products/registry/farmer-registry/README.md) | Farmers, their households, land parcels and declared crops; links the Farmer ID to the national ID | [OpenG2P/farmer-registry](https://github.com/OpenG2P/farmer-registry) |
| Registries | [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md) | What each farmer plans, sows and harvests, plot by plot and season by season | [OpenG2P/crop-sown-registry](https://github.com/OpenG2P/crop-sown-registry) |
| Registries | Livestock Registry | Animals and livestock events ([design](../design/livestock-registry.md)) | Not built yet |
| Registries | [Registry Platform](../../products/registry/registry/README.md) | The platform every registry is built on: registers, activity registers, partner APIs, consent enforcement, verifiable credentials | [OpenG2P/registry-platform](https://github.com/OpenG2P/registry-platform) |
| Catalogues | [Master Data Service](../../platform/platform-services/master-data-service/README.md) | The catalogues: datasets (crops, seeds, units, …) and geography, versioned; public read API | [OpenG2P/master-data-service](https://github.com/OpenG2P/master-data-service) |
| Catalogues | Country packs | A country's datasets and geography, loaded into the Master Data Service | [OpenG2P/openg2p-data](https://github.com/OpenG2P/openg2p-data) |
| Exchange | [Composite](../composite/README.md) | Serves approved use cases: one query, several registries, one signed answer | [OpenG2P/agri-stack](https://github.com/OpenG2P/agri-stack) |
| Exchange and every install | [Consent Manager](../../consent-management/README.md) | The farmer's consent: collected (partner portal), checked, and turned into a consent token per registry | [OpenG2P/consent-manager](https://github.com/OpenG2P/consent-manager) |
| Exchange and every install | [Partner Management](../../platform/platform-services/partner-management/README.md) | Partners, their keys and their access policies | [OpenG2P/partner-management](https://github.com/OpenG2P/partner-management) |
| Exchange | National-ID login (eSignet) | The farmer proves who they are with the national ID | [mosip/esignet](https://github.com/mosip/esignet) |
| Every install | [Audit Manager](../../platform/platform-services/audit-manager/README.md) | Audit events from every hop | [OpenG2P/audit-manager](https://github.com/OpenG2P/audit-manager) |
| Every install | [Approval Workflow Engine](../../platform/platform-services/approval-workflow-engine/README.md) | Approval of changes to registry records | [OpenG2P/awe](https://github.com/OpenG2P/awe) |
| Every install | [IAM](../../identity-and-access-management/README.md) | Staff login and roles | [OpenG2P/iam](https://github.com/OpenG2P/iam) |
| Every install | Commons | The Helm charts that install the shared services in each namespace | [OpenG2P/commons](https://github.com/OpenG2P/commons) |

## Across departments

Each department runs its registries for its own work: its staff, approvals, partners and use cases. It must not depend on another department being up, or on another department's partners and consents. OAN partners, on the other hand, need one onboarding and one consent for all registries. Separate installs give the first; the Exchange gives the second.

| Part | Where | Note |
| --- | --- | --- |
| Composite | Exchange | Path B. Partners can still call a registry directly (path A) |
| Partner Management, Consent Manager | Every install | A registry's for its own partners and the Composite; the Exchange's for OAN partners and the farmer's consent. Access policies are held and approved in Partner Management; the Consent Manager holds consents only |
| Audit Manager | Every install | Each department audits access to its data, including calls from the Composite on behalf of a partner. The Exchange audits who asked what |
| Catalogue | Every install | Codes and geography must match across registries, or the Composite cannot join their data. Today each install loads the same country pack version; a central catalogue is an [open item](../open-items/README.md#catalogues) |
| Farmer identity | Every registry | The national ID and the Farmer ID are the join key across registries |
| Verifiable credentials | Each registry | Each registry issues under its own issuer identity; verification is public |
| Keycloak, IAM, AWE, Kafka, Redis, object store, databases | Each install | Internal. Registry data leaves its department only through the registry's APIs |

**To each department, the Exchange is one partner.** The department's Partner Management holds the Composite's public key and its scope policy per registry (the department's ceiling), and its Consent Manager trusts the Exchange's consent tokens. The department decides at its own boundary what leaves its registry: see [how departments trust the Exchange](exchange.md#how-departments-trust-it), [data-sharing policies](data-sharing-policies.md) and [request flow](request-flow.md).

**Standalone installs are not affected.** The Exchange settings in commons are opt-in and off by default. A registry installed without the Exchange checks partners and consents at its own Partner Management and Consent Manager, as in path A; the registry itself is the same in both cases.

**Networking.** Each department's partner-facing APIs (the registries' partner APIs; at the Exchange, the Composite, the Consent Manager's partner API and partner portal) are on public hostnames on its own ingress. Staff UIs and admin APIs can stay on an internal gateway reached over WireGuard. Calls between departments use those public hostnames, protected by signed requests with keys in Partner Management, not shared Keycloak tokens: each department is a partner of the services it calls, and no secrets are exchanged. A gateway between departments with mutual TLS is an [open item](../open-items/README.md#platform-and-build).

{% hint style="info" %}
How the departments and the Exchange are installed and set up: [Deployment](../deployment/README.md#topology).
{% endhint %}

## Entry point: the OpenG2P deployment, not a separate API gateway

Agri Stack has **no API gateway product**. Partners reach it through the ingress of the [OpenG2P deployment](../../deployment/openg2p-deployment-model.md), as for every OpenG2P service. What an API gateway usually provides is covered as follows:

| API gateway feature | In the OpenG2P deployment |
| --- | --- |
| Single public entry point, TLS, routing | Nginx and the Istio ingress gateway, a VirtualService per service |
| Partner authentication | Each service verifies the partner's signature over the request body against [Partner Management](../../platform/platform-services/partner-management/README.md) |
| Access control | Each partner's use-case policies (one per use case) in the Exchange's Partner Management, checked by the Composite on every call; Istio `AuthorizationPolicy` to limit registries' partner APIs to the Composite (to do) |
| Rate limits and quotas | In the Composite, which knows the partner on every request: per pod today, shared across pods and daily quotas to do |
| Usage reports | Audit events from every hop, in the Audit Manager |
| mTLS between services, timeouts, retries, circuit breaking | Istio |
| Developer portal | The [partner guide](../partner-guide.md) and the Composite's describe endpoints |

{% hint style="info" %}
A gateway product is worth adding only if many partner-facing APIs from different teams need a common portal, keys, analytics or billing, or if a national API gateway is mandated. It would then sit in front of the Composite, unchanged.
{% endhint %}
