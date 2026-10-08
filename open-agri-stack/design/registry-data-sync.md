---
description: >-
  TODO design: keeping read-only copies of Farmer Registry data in other
  registries (Crop Sown, Livestock, …) by publish/subscribe, set up by
  configuration rather than connector code.
---

# Registry Data Sync (TODO)

{% hint style="warning" %}
**Status: proposal, not built.** This page records the design discussed for syncing data between registries. Nothing here is implemented yet; see [what the platform is missing](#what-the-registry-platform-is-missing).
{% endhint %}

## The need

Registries may be owned by different departments. The Crop Sown Registry (CSR), and later a Livestock registry and others, need some of the Farmer Registry's (FR) data, such as basic farmer details, demographics and household size, to operate on their own:

* search and filter farmers by their own criteria (e.g. farmers in a woreda with more than 2 ha);
* link their own records (crop seasons, clusters, herds) to a farmer;
* keep working when FR is slow or briefly unavailable.

FR stays the **source of truth**. A single farmer's data for a partner is already served by the [use-case composite](use-case-composite.md); this page is about a **department operating on a copy**.

For registry-to-registry sharing, a **blanket (standing) consent** from the farmer is assumed, recorded as a policy rather than per-farmer consents.

## Proposal: publish/subscribe into read-only mirror registers

1. **The source publishes changes.** When a register record (e.g. Farmer) is created, changed, corrected or retired, the source registry publishes an event to a topic. The registry platform's outgestion can publish register changes over [WebSub](https://www.w3.org/TR/websub/), and commons-services now installs a WebSub hub; the registries still need to be pointed at it.
   * The event carries the record **filtered to the agreed [data scopes](../../products/registry/registry/design/data-scopes.md)**, so each subscriber receives only what it is allowed.
   * Each event carries the record's **version** and is **signed** by the source (keys in Partner Management).
2. **The subscriber keeps a mirror register.** The subscribing registry defines a register such as "Farmer (from FR)" with its own fields and a mapping from the source's fields, and ingests the events through the platform's existing ingestion pipeline (incoming models and templates).
   * Upserts are keyed on the source's functional ID and **version**, so duplicate and out-of-order events are harmless.
   * A retired source record is marked inactive in the mirror, never silently deleted.
3. **Mirrors are read-only.** No change requests and no local edits. The subscriber's own records link to the mirrored record by the source's ID.
4. **First load and catch-up.** A new subscriber loads a snapshot with a paged search on the source, then switches to the live stream. After downtime it asks the source for "changes since version/cursor N" to fill the gap.
5. **Standing consent as a policy.** The registry-to-registry agreement is a Consent Manager policy: subscriber (audience), source (controller), scopes, a purpose such as "programme administration", periodic fetch. The source checks it when the subscription is set up and periodically afterwards.

### Configuration, not connectors

A subscription is one configuration entry:

| Setting | Example |
| --- | --- |
| Source registry and register | `farmer-registry`, `Farmer` |
| Scopes | `farmer-registry.personal_details`, `farmer-registry.household` |
| Target mirror register | CSR `FarmerMirror` |
| Field mapping | incoming template from the source record to the mirror's fields |
| Topic / hub | the source's WebSub topic for the register |
| Policy | the CM policy (audience, controller, purpose) that authorises it |

Adding a Livestock registry as a subscriber is another entry, not new code.

## Alternatives considered

| Option | Why not (for now) |
| --- | --- |
| Shared database or read replica | Couples the registries; goes against registries sharing data, never code. |
| Query-only through the composite | Good for one farmer; the subscriber cannot search or filter locally. |
| Database change capture (e.g. Debezium) | Heavy infrastructure; subscribers become coupled to the source's tables. |
| Raw Kafka feed | Kafka is already in commons and could replace WebSub as the transport later; the design above stays the same. |

The approach follows the same shape as DCI's subscribe/notify.

## What the registry platform is missing

* A **mirror register** type: read-only, sourced from another registry.
* **Scope filtering on outgoing events** (today it applies to DCI search only).
* **Versioned, idempotent upserts and retirement** on ingestion.
* A **"changes since" endpoint** for catch-up after downtime.
* **Subscription configuration**, and the **standing-consent check** against the Consent Manager.
* **Monitoring:** lag and failed events per subscription.

## Open questions

* How fresh must a copy be: minutes or daily?
* How many records (farmers) are expected, and how often do they change?
* Can a subscriber add its own fields to a mirrored record, or must those always live in its own registers?
