---
description: >-
  Phase 1.5 — the agent hands a credential straight into the citizen's own wallet
  at the counter, using an OpenID4VCI credential offer. Same authentication, same
  Certify, same push as paper; only the delivery changes.
---

# Wallet Handover (Phase 1.5)

A citizen who owns a smartphone should not have to take a printed card. This adds a
second **delivery channel** to Phase 1: at the same counter, after the same
authentication, the agent can hand the credential into the citizen's wallet
instead of — or as well as — printing it.

It is deliberately **not Phase 2**. Phase 2 is self-service: the citizen opens a
wallet at home, authenticates, and downloads without an agent, which requires
Certify to **pull** claims from the registry. This keeps the agent, keeps the
**push**, and keeps the kiosk trip. What it buys is holder binding and digital
presentation, not self-service.

## Why it is nearly free

Phase 1 already performs the whole of OpenID4VCI server-side. The only change is
**where the flow stops**:

| Step | Paper | Wallet handover |
|---|---|---|
| `POST /pre-authorized-data` (push the claims) | Agent Portal API | Agent Portal API |
| `GET /credential-offer-data/{id}` | Agent Portal API | **the wallet** |
| `POST /oauth/token` (redeem) | Agent Portal API | **the wallet** |
| `POST /issuance/credential` (fetch) | Agent Portal API | **the wallet** |
| Holder key | ephemeral, minted by the API | **the wallet's own** |

Because the wallet performs the last three steps, the proof-of-possession JWT is
signed by a key the wallet holds — so `credentialSubject.id` is the wallet's own
`did:jwk`, and the credential is bound to that device. We never see the issued
credential and never hold the holder key.

No second Certify instance, no data-provider plugin, no change to eSignet. It is
the **issuer-initiated pre-authorized-code** flow that OpenID4VCI defines for
exactly this situation.

## The flow

```
1. Agent looks the beneficiary up and the beneficiary authenticates at eSignet
   — identical to paper, and the same gate.

2. Agent chooses "hand to wallet".
   API pushes the claims to Certify and receives a credential OFFER:

   openid-credential-offer://?credential_offer_uri=
     https://<certify-host>/v1/certify/credential-offer-data/<uuid>

3. The portal shows it as a QR. The agent READS OUT a short tx_code.

4. Citizen scans it with their wallet, which fetches the offer and sees it
   requires a transaction code.

5. Wallet prompts for the code; the citizen types what the agent read out.

6. Wallet redeems it against Certify directly:
       POST /oauth/token           (pre-authorized_code + tx_code)
       POST /issuance/credential   (proof JWT signed by the WALLET's key)

7. Certify returns the signed credential. The wallet stores it.
```

The QR is **not** the credential. It is a short-lived, single-use pointer to it.

## The `tx_code` is the whole security model

A credential offer is the credential, to whoever redeems it first. The `tx_code`
is the only thing tying the offer to the person standing at the counter.

* **Read it aloud. Never print it beside the QR**, or it protects nothing.
* Keep the offer **short-lived** (default 300s) — an offer left on a screen is a
  credential waiting to be claimed.
* The pre-authorized code is **single-use**, which limits a race to one winner but
  does not prevent the wrong person being that winner.

## What the citizen's wallet must support

Confirmed against Inji Wallet's documentation: it supports **scanning and
redeeming credential offers** for pre-authorized downloads, **with and without a
transaction code**, and accepts offers **via deep link** as well as QR. Its
VCI client libraries list *Credential Offer + VC Data Model 1.1* support, which
matches what OpenG2P issues.

**Mimoto is not required.** Mimoto serves the wallet's "browse issuers" list,
which this flow does not use — the offer carries everything the wallet needs.

{% hint style="warning" %}
These are recent Inji capabilities. Confirm against the build you intend to
deploy before committing to this channel.
{% endhint %}

Any OpenID4VCI-conformant wallet works; nothing here is Inji-specific.

## Switching it on

| Value | Effect | Default |
|---|---|---|
| `agentPortalApi.vcIssuance.enabled` | Paper — the printed card | `false` |
| `agentPortalApi.walletIssuance.enabled` | Wallet handover | `false` |
| `agentPortalApi.walletIssuance.offerExpiresInSeconds` | Offer lifetime | `300` |

Independent switches: paper only, wallet only, or both. `walletIssuance` requires
`vcIssuance` because the route lives on the issuance controller. With it off the
route is not mounted at all, so an install that issues paper exposes no wallet
surface.

Both channels share `register:issue_credential`. It is the same act — issuing a
credential to an authenticated beneficiary — and splitting the permission would
authorise someone for one delivery channel but not the other for no defensible
reason.

## What is NOT recorded

No issuance-log row is written when the offer is created. **Nothing has been
issued yet** — the credential only exists once the wallet redeems the offer, which
happens out of our sight. Writing a row at offer time would over-report issuance,
and the audit event (`offer_credential_to_wallet`) is the honest record of what
actually happened: an offer was made.

This is a real difference from paper, where the API sees the issued credential and
logs it. If reconciliation matters, that gap has to be closed on Certify's side,
not ours.

## Testing without a wallet app

The wallet's part is plain HTTP — redeem, prove, fetch — with nothing app-specific
in it. `test/sanity/tests/test_e2e_wallet_issuance.py` therefore **acts as the
wallet**: it generates its own keypair, performs those three calls against Certify,
and asserts the returned credential is bound to **the key it generated**. It also
checks that an offer is refused without beneficiary authentication, and that a
pre-authorized code cannot be redeemed twice.

That proves the issuance chain without installing anything. It does not prove a
particular wallet app's UI.

## Where this sits

| | Paper (Phase 1) | **Wallet handover (1.5)** | Phase 2 |
|---|---|---|---|
| Agent needed | yes | yes | **no** |
| Claims | pushed | pushed | **pulled** |
| Certify instances | one | one | **second, eSignet as AS** |
| Holder binding | none (bearer paper) | **device key** | device key |
| Self-service | no | no | **yes** |

See [Phase 1 — Paper Credential](phase-1-paper-credential.md) for the shared
issuance chain, and [Phase 2 — Device Wallet](phase-2-device-wallet.md) for the
self-service design this does not deliver.
