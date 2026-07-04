---
description: >-
  How the Consent Manager design aligns with Kantara/ISO 27560, GDPR, DEPA /
  Account Aggregator, and DCI/OIDC — and the gaps the design deliberately closes.
---

# Standards &amp; best practices

The design is measured against four reference frameworks. This page records where we align and,
importantly, the **gaps** the design closes relative to the original prototype and notes.

## Reference frameworks

| Framework | Why it applies |
| --- | --- |
| **Kantara Consent Receipt v1.1 / ISO/IEC 29184 &amp; 27560** | Canonical, portable consent-record/receipt structure. |
| **GDPR** | Lawful basis, purpose limitation, minimisation, and data-subject rights. |
| **DEPA / Account Aggregator** | Granular, revocable, time-bound data-sharing consent artefacts with fetch semantics. |
| **DCI + OAuth2 / OIDC** | Interoperable consent payloads and ID-token-based authentication context. |

## Alignment &amp; gaps closed

Each row is a best practice, our position, and — where it was missing in the prototype/notes —
the **gap we add**.

### Kantara / ISO 27560 — consent receipts

* **Best practice:** a receipt is a complete, human-readable consent record: controller identity
  &amp; contact, DPO, purposes with legal basis, data categories, retention, third parties,
  withdrawal method, sensitivity, jurisdiction, version — plus a cryptographic proof.
* **Gap closed:** the prototype's receipt held only a hash + signature. The
  [Consent Receipt](data-model.md#consent-receipt-kantara-iso-27560) now carries the full record
  set, signed with an asymmetric key.

### GDPR — data-subject rights

* **Best practice:** subjects can be informed, access their consents, withdraw at any time, and be
  notified of changes; every consent records a **lawful basis** and a purpose.
* **Gaps closed:**
  * **Right of access** — [`GET /my/consents`](../api/subject-api.md) and `GET /my/receipts/{id}`.
  * **Right to withdraw** — `POST /my/consents/{id}/revoke`, with propagation.
  * **Right to be informed** — purpose, retention, and recipients are on every receipt.
  * **Notification** — grant / revoke / expiry events notify the subject and partner.
  * **Lawful basis** — recorded per purpose on the receipt.

### DEPA / Account Aggregator — artefact semantics

* **Best practice:** consent is granular, time-bound, revocable, and carries **fetch semantics** —
  one-shot vs periodic, frequency, and post-fetch data life — with revocation notified to all
  parties.
* **Gaps closed:**
  * `fetch_type` (`oneshot` / `periodic`), `max_fetch_frequency`, and `data_life` on the
    [policy](partner-onboarding-and-policy.md#policy-model) and artefact.
  * A **purpose-code taxonomy** asserted in the object and capped by policy.
  * **Consent templates** for standardised, comparable consents.
  * **Revocation notification** to all parties + a live status endpoint.

### DCI / OIDC — interoperability &amp; auth context

* **Best practice:** accept interoperable, signed consent payloads; build an auth context from a
  **validated** ID token (signature + claims), with JWKS-based key rotation.
* **Gaps closed:**
  * The primary flow accepts a **partner-signed, DCI-style embedded object** as a compact JWS (RFC 7515), verified via the shared `CryptoHelper` against Partner-Management keys.
  * ID-token validation is real (JWKS, `iss`/`aud`/`exp`/`auth_time`/`amr`), replacing the
    prototype's HS256 shortcut. See [Security &amp; trust](security-and-trust.md#id-token-validation-origination).

## Cross-cutting gaps closed

Beyond the four frameworks, the design adds:

| Gap | Resolution |
| --- | --- |
| Symmetric (HS256) signing with a shared secret | **Asymmetric** signing throughout. Partner consent objects are verified with **public keys sourced from Partner Management** (fetched by `partner_mgmt_id` + `kid`, verified locally — the CM keeps no partner-key store); CM **receipts** are signed with the CM's own `.p12` key (EdDSA/ES256/RS256) and published at `/.well-known/jwks.json` |
| No partner / policy concept | First-class **partner policy binding + versioned data-share policy engine** (identity/keys in PM; widening gated by AWE approval) |
| Registry would interpret consent | Strict **PDP/PEP** split; CM returns effective fields |
| No non-repudiation | **Append-only signed decision log** + signed receipts |
| Revocation not propagated | **Status endpoint (OCSP-like) + webhooks** |
| No replay protection | **`jti` + freshness window** |
| Policies/templates unversioned | **Versioned** policies; decisions record the version |
| Mutable state, lost history | **Append-only** transitions; timestamps never overwritten |

## Conformance summary

| Capability | Status |
| --- | --- |
| Partner-signed consent verification (known party) | ✅ Designed |
| Policy ceiling &amp; effective-scope intersection | ✅ Designed |
| Kantara/ISO-27560 receipt | ✅ Designed |
| GDPR access / withdraw / inform / notify | ✅ Designed |
| DEPA fetch semantics &amp; revocation propagation | ✅ Designed |
| DCI embedded payload + OIDC auth context | ✅ Designed |
| Asymmetric signing + JWKS + rotation | ✅ Designed |
| Append-only audit / non-repudiation | ✅ Designed |

> "Designed" means specified in this section and reflected in the [API contract](../api/README.md).
> Implementation tracking will live in the development/release pages once build begins.
