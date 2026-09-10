---
description: >-
  The vocabulary and the moving parts of a registry — what a register is, what
  you inherit, what the metadata does, and what the extension must provide.
---

# Concepts

This section is the **why**. It explains the pieces a registry is made of, so
that the instructions in
[Phase 1 — Build your registry](../build-your-registry.md) read as decisions
rather than incantations.

Read it once before you start, and keep
[Anatomy of an extension](../anatomy-of-an-extension.md) open while you build.

## Where to start

| Page | Answers |
|---|---|
| [Registry vs Register](registry-vs-register.md) | Is this thing a register, a sub-register, or a field? |
| [Base Models](base-models.md) | What do I inherit, and what must I declare myself? |
| [Register Metadata](registry-and-register-metadata/README.md) | Which table drives which part of the screen? |
| [Registry Configuration](registry-configuration/README.md) | Where do registry-wide settings live? |
| [Registry Extensions](registry-extensions/README.md) | What exactly must my package expose for the platform to load it? |
| [Contracts that fail silently](../contracts-that-fail-silently.md) | Which names must match across files — and what breaks when they do not? |

## Organisation of repositories

Three repositories, and the boundary between them is the whole design.

| Repository | Publishes | You |
|---|---|---|
| [`registry-platform`](https://github.com/OpenG2P/registry-platform) | The runnable images (`staff-api`, `partner-api`, `celery`, `db-seed`, `sanity-tests`, `staff-ui`, `bene-api`) and the `openg2p-registry` Helm chart | **Consume.** Never fork |
| [`openg2p/packaging`](https://gitlab.com/openg2p/packaging) | The shared CI — versioning, build, chart publish | **Include.** Never copy |
| `<domain>-registry` | Your five thin images and one wrapper chart | **Own** |

Your repository holds one Python package (the domain), five ~10-line
Dockerfiles, a values overlay over the platform chart, and a handful of tests.
Everything else is inherited. If you find yourself copying platform code,
templates or CI into your repository, stop — that is the pre-1.0 model.

The platform also ships a **reference extension**
(`registry-platform/reference-extension`), which is both the thing you copy to
start and the thing that keeps running if `REGISTRY_EXTENSION_MODULE` is unset.
It is a working registry in its own right, so it is the fastest way to see any
convention in context.

## Base ORM models

Every table a registry stores is composed from abstract SQLAlchemy mixins in
`openg2p_registry_core.models`. You inherit their columns rather than declaring
them.

| Mixin | Use it for |
|---|---|
| `G2PRegister` | Every register and sub-register table |
| `G2PPerson` | A register whose subject is a person |
| `G2PGeo` | A register that is located somewhere |
| `G2PGeoShape` | A register with a boundary (a land parcel) |
| `G2PTable` | A pure child table with no register semantics |
| `G2PProgramRegister` | A programme-enrolment register, keyed on `foundational_id` |

Each register needs **three** tables — the live record, its history twin, and
its intake-form twin — and all three must carry the same domain columns. Declare
those columns once, on a plain mixin, and compose all three from it. A column
added to only the live table makes approval fail when it copies the record into
history.

Full field-by-field reference: [Base Models](base-models.md).

## Base Pydantic model

The API layer mirrors the ORM one-for-one, from `openg2p_registry_core.schemas`:
`G2PRegisterBaseSchema`, `G2PPersonSchema`, `G2PGeoSchema`,
`G2PRegisterHistorySchema`, `G2PIntakeFormSchemaBase`.

Same shape as the models — a plain mixin holding the domain fields, then three
classes composing it with the bases. **Field names must match the ORM column
names exactly.** The schema is what the staff portal and the partner API
serialise; a name that differs produces a field the UI can display and never
save.

## Register metadata

The metadata **is** the registry. The Python package defines what *can* be
stored; the seed SQL in `meta_data/` decides which registers exist, what their
screens look like, which dropdowns have which options, and who must approve a
change. A registry installed with migrations but no metadata has tables and no
screens.

That is what makes the platform metadata-driven: adding a field to an existing
register is a seed-SQL change, not a release of the platform.

Each table is documented under
[Register Metadata](registry-and-register-metadata/README.md).

## Database scripts

Three different kinds of SQL, often confused. They run at different times, in
different databases, with different rules.

| Kind | Lives in | Runs | Must be idempotent? |
|---|---|---|---|
| **Migrations** | `app.py` → `create_migrate()` per ORM class | API container start | Yes — `CREATE TABLE IF NOT EXISTS`, handled for you |
| **Seed SQL** | `meta_data/` | The db-seed Job, on **every** install and upgrade | **Yes — and it is on you** |
| **AWE seed SQL** | `awe_meta_data/` | The db-seed Job, against the **AWE** database | Yes, and defensively — see below |
| **Sample data** | `docker/db-seed/load_sample_data.py` | The db-seed Job, only when `loadSampleData=true` | Yes |

Three rules follow from that table:

1. **Migrations create structure and never carry content.** Anything a registry
   needs in order to *be* that registry belongs in `meta_data/`, which is why
   `dbSeed.enabled` stays `true` in production while every demo switch goes off.
2. **Every `INSERT` in `meta_data/` needs an `ON CONFLICT` clause.** The seed
   re-runs on each upgrade, and the entrypoint runs `psql` with
   `ON_ERROR_STOP=0` — so a duplicate-key error aborts that file and the job
   still exits `0`. The upgrade is reported as successful with the metadata
   half-applied.
3. **`awe_meta_data/` targets a shared database.** AWE is one deployment serving
   every registry in the environment, so another registry may already own the
   same `policy_key` under a different id. Use untargeted
   `ON CONFLICT DO NOTHING`, and filter child rows on the existence of their
   parent — a clause targeting `("id")` leaves that natural-key clash unguarded,
   and one colliding row aborts every policy in the statement.

## The extensions contract

The platform imports your domain model under the fixed name
`openg2p_registry_extensions`. Your package is **not installed** under that
name — it installs under its own, and the container entrypoint aliases the
module named by `REGISTRY_EXTENSION_MODULE` into `sys.modules` before any
platform import runs.

That indirection is what lets your extension and the platform's reference
extension coexist in one image, selected by an environment variable.

Exact class names, required methods and package-level requirements:
[Extensions Contract](registry-extensions/extensions-contract.md).
