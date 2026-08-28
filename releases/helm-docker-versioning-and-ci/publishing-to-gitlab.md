---
description: >-
  Publishing a service's Docker images and Helm chart to GitLab (Container
  Registry + Helm Package Registry) instead of Docker Hub + gh-pages — why, how
  to enable it per repo, what to set up on GitLab,
---

# Publishing to GitLab

The same central pipeline ([CI pipeline](ci-pipeline.md)) can publish a repo's artifacts to **GitLab** instead of the classic Docker Hub + `openg2p-helm` gh-pages targets. Everything about versioning is unchanged — one immutable version per commit, promote-on-release, changelogs — only **where the images and chart land** changes. This page covers the GitLab target: the reasoning, how to switch a repo onto it, what you set up on GitLab, and how a customer takes the whole thing to their own GitLab instance.

{% hint style="info" %}
**Source and CI still run on GitHub.** Today the code lives on GitHub and the build runs in GitHub Actions; only the **publish** step targets GitLab. When a repository is itself _hosted_ on GitLab (the customer / air-gap case), the same versioning logic — which lives in portable shell scripts, not GitHub-specific YAML — will run from an equivalent **GitLab CI** wrapper. That wrapper is planned; the scripts it will call already exist.
{% endhint %}

## Why GitLab — the four requirements it satisfies

The classic targets (Docker Hub for images, a gh-pages `index.yaml` Helm repo for charts) work, but they don't meet four goals we want for private/customer delivery. GitLab meets all four in **one system**:

| # | Requirement                                              | How GitLab satisfies it                                                                                                                                                    |
| - | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | **Chart + its images co-located** and versioned together | A GitLab **project** holds both a Container Registry (images) and a Helm Package Registry (chart) — one place, one login.                                                  |
| 2 | **One Rancher repo lists all charts + versions**         | GitLab's Helm registry is **index-based** (`index.yaml`), so Rancher adds a single HTTP Helm repo URL and browses every chart and version — no per-chart OCI entry.        |
| 3 | **Any artifact can be private**                          | Visibility is **per project** (Public / Internal / Private) with per-project robot/deploy tokens — real tenant isolation, unlike Docker Hub's one-free-private-repo limit. |
| 4 | **One login, not several**                               | Images and charts authenticate to the **same GitLab**; a customer running their own GitLab has a single system for source, registry and charts.                            |

GHCR was evaluated and rejected for requirement #2 specifically: **GHCR disables the registry catalog API**, so Rancher cannot enumerate charts from it (you would add each chart as a separate OCI repo). GitLab's index-based Helm registry is what makes the single browsable Rancher repo possible.

## Classic vs GitLab: choosing per repo

The publish target is **declarative** — a repo chooses by which inputs its caller stub sets. The reusable `@v1` workflow supports three targets:

| Target                | Images go to           | Chart goes to                          | Select it by setting                                     |
| --------------------- | ---------------------- | -------------------------------------- | -------------------------------------------------------- |
| **Classic** (default) | Docker Hub `openg2p/*` | `openg2p-helm` gh-pages (`index.yaml`) | nothing — the defaults                                   |
| **GHCR**              | `ghcr.io`              | OCI push (`oci://…`)                   | `chart-oci-repo`                                         |
| **GitLab**            | `registry.gitlab.com`  | GitLab Helm Package Registry           | `registry: registry.gitlab.com` + `chart-gitlab-project` |

There is no global switch. A repo stays classic until its stub opts into GitLab, so you migrate one service at a time. (`consent-manager` is the reference GitLab repo; the rest are still classic.)

{% hint style="info" %}
**Public reach vs private co-location.** Docker Hub keeps genuine advantages for _public_ images — the default `docker pull openg2p/x`, discoverability, and the Docker-Sponsored OSS program (unlimited pulls). GitLab wins for **private / customer / air-gap** delivery. A sensible split is: keep broadly-consumed public images classic, and use GitLab for the private lane.
{% endhint %}

## How it's laid out on GitLab

GitLab's registries are **per project**, so the layout separates by purpose:

```
openg2p                         GROUP  (= the "organization"; holds the deploy token)
├── consent-manager             PROJECT — the product's images
│     Container Registry:
│       registry.gitlab.com/openg2p/consent-manager/consent-manager-api
│       registry.gitlab.com/openg2p/consent-manager/consent-manager-ui
│       registry.gitlab.com/openg2p/consent-manager/consent-manager-sanity
├── charts                      PROJECT — the SHARED chart catalogue
│     Helm Package Registry:
│       openg2p-consent-manager  0.0.0-develop.44, 1.0.0, …
│       <every other repo's chart lands here too>
└── customers/…                 SUBGROUP — optional per-customer private projects
```

* **Images** → the **product's own project** Container Registry.
* **Chart** → a **single shared `charts` project's** Helm Package Registry. _Every_ repo points its chart here, so Rancher's one repo lists them all. (This is the key to requirement #2 — do not give each product its own chart project, or Rancher is back to N repos.)

{% hint style="warning" %}
A GitLab project has **one visibility**. The shared `charts` project is therefore all-public _or_ all-private. Keep it matching your general catalogue's lane, and give a **private customer their own project** (e.g. `openg2p/nsr`, with `chart-gitlab-project: openg2p/nsr`) — that becomes _their_ separate Rancher repo, isolated by their own read token.
{% endhint %}

### Group vs Project (for those coming from GitHub)

| GitLab       | GitHub equivalent | Holds artifacts?                                          |
| ------------ | ----------------- | --------------------------------------------------------- |
| **Group**    | Organization      | no — container + members + the deploy token               |
| **Subgroup** | (no equivalent)   | no — nested container, useful to scope a customer         |
| **Project**  | Repository        | **yes** — Container Registry + Package Registry live here |

So **OpenG2P the organization is a GitLab&#x20;**_**Group**_, and each product (and the `charts` catalogue) is a **Project** under it.

## Enabling GitLab for a service (caller-stub changes)

Switching a repo's stub from classic to GitLab is a few `with:` inputs plus two secrets. Using `consent-manager` as the model:

```yaml
jobs:
  build-publish:
    # packages: write is unused by the GitLab path, but the shared @v1 reusable's
    # images/chart jobs DECLARE it (for the GHCR path). GitHub requires the caller
    # to grant at least what nested jobs request — omitting it fails at startup.
    permissions:
      contents: read
      packages: write
    uses: openg2p/openg2p-packaging/.github/workflows/build-publish.yml@v1
    with:
      # ── target: GitLab ──
      registry: registry.gitlab.com            # images -> GitLab Container Registry
      namespace: openg2p/consent-manager        # <group>/<product-project>; images land under it
      chart-gitlab-project: openg2p/charts      # SHARED catalogue project (one Rancher repo for all)
      artifact-source: registry.gitlab.com/openg2p   # cosmetic, shown in the changelog catalogue

      # images: drop any Docker Hub `repo` override — the path is
      # registry/<namespace>/<name>, so `name` alone places the image.
      images: |
        [ {"name": "consent-manager-api", "dockerfile": "docker/consent-manager-api/Dockerfile", "pins": […]},
          {"name": "consent-manager-sanity", "dockerfile": "docker/consent-manager-sanity/Dockerfile"},
          {"name": "consent-manager-ui", "dockerfile": "ui/Dockerfile", "context": "ui"} ]

      chart-path: deployment/charts/openg2p-consent-manager
      chart-image-paths: |
        [".ui.image.tag", ".consentManagerApi.image.tag", ".sanity.image.tag"]
      packaging-ref: v1
    secrets:
      gitlab_registry_user: ${{ secrets.gitlab_registry_user }}
      gitlab_registry_token: ${{ secrets.gitlab_registry_token }}
      # still passed (unused by GitLab, required by the reusable's signature):
      docker_hub_actor: ${{ secrets.docker_hub_actor }}
      docker_hub_token: ${{ secrets.docker_hub_token }}
      OPENG2P_BOT_GITHUB_PAT: ${{ secrets.OPENG2P_BOT_GITHUB_PAT }}
      OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
```

You must also point the chart's `values.yaml` image entries at the GitLab paths (`registry.gitlab.com/openg2p/<product>/<image>`) so a plain `helm install` resolves them. CI still overwrites the **tags** at package time; you are changing the **registry/repository** portion.

The GitLab inputs the reusable workflow understands:

| Input                           | Meaning                                                                                                      | Default              |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------ | -------------------- |
| `registry: registry.gitlab.com` | routes image auth to the GitLab deploy token                                                                 | `docker.io`          |
| `namespace`                     | `<group>/<project>` the images live under                                                                    | `openg2p`            |
| `chart-gitlab-project`          | GitLab project (path) whose Helm registry receives the chart; **its presence selects the GitLab chart path** | `''`                 |
| `chart-gitlab-host`             | GitLab base URL — set for a self-hosted instance                                                             | `https://gitlab.com` |
| `chart-gitlab-channel`          | Helm channel segment in the repo-add URL                                                                     | `stable`             |

The chart push includes the same **immutability guard** as every other target — it refuses to overwrite a version already in the registry.

## What you set up on GitLab (one-time)

1. **Group** — `openg2p` (this _is_ the organization; the deploy token attaches here so it covers every project beneath it).
2. **Projects** — create them (GitLab does **not** auto-create a project on push; it only auto-creates the image path _within_ an existing project):
   * one **per product** for images (e.g. `consent-manager`),
   * one **shared `charts`** for the chart catalogue. Set each project's **visibility** (Public / Private) as the lane requires.
3. **Deploy token (push)** — on the **group**, _Settings → Repository → Deploy tokens_ (or _Settings → Access tokens_ → a Group Access Token if deploy tokens are restricted). Scopes:
   * `read_registry`, `write_registry` — images
   * `read_package_registry`, `write_package_registry` — chart Copy the username + token into **GitHub** as repo/org secrets `gitlab_registry_user` and `gitlab_registry_token`.
4. **Pull side** — nothing if the projects are **Public** (pulls are anonymous; only the writing CI authenticates). For a **Private** project, mint a **read-only** deploy token (`read_registry`, `read_package_registry`) and give it to Rancher (repo credentials) and Kubernetes (as an `imagePullSecret`).

{% hint style="info" %}
Pushing always authenticates, even to a public project — so the push token is required regardless of visibility. Pulling from a **public** project is open to all; only a **private** project needs the pull token.
{% endhint %}

## Adding the catalogue to Rancher

Add **one** repository (type: **HTTP Helm** — "URL to an index generated by Helm", _not_ OCI). Use the **numeric project ID**, not the `group/project` path:

```
https://gitlab.com/api/v4/projects/<CHARTS_PROJECT_ID>/packages/helm/stable
```

Find the numeric ID on the `charts` project's overview page (or `curl -s https://gitlab.com/api/v4/projects/<group>%2Fcharts | grep '"id"'`).

{% hint style="warning" %}
**Use the numeric ID, or chart pages fail with `gzip: invalid header`.** GitLab's `index.yaml` gives each chart tarball as a _relative_ URL. With the encoded-path form (`…/projects/openg2p%2Fcharts/…`), Rancher mangles the `%2F` when resolving that relative URL, fetches an error page instead of the `.tgz`, and gunzip fails. The listing still works (that's read straight from the index), which is why the chart _appears_ but won't _open_. The numeric-ID form has no `%2F` to mangle. `helm` on the CLI handles the encoded path fine — this quirk is Rancher-specific.
{% endhint %}

## Customer / air-gap: the same thing on their own GitLab

Because the model is "one GitLab holds source, images and charts," a customer can run the **entire** thing on a **self-hosted GitLab** — ideal for on-prem, air-gapped deployments:

* Point the pipeline at their instance. Under the GitLab-native pipeline this needs no host settings at all — everything is driven by GitLab's predefined `CI_*` variables, so the same files run unchanged on any instance; only the group name and the tokens differ.

{% hint style="info" %}
**Full recipe:** [Standing up your own group](standing-up-your-own-group.md) covers every project, token, permission and air-gap consideration needed to reproduce this setup end to end.
{% endhint %}

* Their GitLab hosts the images (Container Registry) and the chart catalogue (Helm Package Registry); their Rancher adds the one HTTP Helm repo URL on that host.
* Nothing reaches the public internet at deploy time — the whole supply chain is inside their network.

This is the strategic reason for choosing GitLab over a dedicated registry (Harbor/Zot): those solve only the _registry_, leaving source and CI to be stood up separately in the air-gap. **GitLab is one system for all of it**, so a customer installs one thing. As customer repositories move onto GitLab, their CI runs there too (via the GitLab-CI wrapper over the same portable versioning scripts) — at which point source, CI, registry and charts are all one login on one self-hosted platform.

## See also

* the migration notes — the overview: what's on GitLab, org/customer groups, and moving a repo there.
* [CI pipeline](ci-pipeline.md) — the reusable workflow, jobs, and the `@v1` rollout model.
* [Onboarding a repo](onboarding-a-new-repo.md) — putting a repo on the pipeline (classic target).
* [Strategy & versioning](./) — one-version-per-commit and promotion.
