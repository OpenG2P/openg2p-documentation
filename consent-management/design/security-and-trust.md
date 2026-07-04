---
description: >-
  The trust model, the authN/authZ split with Partner Management, signing and
  key management (partner keys from PM, CM receipts via .p12/JWKS), the
  algorithm-confusion guard, replay protection, and the
---

# Security & trust

The Consent Manager's value depends entirely on its cryptography and trust boundaries. This page defines them.

## authN vs authZ — who owns what

The CM's trust model splits cleanly along two axes, and the split decides where keys live:

* **Authentication (who the partner is)** is owned by the **Partner Management (PM)** service. PM holds partner identity, organisation, lifecycle, and — crucially — the partner's **signing keys**. "Is this a known party, and is this signature genuinely theirs?" is answered with material from PM.
* **Authorization (what the partner may receive)** is owned by the **Consent Manager**. CM holds the **data-share policy** and the consent decision. "Given a genuine partner, what fields may they get for this purpose?" is answered entirely inside CM.

The CM is a **verifier / PDP, not a PM partner** — it is _not_ onboarded as a partner in PM. It does not store partner public keys, and it does not poll a partner `jwks_url`; both mechanisms have been removed. Instead the CM **fetches partner keys from PM on demand** and caches them per pod (see [Partner Management Integration](partner-management-integration.md)).

## Trust model

There are three keyholders:

| Party               | Holds                                   | Used for                                                 |
| ------------------- | --------------------------------------- | -------------------------------------------------------- |
| **Partner**         | Its private signing key (managed in PM) | Signs the consent object it embeds in a registry request |
| **Consent Manager** | Its own private signing key (`.p12`)    | Signs consent receipts (proof of decision)               |
| **OIDC Provider**   | Its private signing key                 | Signs ID tokens in the origination flow                  |

The CM uses the **public** counterpart of each, but stores only its own:

* **Partner public keys** — **fetched from PM's key API**, never stored in the CM database. A valid signature (checked against the PM-supplied PEM) proves the consent object came from a **known, active party** — the cornerstone of the "known party" check. If PM returns `404` for the partner (unknown, disabled, or no active keys) the CM **fails closed** and rejects.
* **CM public keys** — published at `GET /.well-known/jwks.json` so registries, partners, and auditors can independently verify receipts **without involving PM**.
* **IdP keys** — fetched from the IdP's JWKS endpoint to validate ID tokens in the origination flow.

## Signing

* **Asymmetric only.** All signatures — partner consent objects and CM receipts — use asymmetric keys (**RS256 / ES256 / EdDSA**). No symmetric/shared-secret signing: anyone holding the verifying key can check a signature without being able to forge one.
* **Canonicalisation.** Artefacts are serialised canonically (stable key ordering, normalised JSON-LD) before hashing/signing so the same logical artefact always yields the same bytes.
* **Key rotation.** Both partner keys (in PM) and CM keys carry `kid`, `not_before`, `not_after`. Rotation = publish new key → switch signing → retire old key, with overlap so in-flight objects still verify.

### Verifying the partner's consent object

The consent object is a **compact JWS** (RFC 7515) — `base64url(header).base64url(payload).base64url(signature)`. The **payload** is the consent claims (jti, subject, aud, data_scopes, purpose, validity, …); the **protected header** carries `alg` and `kid`. This is the same signature format the platform uses everywhere else — the Registry DCI envelope and G2P Bridge requests — so a single verify path covers all of them.

Verification runs through the shared **openg2p-fastapi-common `CryptoHelper`** (`build_crypto_helper`, `partner-mgmt` backend). To verify, the CM:

1. recovers the claims from the JWS payload (unverified) to identify the partner by `aud` and read the requested scopes/validity,
2. reads `kid` + `alg` from the JWS protected header and fetches the matching partner key from PM (`GET {pm}/keys/{reference_id}` — reference `PARTNER_<sender_id>` / the partner's `partner_mgmt_id` — served from the per-pod cache),
3. enforces **algorithm safety** — `alg` must be in the allowed set and must match a key PM registered under that `kid` (prevents alg-confusion / downgrade), and additionally `alg` must be permitted by the partner's policy (`allowed_signing_algs`),
4. verifies the JWS signature against the PM-supplied public key.

Because a JWS carries its signed bytes verbatim in the payload segment, there is **no canonical-JSON byte-matching** between signer and verifier to get wrong. Any failure — unknown/expired key, `404` from PM, algorithm not allowed, or a bad signature — is a **REJECT** (fail-closed). See [Verification & enforcement](verification-and-enforcement.md) and [Registry integration](registry-integration.md).

### Signing CM receipts

* **Detached proof.** A receipt signs the **hash** of the canonical artefact, binding the receipt to exact artefact content. Any later tampering invalidates the signature.
* **Private-key storage.** The CM's signing private key is loaded from a **PKCS#12 (`.p12`) keystore** (key + certificate) minted by the partner-api, mounted from a Kubernetes Secret. The signing algorithm is derived from the key type (Ed25519 → EdDSA, EC → ES256, RSA → RS256). The private key never leaves the pod; only the public half is published via `GET /.well-known/jwks.json`, so **anyone can verify a receipt with no PM involvement**.

## ID-token validation (origination)

When an ID token arrives, the CM:

1. resolves the signing key via `kid` from the IdP's JWKS,
2. verifies the JWS signature,
3. validates claims: `iss` matches the configured issuer, `aud` matches this controller, `exp` is in the future, `iat`/`auth_time` are sane, and `amr` records the auth method,
4. stores **only `sha256(id_token)`** — the raw token is never persisted,
5. records the verified claims in the `AuthContext`.

## Replay protection

* Every consent object carries a unique `jti` and an `issued_at`.
* The CM rejects a `jti` it has already processed (within the validity window) and rejects objects whose `issued_at` is outside a configurable **freshness window** (reason `replay`).
* Re-presenting the _same_ valid object returns the existing `consent_id`/`receipt_id` idempotently rather than minting duplicates.

## Caller authentication

The partner-facing PDP API does **not** use Keycloak. Different endpoint classes are protected differently:

* **`/validate` and status (the PDP API)** — **no Keycloak.** Trust is the **partner-signed consent object**, verified locally against the partner key fetched from PM, and replay-guarded by `jti` plus the freshness window. There is no bearer token on this path; the signature _is_ the application-layer proof of a known party. The Registry ↔ CM channel itself is secured at the **transport level** — **Istio mTLS** and/or Kubernetes network policy — so only the registry can reach `/validate`.
* **Partner/policy admin APIs** — require the `CONSENT_MANAGER_ADMIN` role (configurable), validated against the realm JWKS. Admin endpoints carry **no** consent object, so the signature mechanism does not protect them — role-based auth is essential here. Note these bind _policy_; partner identity and keys are administered in **PM**, not CM.
* **Subject APIs (`/my/*`)** — require a subject bearer token; every query is scoped to the token's identity, so a subject can only ever see their own consents.
* **Public** — receipt fetch and `/.well-known/jwks.json` are unauthenticated (signatures make them self-verifying).

## Privacy by design

* **Minimisation** — the CM returns only `consent_scope ∩ policy_scope`; the registry releases only that.
* **Purpose limitation** — decisions are bound to a purpose code; a consent for one purpose can't authorise another.
* **No raw secrets at rest** — ID tokens are hashed; partner private keys never touch the CM, and partner _public_ keys are not stored either — they are fetched from PM per decision and cached.
* **Append-only audit** — every permit/deny is written to an immutable in-house **DecisionLog**, and each permit yields a **signed receipt** (Kantara / ISO-27560), self-verifying via the CM JWKS. These two are the **authoritative** audit record. A forwarder to the OpenG2P **Audit Manager** (CloudEvents over HTTP, Kafka-buffered) is a **planned** add-on for centralised long-term compliance — not required for the CM to be trustworthy.

## Threat model (selected)

| Threat                                    | Mitigation                                                                                                                                                    |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Forged consent from an unknown party      | Signature must verify against a partner key fetched from PM; PM `404` (unknown/disabled/no active key) fails closed (`unknown_partner` / `signature_invalid`) |
| Algorithm-confusion / alg downgrade       | Declared `signature.algorithm` must equal the algorithm PM reports for that key, else reject                                                                  |
| PM outage during a decision               | Per-pod cache serves last-known-good within the hard TTL; beyond it the CM fails closed                                                                       |
| Partner over-asking beyond its contract   | Policy intersection caps scope (`scope_exceeds_policy`)                                                                                                       |
| Replaying a captured consent object       | `jti` + freshness window (`replay`)                                                                                                                           |
| Using consent meant for another recipient | Audience check (`audience_mismatch`)                                                                                                                          |
| Acting on revoked consent                 | Live status endpoint + revocation notifications (`revoked`)                                                                                                   |
| Tampering with a stored artefact          | Receipt signs the artefact hash; mismatch is detectable                                                                                                       |
| Key compromise                            | Key revocation + rotation; short validity windows                                                                                                             |
| Repudiation of a decision                 | CM-signed receipt + immutable decision log                                                                                                                    |
