---
description: >-
  Step by step in the Partner Management staff portal: disable a partner so
  that every service refuses it, re-enable it, and what happens in between.
---

# Disabling and Enabling a Partner

How a partner manager stops a partner from using any service, and lets it back in, in the Partner Management staff portal (`https://partner-management.<base domain>`, role `partner_manager`). The partner statuses: [Partner status](functional-specifications.md#partner-status).

## Disable

1. **Partners**, open the partner.
2. Click **Disable**.

The partner's status becomes `disabled`. Nothing is deleted: its keys, policies and history stay, and the change is recorded in its **History** (`partner.disabled`).

## What happens

Partner Management stops serving the partner's keys and policies: its key and policy APIs answer "not found", exactly as for an unknown partner. Every service that relies on them then refuses the partner:

* its signed requests no longer verify;
* every policy check fails, so no consent is accepted and no data is released for it.

Services cache keys and policies, so the refusal applies once their caches expire: within about a minute for policies and five minutes for keys, or up to the hard TTL (six hours by default) while Partner Management itself is unreachable ([Integration](integration.md#6-consuming-access-policies)).

To stop one use case or one registry only, revoke that policy instead ([Creating and Changing Policies](creating-and-changing-policies.md#an-existing-partner-add-edit-or-revoke)).

## Enable again

1. **Partners**, open the partner.
2. Click **Enable**.

The partner is `active` again with the keys and policies it had; services accept it once their caches refresh. Recorded as `partner.enabled`.

## By API

`POST /partners/{partner_id}/disable` and `POST /partners/{partner_id}/enable` on the staff API (a token with the `partner_manager` role): [API Reference](api-reference.md).
