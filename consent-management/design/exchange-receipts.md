---
description: >-
  Agri Stack Exchange — one Consent Manager codebase in two roles: the Exchange
  CM issues signed consent tokens (checking the partner's policy for the use case), a
  department CM accepts them from a trusted issuer and applies the Composite's
  scope policy in its own Partner Management. Opt-in, off by default.
---

# Exchange consent tokens (Agri Stack Exchange)

In [Agri Stack across departments](../../open-agri-stack/architecture/README.md#across-departments)
a partner (e.g. a bank) onboards and the farmer consents **only at the Exchange** (the data exchange layer, `agrix`), while
each department registry (`trial`, `dept1`) still decides at its own boundary through its own Consent
Manager. The link between the two is a **consent token** (called *receipt* in the API and settings):
a short-lived JWS the Exchange CM signs for one registry and one query, which the department CM
verifies and evaluates against the policy its own Partner Management holds for the Composite. It is not the long-lived
[consent receipt](data-model.md#consent-receipt-kantara-iso-27560) document (Kantara / ISO 27560)
the CM keeps as the record of a consent (all four terms side by side: [key terms](README.md#key-terms)).

Everything here is **opt-in and off by default**. With the settings empty — every standalone
install — no new code path runs, `/validate` behaves exactly as before, and the Helm chart renders
the same manifests. API changes are additive only (optional request fields, an optional response
field, a new status endpoint, new reason codes).

## Why a consent token

The partner's consent and its access policy are held at the Exchange, but each department must decide for itself what leaves its registry. Without a token there are three ways to connect them, and each falls short:

| Option | Problem |
| --- | --- |
| **Pass the partner's whole consent to every registry** | Each department must hold the partner as its own partner (key and policy in its Partner Management), so the partner onboards at every department. Each registry also sees the whole consent, including grants for other departments' data. |
| **Let each registry ask the Exchange CM per request** | Every department depends on the Exchange's live answer, and keeps nothing signed as proof of why it released the data. |
| **Trust the Composite, capped by the ceiling** | See below. |

**Why trusting the Composite and the ceiling is not enough.** A department could release data to any Composite request, up to its ceiling, with no token. It would lose four things:

1. **Proof per farmer.** With a token, the registry releases a farmer's data only on a statement signed by the Exchange CM (another service, another key) naming that farmer, that registry and those scopes. Without it, a bug, a misconfiguration or a compromise of the Composite alone could read every farmer's data up to the ceiling; with tokens, the Composite and the Exchange CM would both have to fail.
2. **Data minimisation.** The ceiling is the superset of every use case. The token narrows each request to what this farmer consented to for this use case (a declined item is left out). Without it the registry releases everything the ceiling allows and the Composite discards the rest: more personal data leaves the department than the purpose needs.
3. **The department's accountability.** The department is the data controller for its registry. With tokens, each release is recorded in its own Consent Manager and audit against a consent ID and token ID, so it can show the legal basis for every disclosure. Without them it can show only that the Composite asked.
4. **Binding to the subject.** The token names the farmer, so a consent for one farmer cannot be used to fetch another. Without it, nothing at the registry checks this.

Tokens cost almost nothing extra: the Composite calls the Exchange CM to check the consent anyway, the tokens are issued in that same call, and departments verify them offline with a cached key.

A consent token avoids both. The Exchange CM checks the partner's policy and the subject's consent once, then signs a short note for **one** registry and **one** query, with only the scopes allowed there. The registry's own CM verifies the signature, checks the token is addressed to it, presented by the named caller (the Composite) and not expired, and applies the **ceiling** its department set for the Composite. So:

* each department stays sovereign and sees only what concerns it;
* the partner onboards once, at the Exchange;
* a token is useless to anyone else and expires within minutes (default 5); once the consent is revoked the Exchange issues no new token, and those already issued lapse within that time;
* the registry keeps a signed record of why it released the data.

**The trade-off: no live revocation check.** A department checks a token offline and never asks the Exchange whether the consent is still in force. If the farmer revokes a consent, a token issued just before stays usable until it expires: up to the token lifetime (default 5 minutes, never past the consent's own expiry), and only by the Composite, for the one registry and query it was issued for. In exchange, no department depends on the Exchange being up, and no request waits on a call to another organisation. A deployment that needs revocation to apply instantly can shorten the lifetime, or turn on the optional status check (each department then calls the Exchange per token, and refuses tokens while the Exchange is unreachable); see [Department role: accepting](#department-role-accepting) below and the [settings](../deployment/README.md#exchange-optional).

## Two roles, one codebase

| Role | Install | Configured by | What it does |
| --- | --- | --- | --- |
| **Exchange CM** | `agrix` | `receipt_issuer` + `receipt_presenters` | Validates the partner's consent against the partner's policy **for the use case** (one per use case) in the Exchange's Partner Management ([use-case mode](verification-and-enforcement.md#use-case-mode)) and, when a configured **presenter** (the Composite, `agri-composite`) asks with `issue_receipts: true`, signs one consent token per registry. Serves the tokens' status. |
| **Department CM** | `trial`, `dept1` | `trusted_receipt_issuers` | Accepts a consent token from a trusted issuer on `/validate`, checks it, applies the **presenter's scope policy** in the department's Partner Management (the department ceiling), and returns its normal decision to the registry. |

The registry is unchanged: it calls its **own** CM `/validate` with the consent JWS it received (now
a consent token), its `data_controller`, and the DCI `sender_id` as `partner_id` — as it always has.

```mermaid
sequenceDiagram
    participant B as Bank (bank-a)
    participant C as Composite (agri-composite)
    participant X as Exchange CM (agrix)
    participant R as Farmer Registry (trial)
    participant D as Department CM (trial)
    B->>C: request (+ consent signed by bank-a, or none)
    C->>X: POST /validate {consent_jws or none, consent_partner_id, partner_id: agri-composite, issue_receipts: true, use_case, purpose, requested_scopes}
    X->>X: no consent sent → look up bank-a's consent for subject + use case
    X->>X: bank-a has a policy for the use case; each grant ∩ the use case's scopes
    X-->>C: permit + receipts {farmer-registry: token JWS, crop-sown-registry: token JWS}
    C->>R: DCI search, sender_id agri-composite, consent = FR consent token
    R->>D: POST /validate {consent_jws: token, data_controller, partner_id: agri-composite}
    D->>X: GET /.well-known/jwks.json (cached)
    D->>D: token scopes ∩ agri-composite's scope policy for farmer-registry (department PM)
    D-->>R: permit, effective_data_scopes, subject_id
```

## Consent token

A compact JWS signed with the CM's **existing receipt-signing key** — the same key, `kid` and
algorithm as its [Kantara receipts](data-model.md#consent-receipt-kantara-iso-27560), published at
`/.well-known/jwks.json` on the partner API.

**Header:** `{"alg": "<EdDSA|ES256|RS256>", "kid": "<CM kid>", "typ": "consent-receipt+jwt"}`

`typ` marks the JWS as a consent token, so a CM never mistakes it for a partner-signed consent. The value is OpenG2P's own (explicit typing, as RFC 8725 §3.11 recommends), not a registered media type; its name dates from when these tokens were called consent receipts.

| Claim | Meaning |
| --- | --- |
| `iss` | The Exchange CM's issuer ID (`receipt_issuer`, e.g. `agri-stack-exchange-cm`) |
| `jti` | Token ID (UUID) — the key for its status |
| `consent_id` | The Exchange CM's consent artefact for this registry |
| `aud` | The data controller the token is for (e.g. `farmer-registry`) |
| `presenter` | Who may present it — the caller that asked for it (e.g. `agri-composite`) |
| `partner` | The partner that obtained the consent (the consent's `aud`, e.g. `bank-a`) |
| `sub` | The subject, `{"type": "FAYDA_FAN", "value": "…"}` — same shape as the consent's `subject_id` |
| `purpose` | Purpose code |
| `scopes` | Data scope IDs for this registry: the consent's grant ∩ the use case's `requested_scopes` (in use-case mode) or ∩ the partner's scope policy for this registry at the Exchange |
| `consent_issued_at` | When the farmer's consent was issued (ISO-8601). Registries use it as "consent time" for data-scope versions |
| `consent_exp` | Consent expiry (epoch seconds) |
| `iat`, `nbf`, `exp` | Token times (epoch seconds); `exp` = min(consent expiry, now + `receipt_ttl_seconds`, default 300) |

> `sub` is an object, as the spec requires, so a generic RFC 7519 JWT validator (which wants a
> string `sub`) rejects it. Verify a consent token at the **JWS** level (signature with the JWKS
> key), then read the claims — as the department CM does.

## Exchange role: issuing

`POST /consent/v1/validate` with `issue_receipts: true`:

1. **Caller check** — the request's `partner_id` must be in `receipt_presenters` and `receipt_issuer`
   must be set; otherwise the decision is `deny` / `receipt_presenter_not_allowed`. The partner API
   has no Keycloak (transport is Istio mTLS), so — as for every partner-API call — the caller is
   identified by the `partner_id` it sends. That value becomes the token's `presenter`, which the
   department CM then matches against the `sender_id` the registry verified on the signed DCI
   request: a consent token is only usable by the presenter it was issued to.
2. **Consent** — the partner-signed `consent_jws`, a consent the CM holds by `consent_id`, or, with
   neither, the one it finds for the partner, subject and use case
   ([consent by lookup](verification-and-enforcement.md#use-case-mode); none → `consent_not_found`).
   The partner therefore never has to handle the Exchange's consent IDs.
3. **Validation** — each granted controller (or only `data_controller`, if sent) is validated
   as a registry's call would be (for a partner-signed consent: signature via Partner Management and
   replay; for any consent: status and validity). The policy
   is the partner's policy **for that use case** when the Composite sends `request_context.use_case`
   (none → `use_case_not_granted`; effective scopes = grant ∩ `requested_scopes`), otherwise the partner's
   scope policy for that controller in the Exchange's Partner Management
   ([use-case mode](verification-and-enforcement.md#use-case-mode)). Each writes its artefact and
   decision log as usual.
4. **Consent tokens** — if every controller permits, one token per controller is signed and recorded
   (`issued_receipts`), and the response carries `receipts: {data_controller: JWS}`. If any
   controller denies, that deny is returned and **no** tokens are issued.

**Status** — `GET /consent/v1/receipts/{jti}/status` → `active | revoked | expired`, for departments
that turn the optional status check on. A consent token
is `revoked` when its consent artefact is revoked (per registry: revoking the farmer-registry consent
revokes only that token), `expired` after its `exp` or when its consent expires. Auth follows the
partner API (no Keycloak; the jti is an unguessable UUID and the answer is only the status).

## Department role: accepting

When `/validate` receives a JWS whose header `typ` is `consent-receipt+jwt`:

1. **Issuer** — `iss` must be in `trusted_receipt_issuers`; otherwise deny
   `receipt_issuer_not_trusted` (also when no issuers are configured — a consent token is never
   accepted by default).
2. **Signature** — verified against the issuer's JWKS (cached `receipt_jwks_cache_ttl_seconds`,
   refetched — throttled — when the `kid` is unknown, so a key rotation is picked up at once). A bad
   signature, `alg` mismatch or missing claims → `receipt_invalid`.
3. **Audience, presenter, time** — `aud` must equal `data_controller` (`audience_mismatch`);
   `presenter` must equal the caller's `partner_id` (the registry's DCI `sender_id`) and the trusted
   issuer's configured `presenter`, if set (`presenter_mismatch`); `nbf`/`exp` (`expired`, 30 s
   clock leeway on `nbf`).
4. **Status** (optional, **off by default**) — the token is checked offline: signature, issuer,
   presenter, audience, subject, expiry and ceiling. Tokens are short-lived and issued for one
   registry and one query; a revocation applies at the Exchange at once (no new tokens) and to issued
   tokens within their lifetime. With `receipt_status_check: always` the department also `GET`s the
   token's status at the issuer (cached `receipt_status_cache_ttl_seconds`, default 10 s) — a runtime
   call to the Exchange CM per token: `revoked`/`expired` deny with that reason; unreachable →
   `receipt_status_unavailable` (fail closed).
5. **Department ceiling** — the **presenter's** (the Composite's, PM partner
   `PARTNER_AGRI_COMPOSITE`) active scope policy for this controller in the department's Partner
   Management (none → `unknown_partner`; PM unreachable with nothing cached → `policy_unavailable`). Subject type and purpose must be allowed; validity
   (`consent_issued_at` → `consent_exp`) is checked against `max_validity_duration`; **effective
   scopes = token `scopes` ∩ policy `allowed_data_scopes`** (∩ `requested_scopes`, if sent).
6. **Decision** — the normal response (`permit`/`deny`, `effective_data_scopes`, `subject_id` from
   `sub`, `policy_version`, `consent_id`). A permit mints an artefact (`source: receipt`, valid until
   the token expires) and a Kantara consent receipt as usual; presenting the same token again
   returns the stored decision. Every decision on a consent token — permit or deny — logs
   `receipt_jti` and `receipt_issuer` in the decision log.

The policy's `allowed_signing_algs` governs partner signatures and is not applied to consent tokens
(the Exchange CM's key is trusted through `trusted_receipt_issuers`).

## Setting up a department for the Exchange

1. Choose the department role (Helm `global.agriStackExchange.role: department`, which trusts the
   Exchange CM by default; or set `trustedIssuer` yourself, see
   [Deployment](../deployment/README.md#exchange-optional)).
2. In the department's **Partner Management**, give the presenter (`agri-composite`, PM partner
   `PARTNER_AGRI_COMPOSITE`) its key and a **scope policy for each registry** it may read, raised and
   approved as a PM request: that policy is the department's ceiling on what the Exchange may
   receive, so it must cover the registry's scopes of every published use case ([Access policies](../../platform/platform-services/partner-management/functional-specifications.md#access-policies)).
   The Agri Stack setup script does this; see
   [Data-sharing policies](../../open-agri-stack/architecture/data-sharing-policies.md).
3. The registry needs no change beyond accepting the presenter as a DCI sender.
