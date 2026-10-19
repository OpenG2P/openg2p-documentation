---
description: >-
  Design of activity registers in the registry platform: tables, the write
  path, background processing, partner APIs, sharing and configuration.
---

# Activity Register Design

This page describes how activity registers are built in the registry platform. What an activity register is, and when to use one, is in [Activity Register](../features/activity-register.md).

## Overview

An activity register is a `g2p_register_definitions` row with `register_purpose = ACTIVITY`. A registry extension provides its tables and domain logic. The platform provides the shared tables, the write path, the background worker, the staff and partner APIs, and the staff portal pages.

| Part | Provided by |
| --- | --- |
| Activity table `G2PActivity<Mnemonic>` | Extension (subclass of `G2PActivity`, with typed columns promoted from the payload) |
| Current-state table `G2PActivityProjection<Mnemonic>` | Extension (subclass of `G2PActivityProjection`). Optional. |
| Domain service `G2PActivityDomainService<Mnemonic>` | Extension (subclass of `G2PActivityDomainService`). Optional: every hook has a default. |
| Configuration file `meta_data/activity-config/<Mnemonic>.json` | Extension. Optional. |
| Register definition, activity types, indicators, ODK form mappings | Extension seed (db-seed) |
| Shared tables, write path, outbox worker, APIs, staff portal pages | Platform |

The extension classes are found by name in `openg2p_registry_extensions.register_domain.models` and `.services`.

An activity register cannot be created from the register configuration screen: it would have no tables (`ACT-ERR-021`). Its mnemonic names its classes, so it cannot be renamed, and a register cannot be switched to or from `ACTIVITY`. The register configuration counts its activities and contexts when it decides whether a register holds data, so an activity register in use cannot be deleted.

## Tables

### Per register

**Activity table** (`G2PActivity` base). Range-partitioned by `occurred_at`, one partition per year. The primary key is (`activity_id`, `occurred_at`).

| Column group | Columns |
| --- | --- |
| Identity | `activity_id`, `activity_type`, `context_id` |
| Subject | `subject_type`, `subject_id`, `subject_internal_record_id`, `subject_register_mnemonic`, `subject_ancestor_record_ids` |
| Provenance | `occurred_at`, `recorded_at`, `recorded_by`, `channel`, `source_record_id`, `source_partner_id`, `idempotency_key`, `submission_id`, `schema_version` |
| Corrections | `supersedes_activity_id`, `superseded_by_activity_id`, `status` (`ACTIVE`, `SUPERSEDED`, `VOIDED`), `status_reason`, `status_changed_by`, `status_changed_at` |
| Verification | `verification_status` (`NOT_REQUIRED`, `SUBMITTED`, `VERIFIED`, `REJECTED`), `verified_by`, `verified_at`, `verification_remarks` |
| Data | `payload` (JSONB), promoted typed columns, `search_text` |
| Checks and location | `geo_dimensions`, `reference_checks`, `rule_warnings`, `catalogue_versions` |

`channel` is one of `STAFF_PORTAL`, `AGENT_PORTAL`, `PARTNER`, `ODK`, `IMPORT_FILE`, `SYSTEM`. Writes today come from the staff portal, the partner API, ODK Central and sample loading.

A payload field with the same name as a promoted column is also written to that column, typed. Promoted columns are what searches, data policies, indicators and data scopes can name.

**Current-state table** (`G2PActivityProjection` base). One row per context. The platform fills `context_id`, `context_key`, `subject_type`, `subject_id`, `context_status`, `activity_count`, `last_activity_id`, `last_activity_type`, `last_occurred_at`, `last_recorded_at`, `projected_at`, `geo_code_hierarchy_json`, `geo_dimensions`, `replaces_context_id` and `replaced_by_context_id`. The extension adds its own columns, filled by its `project` hook. The row is recomputed from the context's current activities (`ACTIVE` and not rejected); a context with none has no row.

### Shared by all activity registers

| Table | Holds |
| --- | --- |
| `g2p_activity_types` | One row per activity type: payload schema, `schema_version`, form layout, rules, reference rules, participant roles |
| `g2p_activity_type_schemas` | Every payload schema a type has had, by version (written by a trigger) |
| `g2p_activity_contexts` | Contexts: key, type, subject, attributes, `OPEN`/`CLOSED`, replacement links |
| `g2p_activity_period_locks` | Closed date ranges, per register and optionally per type, with reopening |
| `g2p_activity_idempotency_keys` | One row per (register, idempotency key). The partitioned table cannot enforce this itself. |
| `g2p_activity_participants` | Who took part, by role: a local record or an external ID |
| `g2p_activity_outbox` | Events for the background worker |
| `g2p_activity_enrichments` | Derived or external data per activity, kept beside it |
| `g2p_activity_aggregates` | The current value per register × subject × aggregate type × period |
| `g2p_activity_aggregate_history` | Every value an aggregate has had |
| `g2p_activity_indicators` | Indicator definitions over the current-state table |
| `g2p_activity_temporary_references` | IDs created offline and what they resolved to |
| `g2p_activity_odk_forms`, `g2p_activity_odk_failures` | ODK Central form mappings and submissions that failed |

### Database guards

`G2PActivityPartitionService` runs on every migration and from a daily task. It is idempotent.

* Creates yearly partitions from `activity_partition_years_back` years ago to next year, plus a default partition.
* Adds a trigger that rejects `DELETE`, and any `UPDATE` that touches columns other than the status, supersession and verification columns.
* Adds columns that a newer model has and an existing table lacks.
* Adds triggers on `g2p_activity_types` that increment `schema_version` when `payload_schema` changes and keep the old version.

## Write path

`G2PActivityService` appends one activity in one transaction:

1. **Duplicate check.** A known idempotency key returns the existing activity (outcome `DUPLICATE`).
2. **Payload.** Participants given by role fill their payload fields. Ethiopian-calendar date fields are converted. The domain service adds derived values (`enrich_payload`). The payload is checked against the type's JSON Schema (`ACT-ERR-004`).
3. **References.** Each reference rule is checked (see below). A `LOCAL_RECORD` rule with `"subject": true` sets the subject and its ancestor records.
4. **Context.** Taken from `context_id` (unknown: `ACT-ERR-007`), else `context_key`, else the domain service's `build_context`. It is found or created, then locked with `SELECT … FOR UPDATE`, so writes to one context run one at a time. A closed context rejects the write (`ACT-ERR-008`). A type that requires a context and has none is rejected (`ACT-ERR-006`).
5. **Rules.** Date limits (`ACT-ERR-012`, `ACT-ERR-013`), period locks (`ACT-ERR-014`), repeatability (`ACT-ERR-010`), uniqueness (`ACT-ERR-011`), prior types (warning, or `ACT-ERR-009` when the type blocks), then the domain service's `validate`, which by default runs the configured plausibility rules.
6. **Location.** `geo_dimensions` is taken from the payload's location field, else the subject record (or its nearest ancestor), else the context's latest located activity.
7. **Save.** The activity, its idempotency key and its participants are inserted. The context's current state is recomputed. An outbox row is written.

Warnings are stored on the activity (`rule_warnings`, `reference_checks`). Errors reject it.

### Reference rules

`reference_rules` on an activity type maps payload fields to rules:

| Kind | Checks against | Options |
| --- | --- | --- |
| `ATTRIBUTE` | A Master Data list (`attribute`) | |
| `GEO` | Master Data geography | `level`; `"location": true` marks the activity's location |
| `LOCAL_RECORD` | A record of a register in this registry (`register`, `match`) | `"subject": true`; `"belongs_to": "<field>"` |
| `EXTERNAL` | An ID held by another system (`system`) | `pattern`; `"lookup": false` for a format check only |

Each rule has a `mode`: `STRICT` (the default) rejects an unresolved value (`ACT-ERR-005`), `LENIENT` accepts it with a warning, `NONE` skips the check. A `belongs_to` mismatch is rejected or warned the same way. An `EXTERNAL` lookup goes through the domain service's `resolve_external_reference`; a system that cannot be reached counts as unresolved. A field name with a dot (`<list>.<field>`) checks that field in each row of a list.

Any rule can set `temporary_prefix`. A value that starts with it is an ID created offline. It is recorded in `g2p_activity_temporary_references` and, while unresolved, accepted with a warning. Once staff resolve it, later activities get the resolved ID, checked like any other value. Earlier activities keep the value they were written with.

### Corrections and verification

| Action | Effect |
| --- | --- |
| Supersede | Appends a new activity through the same write path, then marks the old one `SUPERSEDED` and links both. The fields in `context_fields` cannot change (`ACT-ERR-015`): void and record again to move an activity to another context. |
| Void | Marks the activity `VOIDED`. |
| Verify / reject | Sets `verification_status` on an `ACTIVE`, `SUBMITTED` activity. Reject needs remarks (`ACT-ERR-016`). Rejected activities drop out of the current state. |

Supersede and void need a reason (`ACT-ERR-016`), work only on `ACTIVE` activities (`ACT-ERR-015`), and are refused inside a closed period (`ACT-ERR-014`). Each action recomputes the current state and writes an outbox event.

### Contexts

A context is opened by the first activity that names or derives its key, or explicitly through the staff API. It can be closed (with a reason) and reopened; both recompute its current state. `build_context` can return `replaces_context_id`: the new context then points to the old one, which is closed. This covers, for example, a change of crop within a season.

## Background processing

Celery beat schedules these worker tasks:

| Task | What it does | Beat setting (seconds) |
| --- | --- | --- |
| `activity_outbox_worker` | Processes outbox events | `activity_outbox_frequency` (default: `default_beat_producer_frequency`, 20) |
| `activity_reconcile_worker` | Recomputes current-state rows that disagree with their activities | `activity_reconcile_frequency` (1 day) |
| `activity_partition_worker` | Creates next year's partitions | `activity_partition_frequency` (1 day) |
| `activity_odk_pull_worker` | Pulls new ODK Central submissions | `activity_odk_pull_frequency` (300) |
| `activity_sample_data_worker` | Loads sample activities once, on demo installs (see below) | `activity_sample_data_frequency` (120) |

### Outbox

The outbox row is committed with the activity, so no event is lost. Events are `APPENDED`, `SUPERSEDED`, `VOIDED`, `VERIFIED` and `REJECTED`. The worker claims a batch of rows (`activity_outbox_batch_size`) with `SKIP LOCKED`, so several workers can run. The batch is one transaction, and each event runs in its own savepoint:

1. **Publish.** If the register has outgestion on, the activity is queued for each active outgoing topic.
2. **Enrich.** For `APPENDED` events, the domain service's `enrich` result is stored in `g2p_activity_enrichments`.
3. **Aggregate.** The domain service's `aggregate` returns every aggregate the event may have changed, recomputed from current data. Each replaces the stored value and is appended to the history.
4. **Hook.** The domain service's `on_activity_event`, if defined.

A failed event is marked `FAILED` and tried again by later runs, up to `activity_outbox_max_attempts` attempts in all. Every step must be idempotent. The worker logs a warning when an event has waited more than five minutes or any event has failed.

### Final aggregates

An aggregate becomes final when all of these hold:

* its type is listed in `final_on_period_lock`;
* it has a `period_start` and a `period_end`;
* an active period lock for all activity types covers its whole period;
* its value was last changed by an event raised no later than that lock;
* no outbox event for an activity in that period is still pending or failed.

This is checked when a lock for all activity types is taken, and after each outbox batch that processed an event. A lock for one activity type never finalises. Reopening the lock makes the aggregate provisional again, unless another active lock still covers it.

If a final aggregate is recomputed to a different value (an activity outside the locked window still feeds it), it becomes provisional, and stays so until the period is reopened and locked again. A figure is then never final and wrong, and a change after a payment is visible. A register whose aggregates draw on activities outside their period (for example a plan made before the season) should lock the wider window.

### ODK Central pull

When `activity_odk_enabled` is on, the pull reads each active `g2p_activity_odk_forms` row:

* It asks ODK Central's OData API for submissions newer than the row's cursor (`last_submission_date`), a page at a time.
* `mapping` turns each submission into an activity: fixed values, paths (`group/field`) and transforms (`number`, `integer`, `date`, `boolean`, `split`, `upper`, `geopoint_lat`, `geopoint_lon`, `geopoint_alt`, `attachment`). An attachment is stored as a document and its ID put in the payload. Without a mapped date, the submission date is used.
* The activity goes through the normal write path with channel `ODK`. The ODK instance ID is the `source_record_id`, and `odk:<form>:<instance>` the idempotency key, so a page read twice adds nothing. One pull run is one submission.
* Submissions rejected in ODK review are skipped. A submission that fails is stored in `g2p_activity_odk_failures` and does not hold back the cursor.

### Sample data

With `activity_load_sample_data` on, each register's `sample_activities` are appended through the normal write path, with channel `SYSTEM`, verified or corrected where a step says so. Date limits are not checked for them. Every sample carries an idempotency key, so loading is exactly-once. A Helm hook Job (`<release>-activity-samples`, after db-seed) loads them on install and upgrade and fails the release if a register's samples cannot be loaded. The beat task stays as a backstop; an advisory lock per register keeps the two apart.

## Indicators

An indicator is a row in `g2p_activity_indicators` with a definition over the current-state table:

```json
{"measure": {"fn": "sum", "field": "area_sown_ha"},
 "group_by": ["season", "geo:district"],
 "filters": {"stage": ["SOWN", "HARVESTED"]}}
```

`fn` is `count`, `count_distinct`, `sum`, `avg`, `min` or `max`. `geo:<level>` groups or filters by a named geography level. Column names are checked against the model, so a definition cannot inject SQL. Indicators are computed when asked, through the staff API only.

Indicators are for day-to-day work: a few figures staff act on, within their own area (their data policy applies), read cheaply from one current-state table. Trends over seasons, comparisons between regions and management reports belong in reporting views and dashboards (for example Superset), not in indicators.

## Staff API

All endpoints are `POST /activity/<action>` on the staff API.

| Permission | Actions |
| --- | --- |
| `activity:view` | `get_activity_registers`, `get_activity_types`, `get_activity`, `search_activities`, `get_timeline`, `search_contexts`, `get_work_list`, `get_projection`, `search_projections`, `get_indicators`, `compute_indicator`, `get_period_locks`, `get_temporary_references`, `get_subject_activities`, `get_latest_activity`, `search_aggregates`, `get_aggregate_history`, `get_activity_type_schemas` |
| `activity:create` | `append_activity`, `append_activities`, `open_context` |
| `activity:correct` | `supersede_activity`, `void_activity`, `close_context`, `reopen_context` |
| `activity:verify` | `verify_activity`, `reject_activity` |
| `activity:configure` | `lock_period`, `unlock_period`, `resolve_temporary_reference`, `rebuild_projections` |

Reads of activities, current state, the work list, indicators, a record's activities and the latest activity apply the user's data policies. A policy on a column the table does not have denies everything (fails closed). Contexts, aggregates and aggregate history are not filtered by data policy. `get_subject_activities` lists, per activity register, the activities about a record of this registry and, optionally, its child records, with their aggregates. The staff portal's Activities tab uses it.

## Partner API

Both endpoints take a DCI-style envelope, `{signature, header, message}`. The detached JWS is verified against the sender's key in Partner Management, like partner search. See [Partner APIs](partner-apis.md).

### `POST /partner/activity/append_activities`

```json
{"signature": "...",
 "header": {"sender_id": "coop-01", "message_id": "m-123", "message_ts": "2026-10-01T08:00:00Z"},
 "message": {"atomic": false,
             "activities": [{"register_mnemonic": "<Register>", "activity_type": "HARVESTED",
                             "occurred_at": "2026-09-30T00:00:00Z", "subject_id": "P-0007",
                             "payload": {"plot_id": "L-17", "quantity_kg": 820},
                             "idempotency_key": "coop-01:h-5521"}]}}
```

* An activity takes `occurred_at`, or `occurred_on_ec` (an Ethiopian-calendar date). It may name `context_id` or `context_key`, `participants`, `source_record_id` and `submission_id`.
* `atomic: false`: each activity succeeds or fails on its own. `atomic: true`: all or nothing; one failure fails the whole message (status `ERROR`, with that error).
* The message is one submission: `submission_id` is `<sender_id>:<message_id>`, unless an activity names its own. The channel is `PARTNER` and the partner is recorded on each activity.
* Each result has `index` and `outcome` (`CREATED`, `DUPLICATE` or `FAILED`), with the activity or the error.
* The response `status` is `SUCCESS`, `PARTIAL`, `FAILED` or `ERROR` (for example a bad signature), in an HTTP 200 response.

### `POST /partner/activity/correct_activities`

Each correction has `register_mnemonic`, `activity_id`, `action` (`SUPERSEDE` or `VOID`) and `reason`. A supersede may add `payload` (merged over the original payload), `occurred_at` or `occurred_on_ec`, and `idempotency_key`. A partner can correct only activities it submitted; any other is reported as not found (`ACT-ERR-003`). Corrections are applied one by one. Each result has `index` and `outcome` `SUPERSEDED`, `VOIDED` or `FAILED`. The response `status` is as for `append_activities`.

The record ingestion pipeline (`/partner/ingest_data`) refuses activity registers: its worker fails such a record instead of matching it.

## Sharing through partner search

A DCI search with `reg_type` set to an activity register's mnemonic returns one of three record kinds, chosen by `reg_record_type`:

| `reg_record_type` | Returns | Shaped by |
| --- | --- | --- |
| Ends in `Aggregate` | Aggregates, filtered by `aggregate_type`, `period_key`, `period_start`, `period_end`, `is_final` or any custom dimension | the `aggregate` template in the configuration, else a generic record |
| Local name matches a context type the register has (`…:CropSeason` → `CROP_SEASON`) | Current state of one subject's contexts of that type, filterable on plain projection columns | the `state` template, else a generic record |
| Anything else | Current activities: `ACTIVE` and not rejected | the register's outgoing DCI template, like register records |

Aggregate and current-state searches name the subject (`subject_id` in an expression query, or an idtype-value query). An expression query can add filters, with the operators of [DCI search](partner-register-search/dci-search.md#expression) and ISO dates and date-times:

* activities: any plain column (type, dates, verification, promoted payload fields);
* current state: any plain projection column;
* aggregates: `aggregate_type`, period, `is_final` and custom dimensions.

Results come newest first (activities by `occurred_at`, current state by last activity, aggregates by period start; a DCI `sort` overrides it for activities), so "the last 10 activities" is a subject search with `page_size: 10`. All search of activity registers is synchronous.

Under consent enforcement:

* The searched subject must be the consent's subject, or be linked to it by the register's own data: an activity with that `subject_id` whose `subject_id_fields` hold the consent's subject.
* Each record is filtered to the consented scopes before it is shaped. Activities use `<Register>.activity.<field>`, current state uses `<Register>.context.<field>`, aggregates use `<Register>.aggregate.<field>`. The fields are table columns, so a payload field is reachable by name only if it is a promoted column; otherwise only the whole `payload` column can be granted. See [Data Scopes](data-scopes.md).

### Bulk aggregate searches

An aggregate search whose expression query has no `subject_id` (and no `search_text`) covers all subjects. It is allowed only for partners listed in `dci_bulk_aggregate_partners` (partner API setting, env `REGISTRY_PARTNER_API_DCI_BULK_AGGREGATE_PARTNERS`, JSON):

```json
{"benefits-system": ["<controller>.<scope>", "<scope>"]}
```

* The key is the partner's `sender_id`. The value lists the data scopes it may receive. A bare name means this registry's scope.
* These scopes replace a consent's, at their current versions. The signature is still checked.
* The query must name `aggregate_type`.
* The page size is capped at `dci_bulk_aggregate_max_page_size` (default 500).

Any other search without a consented subject is refused.

## Configuration

### Configuration file

`<extension package>/meta_data/activity-config/<Mnemonic>.json` (setting `activity_config_path` overrides the directory). It is validated when the register is first used, and every problem is reported at once (`ACT-ERR-023`).

| Key | Declares |
| --- | --- |
| `description`, `register_mnemonic` | Optional. `register_mnemonic` must match the file name. |
| `context_fields` | Payload fields that place an activity in its context. A correction cannot change them. |
| `subject` | `subject_type`, and `subject_id_fields`: activity fields that hold another ID of the subject, used for the consent subject check |
| `ui_hints` | Staff portal hints: `summary_fields` (shown on an activity's row), `context_columns` (current-state columns listed), `batch_carry_fields` (copied to the next batch row), `search_placeholder`, `context_search_placeholder` |
| `final_on_period_lock` | Aggregate types that become final when their period is locked |
| `search_fields` | Payload fields added to an activity's search text |
| `formats` | Output record templates per format and record kind (`state`, `aggregate`): a `template` path relative to the configuration directory, and an optional `record_type` |
| `rules` | Plausibility rules in JSON Logic |

A domain service that sets the attribute or overrides the hook wins over the file. The file wins over the platform default.

**Output templates** are Jinja templates that render JSON. A template sees `record` (already filtered to the consented scopes), `record_type`, `output_format`, `kind` and `register_mnemonic`. Two filters are added: `pick("a", "b")` and `or_null` (a group whose values are all null becomes null). DCI search uses format `dci`.

**Rules** are evaluated on each new or corrected activity:

```json
{"id": "quantity_within_plan", "applies_to": ["HARVESTED"],
 "when":  {"var": "latest.PLANNED.expected_kg"},
 "check": {"<=": [{"var": "payload.quantity_kg"}, {"*": [{"var": "latest.PLANNED.expected_kg"}, 2]}]},
 "message": "Harvest {{ payload.quantity_kg }} kg is more than twice the plan",
 "severity": "warn"}
```

* A rule sees `activity_type`, `payload` and `latest.<TYPE>`: the context's latest current activity of each type.
* A rule that reads a missing value (a `var` without a default) does not apply.
* `warn` adds the message to the activity's warnings. `block` rejects it (`ACT-ERR-022`).

Rules are JSON so they are data like the rest of the file: checked on load, with no `eval` and only a fixed set of operators. The platform evaluates them with a small built-in evaluator, with no new dependency. JSON Logic also has JavaScript evaluators, so the staff portal could show the same warnings before submitting.

### Domain service hooks

| Hook | Purpose | Default |
| --- | --- | --- |
| `build_context` | Derive the context key, type, subject and attributes | none |
| `enrich_payload` | Add derived values before validation | unchanged |
| `validate` | Plausibility checks | configured rules |
| `search_text_values` | Payload values added to the search text | configured `search_fields` |
| `project` | Columns of the current-state row for one context | none |
| `resolve_external_reference`, `reference_display` | Look up and label external IDs | none |
| `enrich` | Derived or external data per activity | none |
| `aggregate` | Aggregates affected by an event | none |
| `render_record` | Shape a record in an output format | configured template, else none |
| `dci_state_record`, `dci_aggregate_record` | Shape shared records | configured template, else generic |
| `on_activity_event` | Runs last for each outbox event | not defined |
| `sample_activities` | Sample data for demo installs | none |

### Settings

| Setting | Where it matters | Default | Purpose |
| --- | --- | --- | --- |
| `activity_partition_years_back` | migration, worker | 5 | First year with its own partition |
| `activity_outbox_batch_size` | worker | 200 | Outbox rows per batch |
| `activity_outbox_max_attempts` | worker | 5 | Retries for a failed event |
| `activity_reference_cache_seconds` | APIs | 600 | Cache for display names |
| `activity_config_path` | all | (extension) | Configuration file directory |
| `activity_odk_enabled`, `activity_odk_base_url`, `activity_odk_username`, `activity_odk_password` | worker | off | ODK Central pull |
| `activity_odk_page_size`, `activity_odk_timeout_seconds` | worker | 250, 60 | ODK Central page size and request timeout |
| `activity_load_sample_data` | worker | off | Load sample activities |
| `activity_samples_wait_seconds` | sample Job | 600 | How long the Job waits for the seed's activity types |
| `dci_bulk_aggregate_partners` | partner API | `{}` | Partners allowed bulk aggregate searches, and their scopes |
| `dci_bulk_aggregate_max_page_size` | partner API | 500 | Page cap for bulk aggregate searches |

The `activity_*` settings are platform (core) settings that every service inherits. Each service reads them with its own environment prefix, for example `REGISTRY_CELERY_WORKERS_ACTIVITY_OUTBOX_BATCH_SIZE` for the worker. Beat frequencies use the prefix `REGISTRY_CELERY_BEAT_`.

An activity register that only some installs need can ship as an optional seed and be switched on with the Helm value `dbSeed.optionalSeeds`.

## Not built

* An API to create or change activity types, indicators or ODK form mappings. They come only from the seed.
* Reviewing or retrying failed ODK submissions. They are kept in `g2p_activity_odk_failures`, but no API, screen or task reads them.
* Activity entry from file import or the agent portal. The `IMPORT_FILE` and `AGENT_PORTAL` channels exist but nothing writes them.
* A bulk export API, and retention or archiving of old partitions.
* Per-type switches and per-stage status for enrichment and aggregation. One outbox status covers all steps.
* Configuring the staff UI per register (tabs, list columns, context and summary pages, form widgets): see [Activity Register UI Configuration (Proposal)](activity-register-ui-configuration.md).

## Relation to the Observations design

The [Observations design](observations-design.md) describes the same idea under another name: append-only records, a JSON Schema per type, corrections as new records, and roll-ups per subject and period. The platform builds it as activity registers, with one table per register (not one generic table), contexts derived from the payload (not explicit links), a projection per context, and aggregates computed in the background. Geography is a snapshot of named levels taken when an activity is written, not resolved from the subject's record when aggregates are computed, so it works when the subject is in another registry.

Taken from the Observations design: the Activities tab on a record's profile, `schema_version` on types and activities, `submission_id`, enrichment and aggregates as an asynchronous layer, form defaults from the latest activity, geography as named levels, and aggregates readable by partners.

**Still missing compared with Observations** (not built):

| In Observations | Today |
| --- | --- |
| Activity types managed through an API | Types come only from the seed |
| Per-type processing switches and a status per stage (enrichment, then computation) | One outbox status per event; the hooks run for every event |
| Calendar periods (month, quarter, year) computed by the platform | Each domain service defines its own periods |
| Area totals broken down by the subject's attributes (e.g. by gender) | Only attributes the activity register holds itself |
| GPS on every record as standard fields | Only where a register adds them to its payload |
| An agent field app with offline drafts | The staff portal, and ODK Collect for offline capture |
| A beneficiary API | Staff and partner APIs only |
