---
description: >-
  Every folder in a registry extension repository and what belongs in it —
  the reference to keep open while building.
---

# Anatomy of an extension

A registry is one repository. This page is the map: what each folder is for, and
what you must put in it. It is a **reference**, not a sequence — the order to do
things in is [Phase 1](build-your-registry.md).

Everything here is real: the paths match the
[Farmer Registry](https://gitlab.com/openg2p/registry/farmer-registry) and the
[National Social Registry](https://gitlab.com/openg2p/registry/national-social-registry)
as they are built today.

## The repository

```
<domain>-registry/
├── <domain>-extension/     ← the Python package: your domain (see below)
├── docker/                 ← thin Dockerfiles + the content your images carry
├── helm/openg2p-<domain>/  ← your Helm chart (wraps the platform chart)
├── test/                   ← your field-specific sanity tests + the pin guard
├── scripts/                ← bump-rp-version.sh, uninstall-registry.sh
└── .gitlab-ci.yml          ← ~40 lines; all logic lives in openg2p/packaging
```

| Folder | You own | Notes |
|---|---|---|
| `<domain>-extension/` | **All of it** | The only place your domain logic lives |
| `docker/` | The `FROM` line and what you copy in | Each Dockerfile is ~10 lines. See [Phase 1 § images](build-your-registry.md#4-build-thin-images) |
| `helm/openg2p-<domain>/` | A values overlay, plus any templates for things the platform has no concept of (analytics jobs, dashboards, maps) | Everything else comes from the pinned platform subchart |
| `test/` | Your **Set 2** field tests only | The harness and generic tests are inherited. See [Testing & the sanity suite](../../deployment-and-extension/testing-and-sanity-suite.md) |
| `scripts/bump-rp-version.sh` | Nothing — copy it | Moves the platform pin in the Dockerfiles and chart together |

## The extension package

```
<domain>-extension/
├── pyproject.toml
└── src/openg2p_registry_<domain>_extension/
    ├── __init__.py            ← version string
    ├── app.py                 ← wires the extension into the platform app
    ├── config.py              ← extension settings
    ├── register_domain/       ← the domain model  (REQUIRED)
    ├── meta_data/             ← seed SQL: registers, UI, code lists  (REQUIRED)
    ├── awe_meta_data/         ← approval-workflow seed SQL
    ├── templates/             ← DCI / message Jinja templates
    ├── score_compute/         ← optional: computed scores
    └── ingestion_pipeline/    ← optional: inbound enrichers
```

{% hint style="warning" %}
The package installs under **its own import name** and is selected at runtime by
`REGISTRY_EXTENSION_MODULE`. Do **not** alias it onto `openg2p_registry_extensions`
in `pyproject.toml` — that was the previous mechanism and it prevents your
extension from coexisting with the platform's reference extension in one image.
{% endhint %}

### `register_domain/` — the domain model

The heart of the extension. One set of files per register.

| Subfolder | Contains | Farmer Registry has |
|---|---|---|
| `models/` | SQLAlchemy ORM models — one file per register, plus `enums.py`. Each declares three tables: the register, its `history`, and its `intake_form` | 9 files |
| `schemas/` | Pydantic mirrors of the models, used by the APIs | 9 files |
| `services/` | `G2PRegisterDomainService{Mnemonic}` — the per-register behaviour the platform calls into | 10 files |
| `factory/` | `g2p_register_domain_factory.py` and `g2p_id_generator_factory.py` — resolve mnemonic → your classes. Copy and adjust the mapping | 2 files |
| `id_generator/` | Functional-ID generation, if your registers need it | 1 file |

The class names are a contract the platform resolves by **register mnemonic** —
see [Extensions contract](concepts/registry-extensions/extensions-contract.md)
for the exact names and methods, and [Base models](concepts/base-models.md) for
what you inherit.

### `meta_data/` — the seed SQL

Applied to the registry database at install, in sorted path order. This is what
turns your ORM tables into a working registry: registers, screens, code lists.

| Subfolder | What it defines |
|---|---|
| `register-metadata/` | The core: `g2p_register_definitions`, `_schemas`, `_sections`, UI tabs and tab-sections, intake-form equivalents, score definitions, documents. **Start here** |
| `lookup-data/` | Code lists — `g2p_attributes` and `g2p_attribute_values` (plus their `_defaults` variants) |
| `registry-configurations/` | Registry-wide settings: languages, themes, input mechanisms, VC configuration |
| `data-models/` | `data_models.sql` — the model definitions used by ingestion/outgestion |
| `registry-inbound-message-rules/` | Incoming templates, key paths, semantic patterns |
| `registry-outbound-messages-templates/` | Outgoing templates |
| `awe-integration/` | Binds registers to approval policies |

Each metadata table is documented under
[Concepts → Register Metadata](concepts/registry-and-register-metadata/README.md).

{% hint style="info" %}
**Code lists are not the same as country data.** The `_defaults` files are your
registry's fallback; a deployment's country pack can override them from Master
Data. See [Country data & seeding](../../deployment-and-extension/country-data-and-seeding.md).
{% endhint %}

### `awe_meta_data/` — approval workflow

Numbered so they apply in dependency order, and written to the **AWE** database
rather than the registry's:

```
10_approval_policy.sql      the policy
20_approval_stage.sql       its stages
30_approver_rule.sql        who approves each stage
40_callback_secret.sql.tpl  per-release HMAC secret (templated at seed time)
```

Background: [AWE integration](../../design/awe-integration.md).

### `templates/` — message rendering

Flat Jinja files, uploaded to MinIO by db-seed. Typically one per direction:

```
<domain>_to_dci.json.j2      outbound: your record → DCI
dci_to_<domain>.json.j2      inbound: DCI → your record
dci_commons_response.json.j2 shared response envelope
```

The **top-level keys your outbound template emits are the consent scopes** a
partner can be granted — get them right or clamping silently returns `{}`. See
[Partner APIs](../../design/partner-apis.md).

### `score_compute/` and `ingestion_pipeline/` — optional

* `score_compute/services/` — implementations of `G2PScoreComputeInterface`, bound
  to a register by seed metadata rather than code. See
  [Score computation framework](../../design/score-computation-framework.md).
* `ingestion_pipeline/enricher_services/` — enrichers that fill derived fields on
  inbound records. See [Ingestion pipeline](../../design/ingestion-pipeline.md).

Omit either folder entirely if you do not need it.

## What is *not* in the extension

A frequent source of confusion — these live in the repo but outside the package:

| Thing | Where it actually lives |
|---|---|
| Sample data (demo records) | `docker/db-seed/seed-data/*.json` |
| Sample-data loader, image uploader | `docker/db-seed/*.py` — only if the platform's is not shape-compatible |
| Reporting views, `reporting.yaml` | `docker/db-seed/` |
| Dashboards, maps | `docker/dashboards/`, `helm/openg2p-<domain>/files/` |
| Sanity field tests | `test/sanity/` |
