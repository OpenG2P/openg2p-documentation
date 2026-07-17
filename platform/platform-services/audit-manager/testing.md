---
description: >-
  Test plan for the Audit Manager — unit tests (pydantic schema), end-to-end
  smoke test against docker compose, concurrent load test, and the Postman
  collection.
---

# Testing

Three layers, each proving a different thing. Full details in
[`tests/README.md`](https://gitlab.com/openg2p/audit-manager/-/blob/develop/tests/README.md).

## 1. Unit tests — schema validation (no infra needed)

Sub-second, pure pydantic. Validates every sample event, enforces required
fields, covers enum constraints and the Postgres column mapping.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e ".[test]"
pytest tests/unit/ -v                # 30 tests
```

## 2. Smoke test — end-to-end against `docker compose`

Posts every sample event shape, posts the batch, triggers an expected
4xx, waits for Kafka → Postgres settle, then queries Postgres to verify
every expected id landed. Also verifies idempotency (repost = no
duplicate row).

```bash
docker compose up --build -d
tests/smoke.sh
```

Overrides: `AUDIT_URL`, `SETTLE_SECONDS`, `COMPOSE_PG_SERVICE`.

## 3. Load test — concurrent POSTs, no-drop verification

Sends N unique events with C concurrent workers, then confirms all N are
in Postgres.

```bash
N=1000 C=20 tests/load.sh
```

## Postman collection

Import [`tests/postman/OpenG2P-Audit-Manager.postman_collection.json`](https://gitlab.com/openg2p/audit-manager/-/blob/develop/tests/postman/OpenG2P-Audit-Manager.postman_collection.json)
into Postman, Bruno, or Insomnia. Folders:

* Service endpoints (`/v1/auditmanager/health`, `/v1/auditmanager/version`,
  `/v1/auditmanager/config`, `/v1/auditmanager/docs`)
* Single events — success paths (login, views, updates, payment approve/reverse)
* Single events — failure / denied outcomes
* Batch ingestion
* Negative tests with assertions

Each request ships with test-script assertions (`202 Accepted`, expected
ids, 4xx on invalid). Use the **Runner** to fire the whole collection.

## Sample events

Nine JSON fixtures under [`tests/sample-events/`](https://gitlab.com/openg2p/audit-manager/-/tree/develop/tests/sample-events)
cover every realistic OpenG2P audit shape — reusable as `curl -d @file.json`:

```bash
curl -sX POST http://localhost:8000/v1/auditmanager/events \
  -H 'content-type: application/json' \
  --data-binary @tests/sample-events/04-beneficiary-updated.json
```
