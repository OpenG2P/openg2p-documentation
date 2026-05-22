---
description: >-
  Running Inji Certify as a shared platform service on the OpenG2P Kubernetes
  cluster — reusing the existing PostgreSQL, supplying configuration, persisting
  keys, and per-authority deployment.
---

# Deployment

## Target environment

Inji Certify runs as a **shared platform service** on the OpenG2P **Kubernetes** cluster,
alongside Registry, PBMS, IAM (eSignet/Keycloak) and the other platform services. It
**reuses the existing cluster PostgreSQL** rather than running its own database.

```
            OpenG2P Kubernetes cluster
 ┌──────────────────────────────────────────────────────────┐
 │  eSignet / Keycloak (IAM)                                  │
 │  Registry bene-portal-api ─┐                               │
 │  PBMS bene-portal-api ─────┼─► Inji Certify (Deployment)   │
 │                            │        │                      │
 │                            │        ▼                      │
 │                            │   PostgreSQL (existing) ◄──────┼─ reuse: dedicated DB/schema
 │                            │   PVC: /…/CERTIFY_PKCS12 (.p12)│
 └──────────────────────────────────────────────────────────┘
```

## PostgreSQL — reuse the cluster instance

* Create a **dedicated database/schema** for Certify on the existing PostgreSQL (e.g.
  `inji_certify`); do **not** co-mingle with `registrydb`.
* Run Certify's **init SQL** once against that database to create the keymanager tables
  (`key_alias`, `key_policy_def`, `key_store`), the `credential_config` table, the key policy
  rows (`CERTIFY_VC_SIGN_ED25519`, etc.), and any seed credential configurations.
* Point Certify at it via the `mosip.certify` datasource properties / env (host, port, db,
  user, password — supplied from a Kubernetes Secret).

## Configuration (the three layers, on Kubernetes)

1. **Service config — properties + env.** Ship the `certify-*.properties` via a **ConfigMap**
   mounted at the Spring config location; supply secrets and host-specific overrides via
   **env vars / Secrets** (`mosip_certify_domain_url`, DB credentials, `.p12` password). Set
   Certify as its own authorization server (issuer/JWKS/audiences → Certify's own URL).
2. **Credential definitions — DB / API.** Seed `credential_config` rows in the init SQL, or
   manage them at runtime via `POST /credential-configurations`. Each row carries the issuer
   **DID**, **signing key** app-id, template, format and display for one credential type.
3. **Keys — `.p12` + key tables.** Auto-generated on first boot (see below).

## Key persistence (critical — no HSM)

Because OpenG2P uses a **PKCS12 `.p12` keystore (no HSM)**, the `.p12` file plus the encrypted
key rows in PostgreSQL **are the issuer identity**:

* Mount the `.p12` directory on a **PersistentVolumeClaim** (durable storage), and ensure the
  keystore path actually resolves to that mount (a misconfigured relative path can write the
  `.p12` outside the volume, after which the master key regenerates on pod restart).
* **Back up** the `.p12` and the Certify database together.
* Regenerating these mints a **new issuer key** → **all previously issued VCs become
  unverifiable**. Treat them as production secrets.

## Issuer DID hosting

Each credential's `didUrl` must be **resolvable by wallets/verifiers**:

* For `did:web:<host>/<path>`, host the `did.json` at the corresponding HTTPS URL (Certify can
  generate the document content; you arrange where it is served — typically behind the cluster
  ingress on a stable domain).
* Use a **stable, public domain** for the issuer DID (not an ephemeral tunnel). Changing the
  DID host invalidates verification of already-issued VCs.

## Per-authority deployment

* **One shared Certify per issuing authority**, serving all of that authority's source
  applications (Registry, PBMS, SPAR) and credential types. This is the OpenG2P default.
* **Separate Certify instances for genuinely separate legal authorities** — each with its own
  `.p12`/master key, database, and DID — for clean key isolation and independent lifecycle.
* Within one authority, multiple **sub-departments** are handled by **per-credential
  `credential_config`** (distinct DIDs/keys), not by extra instances.

## Services to build and run

| Service | Status | Action |
|---|---|---|
| **Inji Certify** | upstream image (`injistack/inji-certify-with-plugins`) | deploy on K8s, reuse PostgreSQL, configure as above |
| **iam-bene-portal-api** | exists (auth scaffold, has Dockerfile) | run like `iam-staff-portal-api` |
| **registry-bene-portal-api** | exists; **no Dockerfile yet** | add VC-issuance endpoints + author a Dockerfile |
| **PBMS bene-portal-api** | equivalent | mirror the registry integration |

> The OpenG2P portal APIs are FastAPI services launched via gunicorn + uvicorn workers
> (port 8000) on the `openg2p-fastapi-common` framework, configured by pydantic-settings with a
> per-service env prefix. New VC endpoints follow the existing controller/service conventions.

## Security checklist

* Certify's `/pre-authorized-data` is reachable **only** by the trusted source applications
  (network policy + M2M auth), never publicly.
* The citizen is authenticated at the portal via **eSignet/IAM** before any offer is minted.
* The PIN (`tx_code`) is generated per offer and shown only on the authenticated session.
* Signing keys never leave Certify; the `.p12` and DB are persisted, backed up, and access-
  controlled.
