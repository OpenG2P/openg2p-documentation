# Modes

The Advisor has a hard mode toggle in the UI. The LLM cannot switch modes implicitly; it can only suggest a transition when intent is clear, with explicit user confirmation.

## Chat mode

Conversational interface for general OpenG2P questions. Reads the wiki's index, drills into relevant pages, synthesises an answer, cites pages with `[[wiki-link]]` references and clickable Gitbook URLs. Some chat history is preserved per user for context.

Not project-scoped. One ongoing chat per user.

**When to use it:** "What is the difference between PBMS and Bridge?", "Explain the OpenG2P deployment architecture", "Where do I configure beneficiary deduplication?"

### Known issues with Chat mode

* **Depth of search is shallow.** Chat mode is optimised for quick, single-page answers. Multi-hop reasoning ("compare X and Y across all references") often misses cross-cutting context. The model has 20 tool-call iterations to traverse the wiki; complex questions sometimes hit that limit before fully exploring.
* **The wiki's `index.md` is no longer inlined in the system prompt** (was 18K tokens — pushed turns over rate-limit ceilings). The model now discovers pages on demand via `wiki_list_by_type`. Result: occasional missed pages on broad questions ("how does eligibility relate to scoring?") because the model can't see all titles + summaries side-by-side.
* **Deep questions are redirected.** Project-mode prompts redirect "deep wiki" questions to Chat mode; Chat mode itself doesn't have an equivalent fall-through.

The roadmap to fix these:

1. Re-add the index inline once token rate limits allow.
2. Add a section-aware retrieval tool (Karpathy's "qmd" pattern) — return matching `##`/`###` blocks with surrounding context instead of whole pages.
3. Track gaps in a `wiki_gaps` table for the wiki team to address.

See [Roadmap](roadmap.md) for status.

## Project mode

The primary value proposition. The Advisor walks an implementer through a phased implementation effort, with the wiki's playbooks (currently the [Registry implementation playbook](../../products/registry/registry/use-case-implementation.md)) as the operating contract.

A user can have multiple projects open simultaneously. Each project has its own state, sandbox, working case, and chat thread.

See [Phases](phases.md) for the per-phase walkthrough.

## Off-topic handling in Project mode

The Advisor classifies each user message in Project mode and behaves accordingly:

| User message intent | Advisor behaviour |
|---|---|
| Directly relevant to current phase | Answer in flow |
| Related to OpenG2P broadly but off the current phase | Brief answer + gentle redirect back to the phase |
| Unrelated to OpenG2P | Polite redirect: *"For general queries, switch to Chat mode."* |

The model makes this call with appropriate prompting; not deterministic, but good enough.
