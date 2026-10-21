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

Create a pending consent request. `partner_id` is the partner's **audience** (e.g. `bank-a`).
Validated up front against the partner's active policy in Partner Management **for each
controller**.

Give **exactly one** of:

* `data_controller` + `requested_scopes` — one controller; or
* `grants: [{data_controller, data_scopes}]` — several controllers (one consent, one grant per
  registry). A controller may appear once; `data_controller` is not sent beside `grants`.

```json
// request — one controller
{ "subject_id": { "type": "national_id", "value": "FARMER_1234" },
  "partner_id": "bank-a", "data_controller": "farmer-registry",
  "purpose": { "code": "share_farm_profile", "text": "..." },
  "requested_scopes": ["farmer-registry.personal_details", "farmer-registry.main_crops"],
  "validity": { "valid_from": "2025-05-01T12:00:00Z", "valid_until": "2026-05-01T12:00:00Z" } }
// request — one grant per registry
{ "subject_id": { "type": "national_id", "value": "FARMER_1234" },
  "partner_id": "bank-a", "purpose": { "code": "credit_scoring", "text": "..." },
  "grants": [
    { "data_controller": "farmer-registry", "data_scopes": ["farmer-registry.personal_details"] },
    { "data_controller": "crop-sown-registry", "data_scopes": ["crop-sown-registry.crop_season"] }
  ] }
// response 201
{ "request_id": "req-123", "status": "pending", "created_at": "2025-05-01T11:55:00Z" }
```

The response also echoes `controller_id` (null when there are several grants), `requested_scopes`
(the union, for a grants request) and `grants`.

Returns `422` with `scope_exceeds_policy` if the request can never be satisfied under the
partner's policy (naming the controller), or if the partner has no active policy in Partner
Management for a requested controller; `503` if Partner Management cannot be reached.

**By use case (exchange role).** On a CM in the [exchange role](../design/exchange-receipts.md),
a request **must** name a `use_case` (`name@major`) and no grants: the consent is made for that
use case. A request with `grants` or `data_controller` + `requested_scopes` is refused (`400`, "at
the Exchange, consents are made for a use case"). The partner must have a policy for that use case in
Partner Management — one policy per use case (else `422` `use_case_not_granted`); the grants (each
registry with the use case's scopes) and the purpose are the use case's, read from the Composite;
`purpose`, if sent, must be the use case's. That policy's purposes, subject ID types and longest
validity apply. The request and the consent carry
`use_case`; on approval each grant is narrowed to the use case's scopes at that time, and the
consent is valid at `/validate` only for that use case. `503` if the Composite cannot be reached.

```json
{ "subject_id": { "type": "FAYDA_FAN", "value": "1234567890" },
  "partner_id": "bank-a", "use_case": "loan-profile@1" }
```

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
// request — one controller
{ "granted_scopes": ["farmer-registry.personal_details", "farmer-registry.main_crops"] }
// request — a grants request: the subject approves per registry
{ "grants": [ { "data_controller": "farmer-registry", "data_scopes": ["farmer-registry.personal_details"] } ] }
// response 201
{ "consent_id": "CONSENT-123456", "receipt_id": "RECEIPT-998877",
  "effective_data_scopes": ["farmer-registry.personal_details", "farmer-registry.main_crops"],
  "status": "active", "valid_until": "2026-05-01T12:02:10Z" }
```

* Give exactly one of `granted_scopes` or `grants`. `granted_scopes` must be a subset of the
  request's `requested_scopes`; the CM further intersects with policy to compute
  `effective_data_scopes`.
* For a grants request, each approved grant must be within that controller's requested scopes,
  and is narrowed to the partner's current policy for that controller. A controller left out (or with no scopes
  left) is **declined**. `granted_scopes` on a grants request applies the same list to every
  grant. `400` if nothing is left. The artefact holds the approved grants (with each one's
  `effective_data_scopes` and policy reference: `policy_ref`, `policy_version`, `policy_id`) and the receipt lists one `data_controllers`
  entry per grant.
* `409` if the request is not `pending`; `412` if no auth context exists.

An originated consent is used at `/validate` by its `consent_id`, or found by lookup when the
partner sends none ([Verification API](verification-api.md#consent-by-lookup)).

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
