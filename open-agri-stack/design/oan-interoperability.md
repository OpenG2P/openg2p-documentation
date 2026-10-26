---
description: >-
  Proposal: the Composite as a provider node on the Open Agri Network (OAN),
  so partners already on the network reach Agri Stack use cases through the
  Beckn order flow, via a beckn-onix adapter. Not built.
---

# Interoperability with OAN (Beckn)

**Status: proposal, not built.** Today partners call the [Composite](../composite/README.md) through its own API ([Composite API](../composite/api.md)).

**Concept.** At a high level, OAN's use-case services sit on top of Agri Stack, which provides consented data sharing (the Exchange), the departments' registries and the public catalogues:

<figure><img src="../../.gitbook/assets/open-agri-stack-oan-overview.svg" alt="OAN above Agri Stack. OAN holds use-case services of value to the farmer, for example access to credit, access to market, grievance, access to payment. Agri Stack has three layers: the Exchange for consented data sharing (national-ID login, Composite, consent, Partner Management); the registries, systems of record, each run by its own department and each issuing verifiable credentials (Farmer Registry, Crop Sown Registry, Livestock Registry, Land Registry); and the catalogues, a public common vocabulary (crop, seed, inputs, livestock, location, land). OAN asks for a use case for a farmer, through Beckn or Agri Stack's own API; the Exchange searches each registry with its consent token."><figcaption><p>Concept: OAN and Agri Stack at a high level (the registries a country may run)</p></figcaption></figure>

## Why

Agri Stack is foundational: layers above it, such as the Open Agri Network (OAN), are built on the [Beckn](https://becknprotocol.io/) protocol. Asking every partner to build a client specific to the Composite is a real barrier, while partners on OAN will implement Beckn anyway. If the Composite is a node on the network, a partner reaches Agri Stack with the same order mechanism it uses for everything else on OAN.

## The idea

The Composite takes part in OAN as a **provider (BPP)**. A partner, as a consumer app (BAP), orders a use case for a farmer and receives the result as the order's fulfilment.

**It is not a marketplace.** A partner uses a use case only after it has been onboarded in Agri Stack's Partner Management and granted that use case, so it already knows Agri Stack's provider address and what it may order. It sends its order straight to Agri Stack's provider platform, starting at `select` or `init`; Beckn allows this without a network `search` when the consumer knows the provider. A participant without a grant gets a Beckn error, as the Composite's API answers 403 `partner_not_allowed` today. Onboarding and grants stay in Partner Management, outside Beckn.

<figure><img src="../../.gitbook/assets/open-agri-stack-oan-beckn.svg" alt="Agri Stack as a provider on the OAN Beckn network: the bank, a network participant, orders a use case for a farmer (it was onboarded and granted it beforehand; listing the use cases on the network is optional and for information only) (select, init, confirm) through Agri Stack's entry point, its provider platform; the Composite answers with on_confirm and on_status. Agri Stack's entry point is registered in the network registry, from which Partner Management can take participants' keys. Inside Agri Stack: the Exchange (Composite, Consent Manager, Partner Management, partner portal, national-ID login, Audit Manager), the departments' registries, each issuing verifiable credentials, and the catalogues. Path A is a plain API call to one registry; path C, one registry as a partner of another."><figcaption><p>Architecture: Agri Stack under OAN, in Beckn terms (proposal; the registries built today)</p></figcaption></figure>

This fits because the Composite already works at the level of **use cases** (e.g. `loan-profile@1`), not individual data scopes: a use case is a natural item to order.

| Beckn step | What it means for the Composite |
| --- | --- |
| `discover` / `search` | Optional, for information only: published use cases, each with its purpose and what it returns, for prospective partners to see what they could apply for. Not part of a request |
| `select` / `init` | The onboarded partner names a use case it is granted, the farmer and the parameters (e.g. crop year, season). The Composite checks the partner's [policy for that use case](../architecture/data-sharing-policies.md). If the farmer has not consented yet, the provider's form step (Beckn XInput) sends the farmer to the Consent Manager's screen to log in with the national ID and approve |
| `confirm` | The order: the query runs. The Exchange Consent Manager finds the consent and issues a [consent token](../../consent-management/design/exchange-consent-tokens.md) per registry; the registries answer |
| `on_confirm` / `on_status` | The fulfilment: the signed result, with a status per source |

Consent through the XInput step would bring consent [scenarios 2 and 3](../architecture/consent.md) (the farmer approving on the Consent Manager's own screen) into the partner's own Beckn flow, with nothing consent-specific for the partner to build.

## How it would be built

* **beckn-onix in front of the Composite.** The Beckn reference implementation handles what a network participant needs: signing, registry lookups, gateway traffic and asynchronous callbacks. A thin adapter behind it maps Beckn messages to the Composite's existing use-case query. The Composite's engine, the consent lookup and the consent tokens stay as they are.
* **Two front doors, one engine.** The current API stays, for partners outside OAN (for example a ministry system). Beckn is one interface, as DCI is one output format: designs stay standard-neutral.

## What would need to be built or decided

* **Identity and keys.** A partner is a network participant (`subscriber_id`, its key in the network registry). Partner Management still holds it as a partner with its policy for each use case. Map `subscriber_id` to the Partner Management partner, and let Partner Management take the partner's key from the network registry, so an organisation is onboarded once.
* **Asynchronous answers.** The result goes back through the partner's callback, so the Composite answers asynchronously. Natural in Beckn; new for the Composite.
* **Farmer data in Beckn messages.** Orders (`select` to `status`) go directly between partner and provider, not through the network gateway, so farmer data never passes through the gateway, only within an order. How the result travels (inline, or a short-lived signed link) and whether it is encrypted to the partner are still to be decided.
* **Listing use cases on the network (optional).** A shop window for prospective partners, not a way in: ordering still needs onboarding and a grant. Whether to list them at all is open.

## How it relates to the architecture

* Path B in the [architecture](../architecture/README.md#components-and-who-talks-to-whom) is unchanged behind the adapter: one consent, a consent token per registry, each department deciding with its own Consent Manager and ceiling.
* Today Beckn appears only at the OAN layer, for discovering service providers and consumers; this proposal adds the Composite as a provider on that network.

## Catalogues and OAN

**Not needed.** Agri Stack's catalogues (Master Data Service) are public data, and their public API already follows open standards: a W3C DCAT catalogue to find datasets, SKOS for code lists, CSV, JSON and GeoJSON downloads, HTTP caching to notice changes, and licence URIs ([MDS standards at a glance](../../platform/platform-services/master-data-service/standards.md#at-a-glance-what-a-public-consumer-uses)). Anyone in the country, on OAN or not, reads them with ordinary open-data tools. Only the staff API (editing and approval) is MDS's own, and it stays internal.

**If OAN does want them on the network**, the suggested approach:

* **Make them findable, not orderable.** Reading public reference data needs no consent and no order. Agri Stack's provider platform can answer a network `search` with the catalogue as an item whose description links to the DCAT catalogue and the downloads; consumers then read them directly. Wrapping each read in `select` / `init` / `confirm` would add ceremony and nothing else.
* **Use the codes as the network's vocabulary.** OAN has no taxonomy of its own. Domain messages on the network (crop, seed, inputs, livestock, location) can carry MDS codes, with the dataset version, as Beckn descriptor codes or tags, so every participant resolves them against the same catalogue.

## Open questions

1. **Which OAN scenario comes first?** Each leads to a different integration point:
   * **Lenders and other providers pulling farmer data** (e.g. to underwrite a loan): the provider is an Agri Stack partner. It may call the Composite through its own API from behind its Beckn node, or Agri Stack is a node it orders from (this proposal).
   * **An OAN app showing the farmer their own data:** a farmer-facing (self-service) path, not the partner API.
   * **Agri Stack itself offering services on the network:** the Composite as a provider (this proposal).
2. **Which OAN domain and specification version** partners will use, and which schema describes a use case as an item to order. This should come from OAN, not be invented by Agri Stack.
3. **How OAN collects consent:** through Beckn XInput forms, a consent artefact or reference carried in the order, or both.
4. **How the result is delivered and protected:** inline in `on_confirm`/`on_status`, or a short-lived signed link; whether it is encrypted to the partner's key.
5. **Onboarding:** whether a network participant's registry entry is enough for Partner Management, or a separate Partner Management approval is still required for each use case (today it is).
6. **Catalogues on the network:** whether OAN wants the catalogues discoverable through network `search`, and whether its domain messages will carry the catalogue codes.
