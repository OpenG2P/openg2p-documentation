---
description: >-
  Open Agri Stack components, the layers they belong to, and who talks to whom
  when a partner asks for farmer data.
---

# Architecture & Concepts

## Components and who talks to whom

<figure><img src="../../.gitbook/assets/open-agri-stack-components.svg" alt="Components: service provider → API gateway → use-case composite → departmental registries; registries validate with CM, which reads policy from PM; Layer 2 reference services below"><figcaption><p>Components of Open Agri Stack</p></figcaption></figure>

| Colour | Layer |
| --- | --- |
| Blue | Layer 1: functional registries (system of record) |
| Ochre | Layer 2: reference / master data (all in MDS) |
| Teal | Layer 3: shared DPI |
| Green | Layer 4: use-case service |

* Every registry sends `/validate` to the Consent Manager; the single arrow in the diagram stands for all four.
* The gateway routes requests but never reads data.
* The composite runs only for approved use cases and keeps nothing after it responds.
* Beckn appears only at the OAN network layer, for discovering service providers and consumers. It isn't used to exchange registry data.

{% hint style="info" %}
The diagram labels CM as "farmer consent, one per registry". That has changed: the partner requests and presents **one consent**, with a grant per registry inside it (see [consent model](consent-model.md)). The diagram also shows the planned API gateway and the policies in PM, which are not built yet ([open items](../open-items/README.md)).
{% endhint %}

## Who does what

* **Partner Management (one instance).** The trust root for every participant: service providers, registries and composites. In the target design it also holds the **data-share policies** (moved here from CM), split into one section per department, and records which partners are associated with each policy. Today the policies are still in CM.
* **Consent Manager (one instance).** Holds the farmer's individual consent. `/validate` returns what the farmer consented to, intersected with the calling registry's policy.
* **Registries (one per department).** Each one is sovereign: it checks the caller, calls `/validate`, and releases only the effective scopes. All of them are keyed to the same Fayda-based identifier.
* **API gateway and composites.** The gateway is the single public entry point. Data from several registries is merged only in narrow composite services built for one purpose each, such as `credit-profile`. There is no general query engine across registries. Each use case is a configuration file loaded by one generic composite service (see [use-case composite](../design/use-case-composite.md)).
* **AWE.** Each department approves its own section of a policy.
* **Audit Manager.** Receives audit events from every hop, linked by the request ID.

## Why not X-Road, IUDX or a data-space connector

* **X-Road** secures transport between organisations, but it has no consent handling, field-level policy or aggregation. It's only worth adding if the government mandates a national interoperability layer. In that case it would carry the DCI calls, and everything described here would sit on top unchanged.
* **IUDX** is out of scope.
* **Eclipse Dataspace Components** duplicate PM and CM and bring a heavy Java stack. We borrow only their vocabularies: DCAT and ODRL.

## In this part

| Page | Covers |
| --- | --- |
| [Request flow](request-flow.md) | One request, end to end |
| [Policy and consent](policy-and-consent.md) | What gets released; policy vs use case vs consent |
| [Consent model](consent-model.md) | One consent for the partner, one grant per registry |
| [Registry model](registry-model.md) | Register, table and activity-register kinds; projections; the Layer 2 split |
| [Register vs activity register](register-vs-activity-register.md) | How the two kinds differ, as built |
| [Terms](terms.md) | Validation, change, correction, void, approval of changes, verification, dispute |
