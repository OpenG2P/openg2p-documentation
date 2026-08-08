---
description: >-
  The choropleth that drills from region to district to ward — where its figures
  come from, and how a country changes what it shows.
---

# Map drill-down

The map surface renders one choropleth per administrative level and lets a reader
click down through the hierarchy — region, then the districts within it, then the
wards within that — with linked figures beside the map re-filtering as they go.

It reads the same [reporting views](reporting-views.md) as the dashboards. What
makes it a map rather than a chart is one join: **each area's figures are matched
to its shape on P-code**, never on name.

## What the registry supplies

A registry ships a small content bundle, published as a ConfigMap during its
install:

```
maps/
  sources/
    level1_summary.sql      one row per first-level unit
    level2_summary.sql      one row per second-level unit
    level3_summary.sql      one row per third-level unit
    level2_commodities.sql  a breakdown panel
  pages/
    index.md                the page: maps, tiles, charts
```

Each source is an aggregate over a reporting view, and every one of them must
return three columns with these names:

| Column | Is |
|---|---|
| `pcode` | the unit's P-code — what the shape is joined on |
| `parent_pcode` | its parent's P-code — what makes drilling down possible |
| `area_name` | the unit's name, for display only |

Everything else in the query is measures.

{% hint style="warning" %}
**Nothing may be called `name`.** The map component's input is a callable, and a
field called `name` collides with a function's own `name` property — which kills
the map outright rather than producing a warning. Use `area_name`.
{% endhint %}

## Why the files are named by depth

`level1_summary.sql`, not `region_summary.sql`. "Region", "zone", "woreda" are
Ethiopian; a Philippines pack has Region, Province, Municipality, Barangay, and an
Indian one has State and District.

The reporting views unpack geography **positionally** into `geo_1..geo_N`, so the
same query works for any country's pack. `<prefix>_rpt_geo_levels` carries this
deployment's own level labels, so a page can title its columns correctly without
anything in the SQL naming a country.

## Adding a measure

Add it to the `SELECT` in the level file, then reference it on the page. A measure
is any aggregate over the view:

```sql
count(*)                                                as farmers,
round(100.0 * avg(case when is_female then 1 else 0 end), 1) as pct_female,
count(*) filter (where has_land and not has_any_title)  as no_title_farmers
```

{% hint style="info" %}
**Prefer counts to rates for anything an officer should act on.** A rate needs a
denominator large enough to survive one record moving; a count is exact whether
the area holds twelve records or twelve thousand, needs no suppression, and sums
up the hierarchy. "318 farmers holding land with no title" is a work order;
"62.1% titled" is not.
{% endhint %}

## Adding a level, or working with a different depth

Levels are bounded by the country pack. A four-level pack gives `geo_1..geo_4`,
and a source file that references `geo_5` returns nothing.

To add a level, copy the deepest existing file, shift the `geo_N` references down
one, and add the corresponding section to `index.md`. The shapes come from the
pack — Master Data uploads one GeoJSON per level to MinIO during seeding, and the
build fetches them — so a level with no boundary file in the pack has no map to
draw, whatever the SQL returns.

## Changing what the map shows

`index.md` is the page. It decides which measure colours each choropleth, which
appear as headline figures, and what the breakdown panels are. Editing it is how
you change the surface without touching any SQL.

## Getting your version deployed

The content bundle lives in your registry's repository and is published as a
ConfigMap by the registry's chart. The map build is told which ConfigMap to read.

{% hint style="danger" %}
**If that setting is left empty the build falls back to reference content**, and
compiles the reference registry's queries against your registry's database. Every
query fails, and the result is a complete, correctly themed site with every panel
empty — which reads as "no data yet" rather than as a misconfiguration. Set it
explicitly.
{% endhint %}

A country that wants its own map content publishes its **own** ConfigMap and
points the build at it — no fork of the registry or the platform is needed, and
no image is rebuilt.

## What the map cannot do

* **Show more than one registry at once.** One map surface reads one registry's
  views. A combined view across registries is not supported today.
* **Drill below the pack's deepest level**, or to individual records. The map is
  an aggregate surface; record-level questions belong in a dashboard or an
  ad-hoc query.

---

**See also:** [Reporting views](reporting-views.md) ·
[Country Data Architecture](../../country-data-architecture.md) for P-codes,
boundary files and how packs are built.
