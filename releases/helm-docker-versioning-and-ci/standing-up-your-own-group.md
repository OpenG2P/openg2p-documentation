---
description: >-
  How to reproduce the whole OpenG2P packaging, versioning and catalogue setup as
  an independent GitLab group — on gitlab.com or a self-hosted, air-gapped GitLab.
---

# Standing up your own group

Everything OpenG2P uses to version, build, publish and catalogue its software is portable. It is driven entirely by GitLab's own predefined `CI_*` variables, so the **same pipeline files run unchanged** on `gitlab.com` or on a customer's self-hosted instance — including an air-gapped one.

This page is the complete recipe: what to create, what to copy, which tokens to mint, and what to change. Follow it and a customer ends up with their own catalogue, their own registries and their own release process, owing nothing to OpenG2P's infrastructure at deploy time.

{% hint style="info" %}
**Who this is for.** An organisation that wants to run OpenG2P-derived software as their own product line, or a deployment that must live entirely inside their network. If you only want to consume OpenG2P's published charts, you do not need any of this — add the catalogue to Rancher and stop there.
{% endhint %}

## What you are reproducing

Four moving parts, three of them shared across the whole group:

| Part | What it is | How many |
| --- | --- | --- |
| **packaging** project | the shared CI: version derivation, build/publish wrapper, changelog engine, withdraw pipeline | one per group |
| **charts** project | the Helm Package Registry every chart publishes into — one Rancher repo URL | one per group |
| **versions** project | the catalogue: generated markdown + a GitLab Pages site | one per group |
| **service** projects | the actual software; each one includes the wrapper and declares only what it contains | many |

Images do **not** get a shared project: each service publishes into its own project's Container Registry, derived from `CI_REGISTRY_IMAGE`.

## Prerequisites

* A GitLab instance — `gitlab.com` or self-managed (CE is sufficient; none of this needs Premium).
* **Runners.** A self-managed GitLab ships with none, and pipelines sit `pending` until you add one. The build job needs the **docker executor in privileged mode** (it uses `docker:dind`). See the runner setup guide.
* Helm 3 and a Kubernetes cluster, for consuming what you publish.

## Step 1 — create the group

The **top-level group is the organisation**. GitLab has no separate "organisation" object; a group is it.

Create your root group (e.g. `acme`), then subgroups mirroring how your software is organised — `acme/registry`, `acme/platform-services`, and so on. Subgroups are worth using from the start: permissions, CI/CD variables and registries all inherit down the tree, and moving a project later changes its image path.

## Step 2 — create the three shared projects

Inside the root group:

1. `acme/packaging` — the shared CI.
2. `acme/charts` — the chart catalogue. Nothing is committed here; it exists to own a Helm Package Registry.
3. `acme/versions` — the catalogue site.

Set visibility deliberately. **Public** projects allow anonymous image and chart pulls, which removes the need for pull secrets in the cluster. **Private** projects need a read-only deploy token wired into Rancher and an `imagePullSecret` in Kubernetes.

## Step 3 — seed the packaging project

Copy the contents of [`openg2p/packaging`](https://gitlab.com/openg2p/packaging) into `acme/packaging`. A fork, a mirror, or a plain `git push` of a clone all work — a fork keeps you able to pull upstream improvements later, which is what most customers want.

What you are copying:

| Path | Purpose |
| --- | --- |
| `ci/version/derive-version.sh` | derives the one version for a commit from git alone |
| `ci/gitlab/build-publish.yml` | the wrapper every service project includes |
| `ci/gitlab/withdraw.yml` | the central withdrawal pipeline |
| `ci/gitlab/ensure-release.sh` | creates/reads a GitLab Release for release notes |
| `ci/changelog/*.sh` | the catalogue engine (assemble, summarise, render, index) |
| `ci/changelog/config.yml` | AI model + Jira link configuration |
| `ci/chart/inherit-questions.sh` | regenerates `questions.yaml` for wrapper charts |
| `ci/withdraw/*.sh` | withdrawal safety rules and tombstones |
| `ci/migrate/github-to-gitlab.sh` | migrates a repo from GitHub |
| `ci/samples/` | caller stubs and the versions-site scaffold |
| `ci/*/test-*.sh` | the test suites — run them after any change |

**Two edits are mandatory**, in `ci/gitlab/build-publish.yml` and `.github/workflows/build-publish.yml`:

```yaml
PIPELINE_NAMESPACE: "acme"          # was "openg2p"
PACKAGING_PROJECT: "acme/packaging" # was "openg2p/packaging"
```

`PIPELINE_NAMESPACE` is the supply-chain guard: a pipeline creates **no jobs at all** outside that root namespace, so a fork of one of your service repos cannot build or publish using your credentials. Leaving it as `openg2p` would disable every pipeline in your group.

Then tag the ref your services will pin:

```bash
git tag -f v1 && git push -f origin v1
```

Services `include:` the wrapper at `ref: v1`, so moving that tag is how you roll policy changes out to everyone at once.

{% hint style="warning" %}
If `acme/packaging` is **private**, allow other projects' job tokens to clone it: *Settings → CI/CD → Job token permissions*, add the group. Otherwise every service pipeline fails at the `git clone .packaging` step.
{% endhint %}

## Step 4 — set up the versions site

Copy `ci/samples/versions/` from the packaging project into `acme/versions`: `build.sh`, `.github/workflows/build-publish.yml`, `assets/`, `.gitignore`. Push to its default branch and GitLab Pages publishes the catalogue at `https://acme.gitlab.io/versions/` (or your instance's Pages domain).

Everything else in that repo is generated: each service's `changelog` job writes `<module>/versions/*.md` and the aggregate. The Pages job re-renders the aggregates on every push, so hand-edited files like `.marked` take effect immediately.

## Step 5 — tokens and CI/CD variables

This is the part that cannot be copied, because tokens are per-instance. Set these as **group-level CI/CD variables** on `acme` so every project inherits them.

| Variable | What it is | Scope needed | Where | Required? |
| --- | --- | --- | --- | --- |
| `HELM_PUBLISH_USER` | username for the chart upload | — | group | yes — set to the token's username |
| `HELM_PUBLISH_TOKEN` | pushes charts into `acme/charts` | `write_package_registry` on `acme` | group, **masked** | yes |
| `CHANGELOG_PROJECT` | e.g. `acme/versions` | — | group | yes, or no catalogue is written |
| `CHANGELOG_BRANCH` | that project's default branch | — | group | yes if not `main` |
| `CHANGELOG_TOKEN` | pushes catalogue commits | `write_repository` on `acme/versions` | group, **masked** | yes |
| `OPENROUTER_API_KEY` | AI change summaries | — | group, **masked** | optional |
| `WITHDRAW_TOKEN` | deletes charts, image tags, catalogue entries | `api` on `acme` | **`acme/packaging` only**, masked | only for withdrawal |

Two of these deserve explanation.

**Why `HELM_PUBLISH_TOKEN` is needed at all.** Most publishing uses `CI_JOB_TOKEN`, which GitLab mints per job — no configuration, no secret to leak. That works for pushing images, because a job pushing to *its own* project's registry is authorised by default. The chart is different: it goes to `acme/charts`, a **different project**, and a job token carries no authority there. Hence a real token.

**Why `WITHDRAW_TOKEN` lives on one project.** It can delete published artifacts across the whole group. It belongs on `acme/packaging` and nowhere else, so exactly one project can invoke destructive operations.

{% hint style="danger" %}
Do not mark these **Protected** unless every branch that runs pipelines is protected. A protected variable is simply absent from jobs on unprotected refs, and the failure looks like a missing-credentials bug rather than a configuration choice.
{% endhint %}

Nothing else needs a secret. Image pushes use `CI_REGISTRY_USER` / `CI_REGISTRY_PASSWORD`, which GitLab injects automatically.

## Step 6 — onboard your service projects

For each project, add a `.github/workflows/build-publish.yml` declaring only what that repo contains:

```yaml
include:
  - project: 'acme/packaging'
    ref: v1
    file: '/ci/gitlab/build-publish.yml'

variables:
  PACKAGING_REF: v1
  IMAGES: |
    [ {"name":"my-api","dockerfile":"docker/api/Dockerfile"} ]
  CHART_PATH: helm/my-chart
  CHART_IMAGE_PATHS: '[".api.image.tag"]'
  CHART_GITLAB_PROJECT: acme/charts
```

`ci/samples/gitlab-caller.yml` in the packaging project is a fuller commented example of every field, and `ci/samples/library.gitlab-ci.yml` covers a code library that builds no image or chart. Those two files are the reference for the GitLab stub.

Migrating an existing GitHub repo? `ci/migrate/github-to-gitlab.sh` translates a repo already on the central GitHub pipeline; for anything else, pass a hand-written config with `--ci`.

## Step 7 — consume the catalogue

Add one Helm repository to Rancher (or `helm repo add`):

```
https://gitlab.acme.internal/api/v4/projects/<charts-project-id>/packages/helm/stable
```

Every chart the group publishes appears there. Private project? Add the read-only deploy token as repository credentials.

## Running air-gapped

The pipeline itself needs no internet — but the *containers it runs in* are pulled from public registries, and a few steps fetch tools. Before an air-gapped install, mirror these into the customer's registry and repoint them:

| Reached by | What for |
| --- | --- |
| `registry-1.docker.io` | `docker:24`, `docker:24-dind`, `alpine:3.20`, `alpine/helm:3.14.4`, `node:20-alpine` |
| `dl-cdn.alpinelinux.org` | `apk add` in nearly every job |
| `github.com` | the pinned `yq` binary; also `git ls-remote` when a build pins a dependency by ref |
| `openrouter.ai` | AI change summaries |

Practical steps for a fully disconnected instance:

1. **Mirror the job images** into `acme/`'s registry and change the `image:` lines in `build-publish.yml` accordingly.
2. **Vendor `yq`** — commit the binary into the packaging project, or bake it into a mirrored image, and replace the `curl` that downloads it.
3. **Set `CHANGELOG_SKIP_AI: "true"`** as a group variable. The changelog engine falls back to commit messages and publishes normally; no external call is attempted.
4. **Drop or repoint image pins.** A pin resolving `https://github.com/...` to a SHA will fail; either remove the `pins` block or point it at an internal mirror.
5. **Use an internal Jira base**, or clear `jira_base` in `ci/changelog/config.yml`, so ticket links do not point outside the network.

## Verifying the setup

In order, because each step depends on the previous one:

1. Run the test suites in `acme/packaging`: `ci/version/test-derive-version.sh`, `ci/changelog/test-changelog.sh`, `ci/withdraw/test-withdraw.sh`. They need no network and no GitLab.
2. Push a commit to a service project's develop branch. Expect `version → build-images → chart → changelog`, all green.
3. Confirm the image tag `0.0.0-develop.N` appears in that project's Container Registry.
4. Confirm the chart appears under *Packages* in `acme/charts`.
5. Confirm a version page appears on the catalogue site.
6. Cut a release: branch `1.0`, push, then tag `1.0.0`. The release must **promote** the existing digest, not rebuild — the page says so explicitly.

If step 2 hangs at `pending`, the runner is missing or refuses untagged jobs. If it fails at the dind handshake, the runner is not privileged.

## What to change, at a glance

| In OpenG2P | In your group |
| --- | --- |
| `openg2p` (root namespace) | `acme` |
| `PIPELINE_NAMESPACE: "openg2p"` | `PIPELINE_NAMESPACE: "acme"` |
| `openg2p/packaging` | `acme/packaging` |
| `openg2p/charts` | `acme/charts` |
| `openg2p/versions` | `acme/versions` |
| `https://openg2p.github.io/versions/` | your Pages domain |
| OpenG2P's tokens | your own, minted on your instance |

## Keeping up with upstream

If you forked `openg2p/packaging`, you can pull improvements later. The rule is the same one OpenG2P follows internally:

> Moving `v1` may change **how** artifacts are built and published. It must never change **what version string a given commit gets.**

Fixing a bug, adding a variable with a default, improving a label — safe under `v1`. Changing the version *format* renames what a commit is called and needs a `v2`, or it breaks the immutability of versions already published from long-lived branches.

Cut an immutable peg first (`git tag v1.2.0`), canary it by pinning one project to `@v1.2.0`, then move `v1`. Keep every peg forever: it answers "which policy built this?" and is how you roll back (`git tag -f v1 v1.1.0 && git push -f origin v1`). The [`v1` maintenance section](onboarding-a-new-repo.md#maintaining-the-pipeline-moving-v1) has the fuller version of this rule.

Keep your `PIPELINE_NAMESPACE` and project-path edits on a branch you rebase onto upstream, rather than editing after each merge — those two values are the only things that must differ.

## See also

* [CI pipeline](ci-pipeline.md) — what each job does and the guarantees it gives
* [Publishing to GitLab](publishing-to-gitlab.md) — layout, registries, Rancher
* [Onboarding a repo](onboarding-a-new-repo.md) — putting one repo on the pipeline, and the `v1` rollout rule
* [Changelogs](changelogs.md) — how the catalogue is generated
* [Withdrawing a version](withdrawing-a-version.md) — deleting a published develop build
* [Marking a known-good build](marking-a-known-good-build.md) — notes without releasing
