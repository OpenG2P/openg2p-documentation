# Technical Architecture

## Components

Following the national-social-registry pattern, the backend is split into two
deployables that share **one Python package and one database**:

| Component | Stack | Auth |
| --- | --- | --- |
| **staff-portal-api** | FastAPI on `openg2p-fastapi-common` (async SQLAlchemy 2.0, PostgreSQL) | Keycloak **staff**-realm JWT + `partner_manager` role |
| **partner-api** | Same package, key-fetch entrypoint only | None (public, internal gateway) |
| **staff-portal-ui** | Next.js (App Router), OpenG2P/AWE theme | Shared commons IAM login |

The two API images are built from the same `openg2p-partner-management-api`
package with different entrypoints (`staff_portal_main` / `partner_main`); both
run the same idempotent migrations against the shared DB.

```
                          ┌──────────────────────────────┐
   staff admin ──────────▶│  staff-portal-ui (Next BFF)   │
   (browser)              │  /api/login, /api/me → IAM    │
                          │  /api/pm/*  → staff-portal-api │
                          └───────┬───────────────┬───────┘
        login (cookies)          │               │  Bearer (server-side)
                                 ▼               ▼
              ┌──────────────────────────┐  ┌───────────────────────────┐
              │ commons-services         │  │ staff-portal-api           │
              │ iam-staff-portal-api     │  │ (staff JWT + partner_mgr)  │
              │ (SHARED login/profile)   │  │ onboarding / approvals     │
              └──────────────────────────┘  └───────────────────────────┘

              ┌───────────────────────────┐
   g2p-bridge │ partner-api               │  GET /keys/{partner_id}
   consent-mgr│ (public key fetch, no auth)│◀── other modules, in-cluster,
   … ────────▶│ fail-closed, cached        │    internal gateway
              └───────────────────────────┘
```

## Staff authentication (national-social-registry pattern)

Login is **not** implemented in this service. The staff-portal-ui is a Next.js
backend-for-frontend:

1. `GET /api/login` calls the **shared** `commons-services-iam-staff-portal-api`
   (`IAM_URL`) `start_authentication_transaction` and redirects to Keycloak
   (staff realm).
2. IAM completes the OIDC callback and sets httpOnly `X-Access-Token` /
   `X-ID-Token` cookies.
3. `/api/me`, `/api/logout` also proxy to the shared IAM. All **domain** calls go
   through `/api/pm/*`, which forwards the access-token cookie as a `Bearer` to
   this release's **staff-portal-api** (`STAFF_PORTAL_API_URL`). The token never
   reaches browser JavaScript.

The staff-portal-api validates the JWT with `openg2p-fastapi-auth`
`JwtBearerAuth` (issuer/JWKS against the staff realm) and requires the
`partner_manager` role — a client role under the `<release>-staff-portal`
Keycloak client that `keycloak-init` provisions.

## Data model

Three tables (`pm_partners`, `pm_partner_keys`, `pm_partner_requests`), UUID
string PKs, created/updated timestamps. JSON columns use `JSONB` on PostgreSQL
and fall back to `JSON` elsewhere (so the suite runs on SQLite).

Key material is normalised and validated at request-creation time and stashed in
the request's `proposed_keys`, so approval is a cheap, deterministic apply — the
same path a future AWE webhook would call.

## Key fetch path

`get_servable_keys(partner_id)` returns active, currently-valid keys **only** for
an `active` partner, else `None`; controllers map `None` to a uniform
`404 not available`. Responses set `Cache-Control` so a caller-side cache (e.g.
the commons `PartnerKeyStore`) absorbs load and picks up rotations within the TTL.

## Auditability

Partner Management keeps **two complementary audit trails** — appropriate for
government infrastructure where every change must be accountable:

1. **Local ledger (`pm_audit_events`) — authoritative, always on.** Every
   material state change (partner created/approved/disabled/enabled, key
   added/revoked, request submitted/approved/rejected) writes an append-only row
   **in the same DB transaction** as the change itself. Because it is atomic with
   the change, it can never be lost or drift, and it survives independently of any
   other service. It records actor, timestamp, entity, request id, and a
   before→after summary, and powers the per-partner **History** view in the admin
   UI (`GET /partners/{partner_id}/audit`). Rows are never updated or deleted.

2. **Central Audit Manager — comprehensive forensic trail.** The staff-portal-api
   ships every admin API call to the platform [Audit Manager](../audit-manager/README.md)
   as a CloudEvent (`POST /v1/auditmanager/events`) via a middleware that is
   **config-gated** (`AUDIT_ENABLED` + `AUDIT_MANAGER_URL`) and **non-blocking**
   (fire-and-forget; a down Audit Manager never fails or delays a request). This
   gives investigators a single, tamper-evident, long-retention store correlated
   across all OpenG2P services.

The two are deliberately layered: the local ledger is the guaranteed
system-of-record for domain changes; Audit Manager is the cross-platform
aggregate. The local table is a deliberate divergence from the (central-only)
OpenG2P reference, justified by PM's low-volume, high-sensitivity change set.

## How other modules consume it (v1)

Modules call the **partner-api** key-fetch endpoints directly (server-to-server,
in-cluster). A documented follow-up adds a `crypto_backend="partner-mgmt"` option
to `openg2p-fastapi-common` so g2p-bridge and consent-manager fetch-and-cache
from this service by flipping a config flag — turning their local `partner_keys`
table into a cache rather than a source of truth.
