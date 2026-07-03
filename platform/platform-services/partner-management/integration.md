---
description: >-
  Handover note for a new OpenG2P service that needs to verify partner signatures
  — how to consume partner public keys from Partner Management (PM).
---

# Integration — consuming partner keys

**TL;DR:** Don't store or seed partner keys in your service. Fetch them from PM's
**partner-api** and cache them. If you're built on `openg2p-fastapi-common`, this
is **config only** — no code.

## 1. Decide your path

| Your service | What to do |
| --- | --- |
| **Built on `openg2p-fastapi-common`, verifies partner JWS via the common partner-auth path** (like g2p-bridge) | Set `crypto_backend=partner-mgmt` + the PM URL. **No code.** Go to §2. |
| **Has its own key model / verification** (like consent-manager keys on `audience`) | Call PM's fetch API yourself and cache with the same discipline (§4). Go to §3. |

## 2. Commons-based service (config only)

Set these env vars (they use **your service's own prefix**, e.g. `G2P_BRIDGE_`, not `COMMON_`):

```
<PREFIX>_CRYPTO_BACKEND=partner-mgmt
<PREFIX>_PARTNER_MGMT_API_URL=http://partner-management-partner-api
# optional cache overrides (sensible defaults exist):
# <PREFIX>_PARTNER_KEY_CACHE_TTL_SECONDS=300
# <PREFIX>_PARTNER_KEY_HARD_TTL_SECONDS=21600
# <PREFIX>_PARTNER_KEY_NEGATIVE_TTL_SECONDS=30
# <PREFIX>_PARTNER_KEY_REFRESH_COOLDOWN_SECONDS=10
```

Then:
- **Remove** any local key seeding (`crypto_partner_certs` / test partner certs). PM is now the source.
- The commons `PartnerMgmtKeyStore` handles fetch + in-process caching (soft/hard TTL, unknown-kid refresh, negative cache, single-flight). See [OpenG2P FastAPI Common → JWS crypto](../../architecture/openg2p-fastapi-common/README.md#jws-crypto).

## 3. Service with its own key handling

Call the unauthenticated fetch API (no caller signature needed — internal gateway):

```
GET {PM_PARTNER_API_URL}/keys/{partner_id}            -> active keys (PEM + kid + alg)
GET {PM_PARTNER_API_URL}/keys/{partner_id}/{kid}      -> one key
GET {PM_PARTNER_API_URL}/keys/{partner_id}/jwks.json  -> JWKS
```

Then **cache it yourself** (don't fetch per request) with the same policy as §4.

## 4. Caching & failure rules (replicate these if you roll your own)

- **Cache per partner**, honoring the response `Cache-Control: max-age`. Keep the TTL **short** (minutes) — it bounds how fast a *revoked* key / *disabled* partner stops being trusted.
- **Refresh on an unknown `kid`** (rate-limited) so key rotation is picked up immediately, not after the TTL.
- **Fail closed:** PM returns `404` for unknown *and* disabled partners — treat "no keys" as reject.
- **Tolerate a brief PM outage:** serve last-known-good keys up to a bounded hard TTL, logging it, then fail closed. Negative-cache 404s briefly so a disabled partner doesn't hammer PM.

## 5. Identity — the one thing you must get right

PM is keyed by **`partner_id`**. Whatever string your service derives from an
inbound request to identify the partner **must equal that `partner_id`.**

- Commons partner-auth path derives `PARTNER_<MNEMONIC>` (from the JWS
  `sender_app_mnemonic`) → **onboard the partner in PM with `partner_id = PARTNER_<MNEMONIC>`.**
- If you key on something else (e.g. an `audience`), onboard the partner in PM
  under that value (or request a PM alias).

## 6. Onboarding & ops checklist

- [ ] Partner is **onboarded in PM and `active`** (an admin approves it) with its public key(s). Until then, fetch returns `404` and you reject — by design.
- [ ] `partner_id` in PM matches your lookup key (§5).
- [ ] Your namespace can reach `partner-management-partner-api` (in-cluster Service DNS / internal gateway).
- [ ] You do **not** ship partner keys in your own Helm values or DB.
- [ ] Key rotation is a PM operation (admin adds a new key, revokes the old); you get it automatically via cache refresh / unknown-kid.

## What not to do
- ❌ Don't call `/keys` on every verification — always cache.
- ❌ Don't put PM's admin/staff APIs in your path — you only need the public `/keys` fetch.
- ❌ Don't manage partners or keys inside your own service.
