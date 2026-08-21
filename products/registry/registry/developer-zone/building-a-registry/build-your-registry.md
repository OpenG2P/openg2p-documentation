---
description: >-
  Phase 1 — from an empty repository to published images and a Helm chart for
  your own registry.
---

# Phase 1 — Build your registry

Eight steps, in order. No cluster is needed until step 8.

Keep [Anatomy of an extension](anatomy-of-an-extension.md) open alongside this —
it says what goes in each folder; this says what to do.

{% hint style="info" %}
**Copy, don't invent.** Start from
[`farmer-registry`](https://gitlab.com/openg2p/registry/farmer-registry) (two
registers, several sub-registers) or
[`national-social-registry`](https://gitlab.com/openg2p/registry/national-social-registry).
Every step below has a working example in both.
{% endhint %}

{% hint style="success" %}
**Every step ends with a `Done when` block.** It is a short list of commands that
exit non-zero on failure and touch nothing. Run them before moving on.

They exist so this page works two ways: a person reads the prose and uses the
block as a checklist; an automated agent can execute the blocks directly and
treat a non-zero exit as "this step is not finished". Substitute your slug for
`<domain>` throughout — it is the only variable in the page.
{% endhint %}

## 1. Decide your registers

Write this down before touching code — it drives everything after it.

1. **List your registers.** A register is a top-level entity a staff user searches
   for and raises change requests against (Farmer, Individual, Household). Things
   that only ever hang off a register — a land parcel, a crop — are
   **sub-registers**, not registers.
2. **Give each a mnemonic** — one CamelCase word (`Farmer`, `IndividualLand`). It
   becomes the class-name suffix and the DCI `reg_type`. Changing it later means
   touching code, SQL and templates.
3. **Freeze a UUID per register** now. Metadata rows reference each other by these.
4. **List the fields per register**, marking which are code lists (dropdowns) and
   which are free text.
5. **Decide which registers mint functional IDs.** Only those get
   `functional_id_generation_required = TRUE`, an ID pool in the chart
   (`registry.idgenerator.idGenerator.appConfig.idTypes.<mnemonic-lowercase>`)
   and a branch in `id_generator/`. Sub-registers reached through a parent
   normally need none of the three.

A single-register registry is a perfectly good shape — do not add a household
register because the worked examples have one. Unsure whether something is a
register: [Registry vs Register](concepts/registry-vs-register.md).

**Done when** you can fill in this table for your domain, because every later
step reads from it:

| Mnemonic | `register_purpose` | `master_register_id` | Mints functional IDs | Frozen UUID |
|---|---|---|---|---|
| `Farmer` | `REGISTER` | `NULL` | yes | `a0000000-…-0001` |
| `Land` | `TABLE` | the Farmer UUID | no | `b0000000-…-0010` |
| `Score` | `CORE_TABLE` | the master UUID | no | `c0000000-…-0001` |

## 2. Create the repository

```
<domain>-registry/
├── <domain>-extension/
├── docker/
├── helm/openg2p-<domain>/
├── test/
├── scripts/
└── .gitlab-ci.yml
```

Copy the reference extension from the platform as your starting point:

```bash
git clone https://gitlab.com/openg2p/registry/registry-platform
cp -r registry-platform/reference-extension <domain>-registry/<domain>-extension
```

Then rename the package to `openg2p_registry_<domain>_extension` — the directory
under `src/`, the `name` in `pyproject.toml`, and the `[tool.hatch.version]` path.

{% hint style="danger" %}
Do **not** add a `[tool.hatch.build.targets.wheel.sources]` alias onto
`openg2p_registry_extensions`. The package must install under its own name.

The factories are the exception and stay as they are: they import
`openg2p_registry_extensions...`, which the entrypoint aliases at startup. Copy
them unchanged. See
[Extensions Contract](concepts/registry-extensions/extensions-contract.md#the-module-alias-two-halves-that-look-contradictory).
{% endhint %}

{% hint style="warning" %}
Write `<domain>-extension/README.md` now. `pyproject.toml` declares
`readme = "README.md"`, and a missing file fails the **Docker build** in step 4
with `OSError: Readme file does not exist` — a long way from the cause.
{% endhint %}

**Everything derives from one slug.** `<domain>` is the repo name, the Python
package, the image names, the chart, the DB schema prefix and the Keycloak
clients — pick it once and use it verbatim everywhere. This is the OpenG2P naming
convention for any service; see
[Creating a New Platform Service](../../../../../platform/platform-services/creating-a-new-service.md)
for the full set of conventions a registry inherits.

**Done when:**

```bash
test -f <domain>-extension/pyproject.toml
test -f <domain>-extension/README.md          # required by pyproject
test -d <domain>-extension/src/openg2p_registry_<domain>_extension
! grep -q "wheel.sources" <domain>-extension/pyproject.toml   # no alias
grep -q "openg2p_registry_extensions" \
  <domain>-extension/src/openg2p_registry_<domain>_extension/register_domain/factory/*.py
```

## 3. Write the domain

In `src/openg2p_registry_<domain>_extension/`:

1. **`register_domain/models/`** — one file per register. Each declares the
   register table, its `history` twin and its `intake_form` twin, inheriting the
   platform base classes. Put enums in `enums.py`.
2. **`register_domain/schemas/`** — a Pydantic mirror per model.
3. **`register_domain/services/`** — `G2PRegisterDomainService{Mnemonic}` per
   register.
4. **`register_domain/factory/`** — map each mnemonic to your classes.
   Alongside it, `register_domain/id_generator/` returns the prefix/suffix for
   each register that mints functional IDs. It branches on the **lowercased
   mnemonic**, and those branches must match the ID pools you declare in the
   chart — see [Functional-ID pools](#functional-id-pools) in step 5.
5. **`meta_data/register-metadata/`** — the seed SQL, in this order: register
   definitions → sections → schemas → UI tabs → tab-sections → intake equivalents.
6. **`meta_data/lookup-data/`** — your code lists.
7. **`templates/`** — your DCI templates.
8. **`awe_meta_data/`** — your approval policy and stages.

Reference: [Extensions contract](concepts/registry-extensions/extensions-contract.md)
for class names, [Base models](concepts/base-models.md) for inherited fields,
[Register metadata](concepts/registry-and-register-metadata/README.md) for each
metadata table.

{% hint style="danger" %}
**This is where the platform's one real hazard lives.** Almost everything in this
step is names matching across files that never import one another, and when they
do not match **nothing raises**:

| Mismatch | What you see |
|---|---|
| widget path ↔ ORM column | a permanently blank field that accepts no input |
| dropdown `attribute_id` ↔ code list | an empty dropdown; the field cannot be filled |
| enum value ↔ code-list value | the field refuses to save, or the value is unreachable |
| inbound template key ↔ section mnemonic | ingested records arrive with empty tables |
| consent scope ↔ template top-level key | every shared record clamps to `{}` |
| seed `INSERT` with no `ON CONFLICT` | the second install half-applies metadata and exits `0` |

Read [Contracts that fail silently](contracts-that-fail-silently.md) **before**
writing the metadata, and add its check suite as `test/test_metadata_consistency.py`
while you go. It needs no cluster and no database, so it runs on every push and
catches all six on the first `pytest`.
{% endhint %}

Two habits that remove whole categories of this:

* **Generate the code lists from the enums** rather than maintaining both, and
  fail CI when the checked-in SQL is stale.
* **Generate the translation keys from the section metadata** — every
  `widget-label` is a translation key, and a missing one renders as the raw key.

**Done when:**

```bash
# every register named in the metadata has its three ORM classes and a service
pytest test/test_metadata_consistency.py -q
python -m compileall -q <domain>-extension/src
```

## 4. Build thin images

Five Dockerfiles under `docker/`, each `FROM` the matching platform image. They
are ~10 lines; the platform image already carries the runtime, the entrypoint and
the CMD.

```dockerfile
ARG RP_VERSION=0.0.0-develop.383
FROM registry.gitlab.com/openg2p/registry/registry-platform/staff-api:${RP_VERSION}

ENV REGISTRY_EXTENSION_MODULE=openg2p_registry_<domain>_extension

COPY <domain>-extension/ /app/<domain>-extension/
RUN pip install --no-cache-dir /app/<domain>-extension
```

Repeat for `partner-api` and `celery` (identical but for the base image).

**`db-seed`** is different — it clears the reference registry's seed content and
copies yours:

```dockerfile
FROM registry.gitlab.com/openg2p/registry/registry-platform/db-seed:${RP_VERSION}
RUN rm -rf /seed/meta_data/* /seed/awe_meta_data/* /seed/templates/* /seed/seed-data/*
COPY <domain>-extension/src/openg2p_registry_<domain>_extension/meta_data/     /seed/meta_data/
COPY <domain>-extension/src/openg2p_registry_<domain>_extension/awe_meta_data/ /seed/awe_meta_data/
COPY <domain>-extension/src/openg2p_registry_<domain>_extension/templates/     /seed/templates/
COPY docker/db-seed/seed-data/                                                 /seed/seed-data/
```

**`sanity-tests`** layers your field tests onto the platform suite — see step 6.

`staff-ui` and `bene-api` carry no domain code: use the platform images as-is.

{% hint style="warning" %}
**The build context is the repository root**, not the Dockerfile's directory —
every image copies `<domain>-extension/` from it:

```bash
docker build -f docker/staff-api/Dockerfile -t <domain>/staff-api:dev .
```
{% endhint %}

**db-seed also needs your own loaders.** The base image's
`load_sample_data.py` and `upload_images.py` are written against the reference
registry's tables and will crash-loop against yours; the entrypoint hard-fails if
`LOAD_SAMPLE_DATA=true` and no variant loader is present.

```dockerfile
COPY docker/db-seed/load_sample_data.py /seed/load_sample_data.py
COPY docker/db-seed/upload_images.py    /seed/upload_images.py
```

Inherited unchanged because they are genuinely domain-agnostic: `entrypoint.sh`,
`load_geo_data.py`, `load_attributes_from_mds.py`, `sync_geo_widgets.py`,
`upload_templates.py`.

#### Where sample people come from

This is the decision that most often gets made wrong, because both sources work
and only one is country-coherent.

| Source | Table / file | Use it |
|---|---|---|
| **Master Data country samples** | `g2p_sample_individuals`, `g2p_sample_households` in the master-data DB | **Always, when present.** Master Data is where the country is declared, so its people match the pack's geography, names and code lists |
| Shared demography CSV | `/openg2p-data/demography/individuals.csv` | Fallback only |

**Read Master Data first and fall back to the CSV**, exactly as the reference
registries do. Your loader's job is to add *your* fields to the country's people,
not to invent a second population.

{% hint style="danger" %}
**The CSV describes one fixture country.** Its five fixed level names
(country/region/district/ward/village) are that country's shape. Load it into a
deployment configured for another country and you get people with the wrong
names sitting in administrative units that do not exist there — and it does not
error, because there is nothing to error against. Say so in the log when you
fall back, or nobody will notice.
{% endhint %}

Two things the Master Data path gives you for free:

* **Geography by p-code.** A sample row carries `geo_pcode` — the unit's own id.
  Walk its ancestry through `parent_level_value_id` and write the chain
  directly. No name matching, and no chance of the slug-path mismatch the CSV
  path has to guard against. Read the **depth and the level names** from
  `g2p_geo_levels` rather than assuming five: Ethiopia has four and calls the
  middle ones zone and woreda.
* **The country's own attributes.** `disability_status`, `employment_status`,
  `relationship_to_head` and friends are on the sample row. If a pack marks who
  it considers disabled, or employed, prefer that over any selection rule of
  your own — the country has already decided.

{% hint style="warning" %}
**Sizing.** A pack's sample set is a curated fixture — tens of people, not
thousands. Applying a prevalence rate to it ("register 16% of them") yields two
or three records and a demo with nothing in it. Take a share of the CSV's
population-shaped set if you must, but take a pack's samples whole, or select
them on an attribute the pack actually carries.
{% endhint %}

{% hint style="info" %}
**Dates.** Older packs carry only `birth_year`, not `birth_date`. Falling back to
1 January puts every sample person on the same birthday, so any chart binned by
month shows one enormous January spike. Age bands are unaffected. Use
`birth_date` when the pack has it, and know which you got.
{% endhint %}

#### The four obligations

A variant loader has to do four things the ORM would otherwise do for it:

1. **Write `search_text` explicitly** — the SQLAlchemy listeners do not fire for
   raw SQL, and a record without it cannot be found by search or by DCI.
2. **Resolve and write geography explicitly** — `geo_lowest_level_value_id` *and*
   `geo_code_hierarchy_json`. The `@validates` hook that normally builds the
   second is ORM-only.
3. **Read the target table's columns from `information_schema`** rather than
   hard-coding them, so a renamed column degrades to a clear error instead of a
   silently skipped insert.
4. **Wrap optional inserts in a `SAVEPOINT`** — without one, a failed statement
   poisons the transaction and the final `COMMIT` rolls back everything.

See [Contracts that fail silently](contracts-that-fail-silently.md).

**Done when** all five images build from a clean checkout **and the three Python
images actually boot**:

```bash
for i in staff-api partner-api celery db-seed sanity-tests; do
  docker build -f "docker/${i}/Dockerfile" -t "<domain>/${i}:dev" . || exit 1
done

# Building only proves pip succeeded. Import each image's OWN app module the
# way its entrypoint does — this is what catches a missing dependency.
boot() {
  docker run --rm --entrypoint python3 "<domain>/$1:dev" -c "
import os, sys, importlib
sys.modules['openg2p_registry_extensions'] = importlib.import_module(
    os.environ['REGISTRY_EXTENSION_MODULE'])
importlib.import_module('$2')
print('$1 boots')
" || { echo "$1 DOES NOT BOOT"; exit 1; }
}
boot staff-api   openg2p_registry_staff_api.app
boot partner-api openg2p_registry_partner_api.app
boot celery      openg2p_registry_celery_worker.main
boot celery      openg2p_registry_celery_beat.main
```

{% hint style="info" %}
The celery image carries **both** codebases — `openg2p_registry_celery_worker`
and `openg2p_registry_celery_beat` (singular, both of them). Which one runs is
chosen at deploy time by `CELERY_APP`, so both are worth importing here.
{% endhint %}

{% hint style="danger" %}
**"It builds" is not "it runs", and the two fail in different images.** Every
image `pip install`s the same extension, so a build succeeds everywhere — but the
platform packages differ per image, and only `staff-api` carries
`openg2p_registry_staff_api`. An import that reaches across packages therefore
breaks `partner-api` and `celery` while `staff-api` stays green, and you find out
in a `CrashLoopBackOff` two steps later.

Import each image's own app module — `openg2p_registry_staff_api.app`,
`openg2p_registry_partner_api.app`, `openg2p_registry_celery_workers.main` —
after aliasing the extension, exactly as the entrypoint does.

This also smoke-tests the **base image you pinned**, so a broken platform build
is caught here rather than in a cluster.
{% endhint %}

## 5. Write the chart

`helm/openg2p-<domain>/Chart.yaml` declares the platform chart as a **pinned
dependency**, aliased so your overlay nests under one key:

```yaml
dependencies:
  - name: openg2p-registry
    alias: registry
    version: 0.0.0-develop.383      # same value as RP_VERSION above
    repository: https://gitlab.com/api/v4/projects/84460547/packages/helm/stable
```

`values.yaml` then carries only what is yours:

```yaml
global:
  registryVariant: <domain>
  registryHostname: '{{ .Release.Name }}.{{ .Release.Namespace }}.openg2p.org'

registry:                    # values for the platform subchart
  staffApi:
    image: { repository: registry.gitlab.com/.../staff-api, tag: 0.0.0-develop }
  dbSeed:
    loadSampleData: true
  idgenerator:
    idGenerator: { appConfig: { idTypes: { <domain>: { idLength: 12 } } } }
  sanity:
    enabled: true
```

{% hint style="warning" %}
**`global.*` vs `registry.*`.** Helm propagates `global` into subcharts
automatically, so shared settings stay at the top level. Everything else is the
*subchart's* value and must nest under `registry.` — a platform setting written
as `dbSeed.loadSampleData` becomes `registry.dbSeed.loadSampleData` here.
{% endhint %}

### Functional-ID pools

The platform runs a MOSIP ID generator as a subchart, and it allocates from a
**pool per register**. You declare one pool for each register that mints
functional IDs — the registers you marked in step 1, and no others. A
single-register registry needs exactly one.

```yaml
registry:
  idgenerator:
    idGenerator:
      appConfig:
        idTypes:
          <mnemonic-lowercase>:
            idLength: 12
```

Three rules, and each of them is a silent failure if you get it wrong:

* **The pool key is the register mnemonic, lowercased.** It must match what your
  `G2PIdGeneratorService.generate_prefix_suffix()` branches on — that method
  receives the mnemonic and returns the prefix/suffix. A key that matches nothing
  means records are created with no functional ID.
* **Declare your pools explicitly.** Defaults exist at two levels below you and
  neither is yours.
* **You cannot remove an inherited pool.** Helm **merges** maps, and a `null` in
  a parent's `values.yaml` does not delete a subchart default.

That second rule has a consequence worth seeing before it surprises you. Pools
accumulate from three layers:

| Layer | Pools it contributes |
|---|---|
| `openg2p-id-generator` subchart defaults | `farmer` (12), `household` (10) |
| `openg2p-registry` chart defaults | `individual` (12), `household` (10) |
| **your overlay** | whatever you declare |

So a single-register registry that declares one pool still renders **four**:

```
farmer                {'id_length': 12}
household             {'id_length': 10}
individual            {'id_length': 12}
personwithdisability  {'id_length': 12}      ← the only one it uses
```

Each unused pool is an empty table and nothing more — it costs nothing at
runtime and allocates no IDs, because nothing ever asks it for one. But it is
alarming when you first see it, so expect it rather than debugging it.

{% hint style="info" %}
**The Rancher form's "ID Types Configuration" note is a static string** from the
platform chart, not a reading of your values — it cannot know which registers
your registry has, and it describes only the deepest layer's defaults. Switch to
*Edit YAML* to see and change the real
`idgenerator.idGenerator.appConfig.idTypes` block.
{% endhint %}

Verify what actually rendered, rather than what you wrote:

```bash
helm template test ./helm/openg2p-<domain> \
  | python -c "
import sys, yaml
for d in yaml.safe_load_all(sys.stdin):
    if d and d.get('kind') == 'ConfigMap' and 'id-generator-config' in d['metadata']['name']:
        cfg = yaml.safe_load(d['data']['config.yaml'])['id_generator']
        print(cfg.get('id_types') or cfg.get('idTypes'))
"
```

Confirm your own pool is present and its name matches your `G2PIdGeneratorService`
branch. Ignore the inherited ones.

You do **not** write a `questions.yaml`. CI generates it from the pinned platform
chart so your Rancher form matches the platform's. If your chart owns keys the
platform has no concept of, put questions for those in `questions.own.yaml` and CI
appends them. Gitignore the generated `questions.yaml` — it rots against the pin.

**The chart owns no *service* templates — but it does own analytics.** The
reporting views and dashboards are written against *your* schema, so they cannot
come from the subchart. Expect to copy roughly five templates from a reference
registry and rename them:

| Template | Purpose |
|---|---|
| `analytics-jobs.yaml` | reporting-views and dashboard-import hook Jobs |
| `reporting-views-refresh.yaml` | CronJob refreshing the materialized views |
| `dashboard-bundle-configmap.yaml` | ships the Superset bundle into the cluster |
| `maps-content-configmap.yaml` + `_maps-content.tpl` | maps content for G2P Insights |
| `superset-service-account-secret.yaml` | the Superset service account |

A registry that ships none of these installs cleanly and has **no reporting at
all**, with nothing to indicate anything is missing. Hook weights matter: the
analytics chain sits above the sanity suite (25) so that rebuilding the views
cannot change what the sanity tests asserted against.

{% hint style="info" %}
The Superset bundle is produced by `docker/dashboards/build_bundle.py`, which
reads the reporting views' real column list — so the views must exist when you
build it. Consider building it as a release step and gitignoring the ZIP rather
than committing a binary nobody can diff, and defaulting
`analytics.dashboards.enabled` to `false` when you ship no bundle.
{% endhint %}

**Done when:**

```bash
helm dependency update ./helm/openg2p-<domain>
helm lint ./helm/openg2p-<domain>
helm template test ./helm/openg2p-<domain> > /tmp/render.yaml
# the overlay actually took effect — not the subchart's defaults
grep -q "registry.gitlab.com/openg2p/registry/<your-repo>/staff-api" /tmp/render.yaml
```

## 6. Narrow the sanity tests

The platform's sanity image already contains the harness and the
extension-independent tests. Add only the files whose assertions are shaped by
*your* fields — typically `sanity/fixtures.py`, `sanity/data_seed.py` and the two
e2e tests — and layer them on:

```dockerfile
FROM registry.gitlab.com/openg2p/registry/registry-platform/sanity-tests:${RP_VERSION}
COPY test/sanity/sanity/fixtures.py               /app/sanity/fixtures.py
COPY test/sanity/sanity/data_seed.py              /app/sanity/data_seed.py
COPY test/sanity/tests/test_e2e_dci.py            /app/tests/test_e2e_dci.py
COPY test/sanity/tests/test_e2e_change_request.py /app/tests/test_e2e_change_request.py
```

{% hint style="danger" %}
`fixtures.py` is a **contract**. Inherited modules import its symbols by name
(`FARMER_INTERNAL_ID` and friends — historical names meaning "the seeded sanity
record"). Change the *values*, never the *names*, or the whole suite dies at
collection.
{% endhint %}

**The chart side is a contract too, and three of its keys mislead.** The suite is
configured entirely through `registry.sanity.*`; left at the defaults, these are
the *reference registry's* values, and the suite then passes or fails for reasons
that have nothing to do with your registry:

| Key | Note |
|---|---|
| `farmerRegisterId` | **This is the register id**, whatever your registry is about. Same historical naming as `fixtures.py`; the subchart helpers and every variant use this spelling |
| `dataScopes`, `deniedScopes` | **Comma-separated strings**, not YAML lists — a list renders into the env var as Go map syntax. Both must name real top-level keys of your outbound DCI template |
| `regType`, `regRecordType` | Your register mnemonic and DCI record type |
| `crTabId`, `crSectionId` | A real, **editable** section of yours, or the change-request test's write is rejected |
| `searchText` | The injected record's `functional_record_id` — must equal what your `data_seed.py` writes |

**Also write the repository guards.** The sanity suite proves a *deployed*
registry works and needs a cluster, commons-services and Keycloak admin. A second,
much cheaper set proves the *repository* is coherent — field names resolving, code
lists existing, scopes matching the template, seed SQL re-runnable — and runs in
CI on every push, before anything is published. Those are the checks that catch
the silent failures listed in step 3.

**Done when:**

```bash
pytest test/test_rp_pin_lockstep.py test/test_metadata_consistency.py -q
helm template test ./helm/openg2p-<domain> \
  | grep -E "SANITY_FARMER_REGISTER_ID|SANITY_DCI_REG_TYPE"   # your values, not the defaults
```

Full model: [Testing & the sanity suite](../../deployment-and-extension/testing-and-sanity-suite.md).

## 7. Wire up CI

`.gitlab-ci.yml` declares only what your repo has; all build, version and publish
logic is central:

```yaml
include:
  - project: 'openg2p/packaging'
    ref: v1
    file: '/ci/gitlab/build-publish.yml'

variables:
  PACKAGING_REF: v1
  IMAGES: |
    [ {"name": "staff-api",    "dockerfile": "docker/staff-api/Dockerfile"},
      {"name": "partner-api",  "dockerfile": "docker/partner-api/Dockerfile"},
      {"name": "celery",       "dockerfile": "docker/celery/Dockerfile"},
      {"name": "db-seed",      "dockerfile": "docker/db-seed/Dockerfile"},
      {"name": "sanity-tests", "dockerfile": "docker/sanity-tests/Dockerfile"} ]
  CHART_PATH: helm/openg2p-<domain>
  CHART_IMAGE_PATHS: '[".registry.staffApi.image.tag", ".registry.partnerApi.image.tag", ".registry.celeryWorker.image.tag", ".registry.celeryBeat.image.tag", ".registry.dbSeed.image.tag", ".registry.sanity.image.tag"]'
  CHART_INHERIT_QUESTIONS: '{"dependency":"openg2p-registry","alias":"registry"}'
  CHART_GITLAB_PROJECT: openg2p/charts
```

**What the pipeline does.** Four stages — `version`, `build`, `chart`,
`changelog`. It derives **one version from git** for the whole commit, builds
every image in `IMAGES`, rewrites each `CHART_IMAGE_PATHS` entry to that version
so the chart can never reference a tag it did not ship with, generates
`questions.yaml` from the pinned platform chart, packages, and publishes.

**Where the artifacts land:**

| Artifact | Destination |
|---|---|
| Images | This project's GitLab container registry — `registry.gitlab.com/openg2p/registry/<your-repo>/<name>` |
| Helm chart | The shared `openg2p/charts` Helm registry (one Rancher catalogue for all of OpenG2P) |
| Changelog | Published per component and indexed at [openg2p.gitlab.io/versions](https://openg2p.gitlab.io/versions/index.html) |

You configure no runners, credentials or registries — `CHART_GITLAB_PROJECT` and
the project's own registry are all the pipeline needs.

### Adding your own job — the stage trap

The included file declares the stage list, and it is the only one:

```yaml
stages: [version, build, chart, changelog]
```

**There is no `test` stage.** If you add a job — the repository guards from
step 6 are the usual reason — it must name one of those four.

{% hint style="danger" %}
Naming a stage that does not exist is **not** a per-job error. GitLab rejects the
whole config, and the pipeline fails **instantly with zero jobs**, `yaml_errors:
null` and an empty `failure_reason`. The UI shows a failed pipeline with nothing
in it, which looks like an infrastructure problem rather than a typo.

Worse: GitLab's **default** stage is `test`. A job that omits `stage:` altogether
fails exactly the same way.
{% endhint %}

Put the guards in **`version`** — it is the first stage, so a failure there stops
`build` and `chart` before any image or chart is published:

```yaml
checks:
  stage: version          # NOT `test` — see above
  image: python:3.11-slim
  script:
    # test/sanity is excluded: those tests import the platform sanity harness,
    # which only exists inside the sanity image. They run in-cluster.
    - pip install --no-cache-dir pytest pyyaml
    - pytest test/ --ignore=test/sanity -v
  rules:
    - if: $CI_COMMIT_BRANCH
    - if: $CI_MERGE_REQUEST_IID
```

Validate before you push — a rejected config costs a full round trip, and the
error it gives you does not name the cause:

```bash
# needs a token, but gives the definitive answer
glab ci lint

# or, with no credentials: check every job against the included stage list
python - <<'EOF'
import urllib.request, yaml
local = yaml.safe_load(open('.gitlab-ci.yml'))
inc = yaml.safe_load(urllib.request.urlopen(
    "https://gitlab.com/api/v4/projects/openg2p%2Fpackaging/repository/files/"
    "ci%2Fgitlab%2Fbuild-publish.yml/raw?ref=v1").read())
stages = local.get('stages') or inc['stages']
reserved = {'include','variables','stages','default','workflow','image',
            'before_script','after_script','cache','services'}
bad = [(n, b.get('stage', 'test')) for n, b in local.items()
       if n not in reserved and isinstance(b, dict)
       and b.get('stage', 'test') not in stages]
raise SystemExit(f"jobs on an undeclared stage: {bad}" if bad else 0)
EOF
```

**Also copy three scripts** from a reference registry:

* `scripts/bump-rp-version.sh` — moves the platform pin in the Dockerfiles **and**
  the chart dependency together (`-n` previews, `<version>` pins explicitly).
* `test/test_rp_pin_lockstep.py` — fails the build if those two ever drift. This
  has caught real breakage: a chart on one platform version with images built
  against another produces an overlay landing on a harness it does not match.
* `scripts/uninstall-registry.sh` — a **clean** teardown. `helm uninstall` leaves
  the PVCs, the database, the MinIO buckets and the Keycloak clients behind, so a
  reinstall into the same namespace inherits stale state. Every OpenG2P service is
  expected to ship one.

**Done when:**

```bash
test -f .gitlab-ci.yml
test -x scripts/bump-rp-version.sh
test -x scripts/uninstall-registry.sh
test -f test/test_rp_pin_lockstep.py
pytest test/test_rp_pin_lockstep.py -q      # chart pin == every Dockerfile pin
# and every job you added sits on a declared stage — see the snippet above
```

{% hint style="warning" %}
A pipeline that fails with **zero jobs** is almost always a rejected config, not
a broken runner. Check `stage:` on every job you added before looking anywhere
else:

```bash
curl -s "https://gitlab.com/api/v4/projects/<id>/pipelines/<pipeline-id>" \
  | grep -o '"status":"[^"]*"\|"yaml_errors":[^,]*'
```
{% endhint %}

Versioning rules: [Helm & Docker versioning and CI](https://docs.openg2p.org/operations/deployment/helm-docker-versioning-and-ci).

## 8. Publish and check

Push. CI builds every image and the chart at **one version**, and publishes them.

Confirm before moving on:

* [ ] All five images published at the same version
* [ ] The chart published at that same version
* [ ] `./scripts/bump-rp-version.sh -n` reports no pin drift
* [ ] The repository guards pass
* [ ] Any generated files are current (code lists, translations)
* [ ] `helm template` renders your chart **and carries your overrides**

**Done when** this exits zero from a clean checkout:

```bash
# --ignore=test/sanity is required: the sanity tests import the platform
# harness, which only exists inside the sanity image. They run in-cluster.
pytest test/ --ignore=test/sanity -q               # pin lockstep + metadata guards
./scripts/bump-rp-version.sh -n                    # no drift
helm dependency update ./helm/openg2p-<domain>
helm lint  ./helm/openg2p-<domain>
helm template test ./helm/openg2p-<domain> > /dev/null && echo OK
```

{% hint style="info" %}
Use `helm dependency **update**`, not `build`, after changing the pin — `build`
honours a stale `Chart.lock` and will silently resolve the old platform version.
{% endhint %}

---

**Next:** [Phase 2 — Run it in a sandbox](run-in-a-sandbox.md)
