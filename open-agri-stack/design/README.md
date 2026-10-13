---
description: >-
  Design notes for Agri Stack: the register model, the use-case composite,
  registry data sync, the distributed deployment across departments, and the
  review of the Activity Registry concept notes.
---

# Design

These pages record where the design discussion has landed. Each page says what is built and what is proposed. Built products are documented with each product (for example [activity registers](../../products/registry/registry/features/activity-register.md) and the [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md)); what Agri Stack configures in each install is in [Configuration](../configuration/README.md).

| Page | Covers | Status |
| --- | --- | --- |
| [Register model design](register-model-design.md) | One register model with entity and occurrence records; one verification model and one correction model for both; participants and entities first; how the Farmer, Crop Sown and Livestock registries fit; API changes; phases; decisions | Phase 1 built, phase 2 proposed |
| [Use-case composite](use-case-composite.md) | How a composite use case is configured, validated and run: configuration format, publishing checks, runtime, worked example | First version built |
| [Registry data sync](registry-data-sync.md) | Registries sharing data with each other through outgestion and ingestion: crop activity from Crop Sown kept in the Farmer Registry (reference design), the gaps, mirrors of farmer data | Proposal, not in use |
| [Distributed deployment architecture](distributed-deployment-architecture.md) | One install per registry in each department and one shared exchange install for Open AgriNet (OAN): what is shared, the consent and policy model between them, networking, and what is still to build | Phase 1 built; phases 2–3 to build |
| [Concept notes review](concept-notes-review.md) | How the Activity Registry concept notes (crop sown, livestock, work log) compare with the activity register, with suggested priorities | Review (30 September 2026) |
