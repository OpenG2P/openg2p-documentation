# Roadmap

Status of the Advisor as of v0.x. Items are roughly ordered by priority within each section.

## Status

* **Chat mode** — shipped, wiki-grounded, citations working.
* **Project mode Phase 1 (Requirements)** — shipped end-to-end. Discovery items, recording, reports, approval flow all functional.
* **Project mode Phase 2 (Build)** — shipped through step 10 (image build + push). Steps 11–13 (test gen + sandbox + smoke) still stubbed.
* **Phases 3–5** — UI stub only. Designed; not built.
* **Auth** — mock user from env vars. Keycloak integration deferred.
* **Lesson feedback into wiki** — designed; not built. Sessions don't yet emit a digest.

## In-progress

### Phase 2 chat panel

Right now Phase 2's UI is just the build-activity panel (terminal log + Start/Stop). There's no conversational way for the implementer to:

* Record Phase 2 Discovery items (currently bypassed via `npm run seed:phase2`).
* Paste a CI / build error and ask the LLM to suggest a fix.
* Request edits to specific generated files.

Planned: split-panel layout (chat left, build log right). Chat has tools to read/write `working_case`, read/write generated workspace files, and trigger a partial rebuild. Replicates the Claude-Code-like loop inside the product.

### Local compile + auto-repair loop

Local compile (Python `py_compile`, helm lint, YAML parse) is shipped — catches syntax-level codegen errors in seconds. The next step is automatic repair: when compile fails, fetch the error, send it back to the codegen LLM with "fix the file at path X, here's the error", regenerate, retry. Cap at 2-3 retries before surfacing to the user.

### CI failure-trace fetching

When GitLab CI does run (e.g. user manually triggers a pipeline) and fails, the orchestrator should fetch the failing job's trace via the GitLab API and surface it inline in the build panel — no need to leave the page to read CI logs. The GitLab client method exists; the orchestrator wiring is partial.

## Deferred

### Phases 3–5

The implementer's environments, not the advisor's local sandbox. Advisor's role becomes guidance + checklists rather than direct execution. Designed in the playbook; not built in v0.x.

### Image push to Docker Hub during iteration

Defer credentials handling; tarball / GitLab-Container-Registry-only handover for v0.x.

### Cross-session pattern analysis

"Five customers asked about MOSIP integration → improve the playbook" — needs scale of accumulated sessions before patterns are meaningful.

### Real-time multi-user collaboration on a project

Single user per project initially.

### Mobile UI

Desktop-first.

## Known issues

### Chat mode depth of search

Multi-hop reasoning across the wiki is shallow. The model has 20 tool-call iterations to traverse pages; complex cross-cutting questions ("how does eligibility relate to scoring?") sometimes hit that limit before fully exploring.

Mitigations on the roadmap:

* Re-add the wiki's `index.md` inline in the system prompt (was removed when token rate limits became painful — should fit again on Tier 2 Anthropic accounts or after model token-context expansion).
* Add a section-aware retrieval tool returning matching `##`/`###` blocks with surrounding context instead of whole pages.
* Track wiki gaps in a `wiki_gaps` table for the wiki team to address.

### `xlsx` package vulnerability

`docExtract.ts` uses `xlsx` (SheetJS community edition) to parse uploaded `.xlsx` / `.xls` / `.csv` files for the extraction LLM. The package has a published prototype-pollution advisory (CVE-2023-30533, CVE-2024-22363).

Not blocking right now — the vulnerability requires an attacker-controlled workbook to be parsed AND the resulting object graph to be passed back into a function that walks `__proto__` keys unsafely. Our path doesn't do that. Plan: switch to `exceljs` (~30 line change) during a future dependency-hardening pass.

### Workspace dir cleanup

Old per-project workspaces don't auto-archive. The `cleanup:phase2` script removes one project's workspace explicitly, but inactive projects accumulate forever. Planned: 60-day idle auto-archive (tarball + delete from disk; user can request restore).

## Models per purpose

| Mode | Recommended | Why |
|---|---|---|
| Chat | Anthropic Haiku 4.5 / Gemini 2.5 Flash | Cheap, fast, good tool-call reliability. Most chat traffic is single-page retrieval. |
| Project (Phase 1) | Anthropic Haiku 4.5 | Conversational + structured tool calls (`record_discovery_answer`). Haiku is plenty. |
| Build (Phase 2 codegen) | Anthropic Sonnet 4.6 | Real Python/Helm/Dockerfile generation. Worth the cost for fewer iterations on broken code. |

All three are independently configurable via env vars (`CHAT_PROVIDER`/`MODEL`, `PROJECT_PROVIDER`/`MODEL`, `BUILD_PROVIDER`/`MODEL`). Switch any of them to OpenAI / Groq / Gemini if rate limits or pricing change.
