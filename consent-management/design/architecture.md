---
description: >-
  Architecture of the Consent Manager — the PDP/PEP model, internal components,
  how the registry integrates, and the end-to-end information flow.
---

# Architecture

## The PDP / PEP model

The Consent Manager (CM) is a **Policy Decision Point (PDP)**. Any service that holds personal
data — primarily the OpenG2P Registry — is a **Policy Enforcement Point (PEP)**. The PEP holds
the data; the PDP holds the consent and policy logic and renders decisions.

```mermaid
flowchart LR
  Partner["Partner / Requesting System"]
  Registry["OpenG2P Registry (PEP)\nholds the data"]
  CM["Consent Manager (PDP)\nverifies + decides"]
  Store[("CM stores:\nartefacts · receipts ·\npartners · policies · audit")]

  Partner -->|"1 API call + embedded\nsigned consent object"| Registry
  Registry -->|"2 validate(consent_object, ctx)"| CM
  CM --> Store
  CM -->|"3 decision + effective_data_scopes"| Registry
  Registry -->|"4 release only permitted fields"| Partner
```

The registry never parses or interprets the consent object. It forwards it, receives a decision
that includes the **effective set of fields**, and releases only those.

## Components

| Component | Responsibility |
| --- | --- |
| **Verification API** | Validates an embedded consent object and returns a decision (the hot path). |
| **Policy Engine** | Evaluates a consent object against the onboarded partner's versioned policy; computes the effective scope. |
| **Partner Registry** | Stores partners, their public keys (JWKS), and their policies. |
| **Trust / Key Store** | Partner public keys for verifying consent objects; the CM's own key pair for signing receipts. |
| **Artefact &amp; Receipt Service** | Produces canonical consent artefacts and CM-signed receipts (JSON-LD). |
| **Origination Service** | The secondary flow — consent requests, OIDC authentication, approval. |
| **Revocation &amp; Expiry** | Revocation store + status endpoint; background expiry of stale consents. |
| **Audit / Decision Log** | Append-only, tamper-evident record of every decision and state change. |
| **Notification Worker** | Async notifications to subjects/partners on grant, revoke, and expiry. |

## Primary flow — verify &amp; enforce

A partner already holds (or has collected) consent and embeds a **partner-signed consent
object** in its data request to the registry.

```mermaid
sequenceDiagram
  participant P as Partner
  participant R as Registry (PEP)
  participant CM as Consent Manager (PDP)
  participant DB as CM Store

  P->>R: GET /farmer/{id}?... + signed consent_object
  R->>CM: POST /consent/v1/validate {consent_object, partner_id, request_ctx}
  CM->>CM: 1. schema-validate object
  CM->>DB: 2. look up partner + key (kid) + policy
  CM->>CM: 3. verify JWS signature (known party)
  CM->>CM: 4. audience / subject / purpose checks
  CM->>CM: 5. effective = consent_scope ∩ policy_scope
  CM->>DB: 6. revocation + validity check
  CM->>DB: 7. persist artefact + signed receipt + decision log
  CM-->>R: {decision: permit, effective_data_scopes, receipt_id, ...}
  R->>R: project record to effective_data_scopes
  R-->>P: data (only permitted fields) + receipt_id
```

If any check fails, the CM returns `decision: deny` with a precise `reason_code`, the registry
releases nothing, and the denial is still logged.

## Secondary flow — originate consent

When OpenG2P itself collects consent (no pre-existing partner-signed object), the CM drives an
authentication + approval flow and issues the artefact and receipt.

```mermaid
sequenceDiagram
  participant Sub as Subject
  participant CM as Consent Manager
  participant IdP as OIDC Provider

  CM->>CM: create ConsentRequest (status=pending)
  Sub->>IdP: authenticate (OTP / biometric / ...)
  IdP-->>Sub: ID Token (JWS)
  Sub->>CM: approve(request_id, id_token, granted_scopes)
  CM->>IdP: validate signature + claims (JWKS)
  CM->>CM: build AuthContext (id_token_hash, verified_claims)
  CM->>CM: issue ConsentArtefact (status=active)
  CM->>CM: sign ConsentReceipt (CM private key)
  CM-->>Sub: artefact + receipt
```

This is covered in detail in [Consent lifecycle](consent-lifecycle.md).

## Registry integration

The registry's consent-aware data sharing supports two ingestion patterns, both terminating at
`POST /consent/v1/validate`:

1. **Stored consent** — the individual previously consented; the registry passes the request
   context and the CM matches an existing active artefact.
2. **Embedded consent payload** — the partner includes a signed consent object directly
   (DCI / UNDP-style). The CM validates it, generates a canonical artefact + signed receipt,
   stores them, and returns the decision.

{% content-ref url="../../products/registry/registry/features/consent-aware-data-sharing.md" %}
[consent-aware-data-sharing.md](../../products/registry/registry/features/consent-aware-data-sharing.md)
{% endcontent-ref %}

## Information flow

<figure><img src="../../.gitbook/assets/image (4).png" alt="Consent management information flow"><figcaption><p>End-to-end information flow across subject, identity provider, registry, and Consent Manager.</p></figcaption></figure>
