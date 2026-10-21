---
description: >-
  Step by step in the Partner Management staff portal: give a partner an access
  policy (scope or use-case), change, widen or revoke it, approve the request,
  and check that PM serves it.
---

# Creating and Changing Policies

How a partner manager gives a partner an access policy and changes it later, in the Partner Management staff portal (`https://partner-management.<base domain>`, role `partner_manager`). What a policy is, its fields and the rules PM applies: [Access policies](functional-specifications.md#access-policies).

Before you start, know:

* **The partner's PM ID:** the partner's ID upper-cased, `-` replaced by `_`, prefixed `PARTNER_` (`bank-a` → `PARTNER_BANK_A`).
* **The kind of policy** and what it grants:
  * **Scope policy:** the registry's data controller ID and the scopes from that registry's data scope catalogue.
  * **Use-case policy:** the use cases, each as `name@major`, from the service that publishes them (e.g. an Exchange's Composite).
* **The limits:** purposes, subject ID types, signing algorithms (the partner's key type), longest consent validity, fetch type.

## A new partner, with its policy

1. **Onboard partner** (top menu): fill in the partner (Partner ID, Name, Organisation), its public key, and the **Reason for onboarding**.
2. Under **Policies (optional)**, click **+ Add policy**:
   * **Policy for:** **Data controller (registry)** for a scope policy, then **Data controller** and **Allowed scopes**; or **Use cases (exchange)**, then **Allowed use cases** (`name@major`).
   * **Purposes**, **Subject ID types**, **Signing algorithms**, **Max consent validity**, **Fetch type** (and **Max fetch frequency**, **Data life** if needed).

   Add one policy per registry (and at most one use-case policy).
3. **Submit request.** The keys and policies wait as `pending` until the request is approved.
4. [Approve the request](#approve-or-reject).

## An existing partner: add, change or revoke

The partner must be `active` (its onboarding approved; a disabled partner is enabled first).

1. **Partners**, open the partner, click **Change policy**.
2. Under **New policy versions**, add a policy for a data controller (or the use-case policy). Proposing one for a data controller that already has a policy creates its next version, replacing it on approval: enter the **whole** policy, not only what is new. To widen, keep everything the active version has and add to it.
3. To withdraw a policy, tick **Revoke** on it. A policy cannot be both changed and revoked in one request.
4. Give a **Description** (why it is changing) and **Submit request.**
5. [Approve the request](#approve-or-reject).

A data controller with a change already waiting cannot get another (`PM-POLICY-409`): approve or reject the open request first.

## Approve or reject

1. **Requests**, open the request. It shows the proposed keys, policies and revocations.
2. Check them against what was agreed with the partner (and, for a scope policy, with the registry's data owner).
3. **Approve** or **Reject**, with notes.

On approval each proposed policy becomes `active` (the previous version `superseded`) and each revoked one `revoked`; on rejection the proposed versions become `rejected`. Every step is in the partner's **History**.

## Check

* **In the portal:** the partner's page lists its **Active policies**; **Show policy version history** shows every version, its status and request.
* **What modules read:** PM's partner API, from inside the cluster (it has no login and is not public):

```bash
curl -s "http://commons-services-pm-partner-api/policies/PARTNER_BANK_A?data_controller=farmer-registry"   # a scope policy
curl -s "http://commons-services-pm-partner-api/policies/PARTNER_BANK_A?data_controller="                  # the use-case policy
```

A `404` (`PM-POLICY-404`) means no active policy (or the partner is not active). Modules cache policies for up to a minute, so a change reaches them within about a minute ([Integration](integration.md#6-consuming-access-policies)).

## By API

The same requests can be raised and approved with PM's staff API (a Keycloak token with the `partner_manager` role): `POST /partners/requests/onboarding` with `policies`, `POST /partners/requests/policy`, then `POST /partners/requests/{id}/approve`. Bodies and errors: [API Reference](api-reference.md).
