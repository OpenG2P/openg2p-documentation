---
description: >-
  Conventions for the Consent Manager HTTP API — base path, authentication,
  the decision/error model, and reason codes shared across endpoints.
---

# API Reference

The Consent Manager exposes a versioned REST API. This page defines the conventions every
endpoint follows; the endpoint pages document the individual contracts.

| Group | Page | API audience |
| --- | --- | --- |
| Verification &amp; enforcement | [Verification API](verification-api.md) | **partner-api** — Registry / PEPs (partner-signed, machine-to-machine) |
| Partner onboarding &amp; policy | [Partner &amp; Policy API](partner-and-policy-api.md) | **staff-api** — Administrators / controller onboarding |
| Consent lifecycle | [Consent Lifecycle API](consent-lifecycle-api.md) | **beneficiary-api** — origination clients (scaffolded/later) |
| Subject rights (GDPR) | [Subject API](subject-api.md) | **beneficiary-api** — authenticated subjects (scaffolded/later) |

## Base path &amp; versioning

* Base path: `/consent/v1`
* Well-known: `/.well-known/jwks.json` (CM signing keys, unversioned)
* Breaking changes increment the path version (`/consent/v2`).

## Audiences &amp; deployment

The CM ships as a **single chart** but is deployed once **per API audience** — separate
Deployments that share the same code and Postgres, differing only in which router/audience they
serve and how they authenticate callers. Authentication therefore differs by audience:

| Audience | Endpoints | Auth model |
| --- | --- | --- |
| **staff-api** | partner &amp; policy, AWE approver proxy, audit `/decisions` | Keycloak, **staff realm**. Roles `CONSENT_MANAGER_ADMIN` (onboarding/policy) and `CONSENT_MANAGER_APPROVER` (approval decisions), from `realm_access` / `resource_access.*` |
| **partner-api** | `/validate`, `/consents/{id}/status`, `/receipts/{id}`, JWKS | **No Keycloak.** Trust is the **partner-signed consent object**, verified against Partner Management (PM) keys and replay-guarded by `jti`. The Registry↔CM link is secured at transport (**Istio mTLS**). This deployment is the **PDP** |
| **beneficiary-api** | `/my/*`, `/consent-requests/*` | Keycloak, **beneficiary realm**, scoped to the authenticated subject (scaffolded/later) |
| any | receipts, JWKS | Public read (signatures make them self-verifying) |

On **partner-api** there is no caller token: the consent object's own JWS signature (verified via
PM keys) is the sole application-layer proof, with Istio mTLS providing transport authentication
between the Registry and CM.

## Conventions

* **Content type:** `application/json`; JSON-LD documents use `application/ld+json`.
* **Timestamps:** RFC 3339 / ISO 8601 UTC.
* **Identifiers:** UUIDs unless an external id (`subject_id`, `kid`, purpose code) is referenced.
* **Idempotency:** re-validating the same consent object (`jti`) returns the same
  `consent_id` / `receipt_id`.
* **Pagination:** list endpoints accept `page` (≥1) and `size` (1–100) and return
  `{ items, total, page, size, pages }`.

## Decision &amp; error model

The verification endpoint returns a **decision** object (HTTP 200 for both permit and deny so the
PEP can read the reason). All other endpoints use standard HTTP status codes with a problem body:

```json
{ "error": "scope_exceeds_policy", "detail": "human-readable explanation", "trace_id": "..." }
```

### Shared reason codes

Used in decisions (`reason_code`) and errors (`error`):

| Code | Meaning |
| --- | --- |
| `ok` | Permit — all checks passed |
| `malformed_object` | Consent object failed schema validation |
| `unknown_partner` | Partner not onboarded / suspended, or `kid` not found in Partner Management |
| `signature_invalid` | JWS signature did not verify |
| `audience_mismatch` | `aud` is not this partner / controller |
| `subject_not_allowed` | Subject missing or `subject_id_type` not permitted |
| `purpose_not_allowed` | Purpose code outside policy |
| `scope_exceeds_policy` | Requested scope not permitted; empty effective intersection |
| `validity_exceeds_policy` | Requested validity longer than `max_validity_duration` |
| `expired` | Consent outside its validity window |
| `revoked` | Consent has been revoked |
| `replay` | Duplicate `jti` or stale `issued_at` |

## Implementation

The service is built on [`openg2p-fastapi-common`](https://github.com/OpenG2P/openg2p-fastapi-common)
with **PostgreSQL** for storage. It is **stateless and horizontally scalable** — scale by adding
pods/workers behind a load balancer; the only shared state is Postgres. Consent expiry runs as an
external CronJob (`python -m openg2p_consent_manager.expire`) rather than an in-pod scheduler, and
the hot path lazily expires on read. Partner keys/policies are cached per pod with a short TTL to
keep `/validate` cheap under high request rates.

These pages are the **normative source** for the contract — the API is documented here in GitBook
directly (FastAPI also serves a live OpenAPI/Swagger UI at `/docs` for the running service).
