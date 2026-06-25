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

## Design: `PyJWTCryptoHelper` — Local JWT Signing/Verification for Partner Auth



### 1. Background

`openg2p_fastapi_common.utils.crypto.CryptoHelper` is the abstract interface used throughout OpenG2P's partner-facing APIs (e.g. `openg2p-g2p-bridge-partner-api`) to validate inbound request signatures and to sign outbound requests:

```python
class CryptoHelper(BaseService):
    async def verify_jwt(self, orig_jwt: str, payload=None, **kw) -> bool: ...
    async def create_jwt_token(self, payload, include_payload=True,
                                include_certificate=False, include_cert_hash=False, **kw) -> str: ...
```

Today the only implementation is `KeymanagerCryptoHelper`, which delegates both operations to an external Key Manager microservice over HTTP (`/jwtVerify`, `/jwtSign`). Every OpenG2P deployment that wants signature verification must therefore stand up and operate that microservice.

`openg2p_fastapi_partner_auth.jwt_validation_helper.JWTValidationHelper` and `jwt_signature_validator.JWTSignatureValidator` (the FastAPI dependency used in route handlers, e.g. `DisbursementController.create_disbursements`) only ever talk to `CryptoHelper` through this interface — they have no knowledge of which implementation is active. Component selection happens by whichever `CryptoHelper` subclass instance the consuming app's `Initializer.initialize()` constructs (component registry is `isinstance`-based, see `BaseComponent`/`get_cached_component`).

### 2. Goal

Add a second `CryptoHelper` implementation, <mark style="color:violet;">**`PyJWTCryptoHelper`**</mark>, that performs signing and verification **locally** using `PyJWT` + `cryptography`, with keys sourced from Kubernetes Secrets, removing the runtime dependency on the Key Manager microservice. It must be a pure drop-in: no changes to `JWTValidationHelper`, `JWTSignatureValidator`, or any controller — only the one line in each consuming app's `Initializer` that decides which `CryptoHelper` to instantiate.

### 3. Design principle: the interface owns the contract, not the wiring

`KeymanagerCryptoHelper` is the precedent for how a `CryptoHelper` implementation should be shaped: it owns its own `httpx.AsyncClient` and auth-token logic entirely inside the class. The only thing the rest of the system knows about is `verify_jwt` / `create_jwt_token`.

`PyJWTCryptoHelper` follows the same shape: **key retrieval is an internal implementation detail**. It is not exposed as a separately-registered component, it is not something the consuming app wires up, and nothing outside `pyjwt_crypto_helper.py` ever imports or instantiates a key-store class directly. `PyJWTCryptoHelper.__init__` builds (lazily) its own Kubernetes API client and a private in-memory cache; `verify_jwt`/`create_jwt_token` call private methods (e.g. `self._get_key(name)`) to fetch PEM bytes.

This avoids two problems with externalizing key retrieval as a registered component:

* **Wiring burden**: the app's `Initializer` would need to know to construct a key-store instance _and_ the crypto helper, in the right order, as two registry entries — leaking "how does this implementation get its keys" out to call sites that shouldn't care.
* **Ordering hazard**: a registry-lookup-based dependency (`KeyStore.get_cached_component()`) silently resolves to nothing if constructed before the key store exists, a class of bug `KeymanagerCryptoHelper` doesn't have because it self-contains its dependencies.

### 4. Signature protocol (must match `KeymanagerCryptoHelper` exactly)

This is the existing wire protocol already implemented by `KeymanagerCryptoHelper.verify_jwt`, and `PyJWTCryptoHelper` must replicate it bit-for-bit so existing partner integrations require no changes:

1. The partner signs the **business payload** using its own private key, producing a _detached_ JWS: `header..signature` (the middle/payload segment is empty — the payload is not duplicated in the JWT because it's already the HTTP request body).
2. The partner sends this detached JWS in the `Signature` header, plus the JSON business payload as the request body.
3. Bridge reconstructs the full JWS by computing `actual_data = base64url(canonical_json(payload))` and splicing it in as the middle segment: `header.actual_data.signature`.
4. Bridge verifies the signature over `header.actual_data` using the partner's public key. A valid signature over `actual_data` is, by construction, a guarantee that `actual_data`'s SHA hash (computed internally by RSA/ECDSA verification) matches what the partner originally signed — this is the "two hash values must match" requirement, expressed as standard JWS verification rather than a manual hash comparison.
5. Canonicalization uses `orjson.dumps(payload, option=orjson.OPT_SORT_KEYS)` — sorted keys, no incidental whitespace — so partner and Bridge compute byte-identical JSON regardless of dict-ordering on either side.

For outbound signing (`create_jwt_token`), Bridge performs the mirror operation: canonicalize the outbound payload the same way, sign with its own private key, and (when `include_payload=False`) strip the middle segment before sending — so the receiving bank/notification/warehouse service applies the same reconstruction algorithm Bridge itself uses for inbound verification.

### 5. Key resolution

| Key                              | Kubernetes Secret object name | Used for                      |
| -------------------------------- | ----------------------------- | ----------------------------- |
| Partner's public key/certificate | `{partnerMnemonic}-PublicKey` | `verify_jwt` (inbound)        |
| Bridge's own private key         | `OpenG2P-PrivateKey`          | `create_jwt_token` (outbound) |

* `partnerMnemonic` is read from the business payload, not the JWT — mirroring `JWTValidationHelper.get_partner_id_from_payload`'s existing precedence: `payload.header.sender` → legacy `payload.header.sender_id` → `payload.request_header.sender_app_mnemonic`.
* **Open design decision**: one Kubernetes Secret object per key (as named above, literal Secret resource names) vs. one shared Secret with many data fields keyed by partner. Per-secret is assumed here because it matches the literal naming convention given (`{partnerMnemonic}-PublicKey`) and allows per-partner RBAC; needs confirmation before implementation.
* The PEM blob may be either a raw public key (`-----BEGIN PUBLIC KEY-----`) or a full X.509 certificate (`-----BEGIN CERTIFICATE-----`); `PyJWTCryptoHelper` tries certificate parsing first (via `cryptography.x509.load_pem_x509_certificate`, extracting `.public_key()`) and falls back to `cryptography.hazmat.primitives.serialization.load_pem_public_key`. This satisfies the "with or without trusted root" requirement without needing a separate code path — trust-chain validation (root CA pinning) is explicitly out of scope for v1 (see §9).

### 6. Class shape

```python
class PyJWTCryptoHelper(CryptoHelper):
    def __init__(self, algorithm="RS256",
                 public_key_secret_template="{partner_mnemonic}-PublicKey",
                 private_key_secret_name="OpenG2P-PrivateKey",
                 k8s_namespace="default", k8s_secret_data_field="value",
                 k8s_in_cluster=True, key_cache_ttl_seconds=300, **kw):
        super().__init__(**kw)
        # stores config; K8s client itself is built lazily on first use

    async def verify_jwt(self, orig_jwt: str, payload=None, **kw) -> bool: ...
    async def create_jwt_token(self, payload, include_payload=True,
                                include_certificate=False, include_cert_hash=False, **kw) -> str: ...

    # --- internal only, never imported elsewhere ---
    def _k8s_client(self): ...          # lazy CoreV1Api(), in-cluster or kubeconfig
    def _get_key(self, secret_name: str) -> bytes: ...   # cached Secret read + base64 decode
    def _load_public_key(self, pem: bytes): ...
    def _load_private_key(self, pem: bytes): ...
    def _sender_mnemonic(self, payload) -> str | None: ...
    def _canonicalize(self, payload) -> bytes: ...
```

All `_`-prefixed methods are private to this class — no `KeyStore` ABC, no registry entry, no import path for anything outside this module to reach key material directly.

### 7. Error handling

* Missing/unreadable Secret, malformed PEM, malformed detached JWT, or signature mismatch → all fail **closed**: `verify_jwt` returns `False` (never raises), matching how `RequestValidation.validate_signature` already consumes the boolean today (raises `RequestValidationException` only on `False`, not on exception type). Exceptions are logged with `_logger.exception` for operability but swallowed at the boundary.
* `create_jwt_token` (outbound signing) is the one path allowed to raise — if Bridge's own private key can't be loaded, the outbound call must not silently proceed unsigned.
* `algorithms=[...]` is always passed explicitly and pinned server-side (never trust the JWT header's own `alg` claim to select verification behavior) — avoids algorithm-confusion attacks.

### 8. Config additions (`openg2p_fastapi_partner_auth/config.py`)

```
pyjwt_algorithm: str = "RS256"
pyjwt_public_key_secret_template: str = "{partner_mnemonic}-PublicKey"
pyjwt_private_key_secret_name: str = "OpenG2P-PrivateKey"
pyjwt_k8s_namespace: str = "default"
pyjwt_k8s_secret_data_field: str = "value"
pyjwt_k8s_in_cluster: bool = True
pyjwt_key_cache_ttl_seconds: int = 300
```

### 9. Out of scope for v1 (flagged, not designed here)

* Trusted-root / CA-chain validation when a full certificate is supplied (currently: signature validity only, no chain-of-trust check).
* Key rotation push/webhook — rotation is only picked up after `key_cache_ttl_seconds` expires.
* `include_certificate` / `include_cert_hash` on `create_jwt_token` (Key-Manager-specific extras with no local equivalent yet) — logged and ignored if requested.

### 10. Dependency changes

`openg2p-fastapi-partner-auth/pyproject.toml`:

* Remove `python-jose` (confirmed unused anywhere in this package's source).
* Add `PyJWT >=2.8.0`, `kubernetes >=29.0.0`.

### 11. Rollout

Per consuming app, one-line `Initializer` change:

```python
# before
KeymanagerCryptoHelper()
# after
PyJWTCryptoHelper()
```

No other code in `openg2p-g2p-bridge-partner-api`, `JWTValidationHelper`, or `JWTSignatureValidator` changes. Different OpenG2P products/deployments can run either implementation independently during migration.

### 12. Testing plan

* Unit tests with a real locally-generated RSA keypair, monkeypatching `_get_key` (no real K8s needed): round-trip sign→verify succeeds; tampered payload fails; unknown partner mnemonic fails closed; malformed detached-JWT input fails closed (no exception escapes).
* Separate, optional integration test for the K8s Secret-reading path only (`_k8s_client`/`_get_key`), run against `kind`/minikube in CI or skipped in environments without cluster access.
* Negative test for RBAC expectation: document (not code-enforce) that the `OpenG2P-PrivateKey` Secret must only be readable by the Bridge service account.
