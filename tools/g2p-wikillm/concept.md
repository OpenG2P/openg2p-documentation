# Concept — WikiLLM

## Karpathy's idea, in one paragraph

Andrej Karpathy proposed treating an LLM-readable knowledge base less like a vector database and more like a **wiki**: a hand-shaped, cross-referenced graph of markdown pages, **compiled once at ingest time** from authoritative sources, with stable slugs and `[[wiki-link]]` cross-references. Instead of every query searching loose text chunks (which is lossy and often hallucinatory), the assistant reads pages from a curated graph — the same graph every time. The wiki is the durable artefact; the assistant on top is just a viewer.

For the long form of the idea, see Karpathy's note as captured here: [https://antigravity.codes/blog/karpathy-llm-wiki-idea-file#implementation-guide](https://antigravity.codes/blog/karpathy-llm-wiki-idea-file#implementation-guide).

## Lens, not mirror

A second principle, complementary to Karpathy's, governs **how each page is written**: the wiki is a **lens** on the source, not a **mirror** of it. Its job is to capture what the source cannot tell an agent on its own — purpose, rationale, cross-cutting patterns, state machines, operator-vocabulary mappings, cross-layer flows — and to point at the source for everything else (exact paths, column names, method signatures, file locations).

A wiki that deliberately doesn't duplicate sources is dramatically more stable against churn: route additions and column edits don't invalidate it, because it never claimed those specific details in the first place. **What changes in the wiki is what changes in *meaning*, not what changes in *spelling*.**

This principle is enforced by the entity-page schema (which asks for characterisations, not enumerations) and by lint heuristics that warn when pages enumerate too much.

## What we adopted

G2P WikiLLM follows both principles directly:

* **Compile once, read many.** Sources are ingested into `raw/`. An LLM-driven synthesis pass turns them into a graph of typed pages under `wiki/`. The advisor reads `wiki/` at runtime and never re-derives.
* **Typed pages, not blobs.** Every page is one of: `concept`, `entity`, `source`, `comparison`, `flow`, `playbook`, or `glossary`. Each type has a fixed body schema (defined in `CLAUDE.md`).
* **Cross-references, not embeddings.** Pages link to each other with `[[slug]]`. A deterministic linter checks every link resolves.
* **Traceability.** Every page lists the `raw/` paths it was derived from in its `sources:` frontmatter. Every claim can be traced back to a source.
* **Confidence labelling.** Synthesis tags each page `high`, `medium`, `low`, or `needs-review` based on how strongly the source supported the page.

## What we did not adopt

* **No global rewriting on every change.** Updates are incremental. Re-mirroring is SHA-pinned; per-source synthesis skips pages whose input hash is unchanged.
* **No auto-folding of community content.** Lessons promoted from advisor sessions live in a separate `lessons/` tree and are surfaced *alongside* wiki pages, never silently merged in.

## Elicitation: knowing what you don't know

Ingesting sources captures **codified** knowledge — what is written down in docs and code. It cannot capture **tacit** knowledge: the experiential know-how that lives in senior engineers' heads (sizing rules, failure modes, on-prem vs air-gapped gotchas, site-specific quirks). For a deployment advisor, that tacit layer is the difference between a competent junior and a senior expert.

The **elicitation engine** is the mechanism that captures it. Its governing idea: *you don't become superhuman by loading everything once — you become superhuman by building a system that knows precisely what it knows and what it doesn't, and captures the missing knowledge faster than it decays.*

Three concepts make that tractable:

* **Taxonomy as a completeness spec.** A hand-authored checklist (`elicitation/taxonomy.yaml`) of everything a superhuman OpenG2P deployer must know, organised as *areas → cells*. Each cell is one unit of knowledge with a question, why it matters, and whether it is `tacit_likely`. Without this spec, "are we superhuman yet?" is unanswerable and elicitation is a random walk. The taxonomy is the **ruler**; the wiki is the **material** measured against it — they are independent (changing the repo list changes coverage, not the taxonomy).
* **The superhuman index.** A single number: the weighted % of taxonomy cells backed by a wiki page at `confidence ≥ medium`. Tracked across snapshots, it is the program's headline progress metric, and calibrated uncertainty is treated as a feature, not a flaw.
* **Grounded asks.** The engine never hands an expert a blank page. For each gap it shows what the wiki already knows, then asks only the hole — so an expert-hour captures the maximum new knowledge.

This extends the wiki's existing flywheel rather than replacing it: elicited answers are synthesised into `lessons/proposed/`, promoted into `lessons/`, and read by the advisor alongside `wiki/` — never silently merged into entity or concept pages.

### Two producers, one ledger

A "gap" — a fact the knowledge base failed to deliver — can be discovered two ways, and both feed the same pipeline:

* **Taxonomy-scan (spec vs static wiki).** The original producer: scan every taxonomy cell against the wiki and ask *"is there a page covering this?"*. Finds structural holes.
* **Persona elicitation (spec vs live advisor).** A newer producer: the AI takes on a real audience — starting with the **operator** (a government administrator running the deployed system, asking "how do I do X", no devops or concepts) — and fires that persona's questions at the **real advisor answer path**, then a critic judges the reply. Finds where the advisor *cannot actually answer*, even when a page exists. The question bank is generated from the taxonomy, so coverage is comprehensive by construction, and because it runs the real path it doubles as an eval set. Personas are a dimension of the taxonomy (`persona:` on each area); the existing deployment areas are the `implementer` persona.

Both emit the same record (`GapRecord`), carrying the **retrieval trace** — which wiki pages ranked, and which the advisor actually opened. That trace is what lets triage tell three failure modes apart, routing every gap to exactly one **sink**:

* **source-fix** — the fact is in no doc or code → author documentation (the only sink that earns a Documentation-epic Jira; the wiki re-derives once the doc lands).
* **synthesis-fix** — the fact *is* in a source but the wiki lens surfaced it badly, or the advisor ranked the right page yet never opened it → fix the synthesis prompt and regenerate (no ticket).
* **lesson** — tacit/operational knowledge in no source → capture as a lesson.

Nothing of value lives permanently in a gap record — it is transient triage state. The knowledge always lands in the docs, the synthesis prompt, or a promoted lesson.

For the step-by-step workflow, see the [Elicitation Engine — Operating Guide](elicitation.md).

## Why this matters for OpenG2P

OpenG2P is a sprawling stack — Registry, PBMS, SPAR, MOSIP integration, dozens of repos, a large GitBook, and an evolving website. Implementers ask questions like *"which repo owns the eligibility engine?"*, *"what's the data model for the Social Registry?"*, *"what are the steps to set up a Registry use case?"* — questions that span repos, modules, and concepts. WikiLLM gives the advisor a single, structured place to read, with citations the implementer can verify.

## Related

* [Design](design.md) — how the principle is realised in this repo.
* [Elicitation Engine — Operating Guide](elicitation.md) — the loop that captures tacit knowledge.
* [CLAUDE.md vs wiki/index.md](claude-md-vs-index.md) — the contract that synthesis must follow.
