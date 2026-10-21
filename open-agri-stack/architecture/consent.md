---
description: >-
  Consent in Agri Stack: one consent per partner and farmer with a grant per
  registry, collected and kept by the Exchange's Consent Manager, and a consent
  token per registry at query time. How a farmer gives it, and what is specific
  to Agri Stack.
---

# Consent

A partner (e.g. a bank) needs the farmer's consent before Agri Stack shares the farmer's data with it. In Agri Stack:

* **One consent covers every registry the partner needs.** The bank asks once, for the data its use case needs; inside, the consent holds a **grant per registry** (Farmer Registry, Crop Sown Registry, …). The bank never deals with which registry holds what.
* **The Exchange's Consent Manager (CM) collects and keeps it,** not the bank. The farmer confirms it there and proves who they are with the national ID.
* **Each registry decides for itself.** At query time the Exchange CM gives the Composite a short-lived **consent token** per registry, with only that registry's allowed scopes, and each registry checks its token at its **own** CM against the department's ceiling for the Composite ([request flow](request-flow.md)). Why a token rather than passing the consent on: [why a consent token](../../consent-management/design/exchange-receipts.md#why-a-consent-token).

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

* **The farmer is identified by the national ID and the Farmer ID.** The consent's subject is the national ID (`FAYDA_FAN` in the reference setup), which the farmer logs in with. Every request must also carry the **Farmer ID** (`requiredSubjectIdentifiers: [FARMER_ID]`, the Exchange role's default). CM staff check it in the **Farmer Registry**, the source of truth for the link between the two, before approving. Demographics shown to them are those of the national-ID login, labelled as such, and never compared automatically ([identifiers and demographics](../../consent-management/design/consent-collection.md#identifiers-and-demographics)).
* **The data asked for comes from a use case.** In the Exchange's partner portal a request is made for one of the use cases the partner is granted (e.g. `loan-profile@1`): the use case's purpose and its scopes per registry (required and optional), read from the Composite, are the consent's purpose and grants. The consent can then be used only for that use case ([data-sharing policies](data-sharing-policies.md#two-policies-two-places)).
* **The registries are the data controllers.** Each grant names a registry (`farmer-registry`, `crop-sown-registry`) and that registry's data scopes (`<registry>.<scope>`, e.g. `farmer-registry.personal_details`).
* **One consent, every registry.** The bank queries the Composite with **no consent** (the Exchange CM looks up the bank's active consent for this farmer and use case; recommended for consents collected in the partner portal), with the consent's ID (`message.consent_id`), or, if its use-case policy allows partner-signed consents, with a consent it signed itself (`message.consent_jws`, a `grants` claim with one grant per registry). Either way the Exchange CM turns it into a consent token per registry, limited to **the use case's scopes ∩ consent**, provided the bank's use-case policy in Partner Management grants that use case ([data-sharing policies](data-sharing-policies.md)).
* **Usage per registry.** One-shot and periodic limits are counted per consent and registry.
* **The bank keeps a provable copy.** The consent record it downloads (receipt, signed form, the CM's signed statement) is the same in every scenario ([the partner's copy](../../consent-management/design/consent-collection.md#the-partners-copy-of-a-consent)).
* **Revocation** is of the whole consent; the Exchange CM issues no further consent token for it. Registries check tokens offline, so a token already issued stays usable until it expires (5 minutes by default).

{% hint style="warning" %}
**Not built yet:** scenarios 2 and 3; declining individual items or revoking one registry's grant only; presenting a consent held in the CM directly at a registry, without the Composite (path A, [open items](../open-items/README.md)).
{% endhint %}

## Details

| Topic | Page |
| --- | --- |
| The scenarios step by step, the partner portal, the gaps | [Consent collection](../../consent-management/design/consent-collection.md) |
| The national-ID login (eSignet) | [National ID authentication](../../consent-management/design/consent-collection.md#national-id-authentication-in-the-partner-portal) |
| Grants, `/validate`, replay per consent and registry | [Verification & enforcement](../../consent-management/design/verification-and-enforcement.md) |
| Consent tokens between the Exchange and the departments | [Exchange consent tokens](../../consent-management/design/exchange-receipts.md) |
| A partner signing its own consent (`grants` claim) | [Partner Integration Guide](../../consent-management/partner-integration-guide.md) and the [partner guide](../partner-guide.md) |
| Turning on the partner portal, the login and the required Farmer ID | [Deployment: Exchange](../../consent-management/deployment/README.md#partner-portal-and-consent-evidence-optional) |
| Trying it end to end | [Testing](../deployment/testing.md#consent-through-the-partner-portal) |
