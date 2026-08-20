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
   │                     │ 6. callback → authentication COMPLETED                │
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
  `COMPLETED` **and** within the configured VC window (default **5 minutes**) measured from
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
* **Inji Verify** — the verifier app that scans and validates the QR offline.

## What a registry manifestation must supply

The Registry Platform owns the service, the chart and the contract. Each manifestation (NSR, Farmer
Registry, …) supplies what is specific to it, because the fields differ:

* the **VC view** exposing the claim columns, keyed on `internal_record_id`;
* its **VC definitions** — credential type, template, fields, scope;
* the **card design** for the printed PDF;
* the **issuer DID** value for the environment.

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

**In progress:** the agent-facing service and `agent` realm, eSignet beneficiary authentication as a
mandatory gate, issuance keyed on `internal_record_id`, the issuance event log, and the reference agent
portal. Then: switch the QR to Certify's **compact signed** form (`qr_settings` + `qr_signature_algo`)
and confirm **Inji Verify validates it offline** against the issuer's trust anchor.
