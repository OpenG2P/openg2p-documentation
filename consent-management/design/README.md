---
description: >-
  Design of the OpenG2P Consent Manager — architecture, data model, the
  verify-and-enforce and origination flows, partner policy, security, and
  alignment with industry best practice.
---

# Design

This section specifies the design of the Consent Manager (CM). It is **API-first** — the
contract is documented before any UI — and is organised so you can read it top to bottom.

CM follows the OpenG2P platform **4-API audience pattern** (staff / beneficiary / agent / partner):
today it ships a **staff** API and a **partner** API, with a **beneficiary** API scaffolded for
later and no agent API — one Helm chart and one image, a Deployment per audience. Partner identity
and signing keys are owned by **Partner Management (PM)** — CM fetches partner keys from PM and holds
only a policy binding — and data-share **policy changes** are approved through the shared **Approval
Workflow Engine (AWE)**.

## Key terms

Four things are easily confused; the CM keeps them apart:

| Term | What it is | Signed by | Lives | Standard |
| --- | --- | --- | --- | --- |
| **Consent object** | A consent the partner collected itself and presents with a request (`consent_jws`) | the partner | as long as its validity | the CM's JSON-LD consent object |
| **Consent artefact** | The consent as the CM stores it: subject, partner, purpose, a grant per data controller, validity, assurance | — (stored in the CM) | until it expires or is revoked | DEPA (consent artefact) |
| **Consent receipt** | The proof that a consent was given, created when it is approved (and per decision at `/validate`); the partner's copy is in its consent record | the CM | long-lived | Kantara Consent Receipt v1.1, ISO/IEC 27560 |
| **Consent token** | A short-lived note the Exchange's CM issues for **one** data controller and **one** query, with only the scopes allowed there; the controller's own CM checks it (called *receipt* in the API and settings) | the Exchange's CM | about 15 minutes | in the spirit of OAuth 2.0 token exchange (RFC 8693) |

See [data model](data-model.md), [standards](standards-and-best-practices.md) and [Exchange consent tokens](exchange-receipts.md).

## Pages

| Page | What it covers |
| --- | --- |
| [Architecture](architecture.md) | Components, the PDP/PEP model, the API-audience split, PM and AWE integration, registry integration, end-to-end sequence diagrams, information flow. |
| [Data model](data-model.md) | Canonical entities and the JSON-LD documents — consent object, auth context, artefact, receipt — plus the partner policy binding and policy records. |
| [Verification &amp; enforcement](verification-and-enforcement.md) | The **primary** flow: a partner embeds a signed consent object, the CM validates it and returns the effective fields. |
| [Partner onboarding &amp; policy](partner-onboarding-and-policy.md) | How partner policy bindings and versioned data-share policies are managed and evaluated. |
| [Partner Management integration](partner-management-integration.md) | How CM fetches and caches partner verifying keys from PM, and holds only a policy binding (no partner identity or keys of its own). |
| [Approval Workflow integration](approval-workflow-integration.md) | How CM gates data-share policy widening through AWE — pending version, proxied approvals inbox, HMAC webhook, activate/supersede. |
| [Exchange consent tokens](exchange-receipts.md) | Agri Stack Exchange (opt-in): the Exchange CM signs a short-lived consent token per registry and query; a department CM accepts tokens from a trusted issuer under its own standing policy. |
| [Consent lifecycle](consent-lifecycle.md) | The **secondary** flow: originating consent (request → authenticate → approve → artefact → receipt), revocation, and expiry. |
| [Consent collection](consent-collection.md) | How a partner seeks consent and how the subject gives it: in person with a form (built), in person digitally, self-service; national-ID login, identifiers and demographics, the partner's copy, the gaps, and the partner portal. |
| [Security &amp; trust](security-and-trust.md) | Signing and key management, ID-token validation, replay protection, and the threat model. |
| [Standards &amp; best practices](standards-and-best-practices.md) | Alignment with Kantara/ISO 27560, GDPR, DEPA/AA, and DCI/OIDC — and the gaps we deliberately close. |

The full HTTP contract lives under [API Reference](../api/README.md).
