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
