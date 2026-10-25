---
description: >-
  Proposal: the Composite as a provider node on the Open Agri Network (OAN),
  so partners already on the network reach Agri Stack use cases through the
  Beckn discover-and-order flow, via a beckn-onix adapter. Not built.
---

# Interoperability with OAN (Beckn)

**Status: proposal, not built.** Today partners call the [Composite](../composite/README.md) through its own API ([Composite API](../composite/api.md)).

## Why

Agri Stack is foundational: layers above it, such as the Open Agri Network (OAN), are built on the [Beckn](https://becknprotocol.io/) protocol. Asking every partner to build a client specific to the Composite is a real barrier, while partners on OAN will implement Beckn anyway. If the Composite is a node on the network, a partner reaches Agri Stack with the same discover-and-order mechanism it uses for everything else on OAN.

## The idea

The Composite takes part in OAN as a **provider (BPP)**. Its catalogue is its published use cases. A partner, as a consumer app (BAP), discovers a use case, orders it for a farmer, and receives the result as the order's fulfilment.

This fits because the Composite already works at the level of **use cases** (e.g. `loan-profile@1`), not individual data scopes: a use case is a natural catalogue item.

| Beckn step | What it means for the Composite |
| --- | --- |
| `discover` / `search` | The catalogue: published use cases, each with its purpose and what it returns |
| `select` / `init` | The partner picks a use case and names the farmer and the parameters (e.g. crop year, season). The Composite checks the partner's [policy for that use case](../architecture/data-sharing-policies.md). If the farmer has not consented yet, the provider's form step (Beckn XInput) sends the farmer to the Consent Manager's screen to log in with the national ID and approve |
| `confirm` | The order: the query runs. The Exchange Consent Manager finds the consent and issues a [consent token](../../consent-management/design/exchange-consent-tokens.md) per registry; the registries answer |
| `on_confirm` / `on_status` | The fulfilment: the signed result, with a status per source |

Consent through the XInput step would bring consent [scenarios 2 and 3](../architecture/consent.md) (the farmer approving on the Consent Manager's own screen) into the partner's own Beckn flow, with nothing consent-specific for the partner to build.

## How it would be built

* **beckn-onix in front of the Composite.** The Beckn reference implementation handles what a network participant needs: signing, registry lookups, gateway traffic and asynchronous callbacks. A thin adapter behind it maps Beckn messages to the Composite's existing use-case query. The Composite's engine, the consent lookup and the consent tokens stay as they are.
* **Two front doors, one engine.** The current API stays, for partners outside OAN (for example a ministry system). Beckn is one interface, as DCI is one output format: designs stay standard-neutral.

## What would need to be built or decided

* **Identity and keys.** A partner is a network participant (`subscriber_id`, its key in the network registry). Partner Management still holds it as a partner with its policy for each use case. Map `subscriber_id` to the Partner Management partner, and let Partner Management take the partner's key from the network registry, so an organisation is onboarded once.
* **Asynchronous answers.** The result goes back through the partner's callback, so the Composite answers asynchronously. Natural in Beckn; new for the Composite.
* **Farmer data in Beckn messages.** Discovery goes through the network gateway; `select` to `status` go directly between partner and provider, so farmer data never passes through the gateway, only within an order. How the result travels (inline, or a short-lived signed link) and whether it is encrypted to the partner are still to be decided.
* **Catalogue visibility.** Use cases become discoverable on the network. They hold no data, but the catalogue should offer only what a partner can actually be granted.

## How it relates to the architecture

* Path B in the [architecture](../architecture/README.md#components-and-who-talks-to-whom) is unchanged behind the adapter: one consent, a consent token per registry, each department deciding with its own Consent Manager and ceiling.
* Today Beckn appears only at the OAN layer, for discovering service providers and consumers; this proposal adds the Composite as a provider on that network.

## Open questions

1. **Which OAN scenario comes first?** Each leads to a different integration point:
   * **Lenders and other providers pulling farmer data** (e.g. to underwrite a loan): the provider is an Agri Stack partner. It may call the Composite through its own API from behind its Beckn node, or Agri Stack is a node it orders from (this proposal).
   * **An OAN app showing the farmer their own data:** a farmer-facing (self-service) path, not the partner API.
   * **Agri Stack itself offering services on the network:** the Composite as a provider (this proposal).
2. **Which OAN domain and specification version** partners will use, and which schema describes a use case as a catalogue item. This should come from OAN, not be invented by Agri Stack.
3. **How OAN collects consent:** through Beckn XInput forms, a consent artefact or reference carried in the order, or both.
4. **How the result is delivered and protected:** inline in `on_confirm`/`on_status`, or a short-lived signed link; whether it is encrypted to the partner's key.
5. **Onboarding:** whether a network participant's registry entry is enough for Partner Management, or a separate Partner Management approval is still required for each use case (today it is).
