---
description: How to onboard a partner so its signed requests are trusted
---

# Onboarding Partners

The Bridge (and SPAR) verify a **detached JWS** signature on every partner request.
Partners and their public keys live in the **Partner Manager (PM)** service — the
Bridge does **not** store partner keys. To verify a signature, the Bridge fetches the
signer's public key from PM (`GET /keys/PARTNER_<MNEMONIC>`). "Onboarding a partner"
therefore means **registering that partner (and its public key) in Partner Manager**.

For the concept and wire format, see the design page
[Partner APIs → Authentication](../../products/g2p-bridge/design-specifications/partner-apis.md#authentication)
and [PyJWTCryptoHelper](../../platform/platform-services/privacy-and-security/pyjwtcryptohelper.md).
This page is the **operational steps**.

{% hint style="info" %}
**Certificates are public — private keys never leave the owner.** A partner keeps its
private key; it gives you only its public **certificate/key**. Verification is
**signature-validity only** (no CA / trust-root check). Onboarding happens in **Partner
Manager**, not the Bridge — the Bridge just reads PM at runtime.
{% endhint %}

## The rule to remember

PM serves keys under an id of the form **`PARTNER_<MNEMONIC>`**, where `<MNEMONIC>` is
the caller's **`sender_app_mnemonic`** (upper-cased) sent in the request envelope. So
the partner id you register in PM **must equal `PARTNER_` + the mnemonic the partner
signs with**, or verification fails with `rjct.jwt.invalid`. The JWS header `kid` must
match a `kid` registered for that partner in PM.

## Onboard a partner that calls the Bridge (inbound)

A partner (bank, PSP, PBMS, …) that calls the Bridge Partner API must be registered in
Partner Manager with its public key.

1. **Collect** the partner's public **certificate or key** (PEM / X.509 / JWK), its
   **mnemonic** (used as `sender_app_mnemonic`, e.g. `MY_PSP`), and optionally a `kid`.
2. **Register it in Partner Manager.** Use PM's **staff portal UI**, or its admin API
   (requires a Keycloak staff-realm token with the **`partner_manager`** role). It is a
   two-step **request → approve** flow:

   ```bash
   # 1) create the onboarding request
   curl -X POST "$PM_ADMIN/partners/requests/onboarding" \
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     -d '{"partner_id":"PARTNER_MY_PSP","name":"My PSP",
          "keys":[{"public_key":"-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----\n",
                   "kid":"my-psp-1","algorithm":"RS256"}]}'
   # → returns {"id": "<request_id>", ...}

   # 2) approve it → partner + key become active
   curl -X POST "$PM_ADMIN/partners/requests/<request_id>/approve" \
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     -d '{"notes":"approved"}'
   ```

   (`$PM_ADMIN` = the PM staff-portal-api base, e.g.
   `http://commons-services-pm-staff-portal-api`.)
3. **Verify** PM serves the key: `GET $PM_PARTNER_API/keys/PARTNER_MY_PSP` returns 200
   with the key. From then on the Bridge verifies that partner's signed calls
   automatically — nothing to configure on the Bridge.

{% hint style="warning" %}
**Enforcement.** Inbound verification is active when
`global.g2pBridgeSignatureValidationEnabled` is `true` (the default) — or whenever the
trial test partner is enabled. Onboard partners in PM **before** turning it on, or
their calls are rejected.
{% endhint %}

## Register the Bridge with SPAR (outbound)

The Bridge **signs** its resolve requests to SPAR, so SPAR must be able to fetch the
Bridge's public key from PM. Because both the Bridge and SPAR read the **same** Partner
Manager, you register the Bridge **once** in PM and both sides work. The Bridge signs as
mnemonic **`g2p_bridge`**, so register it as **`PARTNER_G2P_BRIDGE`**:

1. Take the Bridge's **public cert** (`g2p-bridge.crt` from
   [Partner Signing Key → Step 1](partner-signing-key.md#step-1-generate-your-own-keypair)).
2. Onboard `PARTNER_G2P_BRIDGE` in PM with that cert (same request → approve flow as
   above), using the same `kid` the Bridge signs with (`global.g2pBridgeSigningKeyKid`).

{% hint style="info" %}
The bundled **trial** does this automatically: the chart's **`pm-seed` Job** onboards
`PARTNER_G2P_BRIDGE` (plus `PARTNER_TEST_SANITY` / `PARTNER_TRAINING`) in PM with the
committed test cert on every install/upgrade — so an out-of-the-box install verifies
end-to-end with no manual onboarding. It authenticates to PM with the staff-realm
Keycloak client `commons-services-staff-portal` (Partner Manager provisions this
`<release>-staff-portal` client and it must hold the `partner_manager` role).
{% endhint %}

## Rotating or removing a partner

All of this is done **in Partner Manager**, not the Bridge:

* **Rotate / add a key:** `POST /partners/requests/key-update` with the new key (and any
  `revoke_kids`), then approve. Multiple active keys (kids) per partner are supported.
* **Disable / revoke:** `POST /partners/{partner_id}/disable` (PM then serves no keys →
  the partner's signatures stop verifying) or revoke individual kids via `key-update`.

Because keys are fetched live from PM (with a short cache), changes take effect within
the cache TTL — no Bridge redeploy needed.
