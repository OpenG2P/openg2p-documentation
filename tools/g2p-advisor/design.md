# Design

## Tech stack

| Layer | Choice |
|---|---|
| Web app | Next.js 14 (App Router), TypeScript |
| Database | Postgres (no pgvector — embedding pipeline removed) |
| LLMs | OpenAI SDK against any OpenAI-compatible endpoint (OpenAI / Anthropic / Gemini / Groq) |
| Auth | Keycloak (deferred — mock auth in v0.x) |
| Sandbox runtime | Docker Compose, per project, on the advisor host |
| Wiki access | Filesystem reads of [`g2p-wiki/`](../g2p-wikillm/README.md) via a typed `WikiClient` |
| Streaming | Server-Sent Events |

## Repository relationships

```
g2p-advisor       — this repo. Reads from g2p-wiki, persists per-user/per-project state in Postgres,
                    generates code in per-project workspaces, runs sandboxes via docker-compose.

g2p-wiki          — the knowledge base. Built once from authoritative sources, consumed at runtime.
                    See tools/g2p-wikillm.

openg2p-documentation
                  — the Gitbook source. Authored by the OpenG2P team. Ingested into g2p-wiki.
                    The Advisor never reads Gitbook directly; it reads the wiki layer.
```

## Reading playbook from Gitbook (minimal hardcoding)

Phase walkthrough is data-driven. The [Registry implementation playbook](../../products/registry/registry/use-case-implementation.md) lives in this Gitbook. The wiki ingest pipeline mirrors playbook pages verbatim into `wiki/playbooks/<slug>.md` (deliberately bypassing the synthesis step that collapses structure into prose). The Advisor's `WikiClient.getPlaybook("registry")` reads from there.

What's defined in the playbook (not in code):

* Every phase's purpose, enter/exit conditions, Activities, gap checks, output shape.
* Every Discovery item: question, validation, type, impact, follow-ups.
* Every reference + common-pitfall section.

What's in code (not in the playbook):

* The state machine that loops over phases (`runBuildJob` for Phase 2).
* The functions that *execute* Activities (file generation, GitLab API calls, docker build).
* The LLM tool definitions (`record_discovery_answer`, `phase_complete`, etc).

When the playbook adds a new Discovery item, the Advisor records it without a code change. When it adds an Activity that requires new code, the orchestrator gets extended.

## Prompt layering

Every LLM turn assembles a prompt of the form:

```
System: <base advisor prompt>
        <CLAUDE.md from wiki>             ← agent guidance, page types, conventions
        <current mode + phase>
        <playbook page for current phase> ← Discovery items + Activities + gap checks
        <working_case JSON>               ← what the implementer has already told us
        <recently-relevant wiki pages>

History: <last N messages, summary of older>

User: <current message>
```

OpenAI prompt caching keeps the static parts cheap across turns. The dynamic parts (working_case, recent messages) change per turn; everything else is cacheable.

## LLM mode factory

Three independently-configured modes, each with its own provider + model:

| Mode | Used for | Default | Typical cost profile |
|---|---|---|---|
| `chat` | Chat-mode answers | OpenAI gpt-4o-mini | Cheap, fast |
| `project` | Project-mode Phase 1 conversation | OpenAI gpt-4o-mini | Cheap, fast |
| `build` | Phase 2 codegen | Anthropic Sonnet | Strong, slower |

Each mode reads its own env vars: `CHAT_PROVIDER`/`CHAT_MODEL`, `PROJECT_PROVIDER`/`PROJECT_MODEL`, `BUILD_PROVIDER`/`BUILD_MODEL`. The factory at `src/lib/llm.ts` picks the right OpenAI-SDK base URL per provider.

**Recommended setup** (real-world):

```
CHAT_PROVIDER=anthropic        CHAT_MODEL=claude-haiku-4-5-20251001
PROJECT_PROVIDER=anthropic     PROJECT_MODEL=claude-haiku-4-5-20251001
BUILD_PROVIDER=anthropic       BUILD_MODEL=claude-sonnet-4-6
```

Haiku for the conversational paths (very reliable tool-calling, cheap), Sonnet for the codegen path (worth the cost for fewer iterations on broken code).

## Wiki access from the Advisor

Both modes go through a typed `WikiClient` (`src/lib/wiki/client.ts`) that reads the `g2p-wiki` repo from disk. Tools exposed to the LLM:

* `wiki_search(query, limit?)` — substring search across synthesised pages, ranked.
* `wiki_get_page(slug)` — fetch a page's full body + frontmatter.
* `wiki_list_by_type(type)` — enumerate pages of a given type with summaries.
* `wiki_grep(pattern, pathPrefix?)` — regex grep across both `wiki/` and `raw/`.
* `wiki_read_raw(path)` — read an original Gitbook / repo file from `raw/` by relative path. Path-traversal-guarded.

Project mode adds two recording tools (gated by a recording context):

* `record_discovery_answer(id, value)` — persist a Discovery item answer into `working_case`.
* `phase_complete(phase)` — advance the project to the next phase.

A shared `runToolLoop()` helper handles the function-calling loop: model emits tool calls → server dispatches via `WikiClient` (or recording callbacks for the mutation tools) → results fed back into the conversation → model produces final streamed response. Cap at 20 iterations.

## Postgres schema (sketch)

```
users                — synced from Keycloak (mock for now)
projects             — id, user_id, name, current_phase, status, working_case JSONB
project_messages     — chat history, phase-scoped (each phase has its own thread)
chat_messages        — chat-mode history per user (not project-scoped)
phase_reports        — versioned approved reports per project + phase
build_jobs           — Phase 2: one linear job per project, status running|succeeded|failed|aborted
build_job_events     — append-only event feed: step_start, step_done, step_fail, log, summary
```

Each Phase's chat sees only its own thread — the `phase` column on `project_messages` keeps Phase 1's walkthrough talk from leaking into Phase 2's LLM context window. The `GET /api/projects/{id}/messages?phase=N` endpoint and the per-phase POST handlers honour this filter.

## Phase 2 build orchestrator — playbook-driven

Phase 2 is a single linear job with **abort-on-error, build-locally-first** semantics. The Activity sequence is **not hardcoded in the orchestrator** — it's read from the playbook's `### Activities` section in [use-case-implementation.md](../../products/registry/registry/use-case-implementation.md). The orchestrator's main loop iterates the parsed Activity name list and dispatches each name to a registered handler in `HANDLERS` (`src/lib/build/orchestrator.ts`).

This means **reordering or adding Activities is a playbook edit**:

* Add an Activity → playbook edit + register the handler in `HANDLERS`.
* Reorder Activities → playbook edit only.
* Remove an Activity → playbook edit only.

Current Activity sequence (15 steps; live source is the playbook):

```
1.  collect_build_inputs           ← validate working_case has every required key
2.  prepare_gitlab_workspace       ← reserve subgroup + project shells, allowlist CI_JOB_TOKEN
3.  clone_reference_registry       ← fresh clone of farmer-registry
4.  generate_extension_files       ← LLM-driven codegen
5.  compile_extension              ← `python -m py_compile`
6.  generate_deployment_files      ← deterministic templates: Helm, Docker, sandbox compose
7.  compile_deployment             ← `helm lint` + YAML parse
8.  build_images_locally           ← `docker build` only — no registry push yet
9.  generate_test_suite            ← Python pytest (httpx) + pytest-playwright
10. deploy_local_sandbox           ← `docker compose up -d` on the advisor host
11. run_smoke_tests                ← `pytest tests/` against the live sandbox
   ────────────── EVERYTHING ABOVE IS LOCAL — no GitLab side effects ──────────────
12. push_extension_repo            ← `git init` + force-push (only after smoke tests passed)
13. push_deployment_repo           ← `git init` + force-push deployment repo (incl. tests/)
14. push_images_to_registry        ← `docker push` to GitLab Container Registry
15. produce_build_report           ← versioned report saved to phase_reports/
```

**Build-locally-first** is the contract: a failed Activity at any local step (1–11) leaves zero GitLab side effects — no commits pushed, no images uploaded. The implementer iterates locally without polluting the GitLab repo with broken commits or burning CI minutes. Only after sandbox + smoke tests pass do Activities 12–14 publish.

**Update / change loop**: when the implementer changes a Phase 2 Discovery answer after a successful build, re-running the build re-executes every Activity. Docker layer caching + git's incremental push keep re-runs fast on minor changes.

**Failure semantics**: any handler that throws stops the phase. The orchestrator marks the job failed, emits a `summary` event, and stops. The implementer fixes the underlying cause (usually a Discovery answer or a model output) and re-runs from scratch — no resume mid-flight.

## Image naming convention

Generated Docker images follow `<org_mnemonic>-<registry_mnemonic>-<service>:<tag>`. E.g. for an org with mnemonic `doh` building a `health-worker` registry, the staff portal API lands at:

```
registry.gitlab.com/openg2p/g2p-advisor/<implementer-handle>/health-worker-deployment/doh-health-worker-staff-portal-api:develop
```

The Helm wrapper-chart name follows the same convention: `<org>-<mnemonic>-registry`.
