---
description: >-
  Design notes for Agri Stack: the Composite, registry data sync, the
  Livestock Registry.
---

# Design

These pages record where the design discussion has landed. Each page says what is built and what is proposed. Built products are documented with each product (for example [activity registers](../../products/registry/registry/features/activity-register.md) and the [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md)); what Agri Stack configures in each install is in [Configuration](../configuration/README.md).

| Page | Covers | Status |
| --- | --- | --- |
| [Composite](composite.md) | How a Composite use case is configured, validated and run: configuration format, publishing checks, runtime, worked example | First version built; publishing checks and data-blind mode proposed |
| [Registry data sync](registry-data-sync.md) | Registries sharing data with each other through outgestion and ingestion: crop activity from Crop Sown kept in the Farmer Registry (reference design), the gaps, mirrors of farmer data | Proposal, not in use |
| [Livestock Registry](livestock-registry.md) | An Animal register and a livestock events activity register in one registry: events, entities first, corrections, keys, relation to the Farmer Registry, what it would share | Planned, design only |

The platform-wide proposal for one verification model and one correction model for both register kinds is in the Registry Platform: [Verification and Correction (Proposal)](../../products/registry/registry/design/verification-and-correction.md).
