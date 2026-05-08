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

## Phase 2: Build

Code generation, build, sandbox, handover. Single linear, abort-on-error job per project.

The orchestrator walks 13 steps in order:

1. **collect_build_inputs** — validate working_case has every required Phase 2 Discovery item.
2. **prepare_gitlab_workspace** — create per-implementer subgroup, two private projects (`<mnemonic>-extension`, `<mnemonic>-deployment`), allowlist the deployment project's `CI_JOB_TOKEN` to read the extension project, invite the implementer as Developer.
3. **clone_reference_registry** — fresh clone of [farmer-registry](https://github.com/openg2p/farmer-registry) as the substitution surface.
4. **generate_extension_repo** — LLM-driven codegen of per-Register Python files (models, schemas, services, factory, ORM definitions, ID generator) plus deterministic regeneration of `app.py`, sample-data SQL, register definitions.
5. **compile_extension** — `python -m py_compile` over every `.py`. Catches syntax errors in seconds.
6. **push_extension_repo** — `git init` + force-push to GitLab.
7. **generate_deployment_repo** — deterministic templates for Helm chart, Dockerfile substitution, sandbox compose file.
8. **compile_deployment** — `helm lint` + `yaml.safe_load` over every YAML file.
9. **build_and_push_images** — `docker login` to GitLab Container Registry, `docker build` each service via the upstream `build.sh` (handles `parse_service.py` + dependency staging), `docker push` to the project's Container Registry.
10. **push_deployment_repo** — `git init` + force-push deployment repo (after images live so the compose file references valid images).
11. **generate_test_suite** *(planned)* — Python pytest + httpx (API) + pytest-playwright (UI), parameterised by `register_mnemonics`.
12. **deploy_local_sandbox** *(planned)* — docker-compose up of the customised stack on the advisor host.
13. **run_smoke_tests** *(planned)* — execute generated tests against the running sandbox.

**Image naming:** `<org-mnemonic>-<registry-mnemonic>-<service>:develop`. The Helm wrapper chart follows the same: `<org-mnemonic>-<registry-mnemonic>-registry`. Both come from Discovery items captured upfront.

**Tools used by the Phase 2 LLM:**

The codegen call uses tool calling (`submit_files` with a single `files: [{path, content}]` argument). Tool calls are uniformly supported across providers — robust to per-provider strictness rules on `response_format`. Streaming is enabled so the panel shows live token progress.

**Default model:** Anthropic Sonnet (codegen is the place to spend money for fewer iterations on broken code).

### Build Activity Panel

Phase 2's UI is a terminal-style log of every event the orchestrator emits:

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
