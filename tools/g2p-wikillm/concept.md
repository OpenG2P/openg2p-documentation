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

## Why this matters for OpenG2P

OpenG2P is a sprawling stack — Registry, PBMS, SPAR, MOSIP integration, dozens of repos, a large GitBook, and an evolving website. Implementers ask questions like *"which repo owns the eligibility engine?"*, *"what's the data model for the Social Registry?"*, *"what are the steps to set up a Registry use case?"* — questions that span repos, modules, and concepts. WikiLLM gives the advisor a single, structured place to read, with citations the implementer can verify.

## Related

* [Design](design.md) — how the principle is realised in this repo.
* [CLAUDE.md vs wiki/index.md](claude-md-vs-index.md) — the contract that synthesis must follow.
