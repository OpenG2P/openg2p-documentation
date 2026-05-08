# Concept

## The problem

Implementers adopting OpenG2P need accurate, current answers about a fast-moving stack — and then need to actually *build* a customised registry from scratch. The traditional path is: read documentation, ask on Slack, copy-paste from reference repos, hand-edit configs, debug for weeks. The Advisor compresses that into a guided conversation that produces a working registry.

## Key design decisions

### 1. Wiki-grounded, not hallucinated

Every answer the Advisor gives is anchored to a specific page in [G2P WikiLLM](../g2p-wikillm/README.md). The wiki is built once from authoritative sources (this Gitbook, the GitHub repos under `github.com/openg2p`, the project website). The Advisor reads from the wiki at runtime via a typed file-system client; it never queries upstream sources directly.

**Why:** vector-retrieval RAG systems hallucinate because they search loose chunks of text without a stable structure. Reading from a curated graph means every claim is traceable.

### 2. Playbook-driven, minimal hardcoding

Every phase's Discovery items, Activities, gap checks, and report shape are defined in the [Registry implementation playbook](../../products/registry/registry/use-case-implementation.md). The Advisor reads the playbook at runtime and walks through it; the orchestrator code is mostly a state machine that loops over the playbook's structure.

When the playbook is updated (new Discovery item, renamed Activity, new phase), the Advisor adapts automatically without a code change.

**Why:** keeps domain expertise in Gitbook (where domain experts edit it) and engineering in the codebase. No drift between "what the docs say to do" and "what the Advisor does."

### 3. Kickstart-then-handover (not continuous integration)

In Phase 2 the Advisor generates code into its own per-project workspace, pushes to the implementer's GitLab namespace, builds Docker images locally, and runs a sandbox. When the implementer is satisfied, they take ownership: the GitLab repos, the images, the chart — all live in their account. The Advisor's job is done.

**Why:** the Advisor doesn't want long-running integration with the implementer's CI/CD; that would couple delivery to operations. Kickstart-then-handover gives a clean baseline and steps out of the way.

### 4. Build locally, push to GitLab Container Registry

Phase 2 generates files locally, runs `python -m py_compile` + `helm lint` + `yaml.safe_load` for fast feedback, runs `docker build` on the advisor host, and pushes the resulting images to GitLab Container Registry. The deployment repo's `.gitlab-ci.yml` is intentionally a no-op — CI doesn't rebuild what we've already built.

**Why:** GitLab CI on shared runners is slow (10-15 min per build) and burns CI minutes. Local build catches errors in seconds and reuses the same image for the local sandbox.

### 5. Per-mode LLM provider/model factory

Different phases of work want different models. Chat mode is mostly retrieval and works on cheap-fast models (Gemini Flash, Haiku). Project mode's Phase 1 is conversational + tool-calling, also fine on Haiku. Phase 2 codegen produces real Python/Helm/Dockerfiles and wants a stronger model (Sonnet by default). All three are independently configurable via environment variables.

**Why:** matching cost/latency to the work means iteration stays fast and cheap.

## Memory architecture

Four distinct layers, each with a clear purpose:

| Layer | Where | Purpose |
|---|---|---|
| **Working case** | Postgres JSONB on `projects` | Structured facts the implementer has provided, keyed by Discovery item IDs from the playbook (e.g. `country`, `registry_mnemonic`, `register_columns`). Lives indefinitely. |
| **Conversation history** | Postgres `messages` table | Full chat log per session. The LLM sees recent N + auto-summary of older. |
| **Phase artefacts** | Files on disk + Postgres index | Reports (Phase 1, Phase 2), generated code repos, Docker images, Helm output. |
| **Wiki context** | Read-only from `g2p-wiki/` filesystem | Playbooks, entity pages, source pages, lessons. External; the Advisor reads, never writes. |

The working case schema follows the playbook's Discovery item IDs. Add an item in the playbook → the Advisor captures it without code changes.

## What's not the Advisor's job

* **It is not a deployment tool.** Phase 2 produces images and a Helm chart; deploying to a real Kubernetes cluster is up to the implementer.
* **It is not a long-term operations tool.** Once handover happens the Advisor steps out. Sandbox is for "did the build work?" verification, not for running production traffic.
* **It is not a pretrained chatbot.** Without the wiki, the Advisor has no domain knowledge. Everything it says is grounded in pages that humans (or the WikiLLM ingest pipeline) curated.
