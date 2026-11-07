---
description: How Agri Stack is put together.
---

# Architecture

**Registries are distributed.** Agri Stack does not assume that all registries sit in one department or one system. Each department runs its own registry, in its own install and often its own cluster, for its own work, and stays in control of its data. The **Exchange** is one more install above them: it lets a partner onboard once and use one farmer consent across several registries, without centralising any data. A registry works the same with or without the Exchange.

<figure><img src="../../.gitbook/assets/open-agri-stack-components.svg" alt="Agri Stack in layers: the partner on top; the Exchange, its own install behind its own ingress (partner portal, Composite, eSignet, Consent Manager, Partner Management, catalogue, Audit Manager); below it the departments, each running its registry install behind its own ingress with its own Consent Manager, Partner Management, catalogue and Audit Manager (Department A: Farmer Registry; Department B: Crop Sown Registry). Paths: A, a partner uses one registry directly; B1 to B6, distributed registries through the Composite; C, one registry as a partner of another"><figcaption><p>Components of Agri Stack, across departments</p></figcaption></figure>

## The Exchange

Its own install ([Exchange](exchange.md)). **Everything goes through a use case:** a partner never asks for arbitrary data, only for a use case it is assigned (for example a farmer's loan profile), which says exactly what is read from each registry ([Use Cases](use-cases.md)).

| Component | Role |
| --- | --- |
| [Composite](../composite/README.md) | The partners' entry point: runs approved use cases across registries and returns one signed answer; keeps no farmer data |
| Partner portal (part of the [Consent Manager](../../consent-management/README.md)) | Partner staff raise consent requests and record the farmer's consent and evidence |
| [Consent Manager](../../consent-management/README.md) | Holds the farmers' consents; issues a consent token per registry for each query |
| [Partner Management](../../platform/platform-services/partner-management/README.md) | Partners, their keys, and the use cases each may call |
| eSignet | The farmer's login with the national ID |
| Catalogue, Audit Manager | The shared codes; who asked for what |

## Department registries

Each department is its own install, with its registry and its own services:

| Component | Role |
| --- | --- |
| Registry ([Farmer Registry](../../products/registry/farmer-registry/README.md), [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md)) | The system of record; serves its partners through its partner API ([Registries](../registries/README.md)) |
| Consent Manager | Checks each consent, including the Exchange's consent tokens |
| Partner Management | The department's partners, and what it releases to the Composite (the Composite's scope policy) |
| Catalogue, Audit Manager | The same codes as every install (one country pack); who accessed the department's data |

Registries are joined on the farmer's Farmer ID; the national ID only authenticates the farmer. Other departments (Livestock, Land, …) follow the same pattern.

## Infrastructure

Each install is a namespace on Kubernetes, installed with the OpenG2P Helm charts. A department runs its own cluster; the Exchange runs in its own or shares one. The ingress of each cluster (Nginx, Istio) is the API gateway: TLS, routing and edge limits. Each service checks the caller's signature against its Partner Management, and the Composite enforces per-partner rate limits ([API Gateway](networking-and-gateway.md)). Installs call each other only over public hostnames with signed requests; staff portals can stay on an internal gateway. Installing: [Deployment](../deployment/README.md).

## Partners and farmers

| Who | How they take part |
| --- | --- |
| Partner (bank, MFI, agritech) | Its system calls the Composite, or a registry directly; its staff use the partner portal ([Partner Integration Guide](../partner-integration-guide.md)) |
| Farmer | Gives consent, logging in with the national ID through eSignet ([Consent](consent.md)) |

## Data-sharing paths

The letters in the diagram:

**A — a partner uses one registry directly (no Composite).** The partner is onboarded in that registry's Partner Management, with a scope policy for that registry, and calls the registry's partner API (DCI): searching a farmer by ID with no consent (the registry's Consent Manager finds the one it holds), or, if its policy allows, with a consent it signed itself. The registry checks the signature at its own Partner Management and the consent at its own Consent Manager, and releases only the effective scopes. Every registry shares data this way, Composite or not.

**B — distributed registries, through the Composite** (the OAN layer). The partner onboards once, in the Exchange, and uses one consent for several registries. The Composite runs only approved use cases (each a configuration file, such as `loan-profile`); there is no general query engine across registries.

1. **Consent request.** The partner asks for the farmer's consent at the Exchange's Consent Manager, for example from the partner portal.
2. **Consent.** The farmer gives it through one of several mechanisms ([consent](consent.md#how-a-farmer-gives-consent)), always proving who they are with the national ID (eSignet). Once it is active, the partner can use it.
3. **Query.** The partner's system sends a signed query to the Composite with the consent's ID, or with none (the Exchange's Consent Manager finds it), or, if its policy allows, a consent the partner signed.
4. **Consent tokens.** The Composite asks the Exchange's Consent Manager for one signed consent token per registry, with only the scopes the use case needs.
5. **Search.** The Composite searches each registry with its consent token, through that department's ingress.
6. **Check.** Each registry checks its consent token at its **own** Consent Manager, which trusts the Exchange's consent tokens: it checks them offline with the Exchange CM's public keys and never calls the Exchange, and applies the Composite's scope policy (in its Partner Management).

**C — registry to registry (not in use today).** A registry that needs another's data is simply one of its partners: onboarded in its Partner Management with a scope policy there, no Composite involved. The reference design is crop activity from the Crop Sown Registry kept in the Farmer Registry, through the registries' outgestion and ingestion and a small relay (not built): [registry data sync](../roadmap/registry-data-sync.md), including [how it would be set up](../roadmap/registry-data-sync.md#how-it-would-be-set-up). Sharing of this kind usually rests on a mandate rather than each farmer's consent; a Partner Management policy for that (a standing permission for a purpose) is on the [Roadmap](../roadmap/README.md).

**To each department, the Composite is one partner,** and the department decides at its own boundary what leaves its registry ([Composite as a partner](exchange.md#composite-as-a-partner), [request flow](request-flow.md)). Beckn is used only at the OAN layer, for discovery; it does not carry registry data ([Interoperability with OAN](../roadmap/oan-interoperability.md)).

Versions and source code of each component: [Versions & Source Code](../versions/README.md).
