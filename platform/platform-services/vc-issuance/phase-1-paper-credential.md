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
| **Agent Portal API** | The issuance backend: resolves the citizen in the Registry, **pushes** the claims into Certify, and renders the PDF. (A dedicated FastAPI service, `agent-portal-api`.) |
| **Inji Certify** | Issues + **signs** the VC and produces the **signed QR** payload. **Not connected to the Registry.** |
| **OpenG2P Registry** | Source of claim data; read **only by the Agent Portal API** (a read-only `beneficiary_vc_view`). |
| **Verifier** | A relying party (bank, ration shop, department) who **scans the QR** with **Inji Verify**. |

## Issuance flow (assisted, push model)

```
 Agent (authenticated)            Agent Portal API           Inji Certify        Registry
   │ 1. "issue VC" (phone / functional ID) │                    │                  │
   │ ─────────────────────────────────────►│                    │                  │
   │                                        │ 2. read beneficiary_vc_view (claims)  │
   │                                        │ ────────────────────────────────────►│
   │                                        │ 3. PUSH claims (OpenID4VCI            │
   │                                        │    pre-authorized-code)               │
   │                                        │ ──────────────────►│                  │
   │                                        │                    │ 4. PreAuthDataProviderPlugin:
   │                                        │                    │    pushed claims = subject;
   │                                        │                    │    build VC from template,
   │                                        │                    │    sign (.p12 Ed25519 key)
   │                                        │ ◄── signed VC ──────│                  │
   │                                        │ 5. render PDF (credential + QR)        │
   │ ◄── PDF (printed) ─────────────────────│                    │                  │
   │ 6. hand printed credential to citizen                                          │
```

* **The Agent Portal API owns the Registry lookup.** It reads the claims and **pushes** them into
  Certify; Certify never connects to the Registry. This keeps the issuer **decoupled** from registry
  data and credentials.
* **Photograph (if used) is pushed as bytes.** Photos live in **MINIO**. Certify does **not** pull
  from MINIO — so the Agent Portal API **fetches the image from MINIO, downscales + compresses it to a
  ~1–2 KB WEBP/AVIF/JPEG thumbnail, base64-encodes it, and pushes it as the `face` claim**. (A MINIO
  *link* would not work for the offline QR, which must embed the actual bytes; and the thumbnail must
  be tiny because the whole signed QR fits in ~2.9 KB.)
* **No citizen login.** The **agent** is the authenticated party; the citizen is identified by their
  **phone / functional ID** (looked up in the registry). There is no Logto/eSignet, no citizen wallet.
* **Server-side issuance.** The backend drives Certify directly (a trusted machine-to-machine call)
  via the OpenID4VCI **pre-authorized-code** grant; there is no interactive redirect and no device
  holder key — the credential is a **bearer document** whose trust comes from the **issuer's signature**.
* **Re-issue on demand.** Because the data lives in the registry and Certify is stateless about
  storage, a lost/stale credential is simply **re-issued and re-printed** at any kiosk.

## Presentation & verification (offline)

```
 Citizen ──(hands paper)──► Verifier ──(scans QR with Inji Verify)──► validates signature
                                                                       against issuer's published
                                                                       key / DID  → ✅/❌
```

* **The QR is the credential.** A full JSON-LD VC is far too large for a QR, so the QR carries a
  **compact, signed payload** — MOSIP's **"claim 169"** identity QR (CBOR), the CWT/mDoc family used
  by mDL / COVID certificates. Inji Certify supports this **natively** (no plugin) via the
  `credential_config` columns **`qr_settings` + `qr_signature_algo`**: each `qr_settings` entry is a
  Velocity template; Certify renders it, encodes it with the **pixel-pass** library, **signs it as a
  COSE/CWT** (`CoseSignatureService.cwtSign`), and **base45**-encodes the result into the VC under a
  `claim169` field.
* **Photograph in the QR ("large photo" reality).** A QR is hard-capped at **~2.9 KB**, so you can't
  embed a real photo. The claim-169 standard fits a **low-resolution face thumbnail** by combining: a
  modern codec (the spec's face field, attribute 62, allows **WEBP / AVIF / JPEG / PNG / WSQ** — WEBP/
  AVIF give a recognisable face in **~1–2 KB**), **integer-keyed CBOR** (no JSON field-name overhead),
  **zlib/Brotli** compression, and **Base45** packing. It's recognition-grade, not high-resolution —
  the same approach as Aadhaar's Secure QR. The image **bytes** must be supplied as the `face` claim
  (see issuance note below); Certify does not fetch images. The signature/cert also consume the QR
  budget, so photo quality trades off against embedded trust material.
* **Offline verification — where the key comes from.** The signed QR is a **COSE_Sign1 / CWT**. The
  claim-169 spec **does not** use `.well-known`/JWKS (DID) discovery for the QR; it uses **COSE**
  mechanisms in the signature header — `x5chain` (embedded cert), `x5t` (cert hash), or `x5u` (cert
  URI) — and assumes the verifier holds a **pre-loaded trust anchor** ("the app already has the
  country's/issuer's key"). Certify can embed the issuer cert (`x5c`) so verification is **fully
  offline**, but embedding it costs QR bytes, so issuers often **omit it and rely on the pre-distributed
  trust list**. Either way, no call back to OpenG2P at scan time. (The **JSON-LD VC** — not the QR —
  still uses `proof.verificationMethod = <issuerDID>#<key>`, resolvable via `did:web`.)

## Architecture & components (Phase 1)

```
 Agent Portal API ──reads──► OpenG2P Registry (read-only beneficiary_vc_view)
 (agent-driven)    │
                   └─push claims──► Inji Certify
                                      ├─ PreAuthDataProviderPlugin (built-in) → pushed claims = VC subject
                                      ├─ Velocity template  → VC body
                                      ├─ keymanager + .p12   → Ed25519 signature
                                      └─ (signed VC) ──► Agent Portal API → PDF + QR (printed)

 Verifier (separate):   Inji Verify ── scans QR ── validates vs issuer DID/key (offline)
```

* **Agent Portal API** — the issuance backend (`agent-portal-api`, FastAPI). Reads the citizen's
  claims from the read-only **Registry view** (`functionalRecordId`, `fullName`, `dateOfBirth`),
  **pushes** them into Certify, and renders the PDF/QR. Owns the only Registry connection.
* **Inji Certify** — the issuer (used **stock**, no custom plugin). Builds the VC from a Velocity
  template, signs with a key from its **embedded keymanager (PKCS12 `.p12`, no HSM)**. Certify's
  **built-in `PreAuthDataProviderPlugin`** makes the **pushed claims the credential subject** — so
  Certify needs **no Registry access**. (A custom pull connector exists for the wallet flow; see
  [Registry Data Connector](registry-data-connector.md).)
* **PDF rendering** — the Agent Portal API composes the credential + QR into a printable PDF.
* **Inji Verify** — the verifier app that scans and validates the QR offline.

## Key management
Certify signs with its embedded keymanager backed by a **`.p12` keystore** (no HSM). The `.p12` and
the encrypted key rows **are the issuer identity** — they must be **persisted and backed up**, and
the issuer's **public key / DID must be published at a stable, resolvable URL** so verifiers can
validate offline. (See [Deployment](deployment.md).)

## Status & the remaining linchpin
**Proven end to end:** the Agent Portal API reads a real registrant from the Registry, pushes the
claims to Certify, Certify returns an **Ed25519-signed** `OpenG2PBeneficiaryCredential`, and the API
renders a **printable PDF with a QR** (see [Local Developer Trial](local-setup.md)).

The remaining work is making the **QR compact and offline-verifiable end to end**:
1. the current PDF embeds the full signed VC in the QR; switch to Certify's **compact signed QR**
   (`qr_settings` + `qr_signature_algo`, CWT/mDoc-style) for a smaller, scan-friendly code;
2. confirm **Inji Verify validates that QR offline** against the issuer's published key/DID;
3. settle **revocation/validity** for paper — either short validity, or an *optional* online
   status-list check when the verifier has connectivity.
