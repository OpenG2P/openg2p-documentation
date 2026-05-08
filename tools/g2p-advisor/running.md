# Running

## Prerequisites

* **Node.js 20+**
* **Postgres** (for local dev: a docker-compose file ships with the repo at `docker/docker-compose.yml`)
* **A clone of `g2p-wiki`** at `../g2p-wiki` relative to the advisor repo (or set `WIKI_PATH`). The wiki must have been ingested at least once so the playbooks are available under `raw/gitbook/`.
* **At least one LLM provider's API key:** OpenAI, Anthropic, Gemini, or Groq.

For Phase 2 builds you additionally need:

* **Docker** daemon running (for local image builds + sandbox)
* **Python 3** on PATH (for `python -m py_compile` in the compile step)
* **Helm** on PATH (optional but recommended — without it, `helm lint` is skipped with a warning)
* **A GitLab personal access token** with `api`, `read_repository`, `write_repository`, `read_registry` scopes, and Owner role on `gitlab.com/openg2p/g2p-advisor`

## First-time setup

```bash
git clone https://github.com/openg2p/g2p-advisor.git
cd g2p-advisor

cp .env.example .env
# edit .env — see "Environment variables" below

npm install
npm run db:up           # starts Postgres in Docker
npm run migrate         # applies migrations
```

## Environment variables

Minimum to run:

```env
DATABASE_URL=postgres://g2p:g2p@localhost:5432/g2p_advisor

# At least one provider key
ANTHROPIC_API_KEY=sk-ant-...        # recommended
# OPENAI_API_KEY=sk-...
# GEMINI_API_KEY=...
# GROQ_API_KEY=gsk_...

# Per-mode provider/model selection (defaults: openai gpt-4o-mini)
CHAT_PROVIDER=anthropic    CHAT_MODEL=claude-haiku-4-5-20251001
PROJECT_PROVIDER=anthropic PROJECT_MODEL=claude-haiku-4-5-20251001
BUILD_PROVIDER=anthropic   BUILD_MODEL=claude-sonnet-4-6

# Wiki location
WIKI_PATH=../g2p-wiki

# Mock auth (until Keycloak lands)
MOCK_USER_ID=mock-user-001
MOCK_USER_EMAIL=you@example.org
MOCK_USER_NAME=You
```

Phase 2 build orchestration adds:

```env
GITLAB_TOKEN=glpat-...
# GITLAB_API_URL=https://gitlab.com/api/v4
# GITLAB_PARENT_GROUP=openg2p/g2p-advisor
# GITLAB_REGISTRY_HOST=registry.gitlab.com

# Per-project workspace root on the advisor host. Default: <repo>/workspace/.
# WORKSPACE_PATH=/var/lib/g2p-advisor/workspace
# (On macOS dev: leave unset, or set to a writable path under your home dir.)

# Reference repo pin. Default: develop.
# FARMER_REGISTRY_REF=develop
```

## Running

```bash
npm run dev
```

Open <http://localhost:3000>.

You'll land on `/projects` (Project mode by default). Toggle to Chat mode via the top-right control.

## Tier / rate-limit notes

Anthropic Tier 1 has a ~50K TPM ceiling for Sonnet. Phase 2's codegen call alone is ~10–30K input tokens; combined with the chat-prompt boilerplate, a single turn can push 50K. If you hit a 429 on Phase 2, either:

* Wait a few seconds — the rate limit resets per minute.
* Switch `BUILD_PROVIDER` to `openai` (gpt-4o) temporarily.
* Upgrade your Anthropic account tier.

Gemini's free tier is generous for chat traffic but tool-call reliability is uneven on complex prompts. Anthropic Haiku is the most reliable cheap option for the conversational paths.
