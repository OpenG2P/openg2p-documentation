---
description: >-
  Phase 2 (future) — self-owned smartphone wallets (Inji Mobile). The
  self-sovereign upgrade for citizens who have a smartphone.
---

# Phase 2 — Device Wallet (future)

Phase 2 adds **self-owned smartphone wallets** for the growing segment of citizens who have a
smartphone. It is the **self-sovereign** complement to Phase 1's paper credential — the citizen
holds their own keys and credentials on their device.

> This is a forward-looking section. Phase 1 (paper) is the implementation focus; Phase 2 is added
> as smartphone adoption in the target population grows.

## Carried over — capabilities deferred from Phase 1

These are **not** wallet features; they were consciously sequenced out of Phase 1 and are picked up
here so nothing is lost track of.

| Deferred capability | Why it was deferred | What taking it up involves |
|---------------------|---------------------|-----------------------------|
| **Photograph in the claim-169 QR** | Sequenced behind the core issuance chain. | Request the photo as part of the **eSignet KYC** response (the ID system's own photograph, matching what the beneficiary authenticated against), downscale it to a **~1–2 KB** WEBP/AVIF thumbnail, and push it as the **`face`** claim so Certify embeds it in the signed QR. Needs a hard size budget: the whole QR is capped at **~2.9 KB**, shared with the signature and any embedded certificate. Certify never fetches images — the bytes must be pushed. |
| **Revocation / status lists** | A paper credential is verified **offline**, so a status list cannot be consulted at scan time; short credential validity is the Phase-1 compensating control. | Certify already ships the status-list tables (`status_list_credential`, `credential_status_transaction`, `status_list_available_indices`) and `allowed-status-purposes={'revocation'}`. A device wallet **can** be online at presentation, so revocation becomes genuinely checkable — which is why it belongs here. Decide the posture (revocation vs suspension) and who may revoke. |
| **Android agent app** | The reference **web** portal came first, against the same API. | A native client adds field-grade capability for roaming agents — most importantly **Bluetooth printing**, which a browser cannot do. The eSignet redirect is handled with a Custom Tab plus polling of the authentication status, so no deep-link plumbing is required. |

## What it adds over paper

* **Holder-bound presentation** — bound to a key on the device, so a credential can't simply be
  photocopied and reused (unlike bearer paper).
* **Online / remote presentation (OpenID4VP)** — present digitally to a remote relying party, not
  only face-to-face.
* **Offline presentation** — QR/BLE in the field, no connectivity needed.
* **Selective disclosure** — reveal only the claims a verifier needs.
* **Self-service** — fetch, hold, and re-present without a kiosk trip.

## Component
* **Inji Mobile** — MOSIP's OpenID4VCI device wallet (Android/iOS). Any OpenID4VCI-compliant wallet
  also interoperates, since Certify is standards-based.

## Same issuer, registry data pulled (not pushed)
Phase 2 reuses the **same Inji Certify issuer** — only the **holder/delivery** changes (a device
wallet instead of paper). The data path, however, flips: instead of the Phase-1 **push** (where the
Agent Portal API reads the Registry and pushes claims), the wallet does an interactive **OpenID4VCI**
download, so **Certify pulls** the citizen's claims itself via the custom **Registry connector**
(`RegistryDataProviderPlugin`), keyed by the citizen's authenticated token claim. See
[Registry Data Connector](registry-data-connector.md).

That wallet flow needs an OAuth2/OIDC **authorization server** and introduces the integration
considerations (token type, `c_nonce`, the AS choice) that Phase 1 deliberately avoids. Those are
taken up when Phase 2 is scheduled.

## Not in scope (separate tracks)
* **Hosted/custodial wallet (Option B, Inji Web + Mimoto)** — considered but **not chosen**; see
  [Custody Options & Strategy](custody-options-and-strategy.md). Adopt only as a deliberate
  custodial-locker policy.
* **Consent-based data sharing** (department ↔ department / third-party pull) — a registry
  partner-API + consent concern, not a wallet feature.
