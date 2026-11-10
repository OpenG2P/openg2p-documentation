---
description: The Exchange and its role.
---

# Exchange

The **Exchange** gives a partner (a bank, an insurer, an agritech) one consolidated, signed answer about a farmer, drawn from several departments' registries, **with the farmer's consent**. It is its own install, above the departments: its components are in the [architecture](README.md#the-exchange). One request through it is path B there ([data-sharing paths](README.md#data-sharing-paths)), shown hop by hop in the [request flow](request-flow.md). Without it, a partner would onboard and collect consent at every registry separately (path A).

* **Through a use case.** The partner asks for a use case it is assigned, for one farmer ([Use Cases](use-cases.md)).
* **Onboarded once.** The partner is onboarded only in the Exchange's Partner Management, with its keys and its use cases.
* **With consent.** The farmer consents to the data the use case reads, proving who they are with the national ID ([Consent](consent.md)).
* **Departments keep control.** Each registry decides what it releases ([below](#composite-as-a-partner)).

## The Composite

The **Composite** is the Exchange's service that partners call. It puts together ("composes") one answer about a farmer from several registries: for a use case, it searches each registry the use case reads, with the farmer's consent, and combines the results into one signed response. It is not a general query engine across registries: it runs only the use cases published in it, and it keeps no farmer data. The Exchange's other components (Consent Manager, Partner Management, eSignet) are OpenG2P products used as they are; the Composite is the one built for Agri Stack ([Composite](../composite/README.md)).

## What it stores

Consents, partners' keys and policies, and audit records; never registry data: the Composite passes each answer on and keeps nothing.

| Component | Stores | Never stores |
| --- | --- | --- |
| Consent Manager and partner portal | The farmers' consents, and the form each farmer signed (evidence) | Any farmer data from the registries |
| Partner Management | Each partner's identity, keys and use-case policies | What each department releases: that is in the department's own Partner Management |
| Composite | The published use cases and its signing key | Any answer, once sent |
| Audit Manager | Who asked for what, and when | The data that was returned |

## Composite as a partner

**To each department, the Composite is one partner.** The department's PM holds only the Composite's entry and its scope policy per registry (the ceiling), and its CM trusts the Exchange CM's [consent tokens](../../consent-management/design/exchange-consent-tokens.md).

* **The Composite's key.** The Composite publishes its public key at its JWKS URL (`/.well-known/jwks.json` on its public hostname). Each department's Partner Management onboards the Composite with that URL and reads the key from it when a registry checks a signature, caching it for a few minutes. No key is copied anywhere: a new key reaches every department by itself, and a department can be set up before or after the Exchange. The department's own decision is only what it releases: the scope policy. The Exchange's Partner Management does not hold the Composite: nothing at the Exchange checks its signature. Partners verify the Composite's answers with its JWKS URL, and the Exchange CM issues consent tokens to the Composite by its configuration (**Token Presenters** in Commons Services).
* **Consent tokens.** For each request, the Composite asks the Exchange CM for one signed consent token per registry; when the partner sent no consent, the Exchange CM uses the partner's active consent for that farmer and use case. The Exchange CM issues tokens only if the partner has a policy for the use case, and a token carries only the scopes in the consent's grant for that registry ∩ the scopes the use case asks for. It is short-lived (5 minutes by default) and used for one query. Its format: [consent token](../../consent-management/design/exchange-consent-tokens.md#consent-token).
* **Each registry still decides.** It verifies the Composite's signature at its own PM, validates its consent token at its own CM, checks that the consent's subject is the person searched, and releases only what the [Composite's scope policy](data-sharing-policies.md#two-policies) for that registry, in the department's PM, also allows. Its CM checks the token offline (signature against the Exchange CM's cached keys, issuer, presenter, audience, subject, expiry): no call back to the Exchange per query. A revoked consent gets no new token; one already issued lapses with its short lifetime. A status call to the Exchange CM can be switched on where that delay is not acceptable ([status check](../../consent-management/design/exchange-consent-tokens.md#department-role-accepting)).

How it is installed: [Deployment](../deployment/README.md).
