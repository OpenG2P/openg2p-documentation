---
description: >-
  How OpenG2P services integrate with the Audit Manager. Reference
  integration uses the Registry Staff Portal API as the first caller.
---

# Integration with Registry

This section documents how an OpenG2P service emits audit events to the
Audit Manager. The first reference integration is the **Registry Staff
Portal API**, where a single `AuditMiddleware` captures every authenticated
API call and ships it to Audit Manager as a CloudEvents payload.

## Pages in this section

| Page                                                              | Description                                                                                                              |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| [Local Install — Staff Portal API](local-install.md)              | Step-by-step instructions to run `openg2p-registry-staff-portal-api` locally on a developer machine, with all the fixes needed beyond the upstream README. Required before integrating audit emissions. |

## Integration approach (summary)

The reference integration follows a **single middleware** pattern:

1. **AuditMiddleware** is registered after the existing `AuthMiddleware` in
   the service's `main.py`. It becomes the outermost middleware.
2. On every request:
   * It calls `call_next` and lets the rest of the stack (auth, then the
     handler) run normally.
   * After the response is built, it inspects `request.state.auth` (the
     `AuthPrincipal` populated by `AuthMiddleware`) — and emits an audit
     event **only if the request was authenticated**.
   * Health probes (`/ping`), OpenAPI surfaces (`/docs`, `/redoc`,
     `/openapi.json`), and OPTIONS preflight requests are skipped.
3. Emission is **fire-and-forget** via `asyncio.create_task` — never
   blocks the response. Errors are logged, never raised to the caller.
4. A single `audit_manager_url=None` (default) makes the middleware a
   no-op — auditing is opt-in per environment.

The full middleware design is captured separately (see
[Functional Specifications](../functional-specifications.md) for the
event schema and [API Reference](../api-reference.md) for the HTTP
contract the middleware POSTs to).
