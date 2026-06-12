---
description: >-
  Step-by-step guide to run openg2p-registry-staff-portal-api on a local
  developer machine. Includes every fix needed beyond the upstream README,
  with macOS / Apple Silicon notes called out explicitly.
---

# Local Install — Staff Portal API

## Why this guide exists

The upstream `openg2p-registry-staff-portal-api` repo has a one-line
README. Getting it running locally requires a chain of repos installed in
the right order, two Postgres extensions enabled, two cluster services
port-forwarded, and a couple of macOS-specific quirks worked around. This
page captures the full path so you don't have to rediscover any of it.

By the end you will have:

* The Staff Portal API running on `http://localhost:8001`
* `/ping` returning `pong`
* Swagger UI at `http://localhost:8001/docs`
* Cluster Keycloak and IAM port-forwarded to your laptop
* A local Postgres holding `registry_db` + `openg2p_gen2_master_data_db`

You will **not** install MinIO. The document/template endpoints that need
it are out of scope for the audit integration smoke test.

---

## Prerequisites

| Tool | Notes |
| --- | --- |
| Python 3.11 | Tested on 3.11.9 (Homebrew on Apple Silicon). 3.12 may work but isn't tested here. |
| Docker | For the local Postgres container only. |
| `kubectl` configured against the cluster running OpenG2P | Used for port-forwarding Keycloak + IAM. |
| Read access to Keycloak admin in the cluster | Needed to fetch the client secret and confirm a test user. |

Decisions to confirm before you start (you'll need them in Phase 4):

* Cluster namespace and Service name of Keycloak (often `commons-keycloak`)
* Cluster namespace and Service name of the IAM service (the
  `auth_provider_api_url` — exposes `/user-access/get_permissions_for_roles`)
* Keycloak realm name + client_id used by the staff portal
* A test user (and password) with at least one role on that client

---

## Phase 1 — Python venv + install local repo chain

The order matters because the dependency graph is bottom-up.

```bash
mkdir -p ~/sp-local && cd ~/sp-local
python3.11 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
```

Set a path variable to keep the install commands short:

```bash
REPOS=/Users/<you>/Documents/OpenG2P/repos
```

Install in this exact order:

```bash
pip install -e $REPOS/openg2p-fastapi-common/openg2p-fastapi-common
pip install -e $REPOS/openg2p-fastapi-common/openg2p-fastapi-auth
pip install -e $REPOS/iam-service/iam-core
pip install -e $REPOS/openg2p-registry-gen2-core/openg2p-registry-core

# IMPORTANT: farmer-extension is installed NON-editable (no -e). See note below.
pip install $REPOS/openg2p-registry-gen2-extensions/openg2p-registry-farmer-extension

pip install -e $REPOS/openg2p-registry-gen2-apis/openg2p-registry-staff-portal-api
```

Server runtime + missing transitive dep:

```bash
pip install gunicorn 'uvicorn[standard]' greenlet
```

### Why farmer-extension is installed without `-e`

The farmer extension's `pyproject.toml` uses a hatchling
**source-rename trick** so any concrete extension (farmer / family / NSR)
exposes itself under the **generic name** `openg2p_registry_extensions`:

```toml
[tool.hatch.build.targets.wheel.sources]
"src/openg2p_registry_farmer_extension" = "openg2p_registry_extensions"
```

This rename only kicks in for **wheel builds**, not for `pip install -e`
(editable mode keeps the original directory name). If you install
editable, you'll get `ModuleNotFoundError: No module named
'openg2p_registry_extensions'` on `migrate`. Plain `pip install <path>`
builds the wheel and applies the rename correctly.

If you ever need to edit the farmer extension code, re-run
`pip install <path>` from that directory after each change.

### macOS / Apple Silicon notes

* **`zsh: no matches found: uvicorn[standard]`** — zsh treats `[...]` as
  a glob. Single-quote the spec: `pip install 'uvicorn[standard]'`. Or
  permanently fix in `~/.zshrc`:
  ```bash
  alias pip='noglob pip'
  ```
* **`greenlet` missing** — pip on Apple Silicon + Python 3.11 sometimes
  doesn't pull `greenlet` in transitively from SQLAlchemy's async extra.
  Listed above explicitly so you don't have to discover this via the
  migrate stack trace.

---

## Phase 2 — local Postgres for the two registry databases

```bash
docker run -d --name pg-staff \
  -p 5432:5432 \
  -e POSTGRES_PASSWORD=password \
  postgres:16

# Create both databases the service expects
docker exec pg-staff psql -U postgres -c "CREATE DATABASE registry_db;"
docker exec pg-staff psql -U postgres -c "CREATE DATABASE openg2p_gen2_master_data_db;"
```

### Required Postgres extensions

The migration creates a trigram-based GIN index on intake form sections;
that needs `pg_trgm`. Enable it (and a couple of others the registry uses
in places) **before** running migrate:

```bash
docker exec pg-staff psql -U postgres -d registry_db -c "
  CREATE EXTENSION IF NOT EXISTS pg_trgm;
  CREATE EXTENSION IF NOT EXISTS unaccent;
  CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";
"
```

(Skipping this step gets you the error: `operator class "gin_trgm_ops"
does not exist for access method "gin"`.)

The `master_data_db` can stay empty for now — it's seeded by a separate
service (`master-data-service`) that we don't need for the audit smoke
test. Calls that touch it will fail gracefully; other endpoints work.

---

## Phase 3 — port-forward cluster services

Find the actual service names first:

```bash
kubectl get svc -A | grep -iE 'keycloak|iam'
```

Then keep two terminals running:

```bash
# Terminal A — Keycloak (token issuer)
kubectl -n <keycloak-ns> port-forward svc/<keycloak-svc> 8080:80

# Terminal B — IAM service (auth_provider, returns role permissions)
kubectl -n <iam-ns> port-forward svc/<iam-svc> 9090:80
```

Verify both are responding:

```bash
# Keycloak — should return JSON with the realm's OIDC config
curl -sf http://localhost:8080/realms/<realm>/.well-known/openid-configuration | head

# IAM — root path returns 404 (only specific paths exist).
# That's NORMAL. Hit a real endpoint to confirm the service is alive:
curl -i -X POST http://localhost:9090/user-access/get_permissions_for_roles \
  -H 'content-type: application/json' \
  -d '{"role_mnemonics":[]}'
# Any HTTP response (200/400/401) means the forward is alive.
# Connection refused = forward is down.
```

---

## Phase 4 — `.env` configuration

```bash
cp $REPOS/openg2p-registry-gen2-apis/openg2p-registry-staff-portal-api/.env.example .env
```

Edit `.env`:

```bash
# Registry DB (local Postgres in Docker)
REGISTRY_STAFF_PORTAL_API_DB_USERNAME=postgres
REGISTRY_STAFF_PORTAL_API_DB_PASSWORD=password
REGISTRY_STAFF_PORTAL_API_DB_HOSTNAME=localhost
REGISTRY_STAFF_PORTAL_API_DB_PORT=5432
REGISTRY_STAFF_PORTAL_API_DB_DBNAME=registry_db

# Master-Data DB (also local Postgres, separate database name)
REGISTRY_STAFF_PORTAL_API_MASTER_DATA_DB_DRIVER=postgresql+asyncpg
REGISTRY_STAFF_PORTAL_API_MASTER_DATA_DB_USERNAME=postgres
REGISTRY_STAFF_PORTAL_API_MASTER_DATA_DB_PASSWORD=password
REGISTRY_STAFF_PORTAL_API_MASTER_DATA_DB_HOSTNAME=localhost
REGISTRY_STAFF_PORTAL_API_MASTER_DATA_DB_PORT=5432
REGISTRY_STAFF_PORTAL_API_MASTER_DATA_DB_DBNAME=openg2p_gen2_master_data_db

# IAM (cluster Keycloak + IAM, both port-forwarded)
REGISTRY_STAFF_PORTAL_API_AUTH_PROVIDER_API_URL=http://localhost:9090
REGISTRY_STAFF_PORTAL_API_KEYCLOAK_CLIENT_ID=<actual-client-id>

# Common
COMMON_OAUTH_OPENID_CONFIG_URL=http://localhost:8080/realms/<realm>/.well-known/openid-configuration
COMMON_AUTH_PROVIDER_API_URL=http://localhost:9090

# MinIO — placeholders (we won't hit document endpoints)
REGISTRY_STAFF_PORTAL_API_MINIO_ENDPOINT=localhost:9000
REGISTRY_STAFF_PORTAL_API_MINIO_ACCESS_KEY=admin
REGISTRY_STAFF_PORTAL_API_MINIO_SECRET_KEY=secret
REGISTRY_STAFF_PORTAL_API_MINIO_BUCKET_NAME=default_bucket
REGISTRY_STAFF_PORTAL_API_MINIO_SECURE=false

# App
COMMON_APP_HOST=0.0.0.0
COMMON_APP_PORT=8001
COMMON_LOGGING_LEVEL=DEBUG
```

Two values you must fill in:

* `<actual-client-id>` — Keycloak admin → Clients → your client → Settings
* `<realm>` — visible at the top-left of the Keycloak admin UI

> **Note:** `client_secret` is **not** needed in `.env`. Staff Portal API
> is a resource server — it only validates incoming JWTs against the
> realm's public keys (via the OIDC discovery URL). The secret is only
> needed in Phase 6 to *fetch* a token, and even then only if the client
> is configured as confidential.

### macOS / zsh note — loading the .env

You don't need to export the variables manually. Pydantic-settings reads
`.env` from the current working directory automatically (configured in
`config.py`). Just `cd ~/sp-local` before running and it picks them up.

If you do want them in your shell, **don't** use:

```bash
# BROKEN: chokes on values containing & = ! # etc.
export $(grep -v '^#' .env | xargs)
```

Use the `set -a` auto-export pattern instead:

```bash
set -a
source .env
set +a
env | grep ^REGISTRY_STAFF_PORTAL_API_   # sanity check
```

---

## Phase 5 — migrate + run

```bash
cd ~/sp-local
source .venv/bin/activate

python -m openg2p_registry_staff_portal_api.main migrate
```

Migration output is verbose JSON-formatted log lines. The "Worker ID
-1. Docker Pod ID" lines repeated many times are normal startup
chatter from the controller `post_init()` chain — not errors. Wait for
the process to exit cleanly. If it errors with the `gin_trgm_ops`
message, you skipped the extension step in Phase 2.

Start the server:

```bash
uvicorn openg2p_registry_staff_portal_api.main:app \
  --host 0.0.0.0 --port 8001 --reload
```

Wait for:

```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
```

---

## Phase 6 — verification

In another terminal:

```bash
# Health probe — expect "pong"
curl -i http://localhost:8001/ping

# Swagger UI — open in browser
open http://localhost:8001/docs
```

Both should work. At this point the service is up and you're ready to:

* Fetch a Keycloak token (next step — see your runbook)
* Add the AuditMiddleware (covered in upcoming sub-pages)

---

## Common failures and fixes

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'openg2p_registry_extensions'` | Farmer extension installed editable | `pip uninstall -y openg2p-registry-farmer-extension && pip install <path>` (no `-e`) |
| `ValueError: the greenlet library is required to use this function. No module named 'greenlet'` | Missing transitive dep | `pip install greenlet` |
| `operator class "gin_trgm_ops" does not exist for access method "gin"` | `pg_trgm` extension not enabled | `CREATE EXTENSION pg_trgm` on `registry_db` |
| `zsh: no matches found: uvicorn[standard]` | zsh glob expansion | Quote: `pip install 'uvicorn[standard]'` |
| `export: not valid in this context: &` | `xargs` choking on `&` in env values | Use `set -a; source .env; set +a` instead |
| `curl http://localhost:9090/` returns 404 | IAM has no root route | Normal — hit a real endpoint to verify the forward |
| Server boots but `/ping` hangs / 500 | Postgres container stopped, or port-forward died | `docker ps` and check the two `kubectl port-forward` terminals are still alive |

---

## What we deliberately did NOT install

| Component | Why skipped |
| --- | --- |
| MinIO | Only needed for document/template upload endpoints, which are out of scope for the audit smoke test. The MinIO env vars in `.env` are placeholders — settings load fine, the controllers only fail if a document endpoint is actually called. |
| `master-data-service` | Provides the seed data for `openg2p_gen2_master_data_db`. Endpoints that depend on it will fail; everything else (register-data, change-requests, registry-config, …) works without it. |
| Keycloak (locally) | We use the cluster's via port-forward — tokens issued by cluster Keycloak must be validated against the same realm keys. Running a separate local Keycloak would require recreating the realm/client/user setup. |
| IAM service (locally) | Same reason — cluster's IAM holds the role-to-permission mappings. |
