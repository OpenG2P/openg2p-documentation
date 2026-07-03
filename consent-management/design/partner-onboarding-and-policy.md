---
description: >-
  How a partner is bound to a controller inside the Consent Manager, and how the
  per-binding data-share policy is modelled, versioned, approved, and evaluated.
---

# Partner policy binding &amp; approval

Inside the Consent Manager (CM) a **partner is a thin policy binding**, not an identity record.
Partner **identity, organisation, lifecycle, and signing keys now live in the Partner Management
(PM) service** — CM neither onboards partners nor stores their keys. What CM owns is the
**authorization/consent domain**: which controller a partner is bound to, and the **data-share
policy** that caps everything that partner can ever be granted.

{% hint style="info" %}
Partner identity and key management moved out of CM in 2026-07. For how CM resolves a partner
against PM and fetches verifying keys, see
[Partner Management Integration](partner-management-integration.md).
{% endhint %}

## The policy binding

A CM `partner` row is a **binding** = a PM partner tied to one controller, carrying the policy
that governs data sharing under that controller:

| Field | Meaning |
| --- | --- |
| `partner_mgmt_id` | Reference to the authoritative partner in the Partner Management service |
| `controller_id` | The **module** the binding is scoped to (e.g. farmer registry, social registry). A consent object's `data_controller` is validated against this |
| `audience` | The `audience` identifier the partner uses in its consent objects |
| `name` | Optional, non-authoritative **display label** only (the real identity lives in PM) |
| `status` | Whether this binding is active; the verification hot path only serves `active` bindings |

One shared CM serves **several controllers**. The **same PM partner may be bound per-controller**
with a different policy under each — a partner that needs data from two modules has two CM
bindings, one per `controller_id`, each with its own policy. A consent issued for one module can
never authorise data from another.

{% hint style="warning" %}
CM does **not** store partner public keys, `jwks_url`, or run any partner onboarding/approval flow.
Those are PM's responsibility. CM stores only the binding above plus its data-share policy.
{% endhint %}

## Policy model

The policy is the enforceable contract and stays in CM. It is **versioned** — each change creates a
new version; prior versions are retained, and every decision records the `policy_version` it was
evaluated against. Effective fields on any decision are always `consent scope ∩ policy`.

| Dimension | Meaning | Enforced in validation |
| --- | --- | --- |
| `allowed_data_scopes` | The maximal set of fields/registers this partner may ever receive | `data_scopes ⊆ allowed_data_scopes`; effective = intersection |
| `allowed_purposes` | Purpose codes the partner may assert | checked per request |
| `allowed_subject_id_types` | Which subject identifier types are acceptable | checked per request |
| `allowed_signing_algs` | Acceptable JWS algorithms (reject weak/`none`) | at signature verify |
| `max_validity_duration` | Upper bound (ISO-8601 duration) on `valid_until − valid_from` | at validity check |
| `fetch_type` | `oneshot` or `periodic` (DEPA-style recurring access) | recorded on artefact |
| `max_fetch_frequency` | For `periodic`, the minimum interval between fetches | enforced per fetch |
| `data_life` | Retention the partner may keep data for after fetch | recorded on receipt |

### Example policy

```json
{
  "version": 3,
  "status": "active",
  "allowed_data_scopes": ["farmer_profile.basic", "farmer_profile.crops"],
  "allowed_purposes": ["share_farm_profile", "subsidy_eligibility"],
  "allowed_subject_id_types": ["national_id", "farmer_id"],
  "allowed_signing_algs": ["EdDSA", "ES256"],
  "max_validity_duration": "P1Y",
  "fetch_type": "oneshot",
  "max_fetch_frequency": null,
  "data_life": "P30D",
  "effective_from": "2025-04-01T00:00:00Z"
}
```

A partner presenting a consent object for `farmer_profile.landholdings`, or with a two-year
validity, is partially or fully denied — the policy caps it regardless of what the subject
"consented" to in the object.

## Policy versions &amp; approval

Because a policy is a ceiling on what a partner may receive, **widening** it is a governance event.
CM integrates the shared, per-environment **Approval Workflow Engine (AWE)** so that a policy that
grants **more** access does not take effect until it has been approved.

* A change that **widens** the policy — a larger allowed set (scopes, purposes, subject-id types, or
  signing algs), or a longer `max_validity_duration` / `data_life`; the **first policy counts as
  widening** — creates a new `PartnerPolicy` version in status `pending` and submits an approval
  request to AWE. The prior `active` version **stays in force** until AWE approves.
* A pure **narrowing** change (a strictly smaller/shorter policy), or when AWE is disabled,
  **activates immediately** and supersedes the prior version.

{% hint style="info" %}
The **verification hot path only ever uses the `active` policy version**, so a `pending` version
never affects live decisions. See
[Verification &amp; enforcement](verification-and-enforcement.md).
{% endhint %}

The end-to-end approval flow (submit → approver acts in CM's own UI → terminal webhook →
activate/reject), the two-policies distinction, the approver proxy/inbox model, and the config keys
are documented on their own page:

{% content-ref url="approval-workflow-integration.md" %}
[approval-workflow-integration.md](approval-workflow-integration.md)
{% endcontent-ref %}

## Policy as a decision function

Evaluation is **deterministic and side-effect-free** (logging aside): given a consent object, the
active policy version, and the request context, it always yields the same decision. This keeps it
testable and auditable, and lets enforcement points reason about outcomes.

```
decide(consent_object, active_policy, request_context) -> {
  decision: permit | deny,
  effective_data_scopes: requested ∩ consented ∩ policy.allowed_data_scopes,
  reason_code,
  policy_version
}
```

## Consent templates (optional)

To standardise common partnerships, a controller can define **consent templates** — named bundles
of purpose + scopes + validity that align with a partner policy. Templates make origination flows
consistent and give subjects predictable, comparable consent prompts. See
[Standards &amp; best practices](standards-and-best-practices.md).
