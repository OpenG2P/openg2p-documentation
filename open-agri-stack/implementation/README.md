---
description: >-
  What is built for Open Agri Stack (October 2026), component by component, and
  how.
---

# Implementation

These pages describe what is built and how. The design behind each part is in [Design](../design/README.md); what is still open is in [TODOs and open items](../open-items/README.md).

| Component | What was built | Page |
| --- | --- | --- |
| **Registry platform** | Activity registers (data model, write path, projections, aggregates, final figures on period lock, geography, indicators, staff UI); typed participants; partner corrections; per-subject and filtered DCI queries on activity registers; aggregate search across subjects for allow-listed partners; consent per registry and subject enforcement; `context_fields` and `ui_hints`; the activity register configuration file (declarations, output record templates per format, JSON Logic plausibility rules); the sample-data task | [Registry platform changes](registry-platform.md) |
| **Consent Manager** | One consent with a grant per registry; bindings per (partner, controller); replay per (`jti`, controller); a stored decision returned only after the binding and signature checks | [Consent Manager changes](consent-manager.md) |
| **Crop Sown Registry** | The crop-season activity register; the Cluster entity register; sample clusters and crop seasons; DCI records (activities, crop seasons, season summaries); reporting views | [Crop Sown Registry (as built)](crop-sown-registry.md) |
| **Farmer Registry** | Declared main crops replacing the Crops tab; sample lands numbered to match the Crop Sown Registry; `FARMER_ID` in the DCI farmer record | [Farmer Registry changes](farmer-registry.md) |
| **Use-case composite** | The generic composite service, its partner API, the `loan-profile` use case, Helm chart, partner test kit and end-to-end test | [Composite as built](composite.md) |
| **Standards** | The open standards used in each area, our own formats, and standards still to explore | [Standards](standards.md) |

## Repositories

| Repository | What |
| --- | --- |
| [OpenG2P/registry-platform](https://github.com/OpenG2P/registry-platform) | The registry platform, including activity registers |
| [OpenG2P/crop-sown-registry](https://github.com/OpenG2P/crop-sown-registry) | The Crop Sown Registry extension and chart |
| [OpenG2P/farmer-registry](https://github.com/OpenG2P/farmer-registry) | The Farmer Registry extension and chart |
| [OpenG2P/consent-manager](https://github.com/OpenG2P/consent-manager) | The Consent Manager |
| [openg2p/agri-stack](https://github.com/openg2p/agri-stack) | The use-case composite (`composite/`): service, Helm chart, use cases, scripts |
