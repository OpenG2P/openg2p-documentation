---
description: >-
  How the Farmer Registry is seeded at install — the seed content this repo owns
  and the seeding machinery it inherits from the platform.
---

# Data seeding

{% hint style="info" %}
**New home: GitLab.** **`farmer-registry`** is now developed at [gitlab.com/openg2p/registry/farmer-registry](https://gitlab.com/openg2p/registry/farmer-registry).

Any `github.com` links on this page refer to the **earlier GitHub repository**, which is now read-only. They are kept so that references to previous versions keep working.
{% endhint %}

Seeding follows the same split as everything else: the **machinery** is inherited from the platform's `db-seed` image, and the Farmer Registry supplies only its **content**.

{% hint style="info" %}
The `db-seed` image and the rest of the published artifact set are described in the platform docs: [**Packaging & the reference registry**](../../registry/deployment-and-extension/packaging-and-reference-registry.md).
{% endhint %}

## What comes from where

The platform image `openg2p/openg2p-registry-db-seed` is a postgres-client image carrying the generic loaders and nothing farmer-specific:

| Inherited from the platform | Purpose |
|---|---|
| `entrypoint.sh` | Applies the SQL and drives the ordered steps below, entirely from env |
| `load_geo_data.py` | Geo hierarchy → the **master-data** DB |
| `load_sample_data.py` | Demography CSV + registry sub-table JSON → `g2p_register_*` |
| `upload_images.py` | Profile photos → MinIO |
| `upload_templates.py` | Jinja templates → MinIO |
| `openg2p-data` clone | Shared demography (`individuals.csv`, `households.csv`, ~500 images, `geo/geo.csv`) baked in at image build |

The platform image also ships the **reference registry's** seed. The Farmer Registry's `db-seed` image is a thin `FROM` of it that clears those directories and copies its own:

```dockerfile
FROM openg2p/openg2p-registry-db-seed:${RP_VERSION}
RUN rm -rf /seed/meta_data/* /seed/awe_meta_data/* /seed/templates/* /seed/seed-data/*
COPY farmer-extension/src/openg2p_registry_farmer_extension/meta_data/     /seed/meta_data/
COPY farmer-extension/src/openg2p_registry_farmer_extension/awe_meta_data/ /seed/awe_meta_data/
COPY farmer-extension/src/openg2p_registry_farmer_extension/templates/     /seed/templates/
COPY docker/db-seed/seed-data/                                             /seed/seed-data/
```

So the farmer seed content is exactly four things:

| Content | Source in this repo |
|---|---|
| `meta_data/` SQL — register definitions, schemas, UI tabs/sections, attributes, score definitions, registry configuration | [`farmer-extension/.../meta_data`](https://github.com/OpenG2P/farmer-registry/tree/develop/farmer-extension/src/openg2p_registry_farmer_extension/meta_data) |
| `awe_meta_data/` SQL — approval policy, stages, approver rules, callback-secret template | [`farmer-extension/.../awe_meta_data`](https://github.com/OpenG2P/farmer-registry/tree/develop/farmer-extension/src/openg2p_registry_farmer_extension/awe_meta_data) |
| `templates/` — the DCI Jinja templates (`openg2p_farmer_to_dci`, `dci_to_openg2p_farmer`, `dci_commons_response`) | [`farmer-extension/.../templates`](https://github.com/OpenG2P/farmer-registry/tree/develop/farmer-extension/src/openg2p_registry_farmer_extension/templates) |
| `seed-data/*.json` — farmer-domain sample rows: `farmers`, `household_members`, `lands`, `crops`, `livestocks`, `farm_inputs`, `membership_details`, `scores` | [`docker/db-seed/seed-data`](https://github.com/OpenG2P/farmer-registry/tree/develop/docker/db-seed/seed-data) |

### Why the sample people are not in this repo

The demography half is registry-agnostic and shared: person `i0001` is the same individual in the Farmer Registry and the [National Social Registry](../../national-social-registry/README.md), so cross-registry scenarios line up and the 500 people and images are maintained once rather than forked per registry. Each registry commits only its **domain overlay**.

The two halves join on `internal_record_id`:

* `individuals.csv` supplies the person core (name, gender, birth date, phone, geo, photo).
* `farmers.json` supplies the farmer-only columns (`source_of_income`, `language_spoken`, disability fields …) — a 1:1 overlay merged **onto** the CSV row to form one `g2p_register_farmers` row.
* The remaining JSON files are **sub-tables** with 1..N rows per farmer, linked by `link_internal_record_id`.

The `openg2p-data` fetch is **pinned**: the `OPENG2P_DATA_BRANCH` build-arg is resolved from ref `2.0` to a commit SHA before the build and recorded as an `org.openg2p.pin.*` image label, so a moving `2.0` cannot silently change your seed data.

## What runs, in what order

The chart runs db-seed as a `post-install,post-upgrade` hook Job. An init container first waits for the registry APIs and for **AWE** to be healthy; then the entrypoint executes:

| # | Step | Controlled by | Notes |
|---|---|---|---|
| 1 | **meta-data SQL** → registry DB | *always runs* | Register definitions, UI metadata, AWE integration mappings |
| 2 | **geo** → master-data DB | `loadGeoData` | Runs before sample data so the geo ids the registry rows derive already resolve. Master-data is a generic commons service and ships no seed data, so geo is loaded here over the network |
| 3 | **sample data** → `g2p_register_*` | `loadSampleData` | Joins the demography CSV with the farmer JSON |
| 4 | **images** → MinIO | `loadImages` | Profile photos, linked to farmers — needs step 3 |
| 5 | **templates** → MinIO | `loadTemplates` | The extension's `.j2` files |
| 6 | **AWE seed** → AWE DB | `aweDbSeed` | Approval policy, stages, approver rules, and the per-release `callback_secret` row |

{% hint style="warning" %}
**Only step 1 is unconditional.** In the platform chart every loader defaults to **off**, because the reference registry is deliberately minimal. The Farmer Registry ships demo records, geo and images, so its overlay turns them on:

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

**For a production install set `loadSampleData`, `loadImages` and `loadGeoData` to `false`.** The meta-data SQL is required; the sample farmers and demo geo are not. Keep `loadTemplates: true` — without the DCI templates in MinIO, every record fails to render and a DCI search returns an empty result.

> Seeding is idempotent enough to re-run on upgrade, but it is **sample data for demos and testing**. It is not a migration tool, and the seeded records are not meant to coexist with real registrant data.
