---
description: >-
  A verified local docker-compose trial that issues a real Ed25519-signed
  Verifiable Credential over the OpenID4VCI APIs — no eSignet and no wallet app
  needed for developer testing.
---

# Local Developer Trial

> **Scope note.** This is a **developer smoke-test of the issuing/signing engine** — it proves Inji
> Certify can build and **Ed25519-sign** a credential from external DB data via the
> [Registry connector](registry-data-connector.md). It uses a **simplified issuance path**
> (pre-authorized-code with Certify acting as its own authorization server, driven by a plain HTTP
> client) just to exercise Certify on a laptop. In **Phase 1** production, issuance is instead
> **agent-driven, server-side**, and the output is rendered to a **printed signed QR/PDF** (see
> [Phase 1 — Paper Credential](phase-1-paper-credential.md)) — but the **signing engine and the
> Registry connector validated here are exactly the same**.

This page records a **working** local trial that proves the signing pipeline end-to-end with a
plain HTTP client (no IdP, no wallet app), so a developer can issue a VC in minutes. Verified
with **Inji Certify 0.14.0**.

## What runs

Two containers from the upstream quickstart
(`mosip/inji-certify` → `docker-compose/docker-compose-injistack/`):

* `database` — PostgreSQL 15 (the local stand-in for the cluster PostgreSQL)
* `certify` — `injistack/inji-certify-with-plugins:0.14.0` on `http://localhost:8090`

The wallet UI, Mimoto and nginx services are not needed for an API trial.

> On Apple Silicon / Colima the image is amd64-only — set
> `DOCKER_DEFAULT_PLATFORM=linux/amd64` (runs under emulation). The compose expects an external
> network: `docker network create mosip_network`.

## Config changes vs. the stock quickstart

1. **`mosip_certify_domain_url=http://localhost:8090`** so the token issuer, JWKS, audiences and
   the proof `aud` all resolve to the same host the client uses.
2. **Certify-as-authorization-server overrides** (point `authn.issuer-uri` / `jwk-set-uri` /
   `allowed-audiences` / `oauth.issuer` at Certify itself instead of eSignet).
3. **`mosip.certify.cache.names=…,credentialOfferCache`** — the stock list omits
   `credentialOfferCache`, which the offer endpoint needs.
4. **`mosip.certify.integration.data-provider-plugin=PreAuthDataProviderPlugin`** — so the
   claims submitted to `/pre-authorized-data` become the credential subject (the default CSV
   plugin fails the pre-auth flow with `ERROR_FETCHING_IDENTITY_DATA`).
5. Widened the credential's allowed `credential_subject` keys so all template fields populate.

## Run

```bash
git clone https://github.com/mosip/inji-certify.git
cd inji-certify/docker-compose/docker-compose-injistack
docker network create mosip_network
export DOCKER_DEFAULT_PLATFORM=linux/amd64        # Apple Silicon / Colima
# apply the config changes above, then:
docker compose up -d database certify
curl http://localhost:8090/v1/certify/actuator/health     # {"status":"UP"}
```

## The 4-step API flow

All against `http://localhost:8090/v1/certify`:

| # | Call | Purpose |
|---|------|---------|
| 1 | `POST /pre-authorized-data` (claims + `tx_code`) | create the offer + pre-auth code |
| 2 | `GET /credential-offer-data/{offer_id}` | read the offer → `pre-authorized_code` |
| 3 | `POST /oauth/token` (pre-auth grant + `tx_code`) | get `access_token` + `c_nonce` |
| 4 | `POST /issuance/credential` (Bearer + proof JWT) | receive the signed VC |

A reproducible client script (`issue_vc.py`, Python stdlib + `cryptography`) performs all four
steps, including building the proof-of-possession JWT, and is kept in the
[`vc-issuance` working repository](#working-repository).

## Result

A fully-populated, **Ed25519-signed** credential is returned (abridged):

```jsonc
{
  "credential": {
    "type": ["VerifiableCredential", "FarmerCredential"],
    "issuer": "did:web:<issuer-host>",
    "credentialSubject": {
      "id": "did:jwk:…",            // holder key from the proof JWT
      "fullName": "Jane Thompson", "gender": "Female", "dateOfBirth": "1998-01-24",
      "state": "Karnataka", "district": "Bangalore" /* … */
    },
    "proof": { "type": "Ed25519Signature2020", "proofValue": "z…", "verificationMethod": "did:web:<issuer-host>#…" }
  }
}
```

## What this confirms

* **No wallet app required** to issue/download — a plain HTTP client works (any OpenID4VCI
  wallet works too).
* **No eSignet required** for the developer trial — Certify mints and validates the token
  itself via the pre-authorized-code grant.
* The same mechanics underpin the OpenG2P design, where the **portal** (not a curl script)
  generates the offer after authenticating the citizen, and a **phone wallet** (not curl)
  redeems it.

## Known limitations of the local trial

* The issuer DID is a placeholder `did:web:…` from the stock config, so the VC is not
  third-party verifiable until the DID is hosted at a resolvable URL.
* The local `.p12` keystore is not persisted by default — fine for a throwaway trial, but in
  production the keystore must be persisted and backed up (see [Deployment](deployment.md)).

## Working repository

The runnable trial (the modified compose config, `issue_vc.py`, and a sample issued VC) is
maintained in the internal **`vc-issuance`** working repository. These GitBook pages are the
canonical design documentation; the working repo holds the runnable artifacts.
