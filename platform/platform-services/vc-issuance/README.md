---
description: >-
  Issuing Verifiable Credentials from OpenG2P data (Registry first) with MOSIP
  Inji Certify — and, crucially, how a citizen holds and presents them. Phase 1
  is paper-based; Phase 2 is self-owned smartphone wallets.
---

# VC Issuance

## Overview

**VC Issuance** turns a citizen's OpenG2P data (their **Registry** record first; later PBMS, SPAR) into a standards-based **Verifiable Credential (VC)** signed by **MOSIP Inji Certify**.

The hard question is **not** issuing the VC — it's **how the citizen holds and presents it**, for a population that may have **no smartphone, no laptop, sometimes only a feature phone, sometimes no device at all**. That single constraint drives the whole design.

## The real design question: holder custody

There are three ways a citizen can hold and present a credential. They differ entirely by **what the citizen must own**:

| Option                | Citizen must have                    | Holds the VC as                    | Presents by                                       | Inji component                 |
| --------------------- | ------------------------------------ | ---------------------------------- | ------------------------------------------------- | ------------------------------ |
| **A — Paper**         | **nothing** (an agent assists)       | a **printed PDF with a signed QR** | hands over paper; verifier scans the QR (offline) | Certify + QR/PDF + Inji Verify |
| **B — Hosted wallet** | a phone (OTP) **and** browser access | server-side (custodial)            | log in to view / print / present online           | Inji Web + Mimoto              |
| **C — Device wallet** | a **smartphone**                     | on the device (self-held keys)     | QR / OpenID4VP from the phone                     | Inji Mobile                    |

See the full analysis and comparisons in [Custody Options & Strategy](custody-options-and-strategy.md).

## Why this matters (the reasoning in brief)

* **Classic VCs assume a holder with a device.** That excludes exactly the people we care about. So "give everyone a wallet" is the _top_ of the pyramid, not the **lowest common denominator**.
* **The LCD is Option A (paper).** An agent issues the credential, it's printed as a PDF with an **offline-verifiable signed QR**, the citizen carries paper, and any verifier scans it with Inji Verify — **no device, no login, no connectivity for the citizen.**
* **A feature phone doesn't change this** — it only receives an OTP; it can't run a wallet or the hosted-wallet browser UI. So the feature-phone user is still served by paper.
* **The hosted wallet (B) adds little for our audience.** For the device-less it's unusable; for a smartphone owner the device wallet is strictly better. Its only genuine edge is _online presentation for a "browser-but-no-smartphone"_ minority — a narrow, shrinking slice. B is really a **policy choice** (a custodial government locker, DigiLocker-style) rather than a capability tier.
* **Device wallet (C) is the self-sovereign upgrade** for the growing smartphone segment.

## Strategy (what we are building)

* **Phase 1 — Paper (Option A).** Assisted issuance → signed QR/PDF → offline verification. An
  **Agent Portal API** reads the citizen's Registry record and **pushes** the claims into Certify
  (which stays decoupled from the Registry), then prints the signed QR/PDF. The backbone for the
  device-less majority. **No hosted wallet, no Logto, no Mimoto, no OpenID4VCI device flow** — which
  removes almost all integration complexity.
* **Phase 2 — Self-owned smartphone wallet (Option C).** Inji Mobile device wallets for citizens
  who have smartphones (self-sovereign, online + offline presentation).
* **Option B (hosted wallet) — considered, not chosen.** Documented for completeness; it would only
  be adopted as a deliberate **custodial-locker policy**, not as a default tier.
* **Consent-based data sharing** (department ↔ department / third-party "pull") is a **separate
  track** (registry partner APIs + consent), not a wallet feature — out of scope here.

**One shared issuance service per environment.** A single **standard Inji Certify** instance (no
custom plugin — Certify's built-in `PreAuthDataProviderPlugin` turns the pushed claims into the VC)
serves **all** modules (Registry, PBMS, SPAR …). Each module pushes its own claims; each VC type is a
`credential_config` row, and each can sign under its own issuer **DID/key** — so one instance hosts
many credential types and many issuers. See
[Deployment](deployment.md#one-shared-issuance-service-per-environment).

## Sub-pages

| Page                                                          | Contents                                                                                                                |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| [Custody Options & Strategy](custody-options-and-strategy.md) | Full A/B/C analysis, comparisons, the LCD/feature-phone/custodial-vs-self-sovereign reasoning, and the phasing decision |
| [Phase 1 — Paper Credential](phase-1-paper-credential.md) | The assisted push-issuance → signed QR/PDF → offline-verify design and architecture (incl. the Agent Portal API) |
| [Registry Data Connector](registry-data-connector.md) | How Certify gets claims: the Phase-1 **push** path vs. the **pull** connector plugin (used by the Phase-2 wallet flow) |
| [Deployment](deployment.md) | Running the Phase-1 stack (Agent Portal API + Certify) on Kubernetes, reusing cluster PostgreSQL |
| [Local Developer Trial](local-setup.md) | A verified local run that issues a signed VC + printable QR/PDF from real registry data |
| [Phase 2 — Device Wallet](phase-2-device-wallet.md) | Future: self-owned smartphone wallets (Inji Mobile) |

## Status

The Phase-1 path is proven end to end (verified locally): the **Agent Portal API** reads a real
registrant from the OpenG2P registry, **pushes** the claims into **Inji Certify**, which returns an
**Ed25519-signed** credential, and the API renders a **printable PDF with a QR**. Remaining focus:
switching to Certify's **compact signed QR** and verifying it offline with **Inji Verify**.
