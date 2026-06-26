---
description: >-
  The origination API — create a consent request, bind an authentication
  context from an OIDC ID token, approve or deny, and revoke.
---

# Consent Lifecycle API

Endpoints for the secondary **origination** flow, where OpenG2P collects consent directly. See
[Consent lifecycle](../design/consent-lifecycle.md) for the flow and rules.

**Auth:** origination client credentials; the `authenticate` and `approve` steps additionally
require the subject's authentication. **Base path:** `/consent/v1`.

## `POST /consent-requests`

Create a pending consent request. Validated against the partner policy up front.

```json
// request
{ "subject_id": { "type": "national_id", "value": "FARMER_1234" },
  "partner_id": "8c0b...", "purpose": { "code": "share_farm_profile", "text": "..." },
  "requested_scopes": ["farmer_profile.basic", "farmer_profile.crops"],
  "validity": { "valid_from": "2025-05-01T12:00:00Z", "valid_until": "2026-05-01T12:00:00Z" } }
// response 201
{ "request_id": "req-123", "status": "pending", "created_at": "2025-05-01T11:55:00Z" }
```

Returns `422` with `scope_exceeds_policy` / `validity_exceeds_policy` if the request can never be
satisfied under the partner's policy.

## `GET /consent-requests/{request_id}`

Return the request and its current status (`pending` / `approved` / `denied` / `expired`).

## `POST /consent-requests/{request_id}/authenticate`

Bind an authentication context by submitting the subject's OIDC ID token. The CM validates the
signature and claims against the IdP JWKS and stores only the token hash.

```json
// request
{ "id_token": "eyJ...JWS..." }
// response 200
{ "request_id": "req-123", "auth_context_id": "ac-456", "token_validated": true,
  "auth_method": "otp" }
```

Returns `401` with `signature_invalid` / `audience_mismatch` / `expired` if the token fails
validation.

## `POST /consent-requests/{request_id}/approve`

Approve the request, choosing which scopes to grant. Requires an existing auth context. The CM
issues a signed artefact + receipt.

```json
// request
{ "granted_scopes": ["farmer_profile.basic", "farmer_profile.crops"] }
// response 201
{ "consent_id": "CONSENT-123456", "receipt_id": "RECEIPT-998877",
  "effective_data_scopes": ["farmer_profile.basic", "farmer_profile.crops"],
  "status": "active", "valid_until": "2026-05-01T12:02:10Z" }
```

* `granted_scopes` must be a subset of the request's `requested_scopes`; the CM further intersects
  with policy to compute `effective_data_scopes`.
* `409` if the request is not `pending`; `412` if no auth context exists.

## `POST /consent-requests/{request_id}/deny`

Deny the request. No artefact or receipt is created.

```json
// request
{ "reason": "subject declined" }
// response 200
{ "request_id": "req-123", "status": "denied" }
```

## `POST /consent/v1/consents/{consent_id}/revoke`

Revoke an active consent (callable by controller/partner integrations; subjects use the
[Subject API](subject-api.md)). Writes an append-only revocation record and enqueues
notifications.

```json
// request
{ "reason": "partnership ended", "originated_by": "controller" }
// response 200
{ "consent_id": "CONSENT-123456", "status": "revoked", "revoked_at": "2025-07-01T10:00:00Z" }
```

`409` if the consent is already `revoked` or `expired`.

## Expiry

Expiry is automatic — a scheduled job moves artefacts past `valid_until` to `expired` and notifies
the subject; validation also lazily treats them as expired. There is no expiry endpoint.
