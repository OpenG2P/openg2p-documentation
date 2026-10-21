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
| Audit | [Decisions](#staff-endpoints) | **staff-api** — administrators |
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
| **staff-api** | audit `/decisions`, assisted-consent verifications, partner portal API | Keycloak, **staff realm**. Roles `CONSENT_MANAGER_ADMIN` (decisions) and `CONSENT_MANAGER_APPROVER` (verify assisted consents), from `realm_access` / `resource_access.*`. The partner portal API uses the **partner realm** |
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
* **Idempotency:** re-validating the same consent object (`jti`) for the same `data_controller`
  returns the same `consent_id` / `receipt_id`. Each registry that validates a multi-grant consent
  gets its own.
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
| `malformed_object` | Consent object failed schema validation (incl. both `grants` and `data_controller`/`data_scopes`, a duplicate controller in `grants`, or no `data_controller` on `/validate` for a consent with `grants`) |
| `unknown_partner` | Partner Management has no active policy for the partner and this data controller (partner unknown or not active, or not granted this registry) |
| `policy_unavailable` | Partner Management could not be reached and no policy answer is cached (fail closed; retry later) |
| `signature_invalid` | JWS signature did not verify, the `kid` has no active key in Partner Management, or the algorithm is not allowed |
| `audience_mismatch` | `aud` is not this partner / controller |
| `controller_not_granted` | The consent has no grant for the `data_controller` in the request (or a single-registry consent names another controller) |
| `subject_mismatch` | `request_context.subject_id` has the consent subject's type but a different value |
| `subject_not_allowed` | Subject missing or `subject_id_type` not permitted |
| `purpose_not_allowed` | Purpose code outside policy, or (use-case mode) not the use case's purpose |
| `use_case_not_granted` | Use-case mode: the partner has no active policy for `request_context.use_case` in Partner Management, or a stored consent was given for another use case |
| `scope_exceeds_policy` | Requested scope not permitted; empty effective intersection |
| `validity_exceeds_policy` | Requested validity longer than `max_validity_duration` |
| `expired` | Consent outside its validity window |
| `revoked` | Consent has been revoked |
| `replay` | Stale `issued_at`, or a known `jti` reused for a different consent (a repeat of the same signed consent for the same `data_controller` returns the stored decision instead) |
| `receipt_presenter_not_allowed` | `issue_receipts` from a caller that is not a configured token presenter, or consent-token issuing is not enabled ([Exchange consent tokens](../design/exchange-receipts.md)) |
| `receipt_issuer_not_trusted` | A consent token from an issuer this CM does not trust (or no trusted issuers configured) |
| `receipt_invalid` | A trusted issuer's consent token failed verification (signature, `alg`, missing claims, unknown at the issuer) |
| `presenter_mismatch` | The consent token's `presenter` is not the caller (`partner_id`) or not the issuer's configured presenter |
| `receipt_status_unavailable` | The consent token's status could not be checked at its issuer (fail closed) |

## Staff endpoints

### `GET /consent/v1/decisions`

Read the decision log (staff-api, role `CONSENT_MANAGER_ADMIN`). Filters: `partner_id` (the
partner's audience, e.g. `bank-a`), `decision` (`permit` or `deny`); `limit` (1–200, default 50).

```json
// response 200
[
  { "id": "d-5512", "consent_id": "CONSENT-123456", "partner_id": "bank-a",
    "object_jti": "6f1c-unique-per-object", "data_controller": "farmer-registry",
    "decision": "permit", "reason_code": "ok", "detail": null, "policy_version": 4,
    "policy_id": "7d0c9a52-…", "policy_ref": "data_controller:farmer-registry",
    "created_at": "2026-10-01T10:00:02Z" }
]
```

The policy applied in Partner Management: `policy_ref` is its key (`data_controller:<registry>` or
`use_case:<name@major>`), `policy_version` its version, `policy_id` PM's id of that version (all
null when no policy was read, e.g. `unknown_partner`). The staff console shows it as "Registry
farmer-registry · v4" / "Use case loan-profile@1 · v1", linked to the partner's page in Partner
Management (`partnerManagementUiUrl`).

## Implementation

The service is built on [`openg2p-fastapi-common`](https://github.com/OpenG2P/openg2p-fastapi-common)
with **PostgreSQL** for storage. It is **stateless and horizontally scalable** — scale by adding
pods/workers behind a load balancer; the only shared state is Postgres. Consent expiry runs as an
external CronJob (`python -m openg2p_consent_manager.expire`) rather than an in-pod scheduler, and
the hot path lazily expires on read. Partner keys and policies, read from Partner Management, are
cached per pod with a short TTL to keep `/validate` cheap under high request rates
([Partner Management integration](../design/partner-management-integration.md)). Partners and their
policies are managed in Partner Management
([API reference](../../platform/platform-services/partner-management/api-reference.md)), not here.

These pages are the **normative source** for the contract — the API is documented here in GitBook
directly (FastAPI also serves a live OpenAPI/Swagger UI at `/docs` for the running service).
