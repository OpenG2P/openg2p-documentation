---
description: Onboarding and managing partners.
---

# Managing Partners

How the Exchange's partner manager lets a partner (a bank, an insurer, an agritech) use Agri Stack, and stops it. All partner decisions are made in the **Exchange's** Partner Management (`https://partner-management.<Exchange's base domain>`); the departments never onboard the Exchange's partners. Why it works this way: [Use Cases](../architecture/use-cases.md).

## Onboard a partner

1. **Agree terms** with the partner outside the system: the use cases it may use, purposes, data retention.
2. **Onboard it in Partner Management** with its public key and a policy for each use case it is assigned ([Creating and Changing Policies](../../platform/platform-services/partner-management/creating-and-changing-policies.md#a-new-partner-with-its-policy)). Its partner ID is its own ID upper-cased with the prefix `PARTNER_` (`bank-a` → `PARTNER_BANK_A`).
3. **Approve** the onboarding request. Partner Management lets the person who raised a request approve it; in production, have another person approve every onboarding, key and policy request.
4. **Partner portal accounts** for its staff, if they will collect consents in the portal ([below](#partner-portal-accounts)).

The partner's own steps: [Partner Guide: Fetching Farmer Data](../partner-integration-guide.md).

## Assign or remove a use case

* **Assign another use case:** on the partner's page, **Add policy** → **Use case**, choose it, fill in the limits, submit, approve.
* **Remove a use case:** **Revoke** on that use case's policy, give a reason, approve. The partner's requests and consents for that use case are refused from then on; its other use cases are unaffected.

Steps and fields: [Creating and Changing Policies](../../platform/platform-services/partner-management/creating-and-changing-policies.md).

## Disable a partner

To stop a partner altogether, for example when its agreement ends:

1. **Disable it in Partner Management:** the partner's page → **Disable** ([Disabling and Enabling a Partner](../../platform/platform-services/partner-management/disabling-a-partner.md)).
2. **Disable its staff's partner portal accounts** ([partner portal accounts](#partner-portal-accounts)). Disabling the partner already stops their requests from going anywhere; this also stops them logging in.

Every service then refuses the partner: the Composite refuses its queries, the Exchange Consent Manager issues no consent tokens for it, and the partner portal offers its staff no use case. Its consents stay recorded but can no longer be used. A partner that also calls a registry directly is refused there only if it is disabled in that department's Partner Management too. This applies once the services' caches expire: within about a minute for policies and five minutes for keys ([what happens](../../platform/platform-services/partner-management/disabling-a-partner.md#what-happens)).

## Enable it again

The partner's page → **Enable**, and re-enable its portal accounts in Keycloak. Its keys, use cases and unexpired consents work again as they were.

## Partner portal accounts

Partner staff who collect farmers' consents log in to the [partner portal](../../consent-management/partner-portal.md) (`https://consent-partner-portal.<Exchange domain>`) with an account in the Exchange's Keycloak, realm `partner`. The install creates the realm, its client and roles and the `partner_id` attribute; each account is created by hand. A partner needs accounts only if its staff collect consents in the portal.

**Create an account.** In Keycloak (`https://keycloak.<Exchange domain>`), realm **partner**:

1. **Users → Add user**: a username (e.g. `bank-a-operator`), the user's **Email**, **First name** and **Last name** (Keycloak requires them: left empty, the user must fill them in at first login), **Email verified** on. In the attribute **Partner ID** (`partner_id`), the partner's ID as it signs requests: `bank-a`, not `PARTNER_BANK_A`. **Create**.
2. **Credentials → Set password**: a password the user changes at first login (**Temporary** on).
3. **Role mapping → Assign role → Filter by clients**: `consent-partner-portal` **PARTNER_OPERATOR** (or **PARTNER_ADMIN**; the Consent Manager treats them alike today).

The portal then offers the user only the use cases assigned to that partner. Without the **Partner ID** attribute, or with a role from another client, the user can log in but every request is refused.

**Disable or remove an account.** The user → **Enabled** off; or **Action → Delete**. The consents the user collected stay with the partner.
