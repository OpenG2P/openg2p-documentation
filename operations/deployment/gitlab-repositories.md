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

## Migrating a GitHub repo to GitLab

The change is small: **bring the code over, then swap only the build/publish CI.**
Everything else (chart, Dockerfiles, `values.yaml` structure) stays identical.
`openg2p/consent-manager` is the working exemplar.

### Use the script (repos already on the central pipeline)

A repo on the [central pipeline](../../releases/helm-docker-versioning-and-ci/ci-pipeline.md)
already declares its images/pins/chart in its GitHub caller's `with:` block, so the
migration is a **mechanical translation** — no AI, no re-derivation. Run
**`ci/migrate/github-to-gitlab.sh`** from `openg2p/packaging`:

```bash
# dry-run (default): prints the generated .gitlab-ci.yml + diff, changes nothing
bash ci/migrate/github-to-gitlab.sh \
  --source openg2p/<repo> \            # a GitHub owner/repo, or a local checkout path
  --target openg2p/pbms/<name> \       # the GitLab project to create
  --branch develop --visibility public

# do it for real
GITLAB_TOKEN=<PAT with 'api' scope> bash ci/migrate/github-to-gitlab.sh … --apply
```

It creates the project, transplants the branch **with history** (+ tags), translates
the caller into `.gitlab-ci.yml`, repoints `values.yaml` at the GitLab image paths,
and sets the default branch + visibility.

{% hint style="warning" %}
**Caveats.**

* **Create the group/subgroup first** — the script creates the *project*, not the group.
* **Only repos on the central pipeline.** Anything still on old-style workflows
  (`docker-build*.yml` / `helm-publish.yml`) is **refused** — there is no `with:`
  block to translate. Onboard it first
  ([Onboarding a repo](../../releases/helm-docker-versioning-and-ci/onboarding-a-new-repo.md)),
  or hand-write `.gitlab-ci.yml` using the prompt below.
* **`--apply` force-pushes** the branch. It is meant for a fresh/empty target.
* **Other GitHub workflows are left alone** (tests, pre-commit). They are **inert on
  GitLab** — port them to `.gitlab-ci.yml` jobs separately or lose that CI.
* **Flagged image paths are never guessed.** The link from a `chart-image-paths`
  entry to an image name isn't declared anywhere; the script infers it from the
  current `repository` value and **flags** whatever it can't match — fix by hand.
* **Always dry-run first** and read the generated `.gitlab-ci.yml` (especially `pins`).
{% endhint %}

### Retiring the GitHub source

Once the GitLab pipeline is **green**, retire the old repo — a **separate step**, so
you never archive GitHub before knowing GitLab works:

```bash
# dry-run, then --apply
bash ci/migrate/github-to-gitlab.sh \
  --source openg2p/<repo> --target openg2p/pbms/<name> --retire-source [--apply] \
  [--title "OpenG2P SPAR"] [--docs "Platform Services → SPAR"]
```

It replaces the README with a *"moved to GitLab"* note (a `> [!IMPORTANT]` callout,
nothing else), **deletes `build-publish.yml` in the same commit**, pushes, then
archives the repo.

The note's title comes from **`--title`**, else the existing README's H1, else a
title-cased slug. Pass `--title` when the slug has an acronym (`spar` → *"Spar"*,
so use `--title "OpenG2P SPAR"`); `--docs` adds a documentation breadcrumb.

{% hint style="info" %}
Deleting the workflow **in the same commit** is what stops that very push from
building and publishing a new docker/helm version — GitHub evaluates workflows from
the pushed commit, so a workflow that isn't there can't run. Archiving afterwards
disables Actions entirely.

Needs `gh` authenticated with **admin** on the repo. If the default branch is
**protected** the push is rejected — unprotect it or apply the note by hand.
Archiving is reversible (un-archive), but it is outward-facing: only do it after
the GitLab side is verified.
{% endhint %}

### Once per group (not per repo)

The `charts` and `versions` projects, the group deploy token, and the group CI/CD
variables — see [Publishing to GitLab → *What you set up on GitLab*](../../releases/helm-docker-versioning-and-ci/publishing-to-gitlab.md#what-you-set-up-on-gitlab-one-time).

### Fallback: the manual prompt

Only for repos the script refuses (**not on the central pipeline**, so there is
nothing to translate) — here the config must be *derived* from the Dockerfiles and
chart. Paste this to an AI agent working in the repository (fill the bracketed
values). Otherwise, prefer the script above.

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

## Handing a customer group over to a customer-hosted GitLab

When a customer takes their `cusN` group onto **their own GitLab**, there are two
shapes, and they differ almost entirely in **transport**:

* **Cloud** — their own GitLab.com account/namespace. Both ends are reachable, so
  everything can be copied in one hop.
* **On-prem / air-gapped** — their GitLab lives inside their network. It is
  **reachable from their cluster**, so once artifacts are in it everything resolves
  normally. Only two things are hard: getting data *in*, and build-time fetches to
  the **public internet**.

The procedure below is **manual** — do it once, carefully. (Automation can come
later; the fiddly parts are enumeration and transport, not logic.)

### What GitLab moves — and what it doesn't

| Moves via group export/import | Does **not** move |
| ----------------------------- | ----------------- |
| subgroups, repos (**all branches + tags**), issues, MRs, labels, members | **container images**, **Helm charts**, **CI/CD variables**, **tokens**, Pages |

{% hint style="warning" %}
**Copy the artifacts — do not rebuild them.** A rebuild is not the digest that was
tested, and a release tag **promotes an existing RC digest**: against an empty
registry it fails with *"nothing to promote"*.
{% endhint %}

### Step 1 — Mirror the shared pipeline

Their instance needs **`openg2p/packaging` at the same path**, with the `v1` tag —
otherwise every repo's `include:` fails. Because the wrapper uses `CI_*` variables
and a project-path `include:`, this is what lets every `.gitlab-ci.yml` work
**unchanged** on the new host.

```bash
git clone --mirror https://gitlab.com/openg2p/packaging.git packaging.git
# air-gapped: carry packaging.git in, then run this inside
git -C packaging.git push --mirror https://<their-host>/openg2p/packaging.git
```

### Step 2 — Move the group

* **Cloud:** their GitLab → *Groups → New group → **Import group*** ("direct
  transfer"), pointing at `gitlab.com` with a PAT.
* **Air-gapped:** `cusN` → *Settings → General → Advanced → **Export group*** →
  download the tarball → carry it in → *New group → Import*.

### Step 3 — Move the container images

List every image and tag per project (`Deploy → Container Registry`), skipping any
`-deletion_scheduled-` project — those are soft-deleted and their artifacts are dead
weight.

```bash
# Cloud — one hop
skopeo copy \
  --src-creds  <user>:<read-token>  --dest-creds <user>:<write-token> \
  docker://registry.gitlab.com/cus1/<project>/<image>:<tag> \
  docker://registry.<their-host>/cus1/<project>/<image>:<tag>

# Air-gapped — export to a portable OCI layout, carry it in, then load
skopeo copy --src-creds <user>:<read-token> \
  docker://registry.gitlab.com/cus1/<project>/<image>:<tag> oci:./bundle/<image>:<tag>
skopeo copy --dest-creds <user>:<write-token> \
  oci:./bundle/<image>:<tag> docker://registry.<their-host>/cus1/<project>/<image>:<tag>
```

Repeat per tag. Include the immutable versions **and** the `develop` alias.

### Step 4 — Move the Helm charts

List the versions in `cusN/charts` (*Deploy → Package Registry*), then download and
re-upload each:

```bash
curl -H "PRIVATE-TOKEN: <read-token>" \
  "https://gitlab.com/api/v4/projects/<charts-id>/packages/helm/stable/charts/<name>-<version>.tgz" \
  -o <name>-<version>.tgz

curl --user oauth2:<write-token> --form "chart=@<name>-<version>.tgz" \
  "https://<their-host>/api/v4/projects/<their-charts-id>/packages/helm/api/stable/charts"
```

### Step 5 — Recreate tokens and variables

They are secrets, so nothing exports them. On their group: a **deploy token**
(`read/write_registry`, `read/write_package_registry`), a token with
`write_repository` for the changelog, and the group CI/CD variables
(`HELM_PUBLISH_USER` / `HELM_PUBLISH_TOKEN`, `CHANGELOG_PROJECT` /
`CHANGELOG_BRANCH` / `CHANGELOG_TOKEN`, `OPENROUTER_API_KEY`). Register **runners**.

### Step 6 — Repoint Rancher

Their `charts` project gets a **new numeric id**, so the repo URL changes:
`https://<their-host>/api/v4/projects/<their-charts-id>/packages/helm/stable`.

### Air-gapped only — mirror the build-time internet dependencies

Their GitLab is reachable from their cluster, so anything already in it is fine.
Only these reach the public internet during a build — mirror them in, then repoint:

| Dependency | Used by | Fix |
| ---------- | ------- | --- |
| `openg2p-fastapi-common` (GitHub) | image `pins` | mirror it in; update the pin's `repo` |
| Dockerfile base images | every build | dependency proxy / mirror |
| `common`, `postgres-init` charts | `helm dep up` | mirror into their chart registry |
| `yq`, `marked` downloads | chart + Pages jobs | pre-bake a CI image |
| OpenRouter | AI changelog | set `CHANGELOG_SKIP_AI=true` (degrades to human notes) |

## See also

* [**Publishing to GitLab**](../../releases/helm-docker-versioning-and-ci/publishing-to-gitlab.md) — the full technical detail: CI wrapper, registries, tokens, Rancher.
* [**Helm & Docker Versioning Strategy and CI**](../../releases/helm-docker-versioning-and-ci/README.md) — the one-version-per-commit scheme shared by both platforms.
