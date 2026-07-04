---
description: >-
  The primary, machine-to-machine API — validate an embedded consent object,
  check consent status, fetch a signed receipt, and read the CM's public keys.
---

# Verification API

The hot path used by the registry (and any PEP) to authorise outbound data sharing. See
[Verification &amp; enforcement](../design/verification-and-enforcement.md) for the flow and
[API conventions](README.md) for auth and reason codes.

**Audience:** **partner-api** — the CM **PDP** deployment. There is **no Keycloak** on this path.
Trust rests entirely on the **partner-signed consent object**, whose JWS signature is verified
against the partner's keys in **Partner Management (PM)** and replay-guarded by its `jti`. The
Registry↔CM transport is secured by **Istio mTLS**.

## `POST /consent/v1/validate`

Validate a partner-embedded consent object and return a decision with the effective fields.

**Auth:** **none** — no bearer token. The signed consent object is the proof (verified via PM
keys); Istio mTLS authenticates the Registry↔CM transport.

**Request**

`consent_jws` is a **compact JWS** (RFC 7515): `base64url(header).base64url(payload).base64url(signature)`.
The payload holds the consent claims (jti, subject_id, data_controller, aud, purpose, data_scopes,
fetch_type, validity, issued_at); the protected header carries `alg` + `kid`. The CM verifies it
against the partner's Partner-Management key referenced by `kid`.

```json
{
  "consent_jws": "eyJhbGciOiJFZERTQSIsImtpZCI6InBhcnRuZXJBLTIwMjUtMDEifQ.eyJqdGkiOiJiMmYxLXVuaXF1ZS...}.<signature>",
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

**Auth:** none (Istio mTLS at transport). **Response (HTTP 200)**

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
