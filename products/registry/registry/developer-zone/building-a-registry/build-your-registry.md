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

Unsure whether something is a register: [Registry vs Register](concepts/registry-vs-register.md).

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
{% endhint %}

**Everything derives from one slug.** `<domain>` is the repo name, the Python
package, the image names, the chart, the DB schema prefix and the Keycloak
clients — pick it once and use it verbatim everywhere. This is the OpenG2P naming
convention for any service; see
[Creating a New Platform Service](../../../../../platform/platform-services/creating-a-new-service.md)
for the full set of conventions a registry inherits.

## 3. Write the domain

In `src/openg2p_registry_<domain>_extension/`:

1. **`register_domain/models/`** — one file per register. Each declares the
   register table, its `history` twin and its `intake_form` twin, inheriting the
   platform base classes. Put enums in `enums.py`.
2. **`register_domain/schemas/`** — a Pydantic mirror per model.
3. **`register_domain/services/`** — `G2PRegisterDomainService{Mnemonic}` per
   register.
4. **`register_domain/factory/`** — map each mnemonic to your classes.
5. **`meta_data/register-metadata/`** — the seed SQL, in this order: register
   definitions → sections → schemas → UI tabs → tab-sections → intake equivalents.
6. **`meta_data/lookup-data/`** — your code lists.
7. **`templates/`** — your DCI templates.
8. **`awe_meta_data/`** — your approval policy and stages.

Reference: [Extensions contract](concepts/registry-extensions/extensions-contract.md)
for class names, [Base models](concepts/base-models.md) for inherited fields,
[Register metadata](concepts/registry-and-register-metadata/README.md) for each
metadata table.

{% hint style="warning" %}
**The field names must agree in three places** — the ORM column, the section JSON
in `g2p_register_sections.sql`, and the DCI template. A mismatch shows up as a
blank field in the portal or an empty DCI response, not as an error.
{% endhint %}

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

You do **not** write a `questions.yaml`. CI generates it from the pinned platform
chart so your Rancher form matches the platform's. If your chart owns keys the
platform has no concept of, put questions for those in `questions.own.yaml` and CI
appends them.

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

Versioning rules: [Helm & Docker versioning and CI](https://docs.openg2p.org/operations/deployment/helm-docker-versioning-and-ci).

## 8. Publish and check

Push. CI builds every image and the chart at **one version**, and publishes them.

Confirm before moving on:

* [ ] All five images published at the same version
* [ ] The chart published at that same version
* [ ] `./scripts/bump-rp-version.sh -n` reports no pin drift
* [ ] `helm template` renders your chart without error

```bash
helm dependency update ./helm/openg2p-<domain>
helm template test ./helm/openg2p-<domain> > /dev/null && echo OK
```

{% hint style="info" %}
Use `helm dependency **update**`, not `build`, after changing the pin — `build`
honours a stale `Chart.lock` and will silently resolve the old platform version.
{% endhint %}

---

**Next:** [Phase 2 — Run it in a sandbox](run-in-a-sandbox.md)
