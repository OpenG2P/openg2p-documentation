---
description: >-
  Phase 1 — agent-assisted issuance of a signed, printable credential (PDF with
  an offline-verifiable QR) from OpenG2P Registry data, gated by the
  beneficiary's own eSignet authentication and verified with Inji Verify.
---

# Phase 1 — Paper Credential

The lowest-common-denominator path: a citizen who owns **no device** receives a **printed credential**
with an **offline-verifiable QR**, and a verifier validates it by scanning that QR. Wallets, Mimoto and
OpenID4VCI redirect flows are **out of scope** for Phase 1.

"Owns no device" refers to **holding** the credential. Issuance itself is **always gated by the
beneficiary authenticating digitally** through eSignet — by **biometric at the agent's counter** (which
requires nothing of the citizen) or by **OTP** to their phone.

## Actors

| Actor | Role |
|-------|------|
| **Citizen (beneficiary)** | Receives and carries a **printed** credential. Authenticates once, in person, via **eSignet** to authorise the issuance. Holds nothing digital afterwards. |
| **Agent** | Field/kiosk operator who performs the issuance. Logs in to the Agent Portal with **Keycloak in the `agent` realm**. Distinct from registry **staff** — different realm, different API, different portal. |
| **Agent Portal API** | The issuance backend: resolves the citizen in the Registry, drives the beneficiary's eSignet authentication, **pushes** claims into Certify, renders the PDF and records the issuance. |
| **eSignet** | Authenticates the **beneficiary** against the foundational ID system (biometric or OTP). Issues no credential; it only proves who is standing at the counter. |
| **Inji Certify** | Issues + **signs** the VC and produces the **signed QR** payload. **Not connected to the Registry.** |
| **OpenG2P Registry** | Source of claim data and of the record's identity/status; read **only by the Agent Portal API**. |
| **Verifier** | A relying party (bank, ration shop, department) who **scans the QR** with **Inji Verify**. |

## Issuance flow

```
 Agent            Agent Portal API        Registry         eSignet         Inji Certify
   │ 1. login (Keycloak, `agent` realm)      │               │                  │
   │ ───────────────────►│                   │               │                  │
   │ 2. enter/scan the beneficiary's national ID              │                  │
   │ ───────────────────►│                   │               │                  │
   │                     │ 3. foundational_id exists?         │                  │
   │                     │    record_status == ACTIVE?        │                  │
   │                     │ ─────────────────►│               │                  │
   │                     │ ◄── internal_record_id ────────────│                  │
   │                     │ 4. initiate registrant authentication                 │
   │                     │ ──────────────────────────────────►│                  │
   │ ◄── authorization_url ──────────────────────────────────  │                  │
   │ 5. beneficiary authenticates (biometric at the counter, or OTP)             │
   │ ═══════════════════════════════════════════════════════►│                  │
   │                     │ 6. callback → authentication SUCCESS                │
   │                     │ ◄──────────────────────────────────│                  │
   │                     │ 7. bind: individual_id == foundational_id             │
   │                     │    window: now − completed_at ≤ 5 min                 │
   │                     │ 8. read claims by internal_record_id                  │
   │                     │ ─────────────────►│               │                  │
   │                     │ 9. PUSH claims (pre-authorized-code)                  │
   │                     │ ─────────────────────────────────────────────────────►│
   │                     │                   │               │  build from template,
   │                     │                   │               │  sign (.p12 Ed25519)
   │                     │ ◄────────────── signed VC ─────────────────────────────│
   │                     │ 10. render PDF (credential + QR); log the issuance     │
   │ ◄── PDF download ───│                   │               │                  │
   │ 11. print and hand the paper credential to the citizen                      │
```

### What each step guarantees

* **The beneficiary must exist in the Registry.** The entry point is the citizen's **national ID**,
  matched against the register's **`foundational_id`** (unique and indexed). No record, no credential.
  A record whose `record_status` is not **`ACTIVE`** is refused. `foundational_id` is **required** for
  VC issuance — a record ingested without one cannot be issued a credential.
* **Digital authentication is mandatory.** The beneficiary authenticates *themselves* through eSignet.
  Whether that is a **biometric** capture at the counter or an **OTP** to their phone is determined by
  what the deployment has configured — eSignet's own UI handles capture, including the biometric device.
* **The authentication is bound to the record.** The subject returned by eSignet (`individual_id`) is
  checked against the `foundational_id` of the record being issued. Without this check an agent could
  pair one person's authentication with another person's record.
* **The authorisation is short-lived.** Issuance proceeds only while the authentication is
  `SUCCESS` **and** within the configured VC window (default **5 minutes**) measured from
  `completed_at`. The window is **VC configuration**, deliberately independent of any expiry the
  authentication record carries for other consumers.
* **Issuance is keyed on `internal_record_id`**, not on a value the agent typed. The national ID only
  *finds* the record; the authenticated record identity is what the credential is built from.
* **The Agent Portal API owns the Registry lookup.** It reads the claims and **pushes** them into
  Certify; Certify never connects to the Registry, keeping the issuer decoupled from registry data.
* **Server-side issuance.** The backend drives Certify directly (a trusted machine-to-machine call)
  via the OpenID4VCI **pre-authorized-code** grant; there is no device holder key — the credential is a
  **bearer document** whose trust comes from the **issuer's signature**.
* **Every issuance is recorded.** The Registry keeps an issuance **event log** — which record, which
  credential id, which authentication, which agent, when. It stores a *reference*, never a copy of the
  credential or its claims.
* **The agent downloads the PDF.** It is streamed to the agent's browser, printed on whatever printer
  the counter has, and handed over.
* **Re-issue on demand.** A lost or stale credential is simply **re-issued** — a fresh authentication,
  a new credential, linked to the previous one in the issuance log.

## Presentation & verification

```
 Citizen ──(hands paper)──► Verifier ──(scans/uploads QR)──► checks COSE signature
                                                              against a PRE-LOADED
                                                              trust anchor  → ✅/❌
```

**What "offline" does and does not mean here.** The *signature check* needs no
call back to OpenG2P: the verifier holds the issuer key already. But **Inji
Verify is a web portal**, not a phone app — the verifying organisation hosts it
and a verifier uses it in a browser, by webcam or by uploading a photo of the
paper. A browser still has to load that page. A genuinely disconnected counter
needs Inji Verify's **SDK** (a React/NPM module) embedded in an installed
application. Inji **Wallet** is the phone app, and it is a *holder* app: it
stores the owner's own credentials and does not verify someone else's paper.

**Before any of this works, two things must be true**, and neither happens on
its own:

1. a verifier deployment exists (nothing verifies a credential until a relying
   party stands one up); and
2. the OpenG2P issuer's **ES256 QR key is loaded there as a trust anchor** —
   take it from `/v1/certify/.well-known/jwks.json`.

> **Unverified.** Whether a stock Inji Verify accepts a claim-169 CWT from a
> non-MOSIP issuer has not been tested end to end. Until it has, treat
> third-party verification as unproven rather than assumed.

* **The QR is the credential.** A full JSON-LD VC is far too large for a QR, so the QR carries a
  **compact, signed payload** — MOSIP's **"claim 169"** identity QR (CBOR), the CWT/mDoc family used
  by mDL / COVID certificates. Inji Certify supports this **natively** (no plugin) via the
  `credential_config` columns **`qr_settings` + `qr_signature_algo`**: each `qr_settings` entry is a
  Velocity template; Certify renders it, encodes it with the **pixel-pass** library, **signs it as a
  COSE/CWT** (`CoseSignatureService.cwtSign`), and **base45**-encodes the result into the VC under a
  `claim169` field.
* **Where the verifying key comes from.** The signed QR is a **COSE_Sign1 / CWT**, and claim-169
  verification **does not** use `.well-known` / JWKS / DID discovery. The spec allows the key to be
  identified from the COSE header — `x5chain` (embedded cert), `x5t` (hash) or `x5u` (URI) — otherwise
  the verifier is assumed to hold a **pre-loaded trust anchor**.
  **What OpenG2P actually emits carries no certificate**: the header holds only `alg` (ES256) and a
  `kid`. So a pre-distributed trust anchor is the *only* way our QR verifies — take the ES256 key from
  `/v1/certify/.well-known/jwks.json` and load it into the verifier. Either way, no call back to
  OpenG2P at scan time. (The **JSON-LD VC** — not the QR — uses
  `proof.verificationMethod = <issuerDID>#<key>`, resolvable via `did:web`.) See
  [Signatures, Keys and the QR](signatures-keys-and-the-qr.md).

{% hint style="info" %}
**Photograph in the QR is deferred to Phase 2.** A QR is hard-capped at **~2.9 KB**, but claim 169 can
carry a **low-resolution face thumbnail** by combining a modern codec (attribute 62 allows
**WEBP / AVIF / JPEG / PNG / WSQ** — WEBP/AVIF give a recognisable face in **~1–2 KB**),
**integer-keyed CBOR**, **zlib/Brotli** compression and **Base45** packing. It is recognition-grade,
not high-resolution — the same approach as Aadhaar's Secure QR. When adopted, the photo will be
solicited as part of the **eSignet KYC response** (the ID system's own photograph, matching what the
beneficiary was authenticated against) and pushed to Certify as the `face` claim; Certify never fetches
images. See [Phase 2 — Device Wallet](phase-2-device-wallet.md).
{% endhint %}

## Architecture & components (Phase 1)

```
 Agent ──login (Keycloak `agent` realm)──► iam-agent-portal-api

 Agent Portal API ──reads──► OpenG2P Registry (foundational_id → internal_record_id, claims view)
 (agent-driven)    │
                   ├─initiate──► eSignet  (beneficiary: biometric / OTP)
                   │
                   └─push claims──► Inji Certify
                                      ├─ PreAuthDataProviderPlugin (built-in) → pushed claims = VC subject
                                      ├─ Velocity template  → VC body
                                      ├─ keymanager + .p12   → Ed25519 signature
                                      └─ (signed VC) ──► Agent Portal API → PDF + QR (downloaded)

 Verifier (separate):   Inji Verify ── scans QR ── validates vs issuer trust anchor (offline)
```

* **Agent Portal API** — the issuance backend, part of the **Registry Platform** so every registry
  manifestation inherits it. Ships **disabled by default** and is switched on per deployment.
* **Agent authentication** — `iam-agent-portal-api` (IAM service) against the Keycloak **`agent`**
  realm. Issuance itself is permission-gated on the Agent Portal API.
* **Beneficiary authentication** — the Registry's **registrant-authentication** subsystem with an
  **eSignet** provider. The same subsystem staff already use; the VC flow adds its own time window.
* **Inji Certify** — the issuer (used **stock**, no custom plugin). Builds the VC from a Velocity
  template and signs with its **embedded keymanager (PKCS12 `.p12`, no HSM)**. Certify's built-in
  **`PreAuthDataProviderPlugin`** makes the **pushed claims the credential subject** — so Certify needs
  **no Registry access**. (A custom pull connector exists for the wallet flow; see
  [Registry Data Connector](registry-data-connector.md).)
* **Agent web portal** — a thin reference client proving the chain, following OpenG2P UI conventions.
* **Inji Verify** — the verifier side. NOT a phone app: it is a **web portal** the
  verifying organisation deploys (scan by webcam, or upload a photo/scan of the
  paper), plus an **SDK** (a React/NPM module) for embedding the same
  scan-and-verify into a relying party's own application. The citizen installs
  nothing; the *verifier* runs it. Inji **Wallet** is the phone app, and it is a
  holder app — it stores your own credentials, it does not verify someone
  else's paper.

## What a registry manifestation must supply

The Registry Platform owns the service, the chart and the contract. Each manifestation (NSR, Farmer
Registry, …) supplies what is specific to it, because the fields differ:

* the **VC view** exposing the claim columns, keyed on `internal_record_id`;
* its **VC definitions** — credential type, template, fields, scope;
* the **card design** for the printed PDF;
* the **issuer DID** value for the environment.

### Why a view, and not the tables

The Agent Portal API is part of the **platform**, not of any one registry. It
cannot know that a farmer's land parcels live in one table and a household's
members in another — those tables are declared by the manifestation's extension,
and `G2PRegister` itself is abstract. A view is what lets one platform service
serve every manifestation without importing any of their models.

It also does three things a direct table read would not:

* **flattens** whatever joins the claims need into one row per record, so the
  service never has to know the shape underneath;
* **filters** — the view exposes only the columns that may become claims, so a
  column added to a register does not silently become a credential field;
* **keys** the record consistently on `internal_record_id`, whatever the
  manifestation's own primary keys look like.

### The view contract

Five column names are **reserved**. What becomes a **claim** depends on whether
the VC definition sets `claim_columns`:

| Column | Required | Meaning |
|---|---|---|
| `internal_record_id` | yes | the record key; what claims are fetched by |
| `foundational_id` | yes | the national ID; what the beneficiary's authenticated subject is checked against |
| `record_status` | should | only `ACTIVE` records may be issued a credential |
| `record_name` | optional | shown to the agent after look-up, so they can confirm the right person |
| `register_id` | optional | recorded on the issuance log |

**With `claim_columns` set** (what the Farmer Registry does), only those columns
are stamped into the credential — a column added to the view is *not* issued
unless the definition asks for it by name, and a configured column that the view
does not expose is a hard error at issue time rather than a silently missing
field.

**Without it**, every non-reserved column becomes a claim, and the view alone is
the claim list.

The explicit list is the safer default: it means widening a view for reporting
cannot quietly widen what is printed on a citizen's credential.

### How a column becomes a credential field

The column name is the link. The credential template refers to variables as
`${...}`, and the view's column names must match them:

```sql
-- farmer_vc_view
select f.internal_record_id,
       f.foundational_id,
       f.record_status,
       concat_ws(' ', f.given_name, f.family_name) as "fullName",   -- ${fullName}
       to_char(f.birth_date, 'YYYY-MM-DD')         as "dateOfBirth" -- ${dateOfBirth}
from   g2p_register_farmers f;
```

Two details bite in Postgres: camelCase aliases must be **double-quoted** or
they fold to lowercase and stop matching `${fullName}`; and dates should be
rendered to text, so the claim is a clean string rather than a serialised date
object. The API stringifies any non-string value before pushing it, so an
un-cast date still issues — it just issues Python's rendering of it.

If a template variable has no matching column, Certify returns the credential
with the literal `${...}` still in it. The Agent Portal API **rejects** such a
credential rather than printing it — an unresolved placeholder on a citizen's
paper credential is worse than a failed issuance.

### Who reads it, and when

Only the **Agent Portal API**, twice in one issuance:

1. at **look-up**, by `foundational_id`, to find the record and confirm it is
   `ACTIVE`;
2. at **issue**, by `internal_record_id`, to read the claims that are pushed to
   Certify.

Inji Certify never reads it. In Phase 1 claims are *pushed* to Certify, so
Certify holds no database credentials and needs no access to the registry at
all. (Certify's own `registrydb` data-provider plugin — which would read a view
directly — is a different, wallet-oriented path; see
[Registry Data Connector](registry-data-connector.md).)

## Where the credential template lives

The template is part of the manifestation's **VC definition**, in its Helm
values — not in code and not in the database:

```yaml
agentPortalApi:
  vcDefinitions:
    - config_id: OpenG2PFarmerCredential
      view: farmer_vc_view                    # where the claims come from
      claim_columns: ["fullName", ...]        # which columns are issued
      svg_template: farmer-card.svg           # how the paper card looks
      certifyConfig:
        credentialConfigKeyId: OpenG2PFarmerCredential
        vcTemplateJson: ...                   # the JSON-LD credential template
```

It is authored as readable JSON (`vcTemplateJson`) and **base64-encoded by the
`credential-config-register` Job**, which POSTs each definition to Certify on
install and upgrade. Certify can only issue a credential type it already knows,
so a type that was never registered fails at the first issuance on an unknown
`credential_configuration_id`.

Certify is what substitutes the `${...}` variables, using the claims the Agent
Portal API pushed.

## Where the PDF is made

In the **Agent Portal API**, not in Certify and not in the browser.

Certify returns a signed JSON-LD credential with the compact claim-169 QR
payload inside it. The API then renders the printable card itself, with
`cairosvg`, from the manifestation's **SVG card design** — shipped as a
ConfigMap and mounted at `/app/pdf-templates`, so a designer can restyle the
card without touching code or rebuilding an image. If no SVG is configured the
API falls back to a plain layout, so a missing design file never blocks an
issuance.

The PDF is **streamed straight to the agent's browser** as a download and is
never written to the pod, so any replica can serve any request. The issuance
identifiers travel in response headers (`X-Issuance-Id`, `X-Credential-Id`) for
the client to display or log.

## The portal the agent uses

This page is the *credential* design. The portal itself — its own Keycloak
`agent` realm, why agents are not staff, how the browser is authenticated
without ever holding a token, and how the portal grows beyond issuance — is
documented with the Registry Platform:

→ [Agent Portal](../../../products/registry/registry/features/agent-portal.md)

## Master Data Service

**VC issuance does not use MDS at run time.** The Agent Portal API holds no
Master Data configuration at all: claims come from the registry's own VC view,
and nothing in the look-up → authenticate → issue path calls MDS.

MDS is involved before and after, not during:

* **at seed time**, a registry's `db-seed` reads geography and country code
  lists from the MDS API to populate its own attribute tables;
* **in reporting**, dashboards join registry data to geography held in Master
  Data.

So a Master Data outage does not stop credentials being issued.

## Two documents, two signatures, two keys

An issuance produces **two separately signed documents**, not one shown two ways:
the **JSON-LD credential** (Ed25519 proof) and, embedded inside it, the **compact
claim-169 QR** (COSE/CWT, ES256). The QR is later torn out and travels alone — on
paper, or on a wallet screen — so it must carry its own signature; the
credential's proof covers different bytes and says nothing about it.

On paper, **the QR signature is the only one anyone checks**. A verifier must
already hold the issuer's ES256 key as a trust anchor: claim-169 verification
does not resolve DIDs.

→ [Signatures, Keys and the QR](signatures-keys-and-the-qr.md) explains all of
this properly: who builds which part, which signature is checked on which path,
what claim 169 can and cannot carry (the photo is optional; a programme id will
not fit), where each key is published, and why Inji **Verify** is a hosted web
portal rather than the phone app.

## Key management

Certify signs with its embedded keymanager backed by a **`.p12` keystore** (no HSM). The `.p12` and
the encrypted key rows **are the issuer identity** — they must be **persisted and backed up**, and the
issuer's **public key / DID must be published at a stable, resolvable URL** so verifiers can validate
offline. By default the Certify chart **generates `local.p12` on first boot onto a durable PVC**; to
redeploy with an existing identity, restore it from a Secret (`p12.existingSecret`). See
[Deployment](deployment.md) for the custody modes.

## Deliberately out of scope for Phase 1

| Deferred | Why |
|----------|-----|
| **Photograph in the QR** (claim 169 `face`) | Sequenced after the core chain; needs the eSignet KYC photo and a hard QR size budget. |
| **Revocation / status lists** | Paper is verified **offline**, so a status list cannot be checked at scan time. Short credential validity is the compensating control for now. Certify already ships the status-list tables for when this is taken up. |
| **Android agent app** | The web portal comes first; the app follows against the identical API, adding Bluetooth printing for roaming agents. |
| **Non-digital fallback** | Issuance always requires eSignet authentication. A beneficiary with neither a phone nor an available biometric device cannot be issued a credential. |

## Status

**Proven end to end:** claims are read from a real registrant, pushed to Certify, Certify returns an
**Ed25519-signed** `OpenG2PBeneficiaryCredential`, and a **printable PDF with a QR** is rendered (see
[Local Developer Trial](local-setup.md)).

**In progress:** eSignet beneficiary authentication as a
mandatory gate, issuance keyed on `internal_record_id`, the issuance event log, and the reference agent
portal. Then: switch the QR to Certify's **compact signed** form (`qr_settings` + `qr_signature_algo`)
and confirm **Inji Verify validates it offline** against the issuer's trust anchor.
