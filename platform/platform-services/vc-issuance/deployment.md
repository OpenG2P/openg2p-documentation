---
description: >-
  Deploying the Phase-1 VC-issuance stack — the Agent Portal API + Inji Certify —
  on the OpenG2P Kubernetes cluster, reusing the existing PostgreSQL. Plus Inji
  Verify for offline QR verification.
---

# Deployment (Phase 1)

Phase 1 is intentionally small: an **Agent Portal API** (issuance backend) + **Inji Certify** (issuer)
signing to a **`.p12`** keystore, reusing the cluster **PostgreSQL**, plus **Inji Verify** for the
verification side. The Agent Portal API reads the Registry and **pushes** claims to Certify, so
Certify stays decoupled from the Registry. **No Logto, no Mimoto, no Inji Web** (those belong to the
wallet options).

## Components

| Component | Image / source | Role |
|---|---|---|
| **Agent Portal API** | `agent-portal-api` (FastAPI; built in `openg2p-registry-gen2-apis`) | Reads the Registry view, **pushes** claims to Certify, renders the PDF/QR |
| **Inji Certify** | `injistack/inji-certify-with-plugins` (**stock**, no custom plugin) | Issues + signs the VC (+ QR payload); the built-in `PreAuthDataProviderPlugin` makes the pushed claims the subject |
| **Inji Verify** | `injistack/inji-verify-*` | Scans + validates the QR (offline) — verifier side |
| **PostgreSQL** | existing cluster instance | Reused: a dedicated DB/schema for Certify; the Agent Portal API reads the registry DB read-only |

All run on the OpenG2P **Kubernetes** cluster.

## One shared issuance service per environment
Run **one Certify instance per environment** and let **every module** (Registry, PBMS, SPAR, …) use
it. Certify is a **generic signing service**; the push model keeps it decoupled from each module's
data — every module is its own issuance backend that pushes its own claims.

* **Many credential types** — each VC type is one `credential_config` row (its own Velocity template,
  scope, signing key, issuer DID, format, QR settings). An individual can hold several types; a
  **household** credential is just a config whose subject is household attributes. Adding a type =
  adding a row (no Certify rebuild).
* **Multiple issuers** — each `credential_config` carries its own `did_url` + signing key
  (`key_manager_app_id` / `key_manager_ref_id`). **Onboard an issuer** by (1) generating a signing key
  in Certify's keymanager (app-id + key policy), (2) publishing its **DID** (`did:web` at a stable,
  resolvable HTTPS URL), (3) creating the `credential_config` rows that reference that key/DID. Share
  one org-level issuer DID across types, or give each department its own — a policy choice.
* **All modules push to the same instance** — Certify's built-in **`PreAuthDataProviderPlugin`**
  serves them all; each backend selects its `credential_configuration_id` when pushing.

> **Constraint (Certify 0.14.0):** `mosip.certify.integration.data-provider-plugin` is a **single
> global setting** — one active data-provider plugin per instance. `PreAuthDataProviderPlugin` is
> generic (it just returns the pushed claims), so standardise **all** modules on **push**. Mixing
> push for one module and DB-pull for another on the *same* instance isn't supported in 0.14.0 (use a
> separate instance, or a later Certify version).

## Reuse the cluster PostgreSQL
* Create a **dedicated database/schema** for Certify (e.g. `inji_certify`) on the existing
  PostgreSQL; do not co-mingle with `registrydb`.
* Run Certify's init SQL once (keymanager tables, `credential_config`, key policies).
* The **Agent Portal API** connects to the registry DB **read-only** via a least-privilege user
  against a dedicated `beneficiary_vc_view`. Certify does **not** connect to the registry in Phase 1
  (the pull connector — see [Registry Data Connector](registry-data-connector.md) — is for the wallet
  flow).

## Configuration highlights
* **Certify** (stock image, no custom plugin): set
  `data-provider-plugin=PreAuthDataProviderPlugin` (a built-in — turns the pushed claims into the VC
  subject); point the resource-server token settings (`authn.issuer-uri` / `jwk-set-uri` /
  `allowed-audiences` / `oauth.issuer`) at Certify itself (pre-authorized-code flow, no eSignet);
  define the `credential_config` (Velocity template, issuer DID, signing key, and **`qr_settings` /
  `qr_signature_algo`** for the printable QR).
* **Agent Portal API**: configure the read-only registry datasource (`beneficiary_vc_view`), the
  Certify base URL + credential-config id, and the PDF output dir. It owns the only registry connection.
* **`.p12` keystore (no HSM)**: mount it on durable storage and **back it up** — the `.p12` plus the
  encrypted key rows **are the issuer identity**; regenerating them invalidates previously issued
  credentials.
* **Issuer DID / cert**: publish the issuer's public key / `did.json` at a **stable, resolvable HTTPS
  URL** (`did:web:<host>` → `https://<host>/.well-known/did.json`). The signed claim-169 QR is a
  **COSE/CWT** carrying the issuer **`x5c`** (cert chain) and **`kid`** in its header, so verifiers can
  check it offline and anchor trust on the published key/cert (or its root).
* **Photograph**: if the credential embeds a face in the QR, the **Agent Portal API** must push a
  **small compressed thumbnail** (base64) as the `face` claim — a QR holds only ~2–3 KB and Certify
  does not fetch images. See [Phase 1 — Paper Credential](phase-1-paper-credential.md).

## Verifier side
**Inji Verify** validates the printed QR by checking the COSE/CWT signature — using the **`x5c`**
embedded in the QR — against the issuer's published key/cert/DID. It does not need access to OpenG2P
at scan time (offline-verifiable), aside from (cacheably) resolving/trusting the issuer's key.

## Security checklist
* The **Agent Portal API** calls Certify as a **trusted machine-to-machine** caller
  (agent-authenticated context); Certify is not exposed publicly for issuance.
* The Agent Portal API → Registry connection is **read-only** via a dedicated view and a
  least-privilege `certify_ro` user — never raw registry tables. Certify itself has **no** Registry
  connection in Phase 1.
* Signing keys never leave Certify; the `.p12` + key tables are persisted, backed up, access-controlled.
* Decide a **revocation/validity** posture for paper (short validity and/or an optional online
  status-list check when the verifier is connected).

## Notes (environment)
* The cluster already runs much of the OpenG2P/Inji stack (eSignet, keymanager, mock-identity,
  registry APIs). Phase 1 only needs the **Agent Portal API + Certify** added; the wallet-side
  services are not required.
* Local development can run Certify under Docker/Colima while the Agent Portal API reaches the
  cluster's registry DB via `host.docker.internal` — but Phase-1 production lives on the cluster.
