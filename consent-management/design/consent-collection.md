---
description: >-
  How a partner seeks a subject's consent and how the subject gives it: three
  scenarios (in person, SMS, self-service), what the Consent Manager does today,
  the gaps, and the partner portal.
---

# Consent collection

A partner (e.g. a bank) needs a subject's (e.g. a farmer's) consent before it can receive the subject's data from registries. **Seeking** (the partner asks) and **giving** (the subject agrees) both go through the Consent Manager (CM), so that the consent is evidence the CM holds, not a claim the partner makes.

{% hint style="info" %}
**Roles, as everywhere in OpenG2P:** *staff* (government users), *agents* (government field users), *partners* (organisations such as banks, onboarded in Partner Management), *beneficiaries* (subjects, e.g. farmers). A partner's own employees using the partner portal are **partner users**.
{% endhint %}

## Principle

**The subject's confirmation happens at the CM, or through a channel the CM verifies, never on the partner's word.** The CM records how the subject confirmed (the **assurance**), and a policy can demand a minimum assurance for a purpose.

## Scenarios

### 1. In person, assisted (subject at the partner's office, or the partner's user in the field)

1. A partner user creates the consent request in the partner portal: the use case (or purpose and registries), the subject's ID, the validity.
2. The subject is authenticated on the spot through national ID (e.g. Fayda): OTP to the phone registered with the ID, or biometrics. The CM records the authentication (provider, method, time).
3. The subject signs a consent form; the partner user uploads it as evidence.
4. Staff check the uploaded form (it matches the subject and the request) and verify it. Only then is the consent active.

### 2. Confirmation by SMS or USSD

As scenario 1, but instead of (or as well as) the signed form, the CM sends the subject an SMS ("Bank X asks to see … — reply YES to agree") or a USSD prompt; the subject replies to a trusted number. The reply approves the request with no staff step. **The phone number must be the subject's own**, taken from the national ID or the registry, never from the partner.

### 3. Self-service

The subject logs in to a self-service portal or app (national ID login), sees the pending request (who asks, for what, which data from which registry), and approves (all or part) or declines. The same place lists the subject's consents and lets them revoke any.

## What the CM has today

| Capability | Status |
| --- | --- |
| Consent request (subject, partner, purpose, grants per registry and scopes, validity) | **Built** (`POST /consent/v1/consent-requests`; staff or service callers) |
| Subject authentication: an OIDC ID token, checked against the identity provider's JWKS; the token's subject must be the request's subject; provider, method (`amr`) and time recorded | **Built** (`…/authenticate`) |
| Approve (per registry) or deny; a consent record (`originated`) with its signed receipt | **Built** |
| Subject's own consents and revocation | **Built** (`/consent/v1/my/…`) |
| Subject-facing pages: a consent request page and "my consents" | **Built**, but they log in through the staff Keycloak, not national ID |
| Partner-signed consent presented in each query, checked at `/validate` | **Built** (the path in use today; see the gap below) |
| **Scenario 1, phase 1:** partner portal and partner realm; requests by partner users, signed-form upload (evidence in object storage), submit, staff verification in the CM console, consents with assurance and receipts; `/validate` by `consent_id` (receipts in an exchange deployment); the composite accepts `message.consent_id` | **Built** ([deployment](../deployment/README.md#partner-portal-and-consent-evidence-optional)); phase 2 adds the subject's national-ID authentication (eSignet / Fayda) |

## Gaps

| Gap | Scenarios | Notes |
| --- | --- | --- |
| ~~A consent the subject gave cannot be used in a query~~ | all | **Done** in an exchange deployment (`/validate` with `consent_id` issues registry receipts; registries unchanged). To do: a single install (no exchange CM). |
| **Partner-signed consent proves nothing about the subject.** The CM checks the partner's signature, its policy, the subject in the consent against the subject in the request, validity and replay; nothing shows the subject took part | today's path | Keep it only for partners trusted to collect consent offline, clearly marked, or retire it. |
| **National ID authentication** (OTP, biometrics) for the subject, including assisted authentication on a partner user's device | 1, 3 | e.g. Fayda through eSignet; the CM already verifies an OIDC ID token. |
| ~~Evidence~~ (signed form on a request) | 1 | **Done** (bucket `consent-evidence`). To do: encryption at rest beyond the store's, retention and deletion rules. |
| ~~Staff verification~~ of assisted consents | 1 | **Done** in the CM console (Consent verifications). To do: optionally through an AWE task. |
| **Assurance** on each consent | all | **Recorded** (method, evidence, verifier, whether the subject was authenticated). To do: a minimum assurance per policy. |
| ~~Partner access~~ | 1, 2 | **Done**: partner realm and the partner-portal API. To do: partner user management from the portal (staff create users today), a partner-signed API for partners with their own systems. |
| **SMS / USSD**: sending the prompt, and an inbound webhook that matches the reply to the request | 2 | Through the platform's notification service (Novu) or the national SMS gateway. |
| **Back to the partner**: redirect to the partner's app with the consent ID, or a notification, when the subject approves | 3 | |

## Partner portal

Most partners will not build their own consent screens, so a central **partner portal** is the main way in; partners with their own systems use the same APIs.

* **Consent (backed by the CM):** create a request (pick a use case or purpose, enter the subject's ID, choose how the subject confirms: in person with national ID and an optional signed form, SMS, or a link to self-service); follow requests by status; list consents with their ID, scopes, validity, assurance and status (including revocations by the subject), and download receipts.
* **Their access (read-only):** what the partner may use and the data it returns, and its query history (in Agri Stack, from the use-case composite).
* **Administration:** a partner admin manages the partner's own portal users (roles: *operator*, who creates requests and runs in-person consent; *partner admin*, who also sees all the partner's consents and manages users).
* **Not in the portal:** partner policies, keys (approved in Partner Management by staff; at most shown read-only) and the verification of uploaded forms (staff, in the CM console through AWE).

**Ownership:** the consent logic and its evidence (requests, authentication records, uploaded files, verification, the consent and its revocation) belong to the CM, files in the CM's object store bucket. The portal is a partner-facing front end over the CM's APIs (and, in Agri Stack, the composite's); Partner Management needs no partner-facing UI.

## Order of work

1. Presenting a stored consent by its ID at `/validate` (and receipts from it in an exchange deployment).
2. Scenario 1: partner portal and partner users, request creation, national ID authentication, evidence upload, staff verification, assurance.
3. Scenario 3: national ID login on the subject pages, redirect back to the partner.
4. Scenario 2: SMS / USSD prompts and replies.
