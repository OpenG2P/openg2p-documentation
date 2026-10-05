---
description: >-
  The registry platform's two kinds of register compared, as built: nature of
  the data, definition, configuration, writing, reading, figures and
  governance.
---

# Register vs Activity Register

The registry platform has two kinds of register. They solve different problems and are built differently. This page compares them as built today, first at a glance and then in detail. The examples are the Farmer Registry's **Farmer** register and the Crop Sown Registry's **CropSown** activity register.

**In one line:**

* **A register holds the current truth about an entity** (a farmer, a plot, a household). The record is edited over time through approved change requests, and a history of its versions is kept.
* **An activity register holds what happened** (planned, sown, observed, harvested). Each activity is a new record, appended and never edited. The current state and the figures are _derived_ from the activities.

## At a glance

| | Register (conventional) | Activity register |
| --- | --- | --- |
| **What a row is** | An entity: one farmer, one plot | An event: one sowing, one harvest, one pest sighting |
| **Unit that grows** | Number of entities (roughly stable) | Number of events (grows every season, without bound) |
| **Lifecycle of a row** | Created, then **edited** many times; status Active / Inactive / Archived | **Appended once, never edited.** Corrected by a new activity that supersedes it, or voided. Only status and verification can change. |
| **How data gets in** | **Change requests**: staff portal, intake forms and partner ingestion all become change requests, approved through the AWE workflow (maker-checker) | **Append**: staff portal (single or batch), partner API, ODK Central. There is no change request. Optional supervisor **verification** for chosen types. |
| **History** | A history table per register: a new version on each approved change | The activities _are_ the history. Superseded and voided activities stay. |
| **Identity** | `internal_record_id`, plus an issued **functional ID** (e.g. Farmer ID), dedup, optional registrant authentication | `activity_id` plus an **idempotency key** (no duplicates on retry or offline sync). No functional ID, no dedup. |
| **Grouping** | Parent/child registers (Farmer → Land, Household → Members) | **Contexts**: a key derived from the payload (plot × year × season × crop), open or closed |
| **Current state** | The record itself | A **projection**: one row per context, recomputed from its activities in the same transaction |
| **Defined by** | Extension code (the register's table model) + seed (register definition, sections, tabs, UI schemas) | Extension code (activity and projection models, domain rules) + seed (activity types: JSON Schema, rules, references; indicators; ODK mappings) |
| **Form** | Configured **sections and tabs** of UI widgets | Generated from each activity type's **JSON Schema**; code lists as dropdowns; Ethiopian-calendar date entry; location picker |
| **Validation** | Widget and field rules; code-list check on change requests | JSON Schema, **reference rules** (code lists, geography, records, external IDs; strict / lenient / none), **sequence rules** (e.g. no harvest before sowing), dates and closed periods |
| **Code lists** | Read live from the catalogues (MDS; widget `attribute_id`) | Read live from the catalogues (MDS; reference rule `attribute`) |
| **Geography** | The record's address (`geo_lowest_level_value_id` and its hierarchy) | Every activity is **located** when written, as named levels (region, zone, woreda) |
| **Figures** | Counts of records; reporting views per registry | **Indicators** (by crop, season, region, zone, woreda…), **aggregates** per subject and period with history, **reporting views** by level |
| **Read by staff** | Record search and profile; change requests; version history | Activities, crop seasons (current state), work list, indicators, summaries; an **Activities tab** on records of the same registry |
| **Shared with partners** | DCI search of records, through the register's template, filtered to the consented data scopes | DCI search of **activities**, **current state per context** (e.g. a crop season) and **aggregates**, with the same consent clamp |
| **Storage** | One table per register (plus history and intake-form tables) | One table per register, **partitioned by year**, with an append-only database trigger; shared tables for types, contexts, locks, outbox |
| **Platform features it does not use** | Contexts, projections, verification, period locks | Change requests, AWE, history tables, intake forms, functional IDs, dedup, completion scores, registrant authentication |

## 1. Nature of the data

**Register.** A register is about **who or what something is**: a farmer's name, gender and Fayda FAN, a plot's size and tenure. Such facts change slowly and are corrected when wrong. What matters is the _latest approved version_, plus an audit trail of how it got there. A register can have child registers (a Farmer's Land records), linked by `link_internal_record_id`.

**Activity register.** An activity register is about **what happened, when, where and by whom**: on this date, this farmer sowed 0.9 ha of teff on this plot with improved seed. Facts accumulate. A later observation doesn't replace an earlier one, and an error is fixed by a new record that points to the one it replaces (`supersedes_activity_id`). Every activity records:

* **When:** `occurred_at`, entered in the Gregorian or Ethiopian calendar, and `recorded_at`.
* **Who:** `recorded_by`.
* **How it arrived:** `channel`, `submission_id` (the batch it came in), and the partner if any.
* **Its form version:** `schema_version`.
* **Its subject:** e.g. a farmer ID, or a record in the same registry.
* **Where:** `geo_dimensions`.
* **Checks:** reference results and rule warnings.

Activities are grouped into **contexts**, such as one crop on one plot in one season. The domain code derives the context key from the payload, so a whole crop season (plan → sow → observe → harvest) hangs together without a header record.

## 2. How each is defined

Both are defined by a registry **extension** (code) plus a **seed** (data loaded by db-seed on every install). Reference data such as code lists and geography comes from **Master Data**, not from either.

| Layer | Register | Activity register |
| --- | --- | --- |
| **Extension code** | `G2PRegister<Name>` table model (+ `G2PRegisterHistory<Name>`, `G2PIntakeForm<Name>`), domain service for search text and record names | `G2PActivity<Name>`: the activity table, with payload fields stored in their own typed columns for search, policies and indicators. `G2PActivityProjection<Name>`: the current-state table. `G2PActivityDomainService<Name>`: the context key, derived values (e.g. yield), plausibility warnings, the projection, aggregates, DCI record shapes. |
| **Seed** | Register definition (`register_purpose = REGISTER` or `TABLE`), sections, tabs, UI schemas, intake-form definitions, DCI templates | Register definition (`register_purpose = ACTIVITY`), **activity types** (JSON Schema, rules, reference rules), **indicators**, ODK form mappings, DCI template, reporting views |
| **Catalogues (MDS)** | Code lists and geography for the form's widgets | Code lists and geography for reference rules and the location |

The platform creates both kinds of table from the models on migration, and adds new columns to existing tables on upgrade. An activity register's table is also partitioned by year and protected by an append-only trigger.

An activity register **can't be created from the Registers configuration screen**. Its tables come from the extension's code. Its mnemonic and purpose are fixed once it exists.

## 3. How each is configured

| What | Register | Activity register |
| --- | --- | --- |
| **The form** | Sections and tabs of widgets, edited in the Registers configuration screens | Each activity type's JSON Schema. The form is generated from it: code-list fields become dropdowns, the location field becomes a region → zone → woreda picker, and date fields use the Ethiopian calendar. |
| **Rules** | Required fields and widget validation; approval workflow per register (AWE) | Per activity type:<br>• repeatable or once per context;<br>• uniqueness fields;<br>• prior types, with warn or block;<br>• due window, feeding the work list;<br>• backdating limit;<br>• supervisor verification.<br>Per register: closed periods. |
| **References** | Widgets bound to catalogue lists or geography | Reference rules per field:<br>• `ATTRIBUTE` (a catalogue list, in MDS);<br>• `GEO` (geography, optionally at a level and marked as the location);<br>• `LOCAL_RECORD` (a record in the same registry, optionally the subject, optionally required to belong to another record);<br>• `EXTERNAL` (another registry's ID, format-checked or looked up).<br>Each rule can be strict, lenient or off. |
| **Versioning** | Form changes apply to later edits | Each change to a type's schema increments `schema_version`. Every activity stores the version it was validated against, and every version is kept. |
| **Figures** | Reporting views per registry | Indicators (sum, average, count or distinct count over a projection column, grouped and filtered by any column or `geo:<level>`) and reporting views |
| **Optional parts** | — | Optional seeds (`dbSeed.optionalSeeds`), so a registry can offer an activity register that only some installs switch on |

In the Crop Sown Registry, activity types, indicators and ODK mappings are written in `scripts/activity_definitions.py` for readability, and turned into the seed SQL that ships. That script is a developer tool and never runs in a deployment.

## 4. How data is written

**Register: a change request.**

1. Staff, an intake form or a partner submits a change.
2. It becomes a change request, which may be deduplicated.
3. AWE routes it for approval (maker-checker).
4. On approval the record is created or updated. A version is written to history, and a functional ID is issued if the register issues one.

**Activity register: one append, in one transaction.**

1. **Duplicate check:** a repeated idempotency key returns the existing activity.
2. **Payload:** dates are converted; the domain code adds derived values; the payload is checked against the type's JSON Schema.
3. **References:** each is checked by its rule, and the subject is taken from a reference marked as the subject.
4. **Context:** the context is found or opened, then locked.
5. **Rules:** dates, closed periods, repeatability, uniqueness and sequence. Warnings are kept on the activity; blocking rules reject it.
6. **Location:** taken from the activity's own location field, else the subject's record, else its context.
7. **Save:** the activity is inserted, the context's projection is recomputed, and an outbox event is written.

A background worker then works through the outbox:

* publishes events;
* runs **enrichment** (e.g. weather data), stored beside the activity and never inside it;
* runs **aggregates**, e.g. a farmer's season summary, recomputed from current data and kept with history.

**Corrections:** supersede (replace) or void (withdraw). Each needs a reason, and none is allowed inside a closed period. **Verification** (verify or reject) is separate: it records whether the activity is true and never changes it. The [terms](terms.md) (validation, change, correction, void, approval, verification, dispute) are defined on their own page.

## 5. How data is read

| Reader | Register | Activity register |
| --- | --- | --- |
| **Staff** | Search, record profile, child records, change requests, version history | Per register:<br>• activities (filters, detail with the correction chain);<br>• current state per context;<br>• work list (what's due or overdue);<br>• indicators;<br>• summaries;<br>• record entry.<br>Per context: a timeline. On a record of the same registry: an **Activities** tab listing activities about it and its children, with their summaries. |
| **Home page** | The Registers card counts registers | Counted in the same Registers card (by contexts, e.g. crop seasons) and chosen from the same dropdown, marked "(Activity)" |
| **Partners (DCI)** | Record search, rendered through the register's DCI template, filtered to the consented data scopes | Chosen by record type:<br>• **activities** (the evidence);<br>• **current state per context**, e.g. `…:CropSeason`: stage, areas, yield, verified — what a subsidy or loan decision reads;<br>• **aggregates**, e.g. a farmer's season summary.<br>All three are clamped to the same consent scopes. |
| **Analysts** | Reporting views | Reporting views by region, zone and woreda (plain views over the projection, so always current) |

## 6. Figures and geography

**Register:** the record is the unit, so figures are counts and breakdowns of records (farmers by region, by gender) from its reporting views.

**Activity register:** activities are the raw material, and the figures come from three layers built on them:

1. **The projection:** one exact current-state row per context, updated in the same transaction as each activity.
2. **Aggregates:** per subject and period (e.g. a farmer's Meher season), recomputed asynchronously, with history. These are what decisions about one subject read.
3. **Indicators and reporting views** over the projections: per area, at any geographic level.

Geography is stored on every activity as **named levels** (`{"region": {"code": "ET04", "name": "Oromia"}, …}`), snapshotted when it's written. That keeps history stable when a record is later edited, and it works even when the subject lives in another registry.

## 7. Governance

| | Register | Activity register |
| --- | --- | --- |
| **Approval of changes** (who may change data) | AWE workflows on change requests | Not needed: appends and corrections are governed by permissions and rules |
| **Verification** (is it true) | A verification table tied to change requests | Optional verification (submitted → verified / rejected) per activity type |
| **Closing a period** | — | Period locks: no writes or corrections inside a closed period, with controlled reopening |
| **Permissions** | `register:*` and change-request actions | `activity:view`, `create`, `correct`, `verify`, `configure` |
| **Data policies** | Filter records; a policy on a missing column is skipped | Filter activities and projections; a policy on a missing column **denies** access (fails closed) |
| **Consent** | Records filtered to the consented [data scopes](../../products/registry/registry/design/data-scopes.md) (by default one per register section) before rendering | The same, with scopes over activity, context-state and aggregate fields (`<Register>.activity.*`, `.context.*`, `.aggregate.*`) |
| **Deleting** | Records can be deactivated or archived | Nothing is deleted; the database trigger rejects deletes and edits other than to status and verification |

## 8. When to use which, and how they fit together

* **Use a register** for things you identify, deduplicate and maintain over time: people, households, plots, organisations.
* **Use an activity register** for things that happen repeatedly to those things, and whose history and totals you need: sowings, harvests, visits, attendance, payments.
* **Both can live in one registry.** Activities can then refer to the registry's own records (`LOCAL_RECORD`), take their subject and location from them, and appear on those records' profile. Or the activity register can be a registry of its own, like the Crop Sown Registry, referring to another registry's records by ID. Registries share data, never code.

See also:

* [Register model design](../design/register-model-design.md): the proposal to unify trust and corrections across both kinds, and the API changes that follow;
* [Activity register](../design/activity-register.md), for the design, and [registry platform changes](../implementation/registry-platform.md), for how it is built;
* [Crop Sown Registry](../design/crop-sown-registry.md), for the worked example;
* [Registry model](registry-model.md).
