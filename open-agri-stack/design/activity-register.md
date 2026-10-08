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

{% hint style="info" %}
This section is about the **earlier crop-sown implementation by ATI** ([cropsown-regsitry](https://github.com/Centre-for-Open-Societal-Systems/cropsown-regsitry)), which predates the activity register. It is not how Agri Stack is built. The registry platform is generic: activity registers are one of its features, available to any registry, and the [Crop Sown Registry](crop-sown-registry.md) is a thin extension on it with no modified platform code.
{% endhint %}

**How the earlier crop-sown implementation is built:** it invents a header register, `CropSown` (one record per farmer, crop year and season). It has **8 child `TABLE` registers**, and every one of them runs through change requests, history and intake forms. It also:

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
| `farmer_name`, `region_name`… copied onto records | **Typed references** to the Farmer Registry / Fayda and to catalogue geography (MDS), with names shown through a cached lookup |
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
| 3 | **Typed references**: internal register, external registry, Fayda, catalogue codes and geography (MDS); validation per type (strict / lenient / none); names shown without copying | Farmer and plot held elsewhere; walk-ins at a training session |
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

## Current state, summaries and indicators

An activity register derives three kinds of figures from its activities. In the staff UI they appear as **Current state**, **Summaries** and **Indicators**.

| Figure | What it is | Crop Sown example | Stored? |
| --- | --- | --- | --- |
| **Current state** (projection) | The latest state of one **context**, kept up to date as activities arrive | One crop season: plot + crop year + season + crop | Yes, one row per context |
| **Summary** (aggregate) | A value per **subject** per period, derived from that subject's contexts | A farmer's season summary (`FARMER_SEASON_SUMMARY`): area sown and harvest across all their plots | Yes, versioned, and **final** once the period is locked |
| **Indicator** | A statistic across **many subjects**, grouped and filtered (including by any geography level) | Area sown by woreda and crop; farmers reporting by woreda | No, computed when asked |

### Who defines what

| Part | Registry platform (generic) | Extension (per register) |
| --- | --- | --- |
| Context (what "current state" is keyed by) | Stores contexts and projections; keeps them up to date | Declares the context fields in its [configuration file](#activity-register-configuration) (CSR: farmer, plot, crop year, season, crop), derives the context key in code, and defines the projection's columns |
| Subject (who a summary is about) | Stores `subject_type` and `subject_id` generically | Declares the subject in its configuration file: CSR's is `FARMER_ID`, set from the activity's `farmer_id`, with the Fayda FAN as an alternative identifier (`subject_id_fields`). Other registers may use a worker, a household or a cluster. |
| Summaries | Runs and stores them, keeps history, finalises them when a period is locked | Defines each summary type and how it is computed |
| Indicators | The indicator table, computation (count, distinct count, sum, average, min, max; group by and filter, `geo:<level>`), the staff API and the Indicators panel | **Only the definitions**, as seed data (CSR: `20_g2p_activity_indicators.sql`, 12 indicators). A new activity register gets indicators by adding rows, no code. |

### Who can see them

* **Staff UI:** a subject's record shows its current state and summaries (with their history) on its Activities tab; the activity register's page has the Indicators panel. Each staff user sees only what their data policy allows.
* **Partners:** per subject only, and with consent. Summaries are returned by DCI search as the `spdci-extensions-agri:ActivityAggregate` record type (our own, not a published DCI type), filtered by subject, summary type and dimensions (e.g. crop year, season), within the partner's [data scopes](../../products/registry/registry/design/data-scopes.md). A new kind of figure, such as a monthly yield, is a new summary type defined by the extension; the API does not change. Indicators are not offered to partners.

### Operational and analytical indicators

Choose where an indicator belongs before defining it:

| | Operational: staff UI Indicators | Analytical: reporting (Superset) |
| --- | --- | --- |
| Used for | Day-to-day work and follow-up | Analysis and management reporting |
| Freshness | Live, computed when opened | Refreshed on a schedule |
| Scope | The user's own area (their data policy applies) | Across regions and periods |
| Examples | Pending verifications; crops by stage; farmers reporting this season in my woreda; area sown so far | Trends over seasons; comparisons between regions; yield distributions; reports for management |

Guidelines:

* Keep the staff UI to a **few** operational indicators that staff act on; too many turn the panel into a dashboard.
* Statistics not about a particular subject belong to **reporting**: build views (or materialised views) and Superset dashboards as and when they are needed, rather than adding indicators for them.
* An indicator should read cheaply from current state (one projection table, simple grouping). If it needs joins, history or heavy computation, it belongs to reporting.

## Activity register configuration

An activity register's declarations, output records and plausibility rules are **configuration**, not code, so a new activity register needs less code. The extension ships one file per register, `meta_data/activity-config/<register mnemonic>.json` (setting `activity_config_path` overrides the directory), with its templates beside it. The platform validates the file when the register is first used and reports every problem at once (error `ACT-ERR-023`); a register without a file runs on its domain service and the platform defaults.

| Key | What it declares | Crop Sown |
| --- | --- | --- |
| `context_fields` | The payload fields that place an activity in its context; a correction can't change them | farmer, plot, crop year, season, crop |
| `subject` | `subject_type`, and `subject_id_fields`: activity fields holding another identifier of the subject, for consent subject checks | `FARMER_ID`; Fayda FAN |
| `ui_hints` | How the staff UI shows the register: summary fields, context columns, fields carried between batch rows, search hints | |
| `final_on_period_lock` | Aggregate types that become final when their period is locked | `FARMER_SEASON_SUMMARY` |
| `search_fields` | Payload fields added to an activity's search text | farmer, FAN, plot, crop, cluster |
| `formats` | Output record templates, per output format and record kind (below) | `dci`: crop season state and season summary |
| `rules` | Plausibility rules (below) | Four warnings |

**Precedence.** Per declaration or hook: a domain service that sets the attribute or overrides the method wins; otherwise the configuration file; otherwise the platform default. A domain service that overrides `validate` and still wants the configured rules calls `super().validate(...)`.

**What stays code** (for now): deriving the context key (`build_context`), derived values (`enrich_payload`), the projection (`project`), aggregates (`aggregate`), enrichment and sample data.

### Output formats

DCI is one way of sharing data; other standards may follow. Records are therefore internal and format-independent (a context's current state from the projection, an aggregate) and are **filtered to the partner's consented [data scopes](../../products/registry/registry/design/data-scopes.md) before they are rendered**. Each output format then names a Jinja template per record kind:

```json
"formats": {
  "dci": {
    "state":     {"record_type": "spdci-extensions-agri:CropSeason",         "template": "templates/crop_sown_dci_state.json.j2"},
    "aggregate": {"record_type": "spdci-extensions-agri:ActivityAggregate", "template": "templates/crop_sown_dci_aggregate.json.j2"}
  }
}
```

* A template renders JSON. It sees `record`, `record_type`, `output_format`, `kind` and `register_mnemonic`, in the platform's lenient template environment (the one data scopes use: a missing or non-consented field is `null` under `tojson`).
* Two filters: `pick("a", "b")` takes those fields of the record; `or_null` turns a group whose values are all null (not consented, or nothing recorded) into `null`.
* The DCI partner API asks for format `dci`. A register without a `dci` template gets the platform's generic DCI record. Another standard's API would ask for its own format from the same filtered records.

### Rules

Plausibility rules are written in **[JSON Logic](https://jsonlogic.com)**, evaluated on each new or corrected activity:

```json
{"id": "sown_area_within_plan", "applies_to": ["SOWN"],
 "when":  {"and": [{"var": "payload.area_ha"}, {"var": "latest.PLANNED.area_ha"}]},
 "check": {"<=": [{"var": "payload.area_ha"}, {"*": [{"var": "latest.PLANNED.area_ha"}, 1.5]}]},
 "message": "Area sown {{ payload.area_ha | float }} ha is more than 1.5 × the planned {{ latest.PLANNED.area_ha | float }} ha",
 "severity": "warn"}
```

* A rule sees `payload` (after derived values), `activity_type`, and `latest.<TYPE>`: the context's latest active activity of each type (its payload and columns).
* `applies_to` lists activity types (all when empty); `when` (optional) says whether the rule applies; `check` must hold.
* **A missing value means "not applicable":** a rule that reads a value that isn't there (a `var` without a default) is skipped. `{"var": ["payload.sold_qt", 0]}` gives a default instead.
* `severity`: `warn` adds the message to the activity's rule warnings; `block` rejects the activity (error `ACT-ERR-022`). Crop Sown's four rules are warnings, as before.
* `message` is a Jinja string over the same data, so it can quote the values.
* Rules are checked when the file is loaded: unknown operators, malformed `var`s and bad message templates are reported.

**Why JSON Logic.** Rules are data: JSON, like the rest of the file, checked on load, with no `eval` and nothing outside a fixed set of operators. The platform evaluates them with a small built-in evaluator (`helpers/json_logic.py`), so there is no new dependency. CEL reads better, but `cel-python` brings five dependencies, including `google-re2`, which has no wheels for the Alpine images the services run on; the Python JSON Logic libraries are unmaintained (last releases 2015–2021, one ships broken). JSON Logic also has evaluators in JavaScript, so the staff UI could show the same warnings before submitting.

### Roadmap

This is step 1 of moving activity-register logic from code to configuration. **TODO (design):** the later steps (a projection spec, an aggregate spec, and tables generated from metadata) wait for a second real activity register, so that the specs are shaped by two domains rather than by crop sown alone. See [open items](../open-items/README.md#registries).

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
| Code lists | The registry's local `G2PAttribute` tables | Read live from the catalogues (MDS) | **Ours.** The local tables no longer exist in the platform. |
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
* **The same data for partners:** aggregates are readable through DCI, filtered to the consented data scopes, not only in the staff UI.

**Still missing compared with Observations** (reviewed October 2026; tracked in [open items](../open-items/README.md#registries))

| # | In Observations | What we have | Why it matters |
| --- | --- | --- | --- |
| 1 | **Activity-type definitions managed through an API**: create and update a type, its schema and version | Read-only: types come only from seed SQL, generated by a developer script | Changing a form or schema needs a release and a reinstall. Ties to code-free activity registers |
| 2 | **Per-type processing switches and per-stage status**: enrichment and computation flagged per type; enrichment finishes before computation, each with its own status, attempts and error | One outbox status per event; the enrich and aggregate hooks run for every event | With real enrichment (weather, satellite), only a failed stage should be retried, and types needing neither shouldn't be queued |
| 3 | **A shared calendar-period helper**: month, quarter and year periods computed by the platform; only business periods (a season) are domain-specific | Each register's domain service defines its own periods | Summaries by month or year come free for every register, not only by season |
| 4 | **Breakdowns by the farmer's attributes in area totals** (farmers by gender, cluster vs non-cluster), as in the Observations region rollup | Area, harvest and yield by region, zone and woreda; but the Crop Sown Registry holds no gender (it is in the Farmer Registry, and registries are deliberately separate) | Ministry tables split by gender. Needs a design decision: a consented copy of selected farmer attributes on activities, or an analytics layer that joins the registries |
| 5 | **GPS on every record**: latitude and longitude as standard fields, filled from the device | Only where a register adds them to its payload (CSR, from ODK's geopoint) | Location evidence for every register without each one defining it |
| 6 | **Location resolved from the subject's registered location** when aggregates are computed | Named levels recorded when the activity is written (deliberate: CSR can't walk the Farmer Registry's land records) | Only a gap when boundaries change: aggregates need recomputing from the catalogues' current boundaries |
| 7 | **Agent field app**: offline drafts, a sync badge, search over the agent's downloaded data, device GPS auto-fill | Staff UI, and ODK Collect, which already gives offline capture | Needed only if field agents don't use ODK (agent-portal entry is an activity register gap) |

The beneficiary API (Observations exposes the same APIs to partners, staff and beneficiaries) is in [register model phase 2](../open-items/README.md#registries).

**Not taken:** the single generic table for every type (see storage above), and the payload in a separate table (one table per register with promoted columns serves the same purpose).
