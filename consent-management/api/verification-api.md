---
description: >-
  The primary, machine-to-machine API — validate an embedded consent object,
  check consent status, fetch a signed receipt, and read the CM's public keys.
---

# Verification API

The hot path used by the registry (and any PEP) to authorise outbound data sharing. See
[Verification &amp; enforcement](../design/verification-and-enforcement.md) for the flow and
[API conventions](README.md) for auth and reason codes.

## `POST /consent/v1/validate`

Validate a partner-embedded consent object and return a decision with the effective fields.

**Auth:** mTLS / signed service token (registry → CM).

**Request**

```json
{
  "consent_object": {
    "@type": "ConsentObject",
    "jti": "b2f1-unique",
    "subject_id": { "type": "national_id", "value": "FARMER_1234" },
    "data_controller": "my.registry.org",
    "aud": "PARTNER_SYSTEM_A",
    "purpose": { "code": "share_farm_profile", "text": "Share farmer profile with Partner A" },
    "data_scopes": ["farmer_profile.basic", "farmer_profile.crops", "farmer_profile.landholdings"],
    "fetch_type": "oneshot",
    "validity": { "valid_from": "2025-05-01T12:00:00Z", "valid_until": "2026-05-01T12:00:00Z" },
    "issued_at": "2025-05-01T11:59:50Z",
    "signature": { "algorithm": "EdDSA", "kid": "partnerA-2025-01", "value": "BASE64URL(...)" }
  },
  "partner_id": "PARTNER_SYSTEM_A",
  "request_context": {
    "requested_scopes": ["farmer_profile.basic", "farmer_profile.crops"],
    "subject_id": { "type": "national_id", "value": "FARMER_1234" }
  }
}
```

**Response — permit (HTTP 200)**

```json
{
  "decision": "permit",
  "consent_id": "CONSENT-123456",
  "receipt_id": "RECEIPT-998877",
  "subject_id": { "type": "national_id", "value": "FARMER_1234" },
  "effective_data_scopes": ["farmer_profile.basic", "farmer_profile.crops"],
  "valid_until": "2026-05-01T12:02:10Z",
  "policy_version": 3,
  "reason_code": "ok",
  "evaluated_at": "2025-05-01T12:02:12Z"
}
```

**Response — deny (HTTP 200)**

```json
{
  "decision": "deny",
  "reason_code": "scope_exceeds_policy",
  "detail": "'farmer_profile.landholdings' is not permitted by the partner policy",
  "policy_version": 3,
  "evaluated_at": "2025-05-01T12:02:12Z"
}
```

> Both outcomes return HTTP 200 so the PEP can read `reason_code`. Transport/auth failures use the
> usual 4xx/5xx. The registry releases data **only** when `decision == "permit"`, and only the
> fields in `effective_data_scopes`.

## `GET /consent/v1/consents/{consent_id}/status`

A lightweight, OCSP-like status check for enforcement points that cache decisions.

**Auth:** mTLS / service token. **Response (HTTP 200)**

```json
{ "consent_id": "CONSENT-123456", "status": "active",
  "valid_until": "2026-05-01T12:02:10Z", "checked_at": "2025-06-01T09:00:00Z" }
```

`status` ∈ `active | revoked | expired`. A `404` means no such consent.

## `GET /consent/v1/receipts/{receipt_id}`

Fetch the signed [Consent Receipt](../design/data-model.md#consent-receipt-kantara-iso-27560).

**Auth:** public read (the signature is self-verifying). **Response:** the receipt JSON-LD
document (HTTP 200) or `404`.

## `GET /.well-known/jwks.json`

The CM's signing public keys, so any party can verify receipts independently.

**Response (HTTP 200)**

```json
{ "keys": [
  { "kty": "OKP", "crv": "Ed25519", "kid": "registry-2025-01", "x": "BASE64URL(...)", "use": "sig" }
] }
```

## Reason / error codes

This endpoint can return any [shared reason code](README.md#shared-reason-codes). The common
denials are `unknown_partner`, `signature_invalid`, `audience_mismatch`, `purpose_not_allowed`,
`scope_exceeds_policy`, `expired`, `revoked`, and `replay`.
