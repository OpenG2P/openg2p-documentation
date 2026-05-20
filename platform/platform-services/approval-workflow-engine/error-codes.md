# Error codes

AWE returns errors in a stable envelope shape, with an `AWE-NNN` code
in `errors[0].errorCode`. This page is the canonical catalog — what
each code means, the HTTP status it ships with, what triggers it, and
whether a Caller should retry.

## Response envelope

Every non-2xx response (and every 2xx) uses the same envelope:

```json
{
  "id": "openg2p.awe",
  "version": "1.0",
  "responsetime": "2026-04-23T10:00:00.000Z",
  "response": null,
  "errors": [
    { "errorCode": "AWE-003", "message": "Request not found" }
  ]
}
```

* `response` is the success payload on 2xx, `null` on errors.
* `errors` is empty on 2xx, populated on errors. Today AWE returns
  exactly one entry; the array shape is reserved for future multi-
  error responses.

## Code catalog

| Code | HTTP | When it fires | Retry safe? |
|--|--|--|--|
| `AWE-001` | 404 | Policy or policy version not found. Includes "no `active` version for this `policy_key`" — `POST /v1/awe/requests` returns this when the Caller's `policy_key` resolves to no live policy. | No — fix the reference before retrying. |
| `AWE-002` | 409 | Policy version conflict on create: the `policy_key` already exists. Use `PUT /v1/awe/policies/{key}` to add a new version instead of `POST`. | No — change the request. |
| `AWE-003` | 404 | Approval request not found by id. | No. |
| `AWE-004` | 404 | Task or delegation not found by id. | No. |
| `AWE-005` | 503 | Service has not finished startup — DB schema not yet ensured, workers not started. | **Yes** — the readiness probe will flip to 200 within a few seconds of pod start. |
| `AWE-006` | 503 | Health probe failed to reach the database. | **Yes** after the DB recovers. |
| `AWE-007` | 400 / 409 / 503 | Generic state-conflict / engine-refused / upstream-resolver failure. The HTTP code disambiguates: 400 = engine refused to start (bad context), 409 = resource in wrong state for the transition (e.g. task already completed, request in terminal state, policy version not draft), 503 = an approver-resolution rule's upstream call failed (Keycloak admin API, HTTP resolver). | **Only 503** — for 400/409 the underlying state must change before retry succeeds. |
| `AWE-008` | 401 / 403 | Authentication or authorisation failure. 401 = bearer token missing / malformed / signature or expiry invalid. 403 = token valid but caller lacks the required role (`AWE_VIEWER` / `AWE_ADMIN`) or is not the task's assignee. | **Yes after fixing the token** for 401; never for 403 without a permission change. |
| `AWE-009` | 409 | `Idempotency-Key` header was previously seen with a *different* request body. The header value must uniquely identify one logical request — reusing it across distinct payloads is a Caller bug. | No — generate a fresh key or use the original payload. |
| `AWE-010` | 400 | Validation failure on a policy definition — URL/body mismatch, malformed stage, etc. (Distinct from FastAPI's auto-422 for schema-level validation.) | No — fix the body. |

## Mapping codes to endpoints

| Endpoint | Possible codes |
|--|--|
| `POST /v1/awe/policies` | `AWE-002`, `AWE-008` |
| `PUT /v1/awe/policies/{key}` | `AWE-001`, `AWE-008`, `AWE-010` |
| `PATCH /v1/awe/policies/{key}/versions/{v}` | `AWE-001`, `AWE-007`, `AWE-008`, `AWE-010` |
| `POST /v1/awe/policies/{key}/versions/{v}/activate` | `AWE-001`, `AWE-008` |
| `POST /v1/awe/policies/{key}/versions/{v}/deactivate` | `AWE-001`, `AWE-007`, `AWE-008` |
| `POST /v1/awe/policies/{key}/versions/{v}/simulate` | `AWE-001`, `AWE-007` (503), `AWE-008` |
| `POST /v1/awe/requests` | `AWE-001`, `AWE-007`, `AWE-008`, `AWE-009` |
| `GET /v1/awe/requests/{id}` | `AWE-003`, `AWE-008` |
| `POST /v1/awe/requests/{id}/cancel` | `AWE-003`, `AWE-007`, `AWE-008` |
| `POST /v1/awe/tasks/{id}/claim` | `AWE-004`, `AWE-007`, `AWE-008` |
| `POST /v1/awe/tasks/{id}/decision` | `AWE-003`, `AWE-004`, `AWE-007`, `AWE-008` |
| `POST /v1/awe/tasks/{id}/reassign` | `AWE-003`, `AWE-004`, `AWE-007`, `AWE-008` |
| `POST /v1/awe/admin/deliveries/{id}/retry` | `AWE-007`, `AWE-008` |
| `POST /v1/awe/delegations` | `AWE-008` |
| `DELETE /v1/awe/delegations/{id}` | `AWE-004`, `AWE-008` |
| `GET /v1/awe/health` | `AWE-005`, `AWE-006` |

All read endpoints (`GET`) additionally return `AWE-008` if the bearer
token is missing or insufficiently privileged.

## What about 422?

FastAPI emits HTTP 422 (with its own body shape) when the request body
fails Pydantic schema validation — missing fields, wrong types, etc.
These are **not** AWE error codes; they're caught upstream of any
controller logic. Treat them the same as 400: not retryable, fix the
body.

## Caller guidance

* **Always inspect `errors[0].errorCode`** — never branch on HTTP
  status alone. The same status (e.g. 409) covers several distinct
  causes (`AWE-002`, `AWE-007`, `AWE-009`), each warranting different
  Caller-side handling.
* **Retry on 503 with exponential backoff.** AWE's own outbound
  webhook retry schedule (1m → 5m → 15m → 1h → 6h) is a reasonable
  template.
* **Never retry 4xx without changing the request** — the state /
  payload / token is wrong; retrying the same call won't help.
* **`Idempotency-Key` on `POST /v1/awe/requests`** dedups retries
  safely: AWE replays the original 201 response body for any retry
  with the same key. If you change the body, expect `AWE-009`.
