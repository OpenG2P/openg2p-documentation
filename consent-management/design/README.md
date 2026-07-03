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

| Page | What it covers |
| --- | --- |
| [Architecture](architecture.md) | Components, the PDP/PEP model, the API-audience split, PM and AWE integration, registry integration, end-to-end sequence diagrams, information flow. |
| [Data model](data-model.md) | Canonical entities and the JSON-LD documents — consent object, auth context, artefact, receipt — plus the partner policy binding and policy records. |
| [Verification &amp; enforcement](verification-and-enforcement.md) | The **primary** flow: a partner embeds a signed consent object, the CM validates it and returns the effective fields. |
| [Partner onboarding &amp; policy](partner-onboarding-and-policy.md) | How partner policy bindings and versioned data-share policies are managed and evaluated. |
| [Partner Management integration](partner-management-integration.md) | How CM fetches and caches partner verifying keys from PM, and holds only a policy binding (no partner identity or keys of its own). |
| [Approval Workflow integration](approval-workflow-integration.md) | How CM gates data-share policy widening through AWE — pending version, proxied approvals inbox, HMAC webhook, activate/supersede. |
| [Consent lifecycle](consent-lifecycle.md) | The **secondary** flow: originating consent (request → authenticate → approve → artefact → receipt), revocation, and expiry. |
| [Security &amp; trust](security-and-trust.md) | Signing and key management, ID-token validation, replay protection, and the threat model. |
| [Standards &amp; best practices](standards-and-best-practices.md) | Alignment with Kantara/ISO 27560, GDPR, DEPA/AA, and DCI/OIDC — and the gaps we deliberately close. |

The full HTTP contract lives under [API Reference](../api/README.md).
