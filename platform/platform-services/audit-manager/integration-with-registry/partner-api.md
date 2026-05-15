---
description: >-
  AuditMiddleware for the Registry Partner API — the variant adapted to
  signature-based auth, with controller opt-in hooks for richer actor
  identity and outcome tracking.
---

# Audit Middleware — Partner API

## What it does

A single middleware class — `AuditMiddleware` — registered in the Partner
API's `main.py` as the **only** middleware (partner-api has no upstream
auth middleware to chain after). It captures every audit-worthy API call
and emits one CloudEvent to the Audit Manager service per call.

It mirrors the [Staff Portal API middleware](audit-middleware.md) in its
structural choices — fire-and-forget emission, never raises, disabled by
default — but adapts to partner-api's different auth and error model.

Key properties:

* **Never blocks the response.** Same `asyncio.create_task` pattern.
* **Never raises.** Audit Manager unreachable, slow, or returning errors
  are all logged but never propagated.
* **Disabled by default.** Both `audit_enabled=true` and a non-empty
  `audit_manager_url` must be set to actually emit events.

## How partner-api's auth model changes the middleware

Partner-api does **not** use Keycloak / JWT. Authentication is
**signature-based**: each request envelope carries:

```json
{
  "signature": "<JWT-shaped signature over header + message>",
  "header": { "sender_id": "...", "sender_uri": "...", ... },
  "message": { ... }
}
```

The signature is verified inside the controller via
`keymanager_helper.validate_signature(...)`, **after** the body has been
parsed by FastAPI. There is no `iam_core.user_auth.AuthMiddleware`,
nothing populates `request.state.auth`, and the actor identity
(`sender_id`) lives in the request body — which is already consumed by
the time middleware runs `call_next`.

This forces three concrete differences from staff-portal-api:

1. **No JWT decode helpers**, no `_extract_bearer`, no `principal` path,
   no 403-recovery branch. All removed.
2. **Actor identity is opt-in.** The middleware exposes a
   `request.state.audit_actor` hook for controllers to populate after
   they parse the envelope. If unset, the middleware records the call
   as `actor.type=anonymous` with only the client IP preserved.
3. **Outcome detection has an opt-in override.** Both partner-api
   controllers (`ingest_data`, `search`) catch exceptions and return a
   `200 OK` response with an error envelope inside. So HTTP status alone
   says "success" even on failure paths. The middleware exposes
   `request.state.audit_outcome` for controllers to assert
   `"failure"` / `"denied"` / `"success"` explicitly. If unset, falls
   back to HTTP status.

### Audit policy

| Request kind                                                       | Audited?    |
| ------------------------------------------------------------------ | ----------- |
| Controller set `request.state.audit_actor` (any outcome)           | **Yes**     |
| No actor enrichment + outcome non-2xx (rejected attempt)           | **Yes** — captured as `actor.type=anonymous`. Toggle off via `audit_anonymous_failures=false`. |
| No actor enrichment + outcome 2xx (legitimate sender)              | No          |
| Health probes (`/ping`)                                            | No          |
| OpenAPI surfaces (`/docs`, `/redoc`, `/openapi.json`, `/docs/oauth2-redirect`) | No |
| `OPTIONS` preflight                                                | No          |

## How a controller enriches the audit (optional)

The middleware works without any controller changes — it just records
anonymous + IP for everything until controllers opt in. To get richer
audit rows that identify the real partner, a controller should set
`request.state.audit_actor` immediately after envelope parse, and
`request.state.audit_outcome` in its error path.

**Recommended pattern** (DCI search controller as the example):

```python
async def search(self, request: Request, dci_search_request_env: DciSearchRequestEnvelope) -> DciSearchResponseEnvelope:
    header: DciRequestHeader = dci_search_request_env.header

    # Enrich the audit row with the partner identity before doing
    # anything else. If validate_signature() raises, the audit row will
    # still carry the asserted sender id (audit-worthy on its own).
    request.state.audit_actor = {
        "type": "service",
        "id": header.sender_id,
        "name": header.sender_uri or header.sender_id,
    }

    try:
        await self.keymanager_helper.validate_signature(...)
        # ... rest of the success path ...
        return success_response

    except Exception as error_exception:
        # Mark this 200-shaped wrapped error as a real failure so the
        # audit row reflects reality.
        request.state.audit_outcome = "failure"
        return error_response
```

Both hooks are completely optional. The middleware tolerates missing,
malformed, or partial enrichment.

## Where it sits in the middleware stack

```
Request
   │
   ▼
┌──────────────────────────────┐
│ AuditMiddleware (only one)   │  ← added in main.py
│  - dispatch starts           │
│  - calls call_next ──────────┼─┐
└──────────────────────────────┘ │
                                 ▼
                         FastAPI handler runs
                                 │
                                 │  may set:
                                 │   request.state.audit_actor
                                 │   request.state.audit_outcome
                                 │
                  ┌──────────────┘
                  ▼
┌──────────────────────────────┐
│ AuditMiddleware (return path)│  ← reads state hooks + response.status,
│  builds CloudEvent           │     fires async task to Audit Manager,
│  returns response to caller  │     returns response immediately
└──────────────────────────────┘
                  │
                  ▼
              Response
```

There is no auth middleware to chain after — partner-api validates
signatures inside the controller, not at a middleware layer.

## What gets emitted (per call)

A single CloudEvents 1.0 envelope with the OpenG2P `data` conventions:

| Field                | Source in the request                                                              |
| -------------------- | ---------------------------------------------------------------------------------- |
| `id`                 | UUID4 generated by the middleware                                                  |
| `source`             | `/openg2p/registry-partner-api` (configurable via `audit_source`)                  |
| `type`               | `org.openg2p.partner_api.<endpoint_function_name>` (prefix configurable)           |
| `time`               | UTC timestamp when the response was built                                          |
| `data.actor.type`    | From `request.state.audit_actor.type` (default `"service"`); `"anonymous"` if controller didn't enrich |
| `data.actor.id`      | From `request.state.audit_actor.id` (typically `header.sender_id`); `"anonymous"` fallback |
| `data.actor.name`    | From `request.state.audit_actor.name` if controller set it                         |
| `data.actor.ip`      | `X-Forwarded-For` first hop → `X-Real-IP` → `request.client.host`. Picks the real partner IP behind Istio / a load balancer rather than the proxy's IP. Auto-added if controller didn't set it. |
| `data.action`        | First word of the endpoint function name (`ingest_data` → `ingest`, `search` → `search`). See note in [Staff Portal API page](audit-middleware.md#why-action-is-the-first-word-not-the-full-function-name). |
| `data.outcome`       | Resolution order: exception in `call_next` → `failure`; `request.state.audit_outcome` override; HTTP status (`2xx → success`, `401/403 → denied`, other → `failure`) |
| `data.context.api`   | `"<METHOD> <path>"` — e.g. `"POST /dci/registry/sync/search"`                       |
| `data.context.module`| `"registry-partner-api"` (configurable via `audit_module`)                          |
| `data.context.http_status` | `response.status_code` (or `500` if exception in inner stack)                |
| `data.context.request_id` | Value of the `X-Request-ID` header if present                                 |
| `data.reason`        | Set when an exception bubbled out of `call_next`: `"<ExceptionClass>: <truncated msg>"` (200 chars max) |

`data.actor.id` and `data.actor.type` land in **flat indexed columns**
(`actor_id`, `actor_type`); other actor attributes go under
`details.actor.*` JSONB on the audit-manager side.

`data.resource` is intentionally **not** populated — partner-api
operations target collections (`reg_record_type` filters), not single
entities with stable URLs. We can add per-route extraction hints later
if needed.

## Files changed

In `openg2p-registry-gen2-apis/openg2p-registry-partner-api/`:

| File                                              | Change                                                                                  |
| ------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `src/openg2p_registry_partner_api/audit_middleware.py` | **New** — the middleware class (~290 lines). No JWT path; opt-in `request.state` hooks for actor and outcome. |
| `src/openg2p_registry_partner_api/config.py`           | **+15 lines**: 6 audit settings (`audit_enabled`, `audit_manager_url`, `audit_timeout_seconds`, `audit_source`, `audit_module`, `audit_anonymous_failures`) |
| `src/openg2p_registry_partner_api/main.py`             | **+24 lines** to register `AuditMiddleware`. Also adds the early `Settings.get_config()` call so audit settings are loaded before middleware registration (mirrors staff-portal-api). |
| `.env.example`                                              | **+13 lines** documenting the new env vars                                       |

No changes to controllers in v1. The opt-in `request.state` hooks are
available for controllers to use when ready.

## Implementation differences from staff-portal-api

The two middlewares share the same shape — `dispatch` → `_maybe_emit` →
`_build_actor` → `_build_event` → `_emit`. The differences below are all
intentional adaptations to partner-api's auth model. If you're porting
fixes between the two files, this is the cheat sheet.

| Aspect                                     | Staff Portal API                              | Partner API                                                       | Why different                                                       |
| ------------------------------------------ | --------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| `IAMInitializer` in `main.py`              | yes                                           | no                                                                | No Keycloak in partner-api                                          |
| `AuthMiddleware` registered before audit   | yes (chained — audit becomes OUTERMOST)       | no                                                                | Same — no Keycloak                                                  |
| Middleware position in stack               | outermost (after `AuthMiddleware`)            | only middleware                                                   | Nothing to chain after                                              |
| Actor identity source                      | `request.state.auth` (set by `AuthMiddleware`) | `request.state.audit_actor` (opt-in dict from controller)         | No upstream populates an actor for partner-api                      |
| Default actor types                        | `user`, `anonymous`                           | `service`, `anonymous`                                            | Partner-api is service-to-service                                   |
| JWT helpers (`_decode_jwt_payload`, `_extract_bearer`) | present                            | removed                                                           | No JWT to decode                                                    |
| 403-recovery path (JWT decoded without verify) | present                                  | removed                                                           | No 403 path — no JWT                                                |
| `client_id` constructor arg                | yes (`keycloak_client_id` for role extraction) | removed                                                           | No Keycloak roles to fetch                                          |
| `outcome_state_key` constructor arg + `request.state.audit_outcome` hook | no                | yes                                                               | Partner-api wraps errors in 200 responses — HTTP status is an unreliable outcome signal |
| `type_prefix` constructor arg              | hardcoded `org.openg2p.staff_portal`          | configurable, default `org.openg2p.partner_api`                   | Cleaner abstraction — easier to reuse                               |
| CloudEvents `source` default               | `/openg2p/registry-staff-portal-api`          | `/openg2p/registry-partner-api`                                   | Distinct event source per BFF                                       |
| `module` default                           | `registry-staff-portal-api`                   | `registry-partner-api`                                            | Same — distinct module label                                        |
| Env-var prefix                             | `REGISTRY_STAFF_PORTAL_API_`                  | `REGISTRY_PARTNER_API_`                                           | Matches existing service-level prefix                               |

## Configuration

All settings carry the `REGISTRY_PARTNER_API_` env prefix. Defaults make
the middleware a no-op until both `AUDIT_ENABLED` and `AUDIT_MANAGER_URL`
are set.

| Env var | Default | Purpose |
| ------- | ------- | ------- |
| `REGISTRY_PARTNER_API_AUDIT_ENABLED` | `"false"` | Master on/off. Must be `"true"` to emit. |
| `REGISTRY_PARTNER_API_AUDIT_MANAGER_URL` | `""` | Base URL of the Audit Manager service (e.g. `http://audit-manager.commons`). The middleware POSTs to `<url>/v1/auditmanager/events`. |
| `REGISTRY_PARTNER_API_AUDIT_TIMEOUT_SECONDS` | `"2.0"` | httpx timeout for the audit POST. Short — the audit pipeline absorbs slow/unreachable Audit Manager. |
| `REGISTRY_PARTNER_API_AUDIT_SOURCE` | `"/openg2p/registry-partner-api"` | CloudEvents `source` attribute. |
| `REGISTRY_PARTNER_API_AUDIT_MODULE` | `"registry-partner-api"` | Free-form label landing in `details.context.module`. |
| `REGISTRY_PARTNER_API_AUDIT_ANONYMOUS_FAILURES` | `"true"` | Whether to audit non-2xx calls without controller-supplied actor enrichment. Set to `"false"` to skip those. |

### Local-dev quickstart

```bash
# Run audit-manager (in another terminal — see Audit Manager Deployment page)
helm install audit-manager openg2p/openg2p-audit-manager -n commons

# In another terminal, port-forward the cluster's audit-manager service
kubectl port-forward -n commons svc/audit-manager 8000:80

# In your .env (or shell env)
export REGISTRY_PARTNER_API_AUDIT_ENABLED=true
export REGISTRY_PARTNER_API_AUDIT_MANAGER_URL=http://localhost:8000

# Start partner-api
python3 -m openg2p_registry_partner_api.main
# Should log: "AuditMiddleware enabled — emitting to http://localhost:8000/v1/auditmanager/events ..."
```

### Wiring through the registry Helm chart

Mirror what the staff-portal-api page documents — add the same three
`global.audit*` values, and wire them into `partnerApi.envVars` block:

```yaml
# charts/openg2p-registry/values.yaml — partnerApi.envVars block
partnerApi:
  envVars:
    REGISTRY_PARTNER_API_AUDIT_ENABLED: '{{ .Values.global.auditEnabled | quote }}'
    REGISTRY_PARTNER_API_AUDIT_MANAGER_URL: '{{ tpl (.Values.global.auditManagerUrl | toString) $ }}'
    REGISTRY_PARTNER_API_AUDIT_ANONYMOUS_FAILURES: '{{ .Values.global.auditAnonymousFailures | quote }}'
```

The `global.audit*` values themselves are documented on the
[Staff Portal API page](audit-middleware.md#wiring-through-the-registry-helm-chart) — the same
values feed both BFFs.

## What "no-op" looks like

If `audit_enabled=false` OR `audit_manager_url` is empty, the middleware
runs but does nothing useful:

* Constructor logs `AuditMiddleware disabled (...)` once at startup.
* `dispatch` short-circuits the entire enable-check at request time.
* No httpx client is ever created (lazy init).

This is the default after install and is safe to ship in environments
where Audit Manager isn't deployed.

## Known limitations (v1)

1. **Anonymous-by-default actor.** Until controllers opt in to set
   `request.state.audit_actor`, every audit row identifies the caller
   only by IP. Functional but coarse — the actor enrichment is the
   recommended next step (see ["How a controller enriches the audit"](#how-a-controller-enriches-the-audit-optional)
   above).
2. **Wrapped 200-on-error responses look like success** unless the
   controller sets `request.state.audit_outcome = "failure"`. Same
   opt-in pattern as the actor hook; same recommended next step.
3. **No body inspection.** The middleware deliberately does not re-read
   the request body to extract `header.sender_id`. Body-replay in
   middleware is fragile (large payloads, non-JSON content); the
   `request.state.audit_actor` hook is a cleaner alternative.

## Related pages

* [Audit Middleware — Staff Portal API](audit-middleware.md) — the JWT-aware variant; useful background for the design decisions shared across both BFFs.
* [Audit Manager Functional Specifications](../functional-specifications.md) — the CloudEvent schema this middleware produces.
* [Audit Manager API Reference](../api-reference.md) — the HTTP contract the middleware POSTs to.
