---
description: Step-by-step instructions for tagging and publishing a release.
---

# Cutting a release (how to tag a version)

This page is **instructions only**. For *why* it works this way — immutable versions,
promote-don't-rebuild, release lines — see
[Helm & Docker Versioning Strategy and CI](README.md).

## The rules, in one box

{% hint style="warning" %}
1. **Push the branch first and wait for its pipeline to go GREEN. Only then push the tag.**
2. Tag name is the **bare version**: `1.1.0` — **not** `v1.1.0`.
3. Use an **annotated** tag: `git tag -a … -m "…"` (the message becomes the release notes).
4. Tag **the exact commit** whose pipeline just went green.
5. First release on a line ends in **`.0`** (`1.1.0`); then `1.1.1`, `1.1.2` — no gaps.
6. Never create a **branch** named `1.1.0` — the branch is `1.1`, the tag is `1.1.0`.
{% endhint %}

## A. Standard release (from a release line)

Use this whenever you want a maintenance line you can cut patches from later.

**Step 1 — create the release line branch and push it**

```bash
git checkout develop
git pull
git checkout -b 1.1
git push -u origin 1.1
```

**Step 2 — wait for the `1.1` pipeline to finish GREEN**

It publishes `1.1.0-rc.<n>` (images + chart). Do not continue until it is green.

**Step 3 — tag that exact commit, annotated**

```bash
git tag -a 1.1.0 -m "First 1.1 release.

Highlights:

- Redesigned onboarding (G2P-100)
- Drops the legacy /v0 endpoints"
```

**Step 4 — push the tag**

```bash
git push origin 1.1.0
```

**Step 5 — check the tag pipeline is green.** It does **not** rebuild: it promotes the
already-tested `1.1.0-rc.<n>` image digest to `1.1.0` and publishes the chart at `1.1.0`.

## B. One-off release straight from develop

No maintenance line needed? Tag `develop` directly.

1. Push your work to `develop` and **wait for the pipeline to go GREEN** (it publishes
   `0.0.0-develop.<n>`).
2. Tag and push that same commit:

```bash
git checkout develop
git pull
git tag -a 1.1.0 -m "Release notes here"
git push origin 1.1.0
```

Create a `1.1` branch later only when you need to cut `1.1.1` while develop moves on.

## C. Patch release (1.1.1, 1.1.2 …)

Keep using the **same** `1.1` branch — one branch, many tags. Never create `1.1.1`
as a branch.

```bash
git checkout 1.1
git pull
# ... commit the fix ...
git push origin 1.1
# wait for the pipeline to go GREEN (publishes 1.1.1-rc.<n>)
git tag -a 1.1.1 -m "Fix X"
git push origin 1.1.1
```

## Verify the release

* The **tag pipeline** is green.
* The **image** exists at `…:1.1.0` (Container Registry / Docker Hub).
* The **chart** `1.1.0` appears in the Helm repository.
* The **changelog** shows a `1.1.0` page with your **Release notes**, at
  [openg2p.gitlab.io/versions](https://openg2p.gitlab.io/versions/) (GitLab repos).

## Do not do this

| Don't | What happens |
| --- | --- |
| Push the branch **and** the tag together | Two pipelines race. The tag's promote step usually runs before the RC image is built and **fails** with _"nothing to promote"_. |
| Tag a commit CI never built | Same failure — a release **promotes** an existing digest, it never builds one. |
| Tag with a `v` prefix (`v1.1.0`) | Pipeline stops: _"tag 'v1.1.0' is not N.N.N"_. |
| Create a branch named `1.1.0` | Pipeline stops: use branch `1.1` + tag `1.1.0`. |
| Skip a patch number (e.g. `1.1.3` after `1.1.1`) | Pipeline stops: _"tag … skips a patch"_. |
| Use a lightweight tag (`git tag 1.1.0`) | Release publishes fine, but the page has **no Release notes** section. |

## If something goes wrong

**"nothing to promote for … Tried: 1.1.0-rc.N 0.0.0-develop.N"**

The tagged commit has no built image. Usually the tag was pushed before (or without)
its branch build.

* If the branch pipeline is still running or has since gone green:
  **re-run the failed tag pipeline.** Nothing else to do — no re-tag, no cleanup.
* If the commit was genuinely never built: delete the tag, push the branch, wait for
  green, then re-tag that commit.

```bash
git push origin :refs/tags/1.1.0
git tag -d 1.1.0
```

{% hint style="info" %}
A failed tag pipeline publishes **nothing** — no image, no chart, and no changelog
entry. There is no half-released state to clean up.
{% endhint %}

**Tag pushed with the wrong notes?** Don't re-tag. Edit the Release description and
re-run the pipeline — see
[Editing release notes later](changelogs.md#editing-release-notes-later-without-moving-the-tag-gitlab).

## Related

* [Helm & Docker Versioning Strategy and CI](README.md) — the concepts (immutable
  versions, promote vs rebuild, release lines).
* [Changelogs](changelogs.md) — release notes, what each page shows.
* [CI pipeline](ci-pipeline.md) — what each job does.
