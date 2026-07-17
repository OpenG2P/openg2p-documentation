# Data seeding

The Farmer Registry ships a **db-seed** image that prepares a working registry at install time: it applies the register definitions, loads the geo hierarchy, and (optionally) fills the registry with ~500 sample farmers, their profile photos and document templates. A default install seeds all of it.

## Where the seed data comes from

Seed content comes from **three** places — the sample people are deliberately **not** in this repo:

| Source | Provides | Location |
| ------ | -------- | -------- |
| [`openg2p/openg2p-data`](https://github.com/OpenG2P/openg2p-data) (branch `2.0`) | Shared demography — `demography/individuals.csv`, `demography/households.csv`, ~500 `demography/images/*.jpg`, and `geo/geo.csv` | External repo, fetched at **image build time** |
| `docker/db-seed/seed-data/*.json` | Farmer-domain data — `farmers`, `household_members`, `lands`, `crops`, `livestocks`, `farm_inputs`, `membership_details`, `scores` | [In this repo](https://github.com/OpenG2P/farmer-registry/tree/develop/docker/db-seed/seed-data) |
| `farmer-extension/src/.../` | `meta_data/` and `awe_meta_data/` SQL, plus `templates/*.j2` | [The extension](https://github.com/OpenG2P/farmer-registry/tree/develop/farmer-extension) — schema/config only, **no sample data** |

**Why the split.** The demography half is registry-agnostic and shared: person `i0001` is the same individual in the Farmer Registry and the [National Social Registry](../../national-social-registry/README.md), so cross-registry scenarios line up and the 500 people + images are maintained once rather than forked per registry. Each registry commits only its **domain overlay** — which is why `openg2p-data/scripts/` holds both `generate_farmer_data.py` and `generate_nsr_data.py`.

The two halves are joined on `internal_record_id`:

* `individuals.csv` supplies the person core (name, gender, birth date, phone, geo, photo).
* `farmers.json` supplies the farmer-only columns (`source_of_income`, `language_spoken`, disability fields …) — a 1:1 overlay merged **onto** the CSV row to form one `g2p_register_farmers` row.
* The remaining JSON files are **sub-tables** with 1..N rows per farmer (509 lands, 757 crops, 471 livestock …), linked by `link_internal_record_id`.

## The db-seed image

Built from [`docker/db-seed/Dockerfile`](https://github.com/OpenG2P/farmer-registry/blob/develop/docker/db-seed/Dockerfile) and published as `openg2p/openg2p-farmer-registry-db-seed` by the central CI pipeline (see [Build, versioning and CI](helm-chart.md#versions-and-ci)). At build time it copies the extension's SQL and templates, copies the local farmer JSON, and fetches `openg2p-data` into `/openg2p-data`.

That fetch is **pinned**: the `OPENG2P_DATA_BRANCH` build-arg is resolved from ref `2.0` to a commit SHA before the build and recorded as the `org.openg2p.pin.openg2p-data-branch` image label — so any db-seed image tells you exactly which dataset commit is baked in, and a moving `2.0` can't silently change your seed data.

## How it runs, and how the chart drives it

The chart runs db-seed as a **`post-install,post-upgrade` hook Job** (`hook-weight: 10`, so it precedes the [sanity jobs](helm-chart.md#install-time-jobs)). [`entrypoint.sh`](https://github.com/OpenG2P/farmer-registry/blob/develop/docker/db-seed/entrypoint.sh) executes in a deliberate order:

1. **meta\_data SQL** → registry DB (always).
2. **geo** (`loadGeoData`) → `geo.csv` into the **master-data** DB. Runs first so the geo ids the registry rows derive already resolve. Master-data is a generic commons service and ships no seed data, so geo is loaded here over the network.
3. **sample data** (`loadSampleData`) → joins demography CSV with farmer JSON into the `g2p_register_*` tables.
4. **images** (`loadImages`) → profile photos to MinIO, linked to farmers (needs step 3 first).
5. **templates** (`loadTemplates`) → the extension's `.j2` files to MinIO.
6. **AWE seed** (`aweDbSeed`) → policies, stages and the per-release `callback_secret` row into the AWE DB.

Each step is a flag in [`values.yaml`](https://github.com/OpenG2P/farmer-registry/blob/develop/helm/openg2p-farmer-registry/values.yaml) under `dbSeed` — all default to `true`. **For a production install, set `loadSampleData`, `loadImages` and `loadGeoData` to `false`**: the meta-data SQL is required, but the sample farmers and demo geo are not.

> Seeding is idempotent enough to re-run on upgrade, but it is **sample data for demos and testing** — it is not a migration tool and the seeded records are not meant to coexist with real registrant data.
