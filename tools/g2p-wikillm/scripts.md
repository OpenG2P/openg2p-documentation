# Scripts

All scripts live under `tools/` in the [g2p-wiki](https://github.com/OpenG2P/g2p-wiki) repository. They fall into four families: **ingest**, **synthesise**, **mirror**, and **utility** (lint, index, discovery, hash backfill).

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

## Utility scripts

| Command | What it does |
|---|---|
| `npm run lint` | Deterministic pass — no LLM. Checks frontmatter completeness, `[[wiki-link]]` integrity, source integrity (every `sources:` entry exists under `raw/`), section conformance for entity and playbook pages, Discovery item schema in playbooks, orphan detection (warning), `wiki/index.md` drift, stale frontmatter timestamps. Failures block commits. |
| `npm run index` | Rebuilds `wiki/index.md` from the current set of wiki pages. |
| `npm run discover:gdrive` | Re-runs Google Drive link discovery without ingesting — useful for previewing what the next `ingest:gdrive` would fetch. |
| `npm run backfill:hashes` | One-off maintenance: backfills `source_hash` frontmatter on existing source pages so subsequent `synthesise:sources` runs can skip unchanged inputs. |
| `npm run typecheck` | TypeScript typecheck of the tools themselves. |

You can also invoke the CLI directly: `npx tsx src/cli.ts <command> <subcommand>`.

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
