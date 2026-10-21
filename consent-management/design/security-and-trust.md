---
description: >-
  The Consent Manager's trust model: keyholders, signing and key management
  (partner keys from Partner Management, the CM's own .p12 key and JWKS), the
  algorithm-confusion guard, ID-token checks, replay protection, caller
  authentication, and the threat model.
---

# Security & trust

The Consent Manager's value depends on its cryptography and trust boundaries.

**Who answers what.** "Is this a known party, is the signature theirs, and what may they ever receive?" is answered with keys and policies from **Partner Management (PM)**. "Did the subject consent, and what is released now?" is answered by the **CM**. The CM is not a PM partner; it stores no partner keys or policies and reads them from PM, cached ([Partner Management integration](partner-management-integration.md)).

## Trust model

There are three keyholders:

| Party               | Holds                                   | Used for                                                 |
| ------------------- | --------------------------------------- | -------------------------------------------------------- |
| **Partner**         | Its private signing key (managed in PM) | Signs its DCI requests and, if its policy allows partner-signed consents, the consent object it embeds |
| **Consent Manager** | Its own private signing key (`.p12`)    | Signs consent receipts (proof of decision) and, in the Exchange role, consent tokens |
| **OIDC Provider**   | Its private signing key                 | Signs ID tokens in the origination flow                  |

The CM uses the **public** counterpart of each, but stores only its own:

* **Partner public keys** — **fetched from PM's key API**, never stored in the CM database. A valid signature (checked against the PM-supplied PEM) proves the consent object came from a **known, active party** — the cornerstone of the "known party" check. If PM returns `404` for the partner (unknown, disabled, or no active keys) the CM **fails closed** and rejects.
* **CM public keys** — published at `GET /.well-known/jwks.json` so registries, partners, and auditors can independently verify receipts **without involving PM**.
* **IdP keys** — fetched from the IdP's JWKS endpoint to validate ID tokens in the origination flow.

## Signing

* **Asymmetric only.** All signatures — partner consent objects and CM receipts — use asymmetric keys (**RS256 / ES256 / EdDSA**). No symmetric/shared-secret signing: anyone holding the verifying key can check a signature without being able to forge one.
* **Canonicalisation.** An artefact is serialised as canonical JSON (sorted keys) before hashing, so the same artefact always gives the same bytes.
* **Key rotation.** Partner keys are rotated in PM: register a new `kid`, switch signing, retire the old key; the CM refetches on an unknown `kid`. The CM's own key is rotated by giving the new `.p12` a new `kid` ([Deployment](../deployment/README.md#signing-key-p12)).

### Verifying the partner's consent object

A partner-signed consent is a **compact JWS** (RFC 7515): the payload is the consent claims, the protected header carries `alg` and `kid`. This is the format the platform uses elsewhere (the registry's DCI envelope, G2P Bridge), verified through the shared openg2p-fastapi-common `CryptoHelper` (`partner-mgmt` backend). Because the JWS carries its signed bytes, there is no canonical-JSON matching between signer and verifier.

**Algorithm guard.** The `alg` must be in the CM's allowed set, in the policy's `allowed_signing_algs`, and match the key PM registered under that `kid`. This stops algorithm confusion and downgrade. Any failure (unknown or expired key, PM `404`, algorithm not allowed, bad signature) is a deny, `signature_invalid`. Where this sits in the pipeline: [Verification & enforcement](verification-and-enforcement.md#validation-pipeline-partner-signed-consent).

### Signing CM receipts

* **Detached proof.** A receipt signs the **hash** of the canonical artefact, binding the receipt to exact artefact content. Any later tampering invalidates the signature.
* **Private-key storage.** The CM's private key is loaded from a **PKCS#12 (`.p12`) keystore** mounted from a Kubernetes Secret on the partner API only. The algorithm follows the key type (Ed25519 → EdDSA, EC → ES256, RSA → RS256). Only the public half is published, at `GET /.well-known/jwks.json`, so **anyone can verify a receipt without PM**. The same key signs consent tokens.

## ID-token validation (origination)

When an ID token arrives (origination API), the CM:

1. finds the signing key by `kid` in the identity provider's JWKS and verifies the signature,
2. checks `exp`, and `iss` and `aud` when they are configured; the token's subject must be the request's,
3. stores **only `sha256(id_token)`**, never the token,
4. records the claims (including `amr`, the method) in the `AuthContext`.

Without a JWKS URL configured, the token is read unverified and recorded as `token_validated: false` (development only). The partner portal's national-ID login is checked separately ([Consent collection](consent-collection.md#national-id-authentication-in-the-partner-portal)).

## Replay protection

* Every consent object carries a unique `jti` and an `issued_at`.
* The CM rejects objects whose `issued_at` is outside a configurable **freshness window** (reason `replay`).
* A `jti` is recorded **per data controller** (unique on (`jti`, `data_controller`)). Re-presenting the _same_ object to the same registry returns that registry's existing decision (`consent_id`/`receipt_id`) rather than minting duplicates; a second registry named in the consent's `grants` gets its own decision and receipt.
* A registry can only use **its own grant**: it names its `data_controller`, and a consent with no grant for it is denied (`controller_not_granted`).

## Caller authentication

The partner-facing PDP API does **not** use Keycloak. Different endpoint classes are protected differently:

* **`/validate` and status (the PDP API)** — **no Keycloak.** A **partner-signed consent object** is verified locally against the partner key fetched from PM and replay-guarded by `jti` plus the freshness window; a consent the CM holds (by `consent_id` or lookup) was collected and verified by the CM itself. There is no bearer token on this path, and a lookup names only a partner and a subject, so the caller ↔ CM channel must be secured at the **transport level** — **Istio mTLS** and/or Kubernetes network policy — so only the registries (and, at an Exchange, the Composite) can reach `/validate`. **`/validate` is in-cluster only:** the PDP API is never routed through the ingress; callers use the in-cluster service.
* **Staff APIs** — the decision log (the console's Access Log) requires `CONSENT_MANAGER_ADMIN`; verifying assisted consents requires `CONSENT_MANAGER_APPROVER` (both configurable), checked against the staff realm's JWKS. The **partner portal API** requires a partner-realm token with a `partner_id` claim and a partner role, and shows only that partner's requests and consents. Partners, keys and policies are administered in PM (role `partner_manager`).
* **Subject APIs (`/my/*`)** — require a subject bearer token; every query is scoped to the token's identity, so a subject can only ever see their own consents.
* **Public** — only the CM's **public keys** (`/.well-known/jwks.json`) are published outside the cluster, so departments on other clusters, partners and auditors can verify its signatures. At an Exchange, the consent-token status endpoint is published too, but only where a department checks token status. Receipt fetch is unauthenticated (signatures make it self-verifying) but in-cluster.

## Privacy by design

* **Minimisation** — the CM returns only `consent_scope ∩ policy_scope`; the registry releases only that.
* **Purpose limitation** — decisions are bound to a purpose code; a consent for one purpose can't authorise another.
* **No raw secrets at rest** — ID tokens are hashed; partner private keys never touch the CM, and partner _public_ keys are not stored either — they are fetched from PM per decision and cached.
* **Append-only audit** — every permit and deny is written to the immutable **decision log**, and each consent has a **signed receipt**. These are the authoritative audit record.

## Threat model (selected)

| Threat                                    | Mitigation                                                                                                                                                    |
| ----------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Forged consent from an unknown party      | Signature must verify against a partner key fetched from PM; PM `404` (unknown/disabled/no active key) fails closed (`unknown_partner` / `signature_invalid`) |
| Algorithm-confusion / alg downgrade       | The JWS `alg` must match the algorithm PM registered for that `kid` and be allowed by the policy, else `signature_invalid`                                    |
| PM outage during a decision               | Per-pod cache serves the last keys and policies PM gave within the hard TTL; beyond it the CM fails closed (`policy_unavailable`)                              |
| Partner over-asking beyond its contract   | Policy intersection caps scope (`scope_exceeds_policy`); at an Exchange, only granted use cases (`use_case_not_granted`)                                      |
| Partner claiming a consent it never collected | Partner-signed consents refused unless the partner's policy allows them (`partner_consent_not_accepted`); consents collected through the CM carry national-ID authentication and evidence |
| Replaying a captured consent object       | `jti` + freshness window (`replay`)                                                                                                                           |
| Using consent meant for another recipient | Audience check (`audience_mismatch`)                                                                                                                          |
| Using one registry's grant at another     | Grant selected by the calling registry's `data_controller`; policy per (partner, controller) (`controller_not_granted`, `unknown_partner`)                    |
| Using a consent for a different person    | `subject_mismatch` when the caller declares a same-type subject; the registry also checks the consent's subject against what it searches                     |
| Acting on revoked consent                 | Checked on every `/validate` (`revoked`); a status endpoint for callers that cache; an Exchange consent token already issued lapses within its lifetime (default 5 minutes) |
| Tampering with a stored artefact          | Receipt signs the artefact hash; mismatch is detectable                                                                                                       |
| Key compromise                            | Key revocation + rotation; short validity windows                                                                                                             |
| Repudiation of a decision                 | CM-signed receipt + immutable decision log                                                                                                                    |
