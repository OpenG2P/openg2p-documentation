---
description: >-
  What a registry actually releases through the Composite: the use case, the
  partner's policy, the farmer's consent and the department's own policy, who
  holds and owns each, and how they are checked at query time.
---

# Data-Sharing Policies

## What actually gets released

Through the Composite (path B in the [architecture](README.md#components-and-who-talks-to-whom)):

**effective scopes = what the use case asks for ∩ what the partner's policy allows ∩ what the farmer consented to ∩ what the department allows the Composite**

* The **Exchange's Consent Manager** computes the first three when the Composite asks it to validate the consent, and puts the result for each registry into that registry's signed **consent token**.
* **Each registry's own Consent Manager** checks the consent token and intersects it with the department's **standing policy for the Composite**, so a department always decides what leaves its registry.
* **The registry** releases only what is left, and only its own slice.

A misconfigured use case or partner policy can never leak more than the department allows.

<figure><img src="../../.gitbook/assets/open-agri-stack-released-scopes.svg" alt="Worked example: the use case asks for five scopes; the bank's policy leaves out crop measures; the farmer declines land; the Livestock Department does not allow herd data; released: Farmer Registry personal details and Crop Sown crop season"><figcaption><p>Worked example of released scopes</p></figcaption></figure>

{% hint style="info" %}
**A partner using one registry directly** (path A, no Composite): effective scopes = the partner's policy at that registry's Consent Manager ∩ the farmer's consent.
{% endhint %}

## Layers and owners

| | Held in | Owner | Defines | Changes |
| --- | --- | --- | --- | --- |
| **Use case** ([Composite](../composite/README.md)) | the Composite's configuration | Agri Stack platform team | Sources, the scopes each source needs (`scopes`) and may use (`optional_scopes`), response, timeouts | Versioned like an API |
| **Partner's data-share policy** | the Exchange's Consent Manager, one per partner and registry | The Exchange, on behalf of the departments | Allowed scopes per registry, purposes, subject ID types, validity ceiling, fetch type | Rarely; a widening can need approval (AWE, optional, off by default) |
| **Department's policy for the Composite** | each registry's own Consent Manager (a binding for `agri-composite`) | The department (data controller) | What its registry may release through the Composite, at most | When the department decides; [Exchange setup](../deployment/after-install.md#exchange-setup) creates it from the published use cases |
| **Consent** | the Exchange's Consent Manager | The farmer | One consent with a grant per registry, for one partner and purpose | Per farmer; revocable |

Which partners may use a use case is set in the use case (`allowed_partners`).

{% hint style="info" %}
In the registries, a scope is a registry **data scope**: a named group of the registry's own fields, with ID `<controller>.<name>` (e.g. `farmer-registry.personal_details`, `crop-sown-registry.crop_season`). Each registry publishes its versioned catalogue at `POST /partner/data_scopes` (signed) and filters records to the consented fields before rendering them. See [Data Scopes](../../products/registry/registry/design/data-scopes.md), and the [Farmer Registry](../../products/registry/farmer-registry/README.md#data-scopes) and [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md#data-scopes) scopes.
{% endhint %}

## Runtime checks

Through the Composite, as built:

1. **Composite:** verifies the partner's signature (the Exchange's Partner Management) and that the partner is in the use case's `allowed_partners`.
2. **Composite → Exchange Consent Manager `/validate`:** the consent is valid, not revoked, for this partner, purpose and farmer; the partner's policy per registry; only the use case's scopes. It returns one signed consent token per registry with the effective scopes so far.
3. **Registry → its own Consent Manager `/validate`, with the consent token:** the token is signed by a trusted issuer (the Exchange's Consent Manager), presented by the Composite, still valid and not revoked; the department's standing policy for the Composite is applied.
4. **Registry:** releases only the effective scopes.

{% hint style="warning" %}
**Not built yet:** data-sharing policies held in Partner Management instead of the Consent Manager, as one policy per partner with a section per registry that each department approves; checking a use case against those policies when it is published. See [open items](../open-items/README.md).
{% endhint %}
