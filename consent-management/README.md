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

The CM owns **consent only**. Partners and what they may ask for live elsewhere:

* **Partner Management (PM) owns partners, their signing keys and their access policies.** A policy caps what a partner may ever receive (data scopes per registry, or use cases at an Exchange; purposes, validity, …); onboarding, key and policy changes are requested and approved in PM. At verification time the CM **reads the partner's policy and public key from PM** (cached) and verifies the consent object's signature locally. See [Partner Management integration](design/partner-management-integration.md).
* **The CM owns consents, the PDP decision, receipts and consent tokens.** Receipts are signed with the CM's own `.p12` key and published at `/.well-known/jwks.json` (self-verifying — the CM is **not** a PM partner).
* **API-audience split.** The CM follows the platform's 4-API audience pattern — **staff** (console: decision log, verification of assisted consents; partner portal API), **partner** (the PDP `/validate`, no Keycloak — called by registries and the Composite inside the cluster over mTLS), and **beneficiary** (subject self-service).

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

A partner calls a registry API about a person. The registry asks the CM whether it may answer, passing the consent the partner names: a consent the CM holds (by `consent_id`), **none** (the CM then finds the partner's consent for that person and registry), or a consent object the partner collected and **signed itself** (accepted only if the partner's policy allows it). The CM:

1. finds the consent; for a partner-signed one, verifies its signature against the partner's public key **fetched from Partner Management** (**known-party** check),
2. evaluates the consent's grant **for that registry** against the partner's **access policy for that registry** in Partner Management (allowed scopes, purpose, validity),
3. checks it is **not revoked or expired**, and
4. returns a **decision** containing the **effective data scopes** the registry may release (`grant ∩ partner policy`) and the consent's subject, which the registry checks against what it searches.

One consent can cover **several registries**: the partner asks the subject once and lists a grant per registry (`grants: [{data_controller, data_scopes}]`); each registry validates only its own grant and gets its own receipt. The earlier single-registry consent (`data_controller` + `data_scopes`) still works.

The registry releases only those fields. The CM persists a canonical artefact, a signed receipt, and an immutable decision log.

### 2. Originate — _secondary_

For first-party flows where consent is collected through OpenG2P itself: the CM creates a consent request, the subject authenticates via an OIDC provider, and the CM issues a signed artefact and receipt. Includes revocation and expiry.

## Design principles

* **Delegated consent.** Data-holding services never interpret consent semantics; they enforce a decision.
* **Policy-bound consent.** Every partner has an explicit, versioned access policy in Partner Management (one per registry, or one per use case at an Exchange), changed only through approval there. Consent can never exceed the active policy.
* **Cryptographic proof.** Consents are signed — by the CM, or by the partner for a consent it collected itself (keys sourced from PM); receipts are CM-signed with the CM's own `.p12` key and published via JWKS. Anyone can verify.
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
