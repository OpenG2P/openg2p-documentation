---
description: Where partner staff collect consent.
---

# Partner Portal

The **partner portal** is a web app where a partner's staff (e.g. at a bank branch) collect a subject's consent, follow their requests and download proof of each consent. Most partners will not build their own consent screens, so it is the main way in. It is a front end over the Consent Manager's partner portal API ([API Reference](api/README.md#partner-portal-endpoints)), at `https://consent-partner-portal.<baseDomain>`.

## How a consent is collected

1. Partner staff raise a request (**New consent**): the subject, the purpose (at an Exchange, the use case) and the period.
2. The subject logs in with their national ID on the spot ([national ID authentication](design/consent-collection.md#national-id-authentication-in-the-partner-portal)) and signs the paper consent form by hand; staff scan it, upload the scan and submit.
3. The **Consent Approver** checks the request, the form and the national-ID login in the CM console (**Consent Approvals**), and approves or rejects it.
4. Once approved, the consent is active; the partner downloads its receipt and its consent record.

The scenarios and their rules: [consent collection](design/consent-collection.md).

## Tabs

* **Consents** (the home page): **New consent** raises a consent request (scenario 1): start the subject's national-ID login, upload the signed form, submit; a request can be cancelled until it is decided. Requests not yet decided are listed first (**In progress**), then the consents, with their scopes, validity, assurance and status (active, revoked, expired); each consent's receipt and [consent record](design/consent-collection.md#the-partners-copy-of-a-consent) can be downloaded.
* **Use cases** (read-only, for information): what the partner may ask consent for, read from Partner Management. At an Exchange, its use cases ([below](#at-an-exchange)); elsewhere the tab is **Data access**, its scope policies per registry.
* **History:** every request the partner raised and what became of it: approved (with its consent), rejected with the reason, cancelled.
* **Not in the portal:** policies and keys (requested and approved in Partner Management), the approval of requests (the Consent Approver, in the CM console), and partner users (see [Users and sign-in](#users-and-sign-in)).

## At an Exchange

At an Exchange CM (a CM in the [exchange role](design/exchange-consent-tokens.md)), partners are granted use cases, not registry scopes, so the portal works **by use case**. The partner has one policy per use case in Partner Management. **Use cases** lists one entry per such policy: the use case with its purpose and data per registry (read from the Composite) and the policy's purposes, subject ID types and longest validity. A new request must name one of them (a request naming registries and scopes is refused; a use case without a policy is refused `use_case_not_granted`): its purpose and grants are the use case's, and that use case's policy limits apply. The Consent Approver's approval narrows the consent to the use case's scopes at that time, and the consent records the use case: the Composite can use it for that use case only. The partner need not keep the consent ID: a request to the Composite may carry no consent, and the Exchange CM finds it ([consent by lookup](design/verification-and-enforcement.md#use-case-mode)). If the Composite cannot be reached, no such request can be raised or approved (fail closed).

## Purposes and subject ID types

The portal offers purposes and subject ID types from the country's **Master Data** code lists (by default `CONSENT_PURPOSE` and `SUBJECT_ID_TYPE`), the lists Partner Management uses in policies, so a request and its policy use the same codes. The CM reads them with its own service account and caches them; the portal gets them from `GET /consent/v1/partner-portal/request-settings`. Settings: [Deployment](deployment/README.md#master-data-code-lists).

* **List loaded:** the form offers a dropdown, and a request naming a value outside the list is refused (`400`). At an Exchange only the subject ID type is checked; the purpose is the use case's.
* **No list** (not in the country's Master Data, Master Data unreachable, or not configured): free text, and requests are accepted. Master Data never blocks a request.

The partner's policy still limits both (an empty allowed list in the policy means any value).

**Ownership:** requests, authentication records, uploaded files (in the CM's object-store bucket), verification and the consent belong to the CM. Partner Management needs no partner-facing UI.

## Users and sign-in

Partner staff sign in through the Keycloak realm `partner`. The install creates the realm, the client `consent-partner-portal`, its roles `PARTNER_OPERATOR` and `PARTNER_ADMIN` (the CM treats them alike) and the `partner_id` attribute; each user is created by hand, with the partner's ID in `partner_id`. Setup: [Deployment](deployment/README.md#partner-portal-and-consent-evidence-optional); step by step in Agri Stack: [Managing Partners: partner portal accounts](../open-agri-stack/administration/managing-partners.md#partner-portal-accounts).
