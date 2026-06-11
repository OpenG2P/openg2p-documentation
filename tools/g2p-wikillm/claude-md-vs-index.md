# CLAUDE.md vs wiki/index.md

The repository has two index-like files. They serve completely different purposes — keep the distinction clear.

## `CLAUDE.md` — the contract

`CLAUDE.md` lives at the **root of the repo**. It is the **schema and operating contract** for everything in the wiki.

It is read by:

* The synthesis scripts, when they call the LLM to produce or update wiki pages — the contract is loaded into the prompt so the LLM emits schema-conformant pages.
* Anyone (human or LLM) running `claude` interactively inside this repo — `CLAUDE.md` is auto-loaded into the model's context, so a session in this directory already knows the wiki's rules.
* Reviewers of PRs against the wiki, as the canonical reference for "what should this page look like?".

It defines:

* Directory layout and what each layer is for.
* Page types (`concept`, `entity`, `source`, `comparison`, `flow`, `playbook`, `glossary`, `lesson`) and the body schema each must follow.
* Required frontmatter fields (`title`, `type`, `slug`, `sources`, `related`, `tags`, `created`, `updated`, `confidence`).
* Wiki-link convention (`[[slug]]`).
* The ingest, synthesis, and lint workflows.
* Confidence labelling rules.
* Interactive triggers — what to do when a human in a `claude` session says "ingest X", "lint", "track this", or "promote lesson Y".

`CLAUDE.md` is **hand-maintained**. It changes only when the design itself changes — adding a new page type, tightening a schema rule, adding a workflow.

## `wiki/index.md` — the catalog

`wiki/index.md` is **inside the wiki**. It is the **catalog of every page** the wiki currently contains, grouped by type.

It is read by:

* The advisor at query time — the first thing it does on any question is read `wiki/index.md` to find candidate pages, then drill into the relevant ones.
* Anyone browsing the wiki to see what's there.

It is **auto-maintained** by the synthesis scripts and the `rebuildIndex` utility. Every time a page is created, updated, or removed, `index.md` is updated to match. The lint pass enforces that `index.md` lists every wiki page exactly once.

It contains:

* One section per page type (Concepts, Entities, Sources, Comparisons, Playbooks).
* For each page: its title, slug, one-line description, and `[[wiki-link]]`.

`index.md` is **never edited by hand** — edits would be overwritten on the next synthesis run.

## Side-by-side

| | `CLAUDE.md` | `wiki/index.md` |
|---|---|---|
| Location | Repo root | Inside `wiki/` |
| Defines | The rules for wiki pages | The list of wiki pages that exist |
| Authored by | Humans (rarely) | Synthesis scripts (every run) |
| Consumed by | LLM during synthesis; humans writing PRs | The advisor at runtime; humans browsing |
| Changes when | The design changes | A page is added/updated/removed |
| Editable by hand | Yes | **No** |

## Mental model

Think of `CLAUDE.md` as the **building code** and `wiki/index.md` as the **directory of tenants**. The first tells you how a page must be built; the second tells you which pages exist right now.

## See also

* [Design](design.md) — page types and schema.
* [Scripts](scripts.md) — what regenerates `wiki/index.md`.
