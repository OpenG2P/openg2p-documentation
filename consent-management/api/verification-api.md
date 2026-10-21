---
description: >-
  The primary, machine-to-machine API — validate a consent (by ID, by lookup,
  or a partner-signed object), check consent status, fetch a signed receipt,
  and read the CM's public keys.
---

# Verification API

The hot path used by the registry (and any PEP) to authorise outbound data sharing. See
[Verification &amp; enforcement](../design/verification-and-enforcement.md) for the flow and
[API conventions](README.md) for auth and reason codes.

**Audience:** **partner-api** — the CM **PDP** deployment. There is **no Keycloak** on this path;
its callers are registries and the Composite inside the cluster, over **Istio mTLS**. A consent is
one the CM holds (by `consent_id`, or found by [lookup](#consent-by-lookup)) or a
**partner-signed consent object**, whose JWS signature is verified against the partner's keys in
**Partner Management (PM)** and replay-guarded by its `jti` (per data controller). The partner's
access policy is read from PM
([Partner Management integration](../design/partner-management-integration.md)).

## `POST /consent/v1/validate`

Validate a consent **for one data controller** (the calling registry) and return a decision with
the effective data scopes. The consent is named by `consent_id`, sent as a partner-signed
`consent_jws`, or neither ([lookup](#consent-by-lookup)).

**Auth:** **none** — no bearer token. Istio mTLS authenticates the caller↔CM transport; a
partner-signed consent object is verified with PM keys.

**Request**

A partner-signed `consent_jws` is a **compact JWS** (RFC 7515): `base64url(header).base64url(payload).base64url(signature)`.
The payload holds the consent claims; the protected header carries `alg` + `kid`. The CM verifies it
against the partner's Partner-Management key referenced by `kid`.

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
| `issue_receipts` | no (default `false`) | **Exchange role only** ([Exchange consent tokens](../design/exchange-receipts.md)). On permit, also return one signed consent token per granted controller (or only `data_controller`, if sent). Allowed only when `partner_id` is a configured token presenter, else deny `receipt_presenter_not_allowed` |

`consent_jws` may also be a **consent token** (header `typ: consent-token+jwt`; the earlier `consent-receipt+jwt` is still recognised) from an Exchange
CM. It is accepted only when its issuer is configured as trusted on this CM (department role); then
`data_controller` must be the token's `aud` and `partner_id` its `presenter`. See
[Department role: accepting](../design/exchange-receipts.md#department-role-accepting).

A **partner-signed** `consent_jws` is accepted only when the applicable policy (the scope policy for
`data_controller`, or in use-case mode the use case's policy) sets `allow_partner_consents`; else
`partner_consent_not_accepted`. Consents this CM holds (`consent_id`, lookup) and consent tokens are
not affected.

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

How the controller is resolved:

* **Consent with `grants`:** `data_controller` is **required** (missing → `malformed_object`) and
  selects the grant; no grant for it → `controller_not_granted`.
* **Single-registry consent:** `data_controller` is optional; if given it must equal the consent's
  (else `controller_not_granted`). Registries that do not send it keep working unchanged.
* The partner (`aud`, PM partner `PARTNER_<AUD>`) must have an **active policy for that
  controller in Partner Management** (else `unknown_partner`; PM unreachable with nothing cached →
  `policy_unavailable`). A partner has one scope policy per controller.
* **Effective scopes = the grant's `data_scopes` ∩ that policy's `allowed_data_scopes`** (∩
  `requested_scopes` if sent). In use-case mode the ceiling is `requested_scopes` instead.

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

`subject_id` is the **consent's** subject: the registry checks it against what it actually searches.
`data_controller` is the controller the decision was made for (also set on a deny, when known).
`policy_ref`, `policy_version` and `policy_id` name the Partner Management policy applied: its key
(`data_controller:<registry>`, or `use_case:<name@major>` in use-case mode), version and PM's id of
that version.

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
`receipts`, one consent token (compact JWS) per controller ([token format](../design/exchange-receipts.md#consent-token)).
With one controller the other fields are that controller's decision; with several, they hold the
common `subject_id` and the earliest `valid_until`. If any controller denies, that deny is returned
and no consent tokens are issued. `receipts` is `null` on every other response.

```json
{
  "decision": "permit",
  "reason_code": "ok",
  "subject_id": { "type": "NATIONAL_ID", "value": "1234567890123456" },
  "valid_until": "2027-10-01T00:00:00Z",
  "receipts": {
    "farmer-registry": "eyJhbGciOiJFZERTQSIsImtpZCI6ImNtLTIwMjUtMDEiLCJ0eXAiOiJjb25zZW50LXJlY2VpcHQrand0In0…",
    "crop-sown-registry": "eyJhbGciOiJFZERTQSIs…"
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

A caller may send **neither** `consent_jws` nor `consent_id`: the CM finds the consent itself, so the
partner need not hold or forward any consent ID. Two forms: with a use case (the Composite) and
without (a registry).

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

* Only for a configured token presenter with `consent_partner_id`, `request_context.use_case` and
  `request_context.subject_id`; otherwise `malformed_object`.
* The CM searches the consents it holds — collected through it, or partner-signed consents already
  validated in use-case mode — for that partner, subject (`type` and `value`: the consent's subject or one of its `subject_identifiers`) and use case, active
  and valid now. Several → the latest `valid_until` (tie: the newest). None → `consent_not_found`.
* The consent found is then validated exactly as one sent by `consent_id`; the response and the
  decision log carry its `consent_id`.

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

* `partner_id`, `data_controller` and `request_context.subject_id` are required; otherwise
  `malformed_object`. `requested_scopes` is optional.
* The CM searches the consents it holds — collected through it, or partner-signed consents already
  validated — for that partner, subject (`type` and `value`: the consent's subject or one of its `subject_identifiers`) and a grant for `data_controller`,
  active and valid now. Same selection: the latest `valid_until` (tie: the newest). None →
  `consent_not_found`.
* The consent found is then validated as one sent by `consent_id`: effective scopes = the
  consent's grant ∩ the partner's scope policy for that registry (∩ `requested_scopes`). The
  decision carries its `consent_id`.
* Consents given for a use case are not found (they serve only that use case).
* Types are matched as spelled, with no aliasing: the registry maps its own identifier type names
  (e.g. DCI `UIN`) to the consent's (`FAYDA_FAN`). It may search by another identifier the consent
  carries, e.g. the Crop Sown Registry by `FARMER_ID` for a `FAYDA_FAN` consent.

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

## `GET /consent/v1/receipts/{jti}/status`

Status of a consent token this CM issued in the **exchange role** (with `issue_receipts`). A
department CM calls it only if its optional token status check is on (off by default,
[why](../design/exchange-receipts.md#department-role-accepting)).

**Auth:** none (partner API; Istio mTLS at transport). **Response (HTTP 200)**

```json
{ "jti": "0b6d1f0e-5c1e-4c1a-9d7e-2f1f6c8a9b10", "status": "active", "checked_at": "2026-10-01T10:00:05Z" }
```

`status` ∈ `active | revoked | expired`: `revoked` when the token's consent (the Exchange CM's
artefact for that registry) is revoked, `expired` after the token's `exp` or the consent's expiry.
A `404` means this CM issued no such consent token.

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
denials are `unknown_partner`, `policy_unavailable`, `signature_invalid`, `audience_mismatch`, `controller_not_granted`,
`subject_mismatch`, `purpose_not_allowed`, `scope_exceeds_policy`, `expired`, `revoked`, and
`replay`. In use-case mode, also `use_case_not_granted`; for a lookup, `consent_not_found`; for a partner-signed consent its policy does not accept, `partner_consent_not_accepted`. With the Agri Stack Exchange settings on, also `receipt_presenter_not_allowed`,
`receipt_issuer_not_trusted`, `receipt_invalid`, `presenter_mismatch` and
`receipt_status_unavailable` (only with the optional token status check).
