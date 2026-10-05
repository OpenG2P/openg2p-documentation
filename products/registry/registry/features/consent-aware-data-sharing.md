# Consent-Aware data sharing

The Registry shares personal data with an external partner only when a **positive
authorization decision** comes back from the dedicated **Consent Manager (CM)**
microservice. Consent logic is deliberately *not* embedded in the registry: the registry
is the **Policy Enforcement Point (PEP)**, the Consent Manager is the **Policy Decision
Point (PDP)**. The registry never interprets consent semantics, never holds partner
signing keys, and never evaluates consent policy.

{% hint style="info" %}
The full contract — consent object format, signatures, key handling, configuration and
request flow — is specified **once**, on the Consent Manager side:
[Registry integration (the PEP side)](../../../../consent-management/design/registry-integration.md).
This page covers only what the *registry* does.
{% endhint %}

## How it works

Consent travels **with the request**. A partner calling the registry's DCI search API
embeds its consent object — a compact JWS signed with the partner's own key — in the
DCI-standard `authorize` block:

```
message.search_request[i].search_criteria.authorize.consent_jws
```

The registry partner-api then:

1. **Verifies the caller** — checks the DCI envelope signature against the partner's
   public key fetched from
   [**Partner Management**](../../../../platform/platform-services/partner-management/README.md)
   (looked up as `PARTNER_<sender_id>`, cached in-process). The registry stores no
   partner keys.
2. **Delegates the decision** — forwards the consent JWS verbatim to the Consent
   Manager's `/validate`, naming itself as the **data controller** (for example
   `farmer-registry`). A partner's consent can cover several registries with one grant
   each; CM evaluates only this registry's grant against the partner's policy for this
   registry, and returns a decision, the **effective data scopes** (grant ∩ policy) and
   the consent's subject.
3. **Checks the subject** — the consent's subject must be the person searched. In an
   entity register every returned record's foundational or functional ID must equal it;
   in an activity register the searched subject must equal it or be linked to it by the
   register's own data (e.g. a crop record holding the farmer's Fayda FAN).
4. **Enforces the decision** — filters every record to the fields of those effective
   scopes, then renders it. A scope is a named group of the registry's own fields (by
   default one per register section), not a key of the output format; see
   [Data Scopes](../design/data-scopes.md). A narrower consent or policy can only ever
   *remove* fields, never add them. Any
   non-permit decision or subject mismatch rejects the request (**fail-closed**).

CM separately records a canonical **consent artefact** and issues a signed **consent
receipt** — the audit / non-repudiation evidence. The registry keeps none of it.

## Configuration

Enforcement is governed by two **independent** switches on the partner-api. Both default
**on** (the chart fails closed); turn one off only for testing or a bring-up install:

| Switch | Effect when ON |
| --- | --- |
| **Verify Partner Signature** | verify the DCI envelope signature against Partner Management keys |
| **Enforce Consent** | call the Consent Manager and filter returned records to the consented scopes' fields |

The registry's data-controller ID is set with **Consent data controller**
(`global.consentDataController`), which defaults to the registry variant. It must match
the controller ID that partners are bound to in the Consent Manager.

A composite service or aggregator calling the registry for a partner signs the request
with its own key, forwards the partner's consent unchanged, and names the partner in
`header.meta.on_behalf_of`; the registry logs it.

When a switch is OFF the bypass is logged and stamped into the DCI response header
`meta`, so a bypassed response can never be mistaken for an authorised one. The exact
env vars and Helm values are listed in
[Registry integration](../../../../consent-management/design/registry-integration.md#configuration-registry-partner-api).

## Related

* [Consent Management](../../../../consent-management/README.md) — the service, its design and APIs
* [Registry integration (the PEP side)](../../../../consent-management/design/registry-integration.md) — the full contract
* [Partner integration guide](../../../../consent-management/partner-integration-guide.md) — for partners: onboarding, keys, obtaining consent, signing
* [Partner APIs](../design/partner-apis.md) — the registry's DCI search API
