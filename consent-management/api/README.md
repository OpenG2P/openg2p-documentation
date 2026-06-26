---
description: >-
  Conventions for the Consent Manager HTTP API — base path, authentication,
  the decision/error model, and reason codes shared across endpoints.
---

# API Reference

The Consent Manager exposes a versioned REST API. This page defines the conventions every
endpoint follows; the endpoint pages document the individual contracts.

| Group | Page | Audience |
| --- | --- | --- |
| Verification &amp; enforcement | [Verification API](verification-api.md) | Registry / PEPs (machine-to-machine) |
| Partner onboarding &amp; policy | [Partner &amp; Policy API](partner-and-policy-api.md) | Administrators / controller onboarding |
| Consent lifecycle | [Consent Lifecycle API](consent-lifecycle-api.md) | Origination clients (apps, staff portal) |
| Subject rights (GDPR) | [Subject API](subject-api.md) | Authenticated subjects (UI later) |

## Base path &amp; versioning

* Base path: `/consent/v1`
* Well-known: `/.well-known/jwks.json` (CM signing keys, unversioned)
* Breaking changes increment the path version (`/consent/v2`).

## Authentication

| Caller | Mechanism |
| --- | --- |
| Registry / PEP → `/validate`, `/consents/{id}/status` | **mTLS** or a signed service token |
| Administrator → partner &amp; policy endpoints | Admin credentials (elevated), network-restricted |
| Subject → `/my/*` | OIDC **bearer token**, scoped to the authenticated subject |
| Anyone → receipts, JWKS, schemas | Public read (signatures make them self-verifying) |

The consent object's own JWS signature is the application-layer proof on the verification path,
layered on top of transport/service auth.

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
| `unknown_partner` | Partner not onboarded / suspended, or `kid` not found |
| `signature_invalid` | JWS signature did not verify |
| `audience_mismatch` | `aud` is not this partner / controller |
| `subject_not_allowed` | Subject missing or `subject_id_type` not permitted |
| `purpose_not_allowed` | Purpose code outside policy |
| `scope_exceeds_policy` | Requested scope not permitted; empty effective intersection |
| `validity_exceeds_policy` | Requested validity longer than `max_validity_duration` |
| `expired` | Consent outside its validity window |
| `revoked` | Consent has been revoked |
| `replay` | Duplicate `jti` or stale `issued_at` |

## Specifications

A machine-readable OpenAPI 3.1 specification will accompany this contract and be published in
Stoplight alongside the other OpenG2P services once implementation begins. The pages here are the
normative source for that spec.
