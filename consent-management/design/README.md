---
description: >-
  Design of the OpenG2P Consent Manager — architecture, data model, the
  verify-and-enforce and origination flows, partner policy, security, and
  alignment with industry best practice.
---

# Design

This section specifies the design of the Consent Manager (CM). It is **API-first** — the
contract is documented before any UI — and is organised so you can read it top to bottom.

| Page | What it covers |
| --- | --- |
| [Architecture](architecture.md) | Components, the PDP/PEP model, registry integration, end-to-end sequence diagrams, information flow. |
| [Data model](data-model.md) | Canonical entities and the JSON-LD documents — consent object, auth context, artefact, receipt — plus partner and policy records. |
| [Verification &amp; enforcement](verification-and-enforcement.md) | The **primary** flow: a partner embeds a signed consent object, the CM validates it and returns the effective fields. |
| [Partner onboarding &amp; policy](partner-onboarding-and-policy.md) | How partners are registered, how their keys and policies are managed, and how policy is evaluated. |
| [Consent lifecycle](consent-lifecycle.md) | The **secondary** flow: originating consent (request → authenticate → approve → artefact → receipt), revocation, and expiry. |
| [Security &amp; trust](security-and-trust.md) | Signing and key management, ID-token validation, replay protection, and the threat model. |
| [Standards &amp; best practices](standards-and-best-practices.md) | Alignment with Kantara/ISO 27560, GDPR, DEPA/AA, and DCI/OIDC — and the gaps we deliberately close. |

The full HTTP contract lives under [API Reference](../api/README.md).
