---
description: >-
  The Agri Stack Exchange: it queries several departments' registries and gives
  a partner one consolidated answer about a farmer, through the use cases the
  partner is assigned and only with the farmer's consent.
---

# The Exchange

The **Exchange** gives a service provider (a **partner**: a bank, an insurer, an agritech) one consolidated answer about a farmer, drawn from several departments' registries, **with the farmer's consent**. The partner sends one request; the Exchange checks that the partner may ask, finds the farmer's consent, queries each registry that holds the data, and returns one signed answer.

<figure><img src="../../.gitbook/assets/open-agri-stack-exchange.svg" alt="The Exchange. A partner, onboarded and approved with the use cases assigned to it, sends one request: a use case, for a farmer. In the Exchange, the Composite runs the use case; the Consent Manager, with its partner portal, holds the farmer's consent and issues a consent token per registry; Partner Management holds the partner's keys and use-case policies; eSignet is the farmer's national-ID login; the Audit Manager records every call. The Composite searches each department's registry with its consent token and returns one consolidated, signed answer to the partner."><figcaption><p>The Exchange</p></figcaption></figure>

* **Everything goes through a use case.** A partner never asks for arbitrary data: it asks for a **use case** it has been assigned (for example a farmer's loan profile), which says exactly what is read from each registry. See [Use Cases](use-cases.md).
* **Partners are onboarded and approved.** Before it can ask anything, a partner is onboarded in the Exchange's Partner Management: its keys, and the use cases it is assigned. Both are approved there.
* **The farmer consents.** The farmer gives consent for the use case, proving who they are with the national ID ([Consent](consent.md)).
* **Departments keep control.** Each registry still decides, at its own boundary, what it releases ([below](#how-departments-trust-it)).

The Exchange is its own install, above the departments' registries. It holds no registry and keeps no farmer data. Without it, a partner would onboard and collect consent at every registry separately (path A in the [architecture](README.md#components-and-who-talks-to-whom)).

## Its parts

| Part | Product | Role in the Exchange |
| --- | --- | --- |
| Partner portal | Part of the [Consent Manager](../../consent-management/README.md) | Partner staff (e.g. bank staff) raise consent requests and record a consent the farmer gives in person |
| Consent Manager (CM), exchange role | [Consent Manager](../../consent-management/README.md) | Collects and keeps the farmers' consents; validates them against the partners' policies in PM and issues a consent token per registry to the Composite |
| Partner Management (PM) | [Partner Management](../../platform/platform-services/partner-management/README.md) | The identities, public keys and access policies of the partners; the Composite's identity and key |
| eSignet | Commons services | The farmer's national-ID login in the partner portal, before a consent request is submitted. A mock identity system stands in for the national ID system in testing |
| Composite | [Composite](../composite/README.md) | The partners' entry point |
| Audit Manager | [Audit Manager](../../platform/platform-services/audit-manager/README.md) | Who asked what: the Composite's audit events |

## What the Exchange keeps, and what it does not

For the Exchange as a whole, component by component:

| Component | Keeps | Does not keep |
| --- | --- | --- |
| Consent Manager and partner portal | The farmers' consents, and the form the farmer signed (evidence) | Any farmer data from the registries |
| Partner Management | Each partner's identity, keys and use-case policies | The departments' ceilings: each department sets in its own Partner Management what it releases to the Exchange |
| Composite | The published use cases and its own key | Any answer: it keeps nothing after it responds |
| Audit Manager | Who asked for what, and when | The data that was returned |

## How departments trust it

**To each department, the Exchange is one partner.** The department's PM holds only the Composite's public key and its scope policy per registry (the ceiling), and its CM trusts the Exchange CM's consent tokens.

* **Consent tokens.** For each request, the Composite asks the Exchange CM for one signed consent token per registry; when the partner sent no consent, the Exchange CM uses the partner's active consent for that farmer and use case. The Exchange CM issues tokens only if the partner has a policy for the use case, and a token carries only the scopes in the consent's grant for that registry ∩ the scopes the use case asks for. It is short-lived (5 minutes by default) and used for one query.
* **Each registry still decides.** It verifies the Composite's signature at its own PM, validates its consent token at its own CM, checks that the consent's subject is the person searched, and releases only what the [Composite's scope policy](registries.md#scope-policy-for-the-composite) for that registry, in the department's PM, also allows. Its CM checks the token offline (signature against the Exchange CM's cached keys, issuer, presenter, audience, subject, expiry): no call back to the Exchange per query. A revoked consent gets no new token; one already issued lapses with its short lifetime. A status call to the Exchange CM can be switched on where that delay is not acceptable.

One request, hop by hop: [request flow](request-flow.md). The token format, the optional status check and the department side: [Exchange consent tokens](../../consent-management/design/exchange-consent-tokens.md).

A registry installed without the Exchange is not affected: it checks partners and consents at its own PM and CM (path A).

## Not built yet

* Consent given in person digitally (no form, no staff step) and self-service consent by the farmer ([consent](consent.md#how-a-farmer-gives-consent)).
* A consent collected in the Exchange CM presented directly at a registry, without the Composite.

See [TODOs and open items](../open-items/README.md).

{% hint style="info" %}
Installing the Exchange: [Deployment: Exchange](../deployment/exchange.md) and [Deployment: Composite](../deployment/composite.md).
{% endhint %}
