# Phases

A typical Registry implementation proceeds through five phases. v0.x of the Advisor implements **Phase 1** (Requirements) and **Phase 2** (Build) end-to-end; Phases 3–5 are stubbed.

The phase definitions, Discovery items, Activities, and outputs are all in the [Registry implementation playbook](../../products/registry/registry/use-case-implementation.md). The Advisor reads the playbook at runtime — this page is a high-level summary; the playbook is the source of truth.

## Phase 1: Requirements Analysis

Pure conversation. The Advisor walks the implementer through every Discovery item in the playbook (country, registry purpose, registers list, existing systems being replaced, scale estimates, supported languages, notification triggers, etc.), captures answers into the project's `working_case`, runs Product Feature Discovery against the wiki's Registry feature set, identifies gaps, and produces a **Requirements Analysis Report**.

The report is versioned: every approval creates a new version; the previous approved version is marked superseded. Multiple drafts may coexist; only one approved at a time.

**Tools used by the Phase 1 LLM:**

* `record_discovery_answer(id, value)` — persists an answer into `working_case`.
* `wiki_search`, `wiki_get_page`, `wiki_list_by_type`, `wiki_grep`, `wiki_read_raw` — retrieval against the wiki for clarifications.
* `phase_complete(phase)` — advances to Phase 2 on explicit implementer approval.

**Default model:** Anthropic Haiku (cheap, fast, very reliable tool-calling).

### Phase 1 chat stages

The Phase 1 chat is stage-aware (mirroring Phase 2's behaviour):

| Stage | When | What the chat does |
|---|---|---|
| **Initial walkthrough** | `current_phase = 1` | Walks Discovery items in batches; records via `record_discovery_answer`; runs the sign-off flow (gap classification → Requirements Analysis Report → revisions loop → approval → save + advance to Phase 2) |
| **Already approved** | `current_phase > 1` | Refuses to restart the exit flow. On kickoff, gives a short reply pointing the user at Phase 2 (or offering to revisit captured answers / show a summary). If the user records a change, asks whether to produce a new approved report version. The previous version stays on disk (auto-versioned). |

## Phase 2: Build

Code generation, build, sandbox, handover. Single linear, **abort-on-error, build-locally-first** job per project.

The Activity sequence is **read from the playbook** ([use-case-implementation.md](../../products/registry/registry/use-case-implementation.md) → Phase 2 → `### Activities`). The orchestrator's main loop iterates the parsed list and dispatches each name to a TypeScript handler. Reordering Activities is a playbook edit — no code change needed.

16 Activities in the current sequence:

```
1.  collect_build_inputs       — validate working_case has every required input
2.  prepare_gitlab_workspace   — reserve subgroup + project shells; refuses to
                                  use a deletion-scheduled project
3.  clone_reference_registry   — fresh clone of farmer-registry
4.  generate_extension_files   — LLM codegen, per-Register batched
5.  review_extension_code      — LLM review pass; structured findings,
                                  critical → abort, warning → log
6.  compile_extension          — `python -m py_compile`
7.  generate_deployment_files  — Helm + Docker + sandbox compose templates
8.  compile_deployment         — `helm lint` + YAML parse
9.  build_images_locally       — `docker build` only (NO registry push)
10. generate_test_suite        — pytest + httpx + pytest-playwright
11. deploy_local_sandbox       — docker compose up on the advisor host
12. run_smoke_tests            — pytest against the running sandbox
   ─── above this line is local-only; nothing has reached GitLab yet ───
13. push_extension_repo        — git push (first GitLab side effect)
14. push_deployment_repo       — git push deployment repo (incl. tests/)
15. push_images_to_registry    — docker push to GitLab Container Registry
16. produce_build_report       — versioned report file on disk
```

**Build-locally-first** means a failure at any Activity 1–11 leaves zero side effects on GitLab — no broken commits land, no images get pushed. The implementer iterates locally without polluting the deployment repo. Activities 12–14 only run when everything below the line is green.

**Image naming:** `<org-mnemonic>-<registry-mnemonic>-<service>:develop`. The Helm wrapper chart follows the same: `<org-mnemonic>-<registry-mnemonic>-registry`. Both come from Discovery items captured upfront.

**Tools used by the Phase 2 LLM:**

The codegen call uses tool calling (`submit_files` with a single `files: [{path, content}]` argument). Tool calls are uniformly supported across providers — robust to per-provider strictness rules on `response_format`. Streaming is enabled so the panel shows live token progress.

**Default model:** Anthropic Sonnet (codegen is the place to spend money for fewer iterations on broken code).

**Per-Register batching.** Activity 4 (`generate_extension_files`) issues one LLM `submit_files` tool call per Register, not one combined call. A single call generating files for 7+ Registers exhausts even Sonnet's output budget (~30K+ output tokens) and the stream finishes with empty arguments. Per-Register calls keep each request to ~3 files × 100-200 lines = comfortably under 8K output tokens. The cross-Register barrel files (`models/__init__.py`, `schemas/__init__.py`, `services/__init__.py`, `factory/__init__.py`) are produced deterministically by the orchestrator from the full Register list — the LLM never sees the full set, so it couldn't write correct barrels anyway.

### Phase 2 chat stages

The Phase 2 chat is stage-aware — its behaviour shifts based on `working_case` + the build job's status + `current_phase`:

| Stage | When | What the chat does |
|---|---|---|
| **A — Input collection** | Required Phase 2 Discovery items missing | Walks the items in batches; records via `record_discovery_answer` |
| **B — Build in flight (or not started)** | All required items captured; build_job is none / running / failed | Acknowledges build state; helps diagnose failures (no file edits in v0.x) |
| **C — Build succeeded — sign-off** | build_job.status = succeeded | Synthesises the Build Report from artefacts; runs the revisions loop; on approval calls `save_phase_report` + `phase_complete` |
| **D — Already approved** | current_phase > 2 | Refuses to do further work; declines to walk Phase 3-5 (those aren't implemented). Lets the user revisit/correct Phase 2 inputs without re-issuing sign-off prompts. |

### UI layout

Phase 2's view is a split layout: a **chat panel** on the left (collects build inputs through guided conversation, helps diagnose failures) and a **Build Activity Panel** on the right (terminal-style live log of the orchestrator).

The **Start build** button is disabled until every required Phase 2 Discovery item is recorded in the project's `working_case`. The chat-side LLM walks the implementer through them; the panel polls every 5 seconds and the button enables automatically as soon as the last item lands. Hovering the disabled button shows the missing-inputs list.

### Build Activity Panel

The right-side panel is a terminal-style log of every event the orchestrator emits:

```
▸ → collect_build_inputs
· Phase 2 inputs validated.
✓ collect_build_inputs
▸ → prepare_gitlab_workspace
· Subgroup ready: openg2p/g2p-advisor/<handle>
· Projects ready: ...
✓ prepare_gitlab_workspace
...
```

Reconnect after a network blip is automatic — the panel remembers the last seen event id. Events are append-only and id-monotonic so replay is safe.

A **Stop** button is available while the build is running. It marks the job aborted in the DB; the next step doesn't start (the current step finishes naturally — e.g. an in-progress git clone or LLM call won't be killed mid-stream).

## Phases 3–5

* **Phase 3: Sandbox** — guidance for deploying the customised registry to a development cluster.
* **Phase 4: Pilot** — guidance for limited-rollout testing with real users.
* **Phase 5: Full Rollout** — guidance for production cutover, including brownfield migration from existing systems.

These are about the *implementer's* environments, not the advisor's local sandbox. The Advisor's role becomes guidance + checklists rather than direct execution. Designed but not built in v0.x.

The phase strip in the UI marks Phases 3-5 as `(coming soon)` and keeps them un-clickable even if a project's `current_phase` has advanced past 2 — so accidentally calling `phase_complete({phase: 2})` doesn't expose un-implemented walkthroughs to the user.
