---
description: >-
  The Agri Stack policy model: partners' use-case grants in the Exchange's
  Partner Management, the Composite's scope policy per registry in each
  department's Partner Management as the ceiling, how they combine with the
  farmer's consent, who approves what, and how each hop fails closed.
---

# Data-Sharing Policies

Access policies say what a partner may ask for. In Agri Stack they are all held and approved in **Partner Management (PM)**, next to the partners' keys; the Consent Manager (CM) holds only consents, and reads policies from PM when it validates one. What a policy contains (its fields, versions and statuses, and how it is changed) is defined once, in Partner Management: [access policies](../../platform/platform-services/partner-management/functional-specifications.md#access-policies). This page explains how Agri Stack uses them.

## Two policies, two places

| Policy | Held in | For | Grants | Approved by |
| --- | --- | --- | --- | --- |
| **Use-case policy** (the partner's use-case grant) | The **Exchange's** PM, one per partner | Each partner of the Exchange (e.g. `PARTNER_BANK_A`) | The published use cases it may call, as `name@major` (e.g. `loan-profile@1`), with the purposes, subject ID types, signing algorithms and longest consent validity allowed | The Exchange's partner manager |
| **Scope policy** for the Composite (the department's ceiling) | **Each department's** PM, one per registry (data controller) | The Composite (`PARTNER_AGRI_COMPOSITE`) | The registry's data scopes the Composite may receive, at most, with the purposes and subject ID types allowed | The department's partner manager |

A partner of the Exchange has no policy in any department, and the Composite has no use-case policy: each department deals only with the Composite, and the Exchange only with its partners.

Consents collected in the Exchange's partner portal (a `consent_id`) are made **by use case**: the partner's staff pick one of the use cases its use-case policy grants, and the consent takes that use case's purpose and scopes per registry, read from the Composite; the policy's purposes, subject ID types and longest validity apply. Such a consent can then be used only for that use case. A partner of the Exchange therefore needs only its use-case policy, whether its staff collect the consent in the portal or it signs the consent itself (`consent_jws`).

**The use case** itself ([Composite](../composite/README.md)) is configuration owned by the Agri Stack platform team: its sources, the scopes each source needs (`scopes`) and may use (`optional_scopes`), its purpose and its response. A use-case grant gives the partner exactly that use case's scopes; it carries no scopes of its own. **The consent** is the farmer's, kept in the Exchange's CM: one consent per partner and purpose, with a grant per registry ([consent](consent.md)).

## What actually gets released

Through the Composite (path B in the [architecture](README.md#components-and-who-talks-to-whom)):

**effective scopes = the scopes of a use case the partner is granted ∩ what the farmer consented to ∩ what the department allows the Composite (its ceiling)**

* **The Composite** refuses a partner whose use-case policy does not grant the use case (`name@major`).
* **The Exchange's CM** validates the consent against the partner's use-case policy (use case, purpose, subject ID type, signing algorithm, validity) and puts, for each registry, the consent's grant ∩ the use case's scopes into that registry's signed **consent token**.
* **Each registry's own CM** checks the consent token and intersects it with the Composite's scope policy for that registry, read from the department's PM. A department therefore always decides what leaves its registry.
* **The registry** releases only what is left, and only its own slice.

A misconfigured use case or use-case grant can never leak more than the department allows.

<figure><img src="../../.gitbook/assets/open-agri-stack-released-scopes.svg" alt="Worked example: the use case asks for five scopes; the bank is granted the use case, so all five pass; the farmer declines land; the Livestock Department does not allow herd data; released: Farmer Registry personal details, Crop Sown crop season and measures"><figcaption><p>Worked example of released scopes</p></figcaption></figure>

{% hint style="info" %}
**A partner using one registry directly** (path A, no Composite): effective scopes = the partner's scope policy for that registry, in the registry's own PM ∩ the farmer's consent.
{% endhint %}

{% hint style="info" %}
In the registries, a scope is a registry **data scope**: a named group of the registry's own fields, with ID `<controller>.<name>` (e.g. `farmer-registry.personal_details`, `crop-sown-registry.crop_season`). Each registry publishes its versioned catalogue at `POST /partner/data_scopes` (signed) and filters records to the consented fields before rendering them. See [Data Scopes](../../products/registry/registry/design/data-scopes.md), and the [Farmer Registry](../../products/registry/farmer-registry/README.md#data-scopes) and [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md#data-scopes) scopes.
{% endhint %}

## Who approves what

| Change | Raised by | Approved in |
| --- | --- | --- |
| A partner joins the Exchange: its keys and its use-case policy | The partner asks; the Exchange's partner manager raises an onboarding request carrying both | The Exchange's PM |
| A partner gets another use case, or loses one | A policy request for the partner's use-case policy | The Exchange's PM |
| A new use case is published | The Agri Stack platform team ([creating a use case](../composite/creating-a-use-case.md)) | Not a policy change; partners still need it granted |
| The Composite may read more from a registry (a new scope or purpose) | The operator reruns the [Exchange setup](../deployment/after-install.md#exchange-setup), which raises a policy request for the Composite's scope policy | The department's PM |
| A farmer consents, or revokes | The farmer | The Exchange's CM |

Policy changes are versioned and audited in PM, and take effect when approved; modules see them within their policy cache time (about a minute by default).

## Fail closed

Every hop refuses when it cannot prove a grant:

| Hop | No grant | PM cannot be read |
| --- | --- | --- |
| Composite | `403 partner_not_allowed`: no use-case policy, or it does not grant the use case | The last answer is used for a while (up to six hours by default), then `503 partner_policy_unavailable` |
| Exchange CM | The consent is denied (`use_case_not_granted`), so the call fails with `consent_denied` | As the Composite, then denied with `policy_unavailable` (`consent_denied`) |
| Department CM | No scope policy for the Composite: the source is `denied` | As the Composite, then the source is `denied` |

Partners are matched to PM by convention: `bank-a` → `PARTNER_BANK_A` ([partner ID convention](../../platform/platform-services/partner-management/functional-specifications.md#partner-id-convention)). How the CM evaluates a policy at validate time: [verification & enforcement](../../consent-management/design/verification-and-enforcement.md). How modules read policies from PM and cache them: [PM integration](../../platform/platform-services/partner-management/integration.md).

{% hint style="warning" %}
**Not built yet:** checking a use case against the policies when it is published (for example, that its scopes are within each department's ceiling). See [open items](../open-items/README.md).
{% endhint %}
