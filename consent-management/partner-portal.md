---
description: Where partner staff collect consent.
---

# Partner Portal

The **partner portal** is a web app where a partner's staff (e.g. at a bank branch) collect a subject's consent, follow their requests and download proof of each consent. Most partners will not build their own consent screens, so it is the main way in. It is a front end over the Consent Manager's partner portal API ([API Reference](api/README.md#partner-portal-endpoints)), at `https://consent-partner-portal.<baseDomain>`.

## How a consent is collected

1. Partner staff raise a request (**New consent**): the subject, the purpose (at an Exchange, the consent template) and the period.
2. The subject logs in with their national ID on the spot ([national ID authentication](design/consent-collection.md#national-id-authentication-in-the-partner-portal)) and signs the paper consent form by hand; staff scan it, upload the scan and submit.
3. The **Consent Approver** checks the request, the form and the national-ID login in the CM console (**Consent Approvals**), and approves or rejects it.
4. Once approved, the consent is active; the partner downloads its receipt and its consent record.

The scenarios and their rules: [consent collection](design/consent-collection.md).

## Tabs

* **Consents** (the home page): **New consent** raises a consent request (scenario 1): start the subject's national-ID login, upload the signed form, submit; a request can be cancelled until it is decided. Requests not yet decided are listed first (**In progress**), then the consents, with their scopes, validity, assurance and status (active, revoked, expired); each consent's receipt and [consent record](design/consent-collection.md#the-partners-copy-of-a-consent) can be downloaded. The list shows only consents collected through the CM (portal or origination API). A consent the partner signed itself and sent with a request (`consent_jws`) is stored in the CM too, but not listed here: CM staff see its use in the console's **Access Log** (role `CONSENT_MANAGER_ADMIN`), and open it from there.
* **Consent templates** (read-only, for information, at `/templates`): what the partner may ask consent for. At an Exchange, the consent templates offered to it ([below](#at-an-exchange)); elsewhere the tab is **Data access**, its scope policies per registry, read from Partner Management.
* **History:** every request the partner raised and what became of it: approved (with its consent), rejected with the reason, cancelled.
* **Not in the portal:** policies and keys (requested and approved in Partner Management), the approval of requests (the Consent Approver, in the CM console), and partner users (see [Users and sign-in](#users-and-sign-in)).

## At an Exchange

At an Exchange CM (a CM in the [exchange role](design/exchange-consent-tokens.md)), the portal works **by consent template**. A consent template is a code, a title, a purpose, the scopes per registry (required and optional) and limits (subject ID types, longest validity, partner-signed consents allowed). The CM reads the templates offered to the partner from a **template source** set at install; at the Agri Stack Exchange that is the Composite, which publishes each use case granted to the partner as a template ([Consent](../open-agri-stack/architecture/consent.md#consent-templates)).

| Step | What happens |
| --- | --- |
| **Consent templates** tab | Lists the templates offered to the partner, with purpose, scopes per registry and limits. A template that names no scopes shows as unavailable. |
| New request | Names one template. The consent takes its purpose and scopes per registry; staff may leave out optional scopes (required ones stay). The template's longest validity is the default validity and the ceiling; its subject ID types apply. A template not offered to the partner: `422 template_not_offered`. A request naming registries and scopes without a template: `400`. |
| Approval | The Consent Approver's approval narrows the consent to the template's scopes at that time (the template must still be offered). |
| The consent | Records the purpose and the scopes per registry. The template code is kept as a label. The consent is used through the Composite, not by a direct call by registry. |
| Use | The Composite presents the consent for any use case with the same purpose. The partner need not keep the consent ID: a request to the Composite may carry no consent, and the Exchange CM finds the partner's most recent active consent for the subject and purpose ([consent by lookup](design/verification-and-enforcement.md#caller-terms-mode)). |
| Source down | No request can be raised or approved (`503`, fail closed). |

## Purposes and subject ID types

The portal offers purposes and subject ID types from the country's **Master Data** datasets (by default `CONSENT_PURPOSE` and `SUBJECT_ID_TYPE`), the lists Partner Management uses in policies, so a request and its policy use the same codes. The CM reads them with its own service account and caches them; the portal gets them from `GET /consent/v1/partner-portal/request-settings`. Settings: [Deployment](deployment/README.md#master-data-datasets).

* **List loaded:** the form offers a dropdown, and a request naming a value outside the list is refused (`400`). At an Exchange only the subject ID type is checked; the purpose is the template's.
* **No list** (not in the country's Master Data, Master Data unreachable, or not configured): free text, and requests are accepted. Master Data never blocks a request.

The partner's policy still limits both (an empty allowed list in the policy means any value). At an Exchange the template's limits apply instead.

**Ownership:** requests, authentication records, uploaded files (in the CM's object-store bucket), verification and the consent belong to the CM. Partner Management needs no partner-facing UI.

## Users and sign-in

Partner staff sign in through the Keycloak realm `partner`. The install creates the realm, the client `consent-partner-portal`, its roles `PARTNER_OPERATOR` and `PARTNER_ADMIN` (the CM treats them alike) and the `partner_id` attribute; each user is created by hand, with the partner's ID in `partner_id`. Setup: [Deployment](deployment/README.md#partner-portal-and-consent-evidence-optional); step by step in Agri Stack: [Managing Partners: partner portal accounts](../open-agri-stack/administration/managing-partners.md#partner-portal-accounts).
