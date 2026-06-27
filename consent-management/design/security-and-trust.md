---
description: >-
  The trust model, cryptographic signing and key management, ID-token
  validation, replay protection, and the threat model for the Consent Manager.
---

# Security &amp; trust

The Consent Manager's value depends entirely on its cryptography and trust boundaries. This page
defines them.

## Trust model

There are three keyholders:

| Party | Holds | Used for |
| --- | --- | --- |
| **Partner** | Its private signing key | Signs the consent object it embeds in a registry request |
| **Consent Manager** | Its private signing key | Signs consent receipts (proof of decision) |
| **OIDC Provider** | Its private signing key | Signs ID tokens in the origination flow |

The CM stores the **public** counterpart of each:

* **Partner public keys** — registered at onboarding (or fetched from a partner JWKS URL). A valid
  signature proves the consent object came from a **known, onboarded party** — the cornerstone of
  the "known party" check.
* **CM public keys** — published at `GET /.well-known/jwks.json` so registries, partners, and
  auditors can independently verify receipts.
* **IdP keys** — fetched from the IdP's JWKS endpoint to validate ID tokens.

## Signing

* **Asymmetric only.** Receipts are signed with **EdDSA (ed25519)** by default (ES256/RS256
  supported). No symmetric/shared-secret signing — anyone holding the verifying key can check a
  signature without being able to forge one.
* **Detached proof.** A receipt signs the **hash** of the canonical artefact, binding the receipt
  to exact artefact content. Any later tampering invalidates the signature.
* **Canonicalisation.** Artefacts are serialised canonically (stable key ordering, normalised
  JSON-LD) before hashing so the same logical artefact always yields the same hash.
* **Key rotation.** Both partner and CM keys carry `kid`, `not_before`, `not_after`. Rotation =
  publish new key → switch signing → retire old key, with overlap so in-flight objects still
  verify.
* **Private-key storage.** The CM's signing private key is loaded from a **PKCS#12 (`.p12`)
  keystore** (key + certificate), mounted from a Kubernetes Secret. The signing algorithm is
  derived from the key type (Ed25519 → EdDSA, EC → ES256, RSA → RS256). The private key never
  leaves the pod; only the public half is published via JWKS.

## ID-token validation (origination)

When an ID token arrives, the CM:

1. resolves the signing key via `kid` from the IdP's JWKS,
2. verifies the JWS signature,
3. validates claims: `iss` matches the configured issuer, `aud` matches this controller, `exp` is
   in the future, `iat`/`auth_time` are sane, and `amr` records the auth method,
4. stores **only `sha256(id_token)`** — the raw token is never persisted,
5. records the verified claims in the `AuthContext`.

## Replay protection

* Every consent object carries a unique `jti` and an `issued_at`.
* The CM rejects a `jti` it has already processed (within the validity window) and rejects objects
  whose `issued_at` is outside a configurable **freshness window** (reason `replay`).
* Re-presenting the *same* valid object returns the existing `consent_id`/`receipt_id`
  idempotently rather than minting duplicates.

## Caller authentication (Keycloak)

Protected endpoints require a **Keycloak-issued bearer token**, validated against the realm
JWKS (issuer, signature, optional audience). Roles are read from both `realm_access` and every
`resource_access.*` client block, exactly as in the OpenG2P AWE service.

* **`/validate` and status** — called by the registry/PEP using a Keycloak **service-account
  token** (client-credentials). The consent object's own signature is the application-layer proof
  on top; this is defense-in-depth and may also be fronted by mTLS at the ingress.
* **Partner/policy admin APIs** — require the `CONSENT_MANAGER_ADMIN` role (configurable).
  Admin endpoints carry **no** consent object, so the signature mechanism does not protect them —
  role-based auth is essential here.
* **Subject APIs (`/my/*`)** — require a subject bearer token; every query is scoped to the
  token's identity, so a subject can only ever see their own consents.
* **Public** — receipt fetch and `/.well-known/jwks.json` are unauthenticated (signatures make
  them self-verifying).

## Privacy by design

* **Minimisation** — the CM returns only `consent_scope ∩ policy_scope`; the registry releases
  only that.
* **Purpose limitation** — decisions are bound to a purpose code; a consent for one purpose can't
  authorise another.
* **No raw secrets at rest** — ID tokens are hashed; partner private keys never touch the CM.
* **Append-only audit** — every decision and transition is immutable, supporting non-repudiation
  and dispute resolution without exposing payload data.

## Threat model (selected)

| Threat | Mitigation |
| --- | --- |
| Forged consent from an unknown party | Signature must verify against an onboarded partner key (`unknown_partner` / `signature_invalid`) |
| Partner over-asking beyond its contract | Policy intersection caps scope (`scope_exceeds_policy`) |
| Replaying a captured consent object | `jti` + freshness window (`replay`) |
| Using consent meant for another recipient | Audience check (`audience_mismatch`) |
| Acting on revoked consent | Live status endpoint + revocation notifications (`revoked`) |
| Tampering with a stored artefact | Receipt signs the artefact hash; mismatch is detectable |
| Key compromise | Key revocation + rotation; short validity windows |
| Repudiation of a decision | CM-signed receipt + immutable decision log |
