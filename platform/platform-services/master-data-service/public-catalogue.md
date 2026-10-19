---
description: >-
  The opt-in, anonymous, read-only public catalogue of MDS: what it shows,
  visibility and licence, downloads, DCAT and SKOS, and how to switch it on
---

# Public Catalogue

MDS has no public website: its UI is for administrators. What it can do is make
its catalogue **openly readable** by other websites and open-data portals (a
national data portal, CKAN, a ministry site) through an anonymous, read-only API,
with downloads and standard metadata they can harvest.

Everything public is **opt-in, and off by default**, twice over:

1. The deployment switches the public catalogue on. While it is off, nothing is
   served. An operator turns it on in the MDS chart and, to reach it from
   outside, gives it its own host; the settings are on
   [Deployment: public catalogue host](deployment.md#public-catalogue-host).
2. An administrator marks each dataset, and the geography, **public**. Everything
   is **private** by default, including what a country pack loads.

Whatever the settings, only **published versions** are shown. Drafts, private
datasets, the change feed, who made or approved a version, and the sample people
are never reachable. A private dataset and one that does not exist get the same
"not found", so the API does not reveal what exists behind it.

Authenticated callers, such as registries, are not affected: their API ignores
visibility.

## Visibility and licence

Each dataset, and the geography, has:

* a **visibility**: *Private* (default) or *Public*;
* an optional **data licence**: a label and a URL, for example *CC BY 4.0*.

Both are set in the admin UI and apply at once;
they are not part of a version. Making the geography public makes all its
published versions readable. A public dataset is listed once it has a published
version in effect. The country-pack loader never makes anything public. The steps
are in the [Admin Guide](admin-guide.md#make-a-dataset-public).

### Data licence

The licence of a dataset or of the geography is the **terms under which others may
reuse that data** once it is public. It is shown with the data in the public
catalogue and its downloads, as open-data catalogues (DCAT) expect.

* It often follows the **source's licence**. A country's boundaries from OCHA
  COD-AB, for example, are CC BY-IGO, which requires attribution wherever they are
  shown. The country-pack loader therefore sets the geography's licence from the
  pack's manifest when none is set; see
  [Sources and licence](country-packs.md#sources-and-licence).
* It is set per dataset by the catalogue administrator, who knows the terms of
  each source.
* It is **not** the licence of OpenG2P's code (MPL 2.0).

{% hint style="info" %}
Staff data policies do not apply to the public catalogue: marking a dataset public
is the decision to show all of it.
{% endhint %}

## What it offers

| | |
|---|---|
| **Datasets** | Each public dataset with its entries, at the latest version, a pinned version or as of a date |
| **Geography** | Levels and units, and each level's boundaries |
| **Releases** | Published releases, with their public members only |
| **Downloads** | CSV and JSON per dataset version; CSV and GeoJSON per geography level |
| **DCAT** | A catalogue description that open-data portals can harvest |
| **SKOS** | Each dataset as a concept scheme |

Responses can be cached (they carry `ETag` and `Last-Modified`), can be read from
any website (CORS), and are rate limited per client. Every operation, with its
parameters, is in the [API Reference: Public API](api-reference.md#public-api).

### DCAT catalogue

The DCAT catalogue (JSON-LD) lists each public dataset with a published version in
effect, and the geography when it is public, each with its licence, theme, version
and one download per format. CKAN's DCAT harvester and other portals can harvest
it. See [Standards](standards.md#catalogue-metadata-public-catalogue).

### SKOS concept schemes

Each public dataset can be read as a SKOS concept scheme (JSON-LD): one concept
per active entry, with its code, labels per language and parent. A concept's
address does not include the version, so a code keeps the same address across
versions. See [Standards](standards.md#datasets-and-entries).
