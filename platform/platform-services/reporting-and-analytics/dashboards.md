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

The registry supplies the bundle, a Superset dashboard export ZIP, in a ConfigMap.
The import is the registry platform chart's `<release>-dashboards` Job, the same
for every registry. It runs as the last step of the registry's install chain:

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

Switched by `dashboards.enabled` in the platform chart, which is
`registry.dashboards.enabled` in a registry's chart (on in the Farmer Registry).
The job waits for Superset rather than failing immediately, so a Superset that is
merely restarting does not cost you the import. When Superset does not answer at
all, the job skips the import and the install goes on; set
`registry.dashboards.superset.required: true` to fail the install instead.

{% hint style="info" %}
The Disability Registry and National Social Registry charts still run their own
copy of this job (`<release>-dr-dashboards`, `<release>-nsr-dashboards`),
switched by `analytics.dashboards.enabled`, with the fixed names described below
under "Before per-release names".
{% endhint %}

## Several installs in one Superset

Superset is installed once per namespace, and a namespace can hold several
registries, including several installs of the same one (two Farmer Registries for
two regions). Each install gets its own copy of the dashboards, named after its
Helm release:

| In Superset | Named | Example, release `fr-oromia` |
| --- | --- | --- |
| Dashboards | `<release> · <title>` | `fr-oromia · Land & Tenure` |
| Database connection | `<release>` | `fr-oromia` |
| Charts and datasets | as in the bundle, on that connection | `fr_rpt_land` on `fr-oromia` |

To see one install's dashboards, search the dashboard list for its release name.

**Why.** Superset recognises an imported dashboard, chart, dataset or connection
by its UUID, and a registry's bundle has fixed UUIDs. Imported as they are, a
second install would overwrite the first one's dashboards and point them at its
own database. So the job rewrites the bundle for the release before importing it:
each UUID becomes one derived from the bundle's UUID and the release name, the
connection is named after the release, and the titles get the prefix. Helm release
names are unique within a namespace, so nothing else has to be set, and the same
release gets the same UUIDs on every upgrade, so an upgrade updates its own copy.

**Name releases for what they are.** The release name is what people see in
Superset. Where there may be more than one install, use names like `fr-oromia`
and `fr-amhara` rather than `fr` and `fr2`.

### Before per-release names

Registries that imported their dashboards before this used fixed names: the Farmer
Registry's connection was `FR`, its dashboards had no prefix, and a second install
was not possible. The first upgrade to a chart with per-release names moves the
existing dashboards over in place. They are renamed and keep their ids, so
embedded links, charts made by hand on those datasets and permissions given on the
connection keep working. Only the assets on a connection that points at that
release's own database are moved.

## Access

Superset's own roles decide who sees which dashboards. Give a role access to one
install's data through its connection (`fr-oromia`) and its datasets, and, if you
use [row-level security](row-level-security.md), filter within them.

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
2. **Export** it from Superset (`Export` on the dashboard list), with the other
   dashboards of the same install. You get a ZIP of YAML: dashboards, charts,
   datasets and the database reference.
3. **Turn the export back into a bundle.** The export carries that install's
   names: its UUIDs, its connection name and its title prefix. Committed as it
   is, every other install would get new copies on its next upgrade and stop on
   a clash with its existing connection. The registry platform's script undoes
   the rewrite, using the bundle you have committed:

   ```bash
   # from a checkout of the registry platform repository (registry-platform)
   python3 scripts/dashboards-bundle-from-export.py --release fr-oromia \
     --bundle ../farmer-registry/helm/openg2p-farmer-registry/files/fr-dashboards.zip \
     --export dashboard_export.zip \
     --out ../farmer-registry/helm/openg2p-farmer-registry/files/fr-dashboards.zip
   ```

   Assets the bundle already has get its UUIDs back; charts and dashboards made
   in Superset since keep theirs and become part of the bundle. On the next
   upgrade the install the export came from takes them over in place, and the
   other installs get copies.
4. **Commit the bundle** in your registry's repository and release its chart.
   The import job picks it up on the next install or upgrade.

{% hint style="warning" %}
**Edits made directly in Superset do not survive a reinstall.** The import job
overwrites what it ships (on every upgrade, for that install's copy), and a
rebuilt environment starts from the bundle. Treat
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
