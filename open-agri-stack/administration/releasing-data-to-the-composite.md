---
description: What a department's registry releases to the Composite.
---

# Releasing Registry Data to the Composite

Each department decides what its registry releases to the Composite (the Exchange's service that partners query): the Composite's scope policy for the registry, in the department's own Partner Management. Until the department adds it, the registry releases nothing to the Composite. The department owns this policy: the Exchange's operator should hold no Partner Management admin rights in a department. Why and how it is applied: [Scope policy for the Composite](../architecture/data-sharing-policies.md#what-actually-gets-released) and [Data-Sharing Policies](../architecture/data-sharing-policies.md).

Step 3 of the [install steps](../deployment/README.md#install-steps), and again whenever use cases change. Done by the department's partner manager, in the department's Partner Management (`https://partner-management.<department domain>`).

## The Composite's entry

Installing a department with **Exchange Role** `department` (in Commons Services) onboards the Composite as a partner in the department's Partner Management by default:

* partner ID `PARTNER_AGRI_COMPOSITE`;
* its public keys read from the Composite's JWKS URL whenever needed, so no key is entered by hand;
* **no policy**: it releases nothing until you add one below.

The install raises and approves this onboarding itself (actor `bootstrap` in the Partner Management audit). More: [what the install sets up](../deployment/README.md#what-the-install-sets-up). Check it is there:

```bash
curl -s https://partner-management-partner-api.<department domain>/keys/PARTNER_AGRI_COMPOSITE
```

It serves the same `kid` as `https://agri-composite.<Exchange domain>/.well-known/jwks.json`. If the partner is missing (the setting was off, or the entry was removed), onboard it by hand: **Requests → + Onboard partner**:

| Field | Value |
| --- | --- |
| Partner ID | `PARTNER_AGRI_COMPOSITE` |
| Name | e.g. `Agri Stack Composite` |
| Public keys | None |
| JWKS URL | `https://agri-composite.<Exchange domain>/.well-known/jwks.json` |
| Read keys from this JWKS URL whenever they are needed | **On** |
| Policies | None |

**Submit request**, then approve it (another person, in production). If the partner exists but serves no key, Partner Management cannot reach the JWKS URL.

## What the use cases read from the registry

The Composite lists each published use case and the scopes it reads from each registry:

```bash
curl -s https://agri-composite.<Exchange domain>/composite/v1/use-cases
```

For each use case, `consent_scopes` gives the registry's scopes (`required` and `optional`) and `purpose` its purpose. The policy must cover every use case the department agrees to: the union of their scopes, and their purposes.

## Add the policy

Partner **PARTNER_AGRI_COMPOSITE → Add policy → Data controller**:

| Field | Value |
| --- | --- |
| Data controller | The registry, e.g. `farmer-registry` |
| Data scopes | The scopes the department releases, from those asked for |
| Purposes | The use cases' purposes, e.g. `credit-assessment` |
| Subject ID types | e.g. `FAYDA_FAN`, `FARMER_ID` |
| Signing algorithms | `ES256` (the Composite's generated key) |
| Maximum validity, Fetch type | e.g. `P90D`, `oneshot` |

Submit, then have another person approve the request (Partner Management allows the same person; avoid it in production). Review a widening before approving it. One policy per registry the department runs. Portal steps: [Creating and Changing Policies](../../platform/platform-services/partner-management/creating-and-changing-policies.md).

**Check:** `curl -s https://partner-management-partner-api.<department domain>/policies/PARTNER_AGRI_COMPOSITE` lists the policy; a query through the Composite then gets the registry's data ([Testing](../deployment/testing.md)).

## When use cases change

* **A new use case, or one that reads more:** **Edit** the policy to add the scopes and purposes, if the department agrees. Until then the registry leaves out what the policy does not cover, and denies the source if it covers none of what is asked.
* **To release less:** **Edit** the policy to remove scopes. An optional scope then comes back `null` in the answers; a required one fails the source.
* **To stop releasing:** **Revoke** the policy. The registry then denies every query through the Composite.

Changes apply within the services' policy cache time (about a minute).

## A department added later

A department joining an Exchange that is already running installs its registry with **Exchange Role** `department` ([Separate Clusters: adding a department](../deployment/separate-clusters.md#adding-a-department)), then adds this policy.
