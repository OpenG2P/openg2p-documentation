---
description: >-
  Step-by-step (and a copy-paste AI prompt) to put any repo on the central
  versioning + CI + changelog pipeline, plus how to roll out policy changes.
---

# Onboarding a repo

Adding a repo to the pipeline is almost entirely **replacing its CI workflows with
one thin stub** that calls the central reusable workflow. Use
[`consent-manager`](https://github.com/openg2p/consent-manager/blob/develop/.github/workflows/build-publish.yml)
as the working exemplar, or the canonical template
[`ci/samples/caller-stub.yml`](https://github.com/openg2p/openg2p-packaging/blob/main/ci/samples/caller-stub.yml)
in the packaging repo.

{% hint style="info" %}
**Why some boilerplate is repeated in every stub.** The **Run workflow** dialog is
rendered from a repo's own `workflow_dispatch` inputs — a reusable (imported)
workflow **cannot** supply them. So the two changelog inputs and their wording
live in each stub, not centrally. Keep that block **byte-identical** across repos
(copy it from the canonical template) so every repo's dialog reads the same; the
per-repo bits are only `images` / `chart-path` / `chart-image-paths` / `pins`.
{% endhint %}

## Steps

1. **Add** `.github/workflows/build-publish.yml` (the stub — see the prompt below),
   calling `openg2p/openg2p-packaging/.github/workflows/build-publish.yml@v1`.
2. **Delete** the old `docker-build*.yml` and `helm-publish.yml`.
3. **Placeholder the image tags** in `values.yaml` (CI injects the real ones) and
   confirm `Chart.yaml` keeps `version: 0.0.0-develop`.
4. **Do it on `develop`** (the default branch) — it flows to release lines when
   they're cut.
5. **Push a throwaway branch first** (e.g. `xxx-smoke`) to smoke-test: a feature
   branch builds images at `0.0.0-xxx-smoke.N` and **skips** chart/changelog
   publishing, so nothing central is touched. Then push `develop`.

### Prerequisites (once per org)

* `OPENROUTER_API_KEY` — org-level Actions secret (else changelogs publish without
  the AI summary).
* GitHub **Pages enabled** on `openg2p-packaging` `gh-pages` (to view changelogs).
* The bot PAT (`OPENG2P_BOT_GITHUB_PAT`) can push to `openg2p-helm` **and**
  `openg2p-packaging`.

## The prompt

Paste this to an AI agent working in the new repo (fill the one bracketed line):

> Put this repository on the OpenG2P central build/versioning/changelog pipeline,
> exactly like `consent-manager`.
>
> 1. Create `.github/workflows/build-publish.yml` that triggers on `push` to
>    `branches: ["**"]` and `tags: ["**"]`, plus `workflow_dispatch` with boolean
>    input `changelog_skip_ai` (default false) and string input
>    `changelog_regenerate` (default ""). Give them clear descriptions:
>    `changelog_skip_ai` → "Skip the AI summary — publish the changelog from commit
>    messages only (use when AI is unavailable). Leave OFF for a normal run.";
>    `changelog_regenerate` → "Backfill the AI summary for a release that published
>    without one: enter its release version e.g. 1.0.1 (a bare N.N.N, not a develop version). Leave
>    EMPTY for a normal run." It must have one job that calls
>    `uses: openg2p/openg2p-packaging/.github/workflows/build-publish.yml@v1` and
>    passes `packaging-ref: v1`.
> 2. Under `with:`, set `images` to a JSON array — one entry per Docker image this
>    repo builds — each `{ "name", "repo", "dockerfile", "context"?, "pins"? }`,
>    where `name` labels the build, `repo` is the Docker Hub repository
>    (`openg2p/…`), `context` defaults to `.`, and `pins` is only for images whose
>    Dockerfile declares an `ARG` that is a **git ref** (list
>    `{ "arg", "repo", "ref" }` so CI resolves the ref to a SHA). Find the images
>    by looking at the `docker/**` and `ui/**` Dockerfiles.
> 3. Set `chart-path` to the chart directory, and `chart-image-paths` to a JSON
>    array of the `yq` paths in that chart's `values.yaml` that hold **this org's**
>    image tags (exclude third-party images). Find them by grepping `values.yaml`
>    for `repository: openg2p/…`.
> 4. Forward `changelog_skip_ai` and `changelog_regenerate` from the dispatch
>    inputs, and pass secrets `docker_hub_actor`, `docker_hub_token`,
>    `OPENG2P_BOT_GITHUB_PAT`, and `OPENROUTER_API_KEY`.
> 5. Delete the existing `docker-build*.yml` and `helm-publish.yml`.
> 6. In the chart's `values.yaml`, set every OpenG2P image `tag` to a placeholder
>    (CI injects the real version at package time); keep `Chart.yaml`
>    `version: 0.0.0-develop`.
> 7. Do NOT add any versioning logic or path filters to the stub — all logic is in
>    `openg2p-packaging@v1`. Keep the stub minimal and declarative.
>
> Reference: the `consent-manager` `build-publish.yml`, and the docs at
> Helm & Docker Versioning Strategy and CI.

## Maintaining the pipeline: moving `v1`

When you change the **central** logic in `openg2p-packaging` (the versioning
script, the changelog, the workflow), the repos pick it up only when the **`v1`
tag moves**:

```bash
# in openg2p-packaging, after committing + pushing the change:
git tag -f v1
git push -f origin v1
```

{% hint style="warning" %}
Moving `v1` re-points **every** repo and branch on their next run. Best practice:

1. Cut an immutable peg first: `git tag v1.2.0 && git push origin v1.2.0`.
2. Canary it on one repo by temporarily pinning that repo's stub to `@v1.2.0`.
3. Only then move `v1`: `git tag -f v1 v1.2.0 && git push -f origin v1`.

**Ordering matters:** if you push a stub that uses a new input *before* `v1` has
it, that run fails with `startup_failure`. Move `v1` first. (A re-run fixes a
stale failure once `v1` is current.)
{% endhint %}

### The compatibility rule

> Moving `v1` may change **how** artifacts are built and published. It must never
> change **what version string a given commit gets.**

Fixing a bug, adding an input with a default, improving a label — safe under `v1`.
Changing the version format (e.g. `-rc.` → `-alpha.`) changes what a commit is
called and needs a **`v2`**, or it breaks the immutability guarantees of versions
already published from long-lived branches.

Keep every `v1.x.y` peg forever — it is how you answer "which policy built this?"
and how you roll back (`git tag -f v1 v1.1.0 && git push -f origin v1`).
