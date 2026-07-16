---
description: >-
  Developing the Consent Manager service — technology stack, repository layout,
  and local setup.
---

# Development

{% hint style="info" %}
**Source repository:** the Consent Manager is developed on **GitLab** —
[https://gitlab.com/openg2p/consent-manager](https://gitlab.com/openg2p/consent-manager).
The former GitHub repository (`github.com/openg2p/consent-manager`) is **frozen and
read-only**; its CI is disabled. Clone, raise issues, and open merge requests on GitLab.
{% endhint %}

The Consent Manager is a FastAPI service built on
[`openg2p-fastapi-common`](https://github.com/OpenG2P/openg2p-fastapi-common), backed by
**PostgreSQL** (async SQLAlchemy). It is the Policy Decision Point (PDP) described in the
[design](../design/README.md); this section covers building and running it.

## Technology stack

| Concern | Choice |
| --- | --- |
| Framework | `openg2p-fastapi-common` (`BaseService` / `BaseController` / `Initializer`) |
| Language | Python ≥ 3.10 |
| Database | PostgreSQL via async SQLAlchemy (`asyncpg`) |
| Migrations | `create_migrate()` per model (no Alembic) |
| Crypto | `cryptography` (Ed25519 / ES256 / RS256) + canonical-JSON signing |
| Auth | Keycloak bearer tokens, validated via JWKS (PyJWT) |
| Serving | gunicorn + uvicorn workers |

## Repository layout

The service lives under `backend/` in the [`consent-manager`](https://gitlab.com/openg2p/consent-manager) repository (GitLab):

```
backend/src/openg2p_consent_manager/
  config.py            Settings (env prefix CONSENT_MANAGER_)
  db.py                Shared async session factory
  auth.py              Keycloak bearer auth — CallerIdentity, require_role
  models/              SQLAlchemy models (partner, consent, audit)
  schemas/             Pydantic request/response models
  services/            crypto · partner · policy · receipt · verification · consent · lifecycle
  controllers/         verification · well-known · partner · lifecycle · subject
  app.py               Initializer (wires services + controllers, runs migrations)
  main.py              ASGI entrypoint (gunicorn/uvicorn)
  expire.py            Standalone expiry runner (for a CronJob)
```

The HTTP surface is documented in the [API Reference](../api/README.md).

## Local setup

```bash
cd backend
cp .env.example .env          # adjust DB, signing key, and auth settings
pip install -e .              # pulls openg2p-fastapi-common + deps
python -m openg2p_consent_manager.main migrate   # create tables
uvicorn openg2p_consent_manager.main:app --reload
```

For local dev without Keycloak, set `CONSENT_MANAGER_AUTH_ENABLED=false` (tokens are then
accepted unverified and role checks pass). With no signing key configured, an ephemeral key is
generated — fine for dev, but receipts will not verify across restarts.

The whole stack (Postgres + service) also runs via Docker Compose from the repo root:

```bash
docker compose up --build
```

FastAPI serves an interactive OpenAPI/Swagger UI at `/docs` once running.

## Configuration

All settings use the `CONSENT_MANAGER_` env prefix; see `backend/.env.example` for the full
list (database, controller id, `.p12` signing key, Keycloak auth, replay window, cache TTL). Key
operational settings are summarised in [Deployment](../deployment/README.md).

## Background expiry

Consent expiry is **not** an in-process scheduler (so API pods stay stateless). It runs as a
standalone command, intended for a Kubernetes CronJob:

```bash
python -m openg2p_consent_manager.expire
```

The validation hot path also lazily expires artefacts on read, so an expired consent is never
treated as active even between CronJob ticks.
