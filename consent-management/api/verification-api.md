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
against the partner's keys in **Partner Management (PM)** and replay-guarded by its `jti` (per
data controller). The
Registry↔CM transport is secured by **Istio mTLS**.

## `POST /consent/v1/validate`

Validate a partner-embedded consent object **for one data controller** (the calling registry) and
return a decision with the effective fields.

**Auth:** **none** — no bearer token. The signed consent object is the proof (verified via PM
keys); Istio mTLS authenticates the Registry↔CM transport.

**Request**

`consent_jws` is a **compact JWS** (RFC 7515): `base64url(header).base64url(payload).base64url(signature)`.
The payload holds the consent claims; the protected header carries `alg` + `kid`. The CM verifies it
against the partner's Partner-Management key referenced by `kid`.

| Field | Required | Meaning |
| --- | --- | --- |
| `consent_jws` | yes | The partner-signed consent, forwarded verbatim |
| `partner_id` | no | The caller's view of the partner (traceability only; the partner is keyed off `aud`) |
| `data_controller` | when the consent has `grants` | The **calling registry**. Selects that registry's grant in the consent |
| `request_context.requested_scopes` | no | Narrows the effective scopes further |
| `request_context.subject_id` | no | The subject about to be searched. Same `type` as the consent subject but a different `value` → `subject_mismatch` |

**Consent claims** (the JWS payload): `jti`, `aud`, `subject_id {type, value}`, `purpose {code, text}`,
`fetch_type`, `validity {valid_from, valid_until}`, `issued_at`, and the data to share in **one** of
two forms:

* `grants: [{data_controller, data_scopes}, ...]` — **one consent, one grant per registry**. A partner
  that needs data from several registries asks the subject once and lists a grant for each.
* `data_controller` + `data_scopes` — the earlier single-registry form, still accepted and treated
  as a single grant.

A consent carrying both forms, an empty `grants` list, or two grants for the same controller is
`malformed_object`.

```json
// consent claims (JWS payload) with one grant per registry
{
  "jti": "6f1c-unique-per-object",
  "aud": "PARTNER_SYSTEM_A",
  "subject_id": { "type": "fayda_fan", "value": "1234567890123456" },
  "purpose": { "code": "credit_scoring", "text": "Farm loan eligibility" },
  "grants": [
    { "data_controller": "farmer-registry", "data_scopes": ["farmer_personal_details", "land_parcels"] },
    { "data_controller": "crop-sown-registry", "data_scopes": ["crop_season", "crops_sown"] }
  ],
  "fetch_type": "oneshot",
  "validity": { "valid_from": "2026-10-01T00:00:00Z", "valid_until": "2027-10-01T00:00:00Z" },
  "issued_at": "2026-10-01T09:59:50Z"
}
```

```json
// POST /consent/v1/validate — sent by the Farmer Registry
{
  "consent_jws": "eyJhbGciOiJFZERTQSIsImtpZCI6InBhcnRuZXJBLTIwMjYtMDEifQ.eyJqdGkiOiI2ZjFjLXVuaXF1ZS...}.<signature>",
  "partner_id": "PARTNER_SYSTEM_A",
  "data_controller": "farmer-registry",
  "request_context": {
    "requested_scopes": ["farmer_personal_details", "land_parcels"],
    "subject_id": { "type": "fayda_fan", "value": "1234567890123456" }
  }
}
```

How the controller is resolved:

* **Consent with `grants`:** `data_controller` is **required** (missing → `malformed_object`) and
  selects the grant; no grant for it → `controller_not_granted`.
* **Single-registry consent:** `data_controller` is optional; if given it must equal the consent's
  (else `controller_not_granted`). Registries that do not send it keep working unchanged.
* The partner (`aud`) must have an **active binding to that controller** (else `unknown_partner`).
  A partner can be bound to several controllers, each with its own policy.
* **Effective scopes = the grant's `data_scopes` ∩ that binding's policy** (∩ `requested_scopes` if
  sent).

**Response — permit (HTTP 200)**

```json
{
  "decision": "permit",
  "consent_id": "CONSENT-123456",
  "receipt_id": "RECEIPT-998877",
  "subject_id": { "type": "fayda_fan", "value": "1234567890123456" },
  "data_controller": "farmer-registry",
  "effective_data_scopes": ["farmer_personal_details", "land_parcels"],
  "valid_until": "2027-10-01T00:00:00Z",
  "policy_version": 3,
  "reason_code": "ok",
  "evaluated_at": "2026-10-01T10:00:02Z"
}
```

`subject_id` is the **consent's** subject: the registry checks it against what it actually searches.
`data_controller` is the controller the decision was made for (also set on a deny, when known).

**Response — deny (HTTP 200)**

```json
{
  "decision": "deny",
  "reason_code": "controller_not_granted",
  "detail": "consent has no grant for data_controller 'land-registry'",
  "data_controller": "land-registry",
  "evaluated_at": "2026-10-01T10:00:02Z"
}
```

> Both outcomes return HTTP 200 so the PEP can read `reason_code`. Transport/auth failures use the
> usual 4xx/5xx. The registry releases data **only** when `decision == "permit"`, and only the
> fields in `effective_data_scopes`.

**Idempotency and replay are per (`jti`, `data_controller`).** The same consent validated by two
registries gives two decisions, two artefacts (two `consent_id`s) and two receipts; a repeat by the
same registry returns its stored decision. Revoking one registry's `consent_id` leaves the other's
in force.

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
document (HTTP 200) or `404`. A receipt carries `data_controllers` (one entry per controller it covers) beside
`data_controller`; a receipt from `/validate` covers exactly the one registry that validated.

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
denials are `unknown_partner`, `signature_invalid`, `audience_mismatch`, `controller_not_granted`,
`subject_mismatch`, `purpose_not_allowed`, `scope_exceeds_policy`, `expired`, `revoked`, and
`replay`.
