---
description: >-
  Design of the OpenG2P Consent Manager: key terms, the main design decisions,
  and a guide to the design pages.
---

# Design

The Consent Manager (CM) owns only the **consent**. Partners, their signing keys and their **access policies** are owned by **Partner Management (PM)**, where changes are approved; the CM reads them. One Helm chart and one image run a Deployment per API audience ([Architecture](architecture.md#apis-by-audience)).

## Key terms

Four things are easily confused; the CM keeps them apart. A fifth, **data scope**, is what they are written in.

| Term | What it is | Signed by | Lives | Standard |
| --- | --- | --- | --- | --- |
| **Consent object** | A consent the partner collected itself and presents with a request (`consent_jws`) | the partner | as long as its validity | the CM's JSON-LD consent object |
| **Consent artefact** | The consent as the CM stores it: subject, partner, purpose, a grant per data controller, validity, assurance | — (stored in the CM) | until it expires or is revoked | DEPA (consent artefact) |
| **Consent receipt** | The proof that a consent was given, created when a consent is approved or first validated | the CM | long-lived | Kantara Consent Receipt v1.1, ISO/IEC 27560 |
| **Consent token** | A short-lived note the Exchange's CM issues for **one** data controller and **one** query, with only the scopes allowed there; the controller's own CM checks it (called *receipt* in the API and settings) | the Exchange's CM | 5 minutes by default | in the spirit of OAuth 2.0 token exchange (RFC 8693) |
| **Data scope** | A named group of one registry's own fields, e.g. `farmer-registry.land`. Consents, policies and tokens list scopes, never fields; the registry maps each scope to its fields | — (published by the registry) | permanent ID, versioned contents | the registry's catalogue ([Data Scopes](../../products/registry/registry/design/data-scopes.md)) |

Details: [Data model](data-model.md), [Exchange consent tokens](exchange-consent-tokens.md).

## Design decisions

| Decision | Why | Details |
| --- | --- | --- |
| **One consent, a grant per data controller.** The partner asks the subject once; the consent lists a grant per registry. | The partner thinks in terms of the data it needs. The subject sees one request. India's Account Aggregator works the same way. | [Verification & enforcement](verification-and-enforcement.md), [Data model](data-model.md) |
| **Each data controller validates only its own grant.** `/validate` takes the calling controller and returns its grant ∩ the partner's policy for it. | Each department stays sovereign over its data. | [Verification & enforcement](verification-and-enforcement.md) |
| **Replay and idempotency are per consent and controller.** | One consent is presented to several registries; each gets its own decision and receipt. | [Security & trust](security-and-trust.md#replay-protection) |
| **Consent is preferably collected by the CM.** A partner may present a consent it signed itself only if its policy allows it (`allow_partner_consents`, off by default). | Departments trust a consent the CM witnessed (national-ID login, evidence, staff check) more than one a partner vouches for. | [Consent collection](consent-collection.md) |
| **The subject proves who they are with the national ID; an SMS is only a notification.** Demographics are shown, never compared automatically. | A phone number or a reply proves little. Registry data is not exposed to the CM. | [Consent collection](consent-collection.md#identifiers-and-demographics) |
| **The stored consent never changes.** The partner's downloadable consent record only adds to it. | The consent stays the single source of truth; the record is a copy the partner can prove. | [Consent collection](consent-collection.md#the-partners-copy-of-a-consent) |
| **Across installs, a short-lived consent token per controller** instead of passing the consent on. The controller's CM checks it offline and applies the policy its own PM holds for the presenter. | A controller sees only what concerns it, for one query; a stolen token is useless to anyone else. | [Exchange consent tokens](exchange-consent-tokens.md) |
| **Access policies are in Partner Management.** The CM reads the active policy (cached, fail closed) and records it on every decision. | Policies describe the partner agreement; the CM, the Composite and the registries read the same ones. | [Partner Management integration](partner-management-integration.md) |
| **At an Exchange, partners are granted use cases, not registry scopes.** One policy per use case. | A partner asks for an outcome (e.g. a loan profile); which registries answer it is the Exchange's business. | [Use-case mode](verification-and-enforcement.md#use-case-mode) |

## Pages

| Page | What it covers |
| --- | --- |
| [Architecture](architecture.md) | The PDP/PEP model, API audiences, components. |
| [Data model](data-model.md) | Stored entities and the JSON-LD documents: consent object, artefact, receipt. |
| [Verification &amp; enforcement](verification-and-enforcement.md) | The primary flow: the three ways to present a consent, the validation pipeline, how a policy is applied, use-case mode, consent by lookup. |
| [Partner Management integration](partner-management-integration.md) | How the CM reads keys and policies from PM: partner IDs, calls, caching, failing closed. |
| [Registry integration](registry-integration.md) | The PEP side: where the consent sits in a DCI search, subject and field enforcement, registry settings. |
| [Exchange consent tokens](exchange-consent-tokens.md) | Agri Stack Exchange (opt-in): the Exchange CM issues tokens; a department CM accepts them. |
| [Consent lifecycle](consent-lifecycle.md) | Origination (request, authenticate, approve), revocation and expiry. |
| [Consent collection](consent-collection.md) | How a subject gives consent: the scenarios, national-ID login, identifiers, the partner's copy, the partner portal. |
| [Security &amp; trust](security-and-trust.md) | Keys and signing, replay protection, caller authentication, threat model. |
| [Standards &amp; best practices](standards-and-best-practices.md) | Alignment with Kantara / ISO 27560, GDPR, DEPA and DCI / OIDC. |

The HTTP contract is in the [API Reference](../api/README.md); settings are in [Deployment](../deployment/README.md).
