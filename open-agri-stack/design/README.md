---
description: Design notes and proposals.
---

# Design

These pages record where the design discussion has landed. Each page says what is built and what is proposed. Built products are documented with each product (for example [activity registers](../../products/registry/registry/features/activity-register.md) and the [Crop Sown Registry](../../products/registry/crop-sown-registry/README.md)); how each install is set up for Agri Stack is in [Deployment](../deployment/README.md).

The Composite's design is in its own section: [Composite](../composite/README.md).

| Page | Covers | Status |
| --- | --- | --- |
| [Registry data sync](registry-data-sync.md) | Registries sharing data with each other through outgestion and ingestion: crop activity from Crop Sown kept in the Farmer Registry (reference design), the gaps, mirrors of farmer data | Proposal, not in use |
| [Livestock Registry](livestock-registry.md) | An Animal register and a livestock events activity register in one registry: events, entities first, corrections, keys, relation to the Farmer Registry, what it would share | Planned, design only |
| [Interoperability with OAN (Beckn)](oan-interoperability.md) | The Composite as a provider node on the Open Agri Network: use cases as catalogue items, the Beckn order as the query, a beckn-onix adapter; open questions | Proposal, not built |
| [Rate Limiting](rate-limiting.md) | The three layers (edge, identity-aware edge, application); the edge limit at the ingress gateway and the per-partner limit in the Composite shared in Redis; what is later | Built; partner-aware edge limits and quotas later |
| [API Gateway](api-gateway.md) | The functions of an API gateway, met by the ingress (Nginx, Istio) and the services, with no gateway product; networking between installs | Decided; built except restricting the registries' partner APIs |
| [Data Sharing Gateway](data-sharing-gateway.md) | The Exchange as a generic gateway; stacks as packs; standard-aware connectors per registry; use cases written by administrators; the Exchange setup done at install, in any order | Setup at install built; the rest decided, not built |

The platform-wide proposal for one verification model and one correction model for both register kinds is in the Registry Platform: [Verification and Correction (Proposal)](../../products/registry/registry/design/verification-and-correction.md).
