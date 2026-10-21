---
description: >-
  Design of the OpenG2P Consent Manager — architecture, data model, the
  verify-and-enforce and origination flows, how partner policies from Partner
  Management are applied, security, and alignment with industry best practice.
---

# Design

This section specifies the design of the Consent Manager (CM). It is **API-first** — the
contract is documented before any UI — and is organised so you can read it top to bottom.

CM follows the OpenG2P platform **4-API audience pattern** (staff / beneficiary / agent / partner):
today it ships a **staff** API and a **partner** API, with a **beneficiary** API scaffolded for
later and no agent API — one Helm chart and one image, a Deployment per audience. Partners, their
signing keys and their **access policies** are owned by **Partner Management (PM)**, where changes
are approved; the CM reads keys and policies from PM and owns only the consent.

## Key terms

Four things are easily confused; the CM keeps them apart. A fifth term, **data scope**, is what they are all written in:

| Term | What it is | Signed by | Lives | Standard |
| --- | --- | --- | --- | --- |
| **Consent object** | A consent the partner collected itself and presents with a request (`consent_jws`) | the partner | as long as its validity | the CM's JSON-LD consent object |
| **Consent artefact** | The consent as the CM stores it: subject, partner, purpose, a grant per data controller, validity, assurance | — (stored in the CM) | until it expires or is revoked | DEPA (consent artefact) |
| **Consent receipt** | The proof that a consent was given, created when it is approved (and per decision at `/validate`); the partner's copy is in its consent record | the CM | long-lived | Kantara Consent Receipt v1.1, ISO/IEC 27560 |
| **Consent token** | A short-lived note the Exchange's CM issues for **one** data controller and **one** query, with only the scopes allowed there; the controller's own CM checks it (called *receipt* in the API and settings) | the Exchange's CM | about 15 minutes | in the spirit of OAuth 2.0 token exchange (RFC 8693) |
| **Data scope** | A named group of one data controller's (registry's) own fields, e.g. `farmer-registry.land`. Consents, partner policies and tokens list scopes, never fields or output keys; the registry maps each scope to its fields and filters records to them before rendering | — (defined and published by the registry) | permanent ID, versioned contents | the registry's catalogue ([Data Scopes](../../products/registry/registry/design/data-scopes.md)) |

See [data model](data-model.md), [standards](standards-and-best-practices.md) and [Exchange consent tokens](exchange-receipts.md).

## Design decisions

| Decision | Why | Details |
| --- | --- | --- |
| **One consent, a grant per data controller.** A partner asks the subject once for everything it needs; the consent lists a grant per registry (data controller). | The partner thinks in terms of the data it needs, not of who holds it. The subject sees one request. India's Account Aggregator works the same way: one consent artefact, several data providers. | [Verification & enforcement](verification-and-enforcement.md), [data model](data-model.md) |
| **Each data controller validates only its own grant, at its own CM.** `/validate` takes the calling controller and returns its grant ∩ the partner's policy for it. | Each department stays sovereign over its data: no other party decides what it releases. | [Verification & enforcement](verification-and-enforcement.md) |
| **Replay and usage are counted per consent and controller.** | One consent is presented to several registries; one-shot and periodic limits apply to each separately. | [Security & trust](security-and-trust.md) |
| **Consent is preferably collected by the CM.** The partner can also sign a consent it collected itself. | Departments trust a consent the CM witnessed (national-ID login, evidence, verification) more than one a partner vouches for, and the subject sees the same process whoever asks. | [Consent collection](consent-collection.md) |
| **The subject proves who they are with the national ID; an SMS is only a notification.** Demographics shown to staff come from that login and are never compared automatically. | A phone number or a reply proves little. Registry data is not exposed to the CM. | [Consent collection](consent-collection.md#identifiers-and-demographics) |
| **The stored consent never changes.** The partner's downloadable consent record only adds to it (evidence, the CM's signed statement). | The consent stays the single source of truth; the record is a copy the partner can prove. | [Consent collection](consent-collection.md#the-partners-copy-of-a-consent) |
| **Across installs, a short-lived consent token per controller** instead of passing the consent on. The issuing CM signs a token with only that controller's allowed scopes; the controller's CM verifies it, checks its status, and applies the policy its own Partner Management holds for the presenter. Only named presenters may ask for tokens. | A controller in another install sees only what concerns it, for one query; revocation takes effect at once; a stolen token is useless to anyone else. | [Exchange consent tokens](exchange-receipts.md) |
| **Partner access policies are in Partner Management; the CM keeps only consent.** The CM reads the partner's active policy from PM (cached, fail closed) and records its version on every decision. | Policies describe the partner agreement, which belongs with the partner: onboarding, key and policy changes are approved in one place, and the CM, the Composite and the registries read the same policies. | [Partner Management integration](partner-management-integration.md) |
| **At an Exchange, partners are granted use cases, not registry scopes.** When the Composite names a use case, the CM checks the partner's use-case policy and limits each registry to the use case's scopes. | A partner asks for an outcome (e.g. a loan profile); which registries answer it is the Exchange's business. | [Use-case mode](verification-and-enforcement.md#use-case-mode) |

## Pages

| Page | What it covers |
| --- | --- |
| [Architecture](architecture.md) | Components, the PDP/PEP model, the API-audience split, PM integration, registry integration, end-to-end sequence diagrams, information flow. |
| [Data model](data-model.md) | Canonical entities and the JSON-LD documents — consent object, auth context, artefact, receipt. |
| [Verification &amp; enforcement](verification-and-enforcement.md) | The **primary** flow: a partner embeds a signed consent object, the CM validates it against the partner's policy and returns the effective fields; use-case mode. |
| [Partner Management integration](partner-management-integration.md) | How the CM reads partner keys and access policies from PM: the partner ID convention, endpoints, caching, fail-closed behaviour. |
| [Exchange consent tokens](exchange-receipts.md) | Agri Stack Exchange (opt-in): the Exchange CM signs a short-lived consent token per registry and query; a department CM accepts tokens from a trusted issuer under the Composite's policy in its own PM. |
| [Consent lifecycle](consent-lifecycle.md) | The **secondary** flow: originating consent (request → authenticate → approve → artefact → receipt), revocation, and expiry. |
| [Consent collection](consent-collection.md) | How a partner seeks consent and how the subject gives it: in person with a form (built), in person digitally, self-service; national-ID login, identifiers and demographics, the partner's copy, the gaps, and the partner portal. |
| [Security &amp; trust](security-and-trust.md) | Signing and key management, ID-token validation, replay protection, and the threat model. |
| [Standards &amp; best practices](standards-and-best-practices.md) | Alignment with Kantara/ISO 27560, GDPR, DEPA/AA, and DCI/OIDC — and the gaps we deliberately close. |

The full HTTP contract lives under [API Reference](../api/README.md).
