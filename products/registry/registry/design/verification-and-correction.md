---
description: >-
  Proposal: one verification model and one correction model for both entity
  registers and activity registers, the API changes that follow, and the
  decisions taken so far.
---

# Verification and Correction (Proposal)

{% hint style="warning" %}
**Status: proposed, not built.** This page describes a design. What exists today is stated as such, and is documented in [Activity register](../features/activity-register.md), its [design](activity-register.md), [Change management](change-management.md) and [VC issuance](vc-issuance.md).
{% endhint %}

A registry can hold two kinds of register: **entity registers**, whose records are maintained over time (a person, a plot, an animal), and **activity registers**, whose records are occurrences (a visit, a sowing, a vaccination). How they differ is in [Activity register](../features/activity-register.md#register-and-activity-register-compared).

Today each kind has its own way to verify and to correct a record. This proposal gives both kinds:

* **one trust layer** (verification);
* **one correction model**, with disputes;
* the **API changes** that follow.

**Already built** (not part of this proposal): typed participants per activity, entities first, partner corrections of activities, a context that names the context it replaces, and verification status in an activity register's DCI output. See [Activity register](../features/activity-register.md) and its [design](activity-register.md).

The registry's job is that its records are **authentic, and verified where that is needed**. Whether a programme acts on a record (approval for payment or eligibility) is decided outside the registry, in the programme system (PBMS).

## Today

| | Entity register | Activity register |
| --- | --- | --- |
| **Verification** | Rows in `g2p_register_verifications`, each tied to a change request or an intake submission (`/verifications/get_verifications`, `add_verification`) | Columns on the activity: `verification_status` (`NOT_REQUIRED`, `SUBMITTED`, `VERIFIED`, `REJECTED`), `verified_by`, `verified_at`, `verification_remarks`. Switched on per activity type (`requires_verification`); `verify_activity` and `reject_activity` |
| **Approval of changes** | AWE, on change requests and intake submissions | None: appends and corrections are governed by permissions (`activity:correct`) and rules |
| **Corrections** | A change request: a new version, the old one kept in history. Nothing marks it as a correction rather than a change | Supersede or void, with a reason |
| **Disputes** | None | None |
| **Certificates** | Verifiable credentials from the agent portal ([VC issuance](vc-issuance.md)) | None |

## Trust layer: verification

### Verification policy

Set in configuration. What needs verifying depends on the registry, so the **target** is chosen per case:

* a **field** (for example the national ID, checked against the ID system);
* a **section** (for example land tenure, from a document);
* the **whole record**;
* an **activity type** (for example Sown, as the Crop Sown Registry does today).

For each target, the policy says:

* whether verification is **required**;
* which **methods** count: manual (a supervisor or field officer), document, a system check against an authoritative source, or a **trusted source** whose authenticated submissions count as verified (a vet's system, a biometric device);
* **who** may verify (roles);
* what **evidence** is expected (a photo, a document, a device capture).

### Verification records

A **verification record** is attached to a target. It holds:

* **outcome** (verified or failed) and **method**;
* **actor** (a person, a system or a trusted source);
* **evidence** references;
* **remarks**, and **when**.

A target can have several: a verification, a dispute, a re-verification. The log is kept.

### Verification status

Derived from the records. It is what the staff portal shows, and what the APIs filter on and share:

| Status | Meaning |
| --- | --- |
| `NOT_REQUIRED` | The policy does not ask for verification |
| `PENDING` | Required, not yet done (today's `SUBMITTED` on activities) |
| `VERIFIED` | The latest outcome is verified |
| `FAILED` | The latest outcome is failed (today's `REJECTED` on activities) |
| `DISPUTED` | A dispute is open |

A change or correction to a verified target sets it back to `PENDING`: new data hasn't been checked.

### Verification by an activity

A field check is itself something that happened, so it can be recorded as an **activity**: a site visit with a photo, a GPS point and a short form, whose participant is the record being checked (a sowing, a plot, a person). The verification activity type declares what it verifies, and its outcome creates the verification record, with the activity as its evidence.

This gives a verification a date, a place and evidence, ODK and agent capture, and a work list of visits due. The **status** still sits on the target, because other methods (an ID lookup, a trusted device) set it too. The visit is the evidence; the status is the result.

### Mapping from today

* `g2p_register_verifications` and the verification columns on activities both become **verification records**.
* AWE approval of change requests stays as it is. It governs who may change data, not whether the data is true.
* Certificates stay outside the model. They are verifiable credentials, issued by the existing [VC issuance](vc-issuance.md) feature, not a trust step.
* The default policy reproduces today's behaviour: activity verification only where `requires_verification` is set, entity verification as now. Existing registries need no change.

## One correction model

A **correction** fixes data that was wrong, always with a **reason**. A **change** records that the world changed. How each lands depends on the kind:

| Situation | Entity register | Activity register |
| --- | --- | --- |
| **A value was wrong** | Change request **marked as a correction**, with a reason → new version; history keeps the old one, marked as an error | A correcting activity **supersedes** the old one, which stays (built) |
| **It shouldn't exist** | Deactivate | **Void**: it didn't happen; it stays (built) |
| **Who may** | Change requests go through AWE, as today | The `activity:correct` permission, as today |
| **Disputed** (the person concerned says it's wrong) | A dispute recorded against the target; resolved by verification, then a correction if the claim holds | Same |
| **Verification after** | The changed fields go back to `PENDING` | The correcting activity starts `PENDING` if its type requires verification |

**A resurvey.** An agent re-measures a plot and gets a different value. It is either a **correction** (the first measure was wrong) or a **new observation** (things changed). The form asks which. For an activity, a correction supersedes and a new observation is a new activity; for an entity, both are change requests, and only the correction is marked as one.

A failed verification leads to a correction or a void. It never edits the data itself.

## Shared capabilities for entity registers

Some capabilities built for activity registers would serve entity registers too:

| Capability | Activity register today | Proposed for entity registers |
| --- | --- | --- |
| **Reference rules** (Master Data list, geography, local record, external ID; strict or lenient) | Built | On entity sections, beyond widget-bound lists |
| **Location as named levels** (`geo_dimensions`) | Built | On entity records too, for area statistics (today they have `geo_code_hierarchy_json`) |
| **Idempotent ingestion** | Built (idempotency key per activity) | Idempotency keys on entity ingestion |
| **Derived values** | A context's current state, aggregates, indicators | For example a person's total land area, a household's size |
| **One form definition** | Generated from the type's JSON Schema, with `section_ui_schema` layout | One form definition for both kinds; only what happens on submit differs (a change request or an append) |
| **Participants with roles** | Built | For relations beyond a parent (a member's cooperative, a worker's employer). Not yet needed |

## API changes

All of these are additive: existing endpoints keep working.

**Staff API**

| Area | Change |
| --- | --- |
| **Verification** (new, common) | `/verification/*`: get the policy for a register, section, field or activity type; add a verification record (verified, failed, dispute) on any target, with evidence; list a target's records and status; list items awaiting verification (a work queue). `/verifications/*`, `verify_activity` and `reject_activity` remain as shortcuts onto it |
| **Corrections** | Entity change requests can be marked as corrections, with a reason (approved in AWE as today). `supersede_activity` and `void_activity` stay. Both reset the verification of what they touch |
| **Entity registers** | Named-level locations on records; reference rules on sections; idempotency keys on ingestion |

**Partner API**

| Area | Change |
| --- | --- |
| **Trusted sources** | Partner Management marks a partner as a trusted source for given activity types or fields. Its signed submissions record an automatic verification, with the signature as evidence |
| **Verification status in responses** | Every record type carries its status, filtered by consent like any other field. Searches can require a status, for example only verified records. (Today an activity register's output templates can include it, as the Crop Sown Registry's do; entity records don't carry it) |
| **Subscribe / notify** | Subscribe to activity events (appended, superseded, voided, verified), published from the existing outbox, so a programme hears when a record is verified or corrected |

**Beneficiary API**

| Area | Change |
| --- | --- |
| **Own activities** | A person's own activities, contexts and summaries |
| **Disputes** | Dispute a record or activity about oneself, for staff to resolve by verification and, if the claim holds, a correction |

## Phase 2

The built pieces listed above were phase 1. Phase 2 is this proposal:

1. **Verification model**, common to both kinds: policies per field, section, record or activity type; verification records with evidence; derived status; automatic verification from trusted sources; status on every record type in partner responses.
2. **Corrections and disputes:** corrections marked as such on change requests; disputes; a change or correction resets verification.
3. **Shared capabilities on entity registers:** named-level locations, reference rules, idempotent ingestion.
4. **Beneficiary API for activities** (it needs beneficiary authentication on the registry first), and **subscribe / notify** for activity events.

## Decisions

| Question | Decision |
| --- | --- |
| Programme approval and certificates in the trust layer? | **No.** The registry keeps records authentic and verified; whether a programme acts on them is decided in PBMS. VC issuance stays as it is, outside the verification model |
| Approval vs verification | **Separate.** Approval (AWE) is about authority to change data; verification is about whether it is true. Both can apply to the same data |
| What is verified | **Configurable per case:** a field, a section, the whole record or an activity type. Each target says whether it is required, which methods count, who verifies and what evidence |
| Verification vocabulary | `NOT_REQUIRED`, `PENDING`, `VERIFIED`, `FAILED`, `DISPUTED`. The activity lifecycle stays as built (`ACTIVE`, `SUPERSEDED`, `VOIDED`) |
| Does verification change data? | **Never.** It adds a status; a failed check leads to a correction or a void |

## Open questions

* When a record a credential was issued from is changed or corrected, should the credential be suspended or revoked? Today it is not.
* Does a rejected (`FAILED`) activity keep dropping out of the current state, as today, under the common model?

## Related

* [Activity register](../features/activity-register.md) and its [design](activity-register.md)
* [Change management](change-management.md)
* [VC issuance](vc-issuance.md)
* [Agri Stack terms: validation, correction, verification](../../../../open-agri-stack/architecture/terms.md): the vocabulary as used in Agri Stack
