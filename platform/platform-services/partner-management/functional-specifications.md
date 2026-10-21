---
description: >-
  Partner Management entities (partners, keys, access policies, requests), their
  lifecycles, and how staff onboard partners, rotate keys and change policies.
---

# Functional Specifications

## Entities

### Partner

A third party whose signatures OpenG2P modules need to verify and whose access
they need to check (see [Access policies](#access-policies)).

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
| `request_type` | One of `onboarding`, `key_update`, `policy`. |
| `description` | Free text — e.g. the reason for a rotation. |
| `proposed_keys` | Normalised keys to activate on approval. |
| `revoke_kids` | Kids to revoke on approval. Each must be a current (non-revoked) key of the partner. |
| `proposed_policies` | Policies to activate on approval (onboarding or `policy` requests). |
| `revoke_data_controllers` | Policies to revoke on approval, by data controller (`null` = the use-case policy). |
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
| Requests | Type filter | Select | All, `onboarding`, `key_update`, `policy` |
| Partners | Status filter | Select | All, `created`, `active`, `disabled` |
| Onboard / Change policy | Policy for | Select | *Data controller (registry)*, *Use cases (exchange)* |
| Onboard / Change policy | Signing algorithms | Checkbox list | The key algorithms the deployment allows |
| Onboard / Change policy | Fetch type | Select | `oneshot`, `periodic` |
| Change policy | Revoke | Checkbox (per active policy) | The partner's active policies |

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

## Access policies

An **access policy** says what a partner may ask for. Partner Management is the
one place policies are kept and approved; the modules that enforce them (for
example the Consent Manager and an Exchange's Composite) read them from PM's
partner API — see [Integration](integration.md).

### Two kinds of policy

| Kind | `data_controller` | Grants | Used by |
| --- | --- | --- | --- |
| **Scope policy** | The registry's data controller ID (e.g. `farmer-registry`) | `allowed_data_scopes` — the registry's scopes the partner may receive (required, non-empty) | The Consent Manager of that registry, for every consent and query from the partner |
| **Use-case policy** | `null` | `allowed_use_cases` — published use cases as `name@major` (e.g. `loan-profile@1`) (required, non-empty) | An Exchange: its Composite and its Consent Manager |

A scope policy must not list use cases, and a use-case policy must not list scopes.

### Fields

| Field | Meaning |
| --- | --- |
| `allowed_purposes` | Purposes the partner may ask consent for. Empty = any. |
| `allowed_subject_id_types` | ID types the partner may identify a person by. Empty = any. |
| `allowed_signing_algs` | Algorithms the partner may sign with. At least one, from PM's key algorithms (`EdDSA`, `ES256`, `RS256`) as narrowed by `crypto_allowed_algorithms`. Default `EdDSA`, `ES256`. |
| `max_validity_duration` | Longest consent the partner may ask for (ISO-8601, e.g. `P1Y`). Empty = no limit. |
| `fetch_type` | `oneshot` (default) or `periodic`. |
| `max_fetch_frequency` | How often a periodic partner may fetch (ISO-8601). Optional. |
| `data_life` | How long the partner may keep the data (ISO-8601, e.g. `P30D`). Optional. |

Lists are trimmed and blanks and duplicates dropped; durations must be longer
than zero. Each stored version also records the request that proposed it,
`created_by`, `approved_by`, `created_at` and `effective_from` (the approval time).

### Versions and statuses

A partner has at most one policy per data controller (one use-case policy, one
scope policy per registry). Each change creates a new **version** (1, 2, …):

| Status | Meaning |
| --- | --- |
| `pending` | Proposed by an open request. Not served. |
| `active` | Approved and served. At most one per (partner, data controller). |
| `superseded` | Replaced by a newer approved version. |
| `rejected` | Its request was rejected. |
| `revoked` | Withdrawn by an approved policy request; nothing replaces it. |

There is **at most one pending change** per (partner, data controller). Versions
are never deleted.

### Changing policies

Policies change only through requests, approved like any other request (role
`partner_manager`; the same person may raise and approve):

* **Onboarding request** — may carry initial policies (at most one per data
  controller). On approval the partner, its keys and each policy (version 1)
  become active.
* **Policy request** (`policy`) — for an approved (`active`) partner. Proposes
  new versions and/or revokes policies by data controller. Rules:
  * a partner still in `created` gets its policies through its onboarding
    request; a `disabled` partner must be enabled first;
  * propose or revoke at least one policy;
  * the same data controller cannot be both changed and revoked;
  * a data controller with a change already pending is refused
    (`PM-POLICY-409`: approve or reject that request first);
  * only an active policy can be revoked.

On approval each proposed version becomes `active` (the previous one
`superseded`) and each revoked policy `revoked`; on rejection the proposed
versions become `rejected`. Every step is audited (`policy.requested`,
`policy.approved`, `policy.rejected`, `policy.revoked`). API details:
[API Reference](api-reference.md).

### Partner ID convention

Modules identify the calling partner by its audience / DCI `sender_id` and map
it to the PM partner by convention: upper-case, `-` → `_`, prefix `PARTNER_`
(`bank-a` → `PARTNER_BANK_A`). Onboard partners in PM under that ID. There is no
per-partner override.

### In the staff portal

Step by step: [Creating and Changing Policies](creating-and-changing-policies.md).

## Audit trail

Every material change is recorded twice (see Technical Architecture → Auditability):

* **Locally**, in an append-only `pm_audit_events` ledger written atomically with
  the change — actor, timestamp, action, entity, request id, before→after summary.
  Actions: `partner.created/approved/rejected/disabled/enabled`,
  `key.added/revoked`, `policy.requested/approved/rejected/revoked`,
  `request.submitted/approved/rejected`. Surfaced as a
  per-partner **History** in the admin UI.
* **Centrally**, shipped to the platform Audit Manager (config-gated,
  non-blocking) for the long-term, cross-platform forensic trail.

## Fail-closed guarantees

* Unknown partner, non-active partner, and partner-with-no-valid-keys all return
  the **same** `404 not available`, so callers cannot enumerate partner state.
* Disabling a partner removes its keys from the fetch/JWKS views immediately
  (bounded by the caller-side cache TTL).
* The same rule applies to policies: an unknown or non-active partner, or one
  with no matching active policy, returns the same `404` (`PM-POLICY-404`), and
  callers deny.
