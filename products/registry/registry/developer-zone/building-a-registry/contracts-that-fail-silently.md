---
description: >-
  The names that must match across files the platform never type-checks — and
  exactly what breaks when they do not.
---

# Contracts that fail silently

Most of what a registry does at runtime is driven by **names matching across
files that never import one another**: an ORM column, a JSON string in seed SQL,
a Jinja key, a Helm value. Nothing type-checks them.

When they match, everything works. When they do not, **nothing raises**. A field
renders blank. A dropdown has no options. A shared record comes back `{}`. An
ingested record arrives with its tables empty. No exception, no 5xx, no failed
deploy.

This page is the complete list, the symptom of each, and the check that catches
it before you ship.

{% hint style="info" %}
**Working this way.** Every rule below is stated as *contract → symptom when
broken → automated check*. The checks need no cluster and no database: they read
the repository. Add them in Phase 1 step 3, before you write the metadata, and
they will catch these mistakes on the first `pytest` rather than in a sandbox
three days later.
{% endhint %}

## 1. A field name is a four-way contract

One column is named in four places, and all four must agree:

| Where | Named as |
|---|---|
| `register_domain/models/<x>.py` | the SQLAlchemy column |
| `meta_data/register-metadata/g2p_register_sections.sql` | `widget-data-path` (last segment) or `column-key` |
| `templates/*.json.j2` | the key read from or written to the record |
| `docker/db-seed/reporting_views.sql` | the column selected |

**Symptom:** a widget bound to a column that does not exist is a permanently
blank field which accepts no input. A template reading a missing key emits `""`.
A reporting view referencing one fails at refresh — inside a CronJob nobody is
watching.

**Check:** parse the section JSON out of the seed SQL, parse the column names out
of the model files with `ast` (do **not** import them — that needs the whole
platform installed), and assert every `widget-data-path` leaf and every
`column-key` resolves to a real column.

## 2. Child registers arrive under `snake_case(mnemonic)`

An outbound template receives the master record with each child register's rows
attached. The key is the snake_case of the **register mnemonic**, produced by
`_to_snake_case()` in `g2p_register_hierarchical_service.py`:

| Register mnemonic | Key in the template |
|---|---|
| `IndividualDisability` | `individual_disability` |
| `AssistiveTechnology` | `assistive_technology` |
| `HouseholdHousingAndServices` | `household_housing_and_services` |

It does **not** singularise or pluralise — it only splits CamelCase and lowers.

**Symptom:** `{%- for row in expanded.get('assistive_technologies') -%}` iterates
nothing. The record renders with empty arrays and a `200` response.

## 3. Inbound template keys are **section mnemonics**

The least obvious rule in the platform, and the most expensive to debug.

An inbound template emits a JSON document that the ingestion pipeline applies to
the registry. Its keys are:

* for the **master register** — bare column names (`first_name`, `gender`);
* for **everything else** — the `section_mnemonic` from `g2p_register_sections`
  of the section that owns those fields. **Not** the table name, **not** the
  register mnemonic, **not** the field group.

```jsonc
{
  "first_name": "Amina",           // master register column
  "gender": "FEMALE",
  "individual_identifier": [ … ],  // section_mnemonic, even for a 0..1 group
  "individual_disabilities": [ … ] // section_mnemonic of the list section
}
```

**Symptom:** a key matching no section mnemonic is **dropped**. This is the usual
reason an ingested record lands with correct demographics and every detail table
empty.

## 4. Outbound top-level keys are the consent scopes

Consent clamping is a strict allow-list over the **top-level keys of the rendered
record**. There is no sub-field granularity — a scope carries everything nested
under it.

So the top-level keys of `<domain>_to_dci.json.j2` *are* your registry's scope
vocabulary. Renaming one silently revokes access for every partner consented to
the old name.

**Symptom:** a configured scope that names no top-level key matches nothing, and
every record is clamped to `{}` — the partner receives HTTP `200` with an empty
record, and no error appears anywhere in the chain.

**Check:** assert every scope named in `registry.sanity.dataScopes` and
`deniedScopes` appears as a top-level key of the outbound template.

## 5. The sanity suite's chart values

`fixtures.py` is a contract on the Python side, and Phase 1 step 6 says so. The
**chart** side has its own, and three of the keys are actively misleading:

| Key | Type | Note |
|---|---|---|
| `registry.sanity.farmerRegisterId` | string | **This is the register id**, whatever your registry is about. Named for the registry the harness was first written against; the subchart helpers, the suite's `cfg` object and every variant's override use this spelling. Leave it unset and the suite runs against the reference registry's id |
| `registry.sanity.dataScopes` | **comma-separated string** | Not a YAML list. A list renders into the env var as Go map syntax |
| `registry.sanity.deniedScopes` | **comma-separated string** | Same. Must name real scopes your template emits, or the clamping test asserts nothing |
| `registry.sanity.regType` | string | Your register mnemonic — goes into the DCI envelope as `reg_type` |
| `registry.sanity.regRecordType` | string | The DCI record type |
| `registry.sanity.crTabId` / `crSectionId` | string | A real, **editable** section of yours, or the change-request test's write is rejected |
| `registry.sanity.searchText` | string | The injected record's `functional_record_id`. Must equal what `data_seed.py` writes |

**Symptom:** left at the defaults, these are the *reference registry's* values.
The suite passes or fails for reasons that have nothing to do with your registry.

**Check:** after `helm template`, grep the rendered output for
`SANITY_FARMER_REGISTER_ID` and `SANITY_DCI_REG_TYPE` and assert they carry your
values — a mistyped values key renders happily with the subchart default.

## 6. Raw SQL does not get `search_text`

`G2PRegister.__declare_last__` registers `before_insert` / `before_update`
listeners that rebuild `search_text` and `record_name` from your domain service.

**They fire for ORM writes only.** Anything writing raw SQL — your
`load_sample_data.py`, the sanity `data_seed.py`, a bulk import — must build
`search_text` itself.

**Symptom:** the records exist and are unfindable. The DCI search is
`search_text ILIKE '%…%'`, so the partner API answers `200` with nothing in it,
and the staff-portal search returns nothing.

The same applies to `G2PGeo.geo_lowest_level_value_id`, whose `@validates` hook
builds `geo_code_hierarchy_json` — see §8.

## 7. Seed SQL runs with `ON_ERROR_STOP=0`

The db-seed entrypoint runs each file as:

```sh
psql -v ON_ERROR_STOP=0 -f "$f"
```

so an error **aborts that file and lets the Job exit `0`**.

**Symptom:** on the second install a duplicate-key error stops the rest of that
file, and the upgrade is reported as successful with the metadata partially
applied. Screens that existed before the upgrade quietly stop appearing.

**Check:** grep every `.sql` under `meta_data/` for an `INSERT INTO` with no
`ON CONFLICT`.

`awe_meta_data/` needs a different clause — untargeted `ON CONFLICT DO NOTHING`
plus a `WHERE EXISTS` filter on the parent row, because AWE's database is shared
across registries. See [Concepts → Database scripts](concepts/README.md#database-scripts).

## 8. Geography must be resolved, not computed

The shared demography set carries geography as **names**
(country / region / district / …). The registry stores an id, plus the resolved
hierarchy in `geo_code_hierarchy_json` — and the reporting views unpack that
JSONB **positionally** into `geo_1..geo_5`, which is what every map and every
geo-grouped chart groups by.

Two traps, both silent:

* the `@validates` hook that normally builds the hierarchy is **ORM-only** and
  does not fire for raw SQL;
* a slug-path computed from the names matches nothing when Master Data was seeded
  from a country pack, whose ids are **P-codes**.

**Symptom:** the names still read correctly on the record, so the data looks
fine. The only symptom is that every map and every geo chart is empty.

**Fix:** resolve the name chain against `g2p_geo_level_values` in Master Data by
walking parent links (a village name repeats under different wards), and write
both `geo_lowest_level_value_id` and `geo_code_hierarchy_json` explicitly.

{% hint style="info" %}
The demography CSV is **not uniformly JSON in its JSON columns** —
`phone_numbers` holds a serialised list of objects, `emails` holds a bare
address. A `json.loads` over both raises and takes the whole load down.
{% endhint %}

## 9. Code lists and enums must agree

A dropdown's options come from `g2p_attribute_values`; the column behind it is
constrained by a Python enum in `models/enums.py`.

| Divergence | Symptom |
|---|---|
| value in the code list, not in the enum | the field **refuses to save** |
| value in the enum, not in the code list | the field is **unreachable from the UI** |

Neither logs anything.

**Fix:** rather than maintaining both, **generate the code list from the enum**
and fail CI when the checked-in SQL is stale.

The same argument applies to **translations**: every `widget-label` and
`section-title` in your section JSON is a translation key, and a key with no
entry renders as the raw key — `assistive_technology_type` instead of "Assistive
Technology Type". Nothing errors; the screen just looks unfinished.

{% hint style="warning" %}
**`translation/domain.json` is read by nothing.** The reference registries carry
this file, but no script, CI job, Dockerfile or chart template references it. The
values reach the database only as `registry_languages.domain_translation`, a JSON
literal inside `meta_data/registry-configurations/g2p_registry_languages.sql`,
and keeping the two identical is manual. Editing `domain.json` alone changes
nothing.
{% endhint %}

## 10. The AWE policy key is a string join across two databases

Your registry binds a register to a policy by `policy_key` in
`meta_data/awe-integration/`; AWE creates the policy under that key in
`awe_meta_data/10_approval_policy.sql`. They are matched as **strings**, in
different databases.

**Symptom:** change requests are raised and never routed for approval. They sit
pending forever, with nothing to explain why.

**Check:** extract the keys from both files and assert the bound set is a subset
of the created set.

## 11. Platform table shapes

When your loader or fixture writes to a platform table, these are the details
that are not guessable:

| Table | The trap |
|---|---|
| `g2p_completion_score_computation_queue` | Keyed per **(record, section)**, not per record. `compute_status` and `compute_number_of_attempts` are `NOT NULL`. One row per record leaves every section but one uncomputed |
| `g2p_register_scores` | `triggered_by_cr_id` is **`NOT NULL`** — and not a foreign key, so a marker such as `'seed'` is fine. The unique index is on `(link_internal_record_id, score_type)`, so that is the `ON CONFLICT` target, not the primary key |
| register tables | The image column is `record_image_document_id`. Some older seeded UI JSON says `record_image_storage_id`, which binds to nothing |
| `g2p_register_definitions` | `register_purpose` is `REGISTER`, `PROGRAM_REGISTER`, `TABLE` or `CORE_TABLE` — see [G2PRegisterDefinition](concepts/registry-and-register-metadata/g2pregisterdefinition.md) |

Two habits that make this class of problem self-limiting:

* **Read the target table's columns from `information_schema` at run time**
  rather than hard-coding a list. A column renamed upstream then degrades to a
  clear error instead of a silently skipped insert.
* **Wrap optional inserts in a `SAVEPOINT`.** Without one, a failed statement
  poisons the surrounding transaction and the final `COMMIT` rolls back
  everything the loader did.

## The check suite

None of these need a cluster, a database or credentials — they read the
repository, and they run in well under a second. Add them as
`test/test_metadata_consistency.py` alongside the inherited pin guard, and wire
them into CI on every push:

| Check | Catches |
|---|---|
| every `widget-data-path` names a real column | §1 |
| every table `column-key` names a real column | §1 |
| every dropdown `attribute_id` has a code list | §9 |
| generated code lists match the enums | §9 |
| generated translations cover every UI key | §9 |
| every section is reachable from a tab | invisible sections |
| tab-sections reference existing tabs and sections | dangling references |
| register ids are consistent across metadata files | typo'd frozen UUIDs |
| consent scopes exist in the outbound template | §4 |
| AWE policy keys match between registry and AWE seeds | §10 |
| every seed `INSERT` has `ON CONFLICT` | §7 |
| templates referenced by metadata exist on disk | missing template |
| the `RP_VERSION` pin is identical everywhere | image/chart drift |
| every Dockerfile declares a pin | a floating base image |

{% hint style="success" %}
The sanity suite proves a **deployed** registry works, and needs a cluster,
commons-services and Keycloak admin. These prove the **repository** is coherent,
and they do it before anything is published. You want both.
{% endhint %}
