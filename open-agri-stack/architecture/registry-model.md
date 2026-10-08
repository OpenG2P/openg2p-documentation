---
description: >-
  How each Agri Stack registry is built: register, table and activity
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

## Layer 2: catalogues

Layer 2 is the **catalogues**: the reference data every registry uses, defined once for the country. There is no reference data inside a registry.

* **What the catalogues hold:**
  * simple code lists (gender, tenure type, units, crop types);
  * richer reference entities such as seed varieties, input products and breeds;
  * geography: admin areas, with boundaries.
* **Today:** the [Master Data Service (MDS)](../../platform/platform-services/master-data-service/README.md) serves this role. Registries read code lists and geography from it live, over a direct connection to its database, and the country pack's agriculture domain is loaded into it.
* **Decision: extend MDS.** The catalogue is being built as [MDS as Catalogue](../../platform/platform-services/master-data-service/catalogue/README.md): versioned lists and geography, drafts with approval, immutable published versions, latest / pinned / as-of reads, a crosswalk for boundary changes, and a change feed. The GeoPrism Registry was evaluated: it has strong temporal geography, but versioning and approvals cover only geographic lists, it runs on Java and OrientDB, and it has no Helm chart or Keycloak integration. MDS therefore borrows its ideas (working and published versions, split/merge lineage); an import adapter from GeoPrism or the Common Geo Registry is a possible later add-on.
* **What the catalogue provides:**
  * **typed attributes per list**, so an entity like a seed variety can carry crop, maturity days, release year and agro-ecological zone (for example an attribute set validated by a JSON Schema defined per list);
  * approvals (AWE), audit and history;
  * a public read API and a change feed, instead of registries reading a database directly.
* Codes are defined by the country; international classifications are optional mappings. Publish code lists in SKOS-shaped JSON-LD, and boundaries through OGC API – Features.

See also [Country Data Architecture](../../platform/country-data-architecture.md) for country packs.
