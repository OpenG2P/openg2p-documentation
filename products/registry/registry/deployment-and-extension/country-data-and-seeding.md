---
description: >-
  How a registry gets its country's geography and datasets from Master Data,
  which data is configuration and which is sample data, every switch from
  commons-services to the registry, and the three kinds
---

# Country data & seeding

A registry's **structure** — its tables, fields, validation rules and reports — is built into its extension. Everything country-specific comes from the **Master Data Service** (MDS), which is seeded from a **country pack**.

{% hint style="info" %}
This page covers what the _registry_ does. For what a country pack is, where packs live, what P-codes are and how a country is configured end to end, see [Country Packs](../../../../platform/platform-services/master-data-service/country-packs.md).
{% endhint %}

## The registry has no country setting

A registry never names a country. It reads whatever the MDS beside it was seeded with, and adapts:

| What the registry takes | Held in MDS as (read via its API)                 | When                                    | Effect                                                               |
| ----------------------- | ------------------------------------------------- | --------------------------------------- | -------------------------------------------------------------------- |
| The geo hierarchy       | `g2p_geo_levels`, `g2p_geo_level_values`          | **Live**, as a form loads and is filled | Address dropdowns match the country's levels, however many there are |
| The datasets            | `g2p_attributes`, `g2p_attribute_values`          | **Live**, as a form is filled           | Gender, education, water source… are the country's own               |
| The sample people       | `g2p_sample_individuals`, `g2p_sample_households` | At install, by the sample loader        | Demo records that belong to the country                              |

This is what lets **one registry image serve any country**. Changing country is a matter of pointing the registry at an MDS seeded with a different pack — there is no registry rebuild and no registry-side country value to keep in step.

{% hint style="warning" %}
**Then why do the variant charts have `expectedCountry`?**

It is a **guard, not a selector**. Setting `analytics.bulkSample.expectedCountry: ETH` does not make the registry Ethiopian; it makes the seed job **fail loudly** if the MDS it finds holds a different country than this deployment was set up for. Left empty (the default), no check is made. Nothing in the registry chooses the country — only MDS does.
{% endhint %}

Geography and datasets are **not copied** into the registry, and the registry never reads MDS's database: the staff portal asks the MDS API each time a form needs them, and so does the coded-value check when it is switched on (see [Datasets](country-data-and-seeding.md#datasets)). MDS is therefore a **runtime dependency for data entry** — while it is unavailable, coded dropdowns have no options. Records already stored are unaffected; they hold the codes.

## How the registry reads MDS

A client in the registry core reads through the MDS catalogue API with the registry's own Keycloak client. It caches by version, follows the MDS change feed, and keeps serving the last good data if MDS is briefly unreachable. Activities record the catalogue versions they were checked against, and a registry can pin a catalogue release. New coded values are validated against the version in effect; a retired code's label is shown at the version recorded on the activity. Accepting an unchanged retired value when an entity record is edited is still to do.

Direct reads of MDS's database remain only as a rollback switch (`masterDataReadMode: db`; see [Seeding never touches Master Data's database](country-data-and-seeding.md#seeding-never-touches-master-datas-database)). How any consumer should read MDS is in [For Consumers](../../../../platform/platform-services/master-data-service/consumers.md).

## Three different kinds of data

These are routinely confused. They have different purposes, different volumes, and different switches.

|                                | Sample data                                      | Bulk data                                               | Sanity data                            |
| ------------------------------ | ------------------------------------------------ | ------------------------------------------------------- | -------------------------------------- |
| **Purpose**                    | Demonstrations — records a person actually reads | Volume so reports and dashboards have something to show | Verifying the deploy works             |
| **How much**                   | A few dozen people                               | Tens or hundreds of thousands                           | A handful of fixtures                  |
| **Coherent with the country?** | Yes — comes from the pack                        | No — invented names and numbers                         | No                                     |
| **Where defined**              | MDS (people) + the registry (its own fields)     | Generated by the registry at install                    | Created by the sanity suite            |
| **Left behind afterwards**     | Yes                                              | Yes                                                     | **Yes** — deliberately, for inspection |
| **Switch**                     | `dbSeed.loadSampleData`                          | `analytics.bulkSample.enabled`                          | `sanity.enabled` + `sanity.runE2e`     |

{% hint style="danger" %}
**All three are for demonstration and testing. A production install should create none of them.** See [An empty install](country-data-and-seeding.md#an-empty-install-for-production).
{% endhint %}

## Configuration or sample: every switch

An environment gets its data from two installs: **commons-services** (Master Data, and the mock identity system) and each **registry**. Some of it is configuration, which production needs; the rest is sample data, for demos and tests only.

| Data                                                                                                                                              | Comes from                                                                                                                       | Kind          | Switch (form field, value)                                                              | Default       | Production                                                                                              |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ------------- | --------------------------------------------------------------------------------------- | ------------- | ------------------------------------------------------------------------------------------------------- |
| Geography: levels, units, boundaries                                                                                                              | The country pack, loaded into Master Data                                                                                        | Configuration | **Load Geography** (`geoSeed.load.geo`, Master Data chart form only)                    | On            | On                                                                                                      |
| Core datasets (gender, education…)                                                                                                                | The pack's `codelists/`                                                                                                          | Configuration | **Load Datasets** (`masterData.geoSeed.load.codelists`)                                 | On            | On                                                                                                      |
| Theme datasets (crops, `AGENT_*` lists…)                                                                                                          | The pack's `domains/<theme>/`                                                                                                    | Configuration | **Dataset Themes** (`masterData.geoSeed.domains`)                                       | `agriculture` | The themes the registries need                                                                          |
| Sample people: individuals and households                                                                                                         | The pack's `samples/`, loaded into Master Data                                                                                   | Sample        | **Load Sample People** (`masterData.geoSeed.load.samples`)                              | **On**        | **Off**                                                                                                 |
| Test identities for the national ID login                                                                                                         | Master Data's sample people, copied into the mock identity system                                                                | Sample        | **Install Mock Identity System?** (`mock-identity-system.enabled`)                      | On            | Off: eSignet uses the real ID system                                                                    |
| The staff user `admin`                                                                                                                            | commons-base (its keycloak-init), password `admin`, to be changed at first login. Each registry gives it its administrator roles | Configuration | None                                                                                    | Created       | Created; change the password                                                                            |
| The registry's configuration: registers, screens, templates, the binding of forms and change requests to AWE policy keys, the AWE callback secret | The registry's db-seed image                                                                                                     | Configuration | **Enable DB Seed** (`registry.dbSeed.enabled`)                                          | On            | **On**                                                                                                  |
| Sample records (farmers, agents, clusters…)                                                                                                       | The registry's sample loader, from Master Data or the pack                                                                       | Sample        | **Load Sample Data** (`registry.dbSeed.loadSampleData`)                                 | Off           | Off                                                                                                     |
| Sample approval policies and demo staff users (`alex.carter`, `nina.patel`…)                                                                      | The registry's `awe_meta_data/`; the platform chart's `dbSeed.sampleStaffUsers`                                                  | Sample        | **Load Sample Data**                                                                    | Off           | Off: set up in AWE and Keycloak ([below](country-data-and-seeding.md#approval-policies-and-demo-staff)) |
| Sample profile photos                                                                                                                             | openg2p-data, in the db-seed image                                                                                               | Sample        | **Load Sample Images** (`registry.dbSeed.loadImages`)                                   | Off           | Off                                                                                                     |
| Sample activities (the Agents Registry's trainings, the Crop Sown Registry's crop seasons)                                                        | The registry's activity-samples Job                                                                                              | Sample        | **Load sample trainings**, **Load sample crop seasons**                                 | Off           | Off                                                                                                     |
| Bulk data                                                                                                                                         | The registry's bulk generator                                                                                                    | Sample        | **Generate bulk demo data** (`analytics.bulkSample.enabled`), where the registry has it | Off           | Off                                                                                                     |
| Sanity fixtures                                                                                                                                   | The sanity suite                                                                                                                 | Test          | **Sanity - Run Full E2E** (`registry.sanity.runE2e`)                                    | Off           | Off                                                                                                     |

### What each switch needs

* **Load Sample Data** needs the country's samples. The Farmer Registry's sample farmers are Master Data's sample people, so it needs **Load Sample People**. The Agents Registry's sample agents are the pack's `samples/agents.json`, taken from openg2p-data when the image is built; Master Data must know their areas. The Crop Sown Registry's two sample clusters are in Ethiopian districts, so they need the `ETH` pack.
* **Load sample crop seasons** (Crop Sown Registry) needs Master Data's sample people; **Load sample trainings** (Agents Registry) needs the sample agents.
* **Load Sample Images** needs **Load Sample Data**.
* **Sanity - Run Full E2E** needs **Load Sample Data**: its test user is added as an approver to the sample approval policies.
* **The mock identity system** has test identities only when Master Data holds sample people.

### No fallback

The Farmer, Crop Sown and Agents Registries' sample loaders do not fall back. One that cannot load the country's samples (no Master Data, no sample people, or areas Master Data does not know) stops db-seed with the reason, and the release fails. It never loads other people instead, because records in places the country does not have are worse than none. Either load the samples the loader needs, or turn **Load Sample Data** off.

### Which packs have samples

| Pack               | Sample people                | Sample agents | With Load Sample Data                    |
| ------------------ | ---------------------------- | ------------- | ---------------------------------------- |
| `ETH`              | 21 individuals, 6 households | 24            | Every registry loads its samples         |
| `XKM` (fictitious) | None                         | None          | db-seed stops: keep Load Sample Data off |

The packs are in [openg2p-data](https://github.com/OpenG2P/openg2p-data), under `packs/<country>/samples/`. What else a pack holds: [Country Packs](../../../../platform/platform-services/master-data-service/country-packs.md).

## Bulk data is generated by each registry

Dashboards and maps need volume to be worth looking at. That volume is **not** in the country pack: each registry generates its own at install.

Nobody reads a single bulk row, so its names and numbers need not belong to the country. Only two things must be right, and both come from MDS:

* **Geography**: every record points at a real unit (a P-code MDS holds), or maps and drill-downs break.
* **Datasets**: every coded value is one MDS holds.

So one generator serves every country for a given registry. The generator fails rather than writing records that point nowhere if MDS holds no geography.

Turning bulk data off does **not** remove the reporting views: they are built from the registry's schema, not its data, so they exist and return nothing until real registration starts. See [Setting up reporting](../../../../platform/platform-services/reporting-and-analytics/setting-up-reporting.md).

## The platform ships machinery, not data

The reference registry is deliberately minimal. The platform's `db-seed` image carries the **loaders and the ordering**, and a copy of openg2p-data taken when it is built (a registry's loader can read a pack's sample files or the sample photos from it). It carries no sample loader, no bulk generator and no country content of its own.

| In the platform image | What it is                                                                                 |
| --------------------- | ------------------------------------------------------------------------------------------ |
| `entrypoint.sh`       | Runs the ordered steps, entirely from environment variables                                |
| `mds_client.py`       | Small client for the Master Data API, used by seed scripts that need geography or datasets |
| `upload_templates.py` | Jinja templates → object store (Garage). Always run; an image without templates skips it   |

There is deliberately **no `load_sample_data.py` and no bulk generator in the platform**. The platform owns the _hook_ and the _order_; each registry variant ships its own loader, because sample and bulk data write that variant's own tables. A bare platform install therefore has no sample data at all.

{% hint style="info" %}
Bulk generators are **not shared** between registries for the same reason: a generator writes its registry's own extension tables and has to move in lockstep with that registry's reporting views. Each registry keeps its own copy.
{% endhint %}

## What lives in the platform, and what does not

The platform is machinery only. Everything that produces or presents _data_ lives in the individual registry:

|                                         | Registry Platform                             | NSR / Farmer Registry                                       |
| --------------------------------------- | --------------------------------------------- | ----------------------------------------------------------- |
| Seeding machinery, hook order, switches | **yes**                                       | inherited                                                   |
| Datasets                                | **none** — read live from Master Data         | **none** — read live from Master Data                       |
| Sample-data loader                      | **none**                                      | **its own**                                                 |
| Sample content (the domain overlay)     | **none**                                      | **its own**                                                 |
| Bulk data generator                     | **none**                                      | **its own**                                                 |
| Reporting views                         | the generator (`generate_reporting_views.py`) | its declaration (`reporting.yaml`) and any hand-written SQL |
| Superset dashboards                     | **none**                                      | **its own** (bundle + import job)                           |
| `analytics.*` chart values              | **not defined**                               | **defined**                                                 |

So a bare platform install creates no sample data, no bulk data, no reporting views and no dashboards. Each registry defines all four, because each writes its own tables and its dashboards read its own views.

## Datasets

### Where they are defined

In the **country pack**, and nowhere else. A pack in [openg2p-data](https://github.com/openg2p/openg2p-data) carries its lists as JSON — the core lists under `packs/<country>/codelists/`, and lists that only some registries need under `packs/<country>/domains/<domain>/` (for example `domains/agriculture/` for a Farmer Registry). MDS's own seed Job loads them into its `g2p_attributes` and `g2p_attribute_values` when it installs.

A registry extension ships **no** dataset SQL, and the registry keeps no copy of the lists: there is no dataset table in the registry database.

### How a registry uses them

A coded field names its list in the section UI metadata. Its dropdown asks MDS for the options each time the form is opened:

```json
"widget-data-source": {
  "type": "api", "method": "POST",
  "service": "attributes", "endpoint": "values",
  "params": { "attribute_id": "GENDER" },
  "labelKey": "value_display", "valueKey": "value_id"
}
```

The stored value is the list's `value_id` — the code, such as `FEMALE`. So everything else that writes that field — the sample and bulk loaders, inbound DCI templates, enums in the extension's schemas — must use **the pack's codes**.

{% hint style="warning" %}
**Domain lists load only when asked for.** A list under `domains/<domain>/` reaches MDS only if that domain is named in **Dataset Themes** (`masterData.geoSeed.domains`) on the commons-services form. The Farmer Registry and the Crop Sown Registry need `agriculture`, which is the commons-services default; without it a field such as `SOURCE_OF_INCOME` shows an **empty dropdown**, with no error anywhere. A social registry can clear the field. A pack that lacks a requested domain skips it, with a warning in the Master Data seed Job's log.
{% endhint %}

### Enforcing them on writes

Off by default. With `registry_core_validate_attribute_values` on, change requests and intake-form submissions are rejected when a coded field holds a value that is not in its MDS list. The fields checked are exactly those whose widget declares an `attribute_id`, so the check follows the UI metadata with no separate mapping.

Turn it on only once the data is clean: a record whose stored code is not in the pack — for example one written by an older loader — can no longer be saved until that field is corrected.

| Switch                                    | Where                                                                | Default                           | Effect                                                    |
| ----------------------------------------- | -------------------------------------------------------------------- | --------------------------------- | --------------------------------------------------------- |
| `geoSeed.load.codelists`                  | `openg2p-master-data` chart                                          | `true`                            | MDS loads the pack's core lists                           |
| `geoSeed.domains`                         | `openg2p-master-data` chart (**Dataset Themes** on commons-services) | `agriculture` on commons-services | MDS also loads these domain lists                         |
| `registry_core_validate_attribute_values` | registry API config                                                  | `false`                           | Registry rejects writes whose coded values are not in MDS |

## The seeding switches

All of these live under `registry.dbSeed.*` in a variant chart (`dbSeed.*` in the platform chart itself).

| Switch           | Platform default | What it does                                                                                               |
| ---------------- | ---------------- | ---------------------------------------------------------------------------------------------------------- |
| `enabled`        | `true`           | Run the db-seed Job at all. Meta-data SQL is applied unconditionally when on                               |
| `loadSampleData` | `false`          | Load the registry's sample data: its sample records, the sample approval policies and the demo staff users |
| `loadImages`     | `false`          | Sample profile photos — requires `loadSampleData`                                                          |

{% hint style="info" %}
Removed from the platform: `loadGeoData` (a legacy loader that wrote a second hierarchy into MDS) and `syncGeoWidgets` (the "Match Geo Dropdowns to Country" question). An older values file that still sets them can drop them; they have no effect.
{% endhint %}

{% hint style="warning" %}
These are `registry.dbSeed.*`, **not** `global.*`. The db-seed Job reads `.Values.dbSeed.load*` and there is no global fallback, so setting them under `global` silently does nothing.
{% endhint %}

### Seeding never touches Master Data's database

Seeding writes only the registry's own database. A seed script that needs geography or datasets — a sample loader, a bulk generator, the reporting-view generator — reads them from the MDS API through `mds_client.py`, with a client-credentials token from the `<release>-staff-portal` Keycloak client:

| Env                                   | What it is                               |
| ------------------------------------- | ---------------------------------------- |
| `MDS_API_URL`                         | Master Data API base URL                 |
| `MDS_TOKEN_URL`                       | Keycloak token endpoint                  |
| `MDS_CLIENT_ID` / `MDS_CLIENT_SECRET` | The client the seed Job authenticates as |

That client needs read access to MDS `/catalogue` (and `/samples` when sample data is loaded). The client also has a small CLI — `levels` prints the hierarchy levels, `wait-geo` blocks until MDS holds geography — for use in entrypoints. Registry charts render the MDS database credentials (`masterDataDB*`) only when `masterDataReadMode` is set to `db`, a rollback mode; the default is `api`.

### Geo dropdowns follow the country at runtime

A register's geo field is a `geo-hierarchy` widget with no levels of its own: when the form loads, the staff portal asks MDS for the country's levels (through its `/api/master-data/geo-levels` route, which proxies MDS `/catalogue/get_geo_levels`) and draws one dropdown per level, with MDS's level names. A four-level country gets four dropdowns with no extension change and no seed step. An older `widget-geo-config` widget without levels is treated the same way.

## Configuring from Rancher

A domain registry's Rancher form is generated from the platform chart's questions, with platform paths prefixed `registry.`. How that works: [Domain registry charts](packaging-and-reference-registry.md#domain-registry-charts).

{% hint style="info" %}
**Object store.** Registries store documents, images and templates in the commons **Garage** (S3-compatible; it replaced MinIO), reached in-cluster. The chart values keep their `minio*` names: `global.minioHost` defaults to `commons-garage:3900` and `global.minioSecure` to `false`; credentials come from the `commons-minio` Secret written by the Garage init job. The buckets `default`, `templates`, `documents`, `import-files` and `export-files` must exist (the commons Garage init job creates them). Pre-signed document URLs are signed for this in-cluster host.
{% endhint %}

So in the Rancher form these appear under the **DB Seed** group:

| Form field         | Variable                         |
| ------------------ | -------------------------------- |
| Enable DB Seed     | `registry.dbSeed.enabled`        |
| Load Sample Data   | `registry.dbSeed.loadSampleData` |
| Load Sample Images | `registry.dbSeed.loadImages`     |

and under **Sanity**: `registry.sanity.enabled`, `registry.sanity.runE2e`, `registry.sanity.failOnError`.

{% hint style="warning" %}
**Bulk data is a variant-level switch.** `analytics.*` is defined by each registry chart, not the platform, so it appears in the Rancher form only where the variant adds it to its own questions. The Farmer Registry does — **Analytics → Generate bulk demo data**, off by default. Where a variant does not, set `analytics.bulkSample.enabled` in values — for example in the YAML editor Rancher offers alongside the form.
{% endhint %}

## An empty install, for production

A production registry should carry no demonstration data of any kind:

```yaml
registry:
  dbSeed:
    enabled: true          # meta-data SQL is REQUIRED
    loadSampleData: false
    loadImages: false
  sanity:
    enabled: true          # smoke only; creates nothing
    runE2e: false          # e2e SEEDS fixtures and leaves them behind

analytics:
  bulkSample:
    enabled: false
```

{% hint style="danger" %}
**Do not turn off `dbSeed.enabled`.** The meta-data SQL defines the register itself — without it there is no registry. It also uploads the Jinja templates to the object store, without which every record fails to render and a DCI search returns an empty result. There is no switch for the templates: db-seed uploads the ones the image ships. Registry Platform versions up to `0.0.0-develop.847` had a **Load Templates to Object Store** switch (`dbSeed.loadTemplates`); on them, keep it on for a registry that ships templates.

The same goes for **datasets on the Master Data side**: they are configuration, not demo data. Keep `geoSeed.load.codelists: true` (and any `geoSeed.domains` your registries need) in production — only `geoSeed.load.samples` is demo data.
{% endhint %}

On **commons-services**, turn **Load Sample People** off, and **Install Mock Identity System?** off once eSignet uses the real national ID system. Change the `admin` user's password at first login. Every switch: [Configuration or sample](country-data-and-seeding.md#configuration-or-sample-every-switch).

`sanity.enabled: true` is safe in production: with `runE2e: false` the suite is smoke-only — it checks that the Partner API is live and the DCI route is served, and creates nothing. It is `runE2e: true` that seeds fixtures, and those are **never cleaned up**.

## The reporting layer

Seeding puts data _in_; reporting is how it comes back out, and the platform ships the machinery for that too.

`generate_reporting_views.py` lives in this platform's **db-seed image**, beside the other seeding machinery, and follows the same principle: the platform supplies the mechanism, the registry supplies what is specific to it.

At install it reads the registry's own schema and the country's geography from the Master Data API, and creates a view per entity — geography inherited from the parent, workflow columns carried, personal data withheld and then verified absent. A registry that declares nothing still gets a complete reporting layer.

What each registry supplies is a short `reporting.yaml`: which entity hangs off which, what its columns _mean_, and which views it maintains by hand.

{% hint style="info" %}
**Why generated rather than written.** Each registry used to hand-write its reporting SQL, so coverage was whatever somebody thought of, and the geographic unpacking — identical in intent everywhere — had already drifted between two registries. See [Reporting views](../../../../platform/platform-services/reporting-and-analytics/reporting-views.md).
{% endhint %}

Everything about the reporting layer — the declaration, dashboards, the map drill-down, and what to do when a country pack or a schema changes — is under [**Reporting & Analytics**](../../../../platform/platform-services/reporting-and-analytics/).

## What runs, in what order

The chart runs db-seed as a `post-install,post-upgrade` hook Job:

| # | Step                                                                                         | Controlled by                                                       |
| - | -------------------------------------------------------------------------------------------- | ------------------------------------------------------------------- |
| 1 | **meta-data SQL** → registry DB — register definitions, UI metadata                          | _always, when `enabled`_                                            |
| 2 | **sample data**: the demo staff users → Keycloak, then the sample records → `g2p_register_*` | `loadSampleData`                                                    |
| 3 | **images** → object store                                                                    | `loadImages`                                                        |
| 4 | **templates** → object store                                                                 | _always; skipped when the image ships none_                         |
| 5 | **AWE seed** → AWE DB: the callback secret; the sample approval policies                     | callback secret _always, when AWE is on_; policies `loadSampleData` |

### Approval policies and demo staff

Who approves is decided by each country, so neither ships as configuration:

* **Always seeded:** the binding of the registry's intake forms and change requests to AWE policy keys (e.g. `registry.change_request.farmer`, in the registry's `awe-integration` meta-data), and the AWE callback secret.
* **Only with Load Sample Data:** the registry's approval policies (`awe_meta_data/*.sql`: policies, stages and approver rules) and the demo staff users they name (`alex.carter`, `nina.patel` and others, `dbSeed.sampleStaffUsers`). The demo users get the initial password **AWE Approver User Password** (`global.aweApproverUserPassword`, default `pass`), changed at first login. The value is kept only in the release's Helm values (Rancher's **Edit YAML**, or `helm get values <release> -a`); Keycloak keeps only its hash. The `staff` realm is shared by the registries of a namespace, so a demo user that already exists, e.g. from another registry's sample data, is left as it is, with its own password.
* **In production:** set the policies up in AWE's admin portal under the same policy keys, with the country's stages and approvers, preferably by role. Create staff users in Keycloak. The seed never changes an existing policy or user.
* **Before the policies exist,** a new submission or change request is refused with AWE's error `No active policy for '<policy key>'`, and nothing is saved.

Registry Platform versions up to `0.0.0-develop.847` loaded the policies on every install and created the demo users through keycloak-init; a change request whose policy was missing was saved without reaching an approver.

Datasets and geo dropdowns are not steps here: the registry does not load them. MDS's own seed Job loads them from the pack, so — like the geography — they must be in MDS **before** the registry is installed, or seeded records carry codes no dropdown can show.

Across services, the order is:

1. MDS loads the pack: geography, datasets, sample people.
2. The registry's db-seed waits until MDS holds geography (`mds_client.py wait-geo`), then loads the sample people. It copies no datasets.
3. With `registry_core_validate_attribute_values` on, writes are checked against MDS.
4. The bulk Job generates records, reading the hierarchy from MDS.

Bulk generation and the sanity suite are separate Jobs at later hook weights, so a failure in one does not silently skip the others — but note that Helm stops at a failed hook, so a failing seed step does block everything after it.

See also [Meta Data Seeding](../design/meta-data-seeding.md) for the platform-level metadata framework.
