---
description: >-
  Step by step in the Partner Management staff portal: give a partner an access
  policy (registry or use case), edit, widen or revoke it, approve the request,
  and check that PM serves it.
---

# Creating and Changing Policies

How a partner manager gives a partner an access policy and changes it later, in the Partner Management staff portal (`https://partner-management.<base domain>`, role `partner_manager`). What a policy is and the rules PM applies: [Access policies](functional-specifications.md#access-policies).

The partner's PM ID is its ID upper-cased, `-` replaced by `_`, prefixed `PARTNER_` (`bank-a` → `PARTNER_BANK_A`).

## Filling in a policy

| Field | Enter | Empty means | Checked by |
| --- | --- | --- | --- |
| **Policy for** | **Registry** for a scope policy (a partner of one registry); **Use case** for one use case of an Exchange (one policy per use case) | — | — |
| **Registry** | Not free text: the registry's **Consent Data Controller** setting, exactly (e.g. `farmer-registry`), which is also the prefix of its scope IDs. A mismatch means the policy is never found and every request is denied | Not allowed (scope policy) | — |
| **Allowed scopes** | Full scope IDs from the registry's catalogue, e.g. `farmer-registry.land`: listed on the registry's **Data Scopes** page (e.g. [Farmer Registry](../../../products/registry/farmer-registry/data-scopes.md), [Crop Sown Registry](../../../products/registry/crop-sown-registry/data-scopes.md)), or read live from its partner API. Only these can ever be released, whatever the consent says | Not allowed | The registry's Consent Manager |
| **Use case** | A published use case as `name@major`, e.g. `loan-profile@1`. A new major version needs its own policy | Not allowed | The Exchange's Composite and Consent Manager |
| **Purposes** | The codes the partner may give as a consent's purpose (`purpose.code`). When configured, a checklist of the country's code list `CONSENT_PURPOSE` in the Master Data Service; otherwise free text agreed with the partner, e.g. `credit-assessment`. A use-case policy needs its use case's purpose (shown under the selected use case) | Any purpose | Consent Manager |
| **Subject ID types** | The ID types the partner's consents may name the person by (`subject_id.type`). When configured, a checklist of the country's code list `SUBJECT_ID_TYPE` in the Master Data Service; otherwise free text, spelt as the registries and partners use them, e.g. `FAYDA_FAN`, `FARMER_ID` in Agri Stack | Any type | Consent Manager |
| **Signing algorithms** | Pre-filled from the partner's keys (its active keys, or on onboarding the keys entered above): EC P-256 → `ES256`, Ed25519 → `EdDSA`, RSA → `RS256`. Add a second one only while the partner moves to a key of another type; one with no key is accepted with a warning | Not allowed | Consent Manager (a consent signed otherwise is refused) |
| **Max consent validity** | ISO-8601 duration, e.g. `P90D`, `P1Y` | No limit | Consent Manager |
| **Fetch type** | `oneshot` (one query per consent) or `periodic` (repeated queries under one consent) | `oneshot` | Recorded on the consent |
| **Max fetch frequency** | For `periodic`, ISO-8601, e.g. `P1D` | — | Recorded only |
| **Data life** | How long the partner may keep the data, ISO-8601, e.g. `P30D` | — | Recorded only (a contractual term) |
| **May present its own signed consents** | Tick only for a partner that collects consent in its own trusted system: the Consent Manager then accepts consents the partner signed itself. It cannot verify the person agreed, only the partner's signature | Off: the partner uses consents held by the Consent Manager | Consent Manager (a partner-signed consent is refused when off) |

"Recorded" fields are kept with the policy and the consent for audit; no module enforces them yet.

If the deployment has [catalogue sources](functional-specifications.md#catalogue-sources), **Registry** and **Use case** are lists of the configured registries and the exchange's published use cases (**Other…** for any other), **Allowed scopes** a checklist of the registry's scopes, and **Set purposes from selected use case** fills **Purposes**. If a source (or the Master Data Service) cannot be read, its error is shown and the field is free text; the request then carries a warning for the approver. A code list the country does not have is free text, without a warning.

## A new partner, with its policy

1. **Onboard partner** (top menu): fill in the partner (Partner ID, Name, Organisation), its public key, and the **Reason for onboarding**.
2. Under **Policies (optional)**, click **+ Add policy** for each policy and [fill it in](#filling-in-a-policy): any mix, one per registry and one per use case.
3. **Submit request.** The keys and policies wait as `pending` until the request is approved.
4. [Approve the request](#approve-or-reject).

## An existing partner: add, edit or revoke

The partner must be `active` (its onboarding approved; a disabled partner is enabled first). Open it from **Partners**: **Policies** lists one row per policy (*Registry: …* or *Use case: …*) with its version, status and summary. Each action raises a policy request for one policy, applied when [approved](#approve-or-reject).

* **Add policy** — choose **Registry** or **Use case**, [fill it in](#filling-in-a-policy), give a **Description** and **Submit request.** To let a partner use another use case, add a **Use case** policy for it.
* **Edit** (on a row) — the form opens with the active version; change it and submit. The result is the policy's next version and replaces it whole, so to widen keep what is there and add to it.
* **Revoke** (on a row) — give a reason and click **Raise revoke request**.

A policy with a request waiting shows **Change pending** (a link to it) instead of **Edit** / **Revoke**; another change to it is refused (`PM-POLICY-409`) until that request is approved or rejected. Other policies are not blocked.

## Approve or reject

1. **Requests**, open the request. It shows the proposed keys, and the policies and revocations by registry or use case.
2. Check them against what was agreed with the partner (and, for a scope policy, with the registry's data owner).
3. **Approve** or **Reject**, with notes.

On approval each proposed policy becomes `active` (the previous version `superseded`) and each revoked one `revoked`; on rejection the proposed versions become `rejected`. Every step is in the partner's **History**.

## Check

* **In the portal:** the partner's page lists its **Policies**; **Show policy version history** shows every earlier version, its status and request.
* **What modules read:** PM's partner API, from inside the cluster (it has no login and is not public):

```bash
curl -s "http://commons-services-pm-partner-api/policies/PARTNER_BANK_A?data_controller=farmer-registry"   # a scope policy
curl -s "http://commons-services-pm-partner-api/policies/PARTNER_BANK_A?use_case=loan-profile@1"           # a use-case policy
curl -s "http://commons-services-pm-partner-api/policies/PARTNER_BANK_A"                                   # all of them
```

A `404` (`PM-POLICY-404`) means no active policy (or the partner is not active). Modules cache policies for up to a minute, so a change reaches them within about a minute ([Integration](integration.md#6-consuming-access-policies)).

## By API

The same requests can be raised and approved with PM's staff API (a Keycloak token with the `partner_manager` role): `POST /partners/requests/onboarding` with `policies`, `POST /partners/requests/policy`, then `POST /partners/requests/{id}/approve`. Bodies and errors: [API Reference](api-reference.md).
