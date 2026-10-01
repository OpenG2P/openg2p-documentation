---
description: >-
  TODO: move issued credentials from W3C VC Data Model 1.1 to 2.0. Not started.
  An implementation brief covering what to change, what to keep, and what to test.
layout:
  width: default
  title:
    visible: true
  description:
    visible: true
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
  metadata:
    visible: true
  tags:
    visible: true
---

# Supporting VC 2.0 (TODO)

> **Status: TODO. Nothing here is built.** Credentials are issued today as
> [W3C VC Data Model 1.1](https://www.w3.org/TR/vc-data-model/) with an
> `Ed25519Signature2020` proof. This page is the brief for moving to
> [VC Data Model 2.0](https://www.w3.org/TR/vc-data-model-2.0/). The findings
> were checked against source code in September 2026. Check them again before
> starting, because the MOSIP components change quickly.

## Summary

Moving to VC 2.0 is **configuration, not code**, in Certify. But it is more
than editing the credential template: the agent portal API must send the
matching context, and every consumer of the credential must accept the result.

The main constraint is on the verifier side. **Inji Verify accepts the VC 2.0
data model, but not the VC 2.0 proof type (`DataIntegrityProof` with
`eddsa-rdfc-2022`).** So the version that works with the current stack is
**VC 2.0 data model with the existing `Ed25519Signature2020` proof**.

## What each component supports

| Component | Version checked | VC 2.0 data model | `eddsa-rdfc-2022` proof |
|---|---|---|---|
| Inji Certify (signing) | as deployed | Yes | Yes. Listed with `EdDSA` in `certify-base.properties` |
| Inji Verify (`verify-service`) | 0.18.2 → `vc-verifier` 1.8.1 | Yes. `LdpValidator` has a `DATA_MODEL_2_0` branch and checks `validFrom` / `validUntil` | **No.** `ValidationHelper` rejects any proof type outside its allowed list |
| `vc-verifier` latest | 1.9.0 | Yes | **No** |
| Inji Wallet | not checked | **To check** | **To check** |

Proof types `vc-verifier` accepts (`CredentialValidatorConstants.PROOF_TYPES_SUPPORTED`):
`RsaSignature2018`, `Ed25519Signature2018`, `Ed25519Signature2020`,
`EcdsaSecp256k1Signature2019`, `EcdsaSecp256r1Signature2019`.

## Changes to make

All of these must ship together. If they disagree, issuance fails.

### `farmer-registry`: `helm/openg2p-farmer-registry/values.yaml`

1. **`vcTemplateJson`**
   * `@context`: replace `https://www.w3.org/2018/credentials/v1` with
     `https://www.w3.org/ns/credentials/v2`.
   * **Keep** `https://w3id.org/security/suites/ed25519-2020/v1`. It defines
     the `Ed25519Signature2020` proof type, which we still use.
   * Keep the inline term block (`OpenG2PFarmerCredential`, `functionalRecordId`, …).
   * Rename `issuanceDate` to `validFrom` and `expirationDate` to `validUntil`.
     The values stay `${validFrom}` and `${validUntil}`, which Certify fills in.
2. **`certifyConfig.contextURLs`**: change to the v2 URL. Certify publishes this
   in its issuer metadata and checks credential requests against it.

Other registries built on the Registry Platform need the same two edits in
their own VC definitions.

### `registry-platform`

3. **Agent portal API `certify_credential_context`** (`config.py`, default v1).
   Paper issuance sends this as `credential_definition.@context` in the
   credential request. If it doesn't match the config's context, Certify
   rejects the request and paper issuance stops working. It is better to
   remove the separate setting and read the context from the VC definition's
   `contextURLs`, so there's only one place to change.
4. **Staff UI `VpVerificationModal.tsx`** lists the proof types it accepts in
   presentations. Nothing to do while we keep `Ed25519Signature2020`. Add
   `DataIntegrityProof` there if the proof type ever changes.

### Do **not** change (yet)

* **`global.vcIssuer.signatureCryptoSuite`** stays `Ed25519Signature2020`.
  Certify can sign `eddsa-rdfc-2022`, but Inji Verify can't check it. Only move
  once `vc-verifier` supports it. This setting is global: every credential type
  in the registry changes at once.

## Not affected

* **The printed QR.** It is a claim-169 CWT signed with ES256 and is separate
  from the VC data model. Paper verification at the agent portal is unchanged.
* **Signing keys, the issuer DID, and `did.json`.** The same Ed25519 key signs.
* **Credentials already issued.** Existing 1.1 credentials stay valid. But the
  Certify config is keyed by its ID (`OpenG2PFarmerCredential`) and is
  overwritten on upgrade, so everything issued afterwards is 2.0. To issue
  both versions at once, register the 2.0 template under a **new** config ID.

## Risk to test first

The v2 context marks its terms as protected. Loading the older
`ed25519-2020/v1` context next to it could cause a "protected term
redefinition" error when the credential is signed or verified. We haven't
seen this happen, but haven't ruled it out either. Before rolling out:

1. Issue one credential with the new template, through both paper issuance and
   the wallet offer.
2. Check it through `verify-service` and confirm `SUCCESS`.
3. Tamper with one claim and confirm `INVALID`.
4. Confirm Certify can load the v2 context when signing. It already fetches the
   v1 context.

## Still open

* **Inji Wallet**: confirm it accepts, stores and displays a VC 2.0
  credential with an `Ed25519Signature2020` proof, received through a
  credential offer. Wallet handover is the main reason for this move, so check
  this first.
* **When to adopt `eddsa-rdfc-2022`**: watch
  [`inji/vc-verifier`](https://github.com/inji/vc-verifier) for
  `DataIntegrityProof` support, then change `signatureCryptoSuite` and the
  staff UI list.
* **Documentation**: the VC pages say "VC Data Model 1.1" throughout
  ([Phase 1](phase-1-paper-credential.md),
  [Signatures, Keys and the QR](signatures-keys-and-the-qr.md),
  [Verification](verification.md)). Update them when this ships.
