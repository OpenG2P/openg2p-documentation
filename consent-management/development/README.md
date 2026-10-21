---
description: >-
  Developing the Consent Manager: technology stack, repository layout, local
  setup, tests and configuration.
---

# Development

{% hint style="info" %}
**Source repository:**
[https://github.com/OpenG2P/consent-manager](https://github.com/OpenG2P/consent-manager).
Clone, raise issues, and open pull requests there.
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

The [`consent-manager`](https://github.com/OpenG2P/consent-manager) repository holds the service
(`backend/`), the staff console (`ui/`), the partner portal (`partner-portal/`), the Helm chart and
scripts (`deployment/`), Dockerfiles (`docker/`) and the in-cluster sanity suite (`test/sanity/`).

```
backend/src/openg2p_consent_manager/
  config.py            Settings (env prefix CONSENT_MANAGER_)
  db.py                Shared async session factory
  auth.py              Keycloak bearer auth (staff and partner realms)
  models/              SQLAlchemy models (consent, audit, exchange); no partner tables
  schemas/             Pydantic request/response models
  services/            verification · policy · partner + pm_policy_client (Partner Management) ·
                       crypto · receipt · consent · lifecycle · exchange · assisted · evidence ·
                       subject_auth · consent_record · master_data_client · composite_client
  controllers/         verification · well-known · decisions · consent verification ·
                       partner portal · lifecycle · subject
  utils/               canonical JSON, JWKS, caches
  app.py               Initializer (wires services and controllers per API audience, runs migrations)
  main.py              ASGI entrypoint (gunicorn/uvicorn)
  expire.py            Standalone expiry runner (for the CronJob)
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

For local dev without Keycloak, set `CONSENT_MANAGER_AUTH_ENABLED=false` (staff tokens are then
accepted unverified and role checks pass; partner-portal tokens are always verified). With no signing key configured, an ephemeral key is
generated — fine for dev, but receipts will not verify across restarts.

The whole stack (Postgres + service) also runs via Docker Compose from the repo root:

```bash
docker compose up --build
```

FastAPI serves an interactive OpenAPI/Swagger UI at `/docs` once running.

## Tests

`backend/tests/` runs the services, controllers and the migration against a real Postgres. It
**wipes the database it is given**, and is skipped if the database cannot be reached:

```bash
cd backend
pip install -e '.[test]'
CM_TEST_DB_DATASOURCE=postgresql+asyncpg://postgres@localhost:5432/cm_test pytest tests
```

## Configuration

All settings use the `CONSENT_MANAGER_` env prefix; see `backend/.env.example` for the full
list (database, `.p12` signing key, Keycloak auth, replay window, Partner Management URL and the
partner key and policy caches). Without a Partner Management URL every `/validate` fails closed; tests
stand in for PM with an in-memory fake. Chart values for each setting: [Deployment](../deployment/README.md).

## Background expiry

Expiry is not an in-process scheduler, so API pods stay stateless. It is a standalone command, run
by the chart's CronJob: `python -m openg2p_consent_manager.expire`.
