---
description: >-
  Apache Superset dashboards — shipped by each registry, imported during its own
  install, and how a country changes them.
---

# Dashboards

Dashboards are built in **Apache Superset**, reading the
[reporting views](reporting-views.md). Superset is installed once per environment
as part of `commons-services`; the dashboards themselves belong to each registry.

## The registry imports its own dashboards

This is the part that usually surprises people: the dashboard bundle ships in the
**registry's** repository, and the registry's own install imports it. The
analytics platform does not push dashboards to registries.

It runs as the last step of the registry's install chain:

```
40  bulk sample        generate demo records (optional)
45  reporting views    create the views — hand-written, then generated
50  dashboards         import into Superset, publish, enable embedding
```

The ordering is the point. Dashboards are imported **after** the views exist and
after any bulk data, so a dashboard opened straight after an install already has
figures behind it rather than rendering empty.

Two consequences worth knowing:

* **A registry installed without the analytics platform still gets its
  dashboards.** It needs Superset to be reachable, nothing more.
* **Because the install stops at a failed hook**, a failure in bulk generation
  (40) prevents the views (45) and the import (50) from ever running. If Superset
  has no dashboards after an install, look at the *earlier* jobs first.

Switched by `analytics.dashboards.enabled`. The job waits for Superset rather
than failing immediately, so a Superset that is merely restarting does not cost
you the import.

## What arrives

Each registry ships a small set of published dashboards over its main views —
demographics, coverage and data quality, and whatever is specific to it (land and
tenure, crops, livestock for a Farmer Registry). They are reference dashboards:
correct, useful as a starting point, and not intended to be the set a country
finally runs.

Embedding is enabled on each during import, which is what lets them appear inside
another product's page rather than only at Superset's own URL.

## Adding or changing a dashboard

Superset is the editor. Build the chart or dashboard in Superset against the
existing datasets, then take it back out:

1. **Build it in Superset**, against a `*_rpt_*` dataset. If you need a view that
   does not exist yet, that is a [reporting views](reporting-views.md) change,
   not a dashboard change.
2. **Export** it from Superset (`Export` on the dashboard list) — you get a zip
   of YAML: dashboard, charts, datasets and the database reference.
3. **Put the zip in your registry's repository**, replacing the shipped bundle,
   and rebuild the registry's db-seed image. The import job picks it up on the
   next install.

{% hint style="warning" %}
**Edits made directly in Superset do not survive a reinstall.** The import job
overwrites what it ships, and a rebuilt environment starts from the bundle. Treat
Superset as the editor and your repository as the source of truth — anything you
want to keep has to be exported back.
{% endhint %}

### If you are keeping the shipped dashboards

Export them, commit them as your own bundle, and change them from there. A
country's dashboards will diverge from the reference set almost immediately, and
maintaining that divergence as a fork of the bundle is far easier than
re-applying it after every upgrade.

### New views need no dashboard work to be usable

The views generated for entities the reference dashboards do not cover —
livestock, farm inputs, memberships, change requests — carry no dashboards. They
are queryable in Superset immediately: add the dataset, build a chart. Only the
dashboards are curated; the data is not gated.

## Geographic columns and dashboard portability

Views carry `geo_1..geo_N` where **N is the country's actual depth**, taken from
Master Data. A four-level pack has no `geo_5`.

A dashboard that names `geo_4` therefore works in a country with four or more
levels and breaks in one with three. If you are building dashboards intended to
travel between countries, either stay at `geo_1`/`geo_2`, which every pack has,
or read `<prefix>_rpt_geo_levels` — a small view carrying this deployment's own
level names and depths — and drive the chart from that.

---

**See also:** [Reporting views](reporting-views.md) ·
[Setting up reporting](setting-up-reporting.md) ·
[Row-level security](row-level-security.md) to filter a dashboard by who is
looking at it.
