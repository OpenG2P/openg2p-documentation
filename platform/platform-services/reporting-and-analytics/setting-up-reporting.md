---
description: >-
  What reporting a new deployment gets for free, what to write when it does not
  fit, and what to do when the country pack or the registry schema later changes.
---

# Setting up reporting

This is the practical path: bringing up a registry for a country and ending with
views, dashboards and a map that work — then keeping them working as things
change.

## 1. A plain install, with nothing configured

Install a registry — Farmer Registry, National Social Registry, or your own
manifestation — with `analytics.reportingViews.enabled: true` (the default), and
you already have:

* a **view per entity** in the registry, with geography, workflow columns and
  personal data withheld
* `<prefix>_rpt_geo_levels`, naming this country's levels at their depths
* `<prefix>_rpt_change_request` and `<prefix>_rpt_record_history`, for approval
  throughput and change history
* the registry's **dashboards** imported into Superset and published
* the **map** built from the registry's own content bundle

Nothing above requires a line of configuration. The views come from the
registry's schema and Master Data's country pack.

**Check it worked** by reading the reporting job's log. It states what it found
and what it made:

```
[reporting] hierarchy from Master Data: 4 level(s) — country > region > zone > woreda
[reporting] declared tree agrees with the data
[reporting] created 11 view(s): …
[reporting] verified: no withheld column reached any of the 11 generated view(s)
```

If personal data reached a view, the job **fails** and names the column. That is
the intended behaviour, not a fault to work around.

## 2. When your registry has its own tables

A country extension that adds registers gets views for them automatically, as
long as they follow the platform's conventions — `g2p_register_*` naming, an
`internal_record_id`, and `link_internal_record_id` pointing at the parent.

What the platform cannot work out is **which parent**, so declare it. Draft the
declaration by running the generator against a **populated** environment:

```sh
python3 /seed/generate_reporting_views.py --discover
```

It prints a `tree:` block; review it and put it in your registry's
`reporting.yaml`. Review rather than paste: discovery reads the data, and data can
be unrepresentative — see
[Reporting views](reporting-views.md#writing-the-declaration-for-a-new-registry).

Then add only what is genuinely yours: what a column *means* (`derived`), which
parent attributes belong on a child row (`inherit`), which rows count
(`filter`), which views need a snapshot (`materialized`). Everything else is
already handled.

## 3. Bulk sample data — for testing, not for production

Registries can generate a large volume of invented records so that dashboards and
maps have something to show.

```yaml
analytics:
  bulkSample:
    enabled: false     # production
```

{% hint style="warning" %}
**Turn it off for production.** These are invented people. They are useful for
exercising a dashboard before real registration starts, and they must never sit
in a live register.
{% endhint %}

The important consequence for reporting: **an empty register still produces the
full set of views** — they are built from the schema, not the data — but every
one of them returns nothing, and every dashboard renders empty. That is correct
behaviour and it looks exactly like a broken install. Expect it, and prove the
pipeline once with bulk data in a test environment before turning it off.

Bulk generation reads Master Data's geographic hierarchy, so it fails rather than
producing records that point nowhere if Master Data has not been seeded. See
[Country Data Architecture](../../country-data-architecture.md).

## 4. When things change afterwards

### The country pack changes

A new pack with a different **depth** — five levels where there were four —
changes the views: they carry `geo_1..geo_5` on the next install or upgrade,
because depth is read from Master Data rather than fixed anywhere.

Two things to check afterwards:

* **Dashboards or map sources naming a level that no longer exists.** A source
  file referencing `geo_5` in a four-level country returns nothing.
* **Boundary shapes and figures must come from the same pack.** They are joined
  on P-code, so a map built from one country's pack beside a Master Data seeded
  with another renders empty rather than raising an error.

### The registry schema changes

A new register table in an extension gets a view on the next install, once its
parent is declared in `tree`. A new *column* on an existing table appears with no
declaration at all — unless the classifier reads it as personal data, in which
case it is withheld and the job says so in its log.

### An upgrade

Views are dropped and recreated on every install and upgrade, so an upgrade picks
up new platform behaviour without any migration step. Superset datasets are not
re-synced automatically: a dataset in Superset keeps the column list it was
imported with, so re-sync it there to see columns added since.

### Data changes, but not the schema

Nothing to do — except that **materialized views hold a snapshot**. If yours are
materialized, they show what they held at the last refresh. See
[Reporting views](reporting-views.md#materialized-or-not).

## 5. Adding dashboards

Build in Superset, export the zip, commit it into your registry's repository as
your own bundle. Full round-trip in [Dashboards](dashboards.md) — including why
edits made only in Superset do not survive a reinstall.

## 6. Changing the map

Edit the SQL and the page in your registry's map content bundle, publish it as
your own ConfigMap, and point the map build at it. No fork and no image rebuild.
See [Map drill-down](map-drill-down.md).

## A checklist for a new country

1. Country pack built and Master Data seeded — geographic hierarchy and boundary
   shapes present. ([Country Data Architecture](../../country-data-architecture.md))
2. Registry installed; reporting job log shows the right level count and a
   `verified` line.
3. `<prefix>_rpt_geo_levels` names the country's own levels.
4. Dashboards visible and published in Superset.
5. Map renders and drills down; figures match the register.
6. Bulk sample **off** before the environment carries real registrations.
7. Refresh schedule set if any view is materialized.
