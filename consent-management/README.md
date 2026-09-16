---
description: >-
  The OpenG2P Consent Management service — a purpose-built microservice that
  governs all outbound data sharing from the registry through verifiable,
  policy-bound, cryptographically provable consent.
---

# Consent Management

{% hint style="info" %}
**Source code:** [https://github.com/OpenG2P/consent-manager](https://github.com/OpenG2P/consent-manager)
{% endhint %}

## Overview

OpenG2P includes a dedicated **Consent Management** microservice (the "Consent Manager", or **CM**) that governs how personal data leaves the registry. The registry never interprets consent itself — it **delegates every consent decision to the CM**.

The fundamental rule is simple:

> **No outbound data is shared from the registry without a positive authorization decision from the Consent Manager.**

This service is the system's **Policy Decision Point (PDP)**. The registry — and any other data-holding service — is a **Policy Enforcement Point (PEP)**: it asks the CM "may I release this data?", and releases only what the CM permits.

## Where responsibilities sit

The CM does not own everything about a partner. Identity and keys live elsewhere:

* **Partner Management (PM) owns partner identity + signing keys.** The CM holds only a thin **policy binding** per partner and, at verification time, **fetches the partner's public key from PM** (by `partner_mgmt_id` + `kid`) to verify the consent object's signature locally. See [Partner Management Integration](design/partner-management-integration.md).
* **The CM owns the data-share policy, the PDP decision, and the receipts.** The versioned policy (allowed fields, purposes, validity ceiling, fetch semantics) is attached to the binding; receipts are signed with the CM's own `.p12` key and published at `/.well-known/jwks.json` (self-verifying — the CM is **not** a PM partner).
* **The Approval Workflow Engine (AWE) gates policy-widening.** A change that grants more than the current active policy sits `pending` until AWE returns an approved outcome, then becomes `active`. See [Approval Workflow Integration](design/approval-workflow-integration.md).
* **API-audience split.** The CM follows the platform's 4-API audience pattern — **staff** (admin console, approver inbox), **partner** (the PDP `/validate`, no Keycloak — trust is the partner-signed object + `jti` replay guard over mTLS), and **beneficiary** (subject self-service).

## What problem it solves

Programmes share beneficiary data with partners (banks, agencies, other registries, interoperability gateways). Doing this safely requires answering, on every request:

* Is the requester a **known, onboarded party**?
* Did the **data subject** actually consent, and is that consent still valid?
* Does the request stay **within the policy** the partner was onboarded under (which fields, which purpose, how long)?
* Is there **cryptographic, auditable proof** of the decision for later dispute resolution?

The Consent Manager centralises these answers so individual services don't each re-implement consent logic.

## Two operating modes

The CM supports two complementary modes. The first is the priority.

### 1. Verify &amp; Enforce — _primary_

A partner calls a registry API and **embeds a signed consent object** in the request. The registry forwards it to the CM, which:

1. verifies the object's signature locally against the partner's public key **fetched from Partner Management** (**known-party** check),
2. evaluates it against the partner's **data-share policy** (allowed fields, purpose, validity),
3. checks it is **not revoked or expired**, and
4. returns a **decision** containing the **effective set of fields** the registry may release (`consent scope ∩ partner policy`).

The registry releases only those fields. The CM persists a canonical artefact, a signed receipt, and an immutable decision log.

### 2. Originate — _secondary_

For first-party flows where consent is collected through OpenG2P itself: the CM creates a consent request, the subject authenticates via an OIDC provider, and the CM issues a signed artefact and receipt. Includes revocation and expiry.

## Design principles

* **Delegated consent.** Data-holding services never interpret consent semantics; they enforce a decision.
* **Partner-bound policy.** Every partner binding carries an explicit, versioned data-share policy; widening is gated by AWE approval. Consent can never exceed the active policy.
* **Cryptographic proof.** Consent objects are partner-signed (keys sourced from PM); receipts are CM-signed with the CM's own `.p12` key and published via JWKS. Anyone can verify.
* **Data minimisation &amp; purpose limitation.** The CM returns the intersection of what was consented and what policy allows — never more.
* **Append-only audit.** Every decision and state transition is logged immutably for non-repudiation.
* **Standards-aligned.** Built around Kantara/ISO 27560 consent receipts, GDPR data-subject rights, the DEPA / Account-Aggregator artefact model, and DCI + OAuth2/OIDC interoperability.

## How to read this section

{% content-ref url="design/README.md" %}
[README.md](design/README.md)
{% endcontent-ref %}

{% content-ref url="api/README.md" %}
[README.md](api/README.md)
{% endcontent-ref %}
