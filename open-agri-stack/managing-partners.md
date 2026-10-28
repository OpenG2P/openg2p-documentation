---
description: >-
  Step by step for the Exchange operator: onboard a partner, assign and remove
  use cases, give its staff partner-portal accounts, and disable or re-enable
  the partner.
---

# Managing Partners

How the Exchange's operator lets a partner (a bank, an insurer, an agritech) use Agri Stack, and stops it. All partner decisions are made in the **Exchange's** Partner Management (`https://partner-management.<Exchange's base domain>`); the departments never onboard the Exchange's partners. Why it works this way: [Use Cases](architecture/use-cases.md).

## Onboard a partner

1. **Agree terms** with the partner outside the system: the use cases it may use, purposes, data retention.
2. **Onboard it in Partner Management** with its public key and a policy for each use case it is assigned ([Creating and Changing Policies](../platform/platform-services/partner-management/creating-and-changing-policies.md#a-new-partner-with-its-policy)). Its partner ID is its own ID upper-cased with the prefix `PARTNER_` (`bank-a` → `PARTNER_BANK_A`).
3. **Approve** the onboarding request.
4. **Partner-portal accounts** for its staff, if they will collect consents in the portal ([After Install: partner portal realm and users](deployment/after-install.md#partner-portal-users)).

The partner's own steps: [Partner Guide](partner-guide.md).

## Assign or remove a use case

* **Assign another use case:** on the partner's page, **Add policy** → **Use case**, choose it, fill in the limits, submit, approve.
* **Remove a use case:** **Revoke** on that use case's policy, give a reason, approve. The partner's requests and consents for that use case are refused from then on; its other use cases are unaffected.

Steps and fields: [Creating and Changing Policies](../platform/platform-services/partner-management/creating-and-changing-policies.md).

## Disable a partner

To stop a partner altogether, for example when its agreement ends:

1. **Disable it in Partner Management:** the partner's page → **Disable** ([Disabling and Enabling a Partner](../platform/platform-services/partner-management/disabling-a-partner.md)).
2. **Disable its staff's partner-portal accounts** in Keycloak (realm `partner` → **Users** → each `<partner>-…` user → turn **Enabled** off). Disabling the partner already stops their requests from going anywhere, but this also stops them logging in.

What happens once it is disabled:

| Where | Effect |
| --- | --- |
| Composite | Refuses the partner's queries: its key and its use-case policies are no longer served |
| Exchange Consent Manager | Accepts no consent for it: no consent tokens are issued, and the partner portal offers it no use case |
| Registries | Receive nothing on its behalf; a partner that also called a registry directly is refused by that registry's own Partner Management only if it was disabled there too |
| Its consents | Stay recorded, but can no longer be used |

This takes effect once the services' caches expire: within about a minute for policies and five minutes for keys (longer only while Partner Management itself is down).

## Enable it again

The partner's page → **Enable**, and re-enable its portal accounts in Keycloak. Its keys, use cases and unexpired consents work again as they were.
