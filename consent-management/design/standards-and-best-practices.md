---
description: >-
  How the Consent Manager aligns with Kantara / ISO 27560, GDPR, DEPA /
  Account Aggregator and DCI / OIDC, and what is built against each.
---

# Standards &amp; best practices

The design is measured against four reference frameworks.

| Framework | Why it applies |
| --- | --- |
| **Kantara Consent Receipt v1.1 / ISO/IEC 29184 &amp; 27560** | A portable consent record and receipt. |
| **GDPR** | Lawful basis, purpose limitation, minimisation, data-subject rights. |
| **DEPA / Account Aggregator** | Granular, revocable, time-bound consent artefacts with fetch semantics. |
| **DCI + OAuth2 / OIDC** | Interoperable consent payloads; an authentication context from a validated ID token. |

## Kantara / ISO 27560: consent receipts

* **Best practice:** a receipt is a complete consent record (controller and contact, DPO, purposes with legal basis, data categories, retention, third parties, withdrawal method, jurisdiction, version) with a cryptographic proof.
* **Built:** every consent has a [receipt](data-model.md#consent-receipt-kantara-iso-27560) signed with the CM's asymmetric key: controllers, purposes with legal basis, data categories, third parties, withdrawal method, version, and the artefact hash.
* **Not yet:** the controller's name, contact and DPO, retention and jurisdiction.
* **Not to be confused with the consent token**, a short-lived JWS for one registry and query ([Exchange consent tokens](exchange-consent-tokens.md)), closer to an OAuth 2.0 token-exchange token (RFC 8693) than to a receipt.

## GDPR: data-subject rights

* **Best practice:** subjects can access their consents, withdraw at any time, and be informed; every consent records a lawful basis and a purpose.
* **Built:** access ([`GET /my/consents`](../api/subject-api.md), `GET /my/receipts/{id}`) and withdrawal (`POST /my/consents/{id}/revoke`), on the beneficiary API (off by default); purpose, recipients and lawful basis on every receipt; purpose limitation and minimisation at every decision.
* **Not yet:** notifying the subject of grants, revocations and expiry.

## DEPA / Account Aggregator: artefact semantics

* **Best practice:** consent is granular, time-bound and revocable, with fetch semantics (one-shot or periodic, frequency, data life).
* **Built:** a grant per data controller; validity bounded by policy; revocation per artefact with a status endpoint; `fetch_type`, `max_fetch_frequency` and `data_life` on the partner's [access policy](../../platform/platform-services/partner-management/functional-specifications.md#access-policies), `fetch_type` also on the artefact; purpose codes capped by policy.
* **Not yet:** enforcing fetch frequency and data life; notifying all parties of a revocation.

## DCI / OIDC: interoperability and authentication context

* **Best practice:** accept interoperable, signed consent payloads; build an authentication context from a validated ID token, with JWKS-based key rotation.
* **Built:** a partner-signed consent as a compact JWS in the DCI `authorize` block, verified against Partner Management keys (from partners whose policy allows it); consents collected through the CM used by ID or found by lookup; ID tokens checked against the provider's JWKS ([Security & trust](security-and-trust.md#id-token-validation-origination)).

## Cross-cutting

| Concern | How it is met |
| --- | --- |
| Signing | Asymmetric only: partner consents verified with keys from Partner Management; receipts and tokens signed with the CM's `.p12` key (EdDSA / ES256 / RS256) and published at `/.well-known/jwks.json` |
| Partner agreement | Versioned access policies in Partner Management, changed by approval there, applied on every decision; decisions record the policy version |
| Separation of duties | PDP/PEP: the CM decides, the registry enforces |
| Non-repudiation | Signed receipts and an append-only decision log |
| Replay | `jti` + freshness window |
| History | Status changes only add; timestamps are never overwritten |
