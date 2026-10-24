---
description: >-
  Conventions of the Consent Manager HTTP API: endpoints by audience,
  authentication, the decision and error model, the shared reason codes, and
  the staff endpoints (decision log, consent verification, consents, partner
  portal).
---

# API Reference

The Consent Manager exposes a versioned REST API. This page holds the conventions and the staff endpoints; the endpoint pages hold the other contracts.

| Group | Page | API audience |
| --- | --- | --- |
| Verification | [Verification API](verification-api.md) | **partner**: registries and the Composite, in cluster |
| Decision log, consent verification, consents, partner portal | [Staff endpoints](#staff-endpoints) | **staff**: CM staff (console) and partner users (partner portal) |
| Origination | [Consent Lifecycle API](consent-lifecycle-api.md) | **beneficiary** (off by default) |
| Subject rights (GDPR) | [Subject API](subject-api.md) | **beneficiary** (off by default) |

## Base path and versioning

* Base path: `/consent/v1`; the public keys at `/.well-known/jwks.json`.
* Breaking changes increment the path version (`/consent/v2`).
* Each running API also serves its OpenAPI / Swagger UI at `/docs`.

## Authentication by audience

Each audience is a separate Deployment of the same image ([Architecture](../design/architecture.md#apis-by-audience)):

| Audience | Endpoints | Auth |
| --- | --- | --- |
| **staff** | `/decisions`, `/verifications/*`, `/consents/{id}`, `/consents/{id}/receipt`, `/consents/{id}/revocations`, `/partner-portal/*` | Keycloak bearer token. Staff realm: `CONSENT_MANAGER_ADMIN` (decisions; also reads verifications), `CONSENT_MANAGER_APPROVER` (verifications); either for consents. Partner portal: a **partner-realm** token with a `partner_id` claim and the role `PARTNER_OPERATOR` or `PARTNER_ADMIN` |
| **partner** | `/validate`, `/consents/{id}/status`, `/receipts/{jti}/status`, `/receipts/{id}`, JWKS | **None.** In cluster only (Istio mTLS); the proof is the consent itself. Only the JWKS (and, if enabled, the token status) is routed from outside ([Deployment](../deployment/README.md#what-is-reachable-from-outside)) |
| **beneficiary** | `/my/*`, `/consent-requests/*`, `/consents/{id}/revoke` | Keycloak bearer token (beneficiary realm); `/my/*` is scoped to the token's subject |

## Conventions

* **Content type:** `application/json`.
* **Timestamps:** ISO 8601, UTC.
* **Identifiers:** UUIDs unless an external ID (`subject_id`, `kid`, purpose code) is meant.
* **Pagination:** `/my/consents` takes `page` (≥1) and `size` (1–100) and returns `{items, total, page, size, pages}`; staff lists take `limit` and `offset`.

## Decision and error model

`/validate` returns a **decision**, HTTP 200 for both permit and deny, so the caller can read `reason_code`. Other endpoints use HTTP status codes with a body `{"error": "<message>"}`.

### Shared reason codes

| Code | Meaning |
| --- | --- |
| `ok` | Permit: all checks passed |
| `malformed_object` | The consent object failed schema validation (both `grants` and `data_controller`/`data_scopes`, a controller twice, no `data_controller` for a consent with `grants`), or the request is malformed (both `consent_jws` and `consent_id`; a lookup missing its fields) |
| `unknown_partner` | Partner Management has no active policy for the partner and this data controller (partner unknown, not active, or not granted this registry) |
| `policy_unavailable` | Partner Management could not be reached and nothing usable is cached (fail closed; retry later) |
| `signature_invalid` | The JWS signature did not verify, the `kid` has no active key in Partner Management, or the algorithm is not allowed |
| `audience_mismatch` | `aud` is not the partner, or the grant is not for the policy's controller; for a consent token, `aud` is not `data_controller` |
| `controller_not_granted` | The consent has no grant for `data_controller` (or a single-registry consent names another controller) |
| `subject_mismatch` | `request_context.subject_id` has the type of the consent's subject (or one of its identifiers) but another value |
| `subject_not_allowed` | The subject's ID type is not allowed by the policy |
| `purpose_not_allowed` | Purpose outside the policy, or (use-case mode) not the use case's purpose |
| `use_case_not_granted` | Use-case mode: the partner has no active policy for `request_context.use_case`, or a stored consent was given for another use case |
| `consent_not_found` | Consent by lookup: no active, valid consent of that partner for the subject and use case (without a use case: with a grant for `data_controller`) |
| `partner_consent_not_accepted` | A partner-signed consent whose policy does not set `allow_partner_consents` |
| `scope_exceeds_policy` | No requested scope is permitted (empty effective scopes); in use-case mode, no `requested_scopes` |
| `validity_exceeds_policy` | Validity longer than the policy's `max_validity_duration` |
| `expired` | The consent (or consent token) is outside its validity |
| `not_yet_valid` | A stored consent whose validity has not started |
| `revoked` | The consent has been revoked |
| `unknown_consent` | `consent_id` names no consent this CM collected, or one that is not active |
| `partner_mismatch` | `consent_partner_id` is not the partner the stored consent was given to |
| `replay` | `issued_at` outside the freshness window, or a known `jti` reused for a different consent |
| `receipt_presenter_not_allowed` | `issue_receipts` from a caller that is not a configured token presenter, or token issuing is not enabled ([Exchange consent tokens](../design/exchange-consent-tokens.md)) |
| `receipt_issuer_not_trusted` | A consent token from an issuer this CM does not trust (or none configured) |
| `receipt_invalid` | A trusted issuer's consent token failed verification (signature, `alg`, claims, unknown at the issuer) |
| `presenter_mismatch` | The token's `presenter` is not the caller or not the issuer's configured presenter |
| `receipt_status_unavailable` | The token's status could not be checked at its issuer (only with the optional status check) |

## Staff endpoints

### `GET /consent/v1/decisions`

The decision log (console **Access Log**). Role `CONSENT_MANAGER_ADMIN`. Filters: `partner_id` (the partner's audience, e.g. `bank-a`), `decision` (`permit` or `deny`); `limit` (1–200, default 50).

```json
// response 200
[
  { "id": "d-5512", "consent_id": "5b0e…", "partner_id": "bank-a",
    "object_jti": "6f1c-unique-per-object", "data_controller": "farmer-registry",
    "decision": "permit", "reason_code": "ok", "detail": null, "policy_version": 4,
    "policy_id": "7d0c9a52-…", "policy_ref": "data_controller:farmer-registry",
    "receipt_jti": null, "receipt_issuer": null,
    "created_at": "2026-10-01T10:00:02Z" }
]
```

`policy_ref`, `policy_version` and `policy_id` name the Partner Management policy applied (all null when none was read). The console shows it as "Registry farmer-registry · v4" or "Use case loan-profile@1 · v1", linked to the partner in Partner Management.

### Consent verification (console **Consent Approvals**)

Assisted consents submitted from the partner portal ([Consent collection](../design/consent-collection.md)). Reading needs `CONSENT_MANAGER_APPROVER` or `CONSENT_MANAGER_ADMIN`; approving and rejecting need `CONSENT_MANAGER_APPROVER`.

| Endpoint | Does |
| --- | --- |
| `GET /consent/v1/verifications` | List requests; `status` filter (`pending_verification`, `approved`, `rejected`, `cancelled`), `limit`, `offset` |
| `GET /consent/v1/verifications/{request_id}` | One request with its evidence and the subject's national-ID login |
| `GET /consent/v1/verifications/{request_id}/evidence/{evidence_id}` | Download an uploaded file |
| `POST /consent/v1/verifications/{request_id}/approve` | `{note?, identifiers_checked}`: makes the consent active. `identifiers_checked` must be true when the request carries other subject identifiers |
| `POST /consent/v1/verifications/{request_id}/reject` | `{note}` (required) |

### Consents (console consent page)

A consent by ID, and its revocation when the subject asks the operating organisation ([Revocation](../design/consent-lifecycle.md#revocation)). Role `CONSENT_MANAGER_APPROVER` or `CONSENT_MANAGER_ADMIN`.

| Endpoint | Does |
| --- | --- |
| `GET /consent/v1/consents/{id}` | The consent: partner, subject, purpose, grants with their policy reference, validity, assurance, use case, `source`, `receipt_id`, the request it came from (`consent_request_id`) and its evidence (download through that verification), and `revocations` |
| `GET /consent/v1/consents/{id}/receipt` | The signed receipt |
| `POST /consent/v1/consents/{id}/revocations` | `{reason}` (required): revokes it on the subject's request, as the subject's own revocation; records the staff user. `409` if not active |

### Partner portal endpoints

For partner users; every call is scoped to the user's `partner_id`. Base `/consent/v1/partner-portal`.

| Endpoint | Does |
| --- | --- |
| `GET /me` | The user, partner and roles |
| `GET /access` | What the partner may ask for: its scope policies, or at an Exchange one entry per use-case policy (with the use case from the Composite) |
| `GET /request-settings` | What a new request needs: `consent_by` (`scopes` or `use_case`), required subject identifiers, national-ID login settings, and the Master Data lists `purposes` and `subject_id_types` (null = free text) |
| `POST /consent-requests` | Create a request: `subject_id`, `subject_identifiers`, `purpose` and `grants`, or at an Exchange `use_case`; `validity` |
| `GET /consent-requests`, `GET /consent-requests/{id}` | List (`status`, `limit`, `offset`) and read requests |
| `POST`, `GET`, `DELETE /consent-requests/{id}/evidence[/{evidence_id}]` | Upload (PDF, JPEG, PNG; 10 MB), download and delete the signed form |
| `POST /consent-requests/{id}/submit`, `…/cancel` | Submit for staff verification; cancel |
| `GET /subject-auth`, `POST` / `GET /consent-requests/{id}/subject-auth`, `GET /subject-auth/callback` | The subject's national-ID login: settings, start, status, and the provider's redirect |
| `GET /consents`, `GET /consents/{id}` | The partner's consents |
| `GET /consents/{id}/receipt`, `GET /consents/{id}/record` | The receipt; the [consent record](../design/consent-collection.md#the-partners-copy-of-a-consent) (ZIP) |
