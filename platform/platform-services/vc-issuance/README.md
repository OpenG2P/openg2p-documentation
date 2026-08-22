---
description: >-
  Issuing Verifiable Credentials from OpenG2P data (Registry first) with MOSIP
  Inji Certify — and, crucially, how a citizen holds and presents them. Phase 1
  is paper-based; Phase 2 is a self-owned smartphone wallet.
---

# Verifiable Credentials

## Overview

**Verifiable Credentials** turns a citizen's OpenG2P data (their **Registry** record first; later PBMS, SPAR) into a standards-based **Verifiable Credential (VC)** signed by **MOSIP Inji Certify**.

The hard question is **not** issuing the VC — it's **how the citizen holds and presents it**, for a population that may have **no smartphone, no laptop, sometimes only a feature phone, sometimes no device at all**. That single constraint drives the whole design.

## The real design question: holder custody

There are three ways a citizen can hold and present a credential. They differ entirely by **what the citizen must own**:

| Option                | Citizen must own                     | Holds the VC as                    | Presents by                                       | Inji component                 |
| --------------------- | ------------------------------------ | ---------------------------------- | ------------------------------------------------- | ------------------------------ |
| **A — Paper**         | **nothing** (an agent assists)       | a **printed PDF with a signed QR** | hands over paper; verifier scans the QR (offline) | Certify + QR/PDF + Inji Verify |
| **B — Hosted wallet** | a phone (OTP) **and** browser access | server-side (custodial)            | log in to view / print / present online           | Inji Web + Mimoto              |
| **C — Device wallet** | a **smartphone**                     | on the device (self-held keys)     | QR / OpenID4VP from the phone                     | Inji Mobile                    |

See the full analysis and comparisons in [Custody Options & Strategy](custody-options-and-strategy.md).

{% hint style="warning" %}
**Owning nothing is not the same as proving nothing.** Option A means the citizen needs no device to **hold** the credential. It does **not** mean issuance is unauthenticated: a credential is only issued after the beneficiary **digitally authenticates** through **eSignet** — by **biometric at the agent's counter**, or by **OTP** to their phone. Biometric authentication is what keeps this open to the device-less majority. See [Phase 1 — Paper Credential](phase-1-paper-credential.md).
{% endhint %}

## Why this matters (the reasoning in brief)

* **Classic VCs assume a holder with a device.** That excludes exactly the people we care about. So "give everyone a wallet" is the _top_ of the pyramid, not the **lowest common denominator**.
* **The LCD is Option A (paper).** An agent issues the credential, it's printed as a PDF with an **offline-verifiable signed QR**, the citizen carries paper, and any verifier scans it with Inji Verify — **no device and no connectivity are needed to carry or present it.**
* **A feature phone doesn't change this** — it can receive an OTP, but it can't run a wallet or the hosted-wallet browser UI. So the feature-phone user is still served by paper.
* **The hosted wallet (B) adds little for our audience.** For the device-less it's unusable; for a smartphone owner the device wallet is strictly better. Its only genuine edge is _online presentation for a "browser-but-no-smartphone"_ minority — a narrow, shrinking slice. B is really a **policy choice** (a custodial government locker, DigiLocker-style) rather than a capability tier.
* **Device wallet (C) is the self-sovereign upgrade** for the growing smartphone segment.

## Two parties, two very different authentications

Phase-1 issuance involves **two** authenticated actors, and conflating them is the most common misreading of this design:

| Actor           | Authenticates against              | How                                                  | Why                                                          |
| --------------- | ---------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------ |
| **Agent**       | **Keycloak**, `agent` realm        | username + password (a normal portal login)          | Authorises the operator to use the Agent Portal at all       |
| **Beneficiary** | **eSignet**, against the ID system | **biometric** at the counter, or **OTP** to a phone  | Authorises the issuance of *this* credential to *this* person |

Agents and staff are **entirely distinct**: a separate realm, a separate API, and a separate portal. A staff user administering registers is not an agent, and holds no power to issue credentials.

## Strategy (what we are building)

* **Phase 1 — Paper (Option A).** Agent-assisted issuance, gated by the beneficiary's own eSignet authentication → signed QR/PDF → offline verification. An **Agent Portal API** reads the citizen's Registry record and **pushes** the claims into Certify (which stays decoupled from the Registry), then renders the signed QR/PDF for the agent to download and print. The backbone for the device-less majority. **No hosted wallet, no Mimoto, no OpenID4VCI device flow** — which removes almost all integration complexity.
* **Phase 2 — Self-owned smartphone wallet (Option C).** Inji Mobile device wallets for citizens who have smartphones (self-sovereign, online + offline presentation).
* **Option B (hosted wallet) — considered, not chosen.** Documented for completeness; it would only be adopted as a deliberate **custodial-locker policy**, not as a default tier.
* **Consent-based data sharing** (department ↔ department / third-party "pull") is a **separate track** (registry partner APIs + consent), not a wallet feature — out of scope here.

**One shared issuance service per environment.** A single **standard Inji Certify** instance (no custom plugin — Certify's built-in `PreAuthDataProviderPlugin` turns the pushed claims into the VC) serves **all** modules (Registry, PBMS, SPAR …). Each module pushes its own claims; each VC type is a `credential_config` row, and each can sign under its own issuer **DID/key** — so one instance hosts many credential types and many issuers. See [Deployment](deployment.md#one-shared-issuance-service-per-environment).

## Sub-pages

| Page                                                          | Contents                                                                                                                |
| ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| [Custody Options & Strategy](custody-options-and-strategy.md) | Full A/B/C analysis, comparisons, the LCD/feature-phone/custodial-vs-self-sovereign reasoning, and the phasing decision |
| [Phase 1 — Paper Credential](phase-1-paper-credential.md)     | The issuance chain end to end: agent login, beneficiary eSignet authentication, push-issuance, signed QR/PDF            |
| [Registry Data Connector](registry-data-connector.md)         | How Certify gets claims: the Phase-1 **push** path vs. the **pull** connector plugin (used by the Phase-2 wallet flow)  |
| [Deployment](deployment.md)                                   | Running the Phase-1 stack (Agent Portal API + Certify) on Kubernetes, reusing cluster PostgreSQL                        |
| [Local Developer Trial](local-setup.md)                       | A verified local run that issues a signed VC + printable QR/PDF from real registry data                                 |
| [Phase 2 — Device Wallet](phase-2-device-wallet.md)           | Future: self-owned smartphone wallets, plus the capabilities deliberately deferred from Phase 1                          |

## Status

The **issuance and signing chain** is proven end to end (verified locally): claims are read from a real registrant in the OpenG2P registry, **pushed** into **Inji Certify**, which returns an **Ed25519-signed** credential, and a **printable PDF with a QR** is rendered.

Currently being built on the Registry Platform: the **agent-facing service** (`agent` realm), **beneficiary authentication via eSignet** as a mandatory gate, issuance keyed on the registry's `internal_record_id`, an **issuance event log**, and the reference **agent web portal**. Deferred to Phase 2: the **photograph in the QR** (MOSIP claim 169) and **revocation / status lists**.

## Guides still to be written

Three things are configurable today but have no guide, so each is currently done
by reading someone else's `values.yaml`:

* **Authoring a credential template.** What `type` actually means (the second
  entry is the credential's own type and must match `credentialConfigKeyId`, the
  `@context` term and the Certify `credentialTypes`), where `${validFrom}` /
  `${validUntil}` / `${_holderId}` / `${_issuer}` come from, and which names are
  free to invent. A wrong name is not an error — Velocity emits it verbatim — so
  the rules need writing down.
* **Adding agents.** Creating real agents in the `agent` realm, granting
  `register:issue_credential`, and retiring one. The chart seeds a single demo
  `agent` user, which is not how a deployment runs.
* **Changing what a credential contains.** The claim fields, the JSON-LD body and
  the printed card are edited in four different places that must agree; that is
  worth one page with the order to change them in.
