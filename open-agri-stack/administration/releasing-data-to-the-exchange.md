---
description: >-
  For each department: setting what its registry releases to the Exchange
  (the Composite's scope policy in the department's Partner Management), and
  widening or narrowing it when use cases change.
---

# Releasing Data to the Exchange

Each department decides what its registry releases through the Exchange: the Composite's scope policy for the registry, in the department's own Partner Management. Until it exists the registry releases nothing to the Exchange. Why and how it is applied: [Scope policy for the Composite](../architecture/registries.md#scope-policy-for-the-composite) and [Data-Sharing Policies](../architecture/data-sharing-policies.md).

Step 3 of the [install steps](../deployment/README.md#install-steps), and again whenever use cases change. The install has already onboarded the Composite (`PARTNER_AGRI_COMPOSITE`) in the department's Partner Management, with its key and no policy.

## What the Exchange asks for

The Composite lists each published use case and what it reads from each registry:

```bash
curl -s https://agri-composite.<Exchange domain>/composite/v1/use-cases
```

For each use case, `consent_scopes` gives the registry's scopes (`required` and `optional`) and `purpose` its purpose. The policy must cover every use case the department agrees to: the union of their scopes, and their purposes.

## Add the policy

In the department's Partner Management (`https://partner-management.<department domain>`), partner **PARTNER_AGRI_COMPOSITE → Add policy → Data controller**:

| Field | Value |
| --- | --- |
| Data controller | The registry, e.g. `farmer-registry` |
| Data scopes | The scopes the department releases, from those asked for |
| Purposes | The use cases' purposes, e.g. `credit-assessment` |
| Subject ID types | e.g. `FAYDA_FAN`, `FARMER_ID` |
| Signing algorithms | `ES256` (the Composite's generated key) |
| Maximum validity, Fetch type | e.g. `P90D`, `oneshot` |

Submit, then approve the request (another person, in production). One policy per registry the department runs. Portal steps: [Creating and Changing Policies](../../platform/platform-services/partner-management/creating-and-changing-policies.md).

**Check:** `curl -s https://partner-management-partner-api.<department domain>/policies/PARTNER_AGRI_COMPOSITE` lists the policy; a query through the Composite then gets the registry's data ([Testing](../deployment/testing.md)).

## When use cases change

* **A new use case, or one that reads more:** **Edit** the policy to add the scopes and purposes, if the department agrees. Until then the registry leaves out what the policy does not cover, and denies the source if it covers none of what is asked.
* **To release less:** **Edit** the policy to remove scopes. An optional scope then comes back `null` in the answers; a required one fails the source.
* **To stop releasing:** **Revoke** the policy. The registry then denies every query through the Composite.

Changes apply within the services' policy cache time (about a minute).

## A department added later

A department joining an Exchange that is already running installs its registry with **Exchange Role** `department` ([Separate Clusters: adding a department](../deployment/separate-clusters.md#adding-a-department)), then adds this policy.
