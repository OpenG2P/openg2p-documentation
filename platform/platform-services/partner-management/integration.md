---
description: >-
  Handover note for an OpenG2P service that needs to verify partner signatures or
  check what a partner may ask for — how to consume partner public keys and access
  policies from Partner Management (PM).
---

# Integration — consuming partner keys and policies

**TL;DR:** Don't store or seed partner keys or access policies in your service.
Fetch them from PM's **partner-api** and cache them. For keys, if you're built on
`openg2p-fastapi-common`, this is **config only** — no code. Policies are read
over the same API with the same caching discipline (§6).

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
- A service that identifies the partner by its audience / DCI `sender_id` maps
  it by the platform convention: upper-case, `-` → `_`, prefix `PARTNER_`
  (`bank-a` → `PARTNER_BANK_A`). Keys and policies are both looked up under that
  ID; there is no per-partner override. See
  [Partner ID convention](functional-specifications.md#partner-id-convention).

## 6. Consuming access policies

What a partner may ask for is an **access policy** in PM — a scope policy per
registry data controller, or a use-case policy for an Exchange (model and
lifecycle: [Access policies](functional-specifications.md#access-policies)).
Policies change only through approved PM requests; your service never stores or
edits them.

Read them from the partner-api ([API](api-reference.md)):

```
GET {PM_PARTNER_API_URL}/policies/{partner_id}?data_controller=<controller>  -> that registry's scope policy
GET {PM_PARTNER_API_URL}/policies/{partner_id}?data_controller=              -> the use-case policy
GET {PM_PARTNER_API_URL}/policies?use_case=<name@major>                      -> listing (who is granted a use case)
```

Apply the §4 discipline, per (partner, data controller):

- **Soft TTL** — honour `Cache-Control: max-age` (PM default 60 s, shorter than
  keys so a narrowed or revoked policy takes effect quickly).
- **Hard TTL** — while PM is unreachable, keep using the last answer up to a
  bounded age (hours), then deny.
- **Negative TTL** — remember a `404` briefly (seconds), and wait as long before
  retrying after a failure.
- **Single-flight** — one fetch per key at a time; a short fetch timeout.
- **Fail closed** — `404` (`PM-POLICY-404`) means no policy: deny. PM down with
  nothing usable cached: deny with a retryable error.

Current consumers and where their settings are documented:

| Consumer | Reads | Settings |
| --- | --- | --- |
| Consent Manager | The consenting partner's scope policy for the registry's data controller; in an Exchange, the partner's use-case policy | [Consent Manager deployment](../../../consent-management/deployment/README.md) |
| Composite (Exchange) | The calling partner's use-case policy (is `name@major` granted?); listings for its console | [Composite deployment](../../../open-agri-stack/deployment/composite.md) |

How the Consent Manager evaluates a policy:
[Verification and enforcement](../../../consent-management/design/verification-and-enforcement.md).

## 7. Onboarding & ops checklist

- [ ] Partner is **onboarded in PM and `active`** (an admin approves it) with its public key(s) and the policies it needs. Until then, fetch returns `404` and you reject — by design.
- [ ] `partner_id` in PM matches your lookup key (§5).
- [ ] Your namespace can reach `partner-management-partner-api` (in-cluster Service DNS / internal gateway).
- [ ] You do **not** ship partner keys or policies in your own Helm values or DB.
- [ ] Key rotation and policy changes are PM operations (approved requests); you get them automatically via cache refresh / unknown-kid.

## What not to do
- ❌ Don't call `/keys` or `/policies` on every request — always cache.
- ❌ Don't put PM's admin/staff APIs in your path — you only need the internal `/keys` and `/policies` fetch.
- ❌ Don't manage partners, keys or policies inside your own service.
