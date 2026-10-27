---
description: >-
  Design for a Livestock Registry in Agri Stack: an Animal entity register and
  a livestock events activity register in one registry, its keys, its relation
  to the Farmer Registry and what it would share. Not built.
---

# Livestock Registry

{% hint style="info" %}
**Planned: design only, not built.** Until it exists, the Farmer Registry holds each farmer's livestock (see [Relation to the Farmer Registry](#relation-to-the-farmer-registry)).
{% endhint %}

The Livestock Registry would be the livestock department's registry. It would hold the animals and what happens to them: births, vaccinations, treatments and sales. It combines the registry platform's two register kinds in one registry: an **entity register** for the animals and an **[activity register](../../products/registry/registry/features/activity-register.md)** for the events. How each kind works (append-only activities, contexts, current state, corrections, participants) is in the activity register [feature](../../products/registry/registry/features/activity-register.md) and [design](../../products/registry/registry/design/activity-register.md) pages; this page says only what the Livestock Registry would put in them.

## Registers

| Register | Kind | Holds |
| --- | --- | --- |
| **Animal** | Entity register | Animal ID, species, sex, date of birth, current owner. Changes go through change requests, approved in AWE. The current owner here is authoritative |
| **Livestock events** | Activity register | Born, Vaccinated, Treated, Sold. The context is the animal |
| **Veterinarian** (or a provider registry) | Entity register | Vets who vaccinate and treat. May live in another registry |

### Events

Participants: the animal (primary), the farmer and the vet; the dam too for Born.

| Event | Verification |
| --- | --- |
| **Born** | Off |
| **Vaccinated** | By a **trusted source**: the vet's authenticated system |
| **Treated** | Not decided |
| **Sold** | When it is an official transfer |

Automatic verification from a trusted source is part of the platform's [Verification and Correction proposal](../../products/registry/registry/design/verification-and-correction.md); today an activity type can only require a supervisor's verification.

### Entities first

An event never creates or changes an animal record:

* **Birth:** the newborn is registered in the Animal register first; the Born event then records the birth against it.
* **Sale:** the owner change goes through the Animal register's own change request, with its approval; the Sold event records the sale.

The events are the history. The animal's current status (last vaccinated, sold) is derived from its events, in the context's current state. The owner is the Animal register's.

### Corrections

* **A wrong vaccine batch or dose:** a Vaccinated event that supersedes the old one, verified again.
* **A sale that didn't happen:** void the Sold event, and correct the owner through the Animal register's change request.

## Keys

| Key | Value |
| --- | --- |
| **Animal** | The registry's own Animal ID (format not decided) |
| **Owner** | The Farmer Registry's Farmer ID, with the national ID alongside, as in the [Crop Sown Registry](../architecture/registries.md#how-it-relates-to-the-farmer-registry) |
| **Vet** | A typed participant: a Veterinarian record in this registry, or an ID held by another system |

The Farmer ID is checked by format only: the Farmer Registry runs in another department, so it is not looked up. The farmer is registered in the Farmer Registry first.

## Relation to the Farmer Registry

* **Until the Livestock Registry exists,** livestock stays in the Farmer Registry as it is: a Livestock section of the farmer, held per herd (type, breed, head count, livestock system), not per animal. See [Farmer Registry domain models](../../products/registry/farmer-registry/README.md#domain-models). It is shared under the `farmer-registry.livestock` scope; Agri Stack's use cases don't read it today.
* **Once it exists,** the Farmer Registry's Livestock section is reduced to a declared summary or removed, so each fact has one authoritative registry.
* The Livestock Registry may want basic farmer details (location, household size) to search and filter its own records. That is the mirror described in [Registry Data Sync](registry-data-sync.md#the-other-direction-mirrors-of-farmer-data).

## What it would share

Like the other registries, over DCI search with consent, its consent data controller being `livestock-registry`:

* a farmer's animals, by Farmer ID or national ID;
* each animal's current state (status, last vaccination);
* the events, with their verification status, as evidence.

Its record types and data scopes are not designed yet. [Adding a data source](../composite/adding-a-data-source.md) and the [Composite](../composite/README.md) example use illustrative ones.

## Related

* [Verification and Correction (Proposal)](../../products/registry/registry/design/verification-and-correction.md)
* [Activity register](../../products/registry/registry/features/activity-register.md) and its [design](../../products/registry/registry/design/activity-register.md)
