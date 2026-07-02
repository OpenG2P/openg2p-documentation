---
description: How to onboard a partner so its signed requests are trusted
---

# Onboarding Partners

The Bridge (and SPAR) verify a **detached JWS** signature on every partner request.
"Onboarding a partner" means **registering that partner's public certificate** so the
receiver trusts its signature. Nothing else (no shared secret, no account) is needed —
verification is **signature-validity only** (no CA / trust-root check).

For the concept and wire format, see the design page
[Partner APIs → Authentication](../../products/g2p-bridge/design-specifications/partner-apis.md#authentication)
and [PyJWTCryptoHelper](../../platform/platform-services/privacy-and-security/pyjwtcryptohelper.md).
This page is the **operational steps**.

{% hint style="info" %}
**Certificates are public — private keys never leave the owner.** A partner keeps its
`.p12`/private key; it gives you only its **`.crt`** (public certificate, PEM). You give
partners only **your** `.crt`. See [Partner Signing Key](partner-signing-key.md) for
generating a keypair.
{% endhint %}

## The rule to remember

The receiver looks the signer up by **`PARTNER_<MNEMONIC>`**, where `<MNEMONIC>` is the
caller's **`sender_app_mnemonic`** (upper-cased) sent in the request envelope. So the
`referenceId` you register **must equal `PARTNER_` + the mnemonic the partner signs
with**, or verification fails with `rjct.jwt.invalid`.

## Onboard a partner that calls the Bridge (inbound)

A partner (bank, PSP, PBMS, …) that calls the Bridge Partner API must have its public
cert seeded into the Bridge's `partner_keys` table.

1. **Get the partner's public certificate** (PEM `-----BEGIN CERTIFICATE-----…`) and
   the **mnemonic** it will use as `sender_app_mnemonic` (e.g. `MY_PSP`).
2. **Add it to `global.g2pBridgePartnerCerts`** in your values (one entry per partner):

   ```yaml
   global:
     g2pBridgePartnerCerts:
       - referenceId: PARTNER_MY_PSP          # PARTNER_ + the sender mnemonic (upper-case)
         publicKey: |
           -----BEGIN CERTIFICATE-----
           MIID...snip...
           -----END CERTIFICATE-----
       # add more partners as additional list items
   ```
3. **`helm upgrade`.** The certs are upserted into `partner_keys` at migrate-time
   (idempotent — re-running is safe; existing entries are updated).
4. **Verify.** A signed call from that partner should succeed; the API logs
   `JWS signature verified for partner 'PARTNER_MY_PSP'`. You can also check the row:

   ```bash
   kubectl exec -n <ns> commons-postgresql-0 -- \
     psql -U postgres -d <release-underscored> \
     -c "select reference_id, status from partner_keys;"
   ```

{% hint style="warning" %}
**Enforcement.** Inbound verification is active when
`global.g2pBridgeSignatureValidationEnabled` is `true` (the default) — or whenever the
test partner is enabled. Onboard partners **before** turning it on, or their calls are
rejected.
{% endhint %}

## Register the Bridge with SPAR (outbound)

The Bridge **signs** its resolve requests to SPAR, so SPAR must trust the Bridge's
public cert. The Bridge signs as mnemonic **`g2p_bridge`**, so SPAR must hold it as
**`PARTNER_G2P_BRIDGE`**.

1. Take the Bridge's **public cert** (`g2p-bridge.crt` from
   [Partner Signing Key → Step 1](partner-signing-key.md#step-1-generate-your-own-keypair)).
2. Hand it to the **SPAR operator**, who adds it to the SPAR chart's
   `global.sparPartnerCerts` as `PARTNER_G2P_BRIDGE` and runs `helm upgrade` (see the
   SPAR **Privacy & Security** / Helm docs).

{% hint style="info" %}
The bundled **trial** does both sides automatically with the public demo cert (seeded
as `PARTNER_TEST_SANITY` / `PARTNER_TRAINING` on the Bridge and `PARTNER_G2P_BRIDGE` on
SPAR), so an out-of-the-box install verifies end-to-end with no manual onboarding.
{% endhint %}

## Rotating or removing a partner

* **Rotate:** replace that partner's `publicKey` with the new cert and `helm upgrade`
  (the entry is matched by `referenceId` and updated in place).
* **Remove:** drop the entry and `helm upgrade`. (Seed-based onboarding upserts; it does
  not delete stale rows automatically — delete the `partner_keys` row directly if you
  need immediate revocation.)

{% hint style="info" %}
Onboarding is currently **seed-based** (applied at chart install/upgrade). A runtime
admin API for partner onboarding is planned; until then, changes go through
`helm upgrade` (or a direct DB update for emergency revocation).
{% endhint %}
