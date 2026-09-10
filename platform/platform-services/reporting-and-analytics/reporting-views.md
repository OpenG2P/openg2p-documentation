---
description: >-
  The views every report reads — generated from the registry's own schema,
  refined by a short declaration, with personal data withheld by default.
---

# Reporting views

Every dashboard, map panel and ad-hoc query reads a **reporting view**, never the
register directly. The views are named `<prefix>_rpt_<entity>` — `fr_rpt_farmer`,
`nsr_rpt_individual` — one per entity, one row per record.

They exist because a register and a report want opposite things. The register has
31 tables, no foreign keys, opaque link columns, geography packed into JSON, and
personal detail on nearly every row. A chart wants a wide, flat table it can
group by, with no names in it.

## Generated, declared, hand-written

The reporting layer splits into three, and knowing which part you are looking at
tells you where to change it.

| | What | Who writes it |
|---|---|---|
| **Generated** | one view per entity: columns selected, parent joined for geography, workflow carried, personal data withheld | the platform, at install |
| **Declared** | what cannot be inferred — what a column *means*, which views are materialized | the registry, in `reporting.yaml` |
| **Hand-written** | genuinely bespoke SQL | the registry, in `reporting_views.sql` |

The platform's generator runs during install, immediately after the registry's
own SQL. It reads the schema, works out which tables are entities, and emits a
view for each one. A registry that declares nothing still gets a complete,
PII-safe reporting layer.

{% hint style="warning" %}
**This replaced a hand-written file per registry, and the reason matters.** A
hand-written file covers the entities somebody thought of. The Farmer Registry's
covered farmer, land and crop, and rolled livestock up into a single boolean — so
"how many farmers keep livestock" had an answer and "how many cattle versus
goats" had none, over 132,824 livestock records. Nothing reported the gap,
because nothing was checking for one.

Generation makes coverage structural: every entity in the tree gets a view,
which can be verified, where "did we anticipate every report" cannot.
{% endhint %}

## Nothing depends on what has been registered

The views are a function of three things: the registry's **schema**, Master
Data's **country pack**, and the registry's **declaration**. Never of the data.

That sounds like a detail and is the single most important property here,
because **a production registry is installed empty** — the country loads its
register afterwards. Anything inferred from rows at install time is inferred from
nothing at all.

Two things are affected, and both are read from a source that knows the answer
before the first record exists:

* **How many geographic levels** the country has, and what they are called, comes
  from Master Data's `g2p_geo_levels`. A four-level pack produces `geo_1..geo_4`;
  a six-level pack produces six. Nothing is hard-coded, and no view carries a
  column for a level the country does not have.
* **Which entity hangs off which** is declared in `reporting.yaml`, not inferred
  from where the links happen to point.

## What a generated view carries

* **Its own columns**, minus anything classified as personal data.
* **Its parent's id**, and **geography inherited from the parent** — a livestock
  record has no geography of its own, it is wherever its parcel is. Deriving it
  twice would be a second chance to disagree with the parent.
* **Workflow**: `created_at`, `created_by`, `record_status`, `last_approved_at`,
  `last_approved_by`, `record_status_reason`. These make questions about the
  *registration process* answerable — approval latency, what is still pending —
  which no reporting view carried before.
* **An age** wherever a birth date was withheld. The identifier goes, the
  analytic value stays.

Two further views come free: `<prefix>_rpt_change_request` (approval throughput
and backlog, with `approval_hours` computed once so every chart agrees) and
`<prefix>_rpt_record_history` (every recorded change, across every entity, with
an `entity` column for a per-type breakdown).

## Personal data is withheld by default

The generator classifies every column and drops the ones that identify a person —
names, phone numbers, emails, birth dates, foundational ids, free-text search
blobs, address lines. The list is platform-level, so a new registry inherits it.

The classifier is type-aware: a boolean called `has_personal_phone` is a
statistic, not a phone number, and withholding it would protect nobody while
quietly removing a column reports are built from.

After the views are created, an independent pass **re-reads them and fails the
install** if a withheld column reached one. That is deliberate: an allow-list a
query planner respects is a convention, while a column that is not in the view
is a boundary.

The classifier errs towards withholding, so it will occasionally take something
it should not — `primary_cooperative_name` is an organisation, not a person. The
registry declares those explicitly. Guessing wrong in the cautious direction
loses a report; guessing wrong in the other direction leaks a person.

## The declaration

`reporting.yaml` ships in the registry's db-seed image. Every key is optional.

| Key | Declares |
|---|---|
| `prefix` | view name prefix, e.g. `fr_rpt_` |
| `tree` | which entity hangs off which — the authority, not a guess |
| `custom` | views written by hand; the generator leaves them alone |
| `pii.allow` / `pii.deny` | corrections to the classifier |
| `filter` | which rows belong in a view at all |
| `inherit` | parent attributes carried down onto the child row |
| `derived` | computed columns, in the country's own terms |
| `rollups` | figures summarised up from a child |
| `materialized` | which views hold a snapshot, and their indexes |

Worked examples, kept current with the code:
[Farmer Registry](https://github.com/OpenG2P/farmer-registry/blob/develop/docker/db-seed/reporting.yaml)
and
[National Social Registry](https://github.com/OpenG2P/national-social-registry/blob/develop/docker/db-seed/reporting.yaml).

Two notes worth carrying:

**`tree` can name more than one parent.** A single Farmer Registry install
carries scores hanging off both — the bulk generator attaches them to farmers and
the sample loader to households. Naming one parent silently stripped the id and
the geography from every row of the other, and the view still looked healthy.
Declared as both, each row is joined to whichever matched and a `subject_entity`
column says which.

**`derived` expressions cannot reach withheld data.** They are evaluated over the
already-filtered view, so declaring `contact: phone_numbers` does not leak a phone
number — it fails the install with `column "phone_numbers" does not exist`. The
boundary is structural rather than a matter of trusting the file.

## Materialized or not

Plain views by default: no snapshot, always current, nothing to refresh.

Materialize where measurement says to — a view over hundreds of thousands of rows
that joins a parent on every read. Declaring it materialized also creates the
unique index that `REFRESH ... CONCURRENTLY` requires, so a refresh never blocks
a dashboard mid-query.

Materialized views hold a snapshot and **Postgres never updates one when its base
tables change**. Each registry therefore refreshes its own, on a schedule:

```yaml
analytics:
  reportingViews:
    refreshSchedule: "0 * * * *"   # hourly; empty disables the CronJob
```

Order is resolved from the catalog, not from a list — a view built on another is
always refreshed after it. Between refreshes, records registered since the last
run do not appear in any report; choose the interval accordingly.

## Writing the declaration for a new registry

Run the generator against a **populated** environment with `--discover`. It prints
a starter `tree:` block for review:

```
tree:
  household:  null
  farmer:     {parent: household}
  land:       {parent: farmer}
  crop:       {parent: land}
```

Discovery works by counting which parent each child's links actually resolve
into — real edges land at 100%, coincidental id collisions at a fraction of a
percent. It is a drafting aid, not the authority: on an empty register it can
resolve nothing, which is exactly why the tree is declared rather than inferred.

Where data does exist, the install checks the declaration against it and warns —
never fails, since an empty register has nothing to say — when they disagree:

```
WARNING: tree says score -> household, but only 0.1% of 5,677 links resolve there
```

That check earns its place because a wrong parent is a join that returns nothing,
which is indistinguishable from an empty table.

---

**Next:** [Dashboards](dashboards.md) · [Map drill-down](map-drill-down.md) ·
[Setting up reporting](setting-up-reporting.md)
