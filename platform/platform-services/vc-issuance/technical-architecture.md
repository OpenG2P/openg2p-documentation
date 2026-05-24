---
description: >-
  The pull-based hosted-wallet architecture — Logto as the OIDC authorization
  server, Mimoto's authorization_code/PKCE download, Certify's Registry REST
  connector, key management, multi-application/multi-issuer, and configuration.
---

# Technical Architecture

## Why "pull", and why an OIDC authorization server is mandatory

The hosted wallet ingests credentials in exactly one way: **Mimoto performs an OpenID4VCI
`authorization_code` (PKCE) download** from Certify. Mimoto's download API mandates an `issuer`,
an OAuth **`code`**, `grantType=authorization_code`, and a PKCE **`codeVerifier`**. Consequences:

* There is **no way to "push" a pre-built VC into the hosted wallet** — Mimoto pulls it from
  Certify itself.
* That pull is authorized by a token from an **OIDC authorization server** (here **Logto**), so
  an OIDC AS doing `authorization_code` + PKCE is **mandatory** for the hosted-wallet path.
* Because Certify only receives a *token*, it must **source the claims itself** → a **pull**
  model: a custom connector that fetches the citizen's data from the **Registry REST API**.

This is the MOSIP-standard shape of the stack; the portal does **not** push claims to Certify.

## Components

```
 Branded Inji Web (frontend) ──► Mimoto (BFF + storage + PDF) ──► Inji Certify (issuer)
        │                              │                               │
        └──── OIDC (PKCE) ───► Logto (OIDC AS / citizen IdP)           └─ Postgres plugin ─► certify.beneficiary_vc_view
                                                                        │                     (phone-keyed view over Registry data:
                                                                        │                      FDW / sync / cross-schema)
                              all on Kubernetes, reusing cluster PostgreSQL; Certify keys in .p12
                              (Phase 2 alternative: a custom REST connector → OpenG2P Registry API)
```

* **Logto** — citizen IdP and **OIDC authorization server**: phone+OTP login, issues the
  `authorization_code`/token, exposes discovery + JWKS that Certify trusts.
* **Inji Web** — hosted-wallet frontend, branded, embedded as the portal "My Wallet" tab.
* **Mimoto** — hosted-wallet backend: runs the token exchange + credential download, **stores
  the signed VC** (`verifiable_credentials` table), holds the wallet's custodial keys, renders
  **PDF**.
* **Inji Certify** — the issuer: validates the token, builds the VC from a Velocity template,
  signs it with a `.p12`-held key. Hosts the **custom Registry connector**.
* **OpenG2P Registry** — exposes a **REST API** the connector calls (no direct DB access).

## PKCE (how the auth code is protected)

PKCE (Proof Key for Code Exchange) binds the auth code to the client that started the flow:

1. the **frontend** (branded Inji Web) generates a random **`code_verifier`** and
   **`code_challenge = BASE64URL(SHA-256(verifier))`**;
2. it sends the **challenge** in the `/authorize` redirect to Logto;
3. Logto returns an **auth code**; the frontend passes **code + verifier** to Mimoto;
4. Mimoto sends **code + verifier** to Logto's token endpoint; Logto checks
   `SHA-256(verifier) == challenge` and issues the token.

PKCE is generated **client-side** by Inji Web (automatic — no work for us). Mimoto only consumes
the verifier.

## How Certify gets the claims

Certify produces a VC for whoever the token identifies, so it must fetch that citizen's claims at
issuance. The full design is in **[Registry Data Connector](registry-data-connector.md)**; in
summary:

* **Phase 1 — DB-direct (stock Postgres plugin, no Certify code).** Certify uses
  `PostgresDataProviderPlugin` to run **one SQL query per credential scope** against a
  **phone-keyed, active-only view** that exposes the Registry data inside Certify's database. The
  query's `:id` parameter is bound to the token **`sub`**, so **Logto must present the phone
  number as `sub`**. Because the plugin reads **Certify's own database**, the Registry data is
  surfaced there via **FDW / a synced table / a same-database view**. Presence and active/inactive
  status are handled in the SQL (no row → "no eligible record").
* **Phase 2 — custom REST connector (alternative).** A custom `DataProviderPlugin` that calls the
  **Registry REST API**, reads the `phone_number` claim (so it does not need `sub`=phone), avoids
  DB coupling, and lets the Registry own authorization. Costs custom Java.

> **Identity resolution.** Authentication is Logto's job; the connector consumes the citizen's
> **phone number** to look up the Registry, which is assumed **one-to-one** phone → functional ID.

## Multi-application and multi-issuer

* **One shared Certify** serves Registry first, then PBMS, SPAR. They are **claim sources**, not
  issuers — each contributes data via its own connector/credential type.
* Each **credential type** is one row in Certify's `credential_config` (Velocity template,
  context, format, allowed subject fields, **issuer DID**, **signing key**). Adding a credential
  is a **configuration** change.
* **Issuing authority is not hardcoded:** `didUrl` + `keyManagerAppId` are per credential type,
  so sub-departments can issue under different DIDs/keys on the same Certify. A **single
  authority** is assumed for now; the model already supports more without code changes.

## Key management

* Embedded keymanager with a **PKCS12 `.p12`** keystore (**no HSM**). Master key in the `.p12`;
  application signing keys auto-generated and stored **encrypted in PostgreSQL**
  (`key_alias`/`key_store`), wrapped by the master key.
* Public keys published via `/.well-known/jwks.json` and the issuer **DID document**.
* **The `.p12` + key tables are the issuer identity** — they must be **persisted and backed up**;
  regenerating them invalidates all previously issued VCs. (See [Deployment](deployment.md).)

## Configuration model (three layers)

1. **Service config — Spring properties + env overrides** (DB connection, `.p12` path/password,
   plugin selection, the trusted OIDC issuer = **Logto** `issuer-uri`/`jwk-set-uri`, caches).
2. **Credential definitions — the `credential_config` DB table** (per credential type: template,
   issuer DID, signing key, format, allowed subject fields). Seeded via SQL or the
   `credential-configurations` API.
3. **Keys — `.p12` + key tables**, auto-managed by the embedded keymanager.

Mimoto connects to Certify purely by **configuration** (`mimoto-issuers-config.json` registering
Certify as an issuer with Logto as its auth server) — no Mimoto code changes.

## Later scenarios (not Phase 1)

* **Online sharing to third parties (OpenID4VP)** — present from the hosted wallet via Inji Web.
* **Device wallet (Inji Mobile 0.22.1)** via a credential-offer QR — same Certify/Logto config.

Both reuse the same issuer and IdP; they add presentation/▸device flows on top of the Phase-1
issuance described here.
