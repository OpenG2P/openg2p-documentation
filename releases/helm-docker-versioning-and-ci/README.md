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

## Why we changed

The previous method had two problems that made "freezing" a release unreliable:

1. **Everything on `develop` was a moving target.** Images were tagged `develop` and overwritten on every push. A chart that referenced `develop` therefore changed underneath you even after you "froze" the chart version.
2. **Images and charts could drift apart.** The old dual workflows were _path-filtered_ — a backend change rebuilt the image but not the chart, so the newest chart kept pointing at a previous image. Freezing the chart version froze the label on the box, not its contents.

The new scheme fixes both: the moving tag still exists for convenience, but every build **also** publishes an immutable version, and images + chart are always produced **together at one version**, so a frozen chart genuinely freezes the whole tree.

## The versioning, with examples

`N` below is `git rev-list --count HEAD` — the commit's ordinal. It is one-to-one with the commit, so `…​.39` and a specific commit are interchangeable (see [tracing a version](./#tracing-a-version-to-code)).

| You are on…                       | Version produced                             | Frozen? | Chart published?     |
| --------------------------------- | -------------------------------------------- | ------- | -------------------- |
| `develop`                         | `0.0.0-develop.39`                           | no      | yes (rolling)        |
| release line branch `1.0`         | `1.0.0-rc.41` → after `1.0.0`, `1.0.1-rc.42` | no      | yes                  |
| **tag** `1.0.0`                   | `1.0.0`                                      | **yes** | yes                  |
| any other branch, e.g. `g2p-4567` | `0.0.0-g2p-4567.44`                          | no      | **no** (images only) |

Every value is valid [SemVer](https://semver.org) **and** a valid Docker tag. By the SemVer spec a bare `X.Y.Z` (no suffix) is a stable release, and anything with a `-suffix` sorts strictly below it — so **"a 3-digit version with no suffix is frozen" is enforced by tooling, not just convention.**

{% hint style="info" %}
**No `v` prefix.** Release tags are the bare version, `1.0.0` — **not** `v1.0.0`. The bare 3-digit form _is_ the frozen signal. (The `v`-prefix is reserved for the packaging repo's own workflow tags like `v1`; see [CI pipeline](ci-pipeline.md).) The pipeline rejects a `v1.0.0` tag.
{% endhint %}

## Frozen versions: tag, don't branch

You do **not** create a `1.0.0` branch to cut a release. A branch is mutable — publishing a frozen `1.0.0` from one would let a later push overwrite a released artifact.

Instead:

1. Create the **release line** branch `1.0` off `develop`. Every push there publishes an `1.0.0-rc.N` (image + chart) that is fully built and testable.
2. When an RC is blessed, **tag that commit `1.0.0`**. The tag build **promotes** the already-tested image digest to `1.0.0` (a retag — no rebuild) and packages the chart at `1.0.0`.

The tag is the "peg". You never work _on_ a tag; you tag a commit the release line already produced.

### How versions flow — a worked example

One release line, from the first RC to the second patch, all on the **same** branch `1.0`:

| Step | Ref / action | Published version |
| --- | --- | --- |
| work toward the release | branch `1.0` | `1.0.0-rc.3` |
| …more commits | branch `1.0` | `1.0.0-rc.4` |
| cut the release | **tag `1.0.0`** | `1.0.0` (promoted from the tested RC — not rebuilt) |
| fix a bug (same branch) | branch `1.0` | `1.0.1-rc.5` |
| …more commits | branch `1.0` | `1.0.1-rc.6` |
| cut the patch | **tag `1.0.1`** | `1.0.1` |

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

* tag `1.0.0`. A frozen version may only come from an immutable ref.
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

* [**CI pipeline**](ci-pipeline.md) — how the reusable workflow builds, versions, promotes and publishes; the `@v1` rollout model; a diagram.
* [**Changelogs**](changelogs.md) — where change notes are published, how to link them, the role of AI, and what happens when AI is unavailable.
* [**Onboarding a repo**](onboarding-a-new-repo.md) — a step-by-step guide **and a copy-paste prompt** to add this to any new repo, plus moving the `v1` tag.
