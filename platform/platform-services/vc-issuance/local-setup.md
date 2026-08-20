---
description: >-
  A verified local run of the Phase-1 push flow — the Agent Portal API reads a
  real registrant, pushes claims to Inji Certify, gets an Ed25519-signed
  credential, and renders a printable PDF with a QR. N
---

# Local Developer Trial

This page records a **working, verified** local run of the **issuance and signing chain**: claims are read from a real registrant in the OpenG2P Registry, **pushed** into **Inji Certify** (pre-authorized-code), Certify returns an **Ed25519-signed** credential, and a **printable PDF with a QR** is rendered. Verified with **Inji Certify 0.14.0**.

{% hint style="warning" %}
**This trial predates the current Phase-1 design and is narrower than it.** It proves the
*issuance and signing* half only. It looks the registrant up **by phone** and performs **no
authentication of anyone** — whereas Phase 1 now resolves the record by **national ID →
`foundational_id` → `internal_record_id`**, requires the **agent** to be logged in to the `agent`
realm, and requires the **beneficiary** to authenticate via **eSignet** before anything is issued.
Treat this page as the record of the signing chain working, not as the issuance flow. See
[Phase 1 — Paper Credential](phase-1-paper-credential.md).
{% endhint %}

## What runs

* `database` — PostgreSQL 15 (local stand-in for the cluster PostgreSQL; holds Certify's `inji_certify` DB)
* `certify` — `injistack/inji-certify-with-plugins:0.14.0` on `http://localhost:8090` (**stock**, no custom plugin)
* **OpenG2P Registry** — the real registry DB (e.g. reached on `localhost:5432`), exposing a read-only VC view (`phone`, `functionalRecordId`, `fullName`, `dateOfBirth`) — the current design keys this view on `internal_record_id` instead
* **Agent Portal API** — the `agent-portal-api` FastAPI service (the issuance backend)

The wallet UI, Mimoto and nginx services are not needed.

> On Apple Silicon / Colima the Certify image is amd64-only — set `DOCKER_DEFAULT_PLATFORM=linux/amd64` (runs under emulation). The compose expects an external network: `docker network create mosip_network`.

## Certify config (vs. the stock quickstart)

1. **`mosip_certify_domain_url=http://localhost:8090`** so the token issuer, JWKS, audiences and the proof `aud` all resolve to the same host the client uses.
2. **Certify-as-authorization-server overrides** — point `authn.issuer-uri` / `jwk-set-uri` / `allowed-audiences` / `oauth.issuer` at Certify itself (pre-authorized-code flow, no eSignet).
3. **`mosip.certify.cache.names=…,credentialOfferCache`** — the stock list omits `credentialOfferCache`, which the offer endpoint needs.
4. **`mosip.certify.integration.data-provider-plugin=PreAuthDataProviderPlugin`** — a **built-in** Certify plugin (ships inside `certify-service`, no custom jar) that makes the **pushed claims the credential subject**. Certify needs **no Registry access**.
5. **`credential_config` = `OpenG2PBeneficiaryCredential`** — a 3-field credential (`functionalRecordId`, `fullName`, `dateOfBirth`) with an **inline JSON-LD `@context`** (so no external context hosting is needed), Ed25519 signing key, and `qr_settings`.

## How the run works

```
Agent Portal API ──reads beneficiary_vc_view (by phone)──► OpenG2P Registry
        │  claims = {functionalRecordId, fullName, dateOfBirth}
        └──push (pre-authorized-code)──► Inji Certify ──PreAuthDataProviderPlugin (built-in)──► Ed25519-signed VC
        ◄── signed VC ──┘
        └── render ──► printable PDF + QR
```

Under the hood the push is the standard OpenID4VCI **4-step** sequence, all against `http://localhost:8090/v1/certify`:

| # | Call                                             | Purpose                                |
| - | ------------------------------------------------ | -------------------------------------- |
| 1 | `POST /pre-authorized-data` (claims + `tx_code`) | create the offer + pre-auth code       |
| 2 | `GET /credential-offer-data/{offer_id}`          | read the offer → `pre-authorized_code` |
| 3 | `POST /oauth/token` (pre-auth grant + `tx_code`) | get `access_token` + `c_nonce`         |
| 4 | `POST /issuance/credential` (Bearer + proof JWT) | receive the signed VC                  |

The Agent Portal API's `CertifyIssuanceService` performs all four steps (including building the proof-of-possession JWT); a standalone `issue_vc.py` in the working repo does the same with the Python stdlib for quick raw-flow testing.

## Result

For registrant `+91…` → `IND-NSR-0001`, the API returned an **Ed25519-signed** `OpenG2PBeneficiaryCredential` and wrote a **printable PDF** (`vc-IND-NSR-0001.pdf`) carrying the human-readable fields plus a QR of the signed credential:

```jsonc
{
  "credential": {
    "type": ["VerifiableCredential", "OpenG2PBeneficiaryCredential"],
    "issuer": "did:web:<issuer-host>",
    "credentialSubject": {
      "id": "did:jwk:…",                 // holder key from the proof JWT
      "functionalRecordId": "IND-NSR-0001",
      "fullName": "Alex Rivera",
      "dateOfBirth": "1984-04-10"
    },
    "proof": { "type": "Ed25519Signature2020", "proofValue": "z…", "verificationMethod": "did:web:<issuer-host>#…" }
  }
}
```

## What this confirms

* **End-to-end push works on stock Certify**: real Registry row → Agent Portal API → Certify (built-in `PreAuthDataProviderPlugin`) → Ed25519-signed VC → printable PDF/QR — no citizen device, no wallet, no eSignet, **no custom Certify plugin**.
* **Certify is decoupled** from the Registry; only the Agent Portal API reads `beneficiary_vc_view`.
* The same Agent Portal API code runs unchanged on the cluster; locally the **service classes** were driven directly because the private `openg2p-registry-core/-extensions` packages (needed for the full FastAPI boot) live in the deployment stack, not on PyPI.

## Known limitations of the local trial

* The QR currently embeds the **full signed VC** (gzip+base64url) — verifiable but bulky. Phase-1 production switches to Certify's **compact signed QR** (`qr_settings` / `qr_signature_algo`).
* The issuer DID is a placeholder `did:web:…` from the stock config, so the VC is not third-party verifiable until the DID is hosted at a resolvable URL.
* The local `.p12` keystore must be **persisted** (mounted on durable storage); regenerating it invalidates previously issued credentials (see [Deployment](deployment.md)).

## Working repository

The runnable artifacts — the Certify compose config, `issue_vc.py`, a sample issued PDF, the Certify Helm chart and the (Phase-2) custom pull connector project — live in the **`verifiable-credentials`** repository; the `agent-portal-api` service lives in the **Registry Platform** repository. These GitBook pages are the canonical design documentation; the working repos hold the runnable artifacts.
