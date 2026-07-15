---
description: >-
  OpenG2P's presence on GitLab — which repositories live there, why GitLab, how
  images and charts are published, how the org and per-customer groups are
  organized, and how to move a GitHub repo to GitLab.
---

# OpenG2P GitLab Repositories

OpenG2P's **core codebase remains on GitHub**. Alongside it, a growing set of
repositories live on **GitLab** — chiefly **private, customer/implementation-specific
repositories** — and more are being moved there over time. This page is the
map: what's on GitLab, why, how artifacts are published, and how to migrate a
repository.

For the **detailed publishing mechanics** (the CI wrapper, registries, Rancher
wiring), see [Publishing to GitLab](../../releases/helm-docker-versioning-and-ci/publishing-to-gitlab.md);
this page stays at the "what and why" level and links down for the "how".

## Why GitLab

We chose GitLab for the private/customer lane because it satisfies four
requirements in **one system**, which Docker Hub and GHCR do not:

1. **Chart + its images co-located** and versioned together (one project holds a
   Container Registry *and* a Helm Package Registry).
2. **One Rancher repo lists all charts + versions** — GitLab's Helm registry is
   index-based, so a single repository URL browses everything.
3. **Any artifact can be private** — visibility is per project, with per-project
   tokens; real tenant isolation.
4. **One login** — images, charts, source and CI all authenticate to the same
   GitLab.

The full reasoning (including why GHCR was rejected for #2, and the Docker Hub
trade-offs) is in [Publishing to GitLab → *Why GitLab*](../../releases/helm-docker-versioning-and-ci/publishing-to-gitlab.md#why-gitlab-the-four-requirements-it-satisfies)
— not duplicated here.

## Portable to a customer's own GitLab (air-gap)

Because GitLab is a **single self-contained platform** — source, CI, container
registry and Helm registry in one install — a customer can run the **entire**
thing on their **own, air-gapped GitLab** inside a country deployment. Nothing
needs to reach the public internet at deploy time.

This is what makes the repositories **portable**: the pipeline is written against
GitLab's predefined `CI_*` variables (registry host, API URL, server host), so a
group **exported and imported into the customer's instance runs unchanged** — the
registry and chart URLs resolve to *their* host automatically, with no edits. A
dedicated registry (Harbor/Zot) would solve only the registry, leaving source and
CI to be stood up separately in the air-gap; GitLab is one system for all of it.

## How images and charts are published

Every repository builds and publishes at **one immutable version per commit** —
the same scheme used on GitHub — via a **central GitLab-CI pipeline** included
from `openg2p/packaging`:

* **Images** → the repository's own project **Container Registry**
  (`registry.gitlab.com/<group>/<project>/<image>`).
* **Chart** → a **shared `charts` project's Helm Package Registry**, so Rancher
  adds **one** repo URL and browses every chart and version.
* **Changelog** → pure `.md` pushed to the **`openg2p/versions`** project,
  browseable directly in the repo.

Full details — the `.gitlab-ci.yml` inputs, tokens, and the Rancher URL (use the
**numeric project id**) — are in [Publishing to GitLab](../../releases/helm-docker-versioning-and-ci/publishing-to-gitlab.md).

{% hint style="info" %}
Source and CI currently run on **GitHub**, publishing artifacts **to** GitLab. As
a repository is *hosted* on GitLab (the customer/air-gap case), the same versioning
logic runs from the **GitLab-CI** wrapper — the logic lives in portable shell
scripts shared by both platforms, so there is one source of truth, two thin
adapters.
{% endhint %}

## How the groups are organized

GitLab's registries and permissions are **per project**, grouped under **groups**
(a group is the equivalent of a GitHub organization; projects are repositories).

### The `openg2p` group — shared, public

The top-level **`openg2p`** group holds the shared, public building blocks that
every repository and every customer consumes:

| Project | Purpose |
| ------- | ------- |
| `openg2p/packaging` | the central CI pipeline + versioning/changelog scripts (included at `@v1`) |
| `openg2p/charts` | the shared Helm catalogue — one browsable Rancher repo for all charts |
| `openg2p/versions` | the published changelogs (`.md`) |
| `openg2p/<product>` | a product's own repo + images (e.g. `openg2p/consent-manager`) |

### One group per customer / implementation — private

Each **customer or implementation gets its own group** (e.g. `cus1`), **private**,
with **membership and permissions scoped to that project's members**. Everything
that customer produces stays inside their namespace:

```
cus1                       GROUP — private; only CUS1 + assigned team are members
├── <product>              PROJECT — repo + images (private Container Registry)
└── charts                 PROJECT — CUS1's private chart catalogue (their Rancher repo)
```

The shared **`openg2p/packaging`** pipeline is included by customer repos across
the group boundary (it's public), so there is **no per-customer copy of the CI
logic** — only their artifacts are private and isolated. A group deploy token
scoped to the customer group governs who can pull.

## Moving a GitHub repo to GitLab

The reference migration is **`consent-manager`** — its GitLab form
(`openg2p/consent-manager`, with `.gitlab-ci.yml` at the repo root) is the working
exemplar to copy from.

The change is small: **bring the code over, then swap only the build/publish CI.**
Everything else (chart, Dockerfiles, `values.yaml` structure) stays identical.

### Steps

1. **Create the GitLab projects** (GitLab does not auto-create them on push): the
   product project for images, and — for the shared catalogue — reuse
   `openg2p/charts` (or a per-customer `charts`).
2. **Bring the code over.** Transplant the `develop` branch (with history) into
   the GitLab project — e.g. add the GitHub clone as a temporary remote and push
   `develop` + tags — or use GitLab's *Import from GitHub*.
3. **Swap the CI:**
   * **remove** `.github/workflows/build-publish.yml` (the GitHub Actions caller),
   * **add** `.gitlab-ci.yml` at the repo root that `include:`s
     `openg2p/packaging@v1`'s GitLab wrapper and declares this repo's images/chart.
4. **Point `values.yaml`** image `registry`/`repository` at the GitLab paths
   (`registry.gitlab.com/<group>/<project>/<image>`). CI still overwrites the
   tags at package time.
5. **Ensure the group CI/CD variables** exist (once per group): `HELM_PUBLISH_USER`
   / `HELM_PUBLISH_TOKEN` (deploy token with `write_package_registry`, for the
   cross-project chart push), `CHANGELOG_PROJECT` / `CHANGELOG_BRANCH` /
   `CHANGELOG_TOKEN` (a token with `write_repository`), and `OPENROUTER_API_KEY`.

### Copy-paste prompt

Paste this to an AI agent working in the repository (fill the bracketed values):

> Move this repository from GitHub to GitLab, exactly like `consent-manager`
> (`openg2p/consent-manager` on GitLab is the reference).
>
> 1. The GitLab project is `[<group>/<project>]`. Bring the **`develop`** branch
>    over **with history** (add the GitHub checkout as a temporary local remote,
>    fetch `develop`, and make it the GitLab repo's `develop`) — keep only
>    `develop`. Do **not** change any source other than the build/publish CI.
> 2. **Delete** `.github/workflows/build-publish.yml` (and the `.github/workflows`
>    folder if it holds nothing else).
> 3. **Create `.gitlab-ci.yml`** at the repo root that:
>    ```yaml
>    include:
>      - project: 'openg2p/packaging'
>        ref: v1
>        file: '/ci/gitlab/build-publish.yml'
>    variables:
>      PACKAGING_REF: v1
>      IMAGES: |
>        [ one entry per image: {"name","dockerfile","context"?,"pins"?} ]
>      CHART_PATH: [chart directory]
>      CHART_IMAGE_PATHS: '[ yq paths in values.yaml holding THIS org's image tags ]'
>      CHART_GITLAB_PROJECT: openg2p/charts
>    ```
>    Derive `IMAGES` from the `docker/**` and `ui/**` Dockerfiles; carry over any
>    `pins` (a build-arg that is a git ref) from the old GitHub caller. Derive
>    `CHART_IMAGE_PATHS` by grepping `values.yaml` for this org's image tags.
> 4. In `values.yaml`, set each OpenG2P image's `registry` to `registry.gitlab.com`
>    and `repository` to `<group>/<project>/<image-name>` (for images whose chart
>    template renders `repository:tag` directly, put the full path in `repository`).
> 5. Do NOT add versioning logic or pipeline stages to `.gitlab-ci.yml` — all logic
>    is in `openg2p/packaging`. Keep it minimal and declarative.
>
> Reference: `openg2p/consent-manager`'s `.gitlab-ci.yml`, and the docs at
> *OpenG2P GitLab Repositories* and *Publishing to GitLab*.

Group setup (projects, deploy tokens, CI/CD variables, Rancher URL) is a one-time
step per group — see [Publishing to GitLab → *What you set up on GitLab*](../../releases/helm-docker-versioning-and-ci/publishing-to-gitlab.md#what-you-set-up-on-gitlab-one-time).

## See also

* [**Publishing to GitLab**](../../releases/helm-docker-versioning-and-ci/publishing-to-gitlab.md) — the full technical detail: CI wrapper, registries, tokens, Rancher.
* [**Helm & Docker Versioning Strategy and CI**](../../releases/helm-docker-versioning-and-ci/README.md) — the one-version-per-commit scheme shared by both platforms.
