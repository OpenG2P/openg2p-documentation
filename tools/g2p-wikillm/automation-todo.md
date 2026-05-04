# Roadmap & Automation

This page captures open work items and the proposed approach for keeping the wiki automatically in sync with its sources.

## TODO list

* **Automatic updates on source change** — see below. Currently runs require a human invoking `./tools/update.sh`.
* **Incremental rebuilds for entities and cross-synthesis** — both are full-rebuild today. They should follow the same input-hash skip pattern that `synthesise:sources` already uses.
* **Better redaction tooling for `lessons/`** — Presidio + LLM scrub is wired, but the human-review UX is still a manual diff. A small admin UI on top of `lessons/proposed/` would cut review friction.
* **Wider repo allow-list** — the current `raw/MANIFEST.yaml` allow-list focuses on Registry Gen2. Extend to PBMS, SPAR, MOSIP integration, and identity-related repos as those areas are prioritised by the advisor.
* **Coverage report for Google Drive ingest** — `raw/gdrive-discovery.md` lists what was found; pair it with a coverage report showing which discovered Drive items failed to ingest and why (e.g. non-native files, ACL-restricted, etc.).
* **Cross-repo concept/comparison expansion** — synthesis produces these on demand today. Track which clusters have been compared and which haven't, in a small dashboard page.
* **Lessons feedback loop** — when a `needs-review` page is resolved by a lesson, link the resolution back into the wiki page's frontmatter for traceability.

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
