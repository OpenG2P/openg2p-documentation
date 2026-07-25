---
description: >-
  How OpenG2P versions Docker images and Helm charts, and the central CI that
  builds, versions, and publishes them from every service repo.
---

# Helm & Docker Versioning Strategy and CI

This is the current, authoritative description of how OpenG2P versions and publishes Docker images and Helm charts. It supersedes the older per-repo approach (two path-filtered workflows, `GITHUB_RUN_NUMBER` suffixes, `v`-prefixed tags) for every repo that has adopted the central pipeline.

The broader org-wide conventions (Odoo modules, Git repos in general) still live in [Versioning Conventions](../../operations/deployment/_archive/versioning.md); this page is specifically the **automated Helm + Docker** scheme.

## The one idea

> **One version per commit, shared by every artifact the repo produces.**

Every image and the chart built from a given commit carry the **same** version. A commit's version is derived purely from **git** — the branch/tag and the commit count — never from a file in the working tree.

Two forms of that version exist for every build:

* an **immutable** version (e.g. `0.0.0-develop.39`) that is never overwritten — this is what deployments pin to;
* a **moving alias** (`develop`) that always points at the newest build — a convenience for humans, never referenced by anything that needs to be stable.

## Two properties, kept separate

The word "frozen" used to bundle two different ideas together. Under this scheme they come apart, so keep them separate:

* **Immutable vs moving.** *Every published version is immutable* — `0.0.0-develop.39`, `1.0.0-rc.5` and `1.0.0` each resolve to the same bytes forever and are never overwritten. The only thing that *moves* is an **alias**: the `develop` docker tag, meaning "the newest develop build" (i.e. `latest`). Deployments pin immutable versions; the alias is a human convenience.
* **Release status.** Tagging `1.0.0` does **not** *make* the artifact immutable — it already was (the tag build **promotes the exact digest**, it does not rebuild). The tag adds *meaning*: "this is a supported, stable release." This matches SemVer — a bare `X.Y.Z` is a **stable release**; anything with a `-suffix` (`-develop.N`, `-rc.M`) is a **pre-release**, lower precedence, with no stability promise.

| Reference | Immutable? | What it is |
| --- | --- | --- |
| `develop` (docker tag) | no — moving alias | pointer to the newest develop build ("latest") |
| `0.0.0-develop.39` | **yes** | an immutable **develop build** (pre-release) |
| `1.0.0-rc.5` | **yes** | an immutable **release candidate** |
| `1.0.0` | **yes** | an immutable **release** — declared stable/supported |

So there is no "unfrozen version" — only **immutable versions** and **moving aliases**. What a bare `N.N.N` tag marks is a **release** (a semantic status), not the moment content stops changing.

{% hint style="info" %}
Internally the pipeline still emits a flag called `frozen=true` for a bare
`N.N.N`. Read it as **"is a release"** — it's what tells the build to *promote an
existing digest* rather than build a new one. The name is legacy; the meaning is
"release", not "the point at which it becomes immutable".
{% endhint %}

## Why we changed

The previous method had two problems that made "freezing" a release unreliable:

1. **Everything on `develop` was a moving target.** Images were tagged `develop` and overwritten on every push. A chart that referenced `develop` therefore changed underneath you even after you "froze" the chart version.
2. **Images and charts could drift apart.** The old dual workflows were _path-filtered_ — a backend change rebuilt the image but not the chart, so the newest chart kept pointing at a previous image. Freezing the chart version froze the label on the box, not its contents.

The new scheme fixes both: the moving alias still exists for convenience, but every build **also** publishes an immutable version, and images + chart are always produced **together at one version** — so pinning a chart version genuinely pins the whole tree (the chart and every image it references are immutable, together).

## The versioning, with examples

`N` below is `git rev-list --count HEAD` — the commit's ordinal. It is one-to-one with the commit, so `…​.39` and a specific commit are interchangeable (see [tracing a version](./#tracing-a-version-to-code)).

| You are on…                       | Version produced                             | Kind                | Chart published?     |
| --------------------------------- | -------------------------------------------- | ------------------- | -------------------- |
| `develop`                         | `0.0.0-develop.39`                           | develop build       | yes (rolling)        |
| release line branch `1.0`         | `1.0.0-rc.41` → after `1.0.0`, `1.0.1-rc.42` | release candidate   | yes                  |
| **tag** `1.0.0`                   | `1.0.0`                                      | **release** (stable)| yes                  |
| any other branch, e.g. `g2p-4567` | `0.0.0-g2p-4567.44`                          | test build          | **no** (images only) |

Every one of these is **immutable** once published (see [above](#two-properties-kept-separate)); the `Kind` column is *release status*, not mutability. Every value is valid [SemVer](https://semver.org) **and** a valid Docker tag. By the SemVer spec a bare `X.Y.Z` is a **stable release** and anything with a `-suffix` sorts strictly below it — so **"bare `N.N.N` means a release" is enforced by tooling, not just convention.**

{% hint style="info" %}
**No `v` prefix.** Release tags are the bare version, `1.0.0` — **not** `v1.0.0`. The bare 3-digit form _is_ the release signal. (The `v`-prefix is reserved for the packaging repo's own workflow tags like `v1`; see [CI pipeline](ci-pipeline.md).) The pipeline rejects a `v1.0.0` tag.
{% endhint %}

## Releases: tag, don't branch

{% hint style="success" %}
**Just want the steps?** See **[Cutting a release (how to tag)](cutting-a-release.md)** —
plain instructions, no concepts. This section explains *why* it works that way.
{% endhint %}

You do **not** create a `1.0.0` branch to cut a release. A branch is mutable — cutting the release `1.0.0` from one would let a later push overwrite an already-released artifact. A release must come from an **immutable ref** — a tag.

Instead:

1. Create the **release line** branch `1.0` off `develop`. Every push there publishes an `1.0.0-rc.N` (image + chart) that is fully built and testable.
2. When an RC is blessed, **tag that commit `1.0.0` with an annotated tag** and push it. The tag build **promotes** the already-tested image digest to `1.0.0` (a retag — no rebuild) and packages the chart at `1.0.0`.

   ```bash
   git tag -a 1.0.0 -m "First GA release.

   Highlights:

   - Redesigned onboarding (G2P-100)
   - Drops the legacy /v0 endpoints"
   git push origin 1.0.0
   ```

The tag is the "peg". You never work _on_ a tag; you tag a commit the release line already produced.

{% hint style="warning" %}
**Always tag releases with `git tag -a` (annotated), not a bare `git tag 1.0.0`.** An
annotated tag is a real git object that carries a **message** — and the changelog
engine renders that message **verbatim as a `Release notes` block at the top of the
release's page** (and on the repo's `CHANGELOG`). It's your one chance to say, in your
own words, *what this release is* — highlights, breaking changes, upgrade steps —
right where users look. A **lightweight** tag carries no message, so the page falls
back to just the commit list and AI summary. The message is markdown (leave a blank
line before a bullet list). See [Changelogs → Release notes](changelogs.md#release-notes-the-annotated-tag-message).
{% endhint %}

{% hint style="info" %}
**The `1.0` release-line branch is optional.** For a **one-off** release you can skip it and **tag `1.0.0` directly on `develop`** — the tag build promotes the `0.0.0-develop.N` build at that commit in exactly the same way. Create a `1.0` branch only when you need a **maintenance line** to cut later patches (`1.0.1`, `1.0.2`) independently while `develop` moves on.

Either way there is one requirement: tag a commit CI has **already built** (an existing `…-rc.N` or `0.0.0-develop.N`), because the release **promotes that digest** rather than rebuilding. So: **push the branch, let its build go GREEN, and only then tag that commit and push the tag.** Pushing the branch and the tag together starts two pipelines at once — the tag's promote step usually wins the race against the still-running build and fails with _"nothing to promote"_ (harmless: re-run it once the branch build is green). Tagging a commit CI never built fails the same way. (This applies to image repos; a chart-only repo like commons repackages fresh, so no prior build is needed.)
{% endhint %}

### How versions flow — a worked example

One release line, from the first RC to the second patch, all on the **same** branch `1.0`:

| Step | Ref / action | Published version |
| --- | --- | --- |
| work toward the release | branch `1.0` | `1.0.0-rc.3` |
| …more commits | branch `1.0` | `1.0.0-rc.4` |
| cut the release | **`git tag -a 1.0.0`** (annotated) | `1.0.0` (promoted from the tested RC — not rebuilt) |
| fix a bug (same branch) | branch `1.0` | `1.0.1-rc.5` |
| …more commits | branch `1.0` | `1.0.1-rc.6` |
| cut the patch | **`git tag -a 1.0.1`** (annotated) | `1.0.1` |

Two things to note:

* **The RC target advances automatically the instant `1.0.0` is tagged** — the next
  build on the same branch is `1.0.1-rc.N`, **not** another `1.0.0-rc.N`. The pipeline
  reads the highest `1.0.x` tag reachable from `HEAD` and targets the next patch. There
  is nothing to configure.
* You **keep using the same `1.0` branch** for the whole `1.0.x` series — one branch,
  many tags. You never create a branch per patch.

This ordering is deliberate and required for correctness:

```
1.0.0-rc.4  <  1.0.0  <  1.0.1-rc.5  <  1.0.1
```

By SemVer a pre-release sorts **below** its release. If the branch kept emitting
`1.0.0-rc.N` after `1.0.0` shipped, every bugfix build would sort as **older than the
release it fixes**, and `helm upgrade` would read it as a downgrade. Targeting
`1.0.1-rc.N` keeps every build newer than the last release and older than the next.

{% hint style="info" %}
The `rc.N` number is the commit ordinal (`git rev-list --count HEAD`) — it climbs
monotonically across the whole branch and **does not reset** per patch. Meanwhile
`develop` is unaffected and keeps publishing `0.0.0-develop.N` in parallel.
{% endhint %}

{% hint style="warning" %}
The pipeline **rejects a branch named `1.0.0`** with guidance to use branch `1.0`

* tag `1.0.0`. A release may only come from an **immutable ref** (a tag), never a mutable branch.
{% endhint %}

## The version lives in git, not in the code

Because the version is derived from git and injected at build/package time, the **version strings inside the source do not matter** for services:

* `Chart.yaml` keeps a static placeholder `version: 0.0.0-develop`; CI overrides it with `helm package --version <derived> --app-version <derived>`.
* `values.yaml` image tags are overwritten by CI at package time; the repo keeps a placeholder there too.
* A service's `__init__.py` / code version is **not** the artifact version and need not be bumped to release.

A fresh `helm install ./chart` from a clone therefore shows placeholders — that is expected. The **published** `.tgz` and the **pushed** image carry the real version (in `Chart.yaml` and in the image's OCI labels). Traceability lives in the artifact you ship, not in the working tree.

## Tracing a version to code

Given any image, read its provenance without pulling layers:

```bash
docker buildx imagetools inspect openg2p/openg2p-consent-manager:0.0.0-develop.39 \
  --format '{{ json .Image.Config.Labels }}'
```

It reports `org.opencontainers.image.source` (repo), `…​.revision` (exact commit), and `org.openg2p.pin.*` (the resolved commit of any external ref compiled in, e.g. `openg2p-fastapi-common`). Published charts carry the same `revision`/`source` annotations. And because `N` is the commit ordinal, the chart version alone maps back to a commit:

```bash
git rev-list --reverse origin/develop | sed -n '39p'   # -> the commit for .39
```

## What's on the rest of these pages

* [**Cutting a release (how to tag)**](cutting-a-release.md) — the step-by-step instructions for tagging and publishing a release. Start here when you actually need to ship one.
* [**CI pipeline**](ci-pipeline.md) — how the reusable workflow builds, versions, promotes and publishes; the `@v1` rollout model; a diagram.
* [**Changelogs**](changelogs.md) — where change notes are published, how to link them, the role of AI, and what happens when AI is unavailable.
* [**Onboarding a repo**](onboarding-a-new-repo.md) — a step-by-step guide **and a copy-paste prompt** to add this to any new repo, plus moving the `v1` tag.
* [**Publishing to GitLab**](publishing-to-gitlab.md) — publishing images + chart to GitLab (Container Registry + Helm Package Registry) instead of Docker Hub + gh-pages: why, how to switch a repo, the GitLab group/project/token setup, and running it all on a customer's own GitLab.
