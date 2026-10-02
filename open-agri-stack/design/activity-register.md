---
description: >-
  Append-only activity registers (attendance, crop sown): what they are, what
  the registry platform needed for them, where an activity register lives, and
  how the design relates to the Observations design.
---

# Activity Register

{% hint style="info" %}
For a side-by-side comparison with conventional registers, see [register vs activity register](../architecture/register-vs-activity-register.md). This page uses the Crop Sown Registry as the worked example. How the activity register is built in the registry platform is in [registry platform changes](../implementation/registry-platform.md); the Crop Sown Registry itself is described in [Crop Sown Registry](crop-sown-registry.md).
{% endhint %}

## What it is

An **activity register** records things that happened, such as attendance, sowing, a harvest or a pest sighting. Records are **appended and never edited**. A correction is recorded as a new record that supersedes the old one.

A registry instance can hold:

| Configuration | Example |
| --- | --- |
| **Register only** | Farmer Registry, DA Registry |
| **Activity register only** | Attendance register, a standalone Crop Sown Registry |
| **Both** | Farmer Registry with a "farm visits" activity register attached to the farmer register |

An activity can refer to a subject in the **same instance** (a farmer register next to it) or **held elsewhere** (a Fayda token, a Farmer Registry ID, a plot in another registry). Crop sown is supported both ways; see [where an activity register lives](#where-an-activity-register-lives).

An activity register does **not** use:

* functional ID issuance (optional per activity type, e.g. a receipt number);
* deduplication;
* change requests or maker-checker;
* history tables;
* intake-form mirror tables;
* completion scores;
* registrant authentication.

## Crop sown, remodelled

**How the earlier crop-sown registry implementation is built:** crop sown invents a header register, `CropSown` (one record per farmer, crop year and season). It has **8 child `TABLE` registers**, and every one of them runs through change requests, history and intake forms. It also:

* ships a modified copy of the platform core;
* patches the ingestion worker so that stage forms attach to the right header;
* duplicates approval state in its own fields (`status`, `rejection_reason`, `edit_count`);
* stores every date twice, with an extra `*_date_ec` string holding the Ethiopian-calendar date.

**As an activity register:**

| Before | As an activity register |
| --- | --- |
| `CropSown` header register (functional ID, dedup at 70) | **Activity context** "plot × season": a grouping key (farmer ref + plot ref + crop year + season) with an open/closed status. Crop sown doesn't need to be a register. |
| Planning, Cultivation, Sowing, Production, Harvest, Infestation tables | **Activity types**: `PLANNED`, `LAND_PREPARED`, `SOWN`, `GROWTH_OBSERVED`, `HARVESTED`, `INFESTATION_REPORTED`. Each has a JSON-Schema payload and a few promoted columns. |
| Cluster / CultivationCluster tables | A **cluster register** in the same instance, referenced by activities |
| `lifecycle_stage` on the header | A **projection**: current stage, area sown, yield and last activity per plot × season |
| `farmer_name`, `region_name`… copied onto records | **Typed references** to the Farmer Registry / Fayda and to MDS geography, with names shown through a cached lookup |
| `da_name`, `da_mobile_number` on each line | A reference to the **DA Registry** |
| `status`, `rejection_reason`, `edit_count` | A **lightweight verification** state: submitted → verified / rejected (with reason) |
| `sowing_date_ec`, `harvest_date_ec`… as strings | **Ethiopian calendar support**: store the Gregorian date, enter and display in the Ethiopian calendar |
| `sync_id`, `temporary_land_id` | **Idempotency key** plus **resolution of temporary IDs** created offline |
| Patched ingestion worker (find header, attach child) | Ingestion writes activities directly with context keys, so no parent lookup is needed |
| Custom `dashboard-ui` | **Configured indicators** over projections |

## Changes to the registry platform

### Core platform

1. **Metamodel.** Add an `ACTIVITY` kind to the register definitions, plus **activity type definitions**. An activity type needs no `master_register_id`. Allow instances that have only registers, only activities, or both.
2. **Split the base model.** Break `G2PRegister` into mixins (record base, approvable, identifiable, searchable, linked) and add a `G2PActivity` base with the standard fields:
   * `activity_id`, `activity_type`
   * `occurred_at`, `recorded_at`, `recorded_by`
   * `channel`, `idempotency_key`
   * `supersedes_id`, `status`
   * subject and context references
3. **Write path.**
   * An append API, including batch submission, that bypasses change requests and intake forms.
   * Updates and deletes are blocked at both the API and the database level.
   * Correcting or voiding a record needs permission and a reason.
4. **Ingestion.** ODK, file import and partner ingestion write activities directly.
5. **Search and query.** By subject, context, activity type and time range, across time-partitioned tables.
6. **Access control and data policy.** Filter on the activity's location or owning org unit rather than on a register record's address.
7. **Outgest and DCI.** Publish on insert; support DCI search and subscribe/notify for activities, with consent enforced.
8. **Staff UI.**
   * The activity list with filters is the home screen.
   * A timeline per subject or context.
   * Entry forms reuse the existing `ui-widgets`.
   * Batch entry, e.g. marking attendance for a whole session.
9. **Schema migrations (Alembic).** `create_all` can't change existing tables. This gap affects the whole platform, not just activity registers.

{% hint style="info" %}
As built, the activity model is its own base class, `G2PActivity`, next to an unchanged `G2PRegister` (rather than splitting `G2PRegister` into mixins), and the platform adds new model columns to existing tables on every migration. See [registry platform changes](../implementation/registry-platform.md#data-model).
{% endhint %}

### New features not in the registry platform before

| # | Feature | Why (crop sown / attendance) |
| --- | --- | --- |
| 1 | **Projections** (current-state records) | Current stage per plot × season; attendance rate per person |
| 2 | **Activity context**: a grouping key with open/closed status | Plot × season for crop sown; session for attendance. Replaces the invented header. |
| 3 | **Typed references**: internal register, external registry, Fayda, MDS codes and geography; validation per type (strict / lenient / none); names shown without copying | Farmer and plot held elsewhere; walk-ins at a training session |
| 4 | **Sequence rules**: allowed order, repeatable vs once per context, expected dates | Can't harvest before sowing; infestation is repeatable; harvest due about N days after sowing |
| 5 | **Work lists** from sequence rules | "Plots in my kebele overdue for a harvest visit" |
| 6 | **Lightweight verification** (submitted → verified / rejected) | Supervisor checks a DA's entries without full change management |
| 7 | **Corrections and period locking**: supersede or void with a reason; limits on backdating; closing a period with controlled reopen | No changes to a season after it's closed; no attendance changes after month-end |
| 8 | **Business uniqueness rules**, as well as idempotency | One `SOWN` per plot × season × crop; warn about likely duplicates |
| 9 | **Ethiopian calendar** entry and display | Replaces the duplicate `*_date_ec` string fields |
| 10 | **Support for offline capture**: client-generated IDs, resolving temporary IDs, sync conflicts | ODK in areas with no network; `temporary_land_id` |
| 11 | **Geography on activities**: point or polygon, geo-tagged photos | Plot location at sowing; infestation photo |
| 12 | **Time partitioning, retention and archiving** | Attendance and seasonal data grow quickly |
| 13 | **Configured indicators** over projections | Sown area per woreda, yield per hectare, attendance rate |
| 14 | **Bulk export API** | Analytics, audits, FAO reporting |

Which of these are built is in [registry platform changes](../implementation/registry-platform.md); what is still open (verification, sequence, period-locking and calendar rules; bulk export, file import, archiving, agent-portal entry) is in [open items](../open-items/README.md).

## Where an activity register lives

A crop season can be recorded in either of two places. The platform supports both.

| Deployment | Example | Plot and farmer | Where staff record |
| --- | --- | --- | --- |
| **Its own registry** | The Crop Sown Registry, run by a separate department | References to the Farmer Registry, **checked for format only** (`EXTERNAL`, lenient); the farmer and plot are registered there first (entities first) | The registry's activity pages |
| **Inside a record registry** | A crop-season activity register defined in the Farmer Registry's own extension | The Farmer Registry's own Land and farmer records (`LOCAL_RECORD`, strict); the subject is the Land record | The activity pages, **and** an Activities tab on the Land or farmer record |

* **Registries stay independent.** Registries share data, never code. The Crop Sown Registry stands on its own, like the Disability Registry, and refers to the Farmer Registry only by ID. The Farmer Registry does not depend on it.
* **Crop seasons inside the Farmer Registry are the Farmer Registry's own register.** They would be an activity register defined in the Farmer Registry's extension. It can follow the Crop Sown Registry's activity types, context key and code lists, but it is not the same package.
* **The platform provides what the in-registry case needs**, generically, for any registry:
  * `"subject": true` on a `LOCAL_RECORD` rule: the referenced record (e.g. a Land record) becomes the activity's subject, with its ancestors (the farmer) recorded;
  * `"belongs_to": "<field>"`: the record must be a child of another referenced record, e.g. the plot must be that farmer's. Strict rules reject a mismatch; lenient rules warn;
  * the Activities tab on record profiles;
  * optional seeds (`dbSeed.optionalSeeds`), so a registry can offer an activity register that only some installs switch on.
* **If a country runs both,** one of them has to be authoritative for crop seasons, or the two are merged when data is shared. See [open items](../open-items/README.md).

## Relation to the Observations design

The registry platform's [Observations design](../../products/registry/registry/design/observations-design.md) models the same idea under another name. Both use append-only records, a JSON Schema per type, corrections as new records, lifecycle order, and roll-ups. **The platform term stays "activity" for now.**

**Where the two agree**

| Observations | Activity register |
| --- | --- |
| Observation type, scoped per register | Activity type, scoped per register |
| `VOIDS`: a new record replaces the old one, which is archived | Supersede |
| `FOLLOWS`: harvest links to its sowing | Prior types, with warn or block |
| Payload validated against the type's JSON Schema | Same |

**Where they differ, and what we chose**

| Topic | Observations | Activity register | Decision |
| --- | --- | --- | --- |
| Where the data lives | Inside the subject's registry; recorded from the record's profile | A register of its own. The subject can be in the same registry or in another one | **Support both.** See [where an activity register lives](#where-an-activity-register-lives). |
| Storage | One generic platform table for every type in every register; types added through an API, with no code | One table per register from the extension, with typed columns, yearly partitions and an append-only trigger | **Keep per-register tables.** Both deployments of crop sown ship an extension, and crop sown needs typed columns, partitions and a domain service. A generic, code-free table is deferred ([open items](../open-items/README.md)). |
| Grouping a lifecycle | An explicit `FOLLOWS` link, chosen by the agent, one step at a time | A context derived from the payload (plot × year × season × crop) | **Keep contexts.** They handle an 8-step lifecycle and intercropping. An explicit link is an option for types that can't derive a key. |
| Roll-ups | Asynchronous: optional enrichment, then adapter-computed aggregates per subject and period, with history | Synchronous: a projection per context, recomputed in the same transaction, plus declarative indicators | **Keep projections for current state; add aggregates and enrichment as an asynchronous layer on top.** |
| Geography | Resolved from the subject's record (walking Land → Individual → Household) when aggregates are computed; `geo_dimensions` holds code and name per level; a reporting view groups by `geo_1…geo_5` | Named levels snapshotted on each activity when written, from the activity, the subject's record or the context | **Named levels, as there; snapshot rather than live resolution**, so it works when the subject is in another registry. See [geography and roll-ups](../implementation/registry-platform.md#geography-and-roll-ups). |
| Code lists | The registry's local `G2PAttribute` tables | Read live from Master Data | **Ours.** The local tables no longer exist in the platform. |
| Offline sync | Batch endpoint with no idempotency | Idempotency key, temporary IDs | Ours |
| Governance | Not covered | Verification, period locks, reference rules, DCI with consent, data policies, permissions | Ours |

**Taken from the Observations design** (built)

* **A tab on the subject's profile.** A record in a record register (e.g. a Farmer Registry Land or farmer record) lists the activities about it and about its child records, per activity register, with their summaries, and can record a new one with the subject filled in.
* **`schema_version`**, incremented on the activity type and stamped on each activity; every version is kept.
* **Provenance:** the existing `channel` (staff portal, agent portal, partner, ODK, file) and `source_partner_id` already say where an activity came from. The partner is authenticated by its signature, with keys from Partner Management. `submission_id` is new: one per batch.
* **An asynchronous layer on top of projections,** run by the outbox worker through two domain hooks:
  * **`enrich`**, e.g. weather or satellite data, stored beside the activity and never inside it;
  * **`aggregate`**, roll-ups per subject and period, recomputed from current data, with history. The Crop Sown Registry's is a farmer's season summary across plots and crops.
* **Form defaults** from the latest activity of the same type for the same context or subject.
* **Geography as named levels** (`geo_dimensions`), filled by the platform, on activities, projections and aggregates; **indicators by level**; a **reporting view per registry** by level.
* **Season windows** in the domain code: a season's period is its own date range, not just its year.
* **The same data for partners:** aggregates are readable through DCI with the consent clamp, not only in the staff UI.

Still to take ([open items](../open-items/README.md)): per-type switches for enrichment and aggregation with per-stage status, a beneficiary API, and agent-app capture.

Not taken: offline drafts with a sync badge (a client concern; the platform already has idempotency and temporary IDs), and choice chips (the forms already render code lists as selections).
