---
description: How a registry's configuration and its sample data are seeded into the registry database after deployment.
---

# Meta Data Seeding

## Overview

Every OpenG2P Registry deployment needs a set of **meta data** in its database before it can be used: register definitions, UI tab and section layouts, data-model definitions, verifiable-credential configurations and message templates. Without it, the registry has empty tables and no registers.

Seeding runs **after** the application pods have started and created the tables, as the db-seed Job.

## What gets seeded

| Kind | Source in the registry's extension package | Applied |
| --- | --- | --- |
| **Configuration** | `meta_data/` (registers, screens, the binding of forms and change requests to AWE policy keys), `templates/` (Jinja templates, uploaded to the object store), the AWE callback secret (`awe_meta_data/40_callback_secret.sql.tpl`) | On every install and upgrade |
| **Sample data** | The sample approval policies (`awe_meta_data/*.sql`), the demo staff users they name, the variant's sample records (its `docker/db-seed/load_sample_data.py`) and sample photos | Only with **Load Sample Data** (`dbSeed.loadSampleData`); photos with **Load Sample Images** |

Datasets and geography are not seeded: registries read them live from Master Data, which loads them from the country pack ([Country data & seeding](../deployment-and-extension/country-data-and-seeding.md#datasets)). Which switch controls what, from commons-services to the registry: [every switch](../deployment-and-extension/country-data-and-seeding.md#configuration-or-sample-every-switch).

{% hint style="warning" %}
Configuration is **mandatory**: keep **Enable DB Seed** on in production. Sample data is off by default and stays off in production.
{% endhint %}

## Source: the registry's own repository

The SQL lives in each registry's extension package, for example [`farmer-extension`](https://github.com/OpenG2P/farmer-registry/tree/develop/farmer-extension) in the Farmer Registry; the loaders live in its `docker/db-seed/`:

```
farmer-registry/
├── farmer-extension/src/openg2p_registry_farmer_extension/
│   ├── meta_data/          ← configuration SQL
│   ├── awe_meta_data/      ← sample approval policies; the callback secret template
│   └── templates/          ← Jinja templates
└── docker/db-seed/
    ├── load_sample_data.py ← the variant's sample loader
    └── seed-data/          ← the variant's own sample fields
```

## Docker image

The platform publishes `openg2p/openg2p-registry-db-seed`: the entrypoint, the ordering and the shared machinery (Master Data client, template upload, demo staff users, reporting-view generator), with no registry content. Each registry builds its own image `FROM` it, at the platform version it is built on, and copies in its `meta_data/`, `awe_meta_data/`, `templates/` and loaders (for example `openg2p/openg2p-farmer-registry-db-seed`).

The entrypoint applies the SQL with `ON_ERROR_STOP=0`, so one failed statement does not abort the seed, and every statement must be idempotent ([Contracts that fail silently](../developer-zone/building-a-registry/contracts-that-fail-silently.md)). The steps and their order: [What runs, in what order](../deployment-and-extension/country-data-and-seeding.md#what-runs-in-what-order).

## Helm chart integration

The platform chart `openg2p-registry` runs the image as a **post-install / post-upgrade** hook Job. It waits for the APIs, AWE and Master Data's geography before seeding.

```yaml
dbSeed:
  enabled: true          # configuration: keep on
  loadSampleData: false  # sample records, sample approval policies, demo staff users
  loadImages: false      # sample photos; needs loadSampleData
  image:
    repository: openg2p/openg2p-farmer-registry-db-seed
```

In a registry's own chart these sit under `registry.dbSeed`.

{% hint style="info" %}
Because the seed content is packaged into a Docker image, changing it only needs a new image from the registry's repository, not a chart rebuild.
{% endhint %}

## Versions

| Docker image | Tag | Date | Comments |
| --- | --- | --- | --- |
| `openg2p/openg2p-farmer-registry-db-seed` | `1.0.2` | 19 Apr 2026 | Initial version of meta data seeder |
