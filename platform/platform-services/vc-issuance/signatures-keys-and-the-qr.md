---
description: >-
  What an issuance actually produces — two signed documents, two keys, one QR —
  which component builds each part, which signature a verifier checks, and what
  has to be true before anyone can verify anything.
---

# Signatures, Keys and the QR

The single most confusing thing about this design is that **one issuance produces
two separately signed documents**, not one document shown two ways. Almost every
question that follows — why two keys, which one a verifier checks, why the QR
needs its own signature — falls out of that one fact.

## What an issuance produces

In order, inside Inji Certify:

1. It renders the **compact claim-169 payload** from the credential's
   `qrSettings` — a small CBOR map of identity attributes.
2. It **signs that payload** as a `COSE_Sign1` / CWT, and compacts it to a
   Base45 string (the `NCF…` text).
3. It embeds that string in the credential at
   `credentialSubject.claim169.qrCode`.
4. It **signs the whole credential** with a Linked-Data `Ed25519Signature2020`
   proof.

So the QR's signature sits **inside** the bytes the credential's signature
covers. That ordering is the crux: the QR is later torn out and travels alone —
printed on paper, or shown on a wallet screen — detached from the JSON that
carried it. A signature only covers the exact bytes it was made over, so the
credential's proof says nothing about a QR presented on its own. Hence two.

## Who builds what

| Stage | Component | Detail |
|---|---|---|
| Render `qrSettings` templates | **Certify** | `VelocityTemplatingEngineImpl.formatQRData` |
| Map names → claim-169 integer keys | **Certify**, via MOSIP **pixelpass** | `Full Name`→4, `Gender`→9, `MALE`→1 |
| Sign as COSE/CWT | **Certify** | `CoseSignatureService.cwtSign` |
| Compact-encode | **Certify**, via pixelpass | CBOR → hex → zlib → **Base45** |
| Sign the credential | **Certify** | `Ed25519Signature2020` |
| Draw the QR image | **Agent Portal API** | Python `qrcode`: string → PNG → PDF |

The Agent Portal API contains **no** CBOR, COSE, CWT or Base45 code at all. It
reads the finished string out of the credential and turns it into pixels. Which
is why changing what the QR contains means editing Certify's `credential_config`
— never the Python.

The one encoding the Agent Portal API does perform is the **fallback**: when
`claim169.qrCode` is absent it gzips the entire credential and base64url-encodes
it (the `H4sIA…` form). That is verifiable in principle but roughly four times
the size and not a shape claim-169 verifiers recognise, so it means the
`qrSettings` are missing or misconfigured — treat it as a defect, not an option.

## The two signatures

| | The credential | The QR |
|---|---|---|
| What it is | full **JSON-LD VC** (~1.5 KB) | compact **CBOR** identity payload (~470 B) |
| Signature | `Ed25519Signature2020` Linked-Data proof | `COSE_Sign1` wrapped as a **CWT** (CBOR tag 61 → 18) |
| Algorithm | **EdDSA** (Ed25519) | **ES256** (ECDSA P-256) |
| Key alias | `CERTIFY_VC_SIGN_ED25519` / `ED25519_SIGN` | `CERTIFY_VC_SIGN_EC_R1` / `EC_SECP256R1_SIGN` |
| Configured by | `credentialConfig.signatureAlgo` | `credentialConfig.qrSignatureAlgo` |

### Why two keys and not one

COSE also supports EdDSA, so the credential key *could* sign both, and there is
no security objection — the two structures cannot be confused. It is
deliberately not done:

* **Compatibility.** ES256 is what the mDL / EU-DCC / claim-169 ecosystem
  actually implements. EdDSA is a registered COSE algorithm but less widely
  supported in verifier stacks — and the QR is the artefact most likely to meet
  a third-party verifier.
* **Key separation.** A compromised or rotated QR key does not disturb
  credential signing, and the QR algorithm can change without touching it.
* **Hardware.** P-256 is universally supported in secure elements and HSMs;
  Ed25519 support is patchier. Worth preserving even though Phase 1 uses a
  `.p12`.

### Which one is checked, and when

Not paper-versus-wallet — **transfer versus presentation**:

| | Credential signature (Ed25519) | QR signature (ES256) |
|---|---|---|
| Paper (Phase 1) | not used — the citizen never receives the JSON | **the only thing verified** |
| Wallet, scanned at a counter | checked when the wallet **receives** the credential | **verified at the counter** |
| Wallet, OpenID4VP to a relying party | **the one verified** | not used in that exchange |

A wallet does not hand a shopkeeper a JSON-LD document — it **displays the same
claim-169 QR on screen** and the verifier scans it. Same artefact as the paper,
same scanner, same trust anchor. The QR signature therefore serves both paths.

Note the inversion: **in Phase 1 the Ed25519 signature is the one nothing
checks**, because the JSON is never handed out. It is not wasted — it is what
makes this a W3C Verifiable Credential, it is what a wallet validates on receipt
in Phase 2, and Certify produces it as part of issuing at all.

## What the QR can carry

Claim 169 has a **fixed vocabulary**, defined by MOSIP's pixelpass mapper. Only
those attribute names are accepted:

* Identity — Version, Language, Full Name, First/Middle/Last Name, Date of
  Birth, Gender, Address, Email ID, Phone Number, Nationality, Marital Status,
  Guardian
* Photo — `Binary Image` + `Binary Image Format` (PNG / JPEG / JPEG2000 / AVIF /
  WEBP / TIFF / WSQ)
* Biometrics — fingers, iris, Face, palm, voice

Two consequences people trip over:

* **A photo is optional.** Claim 169 is a compact *signed identity payload*; the
  face image is one attribute among many, and MOSIP's own specification says
  biometrics are optional. A QR carrying only name, date of birth and gender is
  a perfectly valid claim-169 QR. OpenG2P defers the photo to Phase 2 for QR
  size reasons, not validity ones.
* **There is no slot for a programme identifier.** A registry's own id — the
  Farmer Registry's `functionalRecordId`, for instance — cannot go in the QR. It
  stays in the JSON-LD credential only.

## Where the keys are published

* `GET /.well-known/did.json` — the **DID document**, resolving
  `did:web:<certify-host>`. Carries the **Ed25519** key only. Certify builds this
  from the registered credential configs' `signatureAlgo` and never consults
  `qrSignatureAlgo`, so the QR key does not appear here.
* `GET /v1/certify/.well-known/jwks.json` — **all** of Certify's public keys, the
  ES256 QR key included. This is where a verifier obtains the QR key.

That split is not a defect, because **claim-169 verification does not resolve
DIDs.** The COSE header carries only an `alg` and a `kid` — there is no
`x5chain` embedded. A verifier is expected to already hold the issuer's key from
a **pre-distributed trust list**, exactly as EU DCC and mDL work. Publishing the
key is necessary but not sufficient: it must be **loaded into the verifier as a
trust anchor**.

## Who verifies, and with what

Two Inji products are easily confused, and only one of them verifies:

| | What it is | Role |
|---|---|---|
| **Inji Verify** | a **web portal** the verifying organisation hosts (webcam scan or upload), plus an **SDK** — a React/NPM module — for embedding the same into a relying party's own application | **verifier** |
| **Inji Wallet** | a phone app | **holder** — stores the owner's own credentials; does not verify someone else's paper |

So "the citizen scans it with an app" is the wrong picture. The **verifier**
runs the software; the citizen installs nothing in Phase 1.

This also qualifies the word *offline*. The signature check needs no call back
to OpenG2P — the verifier already holds the key. But a web portal is a web page,
so a browser-based verifier still has to load it. A genuinely disconnected
counter needs the SDK embedded in an installed application.

{% hint style="warning" %}
**Unverified.** Whether a stock Inji Verify accepts a claim-169 CWT from a
non-MOSIP issuer has not been tested end to end. Until it has, treat third-party
verification as unproven rather than assumed.
{% endhint %}

## Before anyone can verify anything

Neither of these happens on its own:

1. A **verifier deployment exists** — nothing verifies a credential until a
   relying party stands one up.
2. The OpenG2P issuer's **ES256 QR key is loaded there as a trust anchor**, taken
   from `/v1/certify/.well-known/jwks.json`.

See [Deployment](deployment.md) for the issuer side.
