---
description: Managing partner portal accounts.
---

# Partner Portal Users

Partner staff who collect farmers' consents log in to the partner portal (`https://consent-partner-portal.<Exchange domain>`) through the Keycloak realm `partner` of the Exchange. The install creates the realm, its client `consent-partner-portal`, the roles and the `partner_id` attribute; each account is created by hand. A partner needs accounts only if its staff collect consents in the portal.

## Create an account

In Keycloak (`https://keycloak.<Exchange domain>`), realm **partner**:

1. **Users → Add user**: a username (e.g. `bank-a-operator`), the user's **Email**, **First name** and **Last name** (Keycloak requires them: left empty, the user must fill them in at first login), **Email verified** on. In the attribute **Partner ID** (`partner_id`), the partner's ID as it signs requests: `bank-a`, not `PARTNER_BANK_A`. **Create**.
2. **Credentials → Set password**: a password the user changes at first login (**Temporary** on).
3. **Role mapping → Assign role → Filter by clients**: `consent-partner-portal` **PARTNER_OPERATOR** (or **PARTNER_ADMIN**; the Consent Manager treats them alike today).

The portal then offers the user only the use cases granted to that partner in Partner Management ([Managing Partners](managing-partners.md)).

{% hint style="info" %}
Without the **Partner ID** attribute, or with a role from another client, the user can log in but every request is refused.
{% endhint %}

## Disable or remove an account

* **Disable:** the user → **Enabled** off. Do this for all of a partner's users when the partner is disabled ([Managing Partners: disable a partner](managing-partners.md#disable-a-partner)).
* **Remove:** the user → **Action → Delete**. The consents the user collected stay with the partner.
