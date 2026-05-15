---
description: >-
  How OpenG2P registry services integrate with the Audit Manager.
  Covers two BFF integrations — Staff Portal API and Partner API — that
  share the same middleware shape but adapt to their respective auth
  models.
---

# Integration with Registry

This section documents how OpenG2P registry services emit audit events
to Audit Manager. Each registry BFF (Backend For Frontend) installs a
small `AuditMiddleware` that captures every audit-worthy API call and
ships it to Audit Manager as a CloudEvents payload, fire-and-forget.

There is **no shared library** for the middleware — each BFF carries its
own copy adapted to its auth model. This is a deliberate choice: the
shared `openg2p-fastapi-common` library is consumed by many services
across the platform and its release cycle should not be coupled to
audit-only changes. Drift risk is accepted in exchange for keeping the
common library stable.

## Pages in this section

| Page                                                              | Description                                                                                                              |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| [Local Install — Staff Portal API](local-install.md)              | Step-by-step instructions to run `openg2p-registry-staff-portal-api` locally on a developer machine, with all the fixes needed beyond the upstream README. Required before integrating audit emissions. |
| [Audit Middleware — Staff Portal API](audit-middleware.md)        | Design of the middleware in Staff Portal API: where it sits in the stack, what gets emitted per call, the files changed, configuration env vars (including the on/off switch), the audit policy (including rejected anonymous calls), and how the JWT-on-403 recovery works. |
| [Audit Middleware — Partner API](partner-api.md)                  | The partner-api variant of the same middleware: how it adapts to signature-based auth, the two opt-in `request.state` hooks for controllers (actor enrichment + wrapped-200-on-error outcome override), and the limitations of the v1 wiring. |
| [Verification — End to End](verification.md)                      | Smoke test that confirms the integration works: token fetch, authenticated call, anonymous call, and skipped `/ping` — with the exact `curl` + `psql` for each, plus a troubleshooting matrix. |

## Where the middleware lives

| BFF | Repo | Auth model | Audit middleware path |
| --- | ---- | ---------- | --------------------- |
| Staff Portal API | `openg2p-registry-gen2-apis/openg2p-registry-staff-portal-api` | Keycloak JWT (via `iam_core.user_auth.AuthMiddleware`) | `src/openg2p_registry_staff_portal_api/audit_middleware.py` |
| Partner API     | `openg2p-registry-gen2-apis/openg2p-registry-partner-api`     | Signature in request body (verified inside controllers via `keymanager_helper`) | `src/openg2p_registry_partner_api/audit_middleware.py` |
| Beneficiary Portal API | `openg2p-registry-gen2-apis/openg2p-registry-bene-portal-api` | (not yet integrated) | — |

## Integration approach (summary)

Every BFF integration follows the same shape:

1. **`AuditMiddleware`** is registered in `main.py`. For BFFs that have
   an upstream auth middleware (e.g. staff-portal-api's
   `AuthMiddleware`), the audit middleware is added **after** it, so it
   becomes the OUTERMOST wrapper and sees the populated
   `request.state.auth` post-handler. For BFFs without an upstream
   auth middleware (partner-api), the audit middleware is the only
   middleware.
2. **On every request** the middleware:
   * Calls `call_next` and lets the rest of the stack (auth, handler)
     run normally. If the inner stack raises, the exception is captured,
     audited as `outcome=failure / status=500`, then re-raised.
   * Decides whether to emit based on actor presence + outcome:
     | Request kind                                         | Audited? |
     | ---------------------------------------------------- | -------- |
     | Has actor identity (any outcome)                     | YES      |
     | No actor + outcome 2xx (legitimate public call)      | NO       |
     | No actor + outcome non-2xx, `audit_anonymous_failures=true` | YES (anon) |
     | Health probes / OpenAPI surfaces / OPTIONS preflight | NO       |
   * Builds a CloudEvents 1.0 envelope and POSTs it to Audit Manager
     via `asyncio.create_task` — never blocks the response. Errors are
     logged, never raised to the caller.
3. **Default = disabled.** Both `audit_enabled=true` AND a non-empty
   `audit_manager_url` must be set; otherwise the middleware is a no-op.

## How the two implementations differ

The interface principles are identical; the implementations diverge
where the auth model demands it:

| Principle | Staff Portal API | Partner API |
| --------- | ---------------- | ----------- |
| Where actor identity comes from | `request.state.auth` populated by upstream `AuthMiddleware` (Keycloak JWT) | `request.state.audit_actor` set by the controller after parsing the signed envelope (opt-in) |
| Anonymous fallback | `actor.type=anonymous`, IP only — used for unauthenticated rejected attempts | Same shape, used when controller doesn't enrich (the v1 default state for all calls) |
| Outcome derivation | HTTP status code | HTTP status code, with controller-supplied `request.state.audit_outcome` override (because partner-api wraps errors in 200 responses) |
| 403 recovery | Decodes the bearer JWT (known-valid because AuthMiddleware ran) to identify the user that lacked permission | N/A — no JWT, no 403 path |
| CloudEvents `source`/`type` prefix | `/openg2p/registry-staff-portal-api`, `org.openg2p.staff_portal.<func>` | `/openg2p/registry-partner-api`, `org.openg2p.partner_api.<func>` |

The full middleware designs are captured on the per-BFF pages above.
For the event schema and the HTTP contract the middleware POSTs to,
see [Functional Specifications](../functional-specifications.md) and
[API Reference](../api-reference.md).
