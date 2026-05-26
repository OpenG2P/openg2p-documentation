---
description: >-
  How a citizen holds and presents a Verifiable Credential — the three options
  (paper, hosted wallet, device wallet), who each serves, an honest comparison,
  and why OpenG2P does paper first and self-owned smartphone wallets next.
---

# Custody Options & Strategy

## The problem isn't issuance — it's custody

Issuing a signed VC is the easy part. The hard part is **how a citizen keeps it and shows it to a
verifier**, for an audience that may have **no smartphone, no computer, at most a feature phone, or
no device at all**, and limited digital literacy.

Classic Verifiable Credentials are built around a **holder with a device and a wallet** that stores
keys and "presents" credentials. That assumption **excludes exactly the population OpenG2P serves**.
So a device wallet is the *top* of the pyramid, not the starting point.

## The three options

Ranked by **what the citizen must own** (least → most):

### Option A — Paper credential (lowest common denominator)
* **Citizen owns:** nothing.
* **Issuance:** **assisted** — at a kiosk/CSC, an authenticated agent looks the citizen up by their
  **functional ID**, Certify issues and signs the credential, and it is **printed as a PDF with an
  offline-verifiable signed QR**.
* **Presentation:** the citizen hands over the paper; a verifier scans the QR with **Inji Verify**
  and validates the signature **offline** against the issuer's published key/DID.
* **Needs from the citizen:** no device, no login, no connectivity.

### Option B — Hosted wallet (custodial locker)
* **Citizen owns:** a phone (for OTP) **and** access to a real **browser** (own device, kiosk,
  borrowed, desktop).
* **Mechanism:** credentials stored **server-side** (Mimoto); the citizen **logs in** (phone+OTP) via
  **Inji Web** to view, re-print, or present online (OpenID4VP). It is the **DigiLocker** model —
  custodial: the operator holds the keys and credentials.
* **Needs from the citizen:** a browser session + the ability to log in.

### Option C — Device wallet (self-sovereign)
* **Citizen owns:** a **smartphone**.
* **Mechanism:** credentials and keys live **on the device** (Inji Mobile); presentation by QR/BLE
  offline or **OpenID4VP** online; supports selective disclosure.
* **Needs from the citizen:** a smartphone + the wallet app + some literacy.

## Comparison

| Dimension | A — Paper | B — Hosted | C — Device |
|---|---|---|---|
| Citizen device required | **none** | browser access | smartphone |
| Works fully offline (citizen side) | ✅ | ❌ (needs login) | ✅ |
| In-person verification | ✅ scan QR | ✅ | ✅ |
| Remote / online presentation | ❌ | ✅ | ✅ |
| Holder-bound (anti-copy) | ❌ bearer (copyable) | ✅ bound to login | ✅ bound to device key |
| Selective disclosure / privacy | ❌ all-or-nothing | partial (server sees all) | ✅ best |
| Live revocation at presentation | ❌ offline | ✅ | ✅ |
| Recovery if lost | re-issue at kiosk | ✅ re-login | ❌ unless backup |
| Keys held by | n/a | **operator (custodial)** | **citizen (self-sovereign)** |

## Who each option actually serves

* **Device-less citizen → A (paper).** The only option that needs nothing from them.
* **Feature-phone citizen → still A.** A feature phone only *receives an OTP*; it can't run a wallet
  app **or** the hosted-wallet browser UI. So the OTP alone unlocks nothing — they're served by
  paper (or an assisted/borrowed browser, which is really B-with-help).
* **"Browser-but-no-smartphone" citizen → B.** A genuine but **narrow and shrinking** slice: has a
  phone + occasional browser access (kiosk/borrowed/desktop) but no smartphone, and needs *online*
  presentation. Squeezed from below by paper (in-person) and above by smartphones.
* **Smartphone owner → C.** The device wallet is **strictly more capable** than the hosted wallet
  for them (on-device keys, offline, privacy, control). A hosted wallet adds them almost nothing.

### What the hosted wallet uniquely enables — and its limits
The only things paper fundamentally cannot do, that a wallet can: **remote/online presentation
(OpenID4VP)** and **holder-bound (non-copyable) presentation**. But:
* these matter only when **online relying parties** accept VCs and/or **fraud/privacy** pressure is
  real — for purely **in-person** interactions, paper already suffices;
* the hosted wallet's convenience benefits (durability, re-access, freshness) are largely matched in
  Phase 1 by **re-issue-on-demand** at a kiosk (the data lives in the registry; Certify is stateless);
* and for a smartphone owner, the **device wallet** delivers those same capabilities, better.

## The deeper point: B vs C is a *policy* choice, not just a tier

Hosted vs device is **custodial vs self-sovereign**:

* **Hosted (B) = custodial locker.** The operator holds the citizen's keys/credentials; centrally
  **recoverable, assist-able, works without owning a device**. Some governments *prefer* this
  (DigiLocker-style) as the primary digital channel.
* **Device (C) = self-sovereign.** The citizen holds keys; maximal privacy/control; but must own and
  manage a device, and losing it (without backup) loses the credentials.

So "skip B, go A → C?" is really: *does the program want a government-run custodial locker as a
first-class channel, or self-sovereign wallets?* OpenG2P's direction is **self-sovereign**, so B is
not a default tier.

## The strategy

| Phase | Option | Audience | Why |
|---|---|---|---|
| **1 (now)** | **A — Paper** | device-less majority (+ feature-phone) | Lowest common denominator; needs nothing from the citizen; removes all wallet/IdP complexity |
| **2** | **C — Device wallet** (self-owned) | smartphone owners (growing) | Self-sovereign; full offline + online presentation |
| — | **B — Hosted wallet** | "browser-no-smartphone" minority | **Considered, not chosen** — adopt only as a deliberate custodial-locker policy |
| separate | Consent-based data sharing | dept ↔ dept / third parties | Registry partner APIs + consent — not a wallet feature |

**Consequence:** Phase 1 needs only **Certify (issue + sign) + the Registry connector + a signed
QR/PDF + Inji Verify**. No Logto, no Mimoto, no hosted-wallet login, no OpenID4VCI device flow — i.e.
none of the integration complexity those paths require. See
[Phase 1 — Paper Credential](phase-1-paper-credential.md).
