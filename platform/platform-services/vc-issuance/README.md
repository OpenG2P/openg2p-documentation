---
description: >-
  Issuing W3C Verifiable Credentials from OpenG2P data sources (Registry, PBMS,
  SPAR, …) using MOSIP Inji Certify, delivered to the citizen's phone wallet via
  the Beneficiary Portal.
---

# VC Issuance

## Overview

**VC Issuance** lets OpenG2P turn the data a citizen already holds in OpenG2P systems
(their **Registry** record, a **PBMS** benefit, a **SPAR** entry, …) into a standards-based
**Verifiable Credential (VC)** that the citizen can carry in a mobile wallet and present
anywhere, online or offline.

The signing/issuing engine is **MOSIP [Inji Certify](https://docs.inji.io/inji-certify)**, an
open-source **OpenID4VCI** credential issuer. OpenG2P runs **one shared Inji Certify** as a
platform service; the individual applications (Registry, PBMS, SPAR) are merely *sources of
claims* — Certify itself is **not tied to any one application**.

From the citizen's point of view it is simple: they log into the **Beneficiary Portal** (a
desktop web app), open the Registry or PBMS page, click **"Download Credential"**, scan a
**QR code** with their phone wallet, and the signed credential lands in the wallet.

### Design principles

* **Application-agnostic issuer.** The same Inji Certify serves Registry, PBMS, SPAR and any
  future source. A source application contributes *claims*; it never signs anything.
* **Issuing authority is configuration, not code.** A single issuing authority is assumed for
  now, but nothing is hardcoded — each credential type carries its own issuer **DID** and
  signing key, so multiple sub‑departments within an authority can issue different VCs.
* **Keys stay inside Certify.** Certify uses its **embedded keymanager** with a **PKCS12
  (`.p12`) keystore** (no HSM). No application ever touches signing keys.
* **Reuse the cluster.** Certify runs on the OpenG2P **Kubernetes** cluster and reuses the
  **existing PostgreSQL**.
* **Holder-bound delivery.** The credential is delivered **directly to the citizen's wallet**
  over OpenID4VCI (not handed back to the portal), so it is cryptographically bound to the
  citizen's device.

## High-level architecture

```
   Citizen (desktop browser)
        │  1. Login  (eSignet → National ID, or Keycloak via IAM)
        ▼
 ┌───────────────────────────┐
 │   Beneficiary Portal UI   │  (desktop web app; single login for the citizen)
 └───────────────────────────┘
        │  talks internally to both source apps
        ├───────────────────────────┐
        ▼                            ▼
 ┌──────────────────┐        ┌──────────────────┐
 │ Registry         │        │ PBMS             │   ← sources of VC claims
 │ bene-portal-api  │        │ bene-portal-api  │
 └──────────────────┘        └──────────────────┘
        │  2. citizen clicks "Download Credential" on the Registry/PBMS page
        │  3. portal fetches the citizen's record → builds claims
        │  4. POST /pre-authorized-data  { claims, tx_code (PIN) }   [trusted M2M]
        └───────────────┬───────────────────────────────────────────┐
                        ▼                                             │
                ┌───────────────────────┐                            │
                │   Inji Certify         │  (ONE shared instance)     │
                │   OpenID4VCI issuer    │                            │
                │   embedded keymanager  │                            │
                │   PostgreSQL (shared)  │                            │
                └───────────────────────┘                            │
                        │  returns credential_offer_uri              │
        ┌───────────────┘                                            │
        ▼                                                            │
  Portal returns { offer_uri → QR, PIN } to the UI                   │
        │                                                            │
        ▼  5. citizen scans QR with phone wallet, enters PIN         │
 ┌──────────────────┐   token + proof-of-possession + /credential   │
 │  Phone wallet    │ ─────────────────────────────────────────────►┘
 │ (Inji / any      │ ◄──────────  6. signed VC stored in wallet
 │  OpenID4VCI app) │
 └──────────────────┘
```

> **Key point:** the signed VC travels **Certify → wallet**. The Beneficiary Portal only
> *orchestrates the offer*; it never receives or stores the signed credential.

## Sub-pages

| Page | Contents |
|------|----------|
| [Functional Specifications](functional-specifications.md) | Actors, login, the end-to-end "download credential" journey, QR + PIN, agent-assisted flow |
| [Technical Architecture](technical-architecture.md) | Inji Certify internals, the push integration model, multi-application & multi-issuer design, authentication, key management, the 3-layer config model |
| [API Reference](api-reference.md) | Inji Certify endpoints and the proposed Beneficiary Portal VC-issuance APIs, with example payloads |
| [Deployment](deployment.md) | Running Certify on Kubernetes, reusing cluster PostgreSQL, configuration, per-authority deployment, DID hosting, security |
| [Local Setup & Verified Trial](local-setup.md) | A working local docker-compose trial that issues a real signed VC over the APIs |

## Status

A working local trial has been completed: Inji Certify v0.14.0 was run locally and issued an
Ed25519-signed credential end-to-end over the OpenID4VCI APIs (no eSignet, no wallet app
needed for the developer trial). See [Local Setup & Verified Trial](local-setup.md). The
OpenG2P production design described across these pages builds on that proven flow.
