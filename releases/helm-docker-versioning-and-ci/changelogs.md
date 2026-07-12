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

## Where they are published

Not into the service repo (that would bump the commit-count version and loop).
They go to the **`openg2p-packaging` `gh-pages`** branch, one folder per repo:

```
gh-pages (openg2p-packaging)
  <repo>/
    CHANGELOG.md          ← the page to link; Unreleased first, releases newest-first
    versions/
      1.0.0.md            ← one page per frozen release
      unreleased.md       ← rolling; regenerated each build, never grows
```

**Link to:** `https://openg2p.github.io/openg2p-packaging/<repo>/CHANGELOG.md`

This is the single URL to reference from GitBook or anywhere else — always current,
no diffing, no command line.

## What triggers an entry

| Channel | Changelog |
| --- | --- |
| `develop` | updates the rolling **Unreleased** section (notes since the last release) |
| release tag `N.N.N` | writes a frozen **version page**, clears Unreleased |
| RC (`1.0`), feature branch | skipped — the release tag captures the whole range |

A build with no new commits in its range publishes nothing.

## The role of AI

A single call to [OpenRouter](https://openrouter.ai) turns the commit list into
2–5 user-facing bullets. The model and fallbacks are set in
`openg2p-packaging/ci/changelog/config.yml` (non-secret); the API key is the
**`OPENROUTER_API_KEY`** org-level Actions secret.

The AI **summarises the human-written commit notes** — it does not invent content
from code diffs, so the summary stays grounded in what developers actually stated.

## What happens if AI fails

AI is **never load-bearing.** If OpenRouter (or the key) is unavailable, the job:

* logs a `::warning::` with the actual reason,
* **still publishes** the changelog with the full commit-message list,
* writes `_AI summary unavailable…_` in the Summary section.

The build and the changelog succeed regardless. Two knobs (run the service repo's
workflow via **Run workflow** in the Actions tab):

| Input | Effect |
| --- | --- |
| `changelog_skip_ai: true` | publish commit messages only, no API call (clean success) |
| `changelog_regenerate: 1.0.1` | backfill the AI summary for an already-published version — reads its commit list back and rewrites **only** the Summary; the commit list is immutable after release |

So an AI outage is fully recoverable after the fact, and you can always produce
the human changelog without AI.

{% hint style="warning" %}
If `OPENROUTER_API_KEY` is not configured at all, the job behaves exactly as
`changelog_skip_ai` — human notes publish, with a warning. Configure the secret
once at the org level and every repo gets summaries.
{% endhint %}
