# Functional Specifications

## Entities

### Partner

A third party whose signatures OpenG2P modules need to verify.

| Field | Notes |
| --- | --- |
| `partner_id` | Admin-supplied, unique, stable business key used to fetch keys (e.g. `PARTNER_G2P_BRIDGE`). Free text at onboarding, but no spaces or `/`, `?`, `#`, `%` (it is a URL path segment). |
| `name`, `org_name` | Display fields. |
| `description` | Free text captured at onboarding. |
| `jwks_url` | Optional well-known JWKS endpoint keys may be imported from. Must be an `http(s)://` URL. |
| `status` | One of `created`, `active`, `disabled` (`created` → `active` → `disabled`). |
| `created_by`, `approved_by` | Audit: staff identity behind each transition. |

### Partner key

| Field | Notes |
| --- | --- |
| `kid` | Key ID. Defaults to the key fingerprint when omitted. Same character rule as `partner_id`. |
| `algorithm` | One of `RS256`, `ES256`, `EdDSA` (case-sensitive). Optional on input: omitted means *auto-detect from the key*. A deployment can narrow the list with `crypto_allowed_algorithms`. |
| `public_key` | Canonical PEM (SubjectPublicKeyInfo), regardless of input format. |
| `key_fingerprint` | SHA-256 of the DER SPKI; used for dedup and display. |
| `status` | One of `pending`, `active`, `revoked` (never hard-deleted, for audit). |
| `not_before`, `not_after` | Optional validity window. |

`(partner_id, kid)` is unique. **Multiple active keys** are allowed per partner.

### Request

The admin-facing workflow record.

| Field | Notes |
| --- | --- |
| `request_type` | One of `onboarding`, `key_update`. |
| `description` | Free text — e.g. the reason for a rotation. |
| `proposed_keys` | Normalised keys to activate on approval. |
| `revoke_kids` | Kids to revoke on approval. Each must be a current (non-revoked) key of the partner. |
| `status` | One of `created`, `approved`, `rejected` (`created` → `approved` / `rejected`). |
| `submitted_by`, `reviewed_by`, `review_notes` | Audit. |

### Allowed values in the admin UI

Every field with a fixed set of values is a select (or checkbox list) in the
admin portal, not free text, and the API rejects anything else:

| Screen | Field | Control | Allowed values |
| --- | --- | --- | --- |
| Onboard / Rotate keys | Algorithm (per key) | Select | *Auto-detect*, `RS256`, `ES256`, `EdDSA` |
| Rotate keys | Partner ID | Select (when not opened from a partner) | Existing partners |
| Rotate keys | Revoke existing keys | Checkbox list | The partner's current (non-revoked) keys |
| Onboard / Rotate keys | Import from JWKS URL | Checkbox | Enabled only when a JWKS URL is set |
| Requests | Status filter | Buttons | All, `created`, `approved`, `rejected` |
| Requests | Type filter | Select | All, `onboarding`, `key_update` |
| Partners | Status filter | Select | All, `created`, `active`, `disabled` |

The portal reads these lists from `GET /metadata` (see [API Reference](api-reference.md#get-metadata)),
which builds them from the same enums the API validates against. Partner ID,
name, organisation, description and key ID stay free text; Partner ID and key ID
show the character rule as a hint. Rows stored before this validation existed
still load and display as-is.

## Lifecycles

### Partner status

```
                 approve onboarding request
   created ─────────────────────────────────▶ active
      │                                        │  ▲
      │ reject                          disable│  │enable
      ▼                                        ▼  │
  (stays created,                           disabled
   never served)
```

* **created** — onboarded, awaiting approval. Keys are **not** served.
* **active** — approved. Active, currently-valid keys are served.
* **disabled** — turned off. Key fetch returns *not available*.

### Key status

* **active** — served while its partner is active and the current time is within
  `[not_before, not_after]`.
* **revoked** — never served; retained for audit.

### Key rotation (overlap)

1. Admin files a `key_update` request adding `key-new` and (optionally) revoking
   `key-old`.
2. On approval, `key-new` becomes active. If `key-old` is not in `revoke_kids`
   it stays active too, so both verify during the cutover.
3. A later `key_update` (or the same one) revokes `key-old`. Callers pick up the
   change within the fetch cache window.

## Key material

* **Accepted on input:** PEM (SPKI or X.509 certificate) or a JSON Web Key.
* **Stored:** canonical SPKI PEM.
* **Served:** PEM (raw fetch) and JWK (JWKS view).
* **Algorithms:** `RS256`, `ES256` (P-256), `EdDSA` (Ed25519) — the union of what
  g2p-bridge and consent-manager verify.
* **Validation:** private keys are rejected, RSA below 2048 bits is rejected, a
  declared algorithm must match the key, and disallowed algorithms are rejected.

## Well-known population

If a partner publishes a JWKS endpoint, the admin can supply `jwks_url` and tick
*import*. The service fetches it **once** and stores the resulting keys against
`partner_id` + `kid`. It does **not** live-poll the endpoint — the DB is the
source of truth.

## Audit trail

Every material change is recorded twice (see Technical Architecture → Auditability):

* **Locally**, in an append-only `pm_audit_events` ledger written atomically with
  the change — actor, timestamp, action, entity, request id, before→after summary.
  Actions: `partner.created/approved/rejected/disabled/enabled`,
  `key.added/revoked`, `request.submitted/approved/rejected`. Surfaced as a
  per-partner **History** in the admin UI.
* **Centrally**, shipped to the platform Audit Manager (config-gated,
  non-blocking) for the long-term, cross-platform forensic trail.

## Fail-closed guarantees

* Unknown partner, non-active partner, and partner-with-no-valid-keys all return
  the **same** `404 not available`, so callers cannot enumerate partner state.
* Disabling a partner removes its keys from the fetch/JWKS views immediately
  (bounded by the caller-side cache TTL).
