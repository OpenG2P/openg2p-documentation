---
description: >-
  How the National Social Registry is seeded at install — the seed content this
  repo owns and the seeding machinery it inherits from the platform.
---

# Data seeding

{% hint style="info" %}
**New home: GitLab.** **`national-social-registry`** is now developed at [gitlab.com/openg2p/registry/national-social-registry](https://gitlab.com/openg2p/registry/national-social-registry).

Any `github.com` links on this page refer to the **earlier GitHub repository**, which is now read-only. They are kept so that references to previous versions keep working.
{% endhint %}

Seeding follows the same split as everything else: the **machinery** is inherited from the platform's `db-seed` image, and the NSR supplies only its **content**.

{% hint style="info" %}
The `db-seed` image and the rest of the published artifact set are described in the platform docs: [**Packaging & the reference registry**](../../registry/deployment-and-extension/packaging-and-reference-registry.md).
{% endhint %}

## What comes from where

The platform image `openg2p/openg2p-registry-db-seed` is a postgres-client image carrying the generic loaders and nothing NSR-specific:

| Inherited from the platform | Purpose |
|---|---|
| `entrypoint.sh` | Applies the SQL and drives the ordered steps below, entirely from env |
| `load_geo_data.py` | Geo hierarchy → the **master-data** DB (registry-agnostic) |
| `upload_templates.py` | Jinja templates → MinIO |
| `openg2p-data` clone | Shared demography (`individuals.csv`, `households.csv`, ~500 images, `geo/geo.csv`) baked in at image build |

{% hint style="warning" %}
**Two loaders are not domain-agnostic and NSR ships its own.** The base image's
`load_sample_data.py` and `upload_images.py` are written against the **farmer**
schema — they insert into `g2p_register_farmers`/`crops`/`lands` and read
`farmers.json`, `crops.json`, `lands.json`. NSR has none of those tables or files.
Inheriting them makes the db-seed Job crash-loop as soon as `loadSampleData` is on.

NSR therefore keeps [`docker/db-seed/load_sample_data.py`](https://github.com/OpenG2P/national-social-registry/blob/develop/docker/db-seed/load_sample_data.py)
and [`upload_images.py`](https://github.com/OpenG2P/national-social-registry/blob/develop/docker/db-seed/upload_images.py),
which target `g2p_register_individuals` and NSR's `individual_*` / `household_*`
sub-tables, and copies them over the inherited ones in its Dockerfile.
{% endhint %}

The platform image also ships the **reference registry's** seed. NSR's `db-seed` image is a thin `FROM` of it that clears those directories and copies its own:

```dockerfile
FROM openg2p/openg2p-registry-db-seed:${RP_VERSION}
RUN rm -rf /seed/meta_data/* /seed/awe_meta_data/* /seed/templates/* /seed/seed-data/*
COPY nsr-extension/src/openg2p_registry_nsr_extension/meta_data/     /seed/meta_data/
COPY nsr-extension/src/openg2p_registry_nsr_extension/awe_meta_data/ /seed/awe_meta_data/
COPY nsr-extension/src/openg2p_registry_nsr_extension/templates/     /seed/templates/
COPY docker/db-seed/seed-data/                                       /seed/seed-data/

# NSR's domain-specific loaders, overriding the base image's farmer-shaped ones.
COPY docker/db-seed/load_sample_data.py /seed/load_sample_data.py
COPY docker/db-seed/upload_images.py    /seed/upload_images.py
```

So the NSR seed content is exactly four things:

| Content | Source in this repo |
|---|---|
| `meta_data/` SQL — register definitions, schemas, UI tabs/sections, attribute lookups, score definitions, registry configuration, inbound message rules | [`nsr-extension/.../meta_data`](https://github.com/OpenG2P/national-social-registry/tree/develop/nsr-extension/src/openg2p_registry_nsr_extension/meta_data) |
| `awe_meta_data/` SQL — approval policy, stages, approver rules, callback-secret template | [`nsr-extension/.../awe_meta_data`](https://github.com/OpenG2P/national-social-registry/tree/develop/nsr-extension/src/openg2p_registry_nsr_extension/awe_meta_data) |
| `templates/` — the DCI Jinja templates (`nsr_individual_to_dci`, `dci_to_nsr_individual`, `crvsvc_to_nsr_individual`, `dci_commons_response`) | [`nsr-extension/.../templates`](https://github.com/OpenG2P/national-social-registry/tree/develop/nsr-extension/src/openg2p_registry_nsr_extension/templates) |
| `seed-data/*.json` — NSR-domain sample rows: household assets, housing and services, programs, individual disabilities, land, livelihoods, livestock, programs, vulnerability, shocks, scores | [`docker/db-seed/seed-data`](https://github.com/OpenG2P/national-social-registry/tree/develop/docker/db-seed/seed-data) |

### Why the sample people are not in this repo

The demography half is registry-agnostic and shared: person `i0001` is the same individual in the NSR and the [Farmer Registry](../../farmer-registry/README.md), so cross-registry scenarios line up and the 500 people and images are maintained once rather than forked per registry. Each registry commits only its **domain overlay**.

The two halves join on `internal_record_id`: `individuals.csv` supplies the person core (name, gender, birth date, phone, geo, photo), and the JSON files are **sub-tables** with 1..N rows per individual or household, linked by `link_internal_record_id`.

The `openg2p-data` fetch is **pinned**: the `OPENG2P_DATA_BRANCH` build-arg is resolved from ref `2.0` to a commit SHA before the build and recorded as an `org.openg2p.pin.*` image label, so a moving `2.0` cannot silently change your seed data.

## What runs, in what order

The chart runs db-seed as a `post-install,post-upgrade` hook Job. An init container first waits for the registry APIs and for **AWE** to be healthy; then the entrypoint executes:

| # | Step | Controlled by | Notes |
|---|---|---|---|
| 1 | **meta-data SQL** → registry DB | *always runs* | Register definitions, UI metadata, AWE integration mappings. Every `.sql` under `meta_data/` runs in sorted path order |
| 2 | **geo** → master-data DB | `loadGeoData` | Runs before sample data so the geo ids the registry rows derive already resolve |
| 3 | **sample data** → `g2p_register_*` | `loadSampleData` | Joins the demography CSV with the NSR JSON |
| 4 | **images** → MinIO | `loadImages` | Profile photos, linked to individuals — needs step 3 |
| 5 | **templates** → MinIO | `loadTemplates` | The extension's `.j2` files |
| 6 | **AWE seed** → AWE DB | `aweDbSeed` | Approval policy, stages, approver rules, and the per-release `callback_secret` row |

{% hint style="warning" %}
**Only step 1 is unconditional.** In the platform chart every loader defaults to **off**, because the reference registry is deliberately minimal. NSR ships demo records, geo and images, so its overlay turns them on:

```yaml
registry:
  dbSeed:
    loadGeoData: true
    loadSampleData: true
    loadImages: true
    loadTemplates: true
```

Note these are `registry.dbSeed.*`, **not** `global.*` — the db-seed Job reads `.Values.dbSeed.load*` and there is no global fallback, so setting them under `global` silently does nothing.
{% endhint %}

**For a production install set `loadSampleData`, `loadImages` and `loadGeoData` to `false`.** The meta-data SQL is required; the sample records and demo geo are not. Keep `loadTemplates: true` — without the DCI templates in MinIO, every record fails to render and a DCI search returns an empty result.

> Seeding is idempotent enough to re-run on upgrade, but it is **sample data for demos and testing**. It is not a migration tool, and the seeded records are not meant to coexist with real registrant data.

See the [Meta Data Seeding design](../../registry/design/meta-data-seeding.md) for the platform-level framework.
