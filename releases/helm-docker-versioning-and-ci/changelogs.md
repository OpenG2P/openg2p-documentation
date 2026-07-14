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
(`versions/1.0.0-rc.19.md`) showing both diffs — **New in this build** (vs the
previous RC) and **Since last release** (cumulative). So you can see precisely what
changed from `rc.18` to `rc.19`, which is what release QA needs. They appear under a
**Release candidates (in progress)** section in `CHANGELOG.md`. Once you tag
`1.0.0`, its RC pages drop out of that section (the release is done) but **remain as
files**, browsable by URL, as the historical record of the release run.

develop stays a **single rolling page** by contrast — it's the integration stream,
not a release candidate, so durably paging every push would be noise.

## How versions accumulate, and the two diffs

"Previous version" means two different things, and the changelog shows **both** —
each is just a commit range, exact because a version's `N` is the commit ordinal:

* **Incremental** — vs the *previous build on the same branch* (what this build added).
* **Cumulative** — vs the *last released version* (everything unreleased so far).

**Releases are the durable trace.** Every release `N.N.N` gets a permanent page whose
header names its baseline — _"changes since release 1.0.0"_ — and `CHANGELOG.md`
lists them newest-first. Scrolling the page **is** the release history; when it grows
large the per-version pages under `versions/` can be split by major line.

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

**Develop is a single rolling page**, regenerated each build, showing both diffs at
once:

```
## consent-manager — Unreleased (0.0.0-develop.40, 2026-07-13)
_commit `326edee` · baseline: release 1.0.0 · previous build 0.0.0-develop.39_

### Summary                              (AI, cumulative since 1.0.0)
### New in this build (since 0.0.0-develop.39)   ← incremental diff
### Since last release (1.0.0)                    ← cumulative diff
```

So you always see what *this* build changed and what has piled up since the release,
without a page per build. (Develop builds are transient — only releases are kept
durably; any older develop delta is recoverable from git, since the version number
is the commit ordinal.) At release time the whole Unreleased range folds into the new
version's page and Unreleased resets.

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
