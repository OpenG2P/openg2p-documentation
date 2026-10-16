---
description: >-
  Activity registers record what happened (a visit, a sowing, an attendance) as
  append-only activities, and derive current state and summaries from them.
  Any registry can have one.
---

# Activity Register

A registry can hold two kinds of register:

* A **register** holds the current truth about a subject: a person, a household, a plot. A record is edited over time through approved change requests, and its versions are kept.
* An **activity register** holds what happened to or about a subject: a visit, a sowing, a harvest, an attendance. Each activity is a new row. It is appended once and never edited. Current state and summaries are derived from the activities.

Activity registers are a platform feature. Any registry can define one, alone or next to its registers. The [Crop Sown Registry](../../crop-sown-registry/README.md) is one example.

The technical design is in [Activity register design](../design/activity-register.md).

## Register and activity register compared

| | Register | Activity register |
| --- | --- | --- |
| **A row is** | A subject (one person, one plot) | An event (one visit, one sowing) |
| **What grows** | The number of subjects | The number of events, every period |
| **Lifecycle of a row** | Created, then edited | Appended once. Corrected by a new activity that supersedes it, or voided. Only status and verification change. |
| **How data gets in** | Change requests, approved through the workflow | Appended directly (staff portal, partner API, ODK Central). No change request. |
| **History** | A history table with a version per approved change | The activities are the history. Superseded and voided activities stay. |
| **Identity** | Internal ID, functional ID, deduplication | Activity ID and an optional idempotency key. No functional ID, no deduplication. |
| **Grouping** | Parent and child registers | Contexts: a key derived from the activity (for example, one plot in one season) |
| **Current state** | The record itself | A projection: one row per context, recomputed from its activities |
| **Deleting** | Records can be deactivated | Nothing is deleted. The database rejects deletes and edits. |

An activity register does not use change requests, approval workflows, history tables, intake forms, functional IDs, deduplication, completion scores or registrant authentication.

## When to use which

* Use a **register** for things you identify, deduplicate and maintain: people, households, plots, organisations.
* Use an **activity register** for things that happen repeatedly to those things, where you need the history and the totals: visits, sowings, harvests, attendance, inspections.

Both can live in one registry. Activities can then point to the registry's own records and appear on those records' profiles. Or the activity register can be a registry of its own and refer to another registry's records by ID. Registries share data, not code.

## Activities

An activity has a type, such as `VISITED` or `HARVESTED`. Each activity type is configured with:

| Setting | What it does |
| --- | --- |
| Payload schema | A JSON Schema the activity's data must satisfy. The staff portal builds its form from it. |
| Schema version | Increases whenever the schema changes. Each activity keeps the version it was checked against. |
| Reference rules | Checks on fields that point elsewhere: a Master Data list value, a geography unit, a record in this registry, or an ID held by another system. Each rule is strict (reject), lenient (warn) or off. |
| Repeatable | Whether the type may occur more than once in a context. |
| Uniqueness fields | Payload fields that must be unique among current activities of the type in a context. |
| Prior types | Types that must come first in the context. A breach warns or rejects, as configured. |
| Due rule | When the type falls due after another (for example 90 to 150 days after sowing). Feeds the staff work list. |
| Dates | How far back an activity may be dated, and whether future dates are allowed. |
| Verification | Whether a supervisor must verify or reject the activity. |
| Participant roles | Who took part, by role (for example the person, the plot, the inspector), each read from a payload field. |

Every activity also records when it happened (`occurred_at`), when and by whom it was recorded, the channel it came through, the partner (if any), the batch it came in (`submission_id`), its subject, and where it happened.

An activity is never edited. To fix one:

* **Supersede** it: a new activity replaces it. The old one stays, marked superseded.
* **Void** it: it did not happen. It stays, marked voided.

Both need a reason. Neither is allowed inside a closed period. **Verification** is separate: it records whether the activity is true and never changes its data.

## Contexts and current state

Activities are grouped into **contexts**. A context is a key built from the activity, such as "this plot, this season, this crop" or "this training session". The extension decides how the key is built. A caller can also name the context.

A context is open or closed. No activity can be added to a closed context.

Each context has a **current state** (a projection): one row with the figures that matter, such as the current stage, the area sown or the number of sessions attended. It is recomputed from the context's current activities in the same transaction as each write, so it is never out of step.

## Aggregates

An **aggregate** is a value per subject per period, such as a person's season summary across all their plots, or a worker's monthly attendance.

* Aggregates are computed in the background after each activity event, from current data: a worker picks up the event within seconds (every 20 seconds by default). A context's current state, by contrast, is updated in the same transaction as the activity.
* Each new value replaces the last one, and every value is kept in a history.
* An aggregate type can be marked to become **final** when its period is closed. Then it is the figure a payment or official statistic can rely on. It becomes provisional again if the period is reopened, or if a later change still alters it.

**Indicators** are a third kind of figure: a statistic across many subjects (for example area sown by district), computed when asked from the current state. They are configured as data, shown to staff, and not shared with partners.

## Linking to a subject

Each activity is about a **subject**. The subject can be:

* **A record in the same registry.** A reference rule marked as the subject makes that record the activity's subject. Its parent records are noted too, so a plot's activities also appear on its owner's profile. A second rule can require one record to belong to another (the plot must be that person's).
* **An identifier held elsewhere.** For example another registry's ID or a national ID. It can be checked by format only, or looked up.

**Entities first.** An activity never creates or changes a record in an entity register. The record is registered, or changed through its own change request, first; the activity then records what happened (a birth, a sale) against it.

Records in the same registry show an **Activities** tab. It lists the activities about the record and its children, and those it took part in, with their aggregates. From there staff can record a new activity about the record.

Where an activity happened is stored on it as named geography levels (for example region, district). It comes from the activity's own location field, else from the subject's record, else from its context. It is a snapshot, so history stays stable when a record is later edited.

## Staff portal

Activity registers are listed with the other registers. The home page's Registers card counts them, and its register list offers each as "(Activity)". Each register has its own page under **Activity registers**:

| Tab | Shows | Permission |
| --- | --- | --- |
| **Activities** | Activities with filters; a detail panel with participants, warnings, enrichment and the verify, reject, correct and void actions | `activity:view` |
| **Current state** | One row per context (named **Contexts** when the register has no current-state table) | `activity:view` |
| **Work list** | Activities due or overdue, from each type's due rule | `activity:view` |
| **Summaries** | Aggregates and their history | `activity:view` |
| **Indicators** | The register's indicators | `activity:view` |
| **Record** | Single or batch entry. The form is built from the type's JSON Schema, with lists as dropdowns, a geography picker and an Ethiopian-calendar date picker. It is prefilled from the latest activity of the type. Batch entry carries chosen fields from row to row | `activity:create` |
| **Settings** | Closed periods (lock and reopen), temporary IDs awaiting resolution, rebuilding the current state | `activity:configure` |

A context has its own page: its current state, a timeline of its activities, and the context it replaced or was replaced by. From there staff can record the next activity (`activity:create`) and close or reopen the context (`activity:correct`). Records in the same registry show an **Activities** tab (see [Linking to a subject](#linking-to-a-subject)).

## Partner activity submission

Partner systems append activities, and correct the ones they submitted (supersede or void, with a reason), through two signed Partner API endpoints. Activity registers do not take data through record ingestion. Envelopes and outcomes: [design, Partner API](../design/activity-register.md#partner-api).

## Sharing with partners

A partner reads an activity register through partner search and can ask for **activities**, the **current state per context** (for example each crop season of one person) or **aggregates** (for example one person's season summary). Under consent enforcement the search names one subject, linked to the consented person, and every record is filtered to the consented [data scopes](../design/data-scopes.md) (`<Register>.activity|context|aggregate.<field>`). A partner the registry operator lists can also fetch one aggregate type for all subjects, such as a benefits system paying on monthly attendance, without per-person consent. Details: [design, sharing through partner search](../design/activity-register.md#sharing-through-partner-search); see also [Consent-Aware Data Sharing](consent-aware-data-sharing.md).

## Governance

| Topic | Activity register |
| --- | --- |
| Permissions | `activity:view`, `activity:create`, `activity:correct`, `activity:verify`, `activity:configure` |
| Data policies | Filter activities and current state on their columns, such as location. A policy on a column the table does not have denies access. |
| Closing a period | A period lock stops writes and corrections in a date range. It can be reopened, with a reason. |
| Verification | Optional per activity type: submitted, then verified or rejected. |

## Not built yet

Managing activity types through an API, activity entry from file import or the agent portal, reviewing failed ODK submissions, bulk export and archiving: see [design, not built](../design/activity-register.md#not-built).

One verification model and one correction model for both register kinds (verification records with evidence, trusted sources, disputes) are proposed in [Verification and Correction (Proposal)](../design/verification-and-correction.md).
