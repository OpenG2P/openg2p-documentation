---
description: >-
  The origination API: create a consent request, bind an authentication
  context from an OIDC ID token, approve or deny, and revoke. Runs on the
  beneficiary API (off by default).
---

# Consent Lifecycle API

Endpoints for the **origination** flow, where the CM collects consent itself. Flow and rules:
[Consent lifecycle](../design/consent-lifecycle.md). They run on the **beneficiary API**, off by
default. (Assisted consent through the partner portal uses the
[partner portal endpoints](README.md#partner-portal-endpoints) instead.)

**Auth:** Keycloak bearer token. **Base path:** `/consent/v1`. Errors: `{"error": "<message>"}`.

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
{ "id": "3c9d…", "subject_id_type": "national_id", "subject_id_value": "FARMER_1234",
  "partner_id": "bank-a", "controller_id": "farmer-registry",
  "purpose": { "code": "share_farm_profile", "text": "..." },
  "requested_scopes": ["farmer-registry.personal_details", "farmer-registry.main_crops"],
  "grants": null, "use_case": null, "status": "pending",
  "valid_from": "2025-05-01T12:00:00Z", "valid_until": "2026-05-01T12:00:00Z",
  "created_at": "2025-05-01T11:55:00Z" }
```

For a grants request `controller_id` is null (several grants), `requested_scopes` is the union, and
`grants` lists each with its policy reference.

`422` if a requested scope is outside the partner's policy (`scope_exceeds_policy for
data_controller '…'`) or the partner has no active policy for a requested controller; `503` if
Partner Management cannot be reached.

**By use case (exchange role).** On a CM in the [exchange role](../design/exchange-consent-tokens.md),
a request **must** name a `use_case` (`name@major`) and nothing else to share (without it: `400`;
with `grants`, `data_controller` or `requested_scopes` beside it: `422`). The partner must have a
policy for that use case in Partner Management (else `422` `use_case_not_granted`). The grants and
the purpose are the use case's, read from the Composite; `purpose`, if sent, must be the use case's.
That policy's purposes, subject ID types and longest validity apply. On approval each grant is
narrowed to the use case's scopes at that time; the consent serves only that use case. `503` if the
Composite cannot be reached. Outside the exchange role, `use_case` is refused (`422`).

```json
{ "subject_id": { "type": "FAYDA_FAN", "value": "1234567890" },
  "partner_id": "bank-a", "use_case": "loan-profile@1" }
```

## `GET /consent-requests/{request_id}`

The request, as created, with its current status (`pending`, `approved`, `denied`). `404` if unknown.

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

`401` if the token fails validation (`ID token validation failed: …`); `403` if its subject is not
the request's; `409` if the request is not `pending`.

## `POST /consent-requests/{request_id}/approve`

Approve the request, choosing which scopes to grant. Requires an auth context. The CM stores the
consent and signs its receipt, and returns the consent.

```json
// request — one controller
{ "granted_scopes": ["farmer-registry.personal_details", "farmer-registry.main_crops"] }
// request — a grants request: the subject approves per registry
{ "grants": [ { "data_controller": "farmer-registry", "data_scopes": ["farmer-registry.personal_details"] } ] }
// response 201: the consent, as in GET /my/consents
{ "id": "5b0e…", "consent_id": "5b0e…", "partner_id": "bank-a",
  "controller_id": "farmer-registry",
  "effective_data_scopes": ["farmer-registry.personal_details", "farmer-registry.main_crops"],
  "status": "active", "source": "originated", "valid_until": "2026-05-01T12:00:00Z", "...": "..." }
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

The consent's receipt is at [`GET /consent/v1/receipts/{receipt_id}`](verification-api.md) (partner
API) and [`GET /my/receipts/{receipt_id}`](subject-api.md).

## `POST /consent-requests/{request_id}/deny`

Deny the request. No artefact or receipt is created.

```json
// request
{ "reason": "subject declined" }
// response 200: the request, with "status": "denied"
```

## `POST /consent/v1/consents/{consent_id}/revoke`

Revoke an active consent, for the controller or partner (`originated_by`, default `controller`);
subjects use the [Subject API](subject-api.md). Writes a revocation record.

```json
// request
{ "reason": "partnership ended", "originated_by": "controller" }
// response 200
{ "consent_id": "CONSENT-123456", "status": "revoked", "revoked_at": "2025-07-01T10:00:00Z" }
```

`409` if the consent is already `revoked` or `expired`; `404` if unknown.

## Expiry

There is no expiry endpoint: a CronJob marks consents past `valid_until` as `expired`, and
`/validate` checks validity itself ([Consent lifecycle](../design/consent-lifecycle.md#expiry)).
