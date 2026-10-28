---
description: >-
  Consent in Agri Stack: one consent per partner, farmer and use case, with a
  grant per registry, collected and kept by the Exchange's Consent Manager, and
  a consent token per registry at query time. How a farmer gives it, and what is specific
  to Agri Stack.
---

# Consent

A partner (e.g. a bank) needs the farmer's consent before Agri Stack shares the farmer's data with it. In Agri Stack:

* **One consent per use case, covering every registry it reads.** The bank asks once, for a use case (e.g. a farmer's loan profile); inside, the consent holds a **grant per registry** the use case reads (Farmer Registry, Crop Sown Registry, …). The bank never deals with which registry holds what.
* **The Exchange's Consent Manager (CM) collects and keeps it,** not the bank. The farmer confirms it there and proves who they are with the national ID.
* **Each registry decides for itself.** At query time the Exchange CM gives the Composite a short-lived **consent token** per registry, with only that registry's allowed scopes, and each registry checks its token at its **own** CM against the department's ceiling for the Composite ([request flow](request-flow.md)). Why a token, rather than passing the consent on or simply trusting the Composite up to the ceiling: [why a consent token](../../consent-management/design/exchange-consent-tokens.md#why-a-consent-token).

{% hint style="info" %}
**Consent object, artefact, receipt, token** are four different things; see [key terms](../../consent-management/design/README.md#key-terms). The reasons behind this model (one consent with a grant per registry, each registry validating its own grant, consent tokens across installs) are the Consent Manager's [design decisions](../../consent-management/design/README.md#design-decisions).
{% endhint %}

## How a farmer gives consent

<figure><img src="../../.gitbook/assets/consent-collection-scenarios.svg" alt="Three ways a farmer gives a bank consent, each with a national-ID login: 1, in person with a form (built): staff raise the request in the partner portal, the farmer logs in with the national ID and signs a form that staff upload, Consent Manager staff check it and the Farmer ID in the Farmer Registry, the bank queries and the Exchange finds the consent (no consent ID needed), and its admin downloads the consent record; 2, in person, digital (planned): after the login the farmer approves on the Consent Manager's screen, the consent is active at once and an SMS lets them revoke; 3, self-service (planned), where the farmer can also revoke"><figcaption><p>The three consent scenarios</p></figcaption></figure>

| Scenario | Status | How the farmer confirms |
| --- | --- | --- |
| **1 · In person, with a form** | **Built** | National-ID login (eSignet) on the bank's device, a signed form, and a check by CM staff |
| **2 · In person, digital** | Planned | National-ID login, then the farmer approves the request on the CM's own screen; active at once, no form, no staff step; an SMS to the registered phone lets them revoke |
| **3 · Self-service** | Planned | National-ID login in their own portal or app, where they approve or decline, and can revoke any consent |

In every scenario the farmer proves who they are with the national ID; an SMS is only ever a notification afterwards. The steps, the partner portal and the gaps are in the Consent Manager's [consent collection](../../consent-management/design/consent-collection.md).

## What is specific to Agri Stack

* **The farmer is identified by the national ID and the Farmer ID.** The consent's subject is the national ID the farmer logs in with; each request also carries the **Farmer ID**, which CM staff check in the Farmer Registry (the source of truth for the link between the two) before approving ([identifiers and demographics](../../consent-management/design/consent-collection.md#identifiers-and-demographics)).
* **The use case sets what is asked for.** The use case's purpose and its scopes per registry, read from the Composite, become the consent's purpose and grants; the consent can be used only for that use case ([data-sharing policies](data-sharing-policies.md#two-policies-two-places)).
* **The registries are the data controllers.** Each grant names a registry (`farmer-registry`, `crop-sown-registry`) and its data scopes (e.g. `farmer-registry.personal_details`).
* **The partner need not send the consent.** The Exchange CM finds the partner's active consent for the farmer and use case ([partner guide](../partner-guide.md)).
* **Revocation and consent tokens.** A revoked consent gets no further consent token; a token already issued stays usable until it expires (5 minutes by default), since registries check tokens offline.

{% hint style="warning" %}
**Not built yet:** scenarios 2 and 3; declining individual items or revoking one registry's grant only; using a consent held by the Exchange CM directly at a registry, without the Composite ([open items](../open-items/README.md#identity-consent-and-policies)).
{% endhint %}
