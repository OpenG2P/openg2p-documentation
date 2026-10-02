---
description: >-
  The trust and correction vocabulary used across Open Agri Stack registries:
  validation, change, correction, void, approval of changes, verification and
  dispute.
---

# Terms: Validation, Correction, Verification

The registry's job is that its records are **authentic, and verified where that is needed**. Whether a programme will act on a record (approval for payment or eligibility) is decided in PBMS, not here.

These terms apply to both record kinds: **entity** registers (a farmer, a plot) and **activity** registers, whose records are occurrences (a sowing, a vaccination). See [register vs activity register](register-vs-activity-register.md).

| Term | What it means | What happens to the data | Entity register | Activity register |
| --- | --- | --- | --- | --- |
| **Validation** | Automatic checks at entry: format, required fields, code lists, plausibility | Bad input is rejected or warned on; nothing is stored about it | Built | Built |
| **Change** | The world changed: the farmer moved, got a new phone, sold a plot | New version; the old value stays in history as true _at that time_ | Change request | Doesn't apply: an occurrence never changes; a new event is a new activity |
| **Correction** | The record was wrong: a typo, a mis-measured area | New version; the old value is marked as an error, never true | Change request marked as a correction, with a reason | Supersede, with a reason |
| **Void** | The record shouldn't exist: a duplicate, an event that never happened | Kept, but no longer counts | Record status (e.g. deactivated) | Void, with a reason |
| **Approval** (of a change) | A supervisor authorises a change or correction before it enters the register | Governs who may change data; says nothing about whether it is true | AWE on change requests, as built | Not needed: appends and corrections are governed by permissions and rules |
| **Verification** | An independent check that recorded data matches reality or an authoritative source: a field visit, a document, a Fayda lookup, a trusted device | **Never changes the data.** Adds a trust status (verified, failed or pending), with who checked, how and with what evidence | Phase 2 | Built as a single step; moves onto the common model |
| **Dispute** | The person concerned says a record is wrong | Triggers verification, then a correction if the claim holds | Phase 2 | Phase 2 |

**How they relate:**

* Verification is about **truth**; approval is about **authority to change**. Both can apply to the same data.
* A change or correction **resets the verification** of what it touched: new data hasn't been checked.
* A failed verification leads to a **correction** or a **void**; it never edits the data itself.

The verification model, the correction model and the phases in which they are built are in the [register model design](../design/register-model-design.md#trust-layer-verification).
