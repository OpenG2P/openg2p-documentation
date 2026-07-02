---
description: Physical organization of source code in the g2p-bridge monorepo
---

# Physical Organization

The G2P Bridge source code is consolidated into a **single repository**:
[**`g2p-bridge`**](https://github.com/OpenG2P/g2p-bridge). What were previously
seven separate repositories are now folders within this one monorepo, with each
component's internal structure kept intact.

{% hint style="info" %}
The redundant `openg2p-g2p-bridge-` prefix has been stripped from folder and file
names within the repo. Python package names (e.g. `openg2p_g2p_bridge_models`),
Docker image names, and Helm `Chart.yaml` names are intentionally left unchanged.
{% endhint %}

## Repository layout

| Folder | Origin repo | Contents |
| --- | --- | --- |
| [`core/`](https://github.com/OpenG2P/g2p-bridge/tree/develop/core) | `openg2p-g2p-bridge` | Core services and libraries: `models`, `partner-api`, `bene-portal-api`, `celery-beat-producers`, `celery-workers`. |
| [`extensions/`](https://github.com/OpenG2P/g2p-bridge/tree/develop/extensions) | `openg2p-g2p-bridge-extensions` | Pluggable adapters/connectors meant to be customized per implementation: agency-allocator, bank-connectors, geo-resolver, mapper-connectors, notification-connectors, warehouse-allocator. |
| [`example-bank/`](https://github.com/OpenG2P/g2p-bridge/tree/develop/example-bank) | `openg2p-g2p-bridge-example-bank` | Reference Sponsor Bank simulator (not for production): api, celery-beat-producers, celery-workers, models. |
| [`docker/`](https://github.com/OpenG2P/g2p-bridge/tree/develop/docker) | `openg2p-g2p-bridge-docker` | Dockerfiles for the API and Celery service images. |
| [`deployment/`](https://github.com/OpenG2P/g2p-bridge/tree/develop/deployment) | `openg2p-g2p-bridge-deployment` + `openg2p-g2p-bridge-example-bank-deployment` | The single consolidated Helm chart `charts/openg2p-bridge` (Bridge + bundled Example Bank, toggled via `exampleBank.enabled`) and the `scripts/` (e.g. `uninstall-bridge.sh`). |
| [`test/`](https://github.com/OpenG2P/g2p-bridge/tree/develop/test) | `openg2p-g2p-bridge-test` | Test artefacts — the `sanity/` regression suite (API coverage, full e2e cash flow, business-rule negatives and MT940 reconciliation-error checks). |

## Core modules (`core/`)

| Module | Type | Purpose |
| --- | --- | --- |
| **partner-api** | service (pod) | FastAPI REST APIs for partner systems. Upstream systems like PBMS call this to hand over disbursement instructions. Secured via partner signature validation — in-process local JWS by default (backend selectable: `local` \| `keymanager`); see [Partner APIs → Authentication](partner-apis.md#authentication). Scale horizontally. |
| **bene-portal-api** | service (pod) | FastAPI REST APIs for the OpenG2P Beneficiary Portal. Secured via an access token from an identity provider. Scale horizontally. |
| **celery-beat-producers** | service (pod) | Produces periodic Celery beats. Run as a **single** replica. |
| **celery-workers** | service (pod) | Celery workers that execute the beats (check balance, block funds, initiate payments, reconcile MT940, and — for in-kind — geo/warehouse/agency tasks). Scale horizontally. |
| **models** | library | SQLAlchemy persistence models and Pydantic schemas shared by the api, beat producer and workers. |

The beat producer and workers ship as a **single Docker image** (`openg2p/openg2p-bridge-celery`); the Helm chart runs it as beat or worker by configuration.

## Example Bank modules (`example-bank/`)

| Module | Type | Purpose |
| --- | --- | --- |
| **example-bank-api** | service (pod) | FastAPI REST APIs of a fictitious "Example Bank" — check balance, block funds, initiate payments. Self-seeds the treasury account on migrate. |
| **example-bank-celery** (beat-producers + workers) | service (pod) | Asynchronous processing — payments and MT940 statement generation. |
| **example-bank-models** | library | SQLAlchemy models and Pydantic schemas shared by the api and celery modules. |

{% hint style="warning" %}
The Example Bank only **simulates** a Sponsor Bank for end-to-end demos and is
not used in a production deployment.
{% endhint %}

## CI workflows

GitHub Actions live under `.github/workflows`, each scoped with `paths:` filters
so it runs only when its component changes:

* `pre-commit.yml` — runs each sub-project's own pre-commit config.
* `core-test.yml`, `example-bank-test.yml` — test + coverage.
* `docker-build-apis.yml`, `docker-build-celery.yml`, `docker-build-example-bank.yml` — build/push images. **The image tag matches the `g2p-bridge` repository ref** (branch name or git tag).
* `helm-publish.yml` — package and publish the Helm chart(s) under `deployment/charts/`.

{% hint style="info" %}
The Python packages are **not published to PyPI** — every image builds them from
local in-repo source. On `develop`, each module's `__version__` is `0.0.0.dev0`.
The only external OpenG2P libraries (`openg2p-fastapi-common`, and
`openg2p-spar-models` for celery) are overridable inputs on the docker build
workflows.
{% endhint %}
