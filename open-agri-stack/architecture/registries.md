---
description: The department registries.
---

# Registries in Agri Stack

Each registry in Agri Stack belongs to a department and is its own install there. Two are integrated today; what each holds, its registers and its data scopes are documented with the product. A registry joins Agri Stack by becoming a data source of a use case ([Adding a Data Source](../composite/adding-a-data-source.md)); the [Livestock Registry](../roadmap/livestock-registry.md) is designed as the next one.

| Registry | Department (example) | Holds |
| --- | --- | --- |
| [Farmer Registry](../../products/registry/farmer-registry/README.md) | Agriculture | Farmers, their land, households and declared main crops |
| [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md) | Crops | Crop seasons, plot by plot and season by season |

**One registry per fact.** Crop seasons are held only in the Crop Sown Registry, land in the Farmer Registry (until a land administration registry exists), and livestock moves to the Livestock Registry once it is built. Two registries holding the same fact would disagree, and count it twice.

## Each registry is sovereign

* **Its own install.** Each department runs its registry with its own Partner Management, Consent Manager and data. Registries share identifiers, never code or databases: neither looks anything up in the other.
* **It sees only the Composite.** No bank or other partner calls it through Agri Stack; the partner's ID comes with each request and is logged ([Composite as a partner](exchange.md#composite-as-a-partner)).
* **It decides what leaves it.** The department sets what its registry releases to the Composite, in its own Partner Management, and its Consent Manager applies it to every request ([Data-Sharing Policies](data-sharing-policies.md#what-actually-gets-released), [Releasing Data to the Composite](../administration/releasing-data-to-the-composite.md)).

## Farmer ID across registries

The **Farmer ID**, issued by the Farmer Registry, identifies the farmer across Agri Stack: every registry keys its records on it. The national ID is used only to authenticate the farmer, and registries keep it beside the Farmer ID so that a consent, given after that login, can be checked.

| Identifier | Farmer Registry | Crop Sown Registry |
| --- | --- | --- |
| Farmer ID (`FARMER_ID`, e.g. `FR-0007`) | Issued here: the farmer's functional ID | The subject of each activity |
| National ID (`FAYDA_FAN`) | The farmer's foundational ID | Recorded on each activity, beside the Farmer ID |

* A partner names the farmer by the Farmer ID, or by the national ID if that is all it has: the Composite then reads the Farmer ID from the Farmer Registry and searches the Crop Sown Registry with it ([request flow](request-flow.md)).
* **One consent covers both.** The consent records the national ID the farmer logged in with; the Crop Sown Registry accepts a search by Farmer ID because its own records link that Farmer ID to that national ID ([how the Crop Sown Registry relates to the Farmer Registry](../../products/registry/crop-sown-registry/README.md#how-it-relates-to-the-farmer-registry)).
* Each registry returns only the consent's farmer's records, so a wrong ID finds no data, never another farmer's ([consent](consent.md#key-features)).

What the `loan-profile` use case reads from each registry: [the `loan-profile` use case](../composite/use-case-configuration.md#the-loan-profile-use-case).
