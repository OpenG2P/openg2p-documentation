---
description: >-
  The OpenG2P Consent Manager: the Policy Decision Point for outbound data
  sharing. It holds the subject's consent, checks it against the partner's
  access policy in Partner Management, and tells the registry what it may
  release.
---

# Consent Management

{% hint style="info" %}
**Source code:** [https://github.com/OpenG2P/consent-manager](https://github.com/OpenG2P/consent-manager)
{% endhint %}

## Overview

The **Consent Manager** (CM) decides whether personal data may leave a registry. The registry never interprets consent: it asks the CM and releases only what the CM permits.

> **No outbound data is shared from a registry without a permit from the Consent Manager.**

The CM is the **Policy Decision Point (PDP)**. A registry, or any other data-holding service, is a **Policy Enforcement Point (PEP)**.

## Where responsibilities sit

| Concern | Owner |
| --- | --- |
| Partners, their signing keys and their **access policies** (what a partner may ever receive) | **Partner Management (PM)**. Changes are requested and approved there. The CM reads them, cached ([Partner Management integration](design/partner-management-integration.md)) |
| The subject's **consent**, the decision at `/validate`, consent receipts and consent tokens | **Consent Manager**. Receipts and tokens are signed with the CM's own `.p12` key, published at `/.well-known/jwks.json`; the CM is not a PM partner |
| The data, its [data scopes](../products/registry/registry/design/data-scopes.md), and releasing only the permitted fields | **The registry** ([Registry integration](design/registry-integration.md)) |

## What problem it solves

Programmes share beneficiary data with partners (banks, agencies, other registries). On every request someone must answer:

* Is the requester a **known, onboarded party**?
* Did the **subject** consent, and is the consent still valid?
* Does the request stay **within the partner's policy** (data, purpose, validity)?
* Is there **signed, auditable proof** of the decision?

The CM answers these once, for every registry.

## Two operating modes

1. **Verify &amp; enforce (primary).** A partner calls a registry about a person. The registry asks the CM, which finds or verifies the consent, applies the partner's policy for that registry, and returns the **effective data scopes**. See [Verification & enforcement](design/verification-and-enforcement.md).
2. **Originate (secondary).** Consent is collected through the CM itself: in person through the partner portal (a signed form checked by CM staff, optionally the subject's national-ID login), or through the origination API. See [Consent collection](design/consent-collection.md) and [Consent lifecycle](design/consent-lifecycle.md).

## Design principles

* **Delegated consent.** Data-holding services enforce a decision; they never interpret consent.
* **Policy-bound consent.** Every partner has a versioned access policy in Partner Management. A consent can never exceed it.
* **Signed proof.** Receipts and consent tokens are signed by the CM; anyone can check them against its public keys.
* **Data minimisation and purpose limitation.** The CM returns the intersection of what was consented and what the policy allows.
* **Append-only audit.** Every decision and state change is logged.
* **Standards-aligned.** Kantara / ISO 27560 receipts, GDPR subject rights, the DEPA artefact model, DCI and OIDC ([Standards](design/standards-and-best-practices.md)).

## Not built yet

* **Beneficiary API deployed by default.** The subject API (`/my/*`) and origination API are built but run on the beneficiary API, which the chart ships disabled; subjects have no portal yet (staff revoke on their request).
* **Consent scenarios 2 and 3:** the subject approving digitally after the national-ID login, and self-service with a redirect back to the partner ([Consent collection](design/consent-collection.md#scenarios)).
* **Notifications** to subjects and partners (grant, revoke, expiry; an SMS with a revoke link after digital approval) and revocation webhooks.
* **A minimum assurance per policy.**
* **Partner portal:** partner-user management from the portal (staff create users today); a partner-signed API for partners with their own systems.
* **Evidence:** encryption at rest beyond the object store's, retention and deletion rules.
* **Receipts:** the controller's name, contact and DPO, retention and jurisdiction are not filled in yet.
* **Forwarding decisions to the Audit Manager.**

## How to read this section

{% content-ref url="design/README.md" %}
[README.md](design/README.md)
{% endcontent-ref %}

{% content-ref url="api/README.md" %}
[README.md](api/README.md)
{% endcontent-ref %}
