---
description: >-
  Test plan for the Approval Workflow Engine — hermetic pytest smoke tests
  against in-memory SQLite, what they cover, and how to run against real
  Postgres.
---

# Testing

All tests are **hermetic** — no Docker, no Postgres, no Keycloak, no
network. The test suite drops the SQLAlchemy schema onto an in-memory
SQLite database via `aiosqlite`, points dev-mode auth at empty issuer
(unsigned JWTs accepted), and exercises the full FastAPI app over an
in-process ASGI transport. The whole suite runs in about a second.

Full test docs:
[`tests/README.md`](https://github.com/OpenG2P/awe/blob/develop/tests/README.md).

## Run

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e '.[test]'
pytest -v
```

## What's covered

### `test_health.py` — service endpoints

Verifies `/v1/awe/health`, `/v1/awe/version`, `/v1/awe/config` return
the documented envelopes and that `/config` does **not** leak Keycloak
secrets.

### `test_policies.py` — policy CRUD + lifecycle

* Create a draft, list, list versions, fetch version detail.
* Activate a draft → status flips to `active`.
* Simulate: resolves approvers for a sample context, returns the same
  stages the policy declares.
* AuthZ: unauthenticated calls get 401; non-admin tokens get 403.
* Edit: draft versions can be edited in place (`PATCH`); active and
  archived versions return `409 AWE-007`.

### `test_requests_and_tasks.py` — end-to-end approval lifecycle

* **Two-stage happy path**: create policy → create request → alice
  approves stage 1 (`any-1`) → bob's task flips to `skipped` → director
  approves stage 2 (`all` with 1 approver) → request transitions to
  `approved`. Verifies event timeline contains `request_created`,
  `stage_started`, `stage_completed`, `request_approved`.
* **Reject path**: both approvers reject a single stage → request ends
  `rejected`.
* **Cancel**: admin cancels an in-flight request; outstanding tasks
  flip to `skipped`.
* **Idempotency**: retrying `POST /requests` with the same
  `Idempotency-Key` returns the same `request_id` without creating a
  second request row.
* **Search**: filter by `artifact_type` / `artifact_id`.

### `test_webhook_signing.py` — HMAC signing contract

* Signature equals `"sha256=" + HMAC_SHA256(secret, timestamp + "." + body)`.
* Two signatures with different timestamps differ for the same body —
  proves replay-safety.

## Sample payloads

Sample policy payload used across tests:

```json
{
  "policy_key": "registry.cr.v1",
  "name": "Registry CR approval",
  "artifact_type": "registry.change_request",
  "stages": [
    {
      "name": "District officers",
      "stage_order": 1,
      "mode": "any-n",
      "mode_value": 1,
      "rules": [
        {"rule_type": "user", "rule_value": {"user_id": "u-officer-A"}},
        {"rule_type": "user", "rule_value": {"user_id": "u-officer-B"}}
      ]
    },
    {
      "name": "State directors",
      "stage_order": 2,
      "mode": "all",
      "rules": [
        {"rule_type": "user", "rule_value": {"user_id": "u-director-X"}},
        {"rule_type": "user", "rule_value": {"user_id": "u-director-Y"}}
      ]
    }
  ]
}
```

Re-usable as `curl -d @policy.json` against a running dev-mode instance.

## Running against real Postgres (optional)

The production code path uses async Postgres via `asyncpg`. To exercise
it locally:

```bash
docker compose up postgres -d
DATABASE_URL='postgresql+asyncpg://postgres:postgres@localhost:5432/awe' \
  pytest -v
```

The schema is ensured at startup via `Base.metadata.create_all`, so no
migrations needed. This catches Postgres-specific oddities (SKIP
LOCKED, JSONB coercion) that SQLite happily accepts.

## Testing webhook delivery

The dispatcher and SLA monitor loops run as `asyncio.Task`s during
lifespan. In the smoke tests they're started but never tick (they
sleep on their poll interval). To exercise delivery specifically:

```python
# point callback_url at a local capture, e.g. via `nc -l 9999` or a
# FastAPI stub; set webhook.poll_interval_seconds=1 in config; watch
# webhook_delivery.status flip to `delivered` after a few seconds.
```

A dedicated integration test for this path can be added later.
