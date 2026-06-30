---
layout:
  width: default
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
  tags:
    visible: true
  actions:
    visible: true
---

# PyJWTCryptoHelper

## Local (Keymanager-free) JWS signing & verification in `openg2p-fastapi-common`

All partner-signature signing and verification lives in **`openg2p-fastapi-common`**,
behind the `CryptoHelper` interface. Products (e.g. G2P Bridge, SPAR) do **not**
implement crypto themselves — they select a backend and call the interface. This
page describes how the local backend works and how a product turns it on.

### 1. The interface (unchanged)

`openg2p_fastapi_common.utils.crypto.CryptoHelper` is the abstract contract used by
all partner-facing APIs:

```python
class CryptoHelper(BaseService):
    async def verify_jwt(self, orig_jwt: str, payload=None, **kw) -> bool: ...
    async def create_jwt_token(self, payload, include_payload=True, **kw) -> str: ...
```

`openg2p_fastapi_partner_auth` (`JWTValidationHelper`, `JWTSignatureValidator` — the
FastAPI dependency used in route handlers) only ever talks to `CryptoHelper` through
this interface. It has no knowledge of which implementation is active; selection is
whichever `CryptoHelper` instance the consuming app registers.

### 2. Two backends

| Backend | Class | What it does |
| --- | --- | --- |
| `keymanager` | `KeymanagerCryptoHelper` | Delegates `verify`/`sign` to the remote Key Manager microservice over HTTP (`/jwtVerify`, `/jwtSign`). **Unchanged.** |
| `local` | `PyJWTCryptoHelper` | Performs sign/verify **in-process** with `PyJWT` + `cryptography` — no Key Manager, no Keycloak token. |

The active backend is chosen by configuration (see §6) via a factory:

```python
from openg2p_fastapi_common.utils.crypto import build_crypto_helper

build_crypto_helper()                            # picks the backend from crypto_backend
build_crypto_helper(name="spar_mapper_crypto")   # a named instance for outbound signing
```

### 3. Signature protocol (detached JWS — identical for both backends)

Partners need no change regardless of backend:

1. The partner signs the **business payload** with its own private key, producing a
   **detached JWS**: `header..signature` (the middle/payload segment is empty — the
   payload is not duplicated in the token because it is already the HTTP body).
2. The partner sends this in the **`Signature`** HTTP header; the JSON business
   payload is the request body.
3. The verifier reconstructs `header.base64url(canonical_json(body)).signature` and
   verifies it against the partner's public key.
4. Canonical JSON = `orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)` — compact,
   UTF-8, sorted keys — so both sides compute byte-identical bytes.

Only the **signature** travels in the header — never the whole JWT, never the
business payload twice.

### 4. Algorithm

**RS256 only** (RSA, asymmetric). The HMAC family (`HS*`, symmetric) and `none` are
**always rejected**, independent of configuration — this blocks the JWS
algorithm-confusion attack. The allowed set is pinned server-side; the token
header's own `alg` is never trusted to select behaviour.

### 5. Key storage (local backend)

Signing and verifying use **different keys in different directions**:

| Direction | Key | Where it lives |
| --- | --- | --- |
| **Inbound** — verify a partner's signature | the partner's **public certificate** | the **`partner_keys` DB table** (`openg2p_fastapi_common.models.PartnerKey`) |
| **Outbound** — sign this service's own request | this service's **private key** | a password-protected **PKCS#12 (`.p12`) keystore**, mounted from a K8s Secret |

* **Partner public certs (DB).** Public certs are not secret, so they live in an
  ordinary table — one row per partner, keyed by `reference_id` (`PARTNER_<MNEMONIC>`,
  derived from `sender_app_mnemonic`), holding the cert PEM, optional `kid`,
  `algorithm`, `status` (`active`/`revoked`) and a validity window. The DB-backed
  `PartnerKeyStore` resolves the active certs for a partner on each verify, cached
  for a short TTL so a high request rate does not hit the database every call.
  Multiple active rows per partner make rotation an overlap operation.
* **Service private key (`.p12`).** `PyJWTCryptoHelper` loads the private key from a
  `.p12` keystore (`crypto_signing_key_path` + `crypto_signing_key_password`); the
  outbound `kid` defaults to the signing certificate's SHA-256 thumbprint. A
  verify-only service configures no `.p12`.

#### Partner onboarding (seed-based)

Partner certs are onboarded by **seeding** the `partner_keys` table at app
migrate-time from `crypto_partner_certs` (config), via `seed_partner_certs(...)`
(idempotent). A runtime admin API to register/revoke certs without a redeploy is a
planned follow-up (**TODO**).

### 6. Configuration (`openg2p-fastapi-common` settings — distinct from `keymanager_*`)

```
crypto_backend: str = "keymanager"        # "keymanager" | "local"
crypto_signing_key_path: str = ""         # path to the .p12 (outbound signing)
crypto_signing_key_password: str = ""     # .p12 password
crypto_signing_key_kid: str = ""          # blank -> cert SHA-256 thumbprint
crypto_signing_algorithm: str = "RS256"
crypto_allowed_algorithms: str = "RS256"  # verification allow-list
crypto_partner_certs: list[dict] = []     # seed: [{reference_id, public_key, kid?, algorithm?}]
```

The existing `keymanager_*` settings are **untouched** and used only when
`crypto_backend="keymanager"`.

### 7. Fail-closed behaviour

* Verify failures of every kind — missing/unknown partner, malformed detached JWS,
  forbidden algorithm, signature mismatch — make `verify_jwt` return **`False`**
  (it never raises); `RequestValidation.validate_signature` turns that into a clean
  rejection envelope.
* `create_jwt_token` (outbound) is allowed to raise — if the private key can't be
  loaded, the call must not silently proceed unsigned.
* Signature validity only — **no trust-authority / CA-chain / trusted-root check**
  (out of scope; a self-signed partner cert is fine).

### 8. Impact on products (e.g. G2P Bridge)

Minimal. A product's `Initializer` registers the helper via the factory instead of
hard-coding a backend:

```python
# before
KeymanagerCryptoHelper()
# after
build_crypto_helper()            # backend chosen by crypto_backend config
```

Everything else — `JWTValidationHelper`, `JWTSignatureValidator`, controllers — is
unchanged. The product also exposes a `signature_validation_enabled` gate (only
enforce signatures when on; useful for demos). Supplying the `.p12` and onboarding
partner certs is a **deployment** concern handled in each product's Helm chart (e.g.
a bundled demo key plus a Rancher-supplied production key, and a `crypto_partner_certs`
seed) — not in the library.

### 9. Where the code lives

| Path (in `openg2p-fastapi-common`) | What |
| --- | --- |
| `utils/crypto.py` → `CryptoHelper` | the interface |
| `utils/crypto.py` → `KeymanagerCryptoHelper` | remote backend (unchanged) |
| `utils/crypto.py` → `PyJWTCryptoHelper` | local backend (PyJWT + cryptography) |
| `utils/crypto.py` → `PartnerKeyStore` | DB-backed partner-cert lookup (TTL cache) |
| `utils/crypto.py` → `seed_partner_certs` | idempotent seed-based onboarding |
| `utils/crypto.py` → `build_crypto_helper` | backend-selecting factory |
| `models.py` → `PartnerKey` | the `partner_keys` table |

Dependency added: `PyJWT[crypto] >= 2.8.0`.

> **Note.** An earlier draft of this design proposed reading keys directly from
> Kubernetes Secrets (`{partnerMnemonic}-PublicKey`, `OpenG2P-PrivateKey`). The
> shipped implementation instead uses the DB-backed `partner_keys` table for partner
> public certs and a `.p12` keystore for the private key, as described above.
