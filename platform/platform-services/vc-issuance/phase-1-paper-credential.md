---
description: >-
  Phase 1 — assisted issuance of a signed, printable credential (PDF with an
  offline-verifiable QR) from OpenG2P Registry data, verified with Inji Verify.
  No wallet, no IdP, no OpenID4VCI device flow.
---

# Phase 1 — Paper Credential

The lowest-common-denominator path: a citizen who owns **no device** gets a **printed credential**
with an **offline-verifiable QR**, and a verifier validates it by scanning that QR. Everything heavy
(wallets, Logto, Mimoto, OpenID4VCI redirect flows) is **out of scope** for Phase 1.

## Actors

| Actor | Role |
|-------|------|
| **Citizen (beneficiary)** | Owns nothing digital; receives and carries a **printed** credential. |
| **Agent** | Authenticated operator at a kiosk/CSC who issues on the citizen's behalf. |
| **Issuance backend** | Resolves the citizen, calls Certify, renders the PDF. (Registry/staff portal API.) |
| **Inji Certify** | Issues + **signs** the VC and produces the **signed QR** payload. |
| **OpenG2P Registry** | Source of claim data; exposed to Certify via the [Registry connector](registry-data-connector.md). |
| **Verifier** | A relying party (bank, ration shop, department) who **scans the QR** with **Inji Verify**. |

## Issuance flow (assisted)

```
 Agent (authenticated)                Issuance backend            Inji Certify         Registry
   │ 1. look up citizen by functional ID │                          │                    │
   │ ───────────────────────────────────►│                          │                    │
   │ 2. "issue credential"               │ 3. request issuance (identifier = functional ID / phone)
   │                                     │ ───────────────────────► │                    │
   │                                     │                          │ 4. connector pulls claims
   │                                     │                          │ ─────────────────► │
   │                                     │                          │ 5. build VC from template,
   │                                     │                          │    sign (.p12 key),
   │                                     │                          │    produce signed QR payload
   │                                     │ ◄── signed VC + QR ────── │                    │
   │ 6. render PDF (credential + QR) and PRINT │                     │                    │
   │ ◄───────────────────────────────────│                          │                    │
   │ 7. hand printed credential to citizen                                                │
```

* **No citizen login.** The **agent** is the authenticated party; the citizen is identified by their
  **functional ID** (looked up in the registry). There is no Logto/eSignet, no citizen wallet.
* **Server-side issuance.** The backend drives Certify directly (a trusted machine-to-machine call);
  there is no interactive OpenID4VCI redirect and no device holder key — the credential is a
  **bearer document** whose trust comes from the **issuer's signature**.
* **Re-issue on demand.** Because the data lives in the registry and Certify is stateless about
  storage, a lost/stale credential is simply **re-issued and re-printed** at any kiosk.

## Presentation & verification (offline)

```
 Citizen ──(hands paper)──► Verifier ──(scans QR with Inji Verify)──► validates signature
                                                                       against issuer's published
                                                                       key / DID  → ✅/❌
```

* The **QR is the credential.** A full JSON-LD VC is far too large for a QR, so the QR carries a
  **compact, signed payload** (CWT/mDoc-style, like a COVID certificate / mDL). Inji Certify's
  `credential_config` supports this via **`qr_settings` + `qr_signature_algo`**.
* **Offline verification:** the verifier checks the signature against the issuer's **published public
  key / DID** — no call back to OpenG2P needed at scan time.

## Architecture & components (Phase 1)

```
 Issuance backend ──► Inji Certify ──► Registry connector ──► OpenG2P Registry (read-only view)
 (agent-driven)         │
                        ├─ Velocity template → VC body
                        ├─ keymanager + .p12  → Ed25519 signature
                        └─ qr_settings        → signed QR payload  → PDF (printed)

 Verifier (separate):   Inji Verify ── scans QR ── validates vs issuer DID/key (offline)
```

* **Inji Certify** — the issuer. Builds the VC from a Velocity template, signs with a key from its
  **embedded keymanager (PKCS12 `.p12`, no HSM)**, and produces the signed QR.
* **Registry connector** — our custom Certify `DataProviderPlugin` that reads the citizen's claims
  from a read-only **Registry view** (`functionalRecordId`, `fullName`, `dateOfBirth`). See
  [Registry Data Connector](registry-data-connector.md).
* **PDF rendering** — the credential + QR composed into a printable PDF (rendering template).
* **Inji Verify** — the verifier app that scans and validates the QR offline.

## Key management
Certify signs with its embedded keymanager backed by a **`.p12` keystore** (no HSM). The `.p12` and
the encrypted key rows **are the issuer identity** — they must be **persisted and backed up**, and
the issuer's **public key / DID must be published at a stable, resolvable URL** so verifiers can
validate offline. (See [Deployment](deployment.md).)

## The Phase-1 linchpin to confirm during implementation
The whole model depends on the **QR being compact, signed, and offline-verifiable end to end**:
1. confirm exactly what Certify places in the QR via `qr_settings` (format, size, signature);
2. confirm **Inji Verify validates that QR offline** against the issuer's published key;
3. settle **revocation/validity** for paper — either short validity, or an *optional* online
   status-list check when the verifier has connectivity.

Everything else is proven: Certify issues an Ed25519-signed VC, and the connector populates it from
the real registry (see [Local Developer Trial](local-setup.md)).
