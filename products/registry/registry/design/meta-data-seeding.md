---
description: How variant-specific configuration and sample data are seeded into the registry database after deployment.
---

# Meta Data Seeding

## Overview

Every OpenG2P Registry deployment requires a set of **meta data** to be loaded into the database before the registry is operational. This meta data includes register definitions, UI tab and section layouts, lookup attributes, data-model definitions, verifiable-credential configurations, and message templates.

Meta data seeding runs **after** the application pods have started and created the database tables. Without it, the registry has an empty schema with no register definitions, no intake forms, and no lookup values — effectively unusable.

## What gets seeded

The seed data is split into two categories:

| Category | Folder | Required | Description |
| --- | --- | --- | --- |
| **Configuration** | `configurations/` | Yes | Register definitions, UI layouts, lookup data, VC configs, message templates. These are essential for the registry to function. |
| **Sample data** | `sample_data/` | No | Demo registrants, households, land records, etc. Useful for testing and training but should typically be skipped in production. |

{% hint style="warning" %}
Configuration meta data (the `configurations/` folder) is **mandatory**. The registry will not work correctly without it. Sample data is optional and is disabled by default.
{% endhint %}

## Source: the registry's extension package

The SQL scripts live in each registry's **own repository**, inside its extension package — for example [`farmer-extension`](https://github.com/OpenG2P/farmer-registry/tree/develop/farmer-extension) in the Farmer Registry and [`nsr-extension`](https://github.com/OpenG2P/national-social-registry/tree/develop/nsr-extension) in the National Social Registry:

```
farmer-registry/                      ← the registry's own repo
└── farmer-extension/
    └── src/openg2p_registry_farmer_extension/
│       ├── configurations/          ← mandatory meta data
│       │   ├── data-models/
│       │   ├── lookup-data/
│       │   ├── register-metadata/
│       │   ├── registry-configurations/
│       │   ├── registry-inbound-message-rules/
│       │   └── registry-outbound-messages-templates/
│       └── sample_data/             ← optional demo data
│           └── register-data/
│
├── openg2p-registry-family-extension/
│   └── src/openg2p_registry_family_extension/
│       ├── configurations/
│       └── sample_data/
```

Each variant defines its own set of registers, attributes, UI sections, and sample records. When adding a new variant, create a new extension folder following the same structure.

## Docker image

A lightweight Docker image is automatically built from the extensions repository for each variant. The image is based on `postgres:16-alpine` (which provides the `psql` client) and contains only the SQL scripts and an entrypoint shell script.

**Image naming convention:**

| Variant | Image |
| --- | --- |
| Farmer | `openg2p/openg2p-farmer-registry-db-seed:<branch>` |
| Family | `openg2p/openg2p-family-registry-db-seed:<branch>` |

The CI workflow (`.github/workflows/docker-build-db-seed.yml`) triggers on any push that changes SQL scripts, the Dockerfile, or the entrypoint. It builds all variant images in parallel using a matrix strategy. The image tag matches the Git branch name (`main`/`master` maps to `develop`).

**Entrypoint behaviour:**

1. Executes all `.sql` files under `/seed/configurations/` in alphabetical order (by full path).
2. If the environment variable `LOAD_SAMPLE_DATA` is set to `true`, also executes all `.sql` files under `/seed/sample_data/`.
3. Uses `ON_ERROR_STOP=0` so that individual statement failures (e.g. duplicate key on re-run) do not abort the entire seed process.

## Helm chart integration

The [Registry Helm Chart 4.x](../_archive/deployment/helm-chart-4.x.md) runs the seed image as a **post-install / post-upgrade** hook Job. The Job waits for all application pods to be healthy before executing, ensuring that database tables have been created by the API services.

```yaml
dbSeed:
  enabled: true
  loadSampleData: false
  image:
    repository: openg2p/openg2p-farmer-registry-db-seed
    tag: develop
```

Set `dbSeed.loadSampleData: true` to include sample data during installation. For a different variant, override `dbSeed.image.repository` with the appropriate seed image.

{% hint style="info" %}
Because the seed scripts are packaged into a Docker image, updating meta data only requires publishing a new image from the extensions repository. No Helm chart rebuild is needed.
{% endhint %}

## Versions

| Docker image | Tag | Date | Comments |
| --- | --- | --- | --- |
| `openg2p/openg2p-farmer-registry-db-seed` | `1.0.2` | 19 Apr 2026 | Initial version of meta data seeder |
