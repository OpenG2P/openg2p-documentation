---
description: >-
  The partner API, used by registries and the Composite: validate a consent
  (by ID, by lookup, a partner-signed object or a consent token), consent and
  consent-token status, signed receipts, and the CM's public keys.
---

# Verification API

The hot path a registry (or any PEP) uses before releasing data. The checks and their order:
[Verification &amp; enforcement](../design/verification-and-enforcement.md). Reason codes:
[API Reference](README.md#shared-reason-codes).

**Audience:** the **partner** API. **No auth**: callers (registries, the Composite) reach it in
cluster over Istio mTLS.

## `POST /consent/v1/validate`

Validate a consent **for one data controller** (the calling registry) and return a decision with
the effective data scopes. The consent is named by `consent_id`, sent as a partner-signed
`consent_jws`, or neither ([lookup](#consent-by-lookup)).

**Request**

| Field | Required | Meaning |
| --- | --- | --- |
| `consent_jws` | one of these, or neither ([lookup](#consent-by-lookup)) | The partner-signed consent, forwarded verbatim |
| `consent_id` | | A consent this CM holds (collected through it), by ID. Not with `consent_jws` |
| `consent_partner_id` | with `consent_id`, and for a use-case lookup | The partner the consent was given to (its audience, e.g. `bank-a`); another → `partner_mismatch` |
| `partner_id` | no | The caller (a registry sends the DCI `sender_id`). Traceability only, except for a consent-token presenter: it identifies the presenter for `issue_receipts`, use-case mode and consent tokens. The partner is keyed off `aud`. In a [lookup without use case](#consent-by-lookup), the partner whose consent is looked up |
| `data_controller` | when the consent has `grants`, and for a lookup without use case | The **calling registry**. Selects that registry's grant in the consent |
| `request_context.requested_scopes` | no (yes in use-case mode) | Narrows the effective scopes further; in use-case mode, the use case's scopes |
| `request_context.subject_id` | for a lookup | The subject about to be searched. Same `type` as the consent subject but a different `value` → `subject_mismatch`; the same holds for the consent's other identifiers (`subject_identifiers`, e.g. `FARMER_ID`). A lookup matches it to the consent's subject or one of those identifiers, `type` spelled exactly |
| `request_context.use_case` | no | **Use-case mode** (Exchange): the use case the caller serves, `name@major` (e.g. `loan-profile@1`). Applies only when `partner_id` is a configured token presenter; ignored otherwise. The consenting partner's policy for this use case applies; none → `use_case_not_granted` ([use-case mode](../design/verification-and-enforcement.md#use-case-mode)) |
| `request_context.purpose` | no | Use-case mode: the purpose the use case serves; the consent's `purpose.code` must equal it, else `purpose_not_allowed` |
| `issue_receipts` | no (default `false`) | **Exchange role only** ([Exchange consent tokens](../design/exchange-consent-tokens.md)). On permit, also return one signed consent token per granted controller (or only `data_controller`, if sent). Allowed only when `partner_id` is a configured token presenter, else deny `receipt_presenter_not_allowed` |

`consent_jws` may also be a **consent token** (header `typ: consent-token+jwt`, or the earlier
`consent-receipt+jwt`) from a trusted Exchange CM; then `data_controller` must be the token's `aud`
and `partner_id` its `presenter` ([Department role](../design/exchange-consent-tokens.md#department-role-accepting)).
A partner-signed `consent_jws` is accepted only when the applicable policy sets
`allow_partner_consents`.

**Consent claims** (the payload of a partner-signed compact JWS, RFC 7515; the protected header
carries `alg` and `kid`): `jti`, `aud`, `subject_id {type, value}`, `purpose {code, text}`,
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
  "aud": "bank-a",
  "subject_id": { "type": "national_id", "value": "1234567890123456" },
  "purpose": { "code": "credit_scoring", "text": "Farm loan eligibility" },
  "grants": [
    { "data_controller": "farmer-registry", "data_scopes": ["farmer-registry.personal_details", "farmer-registry.land"] },
    { "data_controller": "crop-sown-registry", "data_scopes": ["crop-sown-registry.crop_season", "crop-sown-registry.measures"] }
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
  "partner_id": "bank-a",
  "data_controller": "farmer-registry",
  "request_context": {
    "requested_scopes": ["farmer-registry.personal_details", "farmer-registry.land"],
    "subject_id": { "type": "national_id", "value": "1234567890123456" }
  }
}
```

For a consent with `grants`, `data_controller` is required and selects the grant; for a
single-registry consent it is optional and must equal the consent's. Effective scopes = the grant ∩
the partner's policy for that registry (∩ `requested_scopes`).

**Response — permit (HTTP 200)**

```json
{
  "decision": "permit",
  "consent_id": "CONSENT-123456",
  "receipt_id": "RECEIPT-998877",
  "subject_id": { "type": "national_id", "value": "1234567890123456" },
  "data_controller": "farmer-registry",
  "effective_data_scopes": ["farmer-registry.personal_details", "farmer-registry.land"],
  "valid_until": "2027-10-01T00:00:00Z",
  "policy_version": 3,
  "policy_id": "7d0c9a52-…",
  "policy_ref": "data_controller:farmer-registry",
  "reason_code": "ok",
  "evaluated_at": "2026-10-01T10:00:02Z"
}
```

`subject_id` is the **consent's** subject: the registry checks it against what it searches.
`data_controller` is the controller the decision was made for (also on a deny, when known).
`policy_ref`, `policy_version` and `policy_id` name the Partner Management policy applied. For a
consent the CM holds, or with `issue_receipts`, a permit also carries `grants`:
`{data_controller: effective scopes}`.

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

**Response — permit with consent tokens** (`issue_receipts: true`, exchange role). The response gains
`receipts`, one consent token (compact JWS) per controller ([token format](../design/exchange-consent-tokens.md#consent-token)).
With one controller the other fields are that controller's decision; with several, they hold the
common `subject_id` and the earliest `valid_until`. If any controller denies, that deny is returned
and no consent tokens are issued. `receipts` is `null` on every other response.

```json
{
  "decision": "permit",
  "reason_code": "ok",
  "subject_id": { "type": "national_id", "value": "1234567890123456" },
  "valid_until": "2027-10-01T00:00:00Z",
  "receipts": {
    "farmer-registry": "eyJhbGciOiJFZERTQSIs…",
    "crop-sown-registry": "eyJhbGciOiJFZERTQSIs…"
  },
  "grants": {
    "farmer-registry": ["farmer-registry.personal_details"],
    "crop-sown-registry": ["crop-sown-registry.crop_season"]
  },
  "evaluated_at": "2026-10-01T10:00:02Z"
}
```

**Request — use-case mode** (the Composite at the Exchange). The Composite names the use case and
its purpose; the CM applies the consenting partner's policy for that use case and limits each registry's
scopes to `requested_scopes`.

```json
{
  "consent_jws": "eyJhbGciOiJFZERTQSIs…",
  "partner_id": "agri-composite",
  "issue_receipts": true,
  "request_context": {
    "use_case": "loan-profile@1",
    "purpose": "credit-assessment",
    "requested_scopes": ["farmer-registry.personal_details", "crop-sown-registry.crop_season"],
    "subject_id": { "type": "national_id", "value": "1234567890123456" }
  }
}
```

### Consent by lookup

A caller may send **neither** `consent_jws` nor `consent_id`: the CM finds the consent it holds.
Two forms: with a use case (the Composite) and without (a registry).

**With a use case** (the Composite at an Exchange):

```json
{
  "partner_id": "agri-composite",
  "consent_partner_id": "bank-a",
  "issue_receipts": true,
  "request_context": {
    "subject_id": { "type": "FAYDA_FAN", "value": "1234567890123456" },
    "use_case": "loan-profile@1",
    "purpose": "credit-assessment",
    "requested_scopes": ["farmer-registry.personal_details", "crop-sown-registry.crop_season"]
  }
}
```

Only for a configured token presenter with `consent_partner_id`, `request_context.use_case` and
`request_context.subject_id`; otherwise `malformed_object`.

**Without a use case** (a registry, when the partner's search carries no consent):

```json
{
  "partner_id": "bank-a",
  "data_controller": "farmer-registry",
  "request_context": {
    "subject_id": { "type": "FAYDA_FAN", "value": "1234567890123456" },
    "requested_scopes": ["farmer-registry.personal_details"]
  }
}
```

`partner_id`, `data_controller` and `request_context.subject_id` are required; otherwise
`malformed_object`. `requested_scopes` is optional.

In both forms the subject matches the consent's subject or one of its `subject_identifiers`, type
spelled exactly. Which consent is picked, and how it is then checked:
[Verification & enforcement](../design/verification-and-enforcement.md#consent-by-lookup-at-a-registry).
The decision carries the `consent_id` used; none found → `consent_not_found`.

**Idempotency is per (`jti`, `data_controller`)**: a repeat of the same signed consent by the
same registry returns its stored decision; another registry gets its own `consent_id` and receipt.

## `GET /consent/v1/consents/{consent_id}/status`

A lightweight, OCSP-like status check for enforcement points that cache decisions.

**Auth:** none (Istio mTLS at transport). **Response (HTTP 200)**

```json
{ "consent_id": "CONSENT-123456", "status": "active",
  "valid_until": "2026-05-01T12:02:10Z", "checked_at": "2025-06-01T09:00:00Z" }
```

`status` ∈ `active | revoked | expired`. A `404` means no such consent.

## `GET /consent/v1/receipts/{jti}/status`

Status of a consent token this CM issued in the **exchange role** (with `issue_receipts`). A
department CM calls it only if its optional token status check is on (off by default,
[why](../design/exchange-consent-tokens.md#department-role-accepting)).

**Auth:** none (partner API; Istio mTLS at transport). **Response (HTTP 200)**

```json
{ "jti": "0b6d1f0e-5c1e-4c1a-9d7e-2f1f6c8a9b10", "status": "active", "checked_at": "2026-10-01T10:00:05Z" }
```

`status` ∈ `active | revoked | expired`: `revoked` when the token's consent (the Exchange CM's
artefact for that registry) is revoked, `expired` after the token's `exp` or the consent's expiry.
A `404` means this CM issued no such consent token.

## `GET /consent/v1/receipts/{receipt_id}`

Fetch the signed [Consent Receipt](../design/data-model.md#consent-receipt-kantara-iso-27560).

**Auth:** none (in cluster; the signature makes it self-verifying). **Response:** the receipt JSON-LD
document (HTTP 200) or `404`. A receipt carries `data_controllers` (one entry per controller it covers) beside
`data_controller`; a receipt from `/validate` covers exactly the one registry that validated.

## `GET /.well-known/jwks.json`

The CM's public signing key, for receipts and consent tokens. Routed from outside the cluster.

**Response (HTTP 200)**

```json
{ "keys": [
  { "kty": "OKP", "crv": "Ed25519", "kid": "cm-2025-01", "x": "BASE64URL(...)", "use": "sig" }
] }
```

## Reason codes

Any [shared reason code](README.md#shared-reason-codes). Consent-token codes (`receipt_*`,
`presenter_mismatch`) occur only with the Exchange settings on.
