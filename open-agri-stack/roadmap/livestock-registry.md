---
description: >-
  A Livestock Registry: the Animal register and the livestock events, their
  fields, checks, verification and corrections
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

### Fields

**Animal** (entity register):

| Field | Value |
| --- | --- |
| `animal_id` | The registry's own Animal ID (format not decided) |
| `species`, `breed` | Master Data lists (`LIVESTOCK_TYPE`, `LIVESTOCK_BREED`) |
| `sex` | Master Data list |
| `date_of_birth` | Date |
| `owner_farmer_id` | The current owner or keeper: the Farmer Registry's Farmer ID, with the national ID alongside. Authoritative here |
| `dam_id` | The mother, where known: another Animal ID |

**Livestock events** (activity register). Each event also carries the platform's provenance: `occurred_at` (when it happened), `recorded_at` and `recorded_by` (when and by whom it was recorded), the channel and the partner it came through.

| Event | Participants (roles) | Payload | `occurred_at` |
| --- | --- | --- | --- |
| **Born** | Animal (primary, the newborn), farmer; dam | Not fixed yet | Date of birth |
| **Vaccinated** | Animal (primary), farmer, vet | `vaccine` (Master Data list), `batch`, `dose` | When the animal was vaccinated |
| **Treated** | Animal (primary), farmer, vet | Not fixed yet; same shape as Vaccinated | When it was treated |
| **Sold** | Animal (primary), seller (the farmer), buyer | Not fixed yet | Date of sale |

The context is the animal. Born occurs once per animal; the others may repeat.

### Checks before storing

An event is stored only if its references hold. These are the activity register's **reference rules**, set to strict (reject): there is no reviewer and no verification status for them.

* the animal is registered in the Animal register;
* the vaccine (or treatment) is a value in its Master Data list;
* the vet is a Veterinarian record allowed for this type, or a valid ID held by another system;
* the farmer's Farmer ID is well formed (format only: the Farmer Registry is in another department).

### Source and verification

Where an event came from (the vet's own system, an agent app, another system) is its **source**, recorded on the activity. A vet's authenticated submission can also be the basis for **verification**. One submission, two records: the source on the activity, the verification as a verification record.

An event can be stored before it is verified. Verification never changes it.

| Event | Verification |
| --- | --- |
| **Born** | Off |
| **Vaccinated** | By a **trusted source**: the vet's authenticated system. Evidence: the vaccine batch, the vet's credentials, a vaccination document |
| **Treated** | As Vaccinated (not decided) |
| **Sold** | Off, unless it is the programme's official transfer of ownership |

Automatic verification from a trusted source is part of the platform's [Verification and Correction proposal](../../products/registry/registry/design/verification-and-correction.md); today an activity type can only require a supervisor's verification.

### Approval

The activity register has no approval step. Approval is needed only when something is issued from an event: a certificate (birth, vaccination, movement or sale), a payment (a vaccination campaign, a treatment) or an official figure (herd size, vaccination coverage). That approval belongs to the programme that issues it ([PBMS](../../pbms/README.md)), not to the registry. A sale that is an official transfer of ownership is approved through the Animal register's owner change request.

### Entities first

An event never creates or changes an animal record:

* **Birth:** the newborn is registered in the Animal register; the Born event records the birth against it. Registering the animal does not replace the birth event.
* **Sale:** the owner change goes through the Animal register's own change request, with its approval; the Sold event records the sale. One sale leads to both records; they stay separate.
* **Vaccination and treatment** change nothing on the animal.

The events are the history. The animal's current status is derived from its events, in the context's current state: Vaccinated, Treated, Vaccinated, Sold gives **Sold**, with the last vaccination. The owner is the Animal register's.

### Corrections

An event is never edited; the original stays for audit.

| Situation | Correction |
| --- | --- |
| A wrong vaccine, batch, dose or date | A Vaccinated event that **supersedes** the old one, verified again. A partner corrects the events it submitted |
| The vaccination did not happen | **Void** the event |
| The animal's identity, sex or ID is wrong | Change request on the Animal register |
| A sale was wrongly recorded | Supersede or void the Sold event, and correct the owner through the Animal register's change request |
| Wrong birth details | Supersede the Born event. The animal stays |
| The animal should never have been registered | The Animal register's own process; the Born event, if recorded, is voided so the history matches |

## Keys

| Key | Value |
| --- | --- |
| **Animal** | The registry's own Animal ID (format not decided) |
| **Owner** | The Farmer Registry's Farmer ID, with the national ID alongside, as in the [Crop Sown Registry](../registries/README.md#farmer-id-across-registries) |
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

Its record types and data scopes are not designed yet. [Adding a Registry](../registries/adding-a-registry.md) and the [Composite](../composite/README.md) example use illustrative ones.

## Related

* [Verification and Correction (Proposal)](../../products/registry/registry/design/verification-and-correction.md)
* [Activity register](../../products/registry/registry/features/activity-register.md) and its [design](../../products/registry/registry/design/activity-register.md)
