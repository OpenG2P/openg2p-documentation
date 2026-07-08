# Roadmap & Automation

This page captures open work items and the proposed approach for keeping the wiki automatically in sync with its sources.

## Shipped

* **Knowledge-elicitation engine** — the loop that captures tacit knowledge (taxonomy → scan → gap ledger → interview guides → synthesise → `lessons/`). This realises the "knowing what you don't know" goal: coverage and the **superhuman index** are now first-class outputs. See the [Elicitation Engine — Operating Guide](elicitation.md). *Outstanding within it: promote the first expert lessons (the index only moves once lessons are promoted), and stand up an eval harness.*
* **Lens-not-mirror migration** — the entity-page schema follows the "lens, not mirror" principle: `## Public surface` asks for a characterisation rather than an enumeration; `## Data model` asks for relationships and meaning; `## Rationale` and `## Cross-layer flows` are required sections; lint enforces these with mirror-warnings. Entity pages have been regenerated under the new schema. The `flow` page type shipped (e.g. `flow-partner-ingest`); the `glossary` page type is defined in the schema but `wiki/glossary.md` is not yet populated.

## TODO list
* **Automatic updates on source change** — see below. Currently runs require a human invoking `./tools/update.sh`.
* **Incremental rebuilds for entities and cross-synthesis** — both are full-rebuild today. They should follow the same input-hash skip pattern that `synthesise:sources` already uses.
* **Better redaction tooling for `lessons/`** — Presidio + LLM scrub is wired, but the human-review UX is still a manual diff. A small admin UI on top of `lessons/proposed/` would cut review friction.
* **Wider repo allow-list** — the `raw/MANIFEST.yaml` allow-list is currently scoped to the Registry and its supporting platform (`registry-platform`, farmer/national-social registries, platform services, deployment repos). Extend to PBMS, SPAR, G2P Bridge, and deeper MOSIP-integration repos as those areas are prioritised by the advisor.
* **Coverage report for Google Drive ingest** — `raw/gdrive-discovery.md` lists what was found; pair it with a coverage report showing which discovered Drive items failed to ingest and why (e.g. non-native files, ACL-restricted, etc.).
* **Cross-repo concept/comparison expansion** — synthesis produces these on demand today. Track which clusters have been compared and which haven't, in a small dashboard page.
* **Lessons feedback loop** — when a `needs-review` page is resolved by a lesson, link the resolution back into the wiki page's frontmatter for traceability.
* **Multi-tab Google Sheet capture** — the current `gdrive` ingest fetches a spreadsheet via the public CSV export, which only returns the default tab. Real-world OpenG2P sheets (e.g. the v4.0.0 Registry test results at [https://docs.google.com/spreadsheets/d/1bnKFyO0DAi2M9Mvath17TUAAGKOaEi_-K_v9VGgI-iw](https://docs.google.com/spreadsheets/d/1bnKFyO0DAi2M9Mvath17TUAAGKOaEi_-K_v9VGgI-iw)) keep aggregate summaries on the default tab and the per-test-case detail on additional tabs that ingest never sees. Result: the advisor cannot answer "give me 10 example test cases for v4.0.0" from the wiki. Fix is to enumerate every tab via the Google Sheets API and capture each tab as its own labelled CSV block in `raw/gdrive/sheet-<id>.md`. Requires `GOOGLE_API_KEY` (already in `.env.example`) and a small extension to `tools/src/ingest/gdrive.ts`.
* **Jira as a first-class source (Layer 2)** — today every Jira URL referenced from a gitbook page is captured as a structured `external_refs:` entry in the corresponding source page's frontmatter (Layer 1 — already shipped); the advisor surfaces those URLs as clickable links so users can reach them. The richer goal is to **ingest** each referenced issue: `tools/src/ingest/jira.ts` would scan all gitbook content for Atlassian issue keys, hit the Jira REST API per key (auth via `JIRA_BASE_URL` / `JIRA_EMAIL` / `JIRA_API_TOKEN` env vars), cache per-issue JSON in `raw/jira/<KEY>.json`, and synthesise a `wiki/sources/source-jira-<key>.md` per issue with structured frontmatter (status, priority, fix_versions, parent, subtasks). Cross-synthesis would then produce per-release rollup pages (e.g. `comparison-release-4-0-0-issues.md`) grouping issues by fix version with sub-sections for "Critical open", "Resolved this release", "Sub-task tree". This is what enables advisor questions like *"top open critical issues for v4.0.0"* without leaving the wiki. Half-day to a day's work plus the ongoing operational story for the Jira token.
* **File-back-as-page (Karpathy compounding loop)** — Karpathy's LLM-Wiki idea includes the pattern *"Good answers can be filed back into the wiki as new pages. This way your explorations compound in the knowledge base just like ingested sources do."* We don't do this. The advisor has a `flag_wiki_gap` tool but it punts to maintainers — the answer itself isn't filed. Proposed: when the advisor produces a substantive multi-source answer (e.g. ≥3 wiki citations, narrative >300 chars), offer the user a "file this as `concept-<slug>` for future reference" button. On confirm, synthesise frontmatter and write a new wiki page. This is the wiki's compounding mechanism — without it, the wiki only grows from raw ingest, never from interactions.
* **Better search backend (BM25, optional embeddings)** — `wiki_search` is currently substring matching with a token-frequency-cap heuristic and title-boost. It works but is naive. A proper BM25 with TF-IDF would improve ranking on multi-term queries. Beyond that, an embedding-based fallback (local model via `node-llama-cpp`) would close the semantic-gap failure mode (e.g. "test case report" vs "test results spreadsheet"). Karpathy describes this as the `qmd` tool that becomes important past ~100 pages — we're at 300+.
* **Ripple updates from ingest** — Karpathy: *"A single source may touch 10-15 pages — creates summary, updates concept pages, revises related entities..."* Our `synthesise:sources` writes exactly one page per source; concept pages update only on full cross-synthesis runs. Proposed: after writing a source page, identify which concept/entity pages cite the same topic (via tag overlap or alias matching) and enqueue them for re-synthesis. This makes ingest the natural moment when the wiki absorbs the new source's claims into the cross-cutting pages.
* **Semantic lint** — Karpathy's lint includes LLM-driven checks: *"concepts mentioned across many sources but lacking own page", "stale claims superseded by newer sources", "suggested investigations"*. Our lint is purely deterministic (frontmatter, link integrity, schema, lens-guards). Add an `npm run lint:semantic` command that runs an LLM pass over the wiki to surface these — not blocking, but reported as a periodic health-check.
* **Alias matcher refinement for `backfill-related-links`** — the v1 matcher catches whole-phrase matches (e.g. "Farmer Registry") but misses spacing/style variants like "Gen-2" vs "Gen2" vs "Gen 2", and short phrases like "ID generation" that don't match the full title "Functional ID Generation". After the v1 pass we got 52 edges into source pages from 31 sources — useful but undermatched. Improvements: (1) normalise dashes/spaces in both alias and body before matching; (2) add tag-as-alias for entities/concepts where tags are multi-word; (3) add stripped-prefix variants ("Functional ID Generation" → also matches "ID Generation"). Risk: false positives. Run with --dry to preview before committing.
* **Cross-documentation consistency check — restore Karpathy Lint fidelity (full-body, not summary-level)** — Karpathy's original LLM-Wiki formulation includes cross-page contradiction detection as a first-class part of the **Lint** operation, with two triggers: (a) *at ingest* — flag when a newly-ingested source contradicts existing wiki content ("Contradicts our wiki claim that X"); (b) *periodic* — a `CONTRADICTIONS` health-check section listing "Page A claims X, but Page B shows opposite". His version compares the **actual bodies** of wiki pages, which fits in-context at his ~100–200 page scale. **We implemented a degraded version of (b) and skipped (a) entirely.** Our contradiction pass inside `synthesise:cross` sees full entity bodies + **one-line source summaries** — a token-budget compromise at our 300–487 page scale — so it never reads the actual bodies of the documentation pages and cannot catch two doc pages whose bodies contradict each other (e.g. one deployment page says "audit is on by default", another says "opt-in"). To restore the fidelity Karpathy assumed, do a **map-reduce over the corpus**: (1) cluster related pages (by tag overlap, shared entities, or the `related:` graph) so each cluster is 5–15 pages, not 300+; (2) feed each cluster's **full page bodies** into one LLM call asking for internal contradictions — bounded prompt, full-body fidelity; (3) aggregate into `wiki/contradictions.md`. Separately, add trigger (a): at ingest, diff a changed source against the wiki pages that cite it and flag new contradictions. Ship the periodic check as a dedicated command (e.g. `npm run check:consistency`) separate from cross so it can run on its own cadence. ~half-day for the periodic checker; the at-ingest trigger is a follow-on.

## Automatic updates — proposed approach

Today, `./tools/update.sh` does the right thing but a human has to invoke it. The goal is: **whenever a source changes upstream, the wiki refreshes itself within a bounded delay, and the change shows up in the next advisor query**.

The plan is layered, cheapest first:

### Layer 1 — scheduled refresh (quick win)

A nightly (or hourly) cron job on the host that runs `./tools/update.sh`, commits the diff to the `g2p-wiki` repo, and pushes. Captures upstream GitBook edits, website edits, and any newly-linked Google Drive docs without needing per-source webhooks.

* **Pros:** trivial to set up, no source-side configuration, single job to monitor.
* **Cons:** up to N minutes of latency; rebuilds even when nothing changed (cheap because ingest and source synthesis are both incremental).

### Layer 2 — webhook-triggered refresh (per source)

Per-source triggers, layered on top of Layer 1:

* **GitBook (`openg2p-documentation`)** — GitHub `push` webhook on the repo → small webhook handler → invokes `update.sh`. Already incremental on the gitbook side, so this is cheap.
* **OpenG2P repos (`ingest:repos` + `synthesise:entities`)** — GitHub `push` webhooks on each repo in the allow-list. Handler maps the repo to a single-repo refresh path: re-run `ingest:repos` (filtered to that repo) and `synthesise:entities` (filtered to that entity page) rather than the full cross-org sweep.
* **Website (`www.openg2p.org`)** — no native push notifications; rely on Layer 1 cron, with shorter cadence (e.g. every 4 hours) since pages change less often.
* **Google Drive** — Drive API `changes.watch` is heavyweight for our use case. Stay on Layer 1 cron; auto-discovery from GitBook is the main update vector.

### Layer 3 — commit and notify

Whichever layer triggers, the same downstream pipeline runs:

1. `update.sh` finishes (or its single-repo equivalent).
2. If `git status` shows a diff under `wiki/`, commit with a message like `auto: refresh from <source> @ <sha>` and push.
3. Append to `wiki/log.md` for traceability.
4. Optional Slack/email notification to the wiki maintainer on lint failures or `needs-review` page additions.

The advisor reads from the deployed `wiki/` checkout — it picks up changes on its next scheduled `git pull` (handled by the advisor's deployment, not this repo).

### Open questions for automation

* **Race conditions** — overlapping webhook invocations during a busy push window. A simple file lock or a queueing layer (single worker) is enough at current volume.
* **Lint failures in CI** — should an auto-commit be blocked, or should it land with the failing pages flagged `needs-review`? The current preference is to **block** auto-commits on lint errors and notify the maintainer; warnings (orphans, low confidence) do not block.
* **Cost ceiling** — `synthesise:sources` is incremental, but `synthesise:cross` re-runs whole clusters. Add a budget guard and a cooldown so a flurry of upstream commits doesn't spike LLM spend.

## See also

* [Scripts](scripts.md) — what `update.sh` runs today.
* [Design](design.md) — what the wiki looks like end-to-end.
