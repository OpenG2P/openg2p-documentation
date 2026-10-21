---
description: >-
  The canonical entities the Consent Manager stores, and the JSON-LD documents
  it exchanges — consent object, auth context, consent artefact, and the
  Kantara/ISO-27560-aligned consent receipt.
---

# Data model

The Consent Manager keeps two kinds of structures:

* **Stored entities** — relational records it owns (consent requests, artefacts, receipts, logs).
  Partners and their access policies are not stored here: they live in Partner Management, and
  records name the partner by its **audience** (e.g. `bank-a`) with the **policy reference** applied: `policy_ref` (its key, `kind:key` — `data_controller:farmer-registry` or `use_case:loan-profile@1`), `policy_version` and `policy_id` (PM's id of that version)
  ([Partner Management integration](partner-management-integration.md)).
* **Exchanged documents** — JSON-LD documents passed in/out (the consent object a partner embeds,
  the ID token from the IdP, and the artefact + receipt the CM issues).

All status transitions are **append-only**: a new status and timestamp are written, prior
timestamps are never overwritten, and the decision log is immutable.

## Entity overview

```mermaid
erDiagram
  CONSENT_REQUEST ||--o| AUTH_CONTEXT : "bound by (origination)"
  CONSENT_REQUEST ||--o| CONSENT_ARTEFACT : produces
  CONSENT_ARTEFACT ||--|| CONSENT_RECEIPT : "proven by"
  CONSENT_ARTEFACT ||--o{ REVOCATION_RECORD : "may be revoked by"
  CONSENT_ARTEFACT ||--o{ DECISION_LOG : "evaluated in"
```

### ConsentArtefact (CM-issued, canonical)

The CM's canonical representation of a consent decision — whether derived from the verified
claims of a partner-embedded consent JWS or produced by the origination flow.

An **embedded** consent yields **one artefact per (`jti`, `data_controller`)** — a consent with
grants for two registries, validated by both, has two artefacts (and two receipts), each revocable
on its own. An **originated** consent yields one artefact per approved request; if the request
carried grants, the approved grants are stored on it.

| Field | Type | Notes |
| --- | --- | --- |
| consent_id | UUID | Primary key |
| subject_id_type / subject_id_value | str | The data subject |
| controller_id | str | Data controller (registry). Null for an originated consent with several approved grants |
| partner_id | str | The partner the consent was given to: its audience (e.g. `bank-a`) |
| purpose | json | `{code, text}` |
| data_scopes | list[str] | Consented fields for this controller's grant (pre-policy-intersection) |
| effective_data_scopes | list[str] | `data_scopes ∩ policy.allowed_data_scopes` at issue time |
| grants | json | Originated consents only: `[{data_controller, data_scopes, granted_scopes, effective_data_scopes, policy_version, policy_id, policy_ref}]` |
| object_jti | str | The embedded consent's `jti`; unique together with `controller_id` |
| valid_from / valid_until | datetime | |
| fetch_type | enum | `oneshot`, `periodic` |
| auth_context_id | UUID | FK → AuthContext (origination) or `null` (embedded, partner-attested) |
| source | enum | `embedded` (partner-signed) or `originated` (CM-collected) |
| policy_version | int | Version of the partner's policy in Partner Management evaluated at issue |
| policy_id | str | PM's id of that policy version |
| policy_ref | str | The policy's key, `kind:key`: `data_controller:farmer-registry` or `use_case:loan-profile@1`. On an originated consent with several grants, set only when all grants share one policy (a consent by use case) |
| status | enum | `active`, `revoked`, `expired` |
| created_at / revoked_at / expired_at | datetime | Append-only |

### AuthContext (origination flow)

Created after the CM validates an ID token. The raw token is **never** persisted — only its hash.

| Field | Type | Notes |
| --- | --- | --- |
| auth_context_id | UUID | Primary key |
| consent_request_id | UUID | FK → ConsentRequest |
| auth_provider | str | e.g. `keycloak` |
| auth_method | str | `otp`, `biometric`, … (from `amr`) |
| auth_timestamp | datetime | |
| issuer | str | `iss` |
| id_token_hash | str | `sha256:…` |
| token_validated | bool | |
| verified_claims | json | `iss, sub, aud, amr, iat, exp, auth_time, kid` |

### ConsentReceipt

Kantara/ISO-27560-aligned, **signed with the CM's own `.p12` key**. The CM is self-verifying — it
publishes its signing public keys at `GET /.well-known/jwks.json`, so any party can verify a receipt
without PM. (The CM is **not** a PM partner.) See the JSON below.

| Field | Type | Notes |
| --- | --- | --- |
| receipt_id | UUID | Primary key |
| consent_id | UUID | FK → ConsentArtefact |
| artefact_hash | str | `sha256:…` over the canonical artefact |
| algorithm | enum | `EdDSA` (ed25519), `ES256`, or `RS256` — the CM `.p12` key's alg |
| kid | str | CM key id used to sign |
| signature | text | Detached/compact JWS over the artefact hash |
| version | str | Receipt schema version |
| issued_at | datetime | |

### ConsentRequest · RevocationRecord · DecisionLog

| Entity | Key fields |
| --- | --- |
| **ConsentRequest** (origination) | request_id, subject, controller_id (null when several grants), partner_id (the partner's audience), requested_scopes (union), grants (`[{data_controller, data_scopes, policy_version, policy_id, policy_ref}]` or null), purpose, status (`pending`/`approved`/`denied`/`expired`), timestamps |
| **RevocationRecord** | revocation_id, consent_id, originated_by (`subject`/`controller`/`partner`), reason, created_at |
| **DecisionLog** (immutable) | decision_id, consent_id (nullable on deny), partner_id (the partner's audience, when known), object_jti, data_controller (when known), request_ctx_hash, decision, reason_code, policy_version / policy_id / policy_ref (null when no policy was read), receipt_jti / receipt_issuer (decisions on an Exchange consent token; null otherwise), evaluated_at |
| **IssuedReceipt** (exchange role) | A consent token issued: jti, consent_id (the artefact it was issued from), data_controller, presenter, partner, expires_at — see [Exchange consent tokens](exchange-receipts.md) |

---

## Exchanged documents (JSON-LD)

### ID Token

Received from the identity provider after subject authentication (origination flow).

```json
{
  "@context": "https://openg2p.org/contexts/id_token.jsonld",
  "@type": "IDToken",
  "iss": "https://idp.example.org",
  "sub": "FARMER_1234",
  "aud": "my.registry.org",
  "amr": ["otp"],
  "iat": 1714555200,
  "exp": 1714558800,
  "auth_time": 1714555190,
  "kid": "key-2025-01",
  "signature": "BASE64URL(JWS_signature)"
}
```

### Consent object (partner-embedded, the primary flow)

The **partner signs this as a compact JWS** (RFC 7515) and embeds it in the registry request. The
claims below are the **JWS payload**; the JWS protected header carries `alg` + `kid`. The CM
recovers the claims from the payload and verifies the signature using the partner's public key
**fetched from Partner Management** (partner ID `PARTNER_<AUD>`) by the JWS `kid` (see
[Partner Management Integration](partner-management-integration.md)). `jti` + `issued_at` give
replay protection.

The data to share is given as **`grants`** — one consent, one grant per registry. The earlier
single-registry form (`data_controller` + `data_scopes` at the top level) is still accepted and
treated as one grant; a consent may not mix the two.

```json
// JWS payload (claims). Wire form: base64url(header).base64url(payload).base64url(signature)
{
  "@context": "https://openg2p.org/contexts/consent_object.jsonld",
  "@type": "ConsentObject",
  "jti": "b2f1...-unique-per-object",
  "subject_id": { "type": "national_id", "value": "FARMER_1234" },
  "aud": "bank-a",
  "purpose": { "code": "share_farm_profile", "text": "Share farmer profile with Partner A" },
  "grants": [
    { "data_controller": "farmer-registry",
      "data_scopes": ["farmer_profile.basic", "farmer_profile.crops", "farmer_profile.landholdings"] },
    { "data_controller": "crop-sown-registry", "data_scopes": ["crop_season", "crops_sown"] }
  ],
  "fetch_type": "oneshot",
  "validity": { "valid_from": "2025-05-01T12:00:00Z", "valid_until": "2026-05-01T12:00:00Z" },
  "issued_at": "2025-05-01T11:59:50Z"
}
```

There is no inline `signature` field — the JWS wrapper carries it (header `alg`/`kid` + the signature segment).

### Auth Context

Generated by the CM after validating the ID token (origination flow).

```json
{
  "@context": "https://openg2p.org/contexts/auth_context.jsonld",
  "@type": "AuthContext",
  "auth_provider": "keycloak",
  "auth_method": "otp",
  "auth_timestamp": "2025-05-01T12:01:22Z",
  "issuer": "https://idp.example.org",
  "subject_id": "FARMER_1234",
  "kid": "key-2025-01",
  "id_token_hash": "sha256:ab349faa12bc908d...",
  "token_validated": true,
  "verified_claims": {
    "iss": "https://idp.example.org", "sub": "FARMER_1234", "aud": "my.registry.org",
    "amr": ["otp"], "iat": 1714555200, "exp": 1714558800, "auth_time": 1714555190, "kid": "key-2025-01"
  }
}
```

### Consent Artefact

The CM's canonical decision document. Stored, and checked before any data is released.

```json
{
  "@context": "https://openg2p.org/contexts/consent_artefact.jsonld",
  "@type": "ConsentArtefact",
  "consent_id": "CONSENT-123456",
  "subject_id": "FARMER_1234",
  "data_controller": "farmer-registry",
  "partner_id": "bank-a",
  "source": "embedded",
  "purpose": { "code": "share_farm_profile", "text": "Share farmer profile with Partner A" },
  "data_scopes": ["farmer_profile.basic", "farmer_profile.crops", "farmer_profile.landholdings"],
  "effective_data_scopes": ["farmer_profile.basic", "farmer_profile.crops"],
  "fetch_type": "oneshot",
  "policy_version": 3,
  "policy_id": "7d0c9a52-…",
  "policy_ref": "data_controller:farmer-registry",
  "validity": { "consent_timestamp": "2025-05-01T12:02:10Z", "expiry_timestamp": "2026-05-01T12:02:10Z" },
  "auth_context": { "...": "Auth Context (origination) or omitted for partner-attested embedded consent" }
}
```

> This is the Farmer Registry's artefact for the consent above: its grant only.
> `effective_data_scopes` excludes `farmer_profile.landholdings` because the partner's policy for
> this registry did not allow it — data minimisation enforced at the point of decision. An
> originated consent with several approved grants carries them under `grants` instead.

### Consent Receipt (Kantara / ISO 27560)

Generated alongside the artefact and **signed with the CM's own `.p12` key**. It is both
cryptographic proof and a human-readable consent record for the subject, audit, and disputes.

```json
{
  "@context": "https://openg2p.org/contexts/consent_receipt.jsonld",
  "@type": "ConsentReceipt",
  "receipt_id": "RECEIPT-998877",
  "version": "1.1",
  "issued_at": "2025-05-01T12:02:12Z",
  "jurisdiction": "IN",
  "data_controller": {
    "id": "farmer-registry",
    "name": "National Farmer Registry",
    "contact": "dpo@registry.org",
    "dpo": "Data Protection Officer"
  },
  "data_controllers": [ { "id": "farmer-registry" } ],
  "subject_id": "FARMER_1234",
  "purposes": [
    { "code": "share_farm_profile", "text": "Share farmer profile with Partner A",
      "legal_basis": "consent", "retention": "P0D-after-fetch" }
  ],
  "data_categories": ["farmer_profile.basic", "farmer_profile.crops"],
  "sensitive": false,
  "third_parties": ["bank-a"],
  "withdrawal": { "method": "POST /consent/v1/consents/CONSENT-123456/revoke" },
  "consent_artefact": { "@id": "CONSENT-123456", "hash": "sha256:7b0a933e7cd398a..." },
  "signature": {
    "algorithm": "EdDSA", "kid": "registry-2025-01",
    "value": "BASE64URL(cm_private_key.sign(consent_artefact_hash))"
  }
}
```

`data_controllers` lists every controller the receipt covers: the one controller for an embedded
consent (one receipt per registry), or one entry per approved grant — `{id, data_categories}` —
for an originated consent with grants, where `data_controller` is null if there are several.

The CM publishes its signing public keys at `GET /.well-known/jwks.json` so any party can verify
a receipt independently.
