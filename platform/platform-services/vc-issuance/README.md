---
description: >-
  Issuing W3C Verifiable Credentials from OpenG2P data sources (Registry first,
  then PBMS, SPAR, …) using MOSIP Inji Certify, held in a hosted wallet (Inji
  Web + Mimoto) and downloadable as a PDF from the citizen's portal.
---

# VC Issuance

## Overview

**VC Issuance** turns a citizen's OpenG2P data (their **Registry** record first; later **PBMS**,
**SPAR**, …) into a standards-based **Verifiable Credential (VC)** held in a **hosted wallet**
and downloadable as a **PDF** from the citizen's portal.

The building blocks are all MOSIP **Inji** components plus an OpenID Connect identity provider:

| Component | Role | Version |
|---|---|---|
| **Inji Certify** | OpenID4VCI credential **issuer** (signs the VC) | 0.14.0 |
| **Mimoto** | Hosted-wallet **backend**: downloads from Certify, **stores** the VC, renders **PDF** | 0.22.0 |
| **Inji Web** | Hosted-wallet **frontend** (branded, embedded in the dept portal) | 0.17.0 |
| **Inji Mobile** | Device wallet (later/optional scenario) | 0.22.1 |
| **Logto** | Citizen **IdP** — phone-number + OTP login, OIDC authorization server | self-hosted (OSS) |
| **PostgreSQL** | Reused from the existing OpenG2P cluster | existing |

> **Phase 1 scope:** citizen logs in (phone + OTP via Logto), generates a **Registry** credential
> into the **Mimoto-based hosted wallet** (Inji Web + Mimoto **only** — no device wallet in
> Phase 1), and downloads it as a **PDF**. Certify reads the citizen's claims **directly from the
> database** via the stock Postgres plugin (see [Registry Data Connector](registry-data-connector.md)).
> eSignet is **not** assumed present (see [Identity & IdP](identity-and-idp.md)).

## Design principles

* **Citizen login is phone-number + OTP**, provided by **Logto** (a citizen-oriented OIDC IdP).
  eSignet is **not** required; if a deployment has it, see the optional section in
  [Identity & IdP](identity-and-idp.md).
* **Hosted wallet, pulled — not pushed.** A credential enters the hosted wallet only by
  Mimoto performing an OpenID4VCI **`authorization_code` (PKCE)** download from Certify. Certify
  therefore receives a **token** and **pulls the citizen's claims** at issuance.
* **Phase 1 data access = DB-direct.** Certify uses the stock **Postgres DataProvider plugin**
  to read a **phone-keyed view** that exposes the Registry data inside Certify's database
  (the lookup key `:id` = the token `sub` = the citizen's phone number). A custom **REST**
  connector is the cleaner Phase-2 alternative. See
  [Registry Data Connector](registry-data-connector.md).
* **One shared Certify, many sources.** Registry/PBMS/SPAR are *claim sources*, not issuers.
  Each credential type is one `credential_config` (template + issuer DID + signing key).
* **Issuing authority is configuration, not code** — single authority assumed for now, but DID
  and key are per credential type, so sub-departments can diverge without code changes.
* **Keys stay inside Certify** — embedded keymanager + **PKCS12 `.p12`** (no HSM).
* **Reuse the cluster** — Kubernetes + the existing PostgreSQL.
* **Departments embed a branded Inji Web** as a "My Wallet" tab (see
  [Department Integration](department-integration.md)).

## End-to-end flow (Phase 1 — hosted wallet + PDF)

```
 Citizen (desktop browser)
   │ 1. opens the Dept/Beneficiary Portal → "My Wallet" tab (branded Inji Web, same parent domain)
   │ 2. login: phone number + OTP   ─────────────────────►  Logto (OIDC AS / citizen IdP)
   │                                ◄─────────────────────  session (SSO; reused everywhere)
   │ 3. picks a Registry credential → "Generate"
   ▼
 Branded Inji Web (frontend, Option C)
   │ 4. OIDC authorization_code + PKCE to Logto (silent via SSO) → auth code
   │ 5. POST /wallets/{id}/credentials
   │      { issuer=Certify, credentialConfigurationId, code, grantType=authorization_code, codeVerifier }
   ▼
 Mimoto (hosted-wallet backend)
   │ 6. token exchange with Logto (code + verifier) → access token
   │ 7. calls Certify credential endpoint (Bearer token)
   ▼
 Inji Certify (issuer)
   │ 8. Postgres plugin: :id = token sub = phone → query certify.beneficiary_vc_view
   │    (a phone-keyed, active-only view over the Registry data) → claims
   │ 9. render VC from template, sign with .p12 key → signed VC
   ▼
 Mimoto stores the signed VC  (verifiable_credentials table)
   │ 10. Inji Web lists it; "Download PDF" → Mimoto renders PDF
   ▼
 Citizen downloads the PDF
```

Key point: the citizen **logs in once** (phone+OTP at the portal); the wallet deposit reuses
that **Logto SSO** silently. Certify **pulls** the claims at issuance (Phase 1: from a
phone-keyed view over the Registry DB); the portal does **not** push claims.

## Sub-pages

| Page | Contents |
|------|----------|
| [Functional Specifications](functional-specifications.md) | Actors, phone-OTP login, the "My Wallet" journey, deposit, PDF, sequence diagram |
| [Technical Architecture](technical-architecture.md) | The pull model, Logto as OIDC AS, Mimoto auth-code/PKCE, key management, multi-app/issuer, config |
| [Registry Data Connector](registry-data-connector.md) | **Phase 1 DB-direct**: Postgres plugin, `:id`=`sub`=phone, the phone-keyed view, active/missing handling; REST as the Phase-2 alternative |
| [Identity & IdP](identity-and-idp.md) | Phone-OTP login, **Logto vs Keycloak**, citizen vs staff IdP, and the optional **eSignet** section |
| [Department Integration](department-integration.md) | Embedding options **A–D** (we use **C**), branding, shared-Logto SSO, the Registry data connection |
| [API Reference](api-reference.md) | Mimoto wallet APIs, Certify endpoints, the Registry connector contract |
| [Deployment](deployment.md) | Kubernetes, reusing cluster PostgreSQL, the published dockers + Logto, persisting `.p12` |
| [Local Developer Trial](local-setup.md) | A verified developer smoke-test of Certify issuance (simplified flow, not the production model) |

## Open items (to finalize during implementation)

These do not change the architecture but must be decided/built before go-live:

* **Logto token `sub` = phone number.** The Phase-1 Postgres plugin keys on the token `sub`, so
  Logto must present the **phone number** as the subject identifier. Verify Logto's behaviour (if
  `sub` is an opaque id, adapt or move to the REST connector). See
  [Registry Data Connector](registry-data-connector.md).
* **Exposing the Registry data inside Certify's DB.** The stock Postgres plugin reads Certify's
  own database, so the Registry data must be reachable there — via **FDW**, a **synced table**, or
  a same-database cross-schema **view** — surfaced as a phone-keyed, active-only view.
* **Phone → record resolver rule.** The **one-to-one** phone → functional ID assumption, plus the
  no-match / inactive / multiple-match handling (largely expressed in the view's SQL).
* **Issuer `did:web` hosting domain.** The stable, public HTTPS domain where each credential's
  `did.json` is served so verifiers can resolve the issuer key. Must be fixed before issuing
  (changing it later invalidates verification of already-issued VCs).
* **Indicative contracts to confirm against pinned versions.** The exact Mimoto
  `mimoto-issuers-config.json` fields and the Registry connector request/response shape are
  written as *indicative* and to be finalized against **Mimoto 0.22.0** / **Inji Certify 0.14.0**.
* **Registry connector authorization.** The service-to-service credentials Certify uses to call
  the Registry API, and the Registry-side authorization for that caller.
