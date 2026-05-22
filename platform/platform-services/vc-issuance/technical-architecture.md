---
description: >-
  How Inji Certify works internally, how OpenG2P applications integrate with it,
  the multi-application and multi-issuer design, authentication, key management,
  and the configuration model.
---

# Technical Architecture

## Inji Certify in brief

Inji Certify is a Spring Boot service that implements **OpenID4VCI (draft 13)** and issues
**W3C Verifiable Credentials** in formats `ldp_vc` (JSON-LD), `vc+sd-jwt`, and ISO mDoc/mDL.
Internally:

* **Credential endpoint** — `POST /v1/certify/issuance/credential`, plus discovery at
  `/.well-known/openid-credential-issuer`.
* **Templating** — each credential's body is an **Apache Velocity template** stored in the DB;
  the data plugin supplies the values.
* **Plugins** — a `DataProviderPlugin` supplies the subject data; Certify owns templating and
  signing. (For OpenG2P we use the **pre-authorized-code data provider**, see below.)
* **Keymanager** — embedded; signs in-process using a key referenced per credential type.

## Integration model: push, with Certify as its own authorization server

There are two ways data can reach Certify, and two ways the wallet can get a token. OpenG2P
uses the simplest, cleanest combination:

### Data: **push** the claims from the source application

The Registry/PBMS `bene-portal-api` is already authenticated as the citizen and already has
the citizen's data. It **pushes the claims** into the credential offer via
`POST /pre-authorized-data`. Certify caches those claims and issues from them using the
built-in **`PreAuthDataProviderPlugin`** (`mosip.certify.integration.data-provider-plugin=PreAuthDataProviderPlugin`).

* ✅ Certify stays a generic signer; **all authorization logic stays in the source application**
  (the registry decides what to issue, to whom).
* ✅ No custom Certify plugin and no Certify→OpenG2P callback needed.
* The alternative — a custom *pull* plugin where Certify calls back into the registry at
  redemption time — was rejected: it couples Certify to each source application and needs
  Certify-held credentials into OpenG2P.

### Token: **Certify acts as its own authorization server** (pre-authorized code)

In the pre-authorized-code flow, the **authorization happened at the portal** (the citizen
logged in via IAM before any code was minted). Certify therefore issues the wallet's access
token itself via `POST /oauth/token`, and validates it against its own JWKS. No second login,
and **eSignet is not required for the wallet step**.

> The portal must call `POST /pre-authorized-data` as a **trusted machine-to-machine client**
> — this endpoint must not be open to the public. The pre-authorized code is only ever minted
> *after* the source application authenticated and authorized the citizen.

## Multi-application: one Certify, many sources

Registry, PBMS and SPAR are **sources of claims**, not separate issuers. They each:

1. authenticate the citizen (via the Beneficiary Portal / IAM),
2. map their own record to the claim set for a credential type,
3. push those claims to the **same** Inji Certify.

```
 Registry bene-portal-api ─┐
 PBMS bene-portal-api ─────┼──►  POST /pre-authorized-data  ──►  Inji Certify (shared)
 SPAR  …          ─────────┘                                       │
                                                       credential_config per VC type
```

Each **credential type** is one row in Certify's `credential_config` (its Velocity template,
context, type, format, allowed subject fields, display, and — crucially — its issuer DID and
signing key). Adding a new source/credential is a **configuration change** (a new
`credential_config`), not a code change in Certify.

> **Source application ≠ issuing authority.** Registry/PBMS are data sources. The *issuer* is
> the authority whose DID/key signs the VC (next section).

## Multi-issuer: the issuing authority is not hardcoded

A **single issuing authority** is assumed for the initial rollout, but the design must not bake
it in, because within one authority different **sub-departments** may issue different VCs.

This is supported natively because issuer identity is **per `credential_config`**, not global:

| `credential_config` field | Meaning |
|---|---|
| `didUrl` | the **issuer DID** that appears as the VC `issuer` and in the proof `verificationMethod` |
| `keyManagerAppId` / `keyManagerRefId` | **which signing key** (in the embedded keymanager) signs this credential |
| `signatureAlgo` / `signatureCryptoSuite` | e.g. `EdDSA` / `Ed25519Signature2020` |

So credential type A can be issued under `did:web:dept-a…` with key `CERTIFY_VC_SIGN_A`, and
type B under `did:web:dept-b…` with key `CERTIFY_VC_SIGN_B`, on the **same** Certify. Today
both can point to one authority DID; tomorrow they can diverge with no code change.

> **Do not rely on the global default issuer** (`mosip.certify.identifier` /
> `data-provider-plugin.did-url`). Drive the issuer DID and key from the per-credential
> `credential_config` so multiple sub-departments work out of the box.

### One instance vs. many

* **One shared Certify per issuing authority**, serving all that authority's apps (Registry,
  PBMS, SPAR) and credential types — the recommended model for OpenG2P.
* **Genuinely separate legal authorities** should get **separate Certify instances** (separate
  keystore/master key, DB, and DID resolution), for clean key isolation and lifecycle.

## Authentication

| Concern | Owned by |
|---|---|
| Citizen authentication (National ID / OTP / Keycloak) | **eSignet / IAM**, at the Beneficiary Portal — once |
| Authorizing & minting the credential offer | **Registry/PBMS bene-portal-api** (after IAM auth) |
| Minting + validating the wallet's access token | **Inji Certify** (its own AS, pre-auth code) |
| Holder key / proof of possession | the **wallet** (binds the VC to the device) |

eSignet is essential for the **citizen's portal login**, but is **not** additionally required
for the wallet's token because the pre-authorized-code grant treats the portal login as the
authorization event.

## Key management

Certify uses its **embedded keymanager** (the `kernel-keymanager` library inside the Certify
process) with a **PKCS12 (`.p12`) keystore — no HSM**.

* **Master key** → the `.p12` file.
* **Application signing keys** (e.g. `CERTIFY_VC_SIGN_ED25519`) → generated automatically on
  first boot and stored **encrypted in Certify's PostgreSQL** (`key_alias` / `key_store`),
  wrapped by the master key. Validity/rotation is governed by `key_policy_def`.
* **Public keys** are published for verifiers via `/.well-known/jwks.json` and the issuer
  **DID document**.

Because there is no HSM, the **`.p12` + the key tables are the issuer identity**:

* they **must be persisted** (mounted on durable storage) and **backed up**;
* losing or regenerating them mints a **new issuer key**, which makes **all previously issued
  VCs unverifiable**.

No OpenG2P application ever handles signing keys — they never leave Certify + its keymanager.

## Configuration model (three layers)

Configuration is **not** all environment variables. It lives in three places:

1. **Service config — Spring properties + env-var overrides.** Mounted
   `certify-*.properties` files (DB connection, `.p12` path/password, plugin selection, cache
   names, Certify-as-AS settings, default identifier). Any property is overridable by an env
   var via relaxed binding (`mosip.certify.domain.url` → `mosip_certify_domain_url`).
2. **Issuer / credential definitions — the `credential_config` DB table.** The issuer DID,
   signing key, Velocity template, allowed subject fields, format and display per credential
   type. Set at DB init (SQL) **or** at runtime via the `POST /credential-configurations` API.
   *This is where "issuing authority details" live — not env vars.*
3. **Keys — `.p12` + key tables**, auto-managed by the embedded keymanager.

See [Deployment](deployment.md) for how these are supplied on Kubernetes, and
[API Reference](api-reference.md) for the exact payloads.
