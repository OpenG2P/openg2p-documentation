---
description: The partners' entry point.
---

# Composite

The **Composite** is the service partners call to get data about a farmer from several registries in one request. It puts together ("composes") the answer: a partner (e.g. a bank) asks for a [use case](../architecture/use-cases.md), such as `loan-profile`, for one farmer; the Composite searches each department's registry the use case reads, with the farmer's consent, and returns the results combined into one response, signed with its own key. It runs only the use cases published in it and keeps no farmer data.

It is part of the Exchange, the install that partners onboard with: [the Composite in the architecture](../architecture/exchange.md#the-composite). How one request travels: [request flow](../architecture/request-flow.md).

## Key features

* **One generic service; each use case is a configuration file,** not code. Adding a use case, or a registry to one, needs no code change.
* **Never grants access.** What a partner receives is decided by the partner's use-case policy at the Exchange, each department's scope policy for the Composite, and the farmer's consent; each registry enforces it itself ([data-sharing policies](../architecture/data-sharing-policies.md)).
* **One partner to every department.** Departments onboard only the Composite, never the banks ([Composite as a partner](../architecture/exchange.md#composite-as-a-partner)).
* **Consent once, a token per registry.** The Exchange Consent Manager finds the partner's consent and gives each registry its own short-lived consent token.
* **Signed both ways.** Partner requests are verified against Partner Management; every response, errors included, is signed with the Composite's key, published at `/.well-known/jwks.json`.
* **Partial answers, reported.** Each source has a status (`ok`, `no_record`, `denied`, `unavailable`, `error`); an optional source can fail without failing the request.
* **Stores no farmer data.** Logs, audit events and the console's call log carry IDs, statuses and timings only.
* **Rate limited** per partner and use case, and optionally at the gateway ([rate limiting](rate-limiting.md)).
* **A staff console**, read-only: the use cases, the registries and their data scopes, the partners allowed each use case, and a log of calls ([console](console.md)).
* **A partner API** to list and describe the use cases and to query one ([Composite API](api.md)).

Installing it: [Deployment: Exchange](../deployment/exchange.md#composite). Source: [`composite/`](https://github.com/openg2p/agri-stack/tree/develop/composite) in the agri-stack repository.

{% hint style="warning" %}
**Not built yet:** checks when a use case is published, data-blind responses, daily quotas, registry endpoints held in Partner Management, a JSON Schema per use case, editing use cases in the console ([open items](../open-items/README.md#composite)).
{% endhint %}
