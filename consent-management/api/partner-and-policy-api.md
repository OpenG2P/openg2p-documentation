---
description: >-
  Administrative API to onboard partners, manage their signing keys, and set the
  versioned policy that caps everything a partner can be granted.
---

# Partner &amp; Policy API

Administrative endpoints used to onboard and govern partners. See
[Partner onboarding &amp; policy](../design/partner-onboarding-and-policy.md) for the model.

**Auth:** admin credentials (elevated), network-restricted. **Base path:** `/consent/v1`.

## Partners

### `POST /partners`

Onboard a new partner.

`jwks_url` is optional — set it to have the CM poll the partner's JWKS endpoint for verifying keys
(in addition to keys registered below).

```json
// request
{ "name": "Partner A", "org_name": "Partner A Pvt Ltd",
  "audience": "PARTNER_SYSTEM_A", "controller_id": "REGISTRY_TENANT_1",
  "jwks_url": "https://partner-a.example.org/.well-known/jwks.json" }
// response 201
{ "partner_id": "8c0b...", "name": "Partner A", "org_name": "Partner A Pvt Ltd",
  "audience": "PARTNER_SYSTEM_A", "controller_id": "REGISTRY_TENANT_1",
  "jwks_url": "https://partner-a.example.org/.well-known/jwks.json",
  "status": "active", "created_at": "2025-04-01T00:00:00Z" }
```

### `GET /partners/{partner_id}`

Return the partner profile (no secrets).

### `PATCH /partners/{partner_id}`

Update mutable fields or `status` (`active` / `suspended`). Suspending a partner causes all its
consent objects to fail with `unknown_partner`.

```json
{ "status": "suspended" }
```

## Keys

### `POST /partners/{partner_id}/keys`

Register a public key (PEM or JWK) used to verify the partner's consent objects.

```json
// request
{ "kid": "partnerA-2025-01", "algorithm": "EdDSA",
  "public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
  "not_after": "2026-04-01T00:00:00Z" }
// response 201
{ "key_id": "k-001", "kid": "partnerA-2025-01", "algorithm": "EdDSA", "status": "active" }
```

A partner may hold multiple active keys to support **rotation**. Alternatively register a
`jwks_url` on the partner that the CM polls.

### `DELETE /partners/{partner_id}/keys/{kid}`

Revoke a key (e.g. on compromise). Objects signed with it immediately fail `signature_invalid`.
Returns `204`.

## Policy

The policy is **versioned**; a `PUT` creates a new active version and retains prior ones.

### `PUT /partners/{partner_id}/policy`

```json
// request
{
  "allowed_data_scopes": ["farmer_profile.basic", "farmer_profile.crops"],
  "allowed_purposes": ["share_farm_profile", "subsidy_eligibility"],
  "allowed_subject_id_types": ["national_id", "farmer_id"],
  "max_validity_duration": "P1Y",
  "fetch_type": "oneshot",
  "max_fetch_frequency": null,
  "data_life": "P30D",
  "allowed_signing_algs": ["EdDSA", "ES256"]
}
// response 200
{ "policy_id": "p-77", "version": 4, "status": "active",
  "effective_from": "2025-06-26T00:00:00Z" }
```

### `GET /partners/{partner_id}/policy`

Return the active policy version. Add `?version=3` to fetch a specific historical version (useful
when interpreting an old decision's `policy_version`).

## Errors

Standard HTTP codes with a problem body (see [conventions](README.md#decision--error-model)).
`404` for unknown partner/key; `409` if registering a duplicate `kid`; `422` for an invalid
policy (e.g. unknown scope or non-ISO-8601 duration).
