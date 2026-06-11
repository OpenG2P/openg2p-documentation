# Scripts

All scripts live under `tools/` in the [g2p-wiki](https://github.com/OpenG2P/g2p-wiki) repository. They fall into five families: **ingest**, **synthesise**, **mirror**, **elicit** (the knowledge-elicitation loop), and **utility** (lint, index, discovery, hash backfill).

## Setup

Requires:

* Node 22+
* The `gh` CLI, authenticated (`gh auth status`)
* The `claude` CLI, logged in (`claude login`) — synthesis runs through your existing Claude Code subscription, no separate Anthropic API key needed.
* Optional: `GOOGLE_API_KEY` in `.env` if you want Google Drive folder enumeration.

```bash
cd tools
npm install
cp .env.example .env   # optional — defaults work for most setups
```

## Ingest scripts

Ingest is **purely mechanical**. It mirrors source material into `raw/`, pins commit SHAs / fetch timestamps, and never calls an LLM.

| Command | What it does |
|---|---|
| `npm run ingest:gitbook` | Mirrors `openg2p-documentation` into `raw/gitbook/`. Skips `_Archive`, `node_modules`, `.git`. **Incremental** from the second run — diffs HEAD against the previously-pinned SHA and only re-mirrors changed files. |
| `npm run ingest:repos` | Pulls structural files from public, non-archived repos under [github.com/OpenG2P](https://github.com/OpenG2P), filtered by the `allow` list in `raw/MANIFEST.yaml`. Extracts READMEs, CHANGELOG, OpenAPI specs, schemas, helm charts, Dockerfile, controllers/routes (signatures only), package metadata. |
| `npm run ingest:gdrive` | Auto-discovers Google Drive links from `raw/gitbook/`, then fetches docs/sheets/slides via public export URLs and folders via the Drive API. Writes a discovery report to `raw/gdrive-discovery.md`. |
| `npm run ingest:sites` | Crawls `www.openg2p.org` to a configured max depth, converts HTML → markdown, snapshots into `raw/sites/`. |

After every ingest, the script appends an entry to `wiki/log.md` (date, kind, source, result).

## Synthesis scripts

Synthesis is **LLM-driven**. It reads `raw/` and writes `wiki/`. This is the only place LLM calls are made.

| Command | What it does |
|---|---|
| `npm run synthesise:sources` | Per-source pass: turns each ingested document into a one-page summary in `wiki/sources/` (Origin, Summary, Key claims, Terminology, Cross-references, Notes for synthesis). **Incremental** — each source page records the SHA-256 of its input in frontmatter (`source_hash`); pages whose input is unchanged are skipped. Pages whose source no longer exists are removed. |
| `npm run synthesise:entities` | Per-repo pass: turns each repo's structural files into an entity page in `wiki/entities/` (Purpose, Public surface, Data model, Dependencies, Deployment shape). Records the source `commit_sha` in frontmatter. |
| `npm run synthesise:cross` | Cross-repo pass: reads `wiki/index.md` plus the entity pages, detects clusters (e.g., all `spar-*` repos), and produces or updates concept and comparison pages. |

## Mirror script

| Command | What it does |
|---|---|
| `npm run mirror:playbooks` | Copies playbook source pages from `raw/gitbook/` directly into `wiki/playbooks/` **verbatim**, bypassing synthesis. Playbooks are the operating contract for the advisor's project mode and must match the source word-for-word. |

## Elicitation scripts

The knowledge-elicitation loop — measure what the wiki is missing, turn the gaps into expert interview questions, and fold the answers back as lessons. See the [Elicitation Engine — Operating Guide](elicitation.md) for the full workflow.

| Command | What it does |
|---|---|
| `npm run elicit:scan` | **No LLM.** Classifies every taxonomy cell (`elicitation/taxonomy.yaml`) as covered/partial/gap against the wiki, scores priority, and writes `elicitation/gaps/{gap-ledger.md,gap-ledger.json,coverage.md}`. `coverage.md` carries the headline **superhuman index**. |
| `npm run elicit:guide` | Turns the top gaps into grounded interview guides under `elicitation/interviews/<cell>.md`. Flags: `--top N` (default 8), `--area <area>`, `<cell-id>`, and `--sharpen` (LLM-refine the questions — one `claude` call per cell). Without `--sharpen`, questions come verbatim from the taxonomy (no LLM). **Overwrites** the interview file for each cell — run before answers are filled in, never after. |
| `npm run elicit:synthesise` | Reads a **filled** interview file (pass the filename; auto-found in `elicitation/interviews/` or `elicitation/intake/`), PII-scrubs it, and writes a confidence-scored draft to `lessons/proposed/<slug>.md`. Add `--dry-run` to preview without a model call. Promotion to `lessons/` stays a human/PR step. |

## Utility scripts

| Command | What it does |
|---|---|
| `npm run lint` | Deterministic pass — no LLM. Checks frontmatter completeness, `[[wiki-link]]` integrity, source integrity (every `sources:` entry exists under `raw/`), section conformance for entity and playbook pages, Discovery item schema in playbooks, orphan detection (warning), `wiki/index.md` drift, stale frontmatter timestamps. Failures block commits. |
| `npm run index` | Rebuilds `wiki/index.md` from the current set of wiki pages. |
| `npm run discover:gdrive` | Re-runs Google Drive link discovery without ingesting — useful for previewing what the next `ingest:gdrive` would fetch. |
| `npm run backfill:hashes` | One-off maintenance: backfills `source_hash` frontmatter on existing source pages so subsequent `synthesise:sources` runs can skip unchanged inputs. |
| `npm run typecheck` | TypeScript typecheck of the tools themselves. |

You can also invoke the CLI directly: `npx tsx src/cli.ts <command> <subcommand>`.

## When something changes — what to run

A quick decision table. All commands run from `tools/`. The pipeline is two stages: **ingest** (mirror source → `raw/`) then **synthesise** (LLM: `raw/` → `wiki/`).

| What changed | Run | Notes |
|---|---|---|
| **GitBook docs** edited / pages added or deleted upstream | `./update.sh` | Incremental; deleted pages are auto-removed from `raw/` and `wiki/sources/`. |
| **GitBook section scope** (`.env` `GITBOOK_INCLUDE_SECTIONS`) | `rm -rf ../raw/gitbook` → `ingest:gitbook` → `synthesise:sources` → `synthesise:cross` → `lint` | Delete first to force a full re-mirror under the new scope (ingest is SHA-incremental). |
| **A repo's code** changed | `ingest:repos` → `synthesise:entities` → `synthesise:cross` → `lint` | Each eligible repo is re-cloned fresh every run. |
| **A repo added** to the `allow:` list in `raw/MANIFEST.yaml` | `ingest:repos` → `synthesise:entities` → `synthesise:cross` | New entity page is created. |
| **A repo removed** from the `allow:` list | `rm -rf ../raw/repos/<repo> ../wiki/entities/<repo>.md` → `ingest:repos` → `synthesise:entities` → `synthesise:cross` | **Not auto-removed** — repo ingest and entity synthesis do not clean orphans, so delete them by hand. |
| **You want to rebuild from scratch** | See [First run from empty state](#first-run-from-empty-state) below, after deleting the generated layers | Delete `raw/{gitbook,repos,sites,gdrive}` and `wiki/{sources,entities,concepts,comparisons,flows,playbooks}` + `wiki/{contradictions,index,log}.md`. **Keep** `raw/MANIFEST.yaml`, `wiki/overview.md`, `wiki/research-queue.md`, `lessons/`, and `elicitation/`. |
| **A knowledge gap** to fill (capture tacit knowledge) | `elicit:scan` → `elicit:guide` → answer → `elicit:synthesise` → promote → `elicit:scan` | See the [Elicitation Engine — Operating Guide](elicitation.md). |

> `wiki/` is git-tracked, so any synthesis run is recoverable with `git checkout -- wiki/` if the output looks wrong. Run the synthesise steps one at a time and check each before continuing.

## Routine update — `update.sh`

For day-to-day refreshes after GitBook changes upstream, run the all-in-one script:

```bash
./tools/update.sh
```

It does:

1. `git pull --ff-only` on the `openg2p-documentation` clone.
2. **Incremental** GitBook ingest.
3. Google Drive ingest (auto-discovered from GitBook).
4. Mirror playbooks (verbatim).
5. **Incremental** sources synthesis.
6. Cross synthesis (concept + comparison pages).
7. Lint.

Repos and entities are **not** touched by `update.sh`. Refresh them manually when needed:

```bash
npm run ingest:repos
npm run synthesise:entities
```

Configuration via env (optional):

* `OPENG2P_DOCS_PATH` — path to the `openg2p-documentation` clone (defaults to `../openg2p-documentation`).
* `SYNTHESISE_INCLUDE_PREFIX` — narrow synthesis to a subtree.

## First run from empty state

```bash
npm run ingest:gitbook
npm run ingest:repos
npm run ingest:sites
npm run ingest:gdrive
npm run mirror:playbooks
npm run synthesise:sources
npm run synthesise:entities
npm run synthesise:cross
npm run lint
```

Each ingest is idempotent. Subsequent runs are incremental where supported (gitbook ingest, sources synthesis); entities, cross, and sites are full-rebuild for now.
