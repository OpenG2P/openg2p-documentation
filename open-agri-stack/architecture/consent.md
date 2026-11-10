---
description: Farmer consent in Agri Stack.
---

# Consent

A partner (e.g. a bank) needs the farmer's consent before Agri Stack shares the farmer's data with it. In Agri Stack:

* **One consent per use case, covering every registry it reads.** The bank asks once, for a use case (e.g. a farmer's loan profile); inside, the consent holds a **grant per registry** the use case reads (Farmer Registry, Crop Sown Registry, …). The consent can be used only for that use case, and the bank never deals with which registry holds what.
* **The Exchange's Consent Manager (CM) collects and keeps it,** not the bank. The farmer confirms it there and proves who they are with the national ID.
* **Each registry decides for itself.** At query time the Exchange CM gives the Composite a short-lived **consent token** per registry, with only that registry's allowed scopes, and each registry checks its token at its **own** CM against the [Composite's scope policy](data-sharing-policies.md#two-policies) ([request flow](request-flow.md)). Why a token, rather than passing the consent on or simply trusting the Composite up to its scope policy: [why a consent token](../../consent-management/design/exchange-consent-tokens.md#why-a-consent-token).

{% hint style="info" %}
**Consent object, artefact, receipt, token** are four different things; see [key terms](../../consent-management/design/README.md#key-terms). The reasons behind this model (one consent with a grant per registry, each registry validating its own grant, consent tokens across installs) are the Consent Manager's [design decisions](../../consent-management/design/README.md#design-decisions).
{% endhint %}

## How a farmer gives consent

<figure><img src="../../.gitbook/assets/consent-collection-scenarios.svg" alt="Three ways a farmer gives a bank consent, each with a national-ID login: 1, in person with a form (built): staff raise the request in the partner portal, the farmer logs in with the national ID and signs a form that staff upload, a Consent Approver checks it and the national-ID login, the bank queries and the Exchange finds the consent (no consent ID needed), and its admin downloads the consent record; 2, in person, digital (planned): after the login the farmer approves on the Consent Manager's screen, the consent is active at once and an SMS lets them revoke; 3, self-service (planned), where the farmer can also revoke"><figcaption><p>The three consent scenarios</p></figcaption></figure>

| Scenario | Status | How the farmer confirms |
| --- | --- | --- |
| **1 · In person, with a form** | **Built** | National-ID login (eSignet) on the bank's device, a signed form, and a check by a Consent Approver |
| **2 · In person, digital** | Planned | National-ID login, then the farmer approves the request on the CM's own screen; active at once, no form, no approval step; an SMS to the registered phone lets them revoke |
| **3 · Self-service** | Planned | National-ID login in their own portal or app, where they approve or decline, and can revoke any consent |

In every scenario the farmer proves who they are with the national ID; an SMS is only ever a notification afterwards. The steps, the partner portal and the gaps are in the Consent Manager's [consent collection](../../consent-management/design/consent-collection.md).

## Two ways a consent reaches the Exchange

| | Consent held by the Exchange CM (the main path) | Consent signed by the partner |
| --- | --- | --- |
| Collected by | The Exchange CM: partner staff in the partner portal (scenario 1), or the CM's own screens (scenarios 2 and 3, planned) | The partner, through its own channel (its app, branch or forms), outside the Exchange |
| What the partner sends to the Composite | Nothing (the Exchange CM finds the consent), or its consent ID | The consent object it signed (`consent_jws`) |
| Allowed | Always | Only if the partner's use-case policy allows partner-signed consents (**May present its own signed consents**; off by default) |
| What the CM can check | The farmer's national-ID login, the signed form, a Consent Approver's check | The partner's signature only, not that the farmer agreed: the partner keeps the evidence and answers for it |
| In the partner portal | Listed under **Consents** | Not listed; stored by the Exchange CM when first used, and usable afterwards by its ID or by lookup |

Both go to the Composite's same query API; the Exchange CM turns either into the registries' consent tokens. All three scenarios above are the first path. The second exists for partners the Exchange trusts with their own consent collection; the [install test](../deployment/testing.md) uses it by default because it needs no person. Partner's side: [Partner Guide, step 4](../partner-integration-guide.md#step-4-collect-the-farmers-consent).

## Key features

| Feature | In brief | Details |
| --- | --- | --- |
| **Given in person, approved by a Consent Approver** | Partner staff raise the request in the Exchange's partner portal, for a use case. The farmer logs in with the national ID and signs the consent form, which lists all the data to be shared from each registry, its purpose and its period: the farmer consents to that data. A Consent Approver checks the form in the CM console and approves it | [Collecting a Consent](../administration/collecting-a-consent.md) |
| **Tied to one farmer** | The farmer authenticates with the national ID, which the consent records; the Farmer ID can be added to the request. The bank names the farmer by the Farmer ID (or the national ID), and each registry returns only that farmer's records: a wrong ID finds no data, never another farmer's | [identifiers and demographics](../../consent-management/design/consent-collection.md#identifiers-and-demographics) |
| **Time-bound** | Valid until the end date set on the request, never longer than the partner's use-case policy allows; then it expires | [expiry](../../consent-management/design/consent-lifecycle.md#expiry) |
| **Used without being sent** | The bank queries naming only the farmer. The Exchange CM finds the consent and gives each registry a short-lived consent token, carrying only that registry's data | [request flow](request-flow.md) |
| **Provable** | The bank downloads the consent record: the receipt, the signed form and a statement signed by the CM, which it can check without the CM | [the partner's copy of a consent](../../consent-management/design/consent-collection.md#the-partners-copy-of-a-consent) |
| **Revocable** | A Consent Approver revokes it at the farmer's request. Sharing stops within minutes, when the consent tokens already issued expire | [revocation](../../consent-management/design/consent-lifecycle.md#revocation) |
| **Audited** | Every decision and change is logged, append-only | [Consent Management](../../consent-management/README.md#design-principles) |

What is planned for consent (giving it without a form, a generated consent form, partial consent and revocation, using an Exchange consent directly at a registry): [Roadmap](../roadmap/README.md).
