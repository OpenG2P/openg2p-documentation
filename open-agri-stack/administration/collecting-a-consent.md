---
description: Recording a farmer's consent.
---

# Collecting a Consent

Records a farmer's consent for a use case in the Exchange's Consent Manager, collected in person by a partner's staff. Once approved, the partner queries the Composite for that farmer without sending a consent. Why consents work this way: [Consent](../architecture/consent.md) and [consent collection](../../consent-management/design/consent-collection.md).

**Needs:** the partner onboarded with a policy for the use case ([Managing Partners](managing-partners.md)), and a partner portal account for the staff member ([partner portal accounts](managing-partners.md#partner-portal-accounts)).

## Partner staff: record the consent

In the partner portal (`https://consent-partner-portal.<Exchange domain>`), logged in with the partner portal account:

1. **Consents → New consent**, choose the use case.
2. Enter the farmer's national ID and, if known (or required by the install), the Farmer ID (`946053125409`, `FR-0007` in the sample data).
3. **Authenticate with national ID**: the farmer logs in with eSignet in the popup.
4. **Upload the signed paper form:** the farmer signs the printed consent form by hand; scan or photograph it and upload the file. **Submit**.

## Consent Approver: approve it

In the Exchange's CM console (`https://consent-manager.<Exchange domain>`), **Consent Approvals**: check the request, the scanned form and the national-ID login, **Approve**. The consent is then active.

## Check

The consent shows as active in the CM console, and under **Consents** in the partner portal. The partner's queries for that farmer and use case now use it, without sending a consent. Trying it with the test script: [Testing](../deployment/testing.md).
