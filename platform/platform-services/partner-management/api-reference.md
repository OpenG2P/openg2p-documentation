# API Reference

Interactive OpenAPI docs are served at `/docs` on each running service.

The endpoints are split across the two backend components:

* **staff-portal-api** serves the admin endpoints below (`/partners...`). They
  require a Keycloak **staff-realm** JWT (obtained via the shared IAM login and
  forwarded by the UI) carrying the `partner_manager` role.
* **partner-api** serves the key-fetch endpoints (`/keys...`), which require no
  authentication.

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
  ]
}
```

Creates the partner in `created` and a request in `created`. Each key may instead
supply `jwk` (a JSON Web Key) rather than `public_key`; `kid` and `algorithm` are
optional and derived when omitted.

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

### `GET /partners/requests?status=&partner_id=`
List requests (optionally filtered).

### `GET /partners/requests/{request_id}`
Request detail, including `proposed_keys`.

### `POST /partners/requests/{request_id}/approve`
Body `{ "notes": "optional" }`. Applies the proposed keys (and revocations); for
onboarding, flips the partner to `active`.

### `POST /partners/requests/{request_id}/reject`
Body `{ "notes": "optional" }`.

## Admin — partners

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/partners?status=` | List partners |
| GET | `/partners/{partner_id}` | Partner detail |
| GET | `/partners/{partner_id}/keys` | All keys (any status) |
| GET | `/partners/{partner_id}/audit` | Local audit history (append-only ledger) |
| POST | `/partners/{partner_id}/disable` | Stop serving keys |
| POST | `/partners/{partner_id}/enable` | Resume serving keys |

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

## Health

`GET /ping` — liveness/readiness probe.

## Error codes

| Code | Meaning |
| --- | --- |
| `PM-KEY-400` | Invalid key material (private key, weak RSA, bad format, disallowed algorithm). |
| `PM-PRT-409` | Partner already exists. |
| `PM-PRT-404` | Partner not found (admin API). |
| `PM-REQ-404` | Request not found. |
| `PM-REQ-409` | Request is not open for review. |
| `PM-JWK-502` | Failed to import from the partner's JWKS URL. |
| `PM-KEY-404` | Key fetch: nothing available (fail-closed). |
