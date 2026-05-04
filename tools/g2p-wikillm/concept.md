# Concept — WikiLLM

## Karpathy's idea, in one paragraph

Andrej Karpathy proposed treating an LLM-readable knowledge base less like a vector database and more like a **wiki**: a hand-shaped, cross-referenced graph of markdown pages, **compiled once at ingest time** from authoritative sources, with stable slugs and `[[wiki-link]]` cross-references. Instead of every query searching loose text chunks (which is lossy and often hallucinatory), the assistant reads pages from a curated graph — the same graph every time. The wiki is the durable artefact; the assistant on top is just a viewer.

For the long form of the idea, see Karpathy's note as captured here: [https://antigravity.codes/blog/karpathy-llm-wiki-idea-file#implementation-guide](https://antigravity.codes/blog/karpathy-llm-wiki-idea-file#implementation-guide).

## What we adopted

G2P WikiLLM follows this principle directly:

* **Compile once, read many.** Sources are ingested into `raw/`. An LLM-driven synthesis pass turns them into a graph of typed pages under `wiki/`. The advisor reads `wiki/` at runtime and never re-derives.
* **Typed pages, not blobs.** Every page is one of: `concept`, `entity`, `source`, `comparison`, or `playbook`. Each type has a fixed body schema (defined in `CLAUDE.md`).
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
