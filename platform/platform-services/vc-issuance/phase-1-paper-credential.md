---
description: >-
  Phase 1 — agent-assisted issuance of a signed, printable credential (PDF with
  an offline-verifiable QR) from OpenG2P Registry data, gated by the
  beneficiary's own eSignet authentication and verified with Inji Verify.
---

# Phase 1 — Paper Credential

The lowest-common-denominator path: a citizen who owns **no device** receives a **printed credential**
with an **offline-verifiable QR**, and a verifier validates it by scanning that QR. Wallets, Mimoto and
OpenID4VCI redirect flows are **out of scope** for Phase 1.

"Owns no device" refers to **holding** the credential. Issuance itself is **always gated by the
beneficiary authenticating digitally** through eSignet — by **biometric at the agent's counter** (which
requires nothing of the citizen) or by **OTP** to their phone.

## Actors

| Actor | Role |
|-------|------|
| **Citizen (beneficiary)** | Receives and carries a **printed** credential. Authenticates once, in person, via **eSignet** to authorise the issuance. Holds nothing digital afterwards. |
| **Agent** | Field/kiosk operator who performs the issuance. Logs in to the Agent Portal with **Keycloak in the `agent` realm**. Distinct from registry **staff** — different realm, different API, different portal. |
| **Agent Portal API** | The issuance backend: resolves the citizen in the Registry, drives the beneficiary's eSignet authentication, **pushes** claims into Certify, renders the PDF and records the issuance. |
| **eSignet** | Authenticates the **beneficiary** against the foundational ID system (biometric or OTP). Issues no credential; it only proves who is standing at the counter. |
| **Inji Certify** | Issues + **signs** the VC and produces the **signed QR** payload. **Not connected to the Registry.** |
| **OpenG2P Registry** | Source of claim data and of the record's identity/status; read **only by the Agent Portal API**. |
| **Verifier** | A relying party (bank, ration shop, department) who **scans the QR** with **Inji Verify**. |

## Issuance flow

```
 Agent            Agent Portal API        Registry         eSignet         Inji Certify
   │ 1. login (Keycloak, `agent` realm)      │               │                  │
   │ ───────────────────►│                   │               │                  │
   │ 2. enter/scan the beneficiary's national ID              │                  │
   │ ───────────────────►│                   │               │                  │
   │                     │ 3. foundational_id exists?         │                  │
   │                     │    record_status == ACTIVE?        │                  │
   │                     │ ─────────────────►│               │                  │
   │                     │ ◄── internal_record_id ────────────│                  │
   │                     │ 4. initiate registrant authentication                 │
   │                     │ ──────────────────────────────────►│                  │
   │ ◄── authorization_url ──────────────────────────────────  │                  │
   │ 5. beneficiary authenticates (biometric at the counter, or OTP)             │
   │ ═══════════════════════════════════════════════════════►│                  │
   │                     │ 6. callback → authentication SUCCESS                │
   │                     │ ◄──────────────────────────────────│                  │
   │                     │ 7. bind: individual_id == foundational_id             │
   │                     │    window: now − completed_at ≤ 5 min                 │
   │                     │ 8. read claims by internal_record_id                  │
   │                     │ ─────────────────►│               │                  │
   │                     │ 9. PUSH claims (pre-authorized-code)                  │
   │                     │ ─────────────────────────────────────────────────────►│
   │                     │                   │               │  build from template,
   │                     │                   │               │  sign (.p12 Ed25519)
   │                     │ ◄────────────── signed VC ─────────────────────────────│
   │                     │ 10. render PDF (credential + QR); log the issuance     │
   │ ◄── PDF download ───│                   │               │                  │
   │ 11. print and hand the paper credential to the citizen                      │
```

### What each step guarantees

* **The beneficiary must exist in the Registry.** The entry point is the citizen's **national ID**,
  matched against the register's **`foundational_id`** (unique and indexed). No record, no credential.
  A record whose `record_status` is not **`ACTIVE`** is refused. `foundational_id` is **required** for
  VC issuance — a record ingested without one cannot be issued a credential.
* **Digital authentication is mandatory.** The beneficiary authenticates *themselves* through eSignet.
  Whether that is a **biometric** capture at the counter or an **OTP** to their phone is determined by
  what the deployment has configured — eSignet's own UI handles capture, including the biometric device.
* **The authentication is bound to the record.** The subject returned by eSignet (`individual_id`) is
  checked against the `foundational_id` of the record being issued. Without this check an agent could
  pair one person's authentication with another person's record.
* **The authorisation is short-lived.** Issuance proceeds only while the authentication is
  `SUCCESS` **and** within the configured VC window (default **5 minutes**) measured from
  `completed_at`. The window is **VC configuration**, deliberately independent of any expiry the
  authentication record carries for other consumers.
* **Issuance is keyed on `internal_record_id`**, not on a value the agent typed. The national ID only
  *finds* the record; the authenticated record identity is what the credential is built from.
* **The Agent Portal API owns the Registry lookup.** It reads the claims and **pushes** them into
  Certify; Certify never connects to the Registry, keeping the issuer decoupled from registry data.
* **Server-side issuance.** The backend drives Certify directly (a trusted machine-to-machine call)
  via the OpenID4VCI **pre-authorized-code** grant; there is no device holder key — the credential is a
  **bearer document** whose trust comes from the **issuer's signature**.
* **Every issuance is recorded.** The Registry keeps an issuance **event log** — which record, which
  credential id, which authentication, which agent, when. It stores a *reference*, never a copy of the
  credential or its claims.
* **The agent downloads the PDF.** It is streamed to the agent's browser, printed on whatever printer
  the counter has, and handed over.
* **Re-issue on demand.** A lost or stale credential is simply **re-issued** — a fresh authentication,
  a new credential, linked to the previous one in the issuance log.

## Presentation & verification

```
 Citizen ──(hands paper)──► Verifier ──(scans/uploads QR)──► checks COSE signature
                                                              against a PRE-LOADED
                                                              trust anchor  → ✅/❌
```

**What "offline" does and does not mean here.** The *signature check* needs no
call back to OpenG2P: the verifier holds the issuer key already. But **Inji
Verify is a web portal**, not a phone app — the verifying organisation hosts it
and a verifier uses it in a browser, by webcam or by uploading a photo of the
paper. A browser still has to load that page. A genuinely disconnected counter
needs Inji Verify's **SDK** (a React/NPM module) embedded in an installed
application. Inji **Wallet** is the phone app, and it is a *holder* app: it
stores the owner's own credentials and does not verify someone else's paper.

**Before any of this works, two things must be true**, and neither happens on
its own:

1. a verifier deployment exists (nothing verifies a credential until a relying
   party stands one up); and
2. the OpenG2P issuer's **ES256 QR key is loaded there as a trust anchor** —
   take it from `/v1/certify/.well-known/jwks.json`.

> **Unverified.** Whether a stock Inji Verify accepts a claim-169 CWT from a
> non-MOSIP issuer has not been tested end to end. Until it has, treat
> third-party verification as unproven rather than assumed.

* **The QR is the credential.** A full JSON-LD VC is far too large for a QR, so the QR carries a
  **compact, signed payload** — MOSIP's **"claim 169"** identity QR (CBOR), the CWT/mDoc family used
  by mDL / COVID certificates. Inji Certify supports this **natively** (no plugin) via the
  `credential_config` columns **`qr_settings` + `qr_signature_algo`**: each `qr_settings` entry is a
  Velocity template; Certify renders it, encodes it with the **pixel-pass** library, **signs it as a
  COSE/CWT** (`CoseSignatureService.cwtSign`), and **base45**-encodes the result into the VC under a
  `claim169` field.
* **Offline verification — where the key comes from.** The signed QR is a **COSE_Sign1 / CWT**. The
  claim-169 spec **does not** use `.well-known`/JWKS (DID) discovery for the QR; it uses **COSE**
  mechanisms in the signature header — `x5chain` (embedded cert), `x5t` (cert hash), or `x5u` (cert
  URI) — and assumes the verifier holds a **pre-loaded trust anchor** ("the app already has the
  country's/issuer's key"). Certify can embed the issuer cert (`x5c`) so verification is **fully
  offline**, but embedding it costs QR bytes, so issuers often **omit it and rely on the pre-distributed
  trust list**. Either way, no call back to OpenG2P at scan time. (The **JSON-LD VC** — not the QR —
  still uses `proof.verificationMethod = <issuerDID>#<key>`, resolvable via `did:web`.)

{% hint style="info" %}
**Photograph in the QR is deferred to Phase 2.** A QR is hard-capped at **~2.9 KB**, but claim 169 can
carry a **low-resolution face thumbnail** by combining a modern codec (attribute 62 allows
**WEBP / AVIF / JPEG / PNG / WSQ** — WEBP/AVIF give a recognisable face in **~1–2 KB**),
**integer-keyed CBOR**, **zlib/Brotli** compression and **Base45** packing. It is recognition-grade,
not high-resolution — the same approach as Aadhaar's Secure QR. When adopted, the photo will be
solicited as part of the **eSignet KYC response** (the ID system's own photograph, matching what the
beneficiary was authenticated against) and pushed to Certify as the `face` claim; Certify never fetches
images. See [Phase 2 — Device Wallet](phase-2-device-wallet.md).
{% endhint %}

## Architecture & components (Phase 1)

```
 Agent ──login (Keycloak `agent` realm)──► iam-agent-portal-api

 Agent Portal API ──reads──► OpenG2P Registry (foundational_id → internal_record_id, claims view)
 (agent-driven)    │
                   ├─initiate──► eSignet  (beneficiary: biometric / OTP)
                   │
                   └─push claims──► Inji Certify
                                      ├─ PreAuthDataProviderPlugin (built-in) → pushed claims = VC subject
                                      ├─ Velocity template  → VC body
                                      ├─ keymanager + .p12   → Ed25519 signature
                                      └─ (signed VC) ──► Agent Portal API → PDF + QR (downloaded)

 Verifier (separate):   Inji Verify ── scans QR ── validates vs issuer trust anchor (offline)
```

* **Agent Portal API** — the issuance backend, part of the **Registry Platform** so every registry
  manifestation inherits it. Ships **disabled by default** and is switched on per deployment.
* **Agent authentication** — `iam-agent-portal-api` (IAM service) against the Keycloak **`agent`**
  realm. Issuance itself is permission-gated on the Agent Portal API.
* **Beneficiary authentication** — the Registry's **registrant-authentication** subsystem with an
  **eSignet** provider. The same subsystem staff already use; the VC flow adds its own time window.
* **Inji Certify** — the issuer (used **stock**, no custom plugin). Builds the VC from a Velocity
  template and signs with its **embedded keymanager (PKCS12 `.p12`, no HSM)**. Certify's built-in
  **`PreAuthDataProviderPlugin`** makes the **pushed claims the credential subject** — so Certify needs
  **no Registry access**. (A custom pull connector exists for the wallet flow; see
  [Registry Data Connector](registry-data-connector.md).)
* **Agent web portal** — a thin reference client proving the chain, following OpenG2P UI conventions.
* **Inji Verify** — the verifier side. NOT a phone app: it is a **web portal** the
  verifying organisation deploys (scan by webcam, or upload a photo/scan of the
  paper), plus an **SDK** (a React/NPM module) for embedding the same
  scan-and-verify into a relying party's own application. The citizen installs
  nothing; the *verifier* runs it. Inji **Wallet** is the phone app, and it is a
  holder app — it stores your own credentials, it does not verify someone
  else's paper.

## What a registry manifestation must supply

The Registry Platform owns the service, the chart and the contract. Each manifestation (NSR, Farmer
Registry, …) supplies what is specific to it, because the fields differ:

* the **VC view** exposing the claim columns, keyed on `internal_record_id`;
* its **VC definitions** — credential type, template, fields, scope;
* the **card design** for the printed PDF;
* the **issuer DID** value for the environment.

## Two documents, two signatures, two keys

This surprises people, so it is worth being explicit. An issuance produces **two
separate signed things**, not one signed thing shown two ways:

| | The credential | The QR |
|---|---|---|
| What it is | the full **JSON-LD VC** (~1.5 KB) | a compact **CBOR** identity payload (~470 B) |
| Signature | `Ed25519Signature2020` (a Linked-Data proof) | `COSE_Sign1`, wrapped as a **CWT** (CBOR tag 61 → 18) |
| Algorithm | **EdDSA** (Ed25519) | **ES256** (ECDSA P-256) |
| Key alias | `CERTIFY_VC_SIGN_ED25519` / `ED25519_SIGN` | `CERTIFY_VC_SIGN_EC_R1` / `EC_SECP256R1_SIGN` |
| Set by | `credentialConfig.signatureAlgo` | `credentialConfig.qrSignatureAlgo` |
| Encoding | JSON | zlib → **Base45** (the `NCF…` string) |

**Why the QR needs its own signature.** The QR does **not** contain the JSON-LD
credential — it contains a different, much smaller document. A signature only
covers the exact bytes it was made over, so the Ed25519 proof over the JSON says
nothing about the CBOR payload. The compact form therefore carries its own
signature or it cannot be trusted at all.

**Why not simply put the signed JSON in the QR?** That is the fallback the
renderer uses when no `qrSettings` are configured, and it does work — but it is
roughly four times the data (1760 characters against 396), it crowds a QR whose
practical ceiling is about 2.9 KB, and it is not a shape claim-169 verifiers
recognise.

**Why two keys rather than one?** COSE also supports EdDSA, so the credential
key *could* sign both and there is no security objection to that — the two
structures cannot be confused. It is deliberately not done:

* **Compatibility.** ES256 is what the mDL / EU-DCC / claim-169 ecosystem
  actually implements. EdDSA is a registered COSE algorithm but less widely
  supported in verifier stacks, and the QR is the artefact most likely to meet a
  third-party verifier.
* **Key separation.** A compromised or rotated QR key does not disturb
  credential signing, and the QR algorithm can change without touching it.
* **Hardware.** P-256 is universally supported in secure elements and HSMs;
  Ed25519 support is patchier — worth preserving even though Phase 1 uses a
  `.p12`.

**Which signature is actually checked, and when.** The two are not
paper-versus-wallet — they are *transfer* versus *presentation*:

| | Signature 1 (Ed25519, on the VC) | Signature 2 (ES256, on the QR) |
|---|---|---|
| Paper (Phase 1) | not used — the citizen never receives the JSON | **the only thing verified** |
| Wallet, scanned at a counter | checked when the wallet **receives** the credential | **verified at the counter** |
| Wallet, OpenID4VP to a relying party | **the one verified** | not used in that exchange |

A wallet does not hand a shopkeeper a JSON-LD document: it **displays the
claim-169 QR on screen** and the verifier scans it — the same artefact as the
paper, the same scanner, the same trust anchor. So the QR signature is needed on
both paths, not only on paper.

The inversion is worth noticing: **in Phase 1 the Ed25519 signature is the one
nothing checks**, because the JSON is never handed out. It is not wasted — it is
what makes this a W3C Verifiable Credential, it is what a wallet validates on
receipt in Phase 2, and Certify produces it as part of issuing at all. It cannot
meaningfully be switched off.

Note also the nesting: Certify signs the compact CBOR payload FIRST, embeds the
resulting Base45 blob at `credentialSubject.claim169.qrCode`, and only then signs
the whole credential. Signature 2 therefore sits inside the bytes signature 1
covers — which is exactly why the credential proof cannot stand in for the QR's:
the QR travels alone, detached from the JSON that carried it.

**Where each key is published.**

* `GET /.well-known/did.json` — the **DID document**, resolving
  `did:web:<certify-host>`. It carries the **Ed25519** key only. Certify builds
  this document from the registered credential configs' `signatureAlgo`; it does
  not consult `qrSignatureAlgo`, so the QR key never appears here.
* `GET /v1/certify/.well-known/jwks.json` — **all** of Certify's public keys,
  the ES256 QR key included. This is where a verifier obtains the QR key.

That split is not a defect, because **claim-169 verification does not resolve
DIDs**. The COSE header carries only an `alg` and a `kid`; there is no
`x5chain`. A verifier is expected to already hold the issuer's key, from a
**pre-distributed trust list** — exactly as EU DCC and mDL work. Publishing the
key is therefore necessary but not sufficient: it must be **loaded into the
verifier as a trust anchor**. See [Deployment](deployment.md).

## Key management

Certify signs with its embedded keymanager backed by a **`.p12` keystore** (no HSM). The `.p12` and
the encrypted key rows **are the issuer identity** — they must be **persisted and backed up**, and the
issuer's **public key / DID must be published at a stable, resolvable URL** so verifiers can validate
offline. By default the Certify chart **generates `local.p12` on first boot onto a durable PVC**; to
redeploy with an existing identity, restore it from a Secret (`p12.existingSecret`). See
[Deployment](deployment.md) for the custody modes.

## Deliberately out of scope for Phase 1

| Deferred | Why |
|----------|-----|
| **Photograph in the QR** (claim 169 `face`) | Sequenced after the core chain; needs the eSignet KYC photo and a hard QR size budget. |
| **Revocation / status lists** | Paper is verified **offline**, so a status list cannot be checked at scan time. Short credential validity is the compensating control for now. Certify already ships the status-list tables for when this is taken up. |
| **Android agent app** | The web portal comes first; the app follows against the identical API, adding Bluetooth printing for roaming agents. |
| **Non-digital fallback** | Issuance always requires eSignet authentication. A beneficiary with neither a phone nor an available biometric device cannot be issued a credential. |

## Status

**Proven end to end:** claims are read from a real registrant, pushed to Certify, Certify returns an
**Ed25519-signed** `OpenG2PBeneficiaryCredential`, and a **printable PDF with a QR** is rendered (see
[Local Developer Trial](local-setup.md)).

**In progress:** eSignet beneficiary authentication as a
mandatory gate, issuance keyed on `internal_record_id`, the issuance event log, and the reference agent
portal. Then: switch the QR to Certify's **compact signed** form (`qr_settings` + `qr_signature_algo`)
and confirm **Inji Verify validates it offline** against the issuer's trust anchor.
