---
description: >-
  Design notes for Open Agri Stack: the register model, activity registers, the
  Crop Sown Registry, the use-case composite, and the review of the Activity
  Registry concept notes.
---

# Design

These pages record where the design discussion has landed. Each page says what is built and what is proposed; the [Implementation](../implementation/README.md) part describes what is built, component by component.

| Page | Covers | Status |
| --- | --- | --- |
| [Register model design](register-model-design.md) | One register model with entity and occurrence records; one verification model and one correction model for both; participants and entities first; how the Farmer, Crop Sown and Livestock registries fit; API changes; phases; decisions | Phase 1 built, phase 2 proposed |
| [Activity register](activity-register.md) | Append-only activity registers (attendance, crop sown): what the registry platform needed, where an activity register lives, and how it relates to the Observations design | Built |
| [Crop Sown Registry](crop-sown-registry.md) | The crop season activity register: context, activity types, code lists, projection, indicators, season summary, clusters, channels | Built |
| [Use-case composite](use-case-composite.md) | How a composite use case is configured, validated and run: configuration format, publishing checks, runtime, worked example | First version built |
| [Registry data sync (TODO)](registry-data-sync.md) | Proposal: read-only copies of Farmer Registry data in other registries (Crop Sown, Livestock, …), kept up to date by publish/subscribe and set up by configuration |
| [Concept notes review](concept-notes-review.md) | How the Activity Registry concept notes (crop sown, livestock, work log) compare with the activity register, with suggested priorities | Review (30 September 2026) |
