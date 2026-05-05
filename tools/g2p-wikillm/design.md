# Design

## High-level shape

Three layers, three rules:

| Layer | Rule | Authored by |
|---|---|---|
| `raw/` | Immutable. Never edit by hand. Replaced wholesale by ingest jobs. | Ingest scripts |
| `wiki/` | LLM-generated. Regenerated when `raw/` changes. Edits get overwritten. | Synthesis scripts |
| `lessons/` | Admin-curated, anonymised. Promoted from advisor sessions; never raw. | Admin via PR |

Operational state (active sessions, message logs, working_case JSON) lives in the **advisor's** Postgres, **not in this repo**. This repo holds only the durable knowledge artefact.

## Sources ingested

The single source of truth for what gets ingested is `raw/MANIFEST.yaml`. As of writing, four sources are configured:

1. **OpenG2P documentation (GitBook)** — local clone of the `openg2p-documentation` repo. Skips any path containing `_Archive` (case-insensitive), `node_modules`, or `.git`. Only `.md` files.
2. **OpenG2P repositories (GitHub)** — public, non-archived repos under [github.com/OpenG2P](https://github.com/OpenG2P). Per repo, only **structural** files are extracted: README, CHANGELOG, `docs/`, OpenAPI specs, GraphQL/Proto schemas, DB migrations, helm charts, Dockerfile, `.env.example`, controllers/routes (signatures only), and package metadata. The current allow-list focuses on Registry Gen2 repos plus farmer-registry, national-social-registry, and ui-widgets.
3. **Google Drive** — Google Docs, Sheets, Slides, and folders **auto-discovered** from links found in ingested GitBook content. Fetched via public export URLs (no auth). Folders enumerated via the Drive API (requires `GOOGLE_API_KEY`).
4. **OpenG2P website** — snapshot of [www.openg2p.org](https://www.openg2p.org), crawled to a configured max depth, converted from HTML to markdown.

To add a source, edit `raw/MANIFEST.yaml` and run the matching ingest command (see [Scripts](scripts.md)).

## Folder structure

```
g2p-wiki/
├── CLAUDE.md             # the contract (see "CLAUDE.md vs index.md")
├── LICENSE
├── raw/                  # immutable sources, never edited by hand
│   ├── MANIFEST.yaml     # source registry: what to ingest, allow/deny lists
│   ├── gitbook/          # mirror of openg2p-documentation (excl _Archive)
│   ├── repos/            # extracted structural files from github.com/OpenG2P
│   ├── gdrive/           # exported Google Docs/Sheets/Slides
│   └── sites/            # snapshot of www.openg2p.org
├── wiki/                 # LLM-built derivative pages
│   ├── concepts/         # abstract topics (eligibility, identity-resolution, …)
│   ├── entities/         # concrete things (modules, products, services, repos)
│   ├── sources/          # one-page summaries of each ingested document
│   ├── comparisons/      # cross-cutting analyses (clusters, contrasts)
│   ├── playbooks/        # phased implementation guides
│   ├── index.md          # auto-maintained catalog of every wiki page
│   ├── log.md            # append-only record of ingests, syntheses, lints
│   ├── overview.md       # short hand-curated map of the knowledge graph
│   └── research-queue.md # durable list of open questions surfaced during use
├── lessons/              # promoted, scrubbed digests from advisor sessions
│   └── proposed/         # admin queue (auto-redacted, not yet approved)
└── tools/                # ingest, synthesise, lint scripts
    ├── package.json
    ├── update.sh
    └── src/
        ├── cli.ts
        ├── ingest/   {gitbook, repos, gdrive, sites}.ts
        ├── synthesise/ {sources, entities, cross}.ts
        ├── mirror/   {playbooks}.ts
        └── lint.ts
```

### What goes in `raw/`

* Verbatim mirrors of the source material, with directory structure preserved where it carries meaning.
* Pinned to a commit SHA (for git sources) or fetch timestamp (for web sources).
* A per-source `manifest.yaml` capturing url/sha/pulled\_at/license.
* **Never written to by anything except ingest scripts. Never read by the advisor at runtime.**

### What goes in `wiki/`

LLM-built, schema-conformant markdown pages. Each page has YAML frontmatter (title, type, slug, sources, related, tags, created, updated, confidence) and a body that follows the schema for its type:

* **`concept/`** — abstract ideas (e.g. eligibility, identity resolution). Body: Definition, Where it appears, Variants and decisions, Related concepts.
* **`entities/`** — concrete things (modules, repos, services). The lens layer for one repository or service: it carries the meaning, points at the code for the spelling. Body: Purpose, Public surface (characterised, not enumerated), Data model (relationships and meaning, not column lists), Rationale, State and lifecycle (when applicable), Dependencies, Cross-layer flows, Deployment shape, Where to read deeper. Frontmatter additionally includes `commit_sha`.
* **`sources/`** — one-page summaries of each ingested document. Body: Origin, Summary, Key claims, Terminology introduced, Cross-references, Notes for synthesis. This is the transparency layer — readers can trace any wiki claim back to the source.
* **`comparisons/`** — cross-cutting analyses spanning multiple entities (e.g. all `spar-*` repos and how they fit together). Body: Purpose, Cluster, How they fit together, Distinctions, Open questions.
* **`flows/`** — directed, sequential traces of a request, event, or job as it crosses entity boundaries (e.g. `flow-partner-ingest`: Partner API → core classify/enrich → Changerequest Controller → store). Body: Trigger, Steps, State transitions, Failure modes, Variants, Where to read deeper. Flows capture cross-layer behaviour that is invisible from any single entity page.
* **`playbooks/`** — phased implementation guides (e.g. Registry use-case implementation). Each phase has Discovery items (`Ask`, `Why`, `Required`, `Type`), Activities, References, Gap analysis, Output spec, Common pitfalls. The advisor walks these section by section.

Plus a single `wiki/glossary.md` that maps OpenG2P vocabulary across audiences — what a term means in code, in product docs, and to operators.

Cross-references between wiki pages use `[[slug]]`. The lint pass verifies every link resolves.

#### Lens, not mirror

The wiki follows the **lens-not-mirror** principle: it documents what code cannot tell an agent on its own (purpose, rationale, cross-cutting patterns, state machines, vocabulary mappings) and points at the code for everything else (exact paths, column names, signatures). A page should never restate a spec that is listed in its `Where to read deeper` section. The lint pass enforces this with heuristics: it warns when an entity's `## Public surface` enumerates more than ~10 endpoints, when `## Data model` enumerates columns alongside a migration source, or when high/medium-confidence pages have an empty `## Rationale`. See [Concept — WikiLLM](concept.md) for the full reasoning.

### What goes in `lessons/`

Admin-curated digests promoted from advisor sessions. Flow:

1. A session ends; the advisor produces a digest.
2. An automated PII scrub (Presidio + LLM pass) produces a redacted draft.
3. The draft lands in `lessons/proposed/` with a redaction log.
4. An admin reviews and, on approval, moves the file to `lessons/`.
5. The advisor reads `lessons/` alongside `wiki/` at runtime — they are surfaced together, never silently merged.

### What goes in `tools/`

The ingest, synthesis, and lint scripts. See [Scripts](scripts.md).

## Confidence labelling

Every wiki page is tagged by the synthesis pass:

* **high** — directly supported by an unambiguous source.
* **medium** — supported, but required minor inference or composition across sources.
* **low** — required substantial inference, or the source was a single sparse mention.
* **needs-review** — sources contradict each other, or the LLM was unable to resolve ambiguity. Surfaced in lint reports.

## Hard rules for synthesis

* Never invent facts not supported by `raw/`.
* Never mirror source code into wiki pages — entity pages summarise structure and link to code at a pinned SHA.
* Never auto-merge `lessons/` content into entity or concept pages.
* Never write to `raw/`. Synthesis only reads from `raw/` and writes to `wiki/`.
