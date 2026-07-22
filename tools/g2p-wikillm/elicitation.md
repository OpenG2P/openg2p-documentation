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

## Persona elicitation — testing the live advisor

The interview loop above finds gaps by scanning the **static wiki**. Persona elicitation finds gaps by running questions through the **real advisor answer path** — it catches cases where a page exists but the advisor still can't produce a usable answer. The two are complementary; run both.

The unit of audience is a **persona**. The taxonomy is now persona-tagged (`persona:` on each area); the original deployment areas are the `implementer` persona, and there is a new set of **operator** areas — a government administrator running the deployed system ("how do I do X", no devops, no concepts).

### Step A — generate the question bank (`elicit:persona-generate`)

```bash
npm run elicit:persona-generate -- operator --per-cell 4   # ~4 phrasings per operator cell
npm run elicit:persona-generate -- operator --dry-run      # list cells, no LLM
```

Reads the taxonomy cells for that persona and generates realistic questions in that persona's voice (one Claude CLI call per area). Writes `elicitation/personas/<persona>.json`. Because the questions derive from the taxonomy, the bank is comprehensive by construction. **Review and freeze the bank** — a stable bank is what makes it a usable regression/eval set across model changes.

### Step B — run the bank through the advisor (in the advisor repo)

```bash
npm run persona -- operator            # answers each question via the REAL advisor, critic judges
```

This lives in **g2p-advisor**, not here, because it must exercise the deployed answer path. The **answerer** uses the advisor's OpenRouter model (it has to reproduce what a real user gets); the **critic** uses the Claude CLI (offline QA). Weak answers become `GapRecord`s in `data/persona-gaps/<persona>.json`. See the advisor's [Gap & feedback loop](../g2p-advisor/gap-feedback-loop.md).

### Step C — triage the gaps (`elicit:triage`)

```bash
npm run elicit:triage                  # collect + classify + rollup
npm run elicit:triage -- --no-llm      # collect + report only, skip classification
```

One pass does three things:

1. **Collect** — merge every producer's gap records into one ledger, `elicitation/gaps/gap-records.json`. Idempotent: prior triage and hand edits are preserved; only evidence refreshes.
2. **Triage** — for each untriaged gap, classify it into a **sink** (`source-fix` / `synthesis-fix` / `lesson` / `not-a-gap`) via the Claude CLI, using the retrieval trace as the key signal. Sets `sink`, `target`, `triage_rationale`.
3. **Rollup** — write `elicitation/gaps/gap-report.md`: source-fix gaps clustered by area into **proposed Documentation-epic stories**, synthesis-fixes as no-ticket prompt tweaks, lessons separately.

**Filing the Jira stories is manual by design** — the rollup proposes them; a human reviews the report and files them, because creating tickets is an external action. The `sink` in `gap-records.json` is hand-editable; a re-run keeps your overrides.

### Where the persona/triage files live

| Path | What it is | Written by |
|---|---|---|
| `elicitation/personas/<persona>.json` | Generated question bank (freeze after review). | `elicit:persona-generate` |
| `elicitation/gaps/gap-records.json` | Unified gap ledger (durable, hand-editable). | `elicit:triage` |
| `elicitation/gaps/gap-report.md` | Triage report — Jira proposal + prompt-fix list + lessons. | `elicit:triage` |
| `data/persona-gaps/<persona>.json` (advisor) | Raw gap records from a persona run. | advisor `npm run persona` |

## See also

* [Concept — WikiLLM § Elicitation](concept.md#elicitation-knowing-what-you-dont-know) — the ideas behind the loop, including the two-producers/three-sinks model.
* [G2P Advisor — Gap & feedback loop](../g2p-advisor/gap-feedback-loop.md) — the persona harness and answer feedback, from the advisor side.
* [Scripts § When something changes](scripts.md#when-something-changes--what-to-run) — how elicitation fits with the ingest/synthesis commands.
