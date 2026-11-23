---
description: >-
  How the Consent Manager reads partner keys and access policies from Partner
  Management: the partner ID convention, the endpoints it calls, which policy
  each check uses, per-pod caching, and fail-closed behaviour.
---

# Partner Management integration (keys and policies)

The Consent Manager (CM) keeps no partner records. **Partner Management (PM)** owns who a partner is,
its signing keys and its **access policies** (what it may ask for). The CM reads keys and policies
from PM when it needs them and owns only the **consent**: consents and consent requests, the
decision at `/validate`, receipts and consent tokens.

## Who owns what

| Concern | Owner | Where it is managed |
| --- | --- | --- |
| Partner identity, organisation, status | PM | PM staff UI and API |
| Partner signing keys | PM | PM (onboarding and key-update requests) |
| Access policies (scopes, use cases, purposes, validity, …) | PM | PM (onboarding and policy requests, approved in PM). The CM reads only scope policies |
| Consents, consent requests, assisted-consent verification | CM | CM console and partner portal |
| The decision at `/validate`, receipts, consent tokens | CM | — (computed per request) |

Why policies live in PM:

* **A policy describes the partner agreement**, which belongs with the partner. Onboarding, key and
  policy changes are approved in one place, through PM's request-and-approve flow.
* **Several modules read the same policies.** The CM reads the partner's scope policies from PM and
  an Exchange's Composite its use-case policies, and registries verify partner signatures with PM's keys, so there is no copy to
  keep in step.
* **The CM stays a verifier.** It checks consent against a policy; it does not govern the policy.

The CM is **not** a PM partner: it signs receipts and consent tokens with its own `.p12` key and
publishes the public half at `/.well-known/jwks.json` ([Security & trust](security-and-trust.md)).

The policy model — scope policies (one per registry) and use-case policies (one per use case, read by the Composite only), their fields, versions and statuses, and how
changes are requested and approved — is documented by PM:
[Access policies](../../platform/platform-services/partner-management/functional-specifications.md#access-policies).
For how an Agri Stack deployment uses them (use-case grants at the Exchange, the Composite's ceiling
in each department) see [Data-sharing policies](../../open-agri-stack/architecture/data-sharing-policies.md).

## Partner ID convention

A partner signs its consents with its **audience** (`aud`, the same value as its DCI `sender_id`,
e.g. `bank-a`). Its PM partner ID follows by convention: upper-case, `-` → `_`, prefix `PARTNER_`.

```
bank-a          → PARTNER_BANK_A
agri-composite  → PARTNER_AGRI_COMPOSITE
```

There is no per-partner override. The CM uses the PM ID for both keys and policies; its own records
(artefacts, consent requests, decision logs, grants) store the **audience** as `partner_id`, with the
policy applied: `policy_ref` (`data_controller:<registry>`), `policy_version` and `policy_id` (PM's id
of that version). With no PM policy (terms sent by the Composite, or a consent template),
`policy_ref` is `template:<code>` and the other two are empty.

## What the CM reads from PM

All reads go to PM's internal partner API (`CONSENT_MANAGER_PARTNER_MGMT_API_URL`, in-cluster
`http://commons-services-pm-partner-api`), which needs no authentication and is reachable only
inside the cluster. Request and response shapes:
[PM API reference](../../platform/platform-services/partner-management/api-reference.md).

| Read | Call | Used for |
| --- | --- | --- |
| **Key** | `GET {pm}/keys/PARTNER_<AUD>/…` (by the JWS `kid`) | Verifying the signature of a partner's consent object |
| **One policy** | `GET {pm}/policies/PARTNER_<AUD>?data_controller=<controller>` | The partner's **scope policy** for one registry |
| **All policies** | `GET {pm}/policies/PARTNER_<AUD>` | The partner portal's **Data access** page (its scope policies) |

The CM reads no use-case policies. At an Exchange the Composite reads them; the CM gets what it needs from the Composite's terms at `/validate` and from the consent templates ([caller-terms mode](verification-and-enforcement.md#caller-terms-mode)).

PM returns only **active** policies of an **active** partner. A pending change never affects a
decision; once approved in PM it applies within the cache time below.

### Which policy each check uses

| Situation | Policy read |
| --- | --- |
| A registry validates a consent (`/validate`) | The consenting partner's scope policy for the calling registry (`data_controller`) |
| The Composite validates at the Exchange with `request_context.purpose` ([caller-terms mode](verification-and-enforcement.md#caller-terms-mode)) | None: the terms the Composite sends apply (the partner's key is still read) |
| A department CM accepts a consent token ([Exchange consent tokens](exchange-consent-tokens.md#department-role-accepting)) | The **presenter's** (the Composite's) scope policy for the calling registry |
| A consent request is created or approved (origination, partner portal) | The partner's scope policy for each requested registry; at an Exchange, for a request made from a consent template, none: the template's limits apply ([consent collection](consent-collection.md#partner-portal)) |

How the CM applies a policy at `/validate` is described in
[Verification & enforcement](verification-and-enforcement.md#how-the-policy-is-applied).

## Caching

Keys and policies change rarely but are read on every `/validate`, so the CM caches each answer from PM **per pod**, instead of calling PM each time or copying PM's data. The general rules for modules consuming PM are on PM's [integration page](../../platform/platform-services/partner-management/integration.md).

| Behaviour | Keys | Policies |
| --- | --- | --- |
| **Reuse** — no call to PM | up to the soft TTL (default 300 s), capped by PM's `Cache-Control: max-age` | per partner and registry, up to the soft TTL (default 60 s), capped likewise |
| **PM unreachable** | the last answer, up to the hard TTL; then fail closed | the same; then deny `policy_unavailable` |
| **PM says "none"** (`404`) | remembered for the negative TTL (30 s) | the same; a failed call is also not retried for that long |
| **Unknown `kid`** | a rate-limited refresh (catches key rotation) | — |
| **Concurrent misses** | share one call | share one call |

What this means in operation:

* **A policy change approved in PM** (a new grant, a widening, a revocation) applies within the soft TTL, one minute by default.
* **During a PM outage** the CM keeps working on what it last knew, up to the hard TTL (six hours by default). A partner revoked just before the outage can therefore still pass until then. A shorter hard TTL narrows that window but stops partners sooner when PM is down.
* **After the hard TTL**, or with nothing cached, the CM denies: it never skips the check.

The times are install-time settings: [Deployment: Partner Management](../deployment/README.md#partner-management).

## Failing closed

PM answers `404` with the same body whether the partner is unknown, not active, or has no matching
active policy or key. The CM never treats a missing answer as "skip the check":

| PM answer | Decision |
| --- | --- |
| No active policy for the partner and registry | deny `unknown_partner` (for a consent the CM holds: that grant is dropped; none left → `scope_exceeds_policy`) |
| No usable key for the JWS `kid` | deny `signature_invalid` |
| PM unreachable and nothing usable cached | deny `policy_unavailable` (retry later) |

## Managing partners and policies

Partners, keys and policies are managed in PM's staff UI. The CM console has no partner pages; it
links to PM (**Partners & policies**, chart value `global.partnerManagementUiUrl`).
