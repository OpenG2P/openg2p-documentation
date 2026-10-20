---
description: >-
  The Docker images and the single Helm chart the platform publishes, the
  reference registry they run out of the box, how the domain model is selected
  at runtime, and how a domain registry's chart wraps the platform chart.
---

# Packaging & the reference registry

## The reference registry

`registry-platform` bundles a **reference extension** — a minimal but real registry with an **Individual** register and a **Household** register (borrowed, trimmed, from the National Social Registry model). It lives at `registry-platform/reference-extension`.

Because the reference extension is baked into the images, the platform **runs as-is**: `helm install openg2p-registry` (no overlay) brings up a working registry, seeds it, and passes its own sanity suite. This makes the platform demoable, CI-testable, and a copy-ready example — not an empty scaffold.

## The images

All images are published to Docker Hub under `openg2p/`, built and versioned together (see [Versioning & CI](#versioning-and-ci)).

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
* a domain registry wraps it in a thin chart of its own (see [Domain registry charts](#domain-registry-charts)).

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

## Domain registry charts

A domain registry (for example the [Farmer Registry](../../farmer-registry/README.md) or the [Crop Sown Registry](../../crop-sown-registry/README.md)) ships a thin chart of its own. Developers read the chart itself; these are the points that are not obvious from it.

* **A wrapper, not a copy.** The chart declares `openg2p-registry` as a pinned dependency with the alias `registry`, and supplies a values overlay: the registry variant, its own images, and its defaults. It adds templates only for things the platform has no concept of (for example a registry's own dashboards). The wrapper exists so the registry has its own catalogue entry, name and version line in Rancher.
* **Two kinds of value.** In a values file, platform settings sit under `registry.*` (the subchart's values). Shared settings sit under `global.*`, which Helm passes to the subchart unchanged. So `dbSeed.loadSampleData` on the platform chart is `registry.dbSeed.loadSampleData` on a domain chart.
* **The Rancher form is inherited.** Rancher reads `questions.yaml` only from the root chart, never from a subchart. So the wrapper keeps no `questions.yaml` in git. At packaging time CI generates it from the pinned platform chart (the `chart-inherit-questions` input of the build workflow, which runs `inherit-questions.sh` in `openg2p-packaging`):
  * every platform question is prefixed with `registry.`; `global.*` questions keep their names;
  * each default is taken from the wrapper's own values first, then the platform's, so the form shows the registry's images and switches (a blank boolean would submit as false);
  * questions for keys only the wrapper has go in its `questions.own.yaml`, which CI appends unchanged.

  The form therefore always matches the pinned platform version.
* **One platform version, in two places.** The platform version is pinned as `RP_VERSION` in each Dockerfile (the base image tag) and as the `openg2p-registry` dependency version in `Chart.yaml`. The two always move together, with the registry's `scripts/bump-rp-version.sh`: `-n` shows the newest version published as both chart and images, `<version>` pins that version in both places. A CI check (`test/test_rp_pin_lockstep.py`) fails the build if the two drift.
* **Two version lines.** The registry's own chart and images share one version, stamped by CI on every commit. The platform version moves only when it is bumped as above.
* **Several registries in one namespace.** Names that would collide (the Keycloak staff client, the keymanager app-id, the AWE callback secret) derive from the release name, so two registries can share a namespace.

## Versioning & CI

A **single** workflow (`build-publish.yml`) builds **all** images + the chart at **one version per commit**, and rewrites every chart image tag to that version so images and chart stay locked together. The `ui-widgets` npm library is the only separately-versioned artifact.

* Scheme, derivation and lockstep rules: [**Helm & Docker versioning and CI**](../../../../releases/helm-docker-versioning-and-ci/README.md).
* Released versions / changelog: [**Registry Platform changelog**](https://openg2p.github.io/versions/registry-platform/CHANGELOG.html).
