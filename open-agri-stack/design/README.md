---
description: >-
  Design notes for Agri Stack: registry data sync, the Livestock Registry,
  interoperability with OAN (Beckn).
---

# Design

These pages record where the design discussion has landed. Each page says what is built and what is proposed. Built products are documented with each product (for example [activity registers](../../products/registry/registry/features/activity-register.md) and the [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md)); how each install is set up for Agri Stack is in [Deployment](../deployment/README.md).

The Composite's design is in its own section: [Composite](../composite/README.md).

| Page | Covers | Status |
| --- | --- | --- |
| [Registry data sync](registry-data-sync.md) | Registries sharing data with each other through outgestion and ingestion: crop activity from Crop Sown kept in the Farmer Registry (reference design), the gaps, mirrors of farmer data | Proposal, not in use |
| [Livestock Registry](livestock-registry.md) | An Animal register and a livestock events activity register in one registry: events, entities first, corrections, keys, relation to the Farmer Registry, what it would share | Planned, design only |
| [Interoperability with OAN (Beckn)](oan-interoperability.md) | The Composite as a provider node on the Open Agri Network: use cases as catalogue items, the Beckn order as the query, a beckn-onix adapter; open questions | Proposal, not built |

The platform-wide proposal for one verification model and one correction model for both register kinds is in the Registry Platform: [Verification and Correction (Proposal)](../../products/registry/registry/design/verification-and-correction.md).
