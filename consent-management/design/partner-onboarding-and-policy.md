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
| `controller_id` | The **module / registry** the binding is scoped to (e.g. `farmer-registry`, `crop-sown-registry`). A registry validating a consent names its controller, and the consent's grant for it is evaluated against this binding |
| `audience` | The `audience` identifier the partner uses in its consent objects |
| `name` | Optional, non-authoritative **display label** only (the real identity lives in PM) |
| `status` | Whether this binding is active; the verification hot path only serves `active` bindings |

One shared CM serves **several controllers**. The **same PM partner may be bound per-controller**
with a different policy under each — a partner that needs data from two registries has two CM
bindings (same `audience`, one per `controller_id`), each with its own policy. Add a binding with
`POST /partners` using the existing `audience` and a new `controller_id`; the pair is unique, and
all bindings of an audience share one `partner_mgmt_id`. In the admin console, a partner's page
lists its **controller bindings** and can add one; the decisions view shows the controller of each
decision.

The partner can then ask the subject **once**: one consent with a grant per registry. Each
registry validates only its own grant, and a grant is only ever evaluated against the binding (and
policy) for that registry — a grant for one registry never authorises data from another. Existing
single-controller partners were migrated unchanged: their binding is simply the first one.

{% hint style="warning" %}
CM does **not** store partner public keys, `jwks_url`, or run any partner onboarding/approval flow.
Those are PM's responsibility. CM stores only the binding above plus its data-share policy.
{% endhint %}

## Policy model

The policy is the enforceable contract and stays in CM. It is **versioned** — each change creates a
new version; prior versions are retained, and every decision records the `policy_version` it was
evaluated against. Effective fields on any decision are always `grant scope ∩ policy`, using the
grant and the policy of the registry that asked.

| Dimension | Meaning | Allowed values | Enforced in validation |
| --- | --- | --- | --- |
| `allowed_data_scopes` | The maximal set of data this partner may ever receive from this registry | The registry's data scope IDs, `<controller>.<name>` (e.g. `farmer-registry.land`), from its scope catalogue | `data_scopes ⊆ allowed_data_scopes`; effective = intersection |
| `allowed_purposes` | Purpose codes the partner may assert | Open list; empty = any purpose | checked per request |
| `allowed_subject_id_types` | Which subject identifier types are acceptable | Open list; empty = any type | checked per request |
| `allowed_signing_algs` | Acceptable JWS algorithms (reject weak/`none`) | At least one of `EdDSA`, `ES256`, `RS256` (the verifier's accepted set, `crypto_allowed_algorithms`) | at signature verify |
| `max_validity_duration` | Upper bound on `valid_until − valid_from` | ISO-8601 duration longer than zero (`P30D`, `P1Y`, `PT12H`, `P1DT6H`), or `null` for no cap | at validity check |
| `fetch_type` | DEPA-style access pattern | `oneshot` or `periodic` | recorded on artefact |
| `max_fetch_frequency` | For `periodic`, the minimum interval between fetches | ISO-8601 duration > 0, or `null` | enforced per fetch |
| `data_life` | Retention the partner may keep data for after fetch | ISO-8601 duration > 0, or `null` for no cap | recorded on receipt |

CM rejects a policy with any other value (`400`). The admin console offers these as fixed choices:
a checkbox per signing algorithm, a fetch-type dropdown, and a number + unit picker (hours, days,
weeks, months, years, or a custom ISO-8601 value) for each duration. The choices come from
`GET /consent/v1/meta`, the same values the API checks. The open lists stay free text, with values
already used in other policies offered as suggestions.

A policy version saved before these checks still loads. Its `issues` field lists the values that
are no longer accepted, and the console flags them. The version stays in force as stored until
someone edits the policy, and the edit can only be saved once those values are fixed.

**Data scopes are the registry's, not CM's.** CM treats scopes as opaque strings. Each registry
publishes its scope catalogue — scope IDs `<controller>.<name>`, each a named group of the
registry's own fields (by default one per register section), versioned — at
`POST /partner/data_scopes` (signed) on its partner API (and `GET /data_scopes` on its staff API). Put those
IDs in `allowed_data_scopes`; they are not keys of a DCI record or any other output format. A
registry ignores IDs it does not know, so a mistyped or outdated scope grants nothing. See
[Data Scopes](../../products/registry/registry/design/data-scopes.md).

### Example policy

```json
{
  "version": 3,
  "status": "active",
  "allowed_data_scopes": ["farmer-registry.personal_details", "farmer-registry.land"],
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
  signing algs), a longer `max_validity_duration` / `data_life`, `oneshot` → `periodic` fetching, or
  a shorter `max_fetch_frequency`; the **first policy counts as widening** (configurable with
  `awe_gate_first_policy`) — creates a new `PartnerPolicy` version in status `pending` and submits
  an approval request to AWE. The prior `active` version **stays in force** until AWE approves.
  Only one version per binding can be `pending` at a time.
* A pure **narrowing** change (a strictly smaller/shorter policy), or when AWE is disabled,
  **activates immediately** and supersedes the prior version. If a widening was pending meanwhile,
  its later approval is not applied (it ends `stale` and can be resubmitted), so a narrowing is
  never silently undone.

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
decide(consent_object, data_controller, active_policy_of(aud, data_controller), request_context) -> {
  decision: permit | deny,
  effective_data_scopes: requested ∩ grant(data_controller).data_scopes ∩ policy.allowed_data_scopes,
  reason_code,
  policy_version
}
```

## Consent templates (optional)

To standardise common partnerships, a controller can define **consent templates** — named bundles
of purpose + scopes + validity that align with a partner policy. Templates make origination flows
consistent and give subjects predictable, comparable consent prompts. See
[Standards &amp; best practices](standards-and-best-practices.md).
