---
description: >-
  The Docker images and the single Helm chart the platform publishes, the
  reference registry they run out of the box, and how the domain model is
  selected at runtime.
---

# Packaging & the reference registry

## The reference registry

`registry-platform` bundles a **reference extension** — a minimal but real registry with an **Individual** register and a **Household** register (borrowed, trimmed, from the National Social Registry model). It lives at `registry-platform/reference-extension`.

Because the reference extension is baked into the images, the platform **runs as-is**: `helm install openg2p-registry` (no overlay) brings up a working registry, seeds it, and passes its own sanity suite. This makes the platform demoable, CI-testable, and a copy-ready example — not an empty scaffold.

## The images

All images are published to Docker Hub under `openg2p/`, built and versioned together (see [versioning](./#versioning-and-ci)).

| Image | Contents |
|---|---|
| `openg2p-registry-staff-api` | core + staff portal API + reference extension |
| `openg2p-registry-partner-api` | core + partner API + reference extension |
| `openg2p-registry-bene-api` | core + beneficiary portal API + reference extension |
| `openg2p-registry-celery` | core + celery worker & beat + reference extension (role via `CELERY_APP`) |
| `openg2p-registry-db-seed` | postgres-client + seeding machinery + `openg2p-data` + the reference registry's seed |
| `openg2p-registry-staff-ui` | Next.js Staff Portal UI |
| `openg2p-registry-sanity-tests` | the sanity/e2e suite (see [Testing](testing-and-sanity-suite.md)) |

Dockerfiles are in `registry-platform/docker/*` (and `ui/staff-ui/Dockerfile`). The API/celery images install the platform packages from **this repo's own working tree** — this repo *is* the platform — so there is no `REGISTRY_PLATFORM_REF`; only the external `openg2p-fastapi-common` / `iam-service` libraries are pulled by git ref.

## The single Helm chart

There is **one** chart, `openg2p-registry` (`registry-platform/helm/openg2p-registry`), published to the OpenG2P Helm repository — [`openg2p.github.io/openg2p-helm`](https://openg2p.github.io/openg2p-helm). It deploys **any** registry:

* installed with **no overlay**, it runs the **reference registry**;
* a domain registry supplies a small **values overlay** pointing at its own images (see [Extending](extending-into-a-new-registry.md)).

There is no per-registry chart copy — the templates live once, here.

## How the domain model is selected — `REGISTRY_EXTENSION_MODULE`

The platform code imports the domain model by a fixed name (`openg2p_registry_extensions`). At startup each entrypoint **aliases the env-selected module** into `sys.modules`:

```python
_ext = os.environ.get("REGISTRY_EXTENSION_MODULE", "openg2p_registry_extensions")
if _ext != "openg2p_registry_extensions":
    sys.modules["openg2p_registry_extensions"] = importlib.import_module(_ext)
```

So a single environment variable, **`REGISTRY_EXTENSION_MODULE`**, decides which registry runs:

* the reference extension installs under its **own** import name (`openg2p_registry_reference_extension`) and the images default the env var to it;
* a domain extension installs under **its own** name too, and its image sets the env var to that.

Both extensions can therefore **coexist in one image** — the env var selects one; there is no import-name collision and no `pip uninstall` step. (This replaces the older approach of aliasing every extension onto the same import name via `pyproject.toml`.)

## Versioning & CI

A **single** workflow (`build-publish.yml`) builds **all** images + the chart at **one version per commit**, and rewrites every chart image tag to that version so images and chart stay locked together. The `ui-widgets` npm library is the only separately-versioned artifact.

* Scheme, derivation and lockstep rules: [**Helm & Docker versioning and CI**](https://docs.openg2p.org/operations/deployment/helm-docker-versioning-and-ci).
* Released versions / changelog: [**registry-platform changelog**](https://openg2p.github.io/openg2p-packaging/registry-platform/CHANGELOG).
