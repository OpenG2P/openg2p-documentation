---
description: Guides for building custom implementations of the Bridge's extension points
---

# Extensions

The G2P Bridge is extensible: the parts that touch external systems are pluggable, so
you can adapt it to a specific country, sponsor bank, or delivery model without
forking the core. Each guide below describes the interface and how to provide your own
implementation:

* [Financial address resolver](address-resolver/README.md) — resolve a beneficiary ID to a financial address (e.g. [with SPAR](address-resolver/account-mapper-resolution.md)).
* [Sponsor Bank connector](bank-connector-interface-guide.md) — integrate a real sponsor bank in place of the Example Bank.
* [Geo resolver](geo-resolver.md) — resolve geography for in-kind allocation.
* [Warehouse allocator](warehouse-allocator.md) / [Agency allocator](agency-alloctor.md) — in-kind fulfilment allocation.
* [Notification connector](notification-connector.md) — deliver notifications to partners and beneficiaries.

For the conceptual overview of these extension points, see
[Features → Extensibility](../features/extensibility-connect-to-sponsor-banks.md).
