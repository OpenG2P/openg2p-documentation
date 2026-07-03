---
description: >-
  The shared FastAPI framework and utilities that most OpenG2P Python services
  are built on — app bootstrap, config, data layer, auth, and JWS crypto.
---

# OpenG2P FastAPI Common

**[`openg2p-fastapi-common`](https://github.com/OpenG2P/openg2p-fastapi-common)**
is the base framework nearly every OpenG2P Python microservice is built on
(g2p-bridge, consent-manager, Partner Management, the registry APIs, the IAM
staff-portal API, …). Standardising it means services share one app lifecycle,
config convention, data layer, error format, and — importantly for signed
inter-service traffic — one **JWS crypto** implementation.

The repository publishes four installable packages:

| Package | Purpose |
| --- | --- |
| `openg2p-fastapi-common` | Core: app `Initializer`, `BaseController`/`BaseService`, `Settings`, async SQLAlchemy models, error envelope, JWS crypto |
| `openg2p-fastapi-auth` | OIDC/JWT validation dependency (`JwtBearerAuth`, `StaffKeycloakAuth`) |
| `openg2p-fastapi-auth-models` | Shared auth schemas (`AuthCredentials`, login providers) |
| `openg2p-fastapi-partner-auth` | Partner-request JWS signature validation dependency |

## What the core provides

* **App bootstrap (`Initializer`)** — builds the FastAPI app, wires logging, CORS,
  security headers, the async SQLAlchemy engine, and the exception handler; exposes
  a CLI (`run`, `migrate`, `getOpenAPI`). Services subclass it and register their
  controllers/services.
* **`BaseController` / `BaseService`** — an `APIRouter`-backed controller base and a
  component-registry service base, so components discover each other as singletons.
* **`Settings`** — Pydantic-settings config with an env prefix per service (e.g.
  `G2P_BRIDGE_*`), plus common fields for DB, logging, CORS, and crypto.
* **Data layer** — async SQLAlchemy 2.0 base models (`BaseORMModelWithId`,
  `BaseORMModelWithTimes`) with idempotent `create_migrate()`.
* **Error envelope** — a `BaseAppException` hierarchy that renders the platform
  standard `{code, message}` response.

## JWS crypto

Services sign their own outbound requests and verify inbound partner-signed
requests using a **detached JWS** (`header..signature`) over a canonical payload.
The behaviour is selected by one setting, **`crypto_backend`**:

| `crypto_backend` | Verification key source | Signing | Notes |
| --- | --- | --- | --- |
| `keymanager` (default) | MOSIP Keymanager (remote) | Keymanager | Legacy/HSM path |
| `local` | Local **`partner_keys`** table, seeded from Helm | Local PKCS#12 keystore | In-process PyJWT; no Keymanager |
| `partner-mgmt` | **Partner Management** service (fetched + cached) | Local PKCS#12 keystore | In-process PyJWT; **no local key seeding** |

Only **asymmetric** algorithms are accepted (RS256 by default); `none` and HMAC
(`HS*`) are always rejected.

### Local signing key

For the `local` and `partner-mgmt` backends, a service that *signs* loads its own
private key from a password-protected **PKCS#12 (`.p12`) keystore**
(`crypto_signing_key_path` / `crypto_signing_key_password`). The `kid` defaults to
the signing certificate's SHA-256 thumbprint. A service that only *verifies* needs
no signing key.

### Partner keys — verifying inbound partner signatures

To verify a partner's signature, the service needs that partner's **public key**.
Two sources exist behind the same `PartnerKeyStore.get_keys(reference_id)` contract
(returning `{kid, algorithm, public_key_pem}` dicts, from which the verifier
selects by `kid`/`alg`):

* **`local` — seeded local table.** Partner certs are upserted into the service's
  own `partner_keys` table at migrate-time from `crypto_partner_certs` (Helm
  config). Simple, but every service maintains its own copy and there is no
  runtime admin API.
* **`partner-mgmt` — fetched from Partner Management.** The recommended path.
  On a cache miss the service does `GET {partner_mgmt_api_url}/keys/{reference_id}`
  against the PM **partner-api** and caches the result in-process. Partners are
  onboarded and rotated centrally in [Partner Management](../../platform-services/partner-management/README.md);
  consumers hold no partner keys of their own.

#### Caching (`partner-mgmt`)

To avoid an HTTP call per verification, `PartnerMgmtKeyStore` caches keys per
`reference_id` in-memory with a small, well-defined policy — the standard JWKS
client pattern:

| Behaviour | Default | Purpose |
| --- | --- | --- |
| **Soft TTL** (refresh) | `min(300s, PM Cache-Control)`, floor 30s | Bounds how long a revoked key / disabled partner stays trusted — kept short |
| **Refresh-on-unknown-kid** | rate-limited by cooldown | A just-rotated partner's new `kid` triggers one immediate refresh, so rotation is picked up without waiting for the TTL |
| **Hard TTL** (serve-stale) | 6h | If PM is unreachable, keep serving last-known-good keys up to this age (logged `WARNING`), then fail closed |
| **Negative cache** | 30s | A `404 not available` (disabled/unknown partner) is remembered briefly so it doesn't fetch per request; still fails closed |
| **Refresh cooldown** | 10s | Min interval between fetch attempts per partner (throttles unknown-kid refreshes and outage retries) |
| **Single-flight** | — | Concurrent misses for one partner collapse to a single HTTP call |

Because unknown-kid refresh makes rotation near-instant, the soft TTL's real job
is **revocation latency** (disable/revoke), which is why it is kept short rather
than the multi-hour TTL some JWKS clients use.

#### Config (env, with the service's own prefix — e.g. `G2P_BRIDGE_*`)

```
<PREFIX>_CRYPTO_BACKEND=partner-mgmt
<PREFIX>_PARTNER_MGMT_API_URL=http://partner-management-partner-api
# optional overrides:
<PREFIX>_PARTNER_KEY_CACHE_TTL_SECONDS=300
<PREFIX>_PARTNER_KEY_HARD_TTL_SECONDS=21600
<PREFIX>_PARTNER_KEY_NEGATIVE_TTL_SECONDS=30
<PREFIX>_PARTNER_KEY_REFRESH_COOLDOWN_SECONDS=10
```

> **Note on the env prefix.** `crypto_*` settings live on the main `Settings`,
> which each service subclasses with its **own** prefix (`G2P_BRIDGE_`,
> `PARTNER_MANAGER_`, …). The `openg2p-fastapi-auth` settings are separate and use
> the `COMMON_` prefix. So it's `<PREFIX>_CRYPTO_BACKEND`, not `COMMON_CRYPTO_BACKEND`.

### Identity: `reference_id` vs `partner_id`

A verifier derives a **`reference_id`** from the inbound request (for the commons
partner-auth path, `PARTNER_<MNEMONIC>` from the JWS `sender_app_mnemonic`) and
fetches `/keys/{reference_id}`. For the fetch to resolve, the partner must be
onboarded in Partner Management under a matching **`partner_id`** — i.e.
standardise `partner_id == PARTNER_<MNEMONIC>` for the commons/local-crypto
consumers. Services that key on a different attribute (e.g. consent-manager's
`audience`) either onboard under that value or rely on a future PM alias.

## Auth

`openg2p-fastapi-auth` provides `JwtBearerAuth` (verifies a Keycloak JWT against
the issuer's JWKS) and `StaffKeycloakAuth` (adds staff-realm role checks), used as
FastAPI dependencies. Its settings use the `COMMON_AUTH_*` env prefix.

## Versioning

Services install these packages from the `develop` git ref (pinnable to a tag via
each service's `FASTAPI_COMMON_REF` build-arg). See [Versions](versions.md).
