---
description: >-
  Change logs are built from commit messages plus an AI summary, and published as
  markdown per repo — with a clear fallback when AI is unavailable.
---

# Changelogs

Every published version gets a human-readable changelog entry, produced by the
**same** CI run that builds the images and chart — no separate step, no second
prompt to update docs.

## The developer writes nothing extra

The **commit message is the change note.** CI collects the commit messages in a
version's range, lists them verbatim (with a short SHA), and adds a compact
**AI summary** on top. There is no note file to write and no PR check.

{% hint style="info" %}
The changelog is only as good as your commit subjects. The existing
`G2P-#### <subject>` style is exactly right — terse is fine, the AI summary makes
the range readable, but a bare `fix` commit produces a bare `fix` line.
{% endhint %}

Each entry shows the commit's short SHA as a **link to the commit on GitHub**, so
you can click through to the exact diff. `G2P-####` references link to Jira.

**Jira links.** Any `G2P-####` reference in a commit message (and in the AI
summary) is rendered as a link to
`https://openg2p.atlassian.net/browse/G2P-####`. The base URL and project key are
set in `ci/changelog/config.yml` (`jira_base`, `jira_project`).

## Release notes: the annotated-tag message

For a release, you can add a curated blurb — "what's in 1.0.0" — by cutting the
release with an **annotated tag** instead of a lightweight one:

```bash
git tag -a 1.0.0 -m "First GA release.

Highlights:

- Redesigned onboarding (G2P-100)
- Drops the legacy /v0 endpoints

Upgrade notes: run the 1.0 migration before deploying."
git push origin 1.0.0
```

The tag message is rendered **verbatim as a `Release notes` section at the top of
the `1.0.0` page** (above the auto-generated Summary and the commit list), and it
shows on the repo's aggregate `CHANGELOG` too. `G2P-####` refs in it are linkified
like everywhere else. The message is plain **markdown**, so leave a blank line
before a bullet list, as above.

This is core git — the annotated tag is a real object carrying the message; both
GitHub and GitLab read the same object. A **lightweight** tag (`git tag 1.0.0`)
carries no message, so the page simply omits the section — nothing breaks. Only
release tags are read this way; release candidates and develop builds are unaffected.

### Editing release notes later — without moving the tag (GitLab)

You often want to refine the notes *after* the release is out — add a link, expand
a highlight, fix a typo. You do **not** re-tag for this. On GitLab the changelog reads
release notes from **two sources, in priority order**:

1. The **GitLab Release** description — an editable field, separate from the tag.
2. Otherwise, the **annotated-tag message** (above).

**The Release is created for you.** When you tag an **annotated** release, the pipeline
**auto-creates a GitLab Release** for that tag, seeded from your tag message — so it
shows up on the project's **Releases** page with no manual step. (A lightweight tag has
no message, so no Release is created.) The Release also gets a small footer with a
**one-click "Publish to the changelog" link** (that footer never appears on the
changelog page itself — it's only in the Release, to make step 2 below obvious).

So the edit-later flow is:

1. **Edit the Release** in the UI. A GitLab Release is a **project-level** object (not
   group-level — the group view only aggregates the _package_ registry). Inside the
   **project** (e.g. `openg2p/spar/spar`): _Deploy → Releases_ (older instances:
   _Deployments → Releases_) → the release for your tag → **edit (pencil)**. Update the
   description and save. _(Scriptable: `glab api -X PUT projects/:id/releases/1.0.0 -f description="…"`.)_
2. **Re-publish**: click the **Publish to the changelog** link in the Release footer —
   it opens _Run pipeline_ with the tag already selected; press **Run pipeline**.
   (Equivalent manual route: _Build → Pipelines → Run pipeline_, ref = the tag.)

That's it. The release page is rewritten from the edited description. **The tag never
moves**, and because a release build only ever **promotes** an existing digest, the
re-run is a safe no-op for the image and chart jobs (they detect the version is already
published and skip) — only the changelog page changes. Because the auto-create is
**create-if-absent**, re-running **never overwrites** the description you edited.

{% hint style="info" %}
**Which wins.** If a GitLab Release description exists, it is used; otherwise the
annotated-tag message is used. So: cut the release with `git tag -a` (the Release is
created and the first changelog page is populated automatically), and only touch the
Release description later if you need to refine the notes — no force-push, no re-tag.
{% endhint %}

{% hint style="info" %}
On **GitHub** the same two-source precedence applies (Release **body** over tag
message), but GitHub Releases are **not** auto-created — create/edit the Release
manually, then re-run the tag's workflow.
{% endhint %}

#### "I edited the tag's annotation instead — why hasn't the page changed?"

Because on GitLab the **Release description shadows the tag message**, and the Release
was auto-created from your original annotation the moment you tagged. Re-writing the
annotation (`git tag -a -f …` + `git push -f`) therefore changes nothing the catalogue
reads — the Release description still wins, and you have force-moved a release tag for
no benefit.

| Where you edit | GitLab | GitHub |
| --- | --- | --- |
| **Release description / body** | ✅ used — the supported path | ✅ used |
| **Tag annotation** (re-tag) | ❌ ignored once a Release exists | ✅ used, if no Release body exists |

So on **GitLab, always edit the Release**; on **GitHub** either works. If you genuinely
want the tag annotation to be the source again on GitLab, clear the Release description
first — then the next run falls back to the tag message.

{% hint style="warning" %}
**Nothing updates until the pipeline runs again.** The catalogue is written by the
`changelog` job, so after editing the notes you must re-run the pipeline **on the tag**
— that is what rewrites the page. Editing the notes alone changes nothing.
{% endhint %}

## Library repos (no image, no chart)

Some repos are **libraries** — code consumed **directly by git reference** (a branch,
tag, or commit), with **no Docker image and no Helm chart** to build. Examples:
`openg2p-fastapi-commons`, `registry-platform`, `g2p-bridge-connectors`. They still
need change tracking, so they use the **same catalogue** in a **library mode**:

- **A moving branch** (e.g. `develop`) gets **one rolling page** — its current tip, the
  **last 5 commits**, and an AI summary of changes **since the last tag**. The identity
  of "what you get" from a branch is the **commit SHA** (that's what you pin), so there
  is no synthetic `0.0.0-develop.N` version here.
- **A tag** gets a **durable release page**, summarised since the previous tag — exactly
  like a service release (annotated-tag release notes and auto-created Releases apply too).
- On the catalogue's landing page these repos appear under a **Libraries** heading,
  separate from **Services**.

Onboarding is just the normal pipeline with **`kind: library`** and **no** `images` /
chart. On **GitLab**:

```yaml
# .gitlab-ci.yml in the library repo
include:
  - project: 'openg2p/packaging'
    ref: v1
    file: '/ci/gitlab/build-publish.yml'
variables:
  PACKAGING_REF: v1
  CHANGELOG_KIND: library
  # CHANGELOG_PROJECT (e.g. openg2p/versions) is normally already a group CI/CD variable.
```

On **GitHub**:

```yaml
# .github/workflows/publish.yml in the library repo
on:
  push:
    branches: [develop]
    tags: ['[0-9]+.[0-9]+.[0-9]+']
jobs:
  publish:
    uses: openg2p/openg2p-packaging/.github/workflows/build-publish.yml@v1
    with:
      changelog_kind: library
      changelog-repo: openg2p/openg2p-packaging
      changelog-branch: gh-pages
    secrets:
      OPENG2P_BOT_GITHUB_PAT: ${{ secrets.OPENG2P_BOT_GITHUB_PAT }}
      OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
```

That's the whole setup — `build`/`promote`/`chart` are skipped automatically; only the
version + changelog run. Out of the box this tracks the **default branch** (`develop`)
and **tags**. On **GitHub**, track more branches by adding them under `branches:`. On
**GitLab**, `develop`, release-line branches (`1.0`, `2.1`, …) and tags are tracked.

## Where they are published

Not into the service repo (that would bump the commit-count version and loop).
They go to the **`openg2p-packaging` `gh-pages`** branch, one folder per repo:

```
gh-pages (openg2p-packaging)
  <repo>/
    CHANGELOG.md          ← the page to link; Unreleased first, releases newest-first
    versions/
      1.0.0.md            ← one page per release
      unreleased.md       ← rolling; regenerated each build, never grows
```

**Link to:** `https://openg2p.github.io/openg2p-packaging/<repo>/CHANGELOG.md`

This is the single URL to reference from GitBook or anywhere else — always current,
no diffing, no command line.

The site root — [`openg2p.github.io/openg2p-packaging`](https://openg2p.github.io/openg2p-packaging/)
— lists every repo that has a published changelog (a landing page regenerated on
each publish). The Jekyll-rendered view of a repo's changelog is at
`…/<repo>/CHANGELOG` (drop the `.md`); the raw markdown for GitBook is the `.md`
URL above.

## What triggers an entry

**Changelog follows the chart.** Anything deployable — anything that publishes a
chart to Rancher/helm — gets a changelog entry:

| Channel | Chart? | Changelog |
| --- | --- | --- |
| `develop` | ✓ | rolling **Unreleased** page |
| RC (release line `1.0`) | ✓ | **durable per-RC page** (`1.0.0-rc.18`, `1.0.0-rc.19`, …) — kept, so you can see exactly what changed between candidates |
| release tag `N.N.N` | ✓ | durable **release page** |
| feature branch (e.g. `g2p-5563`) | ✗ | none — images only |

A build with no new commits in its range publishes nothing.

{% hint style="info" %}
A **feature branch** publishes no chart (not deployable to Rancher), so it gets no
changelog page — that would flood it with disposable entries. Its work surfaces in
develop's **Unreleased** section once the branch is **merged to develop** (and, if
you squash-merge, under a clean commit message). It remains traceable meanwhile via
the image's commit-SHA label.
{% endhint %}

## Release candidates get durable pages

Because an RC is on its way to a release, **every RC build keeps its own page**
(`versions/1.0.0-rc.19.md`) showing the **delta since the previous RC** — precisely
what changed from `rc.18` to `rc.19`, which is what release QA needs. The **first**
RC on a new line diffs against its **branch point** instead. They appear under a
**Release candidates (in progress)** section in `CHANGELOG.md`. Once you tag
`1.0.0`, its RC pages drop out of that section — the release supersedes them.

Develop builds are paged the same way: each build gets its own durable page.

## What each page shows

Every page is just a commit range, exact because a version's `N` is the commit
ordinal. The rule:

* **develop / RC pages show ONE delta** — what changed **since the previous build**.
  They are deliberately **not** cumulative: repeating "everything since the last
  release" on every build makes each page (and its AI summary) longer and less
  readable the further you drift from a release.
* **A release `N.N.N` page is cumulative** — everything since the **previous release
  tag**. That is the "what shipped" view, and it is where the full picture belongs.

How a develop/RC page picks its baseline:

1. the **previous page of the same kind** (previous develop build / previous RC);
2. for the **first RC on a new line**, the newest develop build that is an
   **ancestor** — the branch point. It must be an ancestor, not merely the newest
   develop build, because develop keeps moving after the line is cut;
3. otherwise the **last release tag**, else the start of history.

**Releases are the durable trace.** Every release `N.N.N` gets a permanent page whose
header names its baseline — _"changes since release 1.0.0"_ — and `CHANGELOG.md`
lists them newest-first.

{% hint style="info" %}
**Migrating a repo with old releases.** The baseline is the last release **tag**,
and both the new bare `N.N.N` **and** the legacy `vN.N.N` tags are recognised, so a
repo moving off the old convention baselines against its last old release (e.g.
_"since v1.2.0"_) and follows the new scheme forward. Resolution order:

1. **Nearest release tag that is an ancestor of `HEAD`** (the clean case — the
   release is in develop's history).
2. **Diverged release line:** if the release tag lives only on a separate line (a
   `1.2` branch never merged back into develop), the baseline is the **merge-base**
   — i.e. "develop changes since it branched from the release line" — labelled with
   that release version. This avoids dumping the entire history.
3. **No release tags at all** → _"the start"_ (full history) until the first release
   is tagged. Self-corrects, or anchor it with a baseline tag.

A `1.0` *branch* is not a release; only a tag anchors the baseline.
{% endhint %}

A develop page therefore reads:

```
## consent-manager — develop 0.0.0-develop.40 (2026-07-13)
_commit `326edee` · changes since 0.0.0-develop.39_

### Summary                          (AI, scoped to THIS delta)
### Changes since 0.0.0-develop.39
```

{% hint style="info" %}
**Trivial deltas skip the AI summary.** A develop/RC build with 0–1 new commits
renders **no Summary section at all** — the commit list already *is* the summary.
Releases always get one. And a release line cut at the same commit as the last
develop build shows an explicit _"No new commits since 0.0.0-develop.40."_ rather
than an empty section.
{% endhint %}

**Retention.** The last **10 develop builds** and the last **10 RCs per release
line** are kept — RCs as deep as develop, because they are the audit trail for a
release. **Every release is kept forever.** RC pages are deleted once their release
ships. Older develop deltas remain recoverable from git, since the version number is
the commit ordinal.

{% hint style="info" %}
**Withdrawn versions.** A develop build whose artifacts have been deleted (see
[Withdrawing a version](withdrawing-a-version.md)) keeps its page — the pages chain
to each other, so removing one would break the "changes since &lt;previous build&gt;"
thread. It is flagged in the summary table and listed, with the reason, under a
**Withdrawn** heading at the end of the page.
{% endhint %}

## The role of AI

A single call to [OpenRouter](https://openrouter.ai) turns the commit list into
2–5 user-facing bullets. The model and fallbacks are set in
`openg2p-packaging/ci/changelog/config.yml` (non-secret); the API key is the
**`OPENROUTER_API_KEY`** org-level Actions secret.

The AI is given two inputs: the **developer commit notes** (the primary source of
*intent*) and a **structural change digest** derived from `git` — changed-file
stats and signals (new files, migrations, dependency and config changes), never
raw diff content. The digest is always small regardless of how large the diff is,
so it grounds the summary in *what actually changed* and lets it surface changes
the commit messages omitted — without the cost or context limits of feeding whole
diffs to the model.

{% hint style="info" %}
**Cost is negligible.** One check-in is a single call of ~1,000–1,500 tokens (the
commit notes plus the bounded change digest). The default model is
`openai/gpt-4o-mini` (~$0.15 / $0.60 per 1M input/output tokens) — chosen over the
cheapest tier because that one flattened large ranges into vague filler. Each
summary costs roughly **$0.0003–0.001**, so a **USD $10** OpenRouter credit still
covers **~10,000–30,000 check-ins**. Bump the model to `sonnet`/`gpt-4o` in
`config.yml` for richer notes; only develop builds and release tags call the
model. (Prices approximate — confirm on
[openrouter.ai/models](https://openrouter.ai/models).)
{% endhint %}

## What happens if AI fails

AI is **never load-bearing.** If OpenRouter (or the key) is unavailable, the job:

* logs a `::warning::` with the actual reason,
* **still publishes** the changelog with the full commit-message list,
* writes `_AI summary unavailable…_` in the Summary section.

The build and the changelog succeed regardless.

### The two manual knobs (Run workflow dialog)

The service repo's workflow has two `workflow_dispatch` inputs, shown when you
click **Run workflow** in the Actions tab. **Neither is needed for normal runs** —
regular pushes handle everything. For a plain manual run, leave the checkbox
**off** and the text box **empty** (it rebuilds and publishes the selected branch
as usual).

| I want to… | ☑ Skip AI checkbox | Version text box |
| --- | --- | --- |
| Normal run (rebuild/publish current state) | off | *(empty)* |
| Publish the changelog **without** the AI summary (AI down / save cost) | **on** | *(empty)* |
| Add the AI summary to a **release that shipped without one** | off | e.g. `1.0.1` |

Details and caveats:

* **Skip-AI checkbox** (`changelog_skip_ai`) — builds the changelog from the commit
  list only, no OpenRouter call; the Summary shows the placeholder.
* **Version text box** (`changelog_regenerate`) — finds that version's existing
  page, reads its commit list back, and rewrites **only** the Summary (the commit
  list is immutable after release). It must be a **release version**
  (`1.0.0`, `1.0.1`) that has a published page — a `0.0.0-develop.N` won't work,
  because develop's changelog is the rolling *Unreleased* page, not a per-version
  one.
* **Don't combine them** — backfilling needs AI, so ticking "skip AI" while filling
  the version box just errors.
* A `workflow_dispatch` run builds whichever **branch** you select in the dialog
  (default `develop`), i.e. it publishes that branch's current version — not only
  the changelog.

So an AI outage is fully recoverable after the fact, and you can always produce
the human changelog without AI.

{% hint style="warning" %}
If `OPENROUTER_API_KEY` is not configured at all, the job behaves exactly as
`changelog_skip_ai` — human notes publish, with a warning. Configure the secret
once at the org level and every repo gets summaries.
{% endhint %}
