# Functional Specifications

## Entities

### Partner

A third party whose signatures OpenG2P modules need to verify.

| Field | Notes |
| --- | --- |
| `partner_id` | Admin-supplied, unique, stable business key used to fetch keys (e.g. `PARTNER_G2P_BRIDGE`). |
| `name`, `org_name` | Display fields. |
| `description` | Free text captured at onboarding. |
| `jwks_url` | Optional well-known JWKS endpoint keys may be imported from. |
| `status` | `created` → `active` → `disabled`. |
| `created_by`, `approved_by` | Audit: staff identity behind each transition. |

### Partner key

| Field | Notes |
| --- | --- |
| `kid` | Key ID. Defaults to the key fingerprint when omitted. |
| `algorithm` | `RS256`, `ES256`, or `EdDSA`. |
| `public_key` | Canonical PEM (SubjectPublicKeyInfo), regardless of input format. |
| `key_fingerprint` | SHA-256 of the DER SPKI; used for dedup and display. |
| `status` | `active` or `revoked` (never hard-deleted, for audit). |
| `not_before`, `not_after` | Optional validity window. |

`(partner_id, kid)` is unique. **Multiple active keys** are allowed per partner.

### Request

The admin-facing workflow record.

| Field | Notes |
| --- | --- |
| `request_type` | `onboarding` or `key_update`. |
| `description` | Free text — e.g. the reason for a rotation. |
| `proposed_keys` | Normalised keys to activate on approval. |
| `revoke_kids` | Existing kids to revoke on approval. |
| `status` | `created` → `approved` / `rejected`. |
| `submitted_by`, `reviewed_by`, `review_notes` | Audit. |

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
