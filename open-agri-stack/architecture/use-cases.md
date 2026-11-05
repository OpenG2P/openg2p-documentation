---
description: How data is shared through use cases.
---

# Use Cases

Through the Exchange, farmer data is shared **only through use cases**. A partner never asks for arbitrary data: it asks for a use case it has been assigned, for one farmer, and the farmer consents to the data that use case reads.

<figure><img src="../../.gitbook/assets/open-agri-stack-use-cases.svg" alt="Use cases. In Partner Management, each partner is assigned the use cases it may use at onboarding: in the example, Bank A has loan-profile@1 and crop-insurance@1; Insurer B has crop-insurance@1. Each use case, defined in the Composite, has a purpose and names the data it reads from each registry: loan-profile@1, for credit assessment, reads personal details and land from the Farmer Registry and crop seasons from the Crop Sown Registry; crop-insurance@1, for insurance, reads land location from the Farmer Registry and crop seasons and measures from the Crop Sown Registry. Data is shared only through a use case assigned to the partner, with the farmer's consent for it."><figcaption><p>Partners are assigned use cases; a use case names the data it reads from each registry</p></figcaption></figure>

## What a use case is

A **use case** is a named, versioned definition of one kind of data request, published in the [Composite](../composite/README.md) by the Agri Stack operator. For example `loan-profile@1`, a farmer's loan profile. It says:

* **Why:** its purpose (e.g. credit assessment), which the farmer's consent must match.
* **About whom:** the farmer's ID it takes (the Farmer ID, or the national ID) and any parameters (e.g. a crop season).
* **What:** the registries it reads, its **data sources**, and from each the [data scopes](../../products/registry/registry/design/data-scopes.md) it needs (and may optionally use). A data source is one search of one registry; `loan-profile` has three: the Farmer Registry, then two searches of the Crop Sown Registry. Adding a registry: [Adding a Data Source](../composite/adding-a-data-source.md).
* **The answer:** how the data from the registries is put together into one response.

A use case is configuration, not code: adding one is writing a file ([Use-Case Configuration](../composite/use-case-configuration.md)). It is versioned as `name@major`; a change that reads more data is a new major version, which partners must be assigned again and farmers must consent to again.

## Partners are assigned use cases at onboarding

A partner that consumes data is **onboarded and approved** in the Exchange's [Partner Management](../../platform/platform-services/partner-management/README.md). Onboarding is, in short:

* **its keys:** the public keys its requests are signed with;
* **the use cases it is assigned:** one policy per use case, with the purposes, farmer ID types and longest consent allowed.

Both are approved in Partner Management. A partner may be assigned several use cases; adding one later is a new policy, approved the same way, and removing one is revoking its policy ([Creating and Changing Policies](../../platform/platform-services/partner-management/creating-and-changing-policies.md)). A partner without a policy for a use case is refused.

## The farmer consents to the data

A farmer does not know what `loan-profile@1` means, so the consent is about the data itself: the purpose and, for each registry, the data being shared. The consent request records each item, not only the use case's name, and the partner portal shows the data scopes under **Data requested**. The form the farmer signs is the partner's own; CM staff check that it matches the request before approving. Showing the farmer each item in plain language, field by field, generated from the request, is not built yet ([open items](../open-items/README.md#identity-consent-and-policies)). A consent collected in the partner portal can be used only for the use case it was requested for ([Consent](consent.md)).

## Departments see data, not use cases

A department's systems never deal with use cases. Its Partner Management and Consent Manager see only the Composite as a partner and, for each request, a consent token with the purpose, the farmer and the registry's data scopes. In the Composite's scope policy, each department decides the most its registry releases; its administrator reads the published use cases to decide it ([Releasing Data to the Composite](../administration/releasing-data-to-the-composite.md)). A new use case, or one that reads more, gets that data only once the departments widen their policies.

**What is released for a request:** the use case's data ∩ what the farmer consented to ∩ what each department allows, worked through in [what actually gets released](data-sharing-policies.md#what-actually-gets-released).
