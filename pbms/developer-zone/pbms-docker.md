---
description: >-
  Information regarding the PBMS Odoo, portal API, and background-task Docker
  images and how they are built.
---

# PBMS Docker

## Concepts

All PBMS Docker images are built **from the local source in the consolidated [OpenG2P/pbms](https://github.com/OpenG2P/pbms) repository** (build context = the repository root; the Dockerfiles `COPY` the in-repo code). There are **no package files** — the components are no longer pulled from separate repositories at build time.

The following **five images** are produced (image names are stable; the tag is the branch name — a push to `develop` publishes `:develop`):

<table><thead><tr><th width="360">Image</th><th>Built from</th></tr></thead><tbody>
<tr><td><code>openg2p/openg2p-pbms-core</code></td><td>Odoo — <code>odoo/</code> (core modules, <code>odoo/extensions/</code>, <code>odoo/community-addons/</code>)</td></tr>
<tr><td><code>openg2p/openg2p-pbms-staff-portal-api</code></td><td><code>apis/openg2p-pbms-staff-portal-api</code> (+ <code>core/</code> models, <code>extensions/</code>)</td></tr>
<tr><td><code>openg2p/openg2p-pbms-bene-portal-api</code></td><td><code>apis/openg2p-pbms-bene-portal-api</code> (+ <code>core/</code> models, <code>extensions/</code>)</td></tr>
<tr><td><code>openg2p/openg2p-pbms-bg-task-celery-workers</code></td><td><code>core/openg2p-bg-task-celery-workers</code> (+ models, <code>extensions/</code>)</td></tr>
<tr><td><code>openg2p/openg2p-pbms-bg-task-celery-beat-producers</code></td><td><code>core/openg2p-bg-task-celery-beat-producers</code> (+ models)</td></tr>
</tbody></table>

The Dockerfiles live under [`docker/`](https://github.com/OpenG2P/pbms/tree/develop/docker) in the repository.

### External dependencies (build args)

PBMS's own code is built from the repo; a few **shared** OpenG2P libraries and base images are pulled at build time and are overridable via build args / workflow inputs:

* `FASTAPI_COMMON_REF` (default `develop`) — [openg2p-fastapi-common](https://github.com/OpenG2P/openg2p-fastapi-common), for the API and Celery images.
* `G2P_BRIDGE_REF` — [openg2p-g2p-bridge](https://github.com/OpenG2P/openg2p-g2p-bridge) models, for the Celery worker image.
* `ODOO_COMMONS_REF` (default `v1.4.0`) — [openg2p-odoo-commons](https://github.com/OpenG2P/openg2p-odoo-commons), cloned into the Odoo (`core`) image at build time.
* `BASE_VERSION` — the upstream `odoo:` base image tag for the Odoo image.

## Building the images

Images are built by GitHub Actions workflows in the repository. They run automatically on a push that touches the relevant code paths, and can also be triggered manually via `workflow_dispatch` (where the build-arg refs above are exposed as inputs). The image tag is derived from the branch name (`develop` → `:develop`).

<table><thead><tr><th width="330">Workflow</th><th>Builds</th></tr></thead><tbody>
<tr><td><a href="https://github.com/OpenG2P/pbms/blob/develop/.github/workflows/docker-build-core.yml">docker-build-core.yml</a></td><td><code>openg2p-pbms-core</code> (Odoo)</td></tr>
<tr><td><a href="https://github.com/OpenG2P/pbms/blob/develop/.github/workflows/docker-build-apis.yml">docker-build-apis.yml</a></td><td><code>staff-portal-api</code>, <code>bene-portal-api</code></td></tr>
<tr><td><a href="https://github.com/OpenG2P/pbms/blob/develop/.github/workflows/docker-build-bg-tasks.yml">docker-build-bg-tasks.yml</a></td><td><code>bg-task-celery-workers</code>, <code>bg-task-celery-beat-producers</code></td></tr>
</tbody></table>

To build locally, run `docker build` from the repository root, pointing at the relevant Dockerfile — for example:

```sh
docker build -t openg2p/openg2p-pbms-staff-portal-api:develop \
  -f docker/openg2p-pbms-apis/staff-portal-api/Dockerfile .
```

{% hint style="info" %}
Image tags follow the branch-based versioning contract: a build from `develop` is tagged `:develop`. See [Versions](../versions.md).
{% endhint %}
