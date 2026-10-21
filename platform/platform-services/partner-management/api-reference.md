---
description: >-
  Partner Management APIs — staff APIs for partners, keys, policies and requests,
  and the internal partner API other modules use to fetch keys and policies.
---

# API Reference

Interactive OpenAPI docs are served at `/docs` on each running service.

The endpoints are split across the two backend components:

* **staff-portal-api** serves the admin endpoints below (`/partners...`). They
  require a Keycloak **staff-realm** JWT (obtained via the shared IAM login and
  forwarded by the UI) carrying the `partner_manager` role.
* **partner-api** serves the key- and policy-fetch endpoints (`/keys...`,
  `/policies...`), which require no authentication and are exposed only on the
  internal gateway.

## Admin — requests

### `POST /partners/requests/onboarding`
Onboard a new partner and its initial key(s).

```json
{
  "partner_id": "PARTNER_G2P_BRIDGE",
  "name": "G2P Bridge",
  "org_name": "OpenG2P",
  "description": "Onboarding G2P Bridge for disbursement signing",
  "jwks_url": null,
  "import_from_jwks_url": false,
  "keys": [
    { "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----", "kid": "key-1" }
  ],
  "policies": [
    { "data_controller": "farmer-registry", "allowed_data_scopes": ["farmer-registry.land"] }
  ]
}
```

Creates the partner in `created` and a request in `created`. `policies` is
optional (any mix, at most one per data controller and one per use case); each becomes a `pending` version 1,
activated when the request is approved. Policy fields and rules:
[Access policies](functional-specifications.md#access-policies). Each key may instead
supply `jwk` (a JSON Web Key) rather than `public_key`; `kid` and `algorithm` are
optional and derived when omitted.

Validation (rejected with `400`, code `G2P-REQ-102`):

* `algorithm` — one of `RS256`, `ES256`, `EdDSA`, or omitted / `""` for auto-detect.
  A supported value that does not match the key, or one the deployment's
  `crypto_allowed_algorithms` excludes, is rejected with `PM-KEY-400`.
* `partner_id`, `kid` — no spaces or `/`, `?`, `#`, `%`.
* `jwks_url` — an `http(s)://` URL, or omitted / `""`.

Policies are also checked against the [catalogue sources](functional-specifications.md#catalogue-sources)
and the [Master Data code lists](functional-specifications.md#master-data-code-lists),
if configured (`PM-POLICY-400` for an unknown scope, use case, purpose or subject
ID type; see [`GET /catalogue`](#get-catalogue)). A signing algorithm that matches
none of the proposed keys adds a `warnings` entry.

### `POST /partners/requests/key-update`
File a key rotation/update for an existing partner.

```json
{
  "partner_id": "PARTNER_G2P_BRIDGE",
  "description": "Scheduled quarterly rotation",
  "keys": [ { "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----", "kid": "key-2" } ],
  "revoke_kids": ["key-1"]
}
```

`partner_id` must be an existing partner (`PM-PRT-404` otherwise). Each entry in
`revoke_kids` must be a current (non-revoked) key of that partner (`PM-KEY-400`
otherwise). `keys` and `jwks_url` follow the onboarding rules above.

### `POST /partners/requests/policy`
Change an approved partner's access policies: propose new versions and/or revoke
policies.

```json
{
  "partner_id": "PARTNER_BANK_A",
  "description": "Grant the loan profile use case",
  "policies": [
    {
      "use_case": "loan-profile@1",
      "allowed_purposes": ["credit-assessment"],
      "allowed_signing_algs": ["EdDSA", "ES256"],
      "max_validity_duration": "P1Y",
      "fetch_type": "oneshot",
      "data_life": "P30D",
      "allow_partner_consents": false
    }
  ],
  "revoke": [{ "data_controller": "farmer-registry" }, { "use_case": "name-check@2" }]
}
```

Each policy (`PolicyInput`) has the fields in
[Access policies](functional-specifications.md#access-policies) and exactly one
key: `data_controller` (with `allowed_data_scopes`) for a registry's scope
policy, or `use_case` (`name@major`) for a use-case policy. A policy for a key
that already has an active policy is its next version. Each `revoke` entry names
one active policy by key, `{"data_controller": X}` or `{"use_case": Y}`.
Proposed versions are created `pending` at once.

Errors:

* `PM-PRT-404` — unknown partner.
* `PM-POLICY-400` — the partner is still `created` (use its onboarding request) or
  `disabled`; nothing proposed or revoked; the same key both changed and
  revoked; or a revoked key has no active policy.
* `PM-POLICY-409` (HTTP 400) — a change (new version or revocation) is already
  pending for that key; approve or reject it first. Other keys are not blocked.
* `PM-POLICY-400` — a scope or use case is not in its configured
  [catalogue source](functional-specifications.md#catalogue-sources), or a purpose
  or subject ID type not in its [Master Data list](functional-specifications.md#master-data-code-lists)
  (the message names them).
* `G2P-REQ-102` — a policy field is invalid (e.g. both or neither of
  `data_controller` / `use_case`, scopes missing for a data controller or given
  for a use case, a use case not `name@major`, an unsupported algorithm, a bad
  duration), or two entries for the same key in `policies` or in `revoke`.

If a catalogue source or the Master Data Service needed for the check cannot be
read, the request is accepted and its response carries `warnings`, e.g.
`["Could not check scopes for 'farmer-registry' ['farmer-registry.land'] against Farmer Registry (cannot reach …). Accepted unchecked: verify before approving."]`.
So does an `allowed_signing_algs` entry that matches none of the partner's
active keys (the request names it; the default is not checked).

### `GET /partners/requests?status=&request_type=&partner_id=`
List requests (optionally filtered). `status` is one of `created`, `approved`,
`rejected`; `request_type` is one of `onboarding`, `key_update`, `policy`. Other values
are rejected with `400` (`G2P-REQ-102`).

### `GET /partners/requests/{request_id}`
Request detail, including `proposed_keys`, `revoke_kids`, `proposed_policies`,
`revoke` (by key) and `warnings` (checks that could not run at
submission; empty normally). The same fields are on every request response.

### `POST /partners/requests/{request_id}/approve`
Body `{ "notes": "optional" }`. Applies the proposed keys (and revocations) and
policies (each proposed version `active`, the previous one `superseded`; revoked
ones `revoked`); for onboarding, flips the partner to `active`.

### `POST /partners/requests/{request_id}/reject`
Body `{ "notes": "optional" }`. Proposed policy versions become `rejected`.

## Admin — partners

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/metadata` | Allowed values for the UI selects (see below) |
| GET | `/catalogue` | Scopes and use cases from the configured catalogue sources (see below) |
| GET | `/partners?status=` | List partners. `status`: `created`, `active` or `disabled` |
| GET | `/partners/{partner_id}` | Partner detail |
| GET | `/partners/{partner_id}/keys` | All keys (any status) |
| GET | `/partners/{partner_id}/policies?all_versions=false` | Active policies; `all_versions=true` returns every version (any status) |
| GET | `/partners/{partner_id}/audit` | Local audit history (append-only ledger) |
| POST | `/partners/{partner_id}/disable` | Stop serving keys and policies |
| POST | `/partners/{partner_id}/enable` | Resume serving keys and policies |

`GET /partners/{partner_id}/policies` returns a list of policy versions: the
fields of a served policy (below) plus `id`, `status`, `request_id`,
`created_by`, `approved_by` and `created_at`.

### `GET /metadata`

Allowed values for every enum-backed field, built from the API's own enums so
the admin UI and the validators share one source of truth:

```json
{
  "algorithms": ["RS256", "ES256", "EdDSA"],
  "partner_statuses": ["created", "active", "disabled"],
  "key_statuses": ["pending", "active", "revoked"],
  "request_types": ["onboarding", "key_update", "policy"],
  "request_statuses": ["created", "approved", "rejected"],
  "signing_algorithms": ["RS256", "ES256", "EdDSA"],
  "fetch_types": ["oneshot", "periodic"],
  "policy_statuses": ["pending", "active", "superseded", "rejected", "revoked"],
  "identifier_pattern": "^[^\\s/?#%]+$",
  "identifier_hint": "No spaces or '/', '?', '#', '%' (e.g. PARTNER_G2P_BRIDGE)."
}
```

`algorithms` and `signing_algorithms` list only the supported algorithms the
deployment's `crypto_allowed_algorithms` keeps; `signing_algorithms` is what a
policy's `allowed_signing_algs` may contain.

### `GET /catalogue`

The choices for policy forms, one entry per configured
[catalogue source](functional-specifications.md#catalogue-sources) (cached
`catalogue_cache_ttl` seconds), then one per
[Master Data list](functional-specifications.md#master-data-code-lists):

```json
{
  "sources": [
    {
      "kind": "scopes",
      "data_controller": "farmer-registry",
      "label": "Farmer Registry",
      "items": [
        { "id": "farmer-registry.land", "label": "Land", "description": "Parcels and areas",
          "purpose": null, "fields": ["parcels"] }
      ],
      "error": null
    },
    {
      "kind": "use_cases",
      "data_controller": null,
      "label": "Agri Stack Composite",
      "items": [],
      "error": "cannot reach http://agri-composite-api/composite/v1/use-cases: ConnectError …"
    },
    {
      "kind": "purposes",
      "data_controller": null,
      "label": "Purposes (Master Data CONSENT_PURPOSE v3)",
      "items": [{ "id": "credit-assessment", "label": "Credit assessment", "fields": [] }],
      "error": null,
      "note": null
    },
    {
      "kind": "subject_id_types",
      "data_controller": null,
      "label": "Subject ID types (Master Data SUBJECT_ID_TYPE)",
      "items": [],
      "error": null,
      "note": "SUBJECT_ID_TYPE is not in this country's Master Data: free text."
    }
  ]
}
```

`items[].id` is a scope ID (scopes) or `name@major` (use cases); `purpose` is
set for use cases, `fields` (the scope's current fields) for scopes. Retired
scopes are left out; for `purposes` / `subject_id_types`, `id` is the list's
`value_code` and `label` its `display` (active codes only). A source that cannot
be read has `error` set and no items; a Master Data list the country does not
have, or an empty one, has `note` set instead (free text, not checked). The call
itself still returns `200`. `sources` is empty when none are configured.

## Public — key fetch (no auth)

### `GET /keys/{partner_id}`
Active public keys for an active partner.

```json
{
  "partner_id": "PARTNER_G2P_BRIDGE",
  "keys": [
    {
      "partner_id": "PARTNER_G2P_BRIDGE",
      "kid": "key-2",
      "algorithm": "RS256",
      "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
      "not_before": null,
      "not_after": null
    }
  ]
}
```

Responses carry `Cache-Control: public, max-age=<n>` so callers cache within a
bounded rotation window.

### `GET /keys/{partner_id}/{kid}`
One active public key.

### `GET /keys/{partner_id}/jwks.json`
The partner's active keys as a JWKS document.

**Fail-closed:** unknown, disabled, or empty partners all return:

```json
{ "code": "PM-KEY-404", "message": "No keys available for partner '<id>'." }
```

## Internal — policy fetch (no auth)

Served by the partner-api on the internal gateway, like key fetch. Other modules
(e.g. the Consent Manager and the Composite) read what a partner may ask for;
see [Integration](integration.md) for caching and the partner ID convention.
Responses carry `Cache-Control: public, max-age=<n>` (`PARTNER_MANAGER_POLICY_FETCH_CACHE_MAX_AGE`,
default `60` seconds).

### `GET /policies/{partner_id}[?data_controller=|?use_case=]`
Active policies of an **active** partner: with no filter, all of them (registries
first, then use cases). `?data_controller=farmer-registry` returns only that
registry's scope policy; `?use_case=loan-profile@1` only that use case's policy;
`?data_controller=` (empty) only the use-case policies.

```json
{
  "partner_id": "PARTNER_BANK_A",
  "policies": [
    {
      "id": "9b2f6c1e-…",
      "partner_id": "PARTNER_BANK_A",
      "data_controller": "farmer-registry",
      "use_case": null,
      "version": 2,
      "allowed_data_scopes": ["farmer-registry.land"],
      "allowed_purposes": [],
      "allowed_subject_id_types": [],
      "allowed_signing_algs": ["EdDSA", "ES256"],
      "max_validity_duration": "P1Y",
      "fetch_type": "oneshot",
      "max_fetch_frequency": null,
      "data_life": null,
      "allow_partner_consents": false,
      "effective_from": "2026-10-20T09:15:00"
    }
  ]
}
```

`id` identifies this policy version (each version has its own): a consumer can
record it to show exactly which version it applied.

**Fail-closed:** an unknown partner, a partner that is not `active`, and one with
no matching active policy all return `404`:

```json
{ "code": "PM-POLICY-404", "message": "No policies available for partner '<id>'." }
```

### `GET /policies?use_case=&data_controller=`
Active policies of active partners, for listings (e.g. which partners are
granted a use case). At least one filter is required (`PM-POLICY-400`
otherwise); `data_controller=` (empty) selects use-case policies.

```json
{
  "count": 1,
  "policies": [
    { "id": "4d0a…", "partner_id": "PARTNER_BANK_A", "data_controller": null,
      "use_case": "loan-profile@1", "version": 1, "...": "..." }
  ]
}
```

## Health

`GET /ping` — liveness/readiness probe.

## Error codes

| Code | Meaning |
| --- | --- |
| `G2P-REQ-102` | Request validation failed (e.g. an algorithm, status, request type or `jwks_url` outside the allowed values, or an invalid policy field). |
| `PM-KEY-400` | Invalid key material (private key, weak RSA, bad format, disallowed algorithm), or a `revoke_kids` entry that is not a current key. |
| `PM-PRT-409` | Partner already exists. |
| `PM-PRT-404` | Partner not found (admin API). |
| `PM-REQ-404` | Request not found. |
| `PM-REQ-409` | Request is not open for review. |
| `PM-JWK-502` | Failed to import from the partner's JWKS URL. |
| `PM-KEY-404` | Key fetch: nothing available (fail-closed). |
| `PM-POLICY-400` | Invalid policy request (partner not approved or disabled, nothing to change, change and revoke of the same key, revoke of a key with no active policy, a scope or use case not in its catalogue source, a purpose or subject ID type not in its Master Data list), or `GET /policies` without a filter. |
| `PM-POLICY-409` | A policy change is already pending for that key — data controller or use case (returned with HTTP 400). |
| `PM-POLICY-404` | Policy fetch: nothing available (fail-closed). |
