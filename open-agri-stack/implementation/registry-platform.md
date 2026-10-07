---
description: >-
  How activity registers and the register model's phase 1 are built in the
  OpenG2P registry platform: data model, write path, final figures, interfaces,
  geography, DCI queries, consent per registry, and sample data.
---

# Registry Platform Changes

This is how the [activity register](../design/activity-register.md) and phase 1 of the [register model design](../design/register-model-design.md#phase-1-built) are built in the registry platform ([OpenG2P/registry-platform](https://github.com/OpenG2P/registry-platform), developed on branch `feature/activity-register` and in `develop`). For a side-by-side comparison with conventional registers, see [register vs activity register](../architecture/register-vs-activity-register.md).

## Data model

The activity model is **its own base class**, `G2PActivity`, next to `G2PRegister`. `G2PRegister` itself is unchanged, so existing registries behave exactly as before.

| Table | Purpose |
| --- | --- |
| `g2p_register_definitions` (existing) | An activity register is a row with `register_purpose = ACTIVITY` |
| `g2p_activity_<name>` (per register) | The activities. Standard fields plus a JSONB `payload`, and payload fields promoted to typed columns for filtering, indexes, data policies and indicators. Each activity also carries its location as named levels (`geo_dimensions`; see [geography and roll-ups](#geography-and-roll-ups)). **Partitioned by year** of `occurred_at`, plus a default partition. |
| `g2p_activity_projection_<name>` (per register) | The current state, one row per context, with the context's location (`geo_dimensions`) |
| `g2p_activity_types` | Per type: JSON Schema, form layout, rules (repeatable, uniqueness, prior types with warn/block, due window, backdating limit, verification), reference rules, Ethiopian-calendar fields |
| `g2p_activity_contexts` | Grouping key (e.g. plot × year × season × crop) with subject, attributes and open/closed status. A context can replace another (`replaces_context_id` / `replaced_by_context_id`, e.g. the crop was changed); the replaced one is closed |
| `g2p_activity_participants` | Who or what took part in each activity, in a named role: farmer (primary), plot, development agent, cluster. Each is **typed**: `LOCAL` (a register in this registry, resolved to the record) or `EXTERNAL` (another system's ID). The type's `participant_roles` maps each role to a payload field |
| `g2p_activity_period_locks` | Closed periods, with who reopened them and why |
| `g2p_activity_idempotency_keys` | One activity per key, across all partitions |
| `g2p_activity_outbox` | Events written in the same transaction as the activity |
| `g2p_activity_temporary_references` | Offline temporary IDs and what they resolved to |
| `g2p_activity_indicators` | Indicator definitions: aggregate, column, group-by, filters. No SQL is stored in configuration. |
| `g2p_activity_odk_forms`, `g2p_activity_odk_failures` | ODK Central form mappings and the submissions that failed |
| `g2p_activity_type_schemas` | Every payload schema an activity type has had, by `schema_version`. A trigger increments the version when the schema changes, whether the change comes from a seed, an API or by hand. |
| `g2p_activity_enrichments` | Derived or external data for one activity, written asynchronously; kept beside the activity, never inside it |
| `g2p_activity_aggregates`, `g2p_activity_aggregate_history` | Roll-ups per subject, aggregate type and period (`period_key` with start and end dates, geography and custom dimensions), and every value each has had. An aggregate is **final** or provisional (see [final figures](#final-figures)) |

* **Append-only is enforced in the database.** A trigger rejects `DELETE`, and rejects any `UPDATE` that touches columns other than status and verification.
* **Extensions need no migration code.** The platform migration finds an extension's `G2PActivity…` and `G2PActivityProjection…` models and creates them: partitions, indexes and trigger.
* **Upgrades add columns in place.** `create_all` never alters an existing table, so on every migration the platform adds any column a model has gained, nullable or with its default, to the shared activity tables and to each register's activity and projection tables.
* **Each activity records:**
  * `schema_version`: the version of the activity type's schema it was validated against;
  * `submission_id`: one id per batch. A partner message, an ODK pull run and a staff batch each get one;
  * its subject: when the subject is a record in the same registry, the register it is in, and that record's ancestors (a plot's farmer) as they were at the time.

## Writing an activity (one transaction)

1. **Idempotency.** If the idempotency key has been seen before, return the existing activity.
2. **Prepare the payload.**
   * Convert Ethiopian-calendar dates.
   * Let the domain service add derived values (e.g. yield per hectare).
   * Validate against the type's JSON Schema.
3. **Check references.**
   * Code lists, including nested rows such as fertiliser types: strict. The registry holds no copy; it reads them from Master Data.
   * Master Data geography.
   * Records in the same registry.
   * External IDs: pattern only, or a lookup through the domain service; strict, lenient or none.
   * Temporary IDs: recorded now and resolved later. Supported, but not used by the Crop Sown Registry (entities first).
4. **Find or open the context** and lock it, so concurrent writes to one context are serialised.
5. **Check rules:** dates, closed periods, repeatability, uniqueness, sequence, and the register's [plausibility rules](../design/activity-register.md#rules) (JSON Logic, from its configuration file). Warnings are stored on the activity; blocking rules reject it.
6. **Locate it:** record where the activity happened as named Master Data levels ([geography and roll-ups](#geography-and-roll-ups)).
7. **Save.** Insert the activity, its participants and its idempotency key, recompute the context's projection in the same transaction, and write an outbox event.

**Corrections:**

* **Supersede:** a new activity replaces the old one; the old one is kept as `SUPERSEDED`.
* **Void:** the activity no longer counts, but stays in the history.
* **Verify or reject:** changes only the verification columns.
* All of these need a reason and are blocked inside closed periods.

**Context fields and UI hints.** The activity UI holds no register-specific fields. The register declares, in its [configuration file](../design/activity-register.md#activity-register-configuration) (or its domain service, which wins):

* `context_fields`: the fields that make up the context key. They are locked in a correction, and a supersede can't change them (a correction can't move an activity to another crop season);
* `ui_hints`: summary fields, context columns, the fields carried from one row to the next in batch entry, and search hints.

## Final figures

A payment or official statistic needs a figure that won't change. An aggregate becomes **final** (`is_final`, with when and by whose lock) when:

* its type is one the register lists (`final_on_period_lock` in its configuration file, e.g. a worker's monthly attendance, a farmer's season summary);
* an active period lock for all activity types covers its whole period;
* every activity event in that period has been processed;
* its value was last changed by an event raised before the lock.

It is finalised when the period is locked, or after the outbox worker catches up. Reopening the lock makes it provisional again.

**A late change** (an activity outside the locked window that still feeds the aggregate, e.g. a plan made before the season) makes a final aggregate provisional. It stays provisional until the period is reopened and locked again, so a figure is never final and wrong, and a change after payment is visible. A register whose aggregates draw on activities outside their period should lock the wider window.

## Interfaces

| Where | What |
| --- | --- |
| Staff API `/activity/*` | Registers and types (types include code-list options for forms); append (single and batch, atomic or per item, with participants); supersede, void, verify, reject; get, search (also by participant and role), timeline; contexts (open, close, reopen); work list; projections; indicators; period locks; temporary references; rebuild projections; **a record's activities and summaries across registers** (`get_subject_activities`, for the profile tab); **the latest activity of a type** (`get_latest_activity`, for form defaults); **aggregates and their history**; **a type's schema versions** |
| Partner API `/partner/activity/append_activities` | DCI-style signed envelope (PM keys); per-item outcomes. Activities can name participants (`participants[]`: role + ID) |
| Partner API `/partner/activity/correct_activities` | Same envelope: supersede (with the corrected fields) or void, with a reason. A partner can only correct activities it submitted |
| Partner API `/dci/registry/sync/search` | See [DCI search of activity registers](#dci-search-of-activity-registers) |
| Celery | `activity_outbox_worker` (outgest; enrichment and aggregates through the register's `enrich` and `aggregate` hooks), `activity_reconcile_worker` (repairs projection drift), `activity_partition_worker` (next year's partitions), `activity_odk_pull_worker` (ODK Central), `activity_sample_data_worker` (demo installs only: records each register's sample activities once, from its domain service's `sample_activities` hook, through the normal write path) |
| Staff UI | Activity registers are listed with the other registers: the home page's Registers card counts them (with their number of contexts, e.g. crop seasons) and its register dropdown offers them as "(Activity)", opening `/activity/<register>`. Per register: activities (filters, detail panel with verify/reject/correct/void, and participants), current state, work list, indicators, record (single or batch, form generated from the JSON Schema, Ethiopian-calendar date picker), settings. Per context: current state, timeline, record the next activity, and the context it replaced or was replaced by. |

## DCI search of activity registers

`reg_type` can be an activity register. A search returns current activities only, rendered by the register's DCI template, filtered to the consented data scopes as records are. The `reg_record_type` picks what comes back, by subject ID:

* **activities** (default);
* **current state per context**, when the record type names a context type (e.g. `spdci-extensions-agri:CropSeason` → `CROP_SEASON`): each crop season's stage, areas, yield and verification, from the projection. This is what a subsidy or loan decision reads;
* **aggregates**, when it ends in `Aggregate` (e.g. a farmer's season summaries).

The register shapes the state and aggregate records with the `dci` templates of its [configuration file](../design/activity-register.md#output-formats) (or the domain hooks `dci_state_record`, `dci_aggregate_record`, which win; without either, a generic record). Each row is filtered to the consented [data scopes](../../products/registry/registry/design/data-scopes.md) before it is shaped; an activity register defines those over `<Register>.activity.*`, `<Register>.context.*` and `<Register>.aggregate.*` fields (aggregates by column only).

**Per-subject and filtered queries.** Every search of an activity register can name its subject exactly: an `expression` with `subject_id` plus filters, on fields the view itself has:

* activities: any plain column (type, dates, verification, promoted payload fields);
* state: projection columns;
* aggregates: `aggregate_type`, period, `is_final` and custom dimensions (e.g. `crop_year`, `season`).

Filters accept ISO date-times. The operators are those of entity searches (`$eq`, `$in`, `$gte`…). Results come newest first, so "the farmer's last 10 activities" is a subject search with `page_size: 10`. All DCI search is synchronous.

An exact-field search of an entity register (e.g. the Farmer register by `foundational_id`) also returns the record's linked records, as a search by ID does.

**Aggregates across subjects.** A search with no `subject_id` (e.g. every worker's final monthly attendance for a benefit run) is allowed only for partners the registry operator lists in `dci_bulk_aggregate_partners`, with the data scopes each may receive:

| Setting (partner API) | Default | Meaning |
| --- | --- | --- |
| `REGISTRY_PARTNER_API_DCI_BULK_AGGREGATE_PARTNERS` | `{}` (off) | JSON: `sender_id` → the data scopes it may receive, data scope IDs, e.g. `{"benefits-system": ["crop-sown-registry.crop_season", "crop-sown-registry.measures"]}` (a bare name means this registry's scope) |
| `REGISTRY_PARTNER_API_DCI_BULK_AGGREGATE_MAX_PAGE_SIZE` | `500` | Page size cap for such searches |

There is no per-person consent for such a search, so those scopes, at their current versions, replace the Consent Manager's; the signature is still verified. The search must name the `aggregate_type`. Moving this allow-list into a Partner Management policy is an [open item](../open-items/README.md).

## Consent per registry and subject enforcement

The registry's partner API takes part in the [one consent, a grant per registry](../architecture/consent-model.md) model:

* it sends its own **data controller** (`global.consentDataController`, defaulting to the registry variant, e.g. `farmer-registry`, `crop-sown-registry`) to CM `/validate`, so CM evaluates only this registry's grant;
* it checks that the **consent's subject is the person searched**: in an entity register every returned record's foundational or functional ID must equal it; in an activity register the searched subject must equal it or be linked to it by the register's own data (`subject_id_fields`, e.g. a farmer ID recorded with the farmer's Fayda FAN);
* it filters each record to the fields of the consent's **data scopes** (`<controller>.<name>`, from the registry's versioned scope catalogue, signed `POST /partner/data_scopes`) before rendering it, reading each scope as it was when the consent was issued. Scopes are named groups of the registry's own fields, not DCI keys. See [Data Scopes](../../products/registry/registry/design/data-scopes.md);
* it logs `header.meta.on_behalf_of` when a composite calls for a partner.

How a registry enforces consent, its switches and its settings are in [Consent-aware data sharing](../../products/registry/registry/features/consent-aware-data-sharing.md) and [Registry integration (the PEP side)](../../consent-management/design/registry-integration.md).

## Geography and roll-ups

An activity register piles up activities. People then ask for figures by region, zone or woreda, or for one plot or farmer. So **every activity records where it happened**, as the named levels Master Data holds:

```
geo_dimensions = {"country": {"code": "ET", "name": "Ethiopia"},
                  "region":  {"code": "ET04", "name": "Oromia"},
                  "zone":    {"code": "ET0406", "name": "North Shewa (OR)"},
                  "woreda":  {"code": "ET040611", "name": "Sheno town"}}
```

**Where the location comes from**, in order:

1. **The activity itself:** a payload field with a GEO rule marked `"location": true` (else `geo_lowest_level_value_id`). This is what was observed, e.g. the plot's woreda.
2. **The subject's record, when it is in the same registry:** that record's location, else its parent's (a plot without one takes its farmer's).
3. **The activity's context:** the location of its latest activity that has one, so later stages of a crop season needn't repeat it.

**It's a snapshot, taken when the activity is written.** In the Observations design the location is resolved from the subject's record when roll-ups are computed. A snapshot works when the subject is in another registry (the Crop Sown Registry on its own instance knows only what the activity says), and it keeps history stable when a record is later edited.

**How it's rolled up:**

* **Projections** carry their context's location.
* **Indicators** group and filter by any level with `geo:<level>`, e.g. `"group_by": ["crop_year", "season", "geo:region", "crop"]`. The result has the level's code and name.
* **Aggregates** carry the location in `geo_dimensions`. The platform fills it from the activity unless the domain chooses one; the Crop Sown Registry uses the levels all of a farmer's plots share.
* **Reporting views**, one per registry, flatten the levels into columns and aggregate by level for Superset and Insights. They are plain views over the projection, which is already current, so there is no refresh job.

**Two kinds of numbers:**

* **Per subject** (a farmer's season, a plot's crop season): projections and aggregates. They are what a decision reads, e.g. fertiliser subsidy eligibility, through the staff API or DCI.
* **Per area:** indicators and reporting views over the projections. Area totals are computed from projections rather than stored as aggregates, since one activity would otherwise mean recomputing a whole woreda's or region's totals.

## Permissions, data policies and identity

* **Permissions:** `activity:view`, `activity:create`, `activity:correct`, `activity:verify`, `activity:configure`. They are mapped onto the existing IAM roles by the registry's IAM registration.
* **Data policies fail closed for activity registers.** A policy on a column the activity table doesn't have denies access, instead of being skipped as it is for record registers.
* **An activity register's identity is fixed.** Its mnemonic names the extension's activity classes, so the generic register configuration can't rename it or switch it to or from a record register, and "Add Register" can't create an `ACTIVITY` register. That configuration also counts activities and contexts when deciding whether the register holds data, which is what stops a register in use from being deleted.

## Phase 1 of the register model

| Change | What was built in the platform |
| --- | --- |
| **Participants** | `participant_roles` per activity type (role → payload field, primary flag); typed, indexed participants (`g2p_activity_participants`); `append` accepts `participants[]`; search by participant and role; the profile tab finds a record in any role; participants in the staff UI |
| **Entities first** | Strict local-entity checks (e.g. the cluster must exist in the Cluster register); external IDs stay format-only |
| **Partner corrections** | `/partner/activity/correct_activities` |
| **Crop-change link** | A context can name the context it replaces; the old one is closed and both point to each other in the projection, reporting view, DCI and staff UI |
| **Sample data** | The `activity_sample_data_worker` task and the `sample_activities` domain hook (on when `activity_load_sample_data` is set) |
| **Optional seeds** | `dbSeed.optionalSeeds`, for activity registers only some installs switch on |

## Related settings and fixes

* **Celery worker and beat** wait for Redis before starting; the worker's liveness probe pings the worker, so a worker that stops consuming is restarted.
* **Build pins and migrations:** core pins `sqlalchemy[asyncio] >=2.0,<2.1`, and core migration takes a Postgres advisory lock; see [open items](../open-items/README.md) for what remains.
