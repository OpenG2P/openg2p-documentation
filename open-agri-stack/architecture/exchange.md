---
description: >-
  The Agri Stack Exchange: where partners onboard once and use one farmer
  consent across registries. Its parts, what it holds and does not hold,
  partners and their use-case grants, and how departments trust it.
---

# The Exchange

The **Exchange** is where partners (banks, MFIs, agritechs) onboard once and use one farmer consent for data held in several departments' registries. Without it, a partner would onboard and collect consent at every registry it reads (path A in the [architecture](README.md#components-and-who-talks-to-whom)). The departments keep control: each still decides at its own boundary what leaves its registry.

The Exchange is one more install, hosted by one department, next to the registries' installs. It holds no registry.

## Its parts

| Part | Product | Role in the Exchange |
| --- | --- | --- |
| Partner portal | Part of the [Consent Manager](../../consent-management/README.md) | Partner staff (e.g. bank staff) raise consent requests and record a consent the farmer gives in person |
| Consent Manager (CM), exchange role | [Consent Manager](../../consent-management/README.md) | Collects and keeps the farmers' consents; validates them against the partners' policies in PM and issues a consent token per registry to the Composite |
| Partner Management (PM) | [Partner Management](../../platform/platform-services/partner-management/README.md) | The identities, public keys and access policies of the partners; the Composite's identity and key |
| eSignet | Commons services | The farmer's national-ID login in the partner portal, before a consent request is submitted. A mock identity system stands in for the national ID system in testing |
| Composite | [Composite](../composite/README.md) | The partners' entry point |
| Audit Manager | [Audit Manager](../../platform/platform-services/audit-manager/README.md) | Who asked what: the Composite's audit events |

The **Composite** serves approved use cases (e.g. `loan-profile@1`): a partner sends one signed request about one farmer, with the farmer's consent, and the Composite queries several registries and returns one signed response. It stores nothing after it responds. Each use case is a configuration file, not new code: see [Composite](../composite/README.md).

In the partner portal, every consent request carries the farmer's Farmer ID besides the national ID; CM staff check it in the Farmer Registry before approving the consent ([Farmer ID and national ID](registries.md#farmer-id-and-national-id)). How a consent is collected: [consent](consent.md).

## What it holds, and what it does not

| Holds | Does not hold |
| --- | --- |
| The farmers' consents, and the form the farmer signed (evidence) | Any registry, or any farmer data: the Composite keeps nothing after it responds |
| Each partner's identity, key and use-case policies (in PM) | Any department's ceiling: each department decides in its own PM what it releases to the Composite |
| The Composite's key and its published use cases | Any partner's key in the departments: they trust the Composite and the Exchange's consent tokens, not each partner |

## Partners and their use-case grants

A partner onboards in the Exchange's PM as `PARTNER_<ID>` (e.g. `PARTNER_BANK_A`), with its public key and **one use-case policy per use case it may call** (e.g. `loan-profile@1`), each with the purposes, subject ID types and consent validity allowed. All are approved in the Exchange's PM; adding a use case later is **Add policy** on the partner. A partner of the Exchange is never onboarded in a department. A granted use case brings its own scopes, so a partner needs no policy per registry. This holds for consents its staff collect in the partner portal too: there a consent is made for one of the partner's granted use cases ([data-sharing policies](data-sharing-policies.md#two-policies-two-places)).

How the use-case grant, the consent and each department's ceiling combine, and who approves what: [data-sharing policies](data-sharing-policies.md). Getting onboarded, as a partner: [partner guide](../partner-guide.md#step-2-get-onboarded-in-partner-management).

## How departments trust it

**To each department, the Exchange is one partner.** The department's PM holds only the Composite's public key and its scope policy per registry (the ceiling), and its CM trusts the Exchange CM's consent tokens.

* **Consent tokens.** For each request, the Composite asks the Exchange CM for one signed consent token per registry; when the partner sent no consent, the Exchange CM uses the partner's active consent for that farmer and use case. The Exchange CM issues tokens only if the partner has a policy for the use case, and a token carries only the scopes in the consent's grant for that registry ∩ the scopes the use case asks for. It is short-lived (5 minutes by default) and used for one query.
* **Each registry still decides.** It verifies the Composite's signature at its own PM, validates its consent token at its own CM, checks that the consent's subject is the person searched, and releases only what the [Composite's scope policy](registries.md#scope-policy-for-the-composite) for that registry, in the department's PM, also allows. Its CM checks the token offline (signature against the Exchange CM's cached keys, issuer, presenter, audience, subject, expiry): no call back to the Exchange per query. A revoked consent gets no new token; one already issued lapses with its short lifetime. A status call to the Exchange CM can be switched on where that delay is not acceptable.

One request, hop by hop: [request flow](request-flow.md). The token format, the optional status check and the department side: [Exchange consent tokens](../../consent-management/design/exchange-receipts.md).

A registry installed without the Exchange is not affected: it checks partners and consents at its own PM and CM (path A).

## Not built yet

* Consent given in person digitally (no form, no staff step) and self-service consent by the farmer ([consent](consent.md#how-a-farmer-gives-consent)).
* A consent collected in the Exchange CM presented directly at a registry, without the Composite.

See [TODOs and open items](../open-items/README.md).

{% hint style="info" %}
Installing the Exchange: [Deployment: Exchange](../deployment/exchange.md) and [Deployment: Composite](../deployment/composite.md).
{% endhint %}
