---
description: >-
  Deploying the Phase-1 VC-issuance stack — Inji Certify + the Registry
  connector — on the OpenG2P Kubernetes cluster, reusing the existing
  PostgreSQL. Plus Inji Verify for offline QR verification.
---

# Deployment (Phase 1)

Phase 1 is intentionally small: **Inji Certify** (issuer) with the **Registry connector**, signing
to a **`.p12`** keystore, reusing the cluster **PostgreSQL**, plus **Inji Verify** for the
verification side. **No Logto, no Mimoto, no Inji Web** (those belong to the wallet options).

## Components

| Component | Image / source | Role |
|---|---|---|
| **Inji Certify** | `injistack/inji-certify-with-plugins` + the Registry connector JAR | Issues + signs the VC and the QR payload |
| **Registry connector** | custom plugin (built in the `vc-issuance` repo) | Pulls claim data from the Registry view |
| **Inji Verify** | `injistack/inji-verify-*` | Scans + validates the QR (offline) — verifier side |
| **PostgreSQL** | existing cluster instance | Reused: a dedicated DB/schema for Certify |
| **Issuance backend** | OpenG2P registry/staff portal API | Agent-driven trigger + PDF rendering |

All run on the OpenG2P **Kubernetes** cluster.

## Reuse the cluster PostgreSQL
* Create a **dedicated database/schema** for Certify (e.g. `inji_certify`) on the existing
  PostgreSQL; do not co-mingle with `registrydb`.
* Run Certify's init SQL once (keymanager tables, `credential_config`, key policies).
* The **Registry connector** connects to the registry DB **read-only** via a least-privilege user
  against a dedicated view — see [Registry Data Connector](registry-data-connector.md).

## Configuration highlights
* **Certify**: load the **Registry connector** JAR into the plugin loader path; set
  `data-provider-plugin=RegistryDataProviderPlugin` + `scan-base-package=org.openg2p.certify.registry`;
  configure the external `registrydb.*` datasource, `scope-query-mapping`, and `param-claim-mapping`;
  define the `credential_config` (Velocity template, issuer DID, signing key, and **`qr_settings` /
  `qr_signature_algo`** for the printable QR).
* **`.p12` keystore (no HSM)**: mount it on durable storage and **back it up** — the `.p12` plus the
  encrypted key rows **are the issuer identity**; regenerating them invalidates previously issued
  credentials.
* **Issuer DID**: publish the issuer's public key / `did.json` at a **stable, resolvable HTTPS URL**
  so Inji Verify can validate QRs **offline** at scan time.

## Verifier side
**Inji Verify** validates the printed QR by checking the signature against the issuer's published
key/DID. It does not need access to OpenG2P at scan time (offline-verifiable), aside from resolving
the issuer's published key (cacheable).

## Security checklist
* The issuance backend calls Certify as a **trusted machine-to-machine** caller (agent-authenticated
  context); Certify is not exposed publicly for issuance.
* Certify ↔ Registry is **read-only** via a dedicated view and least-privilege `certify_ro` user —
  never raw registry tables.
* Signing keys never leave Certify; the `.p12` + key tables are persisted, backed up, access-controlled.
* Decide a **revocation/validity** posture for paper (short validity and/or an optional online
  status-list check when the verifier is connected).

## Notes (environment)
* The cluster already runs much of the OpenG2P/Inji stack (eSignet, keymanager, mock-identity,
  registry APIs). Phase 1 only needs **Certify + the connector** added; the wallet-side services are
  not required.
* Local development can run Certify under Docker/Colima, reaching the cluster's registry DB via
  `host.docker.internal` — but Phase-1 production lives on the cluster.
