# Elicitation Engine — Operating Guide

This is the **step-by-step guide** for running the knowledge-elicitation loop. For *why* it exists and the ideas behind it (the taxonomy as a completeness spec, the "superhuman index", tacit vs codified knowledge), see [Concept — WikiLLM § Elicitation](concept.md#elicitation-knowing-what-you-dont-know). Keep the two separate: this page is steps, that page is concepts.

All commands run from the `tools/` directory of the [g2p-wiki](https://github.com/OpenG2P/g2p-wiki) repo.

## The loop at a glance

```
elicit:scan      →  measure coverage, produce a prioritized gap ledger
   │
elicit:guide     →  turn the top gaps into grounded interview guides (questions)
   │
(human)          →  an engineer answers the questions inline + attaches artifacts
   │
elicit:synthesise→  fold the answers into a lessons/proposed/ draft
   │
(human)          →  review the draft, promote it into lessons/
   │
elicit:scan      →  re-measure; the cell flips toward covered, the index rises
```

The engine never says "we don't know enough" in the abstract. Every gap is a specific, scored, answerable question with a target wiki page. That is what makes "plug all the gaps" tractable.

## Prerequisites

* The same setup as the other scripts (see [Scripts § Setup](scripts.md)): Node 22+, and the `claude` CLI logged in.
* `elicit:scan` and a plain `elicit:guide` need **no** LLM — they read the wiki on disk.
* `elicit:guide --sharpen` and `elicit:synthesise` **do** call the `claude` CLI (one call per gap / per intake).

## Step 1 — Measure (`elicit:scan`)

```bash
npm run elicit:scan
```

Reads `wiki/` plus the evidence sources (`research-queue.md`, `contradictions.md`, and the advisor's `content-gaps.md` when present), classifies every taxonomy cell **covered / partial / gap**, scores priority, and writes:

* `elicitation/gaps/gap-ledger.md` and `.json` — the prioritized backlog.
* `elicitation/gaps/coverage.md` — per-area coverage and the headline **superhuman index** (weighted % of cells backed by a page at `confidence ≥ medium`; partials count half).

Run this first, and again at the end of every cycle — the delta is the progress signal.

## Step 2 — Generate the interview questions (`elicit:guide`)

You do **not** write the questions yourself — the engine generates them from the taxonomy and (optionally) sharpens them against the current wiki.

```bash
npm run elicit:guide -- --top 15 --sharpen      # top 15 open cells, LLM-refined
npm run elicit:guide -- --area data-layer        # one whole area
npm run elicit:guide -- data-layer.postgres-placement   # one specific cell
```

* `--top N` — generate guides for the N highest-priority open cells (default 8).
* `--sharpen` — rewrite the questions sharper against the gap, via the `claude` CLI (one call per cell). Without it, questions come verbatim from the taxonomy (deterministic, no LLM).
* Output: one file per cell at `elicitation/interviews/<cell-id>.md`.

> **Warning:** `elicit:guide` **overwrites** the interview file for each cell it regenerates. Always (re)run it **before** anyone types answers — re-running it after answers are filled in will discard those answers. It writes questions only; it does not preserve answers.

## Step 3 — Answer the interview (human step)

Open an interview file, e.g. `elicitation/interviews/data-layer.postgres-placement.md`, and fill it in **inline, in the same file**:

* **`## Open questions (please answer)`** — type your answer on the `_Answer:_` line under each question. This is the core task.
* **`## Variation to probe`** — not separate questions; a lens. Weave the listed dimensions (e.g. cloud/on-prem, scale, country) **into** your answers.
* **`## Artifacts to attach`** — check the box and attach/link any real, sanitised file (a `values.yaml`, a runbook, a postmortem). Artifacts are "worth more than memory" — synthesis extracts hard facts from them.

The other sections (`What we're trying to learn`, `What the wiki already knows`) are read-only context, there so you don't waste time re-explaining the docs.

You do not have to answer every question — partial answers still synthesise. You may also add knowledge the questions didn't ask for.

## Step 4 — Synthesise the answers (`elicit:synthesise`)

```bash
npm run elicit:synthesise -- data-layer.postgres-placement.md --dry-run   # preview, no model call
npm run elicit:synthesise -- data-layer.postgres-placement.md             # writes the draft
```

Pass the **filename** — the script auto-finds it (it searches the current dir, `elicitation/interviews/`, and `elicitation/intake/`). It reads the filled guide, calls the `claude` CLI, runs a **PII-scrub**, sets `confidence` honestly, links provenance back to the gap, and writes a draft to **`lessons/proposed/<slug>.md`**. It never writes straight into `wiki/`.

## Step 5 — Review & promote (human gate)

Read `lessons/proposed/<slug>.md`. If it is accurate and the redaction is clean, **promote** it by moving the file into `lessons/` (a PR / admin step). Discard it if it is not good enough.

Only **promoted** lessons (in `lessons/`) count toward coverage — drafts in `lessons/proposed/` do not.

## Step 6 — Re-measure (`elicit:scan`)

```bash
npm run elicit:scan
```

The newly promoted lesson now backs its taxonomy cell, so the cell flips toward **covered** and the superhuman index rises. That delta is the cycle's output.

## Where the files live

| Path | What it is | Edited by |
|---|---|---|
| `elicitation/taxonomy.yaml` | The completeness spec (areas → cells). Durable, hand-authored. | Humans (rarely) |
| `elicitation/gaps/{gap-ledger.md,gap-ledger.json,coverage.md}` | Generated by `elicit:scan`. | `elicit:scan` |
| `elicitation/interviews/<cell>.md` | Generated questions; **humans fill in answers here**. | `elicit:guide` + humans |
| `lessons/proposed/<slug>.md` | Synthesised draft, awaiting review. | `elicit:synthesise` |
| `lessons/<slug>.md` | Promoted lesson the advisor reads. | Admin via PR |

## See also

* [Concept — WikiLLM § Elicitation](concept.md#elicitation-knowing-what-you-dont-know) — the ideas behind the loop.
* [Scripts § When something changes](scripts.md#when-something-changes--what-to-run) — how elicitation fits with the ingest/synthesis commands.
