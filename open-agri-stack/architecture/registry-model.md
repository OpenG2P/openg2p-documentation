---
description: >-
  How each Open Agri Stack registry is built: register, table and activity
  register kinds, projections, and where reference data lives (Layer 2).
---

# Registry Model

Registries run on the OpenG2P [registry platform](../../products/registry/registry/README.md), which supports **two kinds, register and activity register, plus child tables**. A registry instance can hold only registers, only an activity register, or both. [Register vs activity register](register-vs-activity-register.md) compares them in detail.

| Kind | Behaviour | Platform features | Examples |
| --- | --- | --- | --- |
| **Register** | Changeable, governed entities, person or not | Change requests + AWE, history, functional ID, dedup (can be switched off), DCI | Farmer, household, DA, training session, cluster |
| **Table** | Child rows owned by a register record | Inherits from its parent | Land parcels, household members |
| **Activity register** | Append-only records of activities. A correction supersedes the earlier record; nothing is edited in place. Can stand alone or relate to a register. | Idempotency key, occurred/recorded time, external references, batch entry, time partitioning. No ID issuance, change requests or history tables. See [activity register](../design/activity-register.md). | Sown, harvested, attended, paid |

## Projections

A projection is current state computed from activities: for example, the current crop stage per plot per season, or a beneficiary's 360 view.

* **Per-subject projections** (current crop stage, 360 view) are updated in the same database transaction as the activity, so they are always exact.
* **Aggregates for dashboards** are updated asynchronously. Each change is recorded in an outbox and the projection is recomputed idempotently from it; lag alerts and a nightly reconciliation job catch anything that falls behind. Any projection can be rebuilt from the activities.

## Layer 2 split

All Layer 2 reference data lives in the [Master Data Service (MDS)](../../platform/platform-services/master-data-service/README.md). There is no separate reference registry.

* **What MDS holds:**
  * simple code lists (gender, tenure type, units, crop types);
  * richer reference entities such as seed varieties, input products and breeds;
  * geography: admin areas, with boundaries stored in MinIO.
* **What MDS needs to gain:**
  * **typed attributes per list**, so an entity like a seed variety can carry crop, maturity days, release year and agro-ecological zone (for example a JSONB attribute set validated by a JSON Schema defined per list);
  * approvals through AWE;
  * audit and history;
  * a public read API and a change feed. Registries read code lists live today, but over a direct connection to MDS's database.
* Codes are defined by the country; international classifications are optional mappings. Publish code lists in SKOS-shaped JSON-LD, and boundaries through OGC API – Features.

See also [Country Data Architecture](../../platform/country-data-architecture.md) for country packs.
